"""065 T117: aparência do Studio; fila/cache da 062, sem rede durante a montagem."""
import json
import math
import bpy  # type: ignore
from ..geometry.obra_v2 import escala_da_textura
from ..texture_library import catalog, downloads

COR_RESERVA = '#c6b6a4'


def _cor(hexadecimal):
    def linear(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(linear(int(hexadecimal[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1,)


def criar_material(dado=None, veio='HORIZONTAL', emissivo=False):
    dado = dado or dict(nome='Neutro', tipo='cor', cor=COR_RESERVA, classe_visual='mdf')
    m = bpy.data.materials.new('MOBI v2 ' + dado['nome'])
    m.use_nodes = True
    m['caffmob_material'] = json.dumps(dado, ensure_ascii=False)
    m['caffmob_veio'] = veio
    if dado.get('id'):
        m['caffmob_id'] = dado['id']
    m.diffuse_color = _cor(dado.get('cor', COR_RESERVA))
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = m.diffuse_color
    bsdf.inputs['Roughness'].default_value = 0.75
    classe = dado.get('classe_visual', 'mdf')
    m['caffmob_classe_visual'] = classe
    if classe == 'metal':
        bsdf.inputs['Metallic'].default_value = 1
        bsdf.inputs['Roughness'].default_value = 0.25
    elif classe == 'vidro':
        bsdf.inputs['Transmission Weight'].default_value = 1
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['IOR'].default_value = 1.45
    elif classe in ('pvc', 'porcelanato'):
        bsdf.inputs['Roughness'].default_value = 0.25
    if emissivo:
        bsdf.inputs['Emission Color'].default_value = (1, 0.72, 0.35, 1)
        bsdf.inputs['Emission Strength'].default_value = 3
        m['caffmob_led'] = True
    if dado['tipo'] == 'textura':
        m['caffmob_textura_pendente'] = dado['textura_id']
    return m


def _aplicar_imagem(m, dado, path):
    tree = m.node_tree
    bsdf = tree.nodes.get('Principled BSDF')
    # Os UVs estão em mm. Esta ordem reproduz a matriz de Three.Texture, inclusive
    # escala anisotrópica, centro 0,5 e giro do veio vertical somado à rotação.
    image = bpy.data.images.load(path, check_existing=True)
    escala = escala_da_textura(dado.get('escala_mm'), dict(largura=image.size[0], altura=image.size[1]))
    for node in list(tree.nodes):
        if node not in (bsdf, tree.nodes.get('Material Output')):
            tree.nodes.remove(node)
    uv = tree.nodes.new('ShaderNodeTexCoord')
    sub = tree.nodes.new('ShaderNodeVectorMath')
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = (0.5, 0.5, 0)
    giro = tree.nodes.new('ShaderNodeVectorRotate')
    giro.rotation_type = 'AXIS_ANGLE'
    giro.inputs['Axis'].default_value = (0, 0, 1)
    giro.inputs['Angle'].default_value = -math.radians(dado.get('rotacao', 0) + (90 if m['caffmob_veio'] == 'VERTICAL' else 0))
    repeat = tree.nodes.new('ShaderNodeVectorMath')
    repeat.operation = 'MULTIPLY'
    repeat.inputs[1].default_value = (1 / escala['largura'], 1 / escala['altura'], 1)
    center = tree.nodes.new('ShaderNodeVectorMath')
    center.operation = 'ADD'
    center.inputs[1].default_value = (0.5, 0.5, 0)
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image, tex.extension = image, 'REPEAT'
    for a, output, b, input_ in ((uv, 'UV', sub, 0), (sub, 'Vector', giro, 'Vector'),
                                  (giro, 'Vector', repeat, 0), (repeat, 'Vector', center, 0),
                                  (center, 'Vector', tex, 'Vector'), (tex, 'Color', bsdf, 'Base Color')):
        tree.links.new(a.outputs[output], b.inputs[input_])
    m['caffmob_escala_mm'] = [escala['largura'], escala['altura']]
    m['caffmob_textura_pendente'] = ''


def baixar_pendentes(colecao):
    """Retoma sob demanda, também após voltar à rede. Nunca espera HTTP no Blender.

    Offline mantém o UUID e a cor. T118 pode chamar novamente após reconexão.
    Callbacks só tocam o material preparado, nunca materiais de uma cena anterior.
    """
    materiais = {m for obj in colecao.all_objects if obj.type == 'MESH' for m in obj.data.materials if m}
    for m in materiais:
        tid = m.get('caffmob_textura_pendente')
        if not tid or m.get('caffmob_baixando'):
            continue
        dado = json.loads(m['caffmob_material'])
        entry = catalog.item(tid)
        path = downloads.cached(tid, entry=entry) if entry else ''
        if path:
            try:
                _aplicar_imagem(m, dado, path)
            except (OSError, RuntimeError, ValueError):
                pass
            continue
        if not bpy.app.online_access:
            continue
        m['caffmob_baixando'] = True
        def pronto(path, error, m=m, dado=dado):
            try:
                m['caffmob_baixando'] = False
                if path and not error:
                    _aplicar_imagem(m, dado, path)
            except (ReferenceError, OSError, RuntimeError):
                # A cena pode ter sido substituída durante o download. A pendência
                # conserva o fallback quando a imagem não pode ser aberta.
                pass
        if entry:
            downloads.fetch(tid, pronto, entry=entry)
        else:
            def metadata(status, body, tid=tid, pronto=pronto):
                if status != 200:
                    pronto(None, True)
                    return
                try:
                    entry = catalog.remember(body)
                    downloads.fetch(tid, pronto, entry=entry)
                except (KeyError, TypeError, ValueError):
                    pronto(None, True)
            downloads.request('GET', '/api/draw/v1/texturas/' + tid, callback=metadata)
