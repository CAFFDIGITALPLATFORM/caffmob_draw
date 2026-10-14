"""Abrir, editar, confirmar e cancelar no Editor de Armário (feature 004, T045, T047; RF-01, RF-05, RF-08, RN-01,
RN-04, D-21, D-22, D-26).

- `caffmob.cabinet_editor`: abre a janela para o módulo selecionado e inicia o modal.
- `caffmob.cabinet_editor_modal` (`UNDO`): executa os pedidos dos botões do painel (que não têm `UNDO`), trata o clique
  na vista frontal e o Ctrl+Z / Ctrl+Shift+Z do rascunho. Como tudo acontece dentro dele, o Blender cria um passo de
  desfazer só quando ele termina com Confirmar (`FINISHED`). Cancelar reaplica o instantâneo inicial e devolve
  `CANCELLED`. Se a janela do sistema for fechada, o módulo volta ao inicial e a barra de status avisa.
- `caffmob.cabinet_editor_confirm` / `_cancel` / `_close`: botões do painel.

Feature 006 (T023): o `refresh` calcula os subvãos (vista e lista), valida divisões (`DIV-*`) e espessuras (`STR-*`) e
espelha as listas de componentes externos e de divisões; na aba Divisão, o clique na vista escolhe o subvão (D-13).

Feature 008 (T030, T031; D-04 a D-06, D-16):
- **Aplicar** (`apply`): `ed.undo_push` + `Draft.apply_point`; o Cancelar passa a voltar ao estado aplicado; **OK** é o
  Confirmar (aplica e fecha);
- o clique escolhe a **peça** quando cai numa chapa e o **vão** quando cai em área livre ou numa frente (frentes cobrem
  o vão, como no Construtor); vale em qualquer aba;
- o vão da biblioteca que contém o vão alvo (`library_path`, `library_box`) alimenta Gavetas e Portas;
- setas movem a divisória selecionada pelo Passo (o primeiro toque usa o Passo inicial).
"""

import bpy  # type: ignore

from ..data import units
from ..data.i18n import N_, tr
from . import bridge, divisions as dv, elevation, props, state, structure as st, validate, window
from .scene_divisions import configured as division_material

TIMER_STEP = 0.1


# Sessão ----------------------------------------------------------------------------------------------------
def _sync_ui(context, s):
    ui = context.window_manager.btm_cabinet_editor
    flagged = {m.component for m in s.messages if m.component}
    ui.components.clear()
    selected_index = -1
    for index, part in enumerate(sorted(s.parts, key=lambda p: (p.kind != elevation.OPENING, p.name))):
        row = ui.components.add()
        row.name, row.kind, row.flagged = part.name, part.kind, part.name in flagged
        row.label = part.name
        if part.name == s.selected:
            selected_index = index
    if ui.component_index != selected_index:
        props._session[0] = None                  # sem disparar o `update` do índice
        ui.component_index = selected_index
        props._session[0] = s
    ui.messages.clear()
    for m in validate.sort_messages(s.messages):
        row = ui.messages.add()
        row.code, row.severity, row.component, row.parameter = m.code, m.severity, m.component, m.parameter
        row.value, row.range, row.action, row.blocks = m.value, m.range, m.action, m.blocks
    ui.adjustments.clear()
    for name, change in s.adjustments:
        row = ui.adjustments.add()
        row.component, row.change = name, change
    _sync_006(context, s, ui, flagged)


def _fmt(context, value):
    return units.format_length(value, _unit(context))


def _sync_006(context, s, ui, flagged):
    """Espelhos das abas Estrutura e Divisão (feature 006)."""
    root = s.root()
    ui.structure.clear()
    ui.divisions.clear()
    if root is None:
        return
    for role, info, caps, rstate in bridge.structure_rows(context, root):
        row = ui.structure.add()
        row.role, row.label = role, tr(st.ROLE_LABELS[role])
        length, width = info['size']
        row.size = "{} × {}".format(_fmt(context, length), _fmt(context, width))
        material, _thickness = bridge.configured_part(context, root, role)
        row.material = rstate.material or material
        row.thickness = _fmt(context, rstate.thickness or info['thickness'])
        row.removed, row.mode, row.changed = rstate.removed, rstate.mode, rstate.changed
        row.reason_remove = caps.get('remove') or ""
        row.reason_edit = caps.get('thickness') or ""
    material, thickness = division_material(context.scene, root)
    for obj in sorted(bridge.scene_divisions.objects(root), key=lambda o: o.name):
        d = obj.btm_division
        row = ui.divisions.add()
        row.uid, row.label, row.flagged = d.uid, obj.name, obj.name in flagged
        parts = [tr("Vertical") if d.orientation == dv.VERTICAL else tr("Horizontal"), _fmt(context, d.offset)]
        if d.use_front:
            parts.append(tr("frente {}").format(_fmt(context, d.front)))
        if d.use_back:
            parts.append(tr("trás {}").format(_fmt(context, d.back)))
        parts.append("{} {}".format(d.material or material, _fmt(context, d.thickness or thickness)))
        row.detail = " · ".join(parts)


