"""Coleção das câmeras: nome único, cor aleatória, reorganização e a nova câmera dentro dela.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_cameras_colecao.py

O que exige janela (clicar na lista, ver a cor na outliner) não é afirmado aqui: `color_tag` é o dado que a
outliner pinta.
"""

import sys
import traceback
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402  (registra o add-on)

from caffmob_draw.promob import cameras  # noqa: E402

PASS, FAIL = [], []


def check(nome, ok, detalhe=""):
    (PASS if ok else FAIL).append(nome if ok else f"{nome} :: {detalhe}")
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)


def limpar():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def colecoes_com(nome):
    return [c for c in bpy.data.collections if c.name == nome]


nome_de = lambda c: c.name  # noqa: E731


def nova_camera_na_mao(nome):
    """Uma câmera que já existia na cena, solta na coleção mestre."""
    dados = bpy.data.cameras.new(nome)
    obj = bpy.data.objects.new(nome, dados)
    bpy.context.scene.collection.objects.link(obj)
    return obj


try:
    # -- 1. câmera que já estava na cena, antes de qualquer câmera do add-on ---------------------------------------
    limpar()
    antiga_na_cena = nova_camera_na_mao("CAM antiga")

    check("op nova câmera executa", bpy.ops.caffmob.camera_nova() == {'FINISHED'})

    camerias = colecoes_com(cameras.COLECAO)
    check("existe uma coleção chamada CAMERAS", len(camerias) == 1, [c.name for c in bpy.data.collections])
    check("nenhuma coleção chamada Câmeras do Promob", not colecoes_com(cameras.COLECAO_ANTIGA),
          [c.name for c in bpy.data.collections])
    colecao = camerias[0] if camerias else None
    check("a coleção está ligada à cena", colecao is not None and colecao.name in bpy.context.scene.collection.children)

    lista = cameras.todas(bpy.context.scene)
    check("a câmera antiga e a nova estão na cena", len(lista) == 2, [c.name for c in lista])
    check("a câmera nova nasceu dentro da coleção",
          all(c.name in (colecao.objects if colecao else []) for c in lista),
          [c.name for c in lista])
    check("a câmera que já existia foi reorganizada",
          antiga_na_cena.name in (colecao.objects if colecao else []))
    nova = [c for c in lista if c != antiga_na_cena][0]
    check("a câmera nova nasce apontada para um alvo próprio",
          cameras.alvo_de(nova) is not None, list(nova.get(cameras.ALVO_PROP) or []))
    check("nenhum Empty é criado na cena",
          not [o for o in bpy.data.objects if o.type == 'EMPTY'], [o.name for o in bpy.data.objects])
    check("a coleção ganhou uma cor de etiqueta", colecao is not None and colecao.color_tag in cameras.CORES_DA_COLECAO,
          colecao.color_tag if colecao else None)

    # -- 2. a cor não é trocada a cada câmera nova ----------------------------------------------------------------
    cor = colecao.color_tag
    bpy.ops.caffmob.camera_nova()
    check("a cor da coleção se mantém entre criações", colecao.color_tag == cor, (cor, colecao.color_tag))

    # -- 3. quem organizou a câmera à mão fica onde está ----------------------------------------------------------
    minha = bpy.data.collections.new("Minha organização")
    bpy.context.scene.collection.children.link(minha)
    dados = bpy.data.cameras.new("CAM pessoal")
    pessoal = bpy.data.objects.new("CAM pessoal", dados)
    minha.objects.link(pessoal)
    bpy.ops.caffmob.camera_nova()
    check("câmera já organizada pela pessoa não é movida", [c.name for c in pessoal.users_collection] == [minha.name],
          [c.name for c in pessoal.users_collection])

    # -- 4. coleção antiga é reaproveitada, não duplicada ----------------------------------------------------------
    limpar()
    legado = bpy.data.collections.new(cameras.COLECAO_ANTIGA)
    bpy.context.scene.collection.children.link(legado)
    dados = bpy.data.cameras.new("CAM do legado")
    do_legado = bpy.data.objects.new("CAM do legado", dados)
    legado.objects.link(do_legado)
    bpy.ops.caffmob.camera_nova()
    check("a coleção antiga virou CAMERAS", len(colecoes_com(cameras.COLECAO)) == 1,
          [c.name for c in bpy.data.collections])
    check("a coleção antiga não sobrou", not colecoes_com(cameras.COLECAO_ANTIGA),
          [c.name for c in bpy.data.collections])
    colecao = colecoes_com(cameras.COLECAO)[0]
    check("a câmera do legado continua na coleção", do_legado.name in colecao.objects)
    check("o legado ganhou cor ao ser reaproveitado", colecao.color_tag in cameras.CORES_DA_COLECAO,
          colecao.color_tag)

    # -- 5. a câmera aponta para o alvo sem Empty e sem Track To ---------------------------------------------------
    cam = cameras.todas(bpy.context.scene)[0]
    check("nenhuma restrição Track To", not list(cam.constraints), [k.type for k in cam.constraints])
    check("a câmera não tem alvo-objeto",
          not [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith(cam.name)])
    cam.location = (0.0, -5.0, 1.6)
    cam[cameras.ALVO_PROP] = [0.0, 0.0, 1.6]
    cameras._apontar(cam, cameras.alvo_de(cam))
    bpy.context.view_layer.update()     # sem isto o matrix_world é o de antes do giro
    frente = cam.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    check("a câmera olha para o alvo pelo -Z", frente.y > 0.99, tuple(round(v, 3) for v in frente))

    # -- 6. cena antiga com Empty alvo: o Empty vira ponto e some -------------------------------------------------
    limpar()
    dados = bpy.data.cameras.new("CAM velha")
    velha = bpy.data.objects.new("CAM velha", dados)
    bpy.context.scene.collection.objects.link(velha)
    velha.location = (0.0, -3.0, 1.5)
    mira = bpy.data.objects.new("CAM velha · alvo", None)
    bpy.context.scene.collection.objects.link(mira)
    mira.location = (0.0, 0.0, 1.2)
    nome_da_mira = mira.name
    velha[cameras.ALVO_PROP] = nome_da_mira
    alvo_migrado = cameras.alvo_de(velha)
    check("o Empty alvo da cena antiga é removido", bpy.data.objects.get(nome_da_mira) is None,
          [o.name for o in bpy.data.objects])
    check("o alvo migrado guarda a posição do Empty", tuple(round(v, 3) for v in alvo_migrado) == (0.0, 0.0, 1.2),
          tuple(alvo_migrado))
    guardado = velha.get(cameras.ALVO_PROP)
    check("a câmera migrada guarda o alvo como ponto (x, y, z)",
          not isinstance(guardado, str) and len(guardado) == 3, guardado)

    # -- 7. importação de vistas do .promob (o outro caminho que cria câmera) ---------------------------------------
    limpar()
    vistas = [
        {'nome': 'CAM 0001', 'observador': (0, -3000, 1500), 'alvo': (0, 0, 1200), 'fov': 50,
         'corte_anterior': 10, 'corte_posterior': 50000, 'perspectiva': True},
        {'nome': 'Vista dinâmica', 'atual': True, 'observador': (1000, -3000, 1600), 'alvo': (0, 0, 1200), 'fov': 60,
         'corte_anterior': 10, 'corte_posterior': 50000, 'perspectiva': False, 'largura_ortogonal': 3000},
    ]
    check("importar duas vistas cria duas câmeras", cameras.criar(bpy.context, vistas) == 2)
    importadas = cameras.todas(bpy.context.scene)
    check("a importação não cria Empty", not [o for o in bpy.data.objects if o.type == 'EMPTY'],
          [o.name for o in bpy.data.objects])
    check("a vista ortográfica vira câmera ORTHO",
          [c.data.type for c in importadas if c.name == 'Vista dinâmica'] == ['ORTHO'],
          [(c.name, c.data.type) for c in importadas])
    check("a vista dinâmica é a câmera ativa", bpy.context.scene.camera is not None
          and bpy.context.scene.camera.name == 'Vista dinâmica')
    check("as câmeras importadas foram para a coleção",
          all(c.name in colecoes_com(cameras.COLECAO)[0].objects for c in importadas))
except Exception:  # noqa: BLE001
    traceback.print_exc()
    FAIL.append("exceção")

print(f"\n{len(PASS)} OK, {len(FAIL)} FALHA", flush=True)
for nome in FAIL:
    print("  FALHA:", nome, flush=True)
print("blender_cameras_colecao: " + ("OK" if not FAIL else "FALHOU"), flush=True)
if FAIL:
    raise SystemExit(1)
