"""Operador não destrutivo Converter em Gaveteiro (feature 021, T027; RF-12, RF-13, RN-11).

Aceita tanto uma malha única (particionada em ilhas conexas) quanto múltiplos objetos separados, classifica as peças
estruturais (2 laterais, contrafrente, traseira, fundo) e de acabamento (frente), registra ferragens essenciais
(corrediças, puxador, fixadores/fita de borda), NUNCA bloqueia quando faltam peças, pergunta ao usuário se deseja
completar automaticamente as peças faltantes, vincula o resultado à camada `Marcenaria` e abre o editor para edição
livre.
"""

import json
import bmesh  # type: ignore
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data import layers
from ..data.i18n import tr
from . import build, drawer_detect_core as ddc


def _extract_part_boxes(selected_objects):
    """Extrai `PartBox` de objetos separados ou de componentes conexos de uma malha única em coordenadas de mundo."""
    meshes = [o for o in selected_objects if o.type == 'MESH' and o.data is not None]
    if not meshes:
        return []

    boxes = []
    if len(meshes) == 1:
        obj = meshes[0]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        visited = set()
        island_idx = 0
        for v in bm.verts:
            if v.index in visited:
                continue
            stack = [v]
            comp = []
            visited.add(v.index)
            while stack:
                cur = stack.pop()
                comp.append(obj.matrix_world @ cur.co)
                for e in cur.link_edges:
                    other = e.other_vert(cur)
                    if other.index not in visited:
                        visited.add(other.index)
                        stack.append(other)
            if comp:
                mn = (min(p.x for p in comp), min(p.y for p in comp), min(p.z for p in comp))
                mx = (max(p.x for p in comp), max(p.y for p in comp), max(p.z for p in comp))
                boxes.append(ddc.PartBox(f"{obj.name}__ilha_{island_idx}", mn, mx))
                island_idx += 1
        bm.free()
        return boxes

    for obj in meshes:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        mn = (min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners))
        mx = (max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners))
        boxes.append(ddc.PartBox(obj.name, mn, mx))
    return boxes


def _create_box_mesh(name, min_pt, max_pt, parent, collection):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    sx = max(max_pt[0] - min_pt[0], 1e-4)
    sy = max(max_pt[1] - min_pt[1], 1e-4)
    sz = max(max_pt[2] - min_pt[2], 1e-4)
    cx = 0.5 * (min_pt[0] + max_pt[0])
    cy = 0.5 * (min_pt[1] + max_pt[1])
    cz = 0.5 * (min_pt[2] + max_pt[2])
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x * sx + cx
        v.co.y = v.co.y * sy + cy
        v.co.z = v.co.z * sz + cz
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = parent
    return obj