_TOKEN_LABELS = {'LEFT': "esquerdo", 'RIGHT': "direito", 'BOTTOM': "de baixo", 'TOP': "de cima"}


def space_label(path, core):
    words = []
    for token in dv.space_tokens(path, core):
        if token[0] == 'ROOT':
            words.append(tr("Vão {}").format(token[1]))
        else:
            words.append(tr(_TOKEN_LABELS[token[0]]))
    return " › ".join(words)


def _divisions_refresh(context, s, root):
    """Subvãos (no referencial da vista), rótulos, peças removidas e mensagens `DIV-*`/`STR-*`."""
    roots, core, _raw, names = bridge.division_context(context, root)
    leaves, _cuts, _orphans = dv.resolve(roots, core)
    shift = bridge.view_shift(context, root)
    s.spaces = {path: dv.Box(tuple(box.lo[i] - shift[i] for i in range(3)),
                             tuple(box.hi[i] - shift[i] for i in range(3))) for path, box in leaves.items()}
    s.space_labels = {path: space_label(path, core) for path in s.spaces}
    if s.space not in s.spaces:
        s.space = min(s.spaces) if s.spaces else ""
    messages = dv.validate(roots, core, _unit(context), names)
    for role, values in root.btm_structure.to_dict().items():
        messages += st.check_thickness(role, values.get('thickness', 0.0), _unit(context))
    removed = set()
    adapter = bridge.adapter_of(root)
    if adapter is not None:
        from ..customize.adapters import common
        parts = common.call(adapter, 'structure_parts', root)
        for role in common.removed_roles(root):
            removed.update(o.name for o in parts.get(role, ()))
            removed.add(tr(st.ROLE_LABELS[role]))
    s.removed_parts = [p for p in s.initial_parts if p.name in removed]
    _library_refresh(context, s, root, shift)
    return messages


def _library_refresh(context, s, root, shift):
    """Vão da biblioteca que contém o vão alvo, no referencial da vista (D-05)."""
    s.library_path, s.library_box = None, None
    if not s.space:
        return
    path = bridge.library_opening(context, root, s.space)
    if path is None:
        return
    adapter = bridge.adapter_of(root)
    from ..customize.adapters import common
    box = common.call(adapter, 'opening_boxes', context, root).get(path)
    s.library_path = path
    if box is not None:
        s.library_box = dv.Box(tuple(box.lo[i] - shift[i] for i in range(3)), tuple(box.hi[i] - shift[i] for i in range(3)))


def refresh(context, s, library_messages=(), checkpoint=True):
    """Relê o módulo, valida, calcula os ajustes automáticos e grava um passo do rascunho."""
    root = s.root()
    if root is None:
        return
    s.parts = bridge.parts(context, root)
    if s.selected and not any(p.name == s.selected for p in s.parts):
        s.selected = None
    current = bridge.read_state(root)
    if checkpoint:
        s.draft.checkpoint(current)
    else:
        s.draft.current = current
    s.adjustments = elevation.diff(s.initial_parts, s.parts, targets=s.edited)
    size = bridge.root_size(context, root)
    msgs = list(s.dim_messages.values())
    msgs = [m for group in msgs for m in group]
    msgs += validate.outside_volume((size[0], size[1], size[2]), s.parts)
    msgs += validate.internal_overlaps(s.parts)
    msgs += _divisions_refresh(context, s, root)
    msgs += [validate.Message('LIB-001', validate.WARNING, '', '', '', '', text) for text in library_messages]
    s.messages = msgs
    _sync_ui(context, s)
    s.redraw()


def _unit(context):
    return units.get_scene_length_unit(context.scene)


