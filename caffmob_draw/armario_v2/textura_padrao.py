"""Textura padrão MDF claro na cena: imagem empacotada e nó no material da chapa (024, T005; RN-01, D-01).

A imagem nasce dos bytes de `mdf_core.gerar` e é **empacotada** (`pack()`), então sobrevive ao salvar e reabrir sem
arquivo externo nem download — a feature continua offline. O `Mapping` usa `1 / TAMANHO_M` porque o UV da chapa já
está em metros (1 unidade de UV = 1 m): a textura cobre 0,6 m × 0,6 m e repete a partir daí.

Só o material da chapa recebe a imagem; vidro e alumínio continuam como estavam (`build.materiais`).
"""

from ..texture_library.uv_core import LAYER_UV
from . import mdf_core

NOME_IMAGEM = "CAFFMob MDF claro"
NOME_NO = "MDF claro"
NOME_MAPEAMENTO = "MDF claro (metros)"
NOME_UV = "MDF claro (UV)"
TAMANHO_M = 0.6                 # lado real que a textura cobre na peça


def imagem():
    """`bpy.data.images` empacotada da textura padrão, criada uma vez por arquivo."""
    import bpy  # type: ignore

    existente = bpy.data.images.get(NOME_IMAGEM)
    if existente is not None:
        if existente.packed_file is None:
            existente.pack()
        return existente
    dados = mdf_core.gerar()
    nova = bpy.data.images.new(NOME_IMAGEM, width=mdf_core.TAMANHO, height=mdf_core.TAMANHO, alpha=True)
    nova.pixels.foreach_set([valor / 255.0 for valor in dados])
    nova.pack()
    return nova


def aplicar(material):
    """Liga a textura ao Base Color do material da chapa, com o mapa em metros; devolve o material."""
    if material is None or not material.use_nodes or material.node_tree is None:
        return material
    arvore = material.node_tree
    bsdf = next((no for no in arvore.nodes if no.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        return material
    textura = arvore.nodes.get(NOME_NO)
    if textura is None:
        textura = arvore.nodes.new('ShaderNodeTexImage')
        textura.name = NOME_NO
        textura.label = NOME_IMAGEM
    textura.image = imagem()
    textura.location = (-460.0, 240.0)
    mapeamento = arvore.nodes.get(NOME_MAPEAMENTO)
    if mapeamento is None:
        mapeamento = arvore.nodes.new('ShaderNodeMapping')
        mapeamento.name = NOME_MAPEAMENTO
    mapeamento.inputs['Scale'].default_value = (1.0 / TAMANHO_M, 1.0 / TAMANHO_M, 1.0)
    mapeamento.location = (-650.0, 200.0)
    coordenada = arvore.nodes.get(NOME_UV)
    if coordenada is None:
        coordenada = arvore.nodes.new('ShaderNodeUVMap')
        coordenada.name = NOME_UV
        coordenada.uv_map = LAYER_UV
    coordenada.location = (-840.0, 200.0)
    arvore.links.new(coordenada.outputs['UV'], mapeamento.inputs['Vector'])
    arvore.links.new(mapeamento.outputs['Vector'], textura.inputs['Vector'])
    arvore.links.new(textura.outputs['Color'], bsdf.inputs['Base Color'])
    return material
