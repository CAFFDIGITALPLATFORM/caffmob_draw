"""Conta-gotas: copiar a textura e aplicá-la por parte (feature 018, T016/T017; RF-10, RN-11, D-07, D-08).

`caffmob.texture_pick` é o modo de apontar e capturar: a peça sob o cursor acende com o nome da parte
(`texture_library/pick.py` + `operators/viewport_hud.py`), e o clique guarda a assinatura da textura em
`WindowManager.btm_texture_pick`. Esc e botão direito saem sem capturar, e apontar nunca grava passo de desfazer.

`caffmob.texture_apply_parts` aplica a assinatura guardada nos alvos congelados, só nos domínios marcados
(Porta = `FRONTS`, Exterior = `EXTERNAL`, Interior = `INTERNAL`), revalidando os nomes antes de tocar em qualquer
peça: alvo que sumiu cancela tudo, sem aplicação parcial. A aplicação em si é de `apply.apply_domains` (T023), que
devolve a contagem por domínio. Um passo de Undo.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from ..object_library import retexture
from . import apply, ops_apply, pick, uv_core

SEM_VIEWPORT = N_("Abra o conta-gotas numa vista 3D")
FALTA_ORIGEM = N_("Falta a origem da textura")
CAPTURADO = N_("Textura copiada de {}")
ALVOS_MUDARAM = N_("Os alvos do conta-gotas saíram da cena: escolha de novo")
SEM_PARTE = N_("Marque ao menos uma parte: Porta, Exterior ou Interior")
SEM_ALVO = N_("Nenhum alvo do conta-gotas recebe essa parte")
APLICADO = N_("Textura aplicada em {} peça(s)")


def capturar(context, obj=None):
    """Guarda a assinatura da textura de `obj` (o alvo sob o cursor por padrão); False sem material de imagem."""
    obj = obj or pick.alvo()
    grupo = pick.estado(context)
    material = ops_apply.current_material(obj)
    info = ops_apply.image_info(material)
    if grupo is None or info is None:
        return False
    path, width, height, _rotated, texture_id = info
    grupo.path, grupo.size_mm, grupo.height_mm = path, width, height
    grupo.texture_id = texture_id
    grupo.nome = str(material.get(retexture.NOME_PROP) or material.name)
    grupo.angle = pick.angulo_da_peca(obj)
    grupo.origem = obj.name
    return True


class BTM_OT_TexturePick(bpy.types.Operator):
    """Acende a peça sob o cursor e copia a textura dela no clique (Esc cancela)"""

    bl_idname = 'caffmob.texture_pick'
    bl_label = N_("Conta-gotas: apontar a parte")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        if context.region is None or context.region.type != 'WINDOW':
            self.report({'WARNING'}, tr(SEM_VIEWPORT))
            return {'CANCELLED'}
        if pick.iniciar(context, context.selected_objects) is None:
            return {'CANCELLED'}
        pick.atualizar(context, context.region, event.mouse_region_x, event.mouse_region_y)
        context.area.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        area = context.area
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            pick.encerrar(context)
            if area is not None:
                area.tag_redraw()
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE' and context.region is not None:
            pick.atualizar(context, context.region, event.mouse_region_x, event.mouse_region_y)
            if area is not None:
                area.tag_redraw()
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj = pick.atualizar(context, context.region, event.mouse_region_x, event.mouse_region_y)
            if not capturar(context, obj):
                self.report({'WARNING'}, tr(FALTA_ORIGEM))
                return {'RUNNING_MODAL'}                 # continua apontando: a origem pode ser outra peça
            grupo = pick.estado(context)
            pick.encerrar(context)
            if area is not None:
                area.tag_redraw()
            self.report({'INFO'}, tr(CAPTURADO).format(grupo.nome or grupo.path))
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


class BTM_OT_TextureApplyParts(bpy.types.Operator):
    """Aplica a textura copiada nos alvos do conta-gotas, só nas partes marcadas"""

    bl_idname = 'caffmob.texture_apply_parts'
    bl_label = N_("Aplicar textura copiada")
    bl_options = {'REGISTER', 'UNDO'}

    porta: bpy.props.BoolProperty(name=N_("Na porta"), default=False)  # type: ignore
    exterior: bpy.props.BoolProperty(name=N_("No exterior"), default=False)  # type: ignore
    interior: bpy.props.BoolProperty(name=N_("No interior"), default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return bool(pick.estado(context) is not None and pick.estado(context).path)

    def invoke(self, context, event):
        if not self.poll(context):
            self.report({'WARNING'}, tr(FALTA_ORIGEM))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        grupo = pick.estado(context)
        self.layout.label(text=grupo.nome or grupo.path)
        self.layout.prop(self, "porta")
        self.layout.prop(self, "exterior")
        self.layout.prop(self, "interior")

    def _marcas(self):
        return [parte for parte, marcado in ((uv_core.PORTA, self.porta), (uv_core.EXTERIOR, self.exterior),
                                             (uv_core.INTERIOR, self.interior)) if marcado]

    def execute(self, context):
        grupo = pick.estado(context)
        if grupo is None or not grupo.path:
            self.report({'WARNING'}, tr(FALTA_ORIGEM))
            return {'CANCELLED'}
        marcados = uv_core.partes_para_dominios(self._marcas())
        if not marcados:
            self.report({'WARNING'}, tr(SEM_PARTE))
            return {'CANCELLED'}
        objs = [bpy.data.objects.get(nome) for nome in pick.alvos(context)]
        if not objs or any(obj is None for obj in objs):
            self.report({'WARNING'}, tr(ALVOS_MUDARAM))
            return {'CANCELLED'}
        tamanho = (float(grupo.size_mm), float(grupo.height_mm or grupo.size_mm))
        status, contagem = apply.apply_domains(objs, grupo.texture_id, grupo.path, tamanho, marcados,
                                               angle=grupo.angle)
        mudou = sum(contagem.values()) if status == apply.APPLIED else 0
        if not mudou:
            self.report({'WARNING'}, tr(SEM_ALVO))
            return {'CANCELLED'}
        self.report({'INFO'}, tr(APLICADO).format(mudou))
        return {'FINISHED'}


classes = (BTM_OT_TexturePick, BTM_OT_TextureApplyParts)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