def process(context, s):
    """Executa os pedidos pendentes (botões do painel); devolve True quando algo mudou."""
    changed = False
    while s.requests:
        kind, data = s.requests.pop(0)
        root = s.root()
        if root is None:
            return changed
        s.error = ""                      # limpa antes: o erro que a ação definir fica visível (DT-08)
        try:
            if kind == 'dimension':
                field, value = data
                msgs = validate.check_dimension(field, value, s.limits, _unit(context))
                s.dim_messages[field] = msgs
                if not msgs:
                    bridge.set_dimension(context, root, field, value)
                refresh(context, s, checkpoint=not msgs)
            elif kind == 'edit':
                action, payload = data
                s.edited.update(n for n in payload.get('targets', ()) if n)
                refresh(context, s, bridge.edit(context, root, action, payload))
            elif kind == 'apply':
                _apply_now(context, s)
            elif kind == 'arrow':
                _arrow(context, s, root, *data)
            elif kind in ('undo', 'redo'):
                target = s.draft.undo() if kind == 'undo' else s.draft.redo()
                if target is None:
                    s.error = N_("Nada para desfazer.") if kind == 'undo' else N_("Nada para refazer.")
                    continue
                s.dim_messages.clear()
                refresh(context, s, bridge.apply_state(context, root, target), checkpoint=False)
                s.draft.current = target
        except (ValueError, RuntimeError) as exc:
            s.error = str(exc)
        changed = True
    return changed


def _apply_now(context, s):
    """Aplicar (D-04): grava um passo de desfazer na cena e o estado vira a referência do Cancelar."""
    if s.blocking() or not s.draft.dirty():
        return
    bpy.ops.ed.undo_push(message=tr("Editor de armário: Aplicar"))
    s.draft.apply_point()
    s.initial_parts = list(s.parts)
    s.edited.clear()
    s.applied = True
    refresh(context, s, checkpoint=False)


def _selected_division(s, root):
    obj = bpy.data.objects.get(s.selected) if s.selected else None
    if obj is None or obj.parent != root or not obj.btm_division.is_division:
        return None
    return obj


def _arrow(context, s, root, axis, direction):
    """Seta: move a divisória selecionada pelo Passo, se a orientação dela andar nesse eixo (D-16)."""
    from . import position, scene_divisions
    obj = _selected_division(s, root)
    if obj is None:
        s.error = N_("Selecione uma divisória na vista para mover com as setas")
        return
    data = obj.btm_division
    if (axis == 'X') != (data.orientation == dv.VERTICAL):
        return
    roots, core, _raw, _names = bridge.division_context(context, root)
    _leaves, cuts, _orphans = dv.resolve(roots, core)
    division = next((d for d in core if d.uid == data.uid), None)
    if division is None or division.uid not in cuts:
        return
    ui = context.window_manager.btm_cabinet_editor
    first = s.last_moved != data.uid
    offset = position.step_move(cuts[division.uid][0], division, direction, ui.step, ui.step_initial, first=first)
    s.last_moved = data.uid
    refresh(context, s, bridge.edit(context, root, 'EDIT_DIVISION', {'uid': data.uid, 'offset': offset}))
    scene_divisions.reflow(context, root, force=True)


def _boards(s, x, z):
    """Chapas que o clique pode escolher: não frentes nem vãos, nem as que cobrem o vão inteiro sob o clique (o fundo,
    na vista frontal, fica atrás de tudo e não pode roubar a escolha do vão)."""
    space = s.spaces.get(dv.space_at(s.spaces, x, z) or "")

    def covers(part):
        x0, z0, x1, z1 = part.rect
        return (space is not None and x0 <= space.lo[0] + 1e-6 and x1 >= space.hi[0] - 1e-6
                and z0 <= space.lo[2] + 1e-6 and z1 >= space.hi[2] - 1e-6)
    return [p for p in s.parts if p.kind not in (elevation.FRONT, elevation.OPENING) and not covers(p)]


def rollback(context, s):
    """Devolve o módulo ao instantâneo inicial (Cancelar, janela fechada)."""
    root = s.root()
    if root is not None and s.draft.dirty():
        bridge.apply_state(context, root, s.draft.initial)


