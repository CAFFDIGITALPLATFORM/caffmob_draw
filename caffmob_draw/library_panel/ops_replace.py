"""Operador 'Substituir pelo selecionado' (`caffmob.library_replace_selected`, feature 078, T026; D-11 a D-13, RF-09 a RF-12).

Lê o item selecionado na cena (porta/janela do Home Builder, abertura do contrato v2, abertura importada do Promob ou
módulo de armário CAFFMob), valida a compatibilidade estrita de família (`porta ↔ porta`, `janela ↔ janela`,
`móvel ↔ móvel`) com o modelo selecionado na Biblioteca CAFFMob e realiza a troca preservando posição, orientação e
dimensões em um único passo de Desfazer (`bl_options = {'REGISTER', 'UNDO'}`).
"""

import json
import bmesh  # type: ignore
import bpy  # type: ignore

from ..data.i18n import tr
from ..geometry import door_controller
from ..geometry.mesh_gen import clear_mesh, generate_cabinet_mesh
from ..openings import door_core, sync as openings_sync
from . import draw, models_core, replace_core

PRESET_EXTRA_PROP = "btm_preset_extra"


def _add_box_to_bm(bm, x0, x1, y0, y1, z0, z1):
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    for a, b, c, d in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new((verts[a], verts[b], verts[c], verts[d]))


