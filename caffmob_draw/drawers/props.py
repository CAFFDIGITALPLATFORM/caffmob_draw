"""Campos da gaveta selecionada no painel por seleção (072 D-09): corrediça e comprimento.

O getter lê a frente selecionada; o setter agenda a troca por timer (mexer na cena dentro do desenho do painel não
pode) e grava o passo de desfazer depois, como nos campos do MOBI da onda 8 da 067.
"""
import bpy  # type: ignore

from ..data.i18n import N_
from . import build, catalogo, ops
from .scene import comprimento, spec

_ITENS = []
_pendentes = []


def _itens(_self, _context):
    _ITENS[:] = [(c.id, c.nome, c.carga) for c in catalogo.todas(build.pasta_do_usuario())]
    return _ITENS


def _corredica_get(self):
    front = ops.frente_selecionada(bpy.context)
    if front is None or front.get('btm_drawer') is None:
        return 0
    ids = [i[0] for i in _itens(self, None)]
    cid = spec(front).corredica
    return ids.index(cid) if cid in ids else 0


def _corredica_set(self, indice):
    front = ops.frente_selecionada(bpy.context)
    if front is None:
        return
    ids = [i[0] for i in _itens(self, None)]
    if 0 <= indice < len(ids):
        _pendentes.append((front.name, ids[indice]))
        if not bpy.app.timers.is_registered(_tick):
            bpy.app.timers.register(_tick, first_interval=0.0)


def _comprimento_get(_self):
    front = ops.frente_selecionada(bpy.context)
    if front is None or front.get('btm_drawer') is None:
        return ''
    return f"{int(comprimento(front))} mm"


def _tick():
    while _pendentes:
        nome, cid = _pendentes.pop(0)
        try:
            if 'FINISHED' in bpy.ops.caffmob.gaveta_corredica(gaveta=nome, corredica=cid):
                bpy.ops.ed.undo_push(message="Trocar corrediça")
        except RuntimeError as exc:
            state = getattr(bpy.context.window_manager, 'btm_target', None)
            if state is not None:
                state.error = str(exc)
    return None


class BTM_PG_DrawerSelection(bpy.types.PropertyGroup):
    corredica: bpy.props.EnumProperty(name=N_("Corrediça"), items=_itens, get=_corredica_get,  # type: ignore
                                      set=_corredica_set)
    comprimento: bpy.props.StringProperty(name=N_("Comprimento da corrediça"), get=_comprimento_get)  # type: ignore


def register():
    bpy.utils.register_class(BTM_PG_DrawerSelection)
    bpy.types.WindowManager.btm_drawer_sel = bpy.props.PointerProperty(type=BTM_PG_DrawerSelection)


def unregister():
    del bpy.types.WindowManager.btm_drawer_sel
    bpy.utils.unregister_class(BTM_PG_DrawerSelection)
