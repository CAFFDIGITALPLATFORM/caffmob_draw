"""Sincronia do Padrão de Dimensões com o MOBI (feature 067, T160; D-34; RF-034, RF-035).

Liga o banco local (`store`) às rotas `/api/draw/v2/padroes-de-dimensao` (contrato em
`_reversa_forward/067-propriedades-por-selecao/interfaces/padroes-de-dimensao-mobi.md`). A decisão por uid é de
`sync_core`; aqui ficam só a ordem das chamadas e a gravação do resultado.

- Disparo: no login (depois da descoberta de `mobi/api_v2.na_conexao`), na abertura do arquivo com conta ligada e
  5 s depois da última gravação no banco (`schedule`, com debounce). Nunca no draw nem num getter: tudo roda num
  timer e nas respostas do subprocesso de rede.
- Sem rede, sem conta ou sem a capacidade `padroes_de_dimensao`, não faz nada e as linhas continuam `sujo`.
- O transporte é `downloads.request` direto, não `mobi/tarefas.Job`: a sincronia corre por trás e não pode cancelar
  um envio de ambiente nem ocupar a barra de situação. A sessão (capacidades) é a de `mobi/api_v2`.
- Um ciclo por vez; disparo durante um ciclo marca outro para o fim. Conflito nunca é resolvido aqui: vai para a
  tabela `conflito` e espera a escolha do usuário (`resolve`, chamado pelos operadores de conflito).
"""

import bpy  # type: ignore

from . import store, sync_core as sc
from ..data.i18n import N_, tr

BASE = '/api/draw/v2'
DEBOUNCE = 5.0
RETRY = N_('Padrão de Dimensões: a nuvem não respondeu; a sincronia tenta de novo depois')
REFUSED = N_('Padrão de Dimensões: o MOBI recusou "{}" ({})')
NO_CLOUD = N_('Sem conexão com o MOBI: a escolha fica para quando a nuvem responder')

_state = {'running': False, 'again': False, 'tickets': [], 'transport': None, 'message': '', 'conflicts': (),
          'generation': 0}


# Disponibilidade -----------------------------------------------------------------------------------------------

def _session():
    from ..mobi import api_v2
    from ..texture_library import downloads
    if api_v2._sessao.get('servidor') != downloads.server_url():
        api_v2._sessao.clear()
        api_v2._sessao['servidor'] = downloads.server_url()
    return api_v2._sessao


def unavailable():
    """Motivo para não sincronizar agora ('' quando pode). A capacidade só é conferida depois da descoberta."""
    if _state['transport'] is not None:
        return ''
    from ..texture_library import auth, downloads
    if downloads.unavailable_reason():
        return 'OFFLINE'
    if not auth.signed_in():
        return 'NO_ACCOUNT'
    return ''


def _capable():
    caps = _session().get('capacidades') or {}
    return caps.get('padroes_de_dimensao') is True


# Transporte ----------------------------------------------------------------------------------------------------

def _request(method, path, body, headers, callback):
    """Chama o transporte (o de teste ou o subprocesso de rede) e guarda o pedido para poder cancelar."""
    generation = _state['generation']

    def received(status, data, incoming):
        if generation == _state['generation']:
            callback(status, data if isinstance(data, dict) else {}, incoming or {})
    transport = _state['transport']
    if transport is not None:
        ticket = transport(method, BASE + path, body, headers, received)
    else:
        from ..texture_library import downloads
        ticket = downloads.request(method, BASE + path, body, headers=headers, callback=received,
                                   response_headers=True)
    _state['tickets'].append(ticket)
    return ticket


def _etag_version(headers, fallback):
    value = next((v for k, v in (headers or {}).items() if k.lower() == 'etag'), None)
    try:
        return int(str(value).strip().strip('W/').strip('"'))
    except (TypeError, ValueError):
        return fallback


def _db():
    try:
        return store.get()
    except (store.StoreError, OSError) as exc:
        print(f"CAFFMob Draw: banco do Padrão de Dimensões indisponível: {exc}")
        return None