class BTM_OT_ConvertToDrawer(bpy.types.Operator):
    """Converte a seleção (malha única ou peças separadas) em Gaveteiro na camada Marcenaria"""
    bl_idname = "caffmob.convert_to_drawer"
    bl_label = "Gaveteiro"
    bl_options = {'REGISTER', 'UNDO'}

    completar_faltantes: bpy.props.BoolProperty(
        name="Completar peças faltantes automaticamente",
        description="Quando faltarem peças da gaveta, gera automaticamente as peças ausentes (opcional)",
        default=False,
    )  # type: ignore
    corredica_tipo: bpy.props.EnumProperty(
        name="Corrediça",
        items=[
            ('TELESCOPICA', "Telescópica (lateral)", "Par de corrediças telescópicas fixadas nas laterais"),
            ('OCULTA', "Oculta / Invisível (base)", "Par de corrediças ocultas fixadas por baixo"),
        ],
        default='TELESCOPICA',
    )  # type: ignore
    puxador_tipo: bpy.props.EnumProperty(
        name="Puxador",
        items=[
            ('EXTERNO', "Externo", "Puxador externo parafusado na frente"),
            ('EMBUTIDO', "Embutido", "Puxador embutido"),
            ('CAVA', "Cava (usinado)", "Puxador usinado na própria frente"),
        ],
        default='EXTERNO',
    )  # type: ignore
    fundo_fixacao: bpy.props.EnumProperty(
        name="Fixação do Fundo",
        items=[
            ('RASGO', "Em rasgo (canal)", "Fundo 6 mm encaixado em canais nas laterais"),
            ('PARAFUSADO', "Fixado por baixo", "Fundo 6 mm aparafusado ou pregado por baixo"),
        ],
        default='RASGO',
    )  # type: ignore
    abrir_editor: bpy.props.BoolProperty(
        name="Abrir editor após converter",
        description="Abre o editor de armário/gaveteiro ao concluir para edição livre",
        default=True,
    )  # type: ignore

    _cached_missing = []
    _cached_found = []

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        boxes = _extract_part_boxes(context.selected_objects)
        analysis = ddc.analyze_drawer_parts(boxes)
        BTM_OT_ConvertToDrawer._cached_found = [ddc.ROLE_LABELS[r] for r in analysis.role_map]
        BTM_OT_ConvertToDrawer._cached_missing = [ddc.ROLE_LABELS[r] for r in analysis.missing_roles]
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        found = BTM_OT_ConvertToDrawer._cached_found
        missing = BTM_OT_ConvertToDrawer._cached_missing

        box = layout.box()
        box.label(text=tr("Peças reconhecidas ({}):").format(len(found)), icon='CHECKMARK')
        if found:
            box.label(text=", ".join(found))
        else:
            box.label(text=tr("Nenhuma peça padrão reconhecida automaticamente (conversão liberada)."))

        if missing:
            warn = layout.box()
            warn.label(text=tr("Peças faltantes ({}):").format(len(missing)), icon='ERROR')
            warn.label(text=", ".join(missing))
            warn.prop(self, "completar_faltantes")

        hw = layout.box()
        hw.label(text=tr("Ferragens e Acabamentos"), icon='PREFERENCES')
        hw.prop(self, "corredica_tipo")
        hw.prop(self, "puxador_tipo")
        hw.prop(self, "fundo_fixacao")
        layout.prop(self, "abrir_editor")

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']
        if not selected:
            self.report({'WARNING'}, tr("Selecione ao menos uma malha para converter em Gaveteiro."))
            return {'CANCELLED'}

        boxes = _extract_part_boxes(selected)
        analysis = ddc.analyze_drawer_parts(boxes)
        marcenaria = layers.ensure_marcenaria(context.scene)

        root = build.criar_raiz(context.scene, nome="Gaveteiro")
        root['btm_drawer_unit'] = True
        layers.place(root, marcenaria, context.scene)

        # Clona peças selecionadas para dentro do gaveteiro e preserva origens ocultas fora do corte (não destrutivo)
        for src in selected:
            dup = src.copy()
            dup.data = src.data.copy()
            marcenaria.objects.link(dup)
            dup.parent = root
            dup.matrix_world = src.matrix_world.copy()
            src['btm_cut_exclude'] = True
            src.hide_viewport = True

        created_missing = []
        if self.completar_faltantes and analysis.missing_roles:
            for sp in ddc.synthesize_missing_parts(analysis):
                part_obj = _create_box_mesh(f"Gaveta_{sp.label}", sp.min_pt, sp.max_pt, root, marcenaria)
                if getattr(part_obj, 'btm_armario_parte', None) is not None:
                    part_obj.btm_armario_parte.papel = sp.role
                created_missing.append(sp.role)

        meta = {
            'reconhecidas': {role: pb.part_id for role, pb in analysis.role_map.items()},
            'faltantes': list(analysis.missing_roles),
            'completadas_auto': created_missing,
            'ferragens': ddc.default_hardware(
                slide_type=self.corredica_tipo,
                handle_type=self.puxador_tipo,
                bottom_mount=self.fundo_fixacao,
            ),
        }
        root['btm_gaveteiro_meta'] = json.dumps(meta, ensure_ascii=False)

        for o in context.selected_objects:
            o.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root

        if analysis.missing_roles and not self.completar_faltantes:
            missing_names = ", ".join(ddc.ROLE_LABELS[r] for r in analysis.missing_roles)
            self.report({'WARNING'}, tr("Gaveteiro criado com peças faltantes: {}").format(missing_names))
        else:
            self.report({'INFO'}, tr("Gaveteiro criado na camada Marcenaria."))

        if self.abrir_editor and hasattr(bpy.ops.caffmob, 'cabinet_editor') and bpy.ops.caffmob.cabinet_editor.poll():
            try:
                bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')
            except Exception:
                pass
        return {'FINISHED'}


classes = (BTM_OT_ConvertToDrawer,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
