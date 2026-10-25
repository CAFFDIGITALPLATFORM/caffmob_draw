"""Propriedades da fita de borda visual (feature 067, T069; data-delta §1).

- `Object.btm_edgeband`, na malha da faixa: uid, dono (uid e ponteiro), as chaves das bordas cobertas (JSON), a
  espessura, a largura aparente, o material ou a cor lisa, e o `params_hash` da última geometria (D-21).
- `Object.btm_cut_exclude`: verdadeiro na fita visual; o plano de corte, a colisão e os alvos de textura pulam o
  objeto (RN-11, D-22).

A cor lisa é uma opção explícita: um material liso próprio da faixa, sem tocar na imagem do material fonte (RF-084).
"""

import bpy  # type: ignore

from ..data.i18n import N_


def _changed(self, context):
    from . import build
    obj = self.id_data
    if isinstance(obj, bpy.types.Object) and self.visual:
        build.apply_material(obj)


def _geometry_changed(self, context):
    from . import sync
    obj = self.id_data
    if isinstance(obj, bpy.types.Object) and self.visual and self.edge_keys:
        self.params_hash = ''
        sync.sync_band(obj, remove=False)       # dentro do próprio update o objeto nunca é apagado


class BTM_PG_EdgeBand(bpy.types.PropertyGroup):
    visual: bpy.props.BoolProperty(name=N_("Fita visual"), default=False, options=set())  # type: ignore
    uid: bpy.props.StringProperty(options=set())  # type: ignore
    owner: bpy.props.PointerProperty(name=N_("Componente"), type=bpy.types.Object, options=set())  # type: ignore
    owner_uid: bpy.props.StringProperty(options=set())  # type: ignore
    part_uids: bpy.props.StringProperty(options=set())  # type: ignore
    edge_keys: bpy.props.StringProperty(options=set())  # type: ignore
    thickness: bpy.props.FloatProperty(name=N_("Espessura"), default=0.001, min=0.0001, max=0.01, unit='LENGTH',
                                       update=_geometry_changed, options=set())  # type: ignore
    coverage_width: bpy.props.FloatProperty(name=N_("Largura aparente"), unit='LENGTH', options=set())  # type: ignore
    length: bpy.props.FloatProperty(name=N_("Comprimento"), unit='LENGTH', options=set())  # type: ignore
    material: bpy.props.PointerProperty(name=N_("Material"), type=bpy.types.Material, update=_changed,
                                        options=set())  # type: ignore
    use_color: bpy.props.BoolProperty(name=N_("Cor lisa"), description=N_("Usa uma cor lisa em vez do material, "
                                      "sem mudar a imagem do material"), default=False, update=_changed,
                                      options=set())  # type: ignore
    color: bpy.props.FloatVectorProperty(name=N_("Cor"), subtype='COLOR', size=4, min=0.0, max=1.0,
                                         default=(0.9, 0.9, 0.9, 1.0), update=_changed, options=set())  # type: ignore
    state: bpy.props.StringProperty(name=N_("Estado"), options=set())  # type: ignore
    params_hash: bpy.props.StringProperty(options=set())  # type: ignore


classes = (BTM_PG_EdgeBand,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_edgeband = bpy.props.PointerProperty(type=BTM_PG_EdgeBand)
    bpy.types.Object.btm_cut_exclude = bpy.props.BoolProperty(
        name=N_("Fora do corte"), description=N_("Malha visual: não entra no plano de corte nem na colisão"),
        default=False, options=set())


def unregister():
    for name in ('btm_cut_exclude', 'btm_edgeband'):
        if hasattr(bpy.types.Object, name):
            delattr(bpy.types.Object, name)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