# Ciclo ---------------------------------------------------------------------------------------------------------

def schedule(delay=DEBOUNCE):
    """(Re)arma o disparo; gravações seguidas empurram o disparo para 5 s depois da última."""
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    bpy.app.timers.register(_tick, first_interval=max(0.0, float(delay)))


def _tick():
    run()
    return None


def run(done=None):
    """Um ciclo de sincronia; `done(resumo)` no fim (o ensaio usa). Devolve False quando nada foi tentado."""
    if _state['running']:
        _state['again'] = True
        return True
    reason = unavailable()
    if reason:
        _finish(done, {'skipped': reason})
        return False
    db = _db()
    if db is None:
        _finish(done, {'skipped': 'NO_STORE'})
        return False
    _state['running'], _state['again'], _state['tickets'] = True, False, []
    summary = {'actions': {}, 'errors': []}

    def end():
        _state['running'] = False
        refresh_conflicts(db)
        if _state['again']:
            schedule(0.1)
        _finish(done, summary)

    def listed(remotes):
        if remotes is None:
            end()
            return
        locals_by_uid = {uid: sc.Local(document, state['versao_remota'], state['sujo'], state['excluida'])
                         for uid, document, state in db.rows()}
        in_conflict = {c['uid'] for c in db.conflicts()}
        steps = [(uid, d) for uid, d in sc.plan(locals_by_uid, remotes) if uid not in in_conflict]
        _run_steps(db, steps, locals_by_uid, summary, end)

    def discovered():
        if not _capable():
            summary['skipped'] = 'NO_CAPABILITY'
            end()
            return
        _list_all(summary, listed)

    if _session().get('capacidades') is None:
        _discover(summary, discovered)
    else:
        discovered()
    return True


def _finish(done, summary):
    if done is not None:
        done(summary)


def _discover(summary, then):
    def received(status, data, _headers):
        if status == 200 and data.get('versao_api') == 2 and isinstance(data.get('schemas'), list):
            _session()['capacidades'] = dict(data)
        elif status == 404:
            _session()['capacidades'] = {'versao_api': 1}
        else:
            summary['errors'].append(('capacidades', status))
        then()
    _request('GET', '/capacidades', None, {'Accept': 'application/json'}, received)


def _list_all(summary, then, cursor=None, acc=None):
    acc = {} if acc is None else acc

    def received(status, data, _headers):
        if status != 200:
            summary['errors'].append(('listagem', status))
            _state['message'] = tr(RETRY)
            then(None)
            return
        remotes, following = sc.read_page(data)
        acc.update(remotes)
        if following:
            _list_all(summary, then, following, acc)
        else:
            then(acc)
    _request('GET', sc.page_path(cursor), None, {'Accept': 'application/json'}, received)


def _run_steps(db, steps, locals_by_uid, summary, end):
    steps = list(steps)

    def following(*_args):
        if not steps:
            end()
            return
        uid, decision = steps.pop(0)
        summary['actions'][uid] = decision.action
        _execute(db, uid, decision, locals_by_uid.get(uid), summary, following)
    following()


def _execute(db, uid, decision, local, summary, then):
    """Executa uma decisão de `sync_core` e chama `then()` quando a gravação local terminou."""
    action = decision.action
    if action == sc.NOTHING:
        then()
    elif action in (sc.PURGE, sc.DELETE_LOCAL):
        db.purge(uid)
        then()
    elif action == sc.ADOPT:
        db.mark_synced(uid, decision.if_match)
        then()
    elif action == sc.DOWNLOAD:
        _download(db, uid, summary, then)
    elif action == sc.COMPARE:
        _compare(db, uid, local, summary, then)
    elif action in (sc.UPLOAD, sc.CREATE):
        _put(db, uid, decision, local, summary, then)
    elif action == sc.DELETE_REMOTE:
        _delete(db, uid, decision, local, summary, then)
    elif action == sc.DELETE_CONFLICT:
        if decision.side == 'CLOUD':
            db.add_conflict(uid, sc.DELETE_CONFLICT, 'CLOUD', decision.if_match, None)
            then()
        else:                                        # o local apagou e a nuvem editou: mostra a versão da nuvem
            def got(document, version):
                if document is not None:
                    db.add_conflict(uid, sc.DELETE_CONFLICT, 'LOCAL', version, document)
                then()
            _fetch(uid, summary, got)
    else:
        then()


