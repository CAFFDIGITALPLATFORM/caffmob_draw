"""Troca de corrediça da gaveta (072 D-09, RN-07): um botão, um passo de desfazer, a frente não muda."""
import json

import bpy

from ..data.i18n import tr
from . import build, catalogo, core
from .scene import drawer_of, is_drawer

MM = 0.001


def _raiz_e_caminho(front):
    from ..geometry import subspace_fronts
    from ..selection import classify
    raiz, _library = classify.module_root(front)
    return raiz, front.get(subspace_fronts.PATH_PROP, '')


def _indice(front, raiz, caminho):
    from ..geometry import subspace_fronts
    if front.get('btm_drawer_index') is not None:
        return int(front['btm_drawer_index'])
    frentes = sorted((o for o in subspace_fronts.fronts_of(raiz, caminho) if o.get('hb_part_role') == 'DRAWER_FRONT'),
                     key=lambda o: o.matrix_world.translation.z)
    return frentes.index(front) if front in frentes else 0


def _gravar_no_pedido(raiz, caminho, indice, gaveta):
    from ..geometry import subspace_fronts
    data = subspace_fronts.specs(raiz)
    item = data.get(caminho)
    if not item:
        return
    n = int(item.get('count', 1))
    lista = list(item.get('gavetas') or [item.get('gaveta')] * n)
    lista += [item.get('gaveta')] * (n - len(lista))
    lista[indice] = gaveta.para_dict()
    item['gavetas'] = lista
    subspace_fronts._save(raiz, data)


def _converter_antiga(front, raiz, caminho, corredica):
    """Gaveta de antes da 072: a caixa simples sai e a gaveta passa ao construtor com a corrediça escolhida."""
    from ..geometry import subspace_fronts
    item = subspace_fronts.specs(raiz).get(caminho) or {}
    lo, hi = item.get('box') or ((0, 0, 0), (0, 0, 0))
    espaco = core.Espaco((hi[0] - lo[0]) * 1000, front.dimensions.z * 1000, (hi[1] - lo[1]) * 1000)
    espessura = raiz.btm_cabinet.thickness * 1000
    gaveta = core.Gaveta(corredica=corredica.id, frente_espessura=espessura)
    core.caixa(espaco, gaveta, corredica, espaco.altura)          # ValueError antes de mexer na cena
    for filho in list(front.children):
        if filho.get('hb_part_role') == 'CLOSET_DRAWER_BOX':
            bpy.data.objects.remove(filho, do_unlink=True)
    return espaco, gaveta, espaco.altura, subspace_fronts.MARGIN * 1000, espessura


def trocar(front, corredica_id):
    """Troca a corrediça; devolve a caixa nova. ValueError com o motivo se não cabe (nada muda)."""
    from ..aggregates import apply
    from ..geometry import subspace_fronts
    nova = catalogo.por_id(corredica_id, build.pasta_do_usuario())
    if nova is None:
        raise ValueError(tr("Corrediça desconhecida."))
    raiz, caminho = _raiz_e_caminho(front)
    if is_drawer(front):
        d = json.loads(front['btm_drawer'])
        from .scene import altura, espaco, spec
        e, h = espaco(front), altura(front)
        gaveta = core.trocar_corredica(e, spec(front), nova, h)
        folga_x, espessura = d.get('folga_x', subspace_fronts.MARGIN * 1000), d.get('espessura_da_frente', 18.0)
    else:
        e, gaveta, h, folga_x, espessura = _converter_antiga(front, raiz, caminho, nova)
    caixa = build.aplicar(front, e, gaveta, h, folga_x, espessura)
    for filho in front.children:
        filho[subspace_fronts.PATH_PROP] = caminho
    if getattr(front, 'btm_aggregate', None) is not None and front.btm_aggregate.is_aggregate:
        apply._write(front, 'travel', caixa.comprimento * MM)
    if raiz is not None:
        _gravar_no_pedido(raiz, caminho, _indice(front, raiz, caminho), gaveta)
    return caixa


def frente_selecionada(context):
    obj = context.active_object
    if obj is None:
        return None
    gaveta = drawer_of(obj)
    if gaveta is not None:
        return gaveta
    return obj if obj.get('hb_part_role') == 'DRAWER_FRONT' else None


class CAFFMOB_OT_gaveta_corredica(bpy.types.Operator):
    """Troca a corrediça da gaveta: a caixa é recalculada e a frente fica onde está"""
    bl_idname = 'caffmob.gaveta_corredica'
    bl_label = "Trocar corrediça"
    bl_options = {'REGISTER', 'UNDO'}

    gaveta: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    corredica: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        front = bpy.data.objects.get(self.gaveta) if self.gaveta else frente_selecionada(context)
        if front is None:
            self.report({'ERROR'}, tr("Selecione a frente de uma gaveta."))
            return {'CANCELLED'}
        try:
            caixa = trocar(front, self.corredica)
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        nome = catalogo.por_id(self.corredica, build.pasta_do_usuario()).nome
        self.report({'INFO'}, tr("{} de {} mm").format(nome, int(caixa.comprimento)))
        return {'FINISHED'}


classes = (CAFFMOB_OT_gaveta_corredica,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