def start_session(context, root):
    info = bridge.info_of(root)
    draft = state.Draft(bridge.read_state(root))
    s = props.start(root.name, info.library, draft)
    converted = bridge.migrate_structure(context, root)          # feature 015 (RN-22): depois do instantâneo
    if converted:
        draft.checkpoint(bridge.read_state(root))
    s.limits = validate.limits_for(bridge.library_limits(root, info.library))
    s.dim_messages = {}
    s.edited = set()
    s.view_key = None
    s.parts = bridge.parts(context, root)
    s.initial_parts = list(s.parts)
    s.space, s.spaces, s.space_labels, s.removed_parts = "", {}, {}, []
    s.library_path, s.library_box, s.last_moved, s.applied = None, None, None, False
    context.window_manager.btm_cabinet_editor.tab = 'STRUCTURE'       # abre sempre na Estrutura (RF-01)
    _divisions_refresh(context, s, root)
    _sync_ui(context, s)
    return s


# Operadores ------------------------------------------------------------------------------------------------
def module_root(context):
    from ..customize import adapters
    root, adapter = adapters.for_object(context.active_object)
    return root if adapter is not None else None


class BTM_OT_CabinetEditor(bpy.types.Operator):
    """Abre o Editor de Armário do módulo selecionado: vista frontal, componentes, medidas e personalização, com
    Confirmar e Cancelar"""
    bl_idname = "caffmob.cabinet_editor"
    bl_label = "Abrir editor de armário"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.window is None or props.session() is not None:
            return False
        if module_root(context) is None:
            cls.poll_message_set(tr("Selecione um módulo"))
            return False
        return True

    def execute(self, context):
        root = module_root(context)
        s = start_session(context, root)
        try:
            win, area, region = window.open_editor(context)
        except RuntimeError as exc:
            props.end()
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        with context.temp_override(window=win, area=area, region=region):
            bpy.ops.caffmob.cabinet_editor_modal('INVOKE_DEFAULT')
        s.redraw()
        return {'FINISHED'}


class BTM_OT_CabinetEditorModal(bpy.types.Operator):
    """Interação do Editor de Armário"""
    bl_idname = "caffmob.cabinet_editor_modal"
    bl_label = "Editor de Armário"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _timer = None

    def invoke(self, context, event):
        if props.session() is None:
            return {'CANCELLED'}
        self.tab_ready = False
        self._timer = context.window_manager.event_timer_add(TIMER_STEP, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context, keep):
        s = props.session()
        if s is not None and not keep:
            rollback(context, s)
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if s is not None:
            window.close_later(s)
            props.end()
            ui = context.window_manager.btm_cabinet_editor
            ui.components.clear()
            ui.messages.clear()
            ui.adjustments.clear()
            ui.structure.clear()
            ui.divisions.clear()

    def cancel(self, context):
        self._end(context, False)

    def modal(self, context, event):
        s = props.session()
        if s is None:
            self._end(context, False)
            return {'CANCELLED'}
        if s.root() is None:
            self._end(context, False)
            self.report({'WARNING'}, tr("O módulo não existe mais; o editor foi fechado"))
            return {'CANCELLED'}
        if not window.window_alive(context):
            dirty = s.draft.dirty()
            self._end(context, False)
            if dirty:
                from ..ui import save_feedback
                save_feedback.show(tr("Editor fechado: alterações descartadas"))
            return {'CANCELLED'}
        if s.request == 'cancel':
            s.requests.clear()            # o que estava na fila não roda depois do Cancelar (DT-02)
            self._end(context, False)
            return {'CANCELLED'}
        if s.request == 'ok':
            process(context, s)           # o último botão antes do OK também vale (DT-02)
            self._end(context, True)
            self.report({'INFO'}, tr("Armário atualizado: {}").format(s.root_name))
            return {'FINISHED'}
        if process(context, s):
            return {'RUNNING_MODAL'}
        if event.type == 'TIMER':
            if not self.tab_ready:
                _win, area, _region = window.editor_area(context)
                self.tab_ready = window.focus_tab(area)
            return {'PASS_THROUGH'}
        if self._handle_undo(event, s):
            return {'RUNNING_MODAL'}
        if self._handle_arrows(context, event, s):
            return {'RUNNING_MODAL'}
        return self._handle_click(context, event, s)

    _ARROWS = {'LEFT_ARROW': ('X', -1), 'RIGHT_ARROW': ('X', +1), 'DOWN_ARROW': ('Z', -1), 'UP_ARROW': ('Z', +1)}

    def _handle_arrows(self, context, event, s):
        if event.value != 'PRESS' or event.type not in self._ARROWS:
            return False
        _win, area, region = window.editor_area(context)
        if region is None or window.over_side_panel(area, event.mouse_x, event.mouse_y):
            return False
        s.push('arrow', self._ARROWS[event.type])
        return True

    def _handle_undo(self, event, s):
        if event.value != 'PRESS' or event.type not in {'Z', 'Y'} or not (event.ctrl or event.oskey):
            return False
        s.push('redo' if (event.type == 'Y' or event.shift) else 'undo')
        return True

    def _handle_click(self, context, event, s):
        _win, area, region = window.editor_area(context)
        if region is None or window.over_side_panel(area, event.mouse_x, event.mouse_y):
            return {'PASS_THROUGH'}
        pixel = (event.mouse_x - region.x, event.mouse_y - region.y)
        if not (0 <= pixel[0] <= region.width and 0 <= pixel[1] <= region.height):
            return {'PASS_THROUGH'}
        view = window.ensure_view(region, area)
        if event.type == 'WHEELUPMOUSE':
            view.zoom(1.15, pixel)
        elif event.type == 'WHEELDOWNMOUSE':
            view.zoom(1 / 1.15, pixel)
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            x, z = view.to_world(pixel)
            board = elevation.hit(_boards(s, x, z), x, z)
            if board is not None:
                s.selected = board                                         # peça: chapa sob o clique (D-06)
            else:
                s.selected = None
                s.space = dv.space_at(s.spaces, x, z) or s.space          # vão: área livre ou frente
                root = s.root()
                if root is not None:
                    _library_refresh(context, s, root, bridge.view_shift(context, root))
            _sync_ui(context, s)
        elif event.type == 'ESC' and event.value == 'PRESS':
            bpy.ops.caffmob.cabinet_editor_close('INVOKE_DEFAULT')
        else:
            return {'PASS_THROUGH'}
        s.redraw()
        return {'RUNNING_MODAL'}


