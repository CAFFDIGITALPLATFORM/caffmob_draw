"""Cotas fixas do item ativo (feature 066, T040; D-10, RF-013 a RF-020, RF-023; BUG-20261023-HYCE).

Quatro cotas, da superfície do conjunto ativo até a primeira referência de cada lado: esquerda e direita ao longo do
eixo da parede hospedeira (ou do X local do móvel livre), inferior e superior em Z (`measure/side.py`). A vista só
projeta o desenho: girar, deslocar ou aproximar a vista não muda o que é medido (RF02 da auditoria de cotas fixas). Cada
cota guarda o nome da referência; sem referência, o lado não tem cota (nunca um 0 fictício). Piso e teto valem só
quando não há nada mais perto.

O cálculo roda fora do desenho e dos campos: o timer (`_tick`, 150 ms) refaz o último cálculo (`_snap`) quando a cena
muda (`_revision`, por atualização do depsgraph, abrir, desfazer e refazer) ou muda o ativo; desenho e propriedades só
o leem (RF08). Editar uma cota (rótulo clicável, `caffmob.fixed_cota_edit`, ou o campo nas propriedades) move o
conjunto pela diferença, sem redimensionar, como ferramenta assistida: o guarda de colisão não limita (RF05, RF06).

Desenha só na viewport da operação, capturada ao ligar a chave ou mover o ativo (RF-020). Nada durante o render nem
com as sobreposições desligadas. A chave não mexe na colisão, e a colisão não mexe nela (RF-013).
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Vector  # type: ignore

_handles = []
_owner = [None]        # ponteiro da área que desenha as cotas
_revision = [0]        # muda a cada alteração da cena: invalida os caches abaixo
_snap = {'key': None, 'records': {}}     # último cálculo: lado → (Gap, nome da referência)
_labels = {}           # ponteiro da região → [(lado, retângulo do rótulo na tela)]
_addon_keymaps = []
SIDES = ('LEFT', 'RIGHT', 'TOP', 'BOTTOM')
TICK = 0.15
_HANDLERS = ('depsgraph_update_post', 'load_post', 'undo_post', 'redo_post')


@persistent
def _changed(*_args):
    _revision[0] += 1


def claims(area_ptr, alive):
    """A área `area_ptr` desenha? A dona continua enquanto existir; sem dona viva, a primeira que pedir fica."""
    owner = _owner[0]
    if owner is None or owner not in alive:
        _owner[0] = owner = area_ptr
    return owner == area_ptr


def release():
    _owner[0] = None


def bind(context):
    """Prende à área da ação; callbacks de desenho nunca roubam uma dona ainda viva."""
    area = getattr(context, 'area', None)
    if area is not None and area.type == 'VIEW_3D':
        _owner[0] = area.as_pointer()


def update_enabled(settings, context):
    release()
    if settings.show_side_dimensions:
        bind(context)
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _alive(context):
    try:
        return {a.as_pointer() for w in context.window_manager.windows for a in w.screen.areas
                if a.type == 'VIEW_3D'}
    except AttributeError:
        return set()


def _mover(obj):
    from ..selection import classify
    return classify.movable_root(obj) or obj


def _wall(obj):
    node = obj.parent
    while node is not None:
        if node.get('IS_WALL_BP'):
            return node
        node = node.parent
    return None


def _ref_name(obj):
    from ..selection import classify
    root = classify.movable_root(obj) or classify.reference_root(obj) or obj
    return root.name


def _key(context):
    obj = getattr(context, 'active_object', None)
    if obj is None or not obj.select_get():
        return None, None
    mover = _mover(obj)
    return (_revision[0], context.scene.as_pointer(), mover.session_uid), mover


def _compute(context, mover):
    """Lado → (Gap, nome da referência), no eixo fixo do conjunto. Usa o depsgraph: só fora do desenho e dos campos."""
    from ..collision import guard, rules
    from ..measure import scene_cotas, side
    from ..data.i18n import tr
    depsgraph = context.evaluated_depsgraph_get()
    guard._index.refresh(context.scene, depsgraph, {})
    body = guard._body(mover, depsgraph)
    if not body:
        return {}
    wall = _wall(mover)
    axis = side.fixed_axis(tuple(mover.matrix_world.to_3x3().col[0]),
                           tuple(wall.matrix_world.to_3x3().col[0]) if wall is not None else None)
    skip = guard._subtree_uids([mover])
    everywhere = ((-1.0e9,) * 3, (1.0e9,) * 3)
    entries = [e for e in guard._index.near(everywhere, skip) if not any(rules.excluded(it, e.item) for it in body)]
    obstacles = [e.item.box.corners() for e in entries]
    corners = [c for it in body for c in it.box.corners()]
    names = [_ref_name(e.obj) for e in entries]
    lateral = side.gaps(axis, corners, obstacles)
    vertical = side.vertical(axis, corners, obstacles, 0.0, scene_cotas.ceiling_height(context.scene, wall))
    special = {-1: tr("Piso"), -2: tr("Teto")}
    out = {}
    for name, gap in (('LEFT', lateral.left), ('RIGHT', lateral.right), ('BOTTOM', vertical.below),
                      ('TOP', vertical.above)):
        if gap is not None:
            out[name] = (gap, special.get(gap.ref) if gap.ref in special else names[gap.ref] if gap.ref is not None
                         else "")
    return {'axis': axis, 'gaps': out}


def snapshot(context, compute=True):
    """O último cálculo do ativo; com `compute`, refaz se a cena ou o ativo mudaram (nunca no desenho nem nos campos)."""
    key, mover = _key(context)
    if key is None:
        return {}
    if compute and _snap['key'] != key:
        _snap.update(key=key, records=_compute(context, mover))
    elif _snap['key'] is None or _snap['key'][1:] != key[1:]:
        return {}                     # outro ativo: o timer ainda não calculou
    return _snap['records']


def records(context, compute=True):
    """Lado → (valor em metros, nome da referência)."""
    return {name: (gap.value, ref) for name, (gap, ref) in snapshot(context, compute).get('gaps', {}).items()}


def specs(context, view_right=None, compute=True):
    """Cotas (`PlacementDimSpec`) do ativo, na ordem esquerda, direita, superior, inferior. `view_right` não muda nada
    (cotas fixas); fica pela compatibilidade."""
    from ..data import units
    from ..hb_placement import PlacementDimSpec
    gaps = snapshot(context, compute).get('gaps', {})
    return [PlacementDimSpec(Vector(gaps[name][0].start), Vector(gaps[name][0].end),
                             units.format_value(gaps[name][0].value)) for name in SIDES if name in gaps]


def apply_fixed(context, name, value):
    """Põe a cota `name` em `value` (metros) movendo o conjunto pela diferença; ValueError sem mover nada."""
    import math
    from ..collision import guard
    from ..data.i18n import tr
    if name not in SIDES:
        raise ValueError(tr("Cota desconhecida: {}").format(name))
    if not isinstance(value, (int, float)) or math.isnan(value) or math.isinf(value) or value < 0:
        raise ValueError(tr("Valor Inválido: a cota precisa ser um número positivo."))
    snap = snapshot(context, compute=True)
    record = snap.get('gaps', {}).get(name)
    if record is None:
        raise ValueError(tr("Este lado não tem referência para medir."))
    key, mover = _key(context)
    delta = value - record[0].value
    axis = Vector(snap['axis'])
    up = Vector((0.0, 0.0, 1.0))
    move = {'LEFT': axis * delta, 'RIGHT': -axis * delta, 'BOTTOM': up * delta, 'TOP': -up * delta}[name]
    with guard.suspended():                      # ferramenta assistida (RF06)
        world = mover.matrix_world.copy()
        world.translation += move
        mover.matrix_world = world
        context.view_layer.update()
        guard.accept(mover)
    _changed()
    return move


class _Specs:
    def __init__(self, items):
        self._placement_dim_specs = items
        self._placement_dim_safe_labels = True


def _label_rects(context, region, rv3d, items):
    """Retângulos dos rótulos na tela, no ponto médio de cada cota (onde `draw_placement_dimensions` escreve)."""
    import blf
    from bpy_extras import view3d_utils
    scale = context.preferences.system.ui_scale or 1.0
    out = []
    for name, spec in items:
        mid = view3d_utils.location_3d_to_region_2d(region, rv3d, (spec.start + spec.end) / 2.0)
        if mid is None:
            continue
        blf.size(0, 12 * scale)
        w = blf.dimensions(0, spec.text)[0] + 16 * scale
        h = 22 * scale
        out.append((name, (mid.x - w / 2.0, mid.y - h / 2.0, w, h)))
    return out


def _draw():
    context = bpy.context
    settings = getattr(context.scene, 'btm_settings', None)
    if settings is None or not settings.show_side_dimensions:
        release()
        return
    area, region, rv3d = context.area, context.region, context.region_data
    overlay = getattr(context.space_data, 'overlay', None)
    if area is None or rv3d is None or (overlay is not None and not overlay.show_overlays):
        return
    if bpy.app.is_job_running('RENDER'):
        return
    if not claims(area.as_pointer(), _alive(context)):
        return
    try:
        gaps = snapshot(context, compute=False).get('gaps', {})
        items = specs(context, compute=False)
        named = list(zip([n for n in SIDES if n in gaps], items))
        _labels[region.as_pointer()] = _label_rects(context, region, rv3d, named)
    except (ReferenceError, AttributeError, ValueError):
        return
    if items:
        from ..hb_placement import draw_placement_dimensions
        draw_placement_dimensions(_Specs(items), context)


def label_at(region, x, y):
    for name, (rx, ry, rw, rh) in _labels.get(region.as_pointer(), ()):
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            return name
    return None


def _tick():
    """Refaz o cálculo fora do desenho quando a cena ou o ativo mudam (RF08)."""
    try:
        context = bpy.context
        if bpy.app.is_job_running('RENDER') or getattr(context, 'scene', None) is None:
            return TICK
        key, _mover_obj = _key(context)
        if key is not None and key != _snap['key']:
            snapshot(context, compute=True)
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
    except (ReferenceError, AttributeError, RuntimeError, ValueError):
        pass
    return TICK


class BTM_OT_FixedCotaEdit(bpy.types.Operator):
    """Edita a distância da cota clicada; o conjunto anda pela diferença"""
    bl_idname = "caffmob.fixed_cota_edit"
    bl_label = "Editar cota"
    bl_options = {'REGISTER', 'UNDO'}

    side: bpy.props.EnumProperty(items=[('LEFT', "Esquerda", ""), ('RIGHT', "Direita", ""), ('TOP', "Superior", ""),
                                        ('BOTTOM', "Inferior", "")], options={'HIDDEN'})  # type: ignore
    value: bpy.props.FloatProperty(name="Distância", subtype='DISTANCE', unit='LENGTH', min=0.0)  # type: ignore
    mover_uid: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    pose: bpy.props.FloatVectorProperty(size=3, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        settings = getattr(context.scene, 'btm_settings', None)
        return settings is not None and settings.show_side_dimensions

    def invoke(self, context, event):
        region = context.region
        name = label_at(region, event.mouse_region_x, event.mouse_region_y) \
            if region is not None and context.area is not None and context.area.type == 'VIEW_3D' else None
        if name is None:
            return {'PASS_THROUGH'}
        record = records(context, compute=False).get(name)
        key, mover = _key(context)
        if record is None or mover is None:
            return {'PASS_THROUGH'}
        self.side, self.value = name, record[0]
        self.mover_uid, self.pose = mover.session_uid, tuple(mover.matrix_world.translation)
        return context.window_manager.invoke_props_dialog(self, title=tr_label(name, record[1]))

    def execute(self, context):
        from ..data.i18n import tr
        _key_now, mover = _key(context)
        if self.mover_uid and (mover is None or mover.session_uid != self.mover_uid
                               or (mover.matrix_world.translation - Vector(self.pose)).length > 1e-6):
            self.report({'WARNING'}, tr("O item ou a posição mudou durante a edição; nada foi alterado."))
            return {'CANCELLED'}
        try:
            apply_fixed(context, self.side, self.value)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


def tr_label(name, ref):
    from ..data.i18n import tr
    side = {'LEFT': tr("Esquerda"), 'RIGHT': tr("Direita"), 'TOP': tr("Superior"), 'BOTTOM': tr("Inferior")}[name]
    return tr("Cota {} até {}").format(side, ref) if ref else side


def register():
    from ..move_over.ops_drag import VIEW3D_MODE_KEYMAPS
    bpy.utils.register_class(BTM_OT_FixedCotaEdit)
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))
    for name in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if _changed not in handlers:
            handlers.append(_changed)
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK, persistent=True)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:                   # o clique no rótulo vem antes da seleção, também nos mapas de modo
        for name, space in [('3D View', 'VIEW_3D')] + [(m, 'EMPTY') for m in VIEW3D_MODE_KEYMAPS]:
            km = kc.keymaps.new(name=name, space_type=space)
            _addon_keymaps.append((km, km.keymap_items.new(BTM_OT_FixedCotaEdit.bl_idname, 'LEFTMOUSE', 'PRESS',
                                                           head=True)))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
    for name in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if _changed in handlers:
            handlers.remove(_changed)
    _changed()
    _snap.update(key=None, records={})
    _labels.clear()
    release()
    if BTM_OT_FixedCotaEdit.is_registered:
        bpy.utils.unregister_class(BTM_OT_FixedCotaEdit)
