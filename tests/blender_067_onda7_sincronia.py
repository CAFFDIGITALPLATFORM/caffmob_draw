"""Sincronia do Padrão de Dimensões com o MOBI contra um servidor falso (feature 067, T140; RF-034, RF-035, D-34).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda7_sincronia.py

O servidor falso segue `interfaces/padroes-de-dimensao-mobi.md` (versão otimista, `If-Match`, `If-None-Match: *`,
recibo por `Idempotency-Key`, exclusão lógica listada, páginas) e entra pelo transporte injetável de `sync_cloud`.
Duas "máquinas" são dois bancos temporários na mesma conta. Nenhuma chamada sai para a rede.

- sem rede nada trava e as linhas continuam `sujo`; sem a capacidade não sincroniza;
- pacote igual nas duas máquinas não gera conflito;
- conflito de edição mostra as duas versões; nada muda antes da escolha; fechar sem escolher mantém as duas e a
  pergunta volta; "Manter a da nuvem" e "Manter a minha";
- apagar × editar oferece "Manter apagado" ou "Manter a edição", nos dois sentidos.
"""

import copy
import json
import os
import sys
import tempfile
import traceback
import uuid
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.standards import io_json, store, sync_cloud, sync_core  # noqa: E402

FAILURES = []
ENVELOPE = sync_core.ENVELOPE


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def document(uid, name="Marcenaria X", lateral=15.0, version=1):
    values = {'COZ.sheets.LAT.thickness': lateral, 'COZ.sheets.LAT.material': 'MDF'}
    return io_json.values_to_document(name, uid, 'BR', 'USER', version, "2026-10-25T10:00:00-03:00", values)


class FakeMobi:
    """Servidor do contrato, em memória. `page` pequeno para a listagem precisar de mais de uma página."""

    def __init__(self, capability=True, page=2):
        self.rows, self.receipts, self.calls = {}, {}, []
        self.capability, self.page, self.offline = capability, page, False

    def __call__(self, method, path, body, headers, callback):
        self.calls.append((method, path))
        if self.offline:
            callback(None, {'error': 'offline'}, {})
            return {}
        status, data, out = self.handle(method, path, copy.deepcopy(body), headers or {})
        callback(status, copy.deepcopy(data), out)
        return {}

    def handle(self, method, path, body, headers):
        base = '/api/draw/v2'
        path = path[len(base):]
        if path == '/capacidades':
            caps = {'versao_api': 2, 'schemas': ['caffmob.ambiente/v1', 'caffmob.ambiente/v2'], 'ambientes_v2': True}
            if self.capability:
                caps['padroes_de_dimensao'] = True
            return 200, caps, {}
        if method == 'GET' and (path == '/padroes-de-dimensao' or path.startswith('/padroes-de-dimensao?')):
            after = int(path.split('depois=')[1]) if 'depois=' in path else 0
            uids = sorted(self.rows)
            items = [{'uid': u, 'nome': self.rows[u]['doc']['name'], 'version': self.rows[u]['version'],
                      'atualizado_em': 'x', 'excluido': self.rows[u]['deleted']} for u in uids[after:after + self.page]]
            following = str(after + self.page) if after + self.page < len(uids) else None
            return 200, {'itens': items, 'proximo': following}, {}
        uid = path.rsplit('/', 1)[1]
        row = self.rows.get(uid)
        alive = row is not None and not row['deleted']
        if method == 'GET':
            return (200, row['doc'], {'ETag': f'"{row["version"]}"'}) if alive else (404, {'erro': 'NAO_ENCONTRADO'}, {})
        key = headers.get('Idempotency-Key')
        content = {k: v for k, v in (body or {}).items() if k not in ENVELOPE} if body else None
        digest = json.dumps([method, uid, headers.get('If-Match'), content], sort_keys=True)
        if key in self.receipts:
            old_digest, answer = self.receipts[key]
            if old_digest != digest:
                return 409, {'erro': 'CHAVE_REUTILIZADA'}, {}
            return answer[0], answer[1], {'Idempotency-Replayed': 'true'}
        divergent = (409, {'erro': 'VERSAO_DIVERGENTE', 'versao_atual': row['version'] if row else None,
                           'documento_atual': row['doc'] if row else None}, {})
        if method == 'PUT':
            if headers.get('If-None-Match') == '*':
                if alive:
                    return divergent
                version = row['version'] + 1 if row else 1
                status = 201
            else:
                if not alive:
                    return 404, {'erro': 'NAO_ENCONTRADO'}, {}
                if headers.get('If-Match') != f'"{row["version"]}"':
                    return divergent
                version, status = row['version'] + 1, 200
            self.rows[uid] = {'doc': body, 'version': version, 'deleted': False}
            answer = (status, {'version': version, 'atualizado_em': 'x'})
        else:                                                           # DELETE
            if not alive:
                return 404, {'erro': 'NAO_ENCONTRADO'}, {}
            if headers.get('If-Match') != f'"{row["version"]}"':
                return divergent
            row['version'] += 1
            row['deleted'] = True
            answer = (200, {'version': row['version'], 'excluido_em': 'x'})
        self.receipts[key] = (digest, answer)
        return answer[0], answer[1], {'ETag': f'"{answer[1]["version"]}"'}

    def edit(self, uid, **changes):
        """Outra máquina editou na nuvem."""
        row = self.rows[uid]
        row['doc'] = dict(row['doc'], **changes)
        row['version'] += 1

    def count(self, prefix):
        return sum(1 for _m, p in self.calls if '/padroes-de-dimensao' in p and p.startswith(prefix))