def sync_preset_extras(cabinet_obj):
    """Cria ou atualiza frentes de gaveta (`btm_drawers > 0`) e o segundo braço de canto (`btm_corner_kind` L/OBLIQUE)."""
    if cabinet_obj is None or getattr(cabinet_obj, 'btm_cabinet', None) is None:
        return
    for child in list(cabinet_obj.children):
        if child.get(PRESET_EXTRA_PROP):
            mesh = child.data if child.type == 'MESH' else None
            bpy.data.objects.remove(child, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    cab = cabinet_obj.btm_cabinet
    w, h, d, t = float(cab.width), float(cab.height), float(cab.depth), float(cab.thickness)
    drawers = int(cabinet_obj.get('btm_drawers') or 0)
    corner_kind = str(cabinet_obj.get('btm_corner_kind') or 'NONE')
    right_w = float(cabinet_obj.get('btm_right_width_mm') or 0.0) / 1000.0
    col = cabinet_obj.users_collection[0] if cabinet_obj.users_collection else bpy.context.scene.collection

    if drawers > 0:
        gap = 0.003
        dh = max(0.02, (h - gap * (drawers + 1)) / drawers)
        for i in range(drawers):
            z0 = gap + i * (dh + gap)
            mesh = bpy.data.meshes.new(f"{cabinet_obj.name}_Drawer_{i + 1}")
            child = bpy.data.objects.new(f"{cabinet_obj.name}_Drawer_{i + 1}", mesh)
            col.objects.link(child)
            child.parent = cabinet_obj
            child[PRESET_EXTRA_PROP] = "DRAWER_FRONT"
            bm = bmesh.new()
            _add_box_to_bm(bm, gap, w - gap, -d - t, -d, z0, z0 + dh)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()

    if corner_kind in ('L', 'OBLIQUE') and right_w > 0.05:
        mesh = bpy.data.meshes.new(f"{cabinet_obj.name}_Corner_{corner_kind}")
        child = bpy.data.objects.new(f"{cabinet_obj.name}_Corner_{corner_kind}", mesh)
        col.objects.link(child)
        child.parent = cabinet_obj
        child[PRESET_EXTRA_PROP] = f"CORNER_{corner_kind}"
        bm = bmesh.new()
        # Segundo braço se estende ao longo de -Y na extremidade direita (+X) do módulo
        arm_d = min(d, right_w * 0.65)
        _add_box_to_bm(bm, w - arm_d, w, -right_w, -d, 0.0, h)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()


def _resolve_root_and_target(scene, obj):
    """A partir de um objeto selecionado na cena, devolve `(chave_unica, obj_raiz, SelectionTarget)`."""
    curr = obj
    while curr is not None:
        # 1. Abertura v2 direta ou peça filha dela
        if curr.get('caffmob_tipo') == 'abertura':
            raw = curr.get('caffmob_abertura') or curr.get('caffmob_entidade_v2')
            if raw:
                ab = json.loads(raw)
                fam = 'WINDOW' if ab.get('tipo') == 'WINDOW' else 'DOOR'
                wall_mm = float(curr.get('caffmob_espessura_mm') or 150.0)
                return (
                    f"v2:{ab['id']}",
                    curr,
                    replace_core.SelectionTarget(
                        family=fam,
                        width_mm=float(ab.get('largura', 800.0)),
                        height_mm=float(ab.get('altura', 2100.0)),
                        depth_mm=wall_mm,
                        sill_mm=float(ab.get('peitoril', 0.0)),
                        wall_thickness_mm=wall_mm,
                    ),
                )
        # 2. Grupo de folhas importado do Promob (`btm_promob_abertura`) -> aponta para a abertura v2 correspondente
        promob_ab_id = curr.get('btm_promob_abertura')
        if promob_ab_id and scene is not None:
            v2_root = next(
                (o for o in scene.objects if o.get('caffmob_tipo') == 'abertura' and o.get('caffmob_id') == promob_ab_id),
                None,
            )
            if v2_root is not None:
                return _resolve_root_and_target(scene, v2_root)

        # 3. Caixa de porta/janela do Home Builder (`IS_ENTRY_DOOR_BP` / `IS_WINDOW_BP`)
        if openings_sync.is_opening(curr):
            kind = openings_sync.kind_of(curr)
            fam = 'WINDOW' if kind == 'WINDOW' else 'DOOR'
            w_m, wall_m, h_m = openings_sync._dims(curr)
            sill_mm = max(0.0, float(curr.location.z) * 1000.0) if fam == 'WINDOW' else 0.0
            return (
                f"hb:{curr.as_pointer()}",
                curr,
                replace_core.SelectionTarget(
                    family=fam,
                    width_mm=round(w_m * 1000.0, 3),
                    height_mm=round(h_m * 1000.0, 3),
                    depth_mm=round(wall_m * 1000.0, 3),
                    sill_mm=round(sill_mm, 3),
                    wall_thickness_mm=round(wall_m * 1000.0, 3),
                ),
            )

        # 4. Módulo de armário CAFFMob
        if getattr(curr, 'btm_plane', None) is not None and curr.btm_plane.object_kind == 'MODULE':
            cab = curr.btm_cabinet
            width, height, depth = _physical_dims(curr)
            return (
                f"mod:{curr.as_pointer()}",
                curr,
                replace_core.SelectionTarget(
                    family='MODULE',
                    width_mm=round(width * 1000.0, 3),
                    height_mm=round(height * 1000.0, 3),
                    depth_mm=round(depth * 1000.0, 3),
                    sill_mm=0.0,
                    wall_thickness_mm=0.0,
                    right_width_mm=float(curr.get('btm_right_width_mm') or 0.0),
                    corner_kind=str(curr.get('btm_corner_kind') or 'NONE'),
                    line=str(cab.line or 'COZ'),
                ),
            )
        curr = curr.parent

    return (
        f"unsupported:{obj.as_pointer()}",
        obj,
        replace_core.SelectionTarget(family='UNSUPPORTED', width_mm=0.0, height_mm=0.0),
    )


def inspect_scene_selection(context):
    """Devolve `([(obj_raiz, SelectionTarget), ...])` sem duplicar peças da mesma raiz."""
    scene = context.scene if context is not None else None
    selected = list(getattr(context, 'selected_objects', None) or [])
    active = getattr(context, 'active_object', None)
    if active is not None and active.select_get() and active not in selected:
        selected.insert(0, active)
    seen = {}
    ordered = []
    for obj in selected:
        key, root, target = _resolve_root_and_target(scene, obj)
        if key not in seen:
            seen[key] = (root, target)
            ordered.append((root, target))
    return ordered


def active_library_candidate(context, model_id=""):
    """Encontra o candidato ativo na Biblioteca (`model_id` explícito ou `draw._selected['id']`)."""
    if model_id:
        found = models_core.find_any(model_id)
        if found is not None:
            return found
    sel_id = draw._selected.get('id') or ""
    if sel_id.startswith("BLK:MODEL:") or sel_id.startswith("BLK:PRESET:") or sel_id.startswith("BLK:OPENING:"):
        mid = sel_id.split(":", 2)[2]
        return models_core.find_any(mid)
    if sel_id:
        state = getattr(context.window_manager, 'btm_library', None) if context and context.window_manager else None
        if state is not None:
            for entry in draw.grid_entries(state):
                if draw.entry_key(entry) == sel_id:
                    return entry
        return models_core.find_any(sel_id)
    return None


def _physical_dims(root):
    """080 D-11: a origem vale pela medida física (escala própria e dos ancestrais), não pelo parâmetro cru."""
    from ..selection import module_resize
    cab = root.btm_cabinet
    try:
        _params, _own, _world, phys = module_resize.measure(root, 'BTM')
    except ValueError:
        return float(cab.width), float(cab.height), float(cab.depth)
    width, depth, height = phys
    return width, height, depth


_REPLACE_PROPS = ('cabinet_type', 'line', 'door_swing', 'shelves', 'structure_id') + tuple(
    'has_' + role for role in ('top', 'bottom', 'back', 'left', 'right'))
_REPLACE_KEYS = ('btm_model_id', 'btm_drawers', 'btm_corner_kind', 'btm_right_width_mm')


def _replacement_state(root):
    cab = root.btm_cabinet
    return ({name: getattr(cab, name) for name in _REPLACE_PROPS},
            {key: root[key] for key in _REPLACE_KEYS if key in root})


def _restore_replacement(context, root, saved):
    """Rollback do `execute` (080 D-11): volta o tipo e as marcas; as medidas e a escala já voltaram na transação."""
    from ..data.properties import back_setback_of, structure_of, suspended_geometry
    props, keys = saved
    cab = root.btm_cabinet
    with suspended_geometry():
        for name, value in props.items():
            setattr(cab, name, value)
    for key in _REPLACE_KEYS:
        if key in keys:
            root[key] = keys[key]
        elif key in root:
            del root[key]
    generate_cabinet_mesh(root, cab.width, cab.height, cab.depth, float(cab.thickness), cab.shelves,
                          structure=structure_of(cab), back_setback=back_setback_of(root), assembly=cab.assembly)
    door_controller.update_door_geometry_and_controller(root)
    sync_preset_extras(root)
    context.view_layer.update()


def _apply_module_replacement(context, root, plan):
    from ..data.properties import back_setback_of, structure_of, suspended_geometry
    from ..operators.cabinet_builder import _ROLE_PROPS, standard_defaults
    from ..cabinet_editor import structures_core

    cab = root.btm_cabinet
    found, _definition = standard_defaults(context, plan.line, plan.cabinet_type)
    w = plan.width_mm / 1000.0
    h = plan.height_mm / 1000.0
    d = plan.depth_mm / 1000.0
    carcass = float(cab.thickness or found.carcass)
    recipe = structures_core.get(plan.structure_id) if plan.structure_id else None

    from ..selection import classify, editing, module_resize
    info = classify.classify(root)
    transactional = module_resize.handles(info) and info.root == root
    with suspended_geometry():
        if not transactional:
            cab.width, cab.height, cab.depth = w, h, d
        cab.cabinet_type = plan.cabinet_type
        cab.line = plan.line
        cab.door_swing = plan.door_swing
        cab.shelves = plan.shelves
        cab.structure_id = plan.structure_id or ""
        if recipe is not None:
            for role in _ROLE_PROPS:
                setattr(cab, 'has_' + role.lower(), recipe.has(role))

    root['btm_model_id'] = plan.model_id
    root['btm_drawers'] = int(plan.drawers)
    root['btm_corner_kind'] = plan.corner_kind
    root['btm_right_width_mm'] = float(plan.right_width_mm)

    if transactional:
        # 080 D-11: as medidas físicas do destino entram pela transação, que assa a escala (destino com ±1) e
        # recusa fora da faixa sem cortar; o parâmetro passa a ser a medida física ÷ escala dos ancestrais.
        editing.set_dimensions(context, info, {'width': w, 'height': h, 'depth': d})
        w, h, d = float(cab.width), float(cab.height), float(cab.depth)
    generate_cabinet_mesh(
        root, w, h, d, carcass, plan.shelves,
        structure=structure_of(cab), back_setback=back_setback_of(root), assembly=cab.assembly
    )
    door_controller.update_door_geometry_and_controller(root)
    sync_preset_extras(root)


class BTM_OT_LibraryReplaceSelected(bpy.types.Operator):
    """Substitui a abertura ou o móvel selecionado na cena pelo modelo escolhido na Biblioteca CAFFMob"""
    bl_idname = "caffmob.library_replace_selected"
    bl_label = "Substituir pelo selecionado"
    bl_options = {'REGISTER', 'UNDO'}

    model_id: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore
    material: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context is not None and context.scene is not None

    def execute(self, context):
        pairs = inspect_scene_selection(context)
        targets = [t for _r, t in pairs]
        candidate = active_library_candidate(context, self.model_id)

        ok, reason = replace_core.validate_replacement(targets, candidate)
        if not ok:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}

        root, target = pairs[0]
        state = getattr(context.window_manager, 'btm_library', None) if context.window_manager else None
        active_mat = self.material or (getattr(state, 'opening_material', "") if state is not None else "")

        std_width_mm = 800.0
        if target.family == 'MODULE':
            try:
                from ..operators.cabinet_builder import standard_defaults
                model = replace_core.resolve_candidate_model(candidate)
                cab_type = model.cabinet_type if model is not None else 'BASE'
                found, _def = standard_defaults(context, target.line or 'COZ', cab_type)
                std_width_mm = round(float(found.width) * 1000.0, 3)
            except Exception:
                std_width_mm = 800.0

        plan = replace_core.plan_replacement(
            target, candidate, active_material=active_mat or None, standard_width_mm=std_width_mm
        )

        if plan.family in ('DOOR', 'WINDOW'):
            if root.get('caffmob_tipo') == 'abertura':
                from ..mobi import cena_v2
                cena_v2.reconstruir_abertura_v2(
                    context, root, modelo=plan.opening_model, material=plan.opening_material
                )
            elif openings_sync.is_opening(root):
                root.btm_opening_real['opening_model'] = plan.opening_model
                if plan.opening_material in ('madeira', 'aluminio', 'blindex'):
                    root.btm_opening_real['opening_material'] = ('madeira', 'aluminio', 'blindex').index(
                        plan.opening_material
                    )
                if plan.family == 'DOOR':
                    is_dbl = door_core.is_double_leaf(plan.opening_model)
                    root.btm_opening_real.kind = 'DOUBLE_DOOR' if is_dbl else 'DOOR'
                    swing_obj = openings_sync._swing(root)[0]
                    if swing_obj is not None:
                        from .. import hb_types
                        try:
                            hb_types.GeoNodeObject(swing_obj).set_input('Is Double', is_dbl)
                        except Exception:
                            pass
                openings_sync.sync(context, root, force=True)
        else:
            saved = _replacement_state(root)
            try:
                _apply_module_replacement(context, root, plan)
            except Exception as exc:
                _restore_replacement(context, root, saved)
                self.report({'WARNING'}, str(exc))
                return {'CANCELLED'}

        for other in list(context.selected_objects):
            other.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        self.report({'INFO'}, tr("Item substituído por {}").format(plan.model_id))
        return {'FINISHED'}


classes = (BTM_OT_LibraryReplaceSelected,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
