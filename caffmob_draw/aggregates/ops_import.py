"""Importar modelo 3D externo (feature 003, T047; RF-11, D-16).

Chama o importador do próprio Blender pelo tipo do arquivo (OBJ, FBX, glTF/GLB). Objetos trazidos por outros addons
(por exemplo, um importador de SketchUp) também podem ser convertidos: a conversão aceita qualquer malha da cena.

Feature 007 (T014; RN-01, D-01, D-02): **Unidade** do arquivo (Automática, mm, cm, m, pol) e **Eixo vertical** (Z, Y).
O OBJ e o FBX recebem o eixo no importador; a escala é aplicada depois, sobre as raízes importadas, para a Automática
poder medir o modelo em escala 1 (mais de 50 unidades = mm). O glTF já é métrico e Y-up por especificação.

Feature 009 (T033-T034; RN-13, RN-14, D-16): **SketchUp (.skp)** pelo OpenSKP (`aggregates/skp.py`), em qualquer
plataforma. A montagem (`skp_build`) já entrega metros e Z para cima, com um grupo de peças por instância e os
materiais do SketchUp; a unidade e o eixo acima não se aplicam. Um arquivo que não abre não cria nada e diz o motivo.
"""

import os

import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper  # type: ignore
from mathutils import Matrix  # type: ignore

from ..data.i18n import tr
from . import import_units

UNIT_ITEMS = [('AUTO', "Automática", "Mede o modelo: mais de 50 unidades numa medida = milímetros"),
              ('MM', "Milímetros", ""), ('CM', "Centímetros", ""), ('M', "Metros", ""), ('IN', "Polegadas", "")]
UP_ITEMS = [('Z', "Z", "O arquivo usa Z para cima (SketchUp, Promob, a maioria dos CAD)"),
            ('Y', "Y", "O arquivo usa Y para cima (padrão do OBJ do Blender, glTF)")]

FORMATS = {'.obj': ('wm', 'obj_import'), '.fbx': ('import_scene', 'fbx'), '.glb': ('import_scene', 'gltf'),
           '.gltf': ('import_scene', 'gltf')}