def _fetch(uid, summary, then):
    """GET do documento da nuvem: `then(documento, versão)`, ou `(None, None)` quando não veio."""
    def received(status, data, headers):
        if status == 200 and data.get('uid') == uid:
            then(data, _etag_version(headers, None))
        else:
            summary['errors'].append((uid, status))
            then(None, None)
    _request('GET', f'/padroes-de-dimensao/{uid}', None, {'Accept': 'application/json'}, received)


def _download(db, uid, summary, then):
    def got(document, version):
        if document is not None and version is not None:
            db.apply_remote(document, version)
        then()
    _fetch(uid, summary, got)


def _compare(db, uid, local, summary, then):
    def got(document, version):
        if document is not None and version is not None:
            decision = sc.after_compare(local, sc.Remote(version), document)
            if decision.action == sc.ADOPT:
                db.mark_synced(uid, version, dirty=not sc.same_content(db.local_document(uid), local.document))
            else:
                db.add_conflict(uid, sc.EDIT_CONFLICT, '', version, document)
        then()
    _fetch(uid, summary, got)


def _on_conflict_body(db, uid, decision, data):
    """409 `VERSAO_DIVERGENTE`: conteúdo igual ao local adota a nuvem; diferente vira conflito."""
    version, current = data.get('versao_atual'), data.get('documento_atual')
    local_document = db.local_document(uid)
    if decision.action == sc.CREATE and isinstance(current, dict) and type(version) is int \
            and sc.same_content(local_document, current):
        db.mark_synced(uid, version)
        return
    kind = sc.on_status(decision, 409, None)
    db.add_conflict(uid, kind.action, kind.side, version if type(version) is int else None,
                    current if isinstance(current, dict) else None)


def _put(db, uid, decision, local, summary, then):
    document = db.local_document(uid)
    if document is None:
        then()
        return
    key = db.pending_key(uid)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Idempotency-Key': key}
    if decision.action == sc.CREATE:
        headers['If-None-Match'] = '*'
    else:
        headers['If-Match'] = f'"{decision.if_match}"'

    def received(status, data, _headers):
        if status in (200, 201) and type(data.get('version')) is int:
            db.mark_synced(uid, data['version'], dirty=not sc.same_content(db.local_document(uid), document))
        elif status == 409 and data.get('erro') == 'VERSAO_DIVERGENTE':
            _on_conflict_body(db, uid, decision, data)
        elif status == 409 and data.get('erro') == 'CHAVE_REUTILIZADA':
            db.drop_pending_key(uid)                 # a próxima tentativa vai com outra chave; continua `sujo`
        elif status == 404:
            follow = sc.on_status(decision, 404, local or sc.Local(document, dirty=True))
            if follow is not None:
                _execute(db, uid, follow, local, summary, then)
                return
            _refused(uid, document, status, data, summary)
        else:
            _refused(uid, document, status, data, summary)
        then()
    _request('PUT', f'/padroes-de-dimensao/{uid}', document, headers, received)


def _delete(db, uid, decision, local, summary, then):
    key = db.pending_key(uid)
    headers = {'Accept': 'application/json', 'Idempotency-Key': key, 'If-Match': f'"{decision.if_match}"'}

    def received(status, data, _headers):
        if status in (200, 404):                     # 404: a nuvem já não tem; a exclusão chegou aos dois lados
            db.purge(uid)
        elif status == 409 and data.get('erro') == 'VERSAO_DIVERGENTE':
            _on_conflict_body(db, uid, decision, data)
        elif status == 409 and data.get('erro') == 'CHAVE_REUTILIZADA':
            db.drop_pending_key(uid)
        else:
            _refused(uid, db.local_document(uid) or {}, status, data, summary)
        then()
    _request('DELETE', f'/padroes-de-dimensao/{uid}', None, headers, received)