class Machines:
    def __init__(self, directory):
        self.paths = {name: os.path.join(directory, f"{name}.sqlite3") for name in ('A', 'B')}

    def use(self, name):
        store.override_path = self.paths[name]
        return store.get()


class Layout:
    """Layout falso: registra textos e botões que o painel desenha."""

    def __init__(self, log=None):
        self.log = [] if log is None else log

    def box(self, **_kwargs):
        return Layout(self.log)

    column = row = box

    def label(self, text="", icon=None):
        self.log.append(('label', text))

    def operator(self, idname, text=""):
        import types
        op = types.SimpleNamespace()
        self.log.append(('op', text, op))
        return op


def drawn():
    from caffmob_draw.ui import panels
    layout = Layout()
    panels.draw_standards_conflicts(layout)
    return layout.log


def sync():
    result = {}
    sync_cloud.run(lambda summary: result.update(summary))
    return result


def capabilities_reset():
    from caffmob_draw.mobi import api_v2
    api_v2._sessao.clear()


def scenario(directory):
    server = FakeMobi()
    sync_cloud._state['transport'] = server
    m = Machines(directory)
    u1, u2, u3 = (str(uuid.uuid4()) for _ in range(3))

    # Sem rede: nada trava, sujo fica.
    db = m.use('A')
    db.put(document(u1, "Marcenaria X"))
    server.offline = True
    capabilities_reset()
    summary = sync()
    check("sem rede: o ciclo termina", 'errors' in summary or 'skipped' in summary, summary)
    check("sem rede: a linha continua suja", db.state(u1)['sujo'] is True, db.state(u1))
    check("sem rede: nada fica rodando", sync_cloud._state['running'] is False)
    server.offline = False

    # Capacidade ausente: não sincroniza.
    server.capability = False
    capabilities_reset()
    summary = sync()
    check("sem a capacidade: não sincroniza", summary.get('skipped') == 'NO_CAPABILITY' and server.count('/') == 0,
          (summary, server.calls))
    check("sem a capacidade: continua suja", db.state(u1)['sujo'] is True)
    server.capability = True
    capabilities_reset()

    # A cria três; a listagem precisa de duas páginas.
    db.put(document(u2, "Marcenaria Y"))
    db.put(document(u3, "Marcenaria Z"))
    summary = sync()
    check("A envia as três", sorted(server.rows) == sorted([u1, u2, u3]) and not summary['errors'], summary)
    check("A fica limpa com a versão da nuvem", all(db.state(u)['sujo'] is False and db.state(u)['versao_remota'] == 1
                                                    for u in (u1, u2, u3)))
    sync()
    check("listagem em duas páginas", any('depois=2' in p for _m, p in server.calls))

    # B importou o mesmo pacote (mesmo conteúdo, outro envelope): adota sem conflito.
    db_b = m.use('B')
    for u, name in ((u1, "Marcenaria X"), (u2, "Marcenaria Y"), (u3, "Marcenaria Z")):
        db_b.put(document(u, name, version=7))
    puts = server.count('/api/draw/v2/padroes-de-dimensao/')
    sync()
    check("pacote igual nas duas máquinas não gera conflito", db_b.conflicts() == [], db_b.conflicts())
    check("B adota a versão da nuvem", all(db_b.state(u) == dict(db_b.state(u), sujo=False, versao_remota=1)
                                           for u in (u1, u2, u3)))
    check("B não reenviou nada", server.count('/api/draw/v2/padroes-de-dimensao/') - puts == 3,
          server.calls[-6:])                                           # só os 3 GET de comparação

    # Conflito de edição: B sobe uma edição; A editou a mesma definição.
    db_b.put(document(u1, "Marcenaria X", lateral=18.0))
    sync()
    db = m.use('A')
    db.put(document(u1, "Marcenaria X", lateral=25.0))
    sync()
    [conflict] = sync_cloud.conflicts()
    check("conflito de edição aparece com as duas versões",
          conflict['tipo'] == 'EDIT_CONFLICT' and conflict['documento_remoto']['lines'] == document(u1, lateral=18.0)['lines']
          and conflict['documento_local']['lines'] == document(u1, lateral=25.0)['lines'], conflict)
    check("conflito mostra o que difere", conflict['campos'] == ['lines'], conflict['campos'])
    log = drawn()
    buttons = [(entry[1], entry[2].choice, entry[2].uid) for entry in log if entry[0] == 'op']
    check("a lista mostra as duas versões e as duas escolhas",
          ('label', "Conflitos de padrão") in log and any(e[0] == 'label' and 'versão 2' in e[1] for e in log)
          and buttons == [("Manter a minha", 'KEEP_MINE', u1), ("Manter a da nuvem", 'KEEP_CLOUD', u1)], log)
    check("nada muda antes da escolha", db.local_document(u1)['lines'] == document(u1, lateral=25.0)['lines']
          and server.rows[u1]['doc']['lines'] == document(u1, lateral=18.0)['lines'])
    store.close()                                                      # fechar sem escolher
    db = m.use('A')
    sync()
    check("fechar sem escolher mantém as duas e a pergunta volta",
          [c['uid'] for c in sync_cloud.refresh_conflicts()] == [u1] and db.state(u1)['sujo'] is True)
    bpy.ops.caffmob.standards_conflict_resolve(uid=u1, choice='KEEP_CLOUD')
    check("Manter a da nuvem grava a remota e tira o conflito",
          db.local_document(u1)['lines'] == document(u1, lateral=18.0)['lines'] and sync_cloud.conflicts() == ()
          and db.state(u1)['sujo'] is False, db.state(u1))
    result = bpy.ops.caffmob.standards_conflict_resolve(uid=u1, choice='KEEP_CLOUD')
    check("escolha repetida é recusada", result == {'CANCELLED'}, result)
    check("sem conflito, a lista some", drawn() == [], drawn())

    # Manter a minha.
    server.edit(u2, name="Y da nuvem")
    db.put(document(u2, "Y daqui"))
    sync()
    version = server.rows[u2]['version']
    bpy.ops.caffmob.standards_conflict_resolve(uid=u2, choice='KEEP_MINE')
    check("Manter a minha envia por cima com a versão da nuvem",
          server.rows[u2]['doc']['name'] == "Y daqui" and server.rows[u2]['version'] == version + 1
          and sync_cloud.conflicts() == () and db.state(u2)['sujo'] is False, server.rows[u2]['version'])

    # A nuvem apagou e A editou: "Manter a edição" recria.
    db_b = m.use('B')
    sync()
    db_b.delete(u3)
    sync()
    check("B propaga a exclusão", server.rows[u3]['deleted'] and db_b.state(u3) is None, server.rows[u3])
    db = m.use('A')
    db.put(document(u3, "Z editada"))
    sync()
    [conflict] = sync_cloud.conflicts()
    check("apagar × editar (nuvem apagou) oferece a escolha", (conflict['tipo'], conflict['lado']) == ('DELETE_CONFLICT', 'CLOUD'),
          conflict)
    labels = [e[1] for e in drawn() if e[0] == 'label']
    check("a lista mostra 'apagada' do lado da nuvem e as escolhas do tipo",
          "Na nuvem: apagada" in labels and [e[1] for e in drawn() if e[0] == 'op'] == ["Manter apagado", "Manter a edição"],
          labels)
    check("apagar × editar: nada acontece antes da escolha",
          db.get(u3)['name'] == "Z editada" and server.rows[u3]['deleted'])
    bpy.ops.caffmob.standards_conflict_resolve(uid=u3, choice='KEEP_EDIT')
    check("Manter a edição recria na nuvem", not server.rows[u3]['deleted'] and server.rows[u3]['doc']['name'] == "Z editada"
          and sync_cloud.conflicts() == () and db.state(u3)['sujo'] is False, server.rows[u3])

    # A apagou e a nuvem editou: "Manter apagado" apaga nos dois lados.
    db.delete(u2)
    server.edit(u2, name="Y editada na nuvem")
    sync()
    [conflict] = sync_cloud.conflicts()
    check("apagar × editar (A apagou) mostra a versão da nuvem",
          (conflict['tipo'], conflict['lado'], conflict['documento_remoto']['name']) == ('DELETE_CONFLICT', 'LOCAL', "Y editada na nuvem"),
          conflict)
    bpy.ops.caffmob.standards_conflict_resolve(uid=u2, choice='KEEP_DELETED')
    check("Manter apagado apaga na nuvem e no banco", server.rows[u2]['deleted'] and db.state(u2) is None
          and sync_cloud.conflicts() == (), (server.rows[u2], db.state(u2)))

    # Sem rede, a escolha que precisa da nuvem não tira o conflito.
    server.edit(u1, name="X na nuvem")
    db.put(document(u1, "X aqui"))
    sync()
    server.offline = True
    result = bpy.ops.caffmob.standards_conflict_resolve(uid=u1, choice='KEEP_MINE')
    check("sem rede: Manter a minha fica pendente", [c['uid'] for c in sync_cloud.conflicts()] == [u1], result)
    server.offline = False

    # Disparo com debounce: gravações seguidas armam um só timer.
    sync_cloud.schedule()
    sync_cloud.schedule()
    check("gravações seguidas armam um só disparo", bpy.app.timers.is_registered(sync_cloud._tick))
    bpy.app.timers.unregister(sync_cloud._tick)


try:
    with tempfile.TemporaryDirectory(prefix="caffmob_067_sync_") as directory:
        previous = store.override_path
        try:
            scenario(directory)
        finally:
            sync_cloud._state['transport'] = None
            store.close()
            store.override_path = previous
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "OK" if not FAILURES else "FALHAS " + ", ".join(FAILURES))
print("blender_067_onda7_sincronia:", "OK" if not FAILURES else "FALHA")
if FAILURES:
    sys.exit(1)