class BTM_OT_CabinetEditorConfirm(bpy.types.Operator):
    """Aplica as alterações do editor ao armário (um passo de desfazer)"""
    bl_idname = "caffmob.cabinet_editor_confirm"
    bl_label = "Confirmar"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        s = props.session()
        if s is None:
            return False
        if s.blocking():
            cls.poll_message_set(tr("Corrija os erros para confirmar"))
            return False
        return True

    def execute(self, context):
        props.session().request = 'ok'
        return {'FINISHED'}


class BTM_OT_CabinetEditorCancel(bpy.types.Operator):
    """Fecha o editor e devolve o armário como estava ao abrir"""
    bl_idname = "caffmob.cabinet_editor_cancel"
    bl_label = "Cancelar"
    bl_options = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        s = props.session()
        if s is not None and s.draft.dirty():
            return context.window_manager.invoke_confirm(
                self, event, title=tr("Descartar alterações"), message=tr("Descartar as alterações e fechar o editor?"),
                confirm_text=tr("Descartar"), icon='WARNING')
        return self.execute(context)

    def execute(self, context):
        s = props.session()
        if s is not None:
            s.request = 'cancel'
        return {'FINISHED'}


class BTM_OT_CabinetEditorClose(bpy.types.Operator):
    """Fecha o editor; com alterações pendentes, pergunta o que fazer"""
    bl_idname = "caffmob.cabinet_editor_close"
    bl_label = "Fechar"
    bl_options = {'REGISTER', 'INTERNAL'}

    choice: bpy.props.EnumProperty(
        name="Alterações pendentes",
        items=[('CONTINUE', "Continuar editando", "Volta ao editor"),
               ('DISCARD', "Descartar", "Fecha e devolve o armário como estava"),
               ('CONFIRM', "Confirmar", "Aplica as alterações e fecha")],
        default='CONTINUE')  # type: ignore

    def invoke(self, context, event):
        s = props.session()
        if s is not None and s.draft.dirty():
            self.choice = 'CONTINUE'
            return context.window_manager.invoke_props_dialog(self, title=tr("O armário tem alterações"))
        return self.execute(context)

    def draw(self, context):
        self.layout.prop(self, "choice", expand=True)

    def execute(self, context):
        s = props.session()
        if s is None:
            return {'CANCELLED'}
        if not s.draft.dirty() or self.choice == 'DISCARD':
            s.request = 'cancel'
        elif self.choice == 'CONFIRM':
            if s.blocking():
                self.report({'WARNING'}, tr("Corrija os erros para confirmar"))
                return {'CANCELLED'}
            s.request = 'ok'
        return {'FINISHED'}


classes = (BTM_OT_CabinetEditor, BTM_OT_CabinetEditorModal, BTM_OT_CabinetEditorConfirm, BTM_OT_CabinetEditorCancel,
           BTM_OT_CabinetEditorClose)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