def _refused(uid, document, status, data, summary):
    summary['errors'].append((uid, status))
    if status is None or status in (401, 429) or (isinstance(status, int) and status >= 500):
        _state['message'] = tr(RETRY)
    else:
        _state['message'] = tr(REFUSED).format(document.get('name') or uid, data.get('erro') or status)
    print(f"CAFFMob Draw: {_state['message']}")


# Conflitos -----------------------------------------------------------------------------------------------------

def refresh_conflicts(db=None):
    """Cópia dos conflitos para o painel (o draw nunca lê o banco)."""
    db = db or _db()
    if db is None:
        _state['conflicts'] = ()
        return ()
    items = []
    for conflict in db.conflicts():
        local_document = db.local_document(conflict['uid'])
        state = db.state(conflict['uid']) or {}
        remote = conflict['documento_remoto']
        items.append(dict(conflict, documento_local=local_document, local_apagada=bool(state.get('excluida')),
                          campos=sc.changed_fields(local_document, remote) if local_document and remote else []))
    _state['conflicts'] = tuple(items)
    _tag_redraw()
    return _state['conflicts']


def conflicts():
    return _state['conflicts']


def _tag_redraw():
    wm = getattr(bpy.context, 'window_manager', None)
    for window in (wm.windows if wm else ()):
        for area in window.screen.areas:
            if area.type in ('VIEW_3D', 'PROPERTIES'):
                area.tag_redraw()


def resolve(uid, choice, done=None):
    """Escolha do usuário num conflito (RF-035). Só tira o item de `conflito` quando a escolha foi aplicada:
    sem rede, a escolha que precisa da nuvem fica para depois e o item continua. `done(ok, mensagem)`."""
    db = _db()
    conflict = db.conflict(uid) if db is not None else None
    if conflict is None:
        _finish_resolve(done, False, '')
        return
    decision = sc.resolve(conflict['tipo'], choice, conflict['lado'], conflict['versao_remota'])
    action = decision.action
    if action == sc.ADOPT or (action == sc.DOWNLOAD and conflict['documento_remoto'] is not None):
        db.apply_remote(conflict['documento_remoto'], conflict['versao_remota'])        # tira o conflito
        _resolved(db, done)
        return
    if action == sc.DELETE_LOCAL:
        db.purge(uid)
        _resolved(db, done)
        return
    if unavailable() or not _capable():
        _finish_resolve(done, False, tr(NO_CLOUD))
        return
    summary = {'actions': {}, 'errors': []}
    state = db.state(uid) or {}
    local = sc.Local(db.local_document(uid) or {}, state.get('versao_remota'), True, state.get('excluida', False))

    def after():
        if summary['errors']:
            _finish_resolve(done, False, _state['message'] or tr(NO_CLOUD))
            return
        current = db.conflict(uid)
        if current is not None and current['detectado_em'] == conflict['detectado_em']:
            db.remove_conflict(uid)
        _resolved(db, done)
    if action in (sc.CREATE, sc.UPLOAD):
        _put(db, uid, decision, local, summary, after)
    elif action == sc.DELETE_REMOTE:
        _delete(db, uid, decision, local, summary, after)
    else:
        _finish_resolve(done, False, '')


def _resolved(db, done):
    refresh_conflicts(db)
    _finish_resolve(done, True, '')


def _finish_resolve(done, ok, message):
    if done is not None:
        done(ok, message)


# Registro ------------------------------------------------------------------------------------------------------

def cancel():
    """Para o ciclo em andamento (descarregar o addon, trocar de arquivo)."""
    _state['generation'] += 1
    if _state['transport'] is None:
        from ..texture_library import downloads
        for ticket in _state['tickets']:
            downloads.cancel_request(ticket)
    _state['tickets'], _state['running'], _state['again'] = [], False, False


def register():
    pass


def unregister():
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    cancel()
