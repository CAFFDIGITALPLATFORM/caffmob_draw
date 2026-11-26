"""Posicionamento do armário v2 depois do Aplicar (feature 025).

O armário é montado no construtor; ao aplicar, o usuário escolhe onde ele entra na cena. Este módulo guarda o núcleo
do fluxo, importável sem `bpy` nas funções puras:

- `seta_para_yaw` / `yaw_para_seta`: as quatro setas apontam o armário para as quatro direções cardeais; `R` continua
  girando de 90 em 90 graus.
- `caixa`: medidas do spec em metros, na mesma convenção de `build` — X centrado na largura, Y da frente (−) ao fundo
  (0) e Z do piso à altura.
- `criar_cage`: caixa de arame (8 vértices, 12 arestas, sem faces) que acompanha o mouse.
- `esconder` / `restaurar`: o armário real fica oculto durante a escolha e volta ao estado anterior no fim.
- `chao`: raio do mouse contra o plano do piso (z = 0), para o armário nascer apoiado.
"""

import math

# Direção cardeal que cada seta representa. O eixo Z é o "giro" do armário na planta; 0° é a frente de construção
# do armário (a mesma de `build`), então as quatro setas dão quatro orientações distintas.
ORIENTACOES = {'UP_ARROW': 0.0, 'RIGHT_ARROW': 90.0, 'DOWN_ARROW': 180.0, 'LEFT_ARROW': 270.0}
PASSO = 90.0


def caixa(spec):
    """(largura, profundidade, altura) do spec em metros."""
    return (float(spec.largura) * 0.001, float(spec.profundidade) * 0.001, float(spec.altura) * 0.001)


def seta_para_yaw(seta):
    """Radiano da direção cardeal da seta; seta desconhecida mantém 0°."""
    return math.radians(ORIENTACOES.get(str(seta).upper(), 0.0))


def yaw_para_seta(yaw):
    """Seta cardeal mais próxima do yaw atual (0°, 90°, 180° ou 270°)."""
    graus = math.degrees(float(yaw)) % 360.0
    return min(ORIENTACOES, key=lambda seta: abs(((graus - ORIENTACOES[seta] + 180.0) % 360.0) - 180.0))


def girar(yaw, passo=PASSO):
    """Yaw seguinte no sentido anti-horário, normalizado em [0, 2π)."""
    return math.radians((math.degrees(float(yaw)) + float(passo)) % 360.0)


def posicionar(root, location):
    """Move a raiz para `location`; as peças são filhas e acompanham."""
    from mathutils import Vector  # type: ignore

    root.location = Vector(location)


def orientar(root, yaw):
    """Aplica o giro cardeal na raiz, preservando a inclinação existente."""
    root.rotation_euler.z = float(yaw)


def no_cursor(root, scene):
    """Coloca a raiz na posição do Cursor 3D, preservando a orientação do armário."""
    root.location = scene.cursor.location.copy()


def criar_cage(context, spec, nome="Armário v2 — prévia"):
    """Caixa de arame com as medidas do armário, sem faces, para acompanhar o mouse."""
    import bpy  # type: ignore

    largura, profundidade, altura = caixa(spec)
    meia = largura / 2.0
    verts = [(-meia, -profundidade, 0.0), (meia, -profundidade, 0.0),
             (meia, 0.0, 0.0), (-meia, 0.0, 0.0),
             (-meia, -profundidade, altura), (meia, -profundidade, altura),
             (meia, 0.0, altura), (-meia, 0.0, altura)]
    arestas = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
               (0, 4), (1, 5), (2, 6), (3, 7)]
    malha = bpy.data.meshes.new(nome)
    malha.from_pydata(verts, arestas, [])
    malha.update()
    cage = bpy.data.objects.new(nome, malha)
    context.scene.collection.objects.link(cage)
    cage.display_type = 'WIRE'
    cage.show_in_front = True
    cage.hide_render = True
    cage.hide_select = True
    cage.color = (1.0, 0.55, 0.15, 1.0)
    cage['btm_armario_v2_cage'] = True
    return cage


def remover(cage):
    """Remove a caixa de arame e a malha temporária."""
    import bpy  # type: ignore

    if cage is None:
        return
    malha = cage.data if cage.type == 'MESH' else None
    bpy.data.objects.remove(cage, do_unlink=True)
    if malha is not None and malha.users == 0:
        bpy.data.meshes.remove(malha)


def esconder(root, esconder=True):
    """Oculta (ou mostra) a raiz e as peças; devolve o estado anterior por nome."""
    estados = {}
    for obj in [root] + list(root.children_recursive):
        estados[obj.name] = obj.hide_get()
        obj.hide_set(bool(esconder))
    return estados


def restaurar(estados):
    """Devolve a visibilidade anterior das peças, pelo nome (a cena pode ter mudado)."""
    import bpy  # type: ignore

    for nome, oculto in (estados or {}).items():
        obj = bpy.data.objects.get(nome)
        if obj is not None:
            obj.hide_set(bool(oculto))


def chao(region, rv3d, x, y):
    """Ponto do piso (z = 0) sob o pixel (x, y) da região, ou None quando o raio não o encontra."""
    from mathutils import Vector  # type: ignore
    from mathutils.geometry import intersect_line_plane  # type: ignore
    from bpy_extras import view3d_utils  # type: ignore

    if region is None or rv3d is None:
        return None
    coord = (float(x), float(y))
    origem = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direcao = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    return intersect_line_plane(origem, origem + direcao * 1000.0, Vector((0.0, 0.0, 0.0)),
                                Vector((0.0, 0.0, 1.0)))
