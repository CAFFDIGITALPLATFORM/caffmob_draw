"""Detalhe branco do módulo antes de inserir (medidas e ambiente).

Clicar num modelo na grade abre o card; os campos são editados pelo modal `BTM_OT_LibraryDetailType` (mesmo esquema da
busca digitada) e o botão Inserir valida contra o Padrão de Dimensões antes de chamar `caffmob.library_insert_model`
com largura, altura, profundidade e ambiente escolhidos. Recusa não cria nada e deixa a mensagem no card.
"""

import bpy  # type: ignore

from ..data import dimension_schema as schema
from ..data.i18n import tr
from . import detail_core, draw

FALLBACK_SHEET = (1810.0, 2730.0)
FALLBACK_MODULE = (1200.0, 2700.0, 900.0)


def limite(context, chave, padrao):
    try:
        from ..standards import api
        return float(api.get_value(context.scene, chave))
    except Exception:
        return padrao


def limites(context, line):
    """(chapa ordenada menor/maior, máximos do módulo) do Padrão de Dimensões ativo, em mm."""
    chapa = sorted((limite(context, schema.max_key('sheet_width_max'), 2730.0),
                    limite(context, schema.max_key('sheet_length_max'), 1810.0)))
    modulo = (limite(context, schema.max_key('module_width_max'), FALLBACK_MODULE[0]),
              limite(context, schema.max_key('module_height_max'), FALLBACK_MODULE[1]),
              limite(context, schema.max_key('module_depth_max'), FALLBACK_MODULE[2]))
    return tuple(chapa), modulo


def espessura(context, line):
    """Espessura da lateral no Padrão de Dimensões, em mm."""
    return limite(context, schema.sheet_key(line, 'LAT', 'thickness'), 15.0)


def profundidade_do_padrao(context, line, cabinet_type):
    try:
        from ..operators.cabinet_builder import standard_defaults
        found, _definition = standard_defaults(context, line, cabinet_type)
        return round(float(found.depth) * 1000.0, 1)
    except Exception:
        return 550.0


def abrir(context, key):
    """Abre o card para a entrada `key` da grade; False quando não é modelo de armário."""
    state = context.window_manager.btm_library
    entry = next((item for item in draw.grid_entries(state) if draw.entry_key(item) == key), None)
    if entry is None or entry.get('kind') not in ('MODEL', 'PRESET'):
        return False
    size = entry.get('size_mm') or (800.0, 720.0, 0.0)
    line = entry.get('line') or 'COZ'
    state.detail_open = True
    state.detail_key, state.detail_model = key, entry.get('model', '')
    state.detail_name, state.detail_line = entry.get('name', ''), line
    state.detail_width = float(size[0] or 800.0)
    state.detail_height = float(size[1] or 720.0)
    state.detail_depth = profundidade_do_padrao(context, line, entry.get('cabinet_type', 'BASE'))
    state.detail_thickness = espessura(context, line)
    state.detail_field, state.detail_text, state.detail_error = "", "", ""
    draw.tag_redraw(context)
    return True


def fechar(state):
    state.detail_open = False
    state.detail_key = state.detail_model = state.detail_name = ""
    state.detail_field = state.detail_text = state.detail_error = ""


def fechar_painel(context):
    fechar(context.window_manager.btm_library)
    draw.tag_redraw(context)


def set_valor(state, campo, valor):
    setattr(state, 'detail_' + campo, float(valor))


def validar(context, state):
    chapa, modulo = limites(context, state.detail_line)
    return detail_core.validate(state.detail_width, state.detail_height, state.detail_depth, chapa, modulo,
                                state.detail_thickness)


def confirmar(context):
    """Valida e insere com as medidas e o ambiente do card; False mantém o card com a mensagem."""
    state = context.window_manager.btm_library
    ok, mensagem = validar(context, state)
    if not ok:
        state.detail_error = mensagem
        draw.tag_redraw(context)
        return False
    result = bpy.ops.caffmob.library_insert_model(
        model_id=state.detail_model, line=state.detail_line, width_mm=state.detail_width,
        height_mm=state.detail_height, depth_mm=state.detail_depth)
    if 'FINISHED' not in result:
        state.detail_error = tr("Não foi possível inserir o módulo")
        draw.tag_redraw(context)
        return False
    fechar_painel(context)
    return True


def click(context, part):
    """Trata a parte do card sob o clique (FIELD/LINE/OK/CANCEL)."""
    state = context.window_manager.btm_library
    if part.startswith('FIELD:'):
        state.detail_field = part.split(':', 1)[1]
        state.detail_text = detail_core.fmt(getattr(state, 'detail_' + state.detail_field))
        if bpy.ops.caffmob.library_detail_type.poll():
            bpy.ops.caffmob.library_detail_type('INVOKE_DEFAULT')
        else:
            draw.tag_redraw(context)
    elif part.startswith('LINE:'):
        state.detail_line = part.split(':', 1)[1]
        state.detail_thickness = espessura(context, state.detail_line)
        state.detail_error = ""
        draw.tag_redraw(context)
    elif part == 'OK':
        confirmar(context)
    elif part == 'CANCEL':
        fechar_painel(context)


def _commit(state, context):
    """Grava o texto do campo ativo; devolve False quando o texto não é número."""
    campo = state.detail_field
    valor = detail_core.parse_mm(state.detail_text)
    if valor is None:
        state.detail_error = tr("Medida inválida: {}").format(state.detail_text)
        draw.tag_redraw(context)
        return False
    set_valor(state, campo, valor)
    state.detail_field, state.detail_text = "", ""
    ok, mensagem = validar(context, state)
    state.detail_error = "" if ok else mensagem
    draw.tag_redraw(context)
    return True


class BTM_OT_LibraryDetailType(bpy.types.Operator):
    """Digitar a medida do campo escolhido no card do módulo"""

    bl_idname = "caffmob.library_detail_type"
    bl_label = "Digitar medida do módulo"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        state = getattr(context.window_manager, 'btm_library', None)
        return state is not None and state.detail_open and bool(state.detail_field)

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        draw.tag_redraw(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        state = context.window_manager.btm_library
        if not state.detail_open or not state.detail_field:
            return {'CANCELLED'}
        if event.value != 'PRESS':
            return {'PASS_THROUGH'} if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE') else {'RUNNING_MODAL'}
        if event.type == 'ESC':
            state.detail_field, state.detail_text = "", ""
            draw.tag_redraw(context)
            return {'FINISHED'}
        if event.type in ('RET', 'NUMPAD_ENTER', 'TAB'):
            _commit(state, context)
            return {'FINISHED'}
        if event.type == 'BACK_SPACE':
            state.detail_text = state.detail_text[:-1]
            draw.tag_redraw(context)
            return {'RUNNING_MODAL'}
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE'):
            _commit(state, context)
            return {'FINISHED'}
        if event.unicode and event.unicode in "0123456789.," and len(state.detail_text) < 10:
            state.detail_text += event.unicode
            draw.tag_redraw(context)
        return {'RUNNING_MODAL'}


classes = (BTM_OT_LibraryDetailType,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
