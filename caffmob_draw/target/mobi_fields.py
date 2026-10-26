"""Campos do painel para a parede e a abertura do CAFF MOBI (067 onda 8, T205; D-42, D-43; RF-165, RF-166).

`WindowManager.btm_mobi` fica fora do arquivo e do Undo. Os getters leem o objeto do snapshot e o JSON que a montagem
gravou nele (`caffmob_abertura`, `caffmob_parede`), na unidade do projeto. O setter não mexe na cena: converte o texto
para mm e agenda o operador `caffmob.mobi_editar_entidade`, que grava no documento e remonta. Remontar dentro do setter
apagaria objetos durante o desenho; e o operador chamado por timer não grava passo de desfazer sozinho (protótipo
T180), então o passo é gravado aqui, depois de a edição terminar.
"""
import json

import bpy  # type: ignore

from ..data import units
from ..data.i18n import N_
from . import snapshot

_pendentes = []


def _alvo(context, tipo):
    target = snapshot.current(context)
    obj = snapshot.object_for(context, target.uid) if target is not None else None
    if obj is None or obj.get('caffmob_tipo') != tipo:
        return None
    return obj


def _unidade():
    return units.get_scene_length_unit(bpy.context.scene)


def _texto(mm):
    return '' if mm is None else units.format_length(mm / 1000, unit=_unidade())


def ler_abertura(obj, campo):
    try:
        return json.loads(obj.get('caffmob_abertura') or '{}').get(campo)
    except ValueError:
        return None


def ler_parede(obj, campo):
    """Valor comum dos trechos da parede, ou None quando diferem ("Múltiplos")."""
    try:
        trechos = json.loads(obj.get('caffmob_parede') or '{}').get('segmentos', [])
    except ValueError:
        return None
    if campo == 'altura':
        valores = {v for s in trechos for v in (s['pe_direito_inicial'], s['pe_direito_final'])}
    else:
        valores = {s[campo] for s in trechos}
    return next(iter(valores)) if len(valores) == 1 else None


def trechos(obj):
    try:
        return json.loads(obj.get('caffmob_parede') or '{}').get('segmentos', [])
    except ValueError:
        return []


def _erro(texto):
    state = getattr(bpy.context.window_manager, 'btm_target', None)
    if state is not None:
        state.error = texto


def _campo(nome, tipo, campo, ler, zero=False):
    def get(_self):
        obj = _alvo(bpy.context, tipo)
        return '' if obj is None else _texto(ler(obj, campo))

    def set_(_self, texto):
        context = bpy.context
        obj = _alvo(context, tipo)
        if obj is None:
            return
        try:
            mm = round(units.parse_length(texto, _unidade(), allow_zero=zero) * 1000)
        except ValueError as exc:
            _erro(str(exc))
            return
        _erro('')
        agendar(tipo, obj.get('caffmob_id'), campo, mm, context.scene.get('caffmob_ambiente') or '')
    return bpy.props.StringProperty(name=nome, get=get, set=set_, options=set())


def agendar(tipo, entidade_id, campo, valor_mm, original):
    _pendentes.append(dict(tipo=tipo, entidade_id=entidade_id, campo=campo, valor_mm=valor_mm, original=original))
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0)


def _tick():
    """Executa as edições agendadas, uma por vez, cada uma com o seu passo de desfazer."""
    while _pendentes:
        pedido = _pendentes.pop(0)
        try:
            resultado = bpy.ops.caffmob.mobi_editar_entidade(**pedido)
        except RuntimeError as exc:                     # recusa com relatório de erro vira exceção vinda do Python
            _erro(str(exc).split(':', 1)[-1].strip())
            continue
        if 'FINISHED' in resultado:
            try:
                bpy.ops.ed.undo_push(message=N_("Editar medida do CAFF MOBI"))
            except RuntimeError:
                pass                                    # sem janela (ensaio em segundo plano): nada a empilhar
        else:
            _erro(N_("A medida não foi aplicada; veja o motivo na barra de status."))
    return None


class BTM_PG_MobiFields(bpy.types.PropertyGroup):
    largura: _campo(N_("Largura"), 'abertura', 'largura', ler_abertura)  # type: ignore
    altura: _campo(N_("Altura"), 'abertura', 'altura', ler_abertura)  # type: ignore
    peitoril: _campo(N_("Peitoril"), 'abertura', 'peitoril', ler_abertura, zero=True)  # type: ignore
    posicao: _campo(N_("Distância do início"), 'abertura', 'posicao', ler_abertura, zero=True)  # type: ignore
    parede_altura: _campo(N_("Altura"), 'parede', 'altura', ler_parede)  # type: ignore
    parede_espessura: _campo(N_("Espessura"), 'parede', 'espessura', ler_parede)  # type: ignore


def register():
    bpy.utils.register_class(BTM_PG_MobiFields)
    bpy.types.WindowManager.btm_mobi = bpy.props.PointerProperty(type=BTM_PG_MobiFields)


def unregister():
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    _pendentes.clear()
    if hasattr(bpy.types.WindowManager, 'btm_mobi'):
        del bpy.types.WindowManager.btm_mobi
    bpy.utils.unregister_class(BTM_PG_MobiFields)