class BTM_OT_ImportModel(bpy.types.Operator, ImportHelper):
    """Importa um modelo 3D (OBJ, FBX, glTF/GLB ou SketchUp) para converter em agregado ou folha de porta"""
    bl_idname = "caffmob.import_model"
    bl_label = "Importar modelo 3D"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.obj;*.fbx;*.glb;*.gltf;*.skp", options={'HIDDEN'})  # type: ignore
    unit: bpy.props.EnumProperty(name="Unidade do arquivo", items=UNIT_ITEMS, default='AUTO')  # type: ignore
    up_axis: bpy.props.EnumProperty(name="Eixo vertical", items=UP_ITEMS, default='Z')  # type: ignore

    def _kwargs(self, ext):
        if ext == '.obj':
            return {'up_axis': self.up_axis, 'forward_axis': 'Y' if self.up_axis == 'Z' else 'NEGATIVE_Z'}
        if ext == '.fbx':
            return {'axis_up': self.up_axis, 'axis_forward': 'Y' if self.up_axis == 'Z' else '-Z'}
        return {}

    def _import_skp(self, context):
        """SketchUp pelo OpenSKP: lê, monta e seleciona; nada fica pela metade se falhar (RF-12)."""
        from . import skp, skp_build, skp_core
        name = os.path.basename(self.filepath)
        wm = context.window_manager
        wm.progress_begin(0, 2)
        before = set(bpy.data.objects)
        try:
            try:
                model, scene = skp.read(self.filepath)
            except ValueError as exc:
                self.report({'ERROR'}, skp_core.failure_message(exc))
                return {'CANCELLED'}
            wm.progress_update(1)
            try:
                groups, skipped = skp_build.build(context, model, scene)
            except Exception as exc:          # falha na montagem: desfaz o que foi criado
                for obj in [o for o in bpy.data.objects if o not in before]:
                    bpy.data.objects.remove(obj, do_unlink=True)
                self.report({'ERROR'}, skp_core.failure_message(exc))
                return {'CANCELLED'}
        finally:
            wm.progress_end()
        for obj in context.selected_objects:
            obj.select_set(False)
        for root in groups:
            root.select_set(True)
        if groups:
            context.view_layer.objects.active = groups[0]
        message = tr("SketchUp importado: {} grupo(s) de peças de {}").format(len(groups), name)
        if skipped:
            message += tr("; {} figura(s) de escala ignorada(s)").format(skipped)
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def execute(self, context):
        ext = os.path.splitext(self.filepath)[1].lower()
        if ext == '.skp':
            return self._import_skp(context)
        target = FORMATS.get(ext)
        if target is None:
            self.report({'ERROR'}, tr("Formato não suportado: {} (use OBJ, FBX, glTF, GLB ou SKP)").format(
                ext or tr("sem extensão")))
            return {'CANCELLED'}
        before = set(bpy.data.objects)
        operator = getattr(getattr(bpy.ops, target[0]), target[1])
        try:
            result = operator(filepath=self.filepath, **self._kwargs(ext))
        except RuntimeError as exc:
            self.report({'ERROR'}, tr("O Blender não conseguiu importar {}: {}").format(os.path.basename(self.filepath), exc))
            return {'CANCELLED'}
        if 'FINISHED' not in result:
            self.report({'ERROR'}, tr("Importação cancelada: {}").format(os.path.basename(self.filepath)))
            return {'CANCELLED'}
        new = [obj for obj in bpy.data.objects if obj not in before]
        meshes = [obj for obj in new if obj.type == 'MESH']
        unit = self._apply_unit(context, new, ext)
        root = _group_import(new, meshes, os.path.splitext(os.path.basename(self.filepath))[0])
        for obj in context.selected_objects:
            obj.select_set(False)
        if root is not None:
            root.select_set(True)
            context.view_layer.objects.active = root
            self.report({'INFO'}, tr("{} malha(s) importada(s) num grupo, unidade: {}. Alt + clique seleciona uma "
                                     "peça; para converter, selecione as peças com Alt + Shift + clique, o pai por "
                                     "último").format(len(meshes), unit))
            return {'FINISHED'}
        for obj in meshes:
            obj.select_set(True)
        if meshes:
            context.view_layer.objects.active = meshes[0]
        self.report({'INFO'}, tr("{} malha(s) importada(s), unidade: {}. Selecione o pai por último e use "
                                 "\"Converter em agregado\" ou \"Montar esquadria\"").format(len(meshes), unit))
        return {'FINISHED'}


    def _apply_unit(self, context, new, ext):
        """Escala as raízes importadas para metros; devolve o nome da unidade usada."""
        if ext in ('.glb', '.gltf') and self.unit == 'AUTO':
            return "m"
        context.view_layer.update()
        from . import group
        box = group.world_box(new)
        largest = max(box[1][i] - box[0][i] for i in range(3)) if box else 0.0
        factor = import_units.scale_for(self.unit, largest)
        if abs(factor - 1.0) > 1e-12:
            pivot = Matrix.Scale(factor, 4)
            for obj in new:
                if obj.parent is None or obj.parent not in new:
                    obj.matrix_world = pivot @ obj.matrix_world
            for obj in new:                    # a escala vai para a malha: peças com escala 1 (D-01)
                if obj.type == 'MESH' and obj.data.users == 1:
                    obj.data.transform(Matrix.Diagonal((*obj.scale, 1.0)))
                    obj.scale = (1.0, 1.0, 1.0)
        unit = 'AUTO' if self.unit == 'AUTO' else self.unit
        return {'MM': "mm", 'CM': "cm", 'M': "m", 'IN': "pol"}[import_units.suggest(largest) if unit == 'AUTO'
                                                                else unit]


classes = (BTM_OT_ImportModel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)


def _group_import(new, meshes, name):
    """Feature 011 (RN-02, D-09): o arquivo importado vira um componente; devolve a raiz, ou None com uma malha só.

    - várias raízes, todas malhas (OBJ): um grupo de peças novo (`group.create_group`);
    - uma raiz que não é malha (Empty do FBX/glTF): ela mesma vira o grupo;
    - várias raízes mistas: as malhas de topo vão para um grupo novo; os Empties ficam como vieram.
    """
    from . import group
    if len(meshes) < 2:
        return None
    roots = [obj for obj in new if obj.parent is None or obj.parent not in new]
    if len(roots) == 1 and roots[0].type != 'MESH':
        data = roots[0].btm_group
        data.is_group, data.kind = True, 'PLAIN'
        return roots[0]
    mesh_roots = [obj for obj in roots if obj.type == 'MESH']
    if len(mesh_roots) < 2:
        return None
    return group.create_group(mesh_roots, 'PLAIN', name or "Grupo")
