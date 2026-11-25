"""Teste de fumaça da rodada 026: dobradiça, lista de materiais, `.skp` no File > Import e conversão peça por peça.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_026_dobradica_lista_conversao_smoke.py

Tudo passa pelos `bl_idname` de verdade (`tests/_blender_env.py` registra o add-on inteiro):

1. Gerar um armário com duas folhas de porta cria as dobradiças do `assets/hinges/dobradica.obj` na aresta de cada
   folha, com `papel` vazio e `ferragem = 'DOBRADICA'`; a malha é a do OBJ (não a caixa de reserva), elas ficam fora do
   plano de corte e entram em `hardware[]` como "Dobradiça";
2. abrir a porta leva as dobradiças no pivô da folha e fechar devolve cada uma ao lugar;
3. `caffmob.lista_materiais` percorre toda malha da cena aberta, agrupa linhas iguais e grava o texto do arquivo;
4. `caffmob.import_skp` está no menu File > Import (a função do menu pede o operador) e importa o `.skp` de teste;
5. `caffmob.armario_v2_converter_pecas` cria o armário com as peças apontadas **sem gerar nem mover nada**, e o Gerar
   depois cai exatamente onde as originais estavam; `caffmob.armario_v2_separar_pecas` separa a malha em peças soltas.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from caffmob_draw.aggregates import ops_import  # noqa: E402
from caffmob_draw.armario_v2 import anim, build, ops, ponte  # noqa: E402
from caffmob_draw.cutting import hardware, part_extractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "porta_teste.skp"
BLOCO_LISTA = "Lista de Materiais"
FAILURES = []


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FAILURES.append(nome)


def selecionar(obj):
    for outro in [item for item in bpy.context.view_layer.objects if item is not None]:
        outro.select_set(False)
    if obj is None:
        bpy.context.view_layer.objects.active = None
        return
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def pecas(root):
    return [filho for filho in root.children if getattr(filho, 'btm_armario_parte', None) is not None]


def por_papel(root, nome):
    return [item for item in pecas(root) if item.btm_armario_parte.papel == nome]


def de_ferragem(root, nome):
    return [item for item in pecas(root) if getattr(item.btm_armario_parte, 'ferragem', 'NENHUMA') == nome]


def caixa(item):
    """Caixa de mundo da peça em milímetros."""
    pontos = [item.matrix_world @ Vector(canto) for canto in item.bound_box]
    return (tuple(min(ponto[i] for ponto in pontos) * 1000.0 for i in range(3)),
            tuple(max(ponto[i] for ponto in pontos) * 1000.0 for i in range(3)))


def centro(item, eixo):
    """Centro de mundo da peça no eixo pedido, em milímetros."""
    pontos = [item.matrix_world @ vertice.co for vertice in item.data.vertices]
    return sum(getattr(ponto, eixo) for ponto in pontos) / len(pontos) * 1000.0


def posicao_xy(item):
    return centro(item, 'x'), centro(item, 'y')


def distancia_xy(antes, depois):
    """Quanto a peça andou no plano horizontal, em milímetros."""
    return ((depois[0] - antes[0]) ** 2 + (depois[1] - antes[1]) ** 2) ** 0.5


def passo_frames(alvo):
    """Roda os quadros do timer à mão: em `--background` não há laço de eventos que o acorde."""
    funcao = anim._handles.get(alvo.name)
    for _ in range(anim.QUADROS + 2):
        if funcao is None:
            break
        funcao()
        funcao = anim._handles.get(alvo.name)


def armario_com_porta():
    env.clean_scene()
    root = build.criar_raiz(bpy.context.scene, nome="Armário dobradiça")
    armario = root.btm_armario
    armario.largura, armario.altura, armario.profundidade = 1000.0, 2400.0, 510.0
    armario.lateral_esq_ativa = armario.lateral_dir_ativa = True
    armario.base_inf_ativa = armario.base_sup_ativa = True
    armario.porta_ativa, armario.porta_folhas, armario.porta_dobradica = True, 2, 'ESQUERDA'
    ops.semear_contrato(bpy.context.scene)
    selecionar(root)
    return root


# 1 e 2 — dobradiça ------------------------------------------------------------------------------------------------
def run_dobradica(ctx):
    root = armario_com_porta()
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    dobradicas = de_ferragem(root, 'DOBRADICA')
    check("Gerar cria as dobradiças das duas folhas",
          resultado == {'FINISHED'} and len(dobradicas) == 10, f"{len(dobradicas)} dobradiça(s)")
    check("dobradiça tem papel vazio (fora do plano de chapa)",
          bool(dobradicas) and all(item.btm_armario_parte.papel == '' for item in dobradicas))
    check("dobradiça usa o modelo do OBJ, não a caixa de reserva",
          bool(dobradicas) and max(len(item.data.vertices) for item in dobradicas) > 100,
          f"{max((len(item.data.vertices) for item in dobradicas), default=0)} vértices")
    porta = por_papel(root, 'PORTA')[0]
    (px0, py0, pz0), (px1, _py1, pz1) = caixa(porta)
    primeira = [item for item in dobradicas if item.name.endswith(' da porta 1')][0]
    (dx0, dy0, dz0), (dx1, _dy1, dz1) = caixa(primeira)
    check("dobradiça na aresta esquerda da porta, do lado de dentro",
          abs(dx0 - px0) < 1.0 and abs(dy0 - py0) < 1.0, f"x {dx0:.1f} de {px0:.1f}; y {dy0:.1f} de {py0:.1f}")
    check("dobradiça dentro da altura da porta e com a medida do modelo",
          dz0 >= pz0 - 0.1 and dz1 <= pz1 + 0.1 and abs((dz1 - dz0) - 52.2) < 1.0,
          f"z {dz0:.1f}–{dz1:.1f} de {pz0:.1f}–{pz1:.1f}")

    itens = part_extractor.extract_production_parts(ctx)[0]
    nomes = [item.name.upper() for item in itens if item.source == 'ARMARIO_V2']
    check("plano de corte não lista a dobradiça",
          not [nome for nome in nomes if 'DOBRAD' in nome], str([n for n in nomes if 'DOBRAD' in n][:3]))
    linhas = hardware.collect(ctx.scene, ensure_uid=False)
    dobradica = [linha for linha in linhas if linha['code'] == 'DOBRADICA']
    check("lista de ferragens conta as dobradiças",
          bool(dobradica) and dobradica[0]['quantity'] == 10, str(dobradica[:1]))

    # A dobradiça fica **na** linha do pivô, então o giro aparece na profundidade (Y), não na largura (X).
    fechada = posicao_xy(primeira)
    anim.alternar(porta)
    passo_frames(porta)
    andou = distancia_xy(fechada, posicao_xy(primeira))
    check("porta aberta leva a dobradiça no pivô da folha", andou > 50.0, f"{andou:.1f} mm")
    anim.alternar(porta)
    passo_frames(porta)
    voltou = distancia_xy(fechada, posicao_xy(primeira))
    check("fechar devolve a dobradiça ao lugar", voltou < 0.01, f"{voltou:.3f} mm")
    check("nenhum timer de animação sobrou de pé", not anim._handles and not anim._animacoes)
    return root


# 3 — lista de materiais -------------------------------------------------------------------------------------------
def run_lista(ctx, root):
    solto = bpy.data.objects.new("Malha solta", bpy.data.meshes.new("Malha solta"))
    ctx.scene.collection.objects.link(solto)
    solto.location = (5.0, 0.0, 0.0)
    resultado = bpy.ops.caffmob.lista_materiais()
    texto = bpy.data.texts.get(BLOCO_LISTA)
    conteudo = texto.as_string() if texto is not None else ""
    check("Lista de materiais roda e grava o texto do arquivo",
          resultado == {'FINISHED'} and bool(conteudo), f"{len(conteudo)} caractere(s)")
    check("lista tem as chapas, as ferragens e a malha sem marca",
          all(marca in conteudo for marca in ('LATERAL', 'PORTA', 'DOBRADICA', 'OUTRO')),
          conteudo.splitlines()[0] if conteudo else "")
    linhas_dobradica = [linha for linha in conteudo.splitlines() if 'DOBRADICA' in linha]
    quantidade = sum(int(linha.split()[-1]) for linha in linhas_dobradica)
    check("dobradiças somadas na lista com as medidas do modelo",
          quantidade == 10 and all('87.7' in linha and '27.2' in linha for linha in linhas_dobradica),
          f"{quantidade} dobradiça(s) em {len(linhas_dobradica)} linha(s)")
    check("lista fecha com o total de linhas e de peças", 'peça(s)' in conteudo)
    bpy.data.objects.remove(solto, do_unlink=True)


# 4 — .skp na lista de importação ----------------------------------------------------------------------------------
class LayoutFalso:
    """Layout mínimo para desenhar o menu sem interface: guarda os `bl_idname` pedidos."""

    def __init__(self):
        self.itens = []
        self.layout = self

    def operator(self, idname, **_kw):
        self.itens.append(idname)


def run_skp(ctx):
    env.clean_scene()
    layout = LayoutFalso()
    ops_import.menu_importar(layout, ctx)
    check("menu File > Import pede o importador do SketchUp",
          layout.itens == ['caffmob.import_skp'], str(layout.itens))
    resultado = bpy.ops.caffmob.import_skp(filepath=str(FIXTURE))
    grupos = list(ctx.selected_objects)
    check("importa o .skp pelo operador do menu",
          resultado == {'FINISHED'} and bool(grupos), f"{len(grupos)} grupo(s) de {len(ctx.scene.objects)} objeto(s)")
    try:            # o relatório de erro do operador chega ao Python como exceção
        recusado = bpy.ops.caffmob.import_skp(filepath=str(FIXTURE.with_suffix('.txt')))
    except RuntimeError:
        recusado = {'CANCELLED'}
    check("importador recusa arquivo que não é .skp", recusado == {'CANCELLED'}, str(recusado))


# 5 — conversão peça por peça --------------------------------------------------------------------------------------
def cubo(nome, x0, y0, z0, x1, y1, z1):
    """Caixa de malha em metros entre os cantos pedidos."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = ctx_object()
    obj.name = nome
    obj.data.name = nome
    obj.location = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    obj.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.context.view_layer.update()
    return obj


def ctx_object():
    return bpy.context.view_layer.objects.active


def run_conversao(ctx):
    env.clean_scene()
    t, largura, altura, profundidade = 0.015, 1.0, 2.4, 0.51
    esquerda = cubo("Peça lateral esquerda", -0.5, -profundidade, 0.0, -0.5 + t, 0.0, altura)
    direita = cubo("Peça lateral direita", 0.5 - t, -profundidade, 0.0, 0.5, 0.0, altura)
    base = cubo("Peça base inferior", -0.5, -profundidade, 0.0, 0.5, 0.0, t)
    topo = cubo("Peça base superior", -0.5, -profundidade, altura - t, 0.5, 0.0, altura)
    porta = cubo("Peça porta", -0.5, -profundidade - t, t, 0.0, -profundidade, altura - t)
    for obj, papel in ((esquerda, 'lateral_esq'), (direita, 'lateral_dir'), (base, 'base_inf'),
                       (topo, 'base_sup'), (porta, 'porta')):
        selecionar(obj)
        bpy.ops.caffmob.armario_v2_marcar_papel(papel=papel)
    marcadas = ponte.pecas_marcadas(ctx.scene)
    check("marcar guarda uma peça por papel",
          sorted(marcadas) == ['base_inf', 'base_sup', 'lateral_dir', 'lateral_esq', 'porta'], str(sorted(marcadas)))
    intrusa = cubo("Peça intrusa", 2.0, 0.0, 0.0, 2.1, 0.1, 0.1)
    selecionar(intrusa)
    bpy.ops.caffmob.armario_v2_marcar_papel(papel='porta')
    check("um papel aceita uma peça só", ponte.pecas_marcadas(ctx.scene)['porta'] is intrusa)
    selecionar(intrusa)
    bpy.ops.caffmob.armario_v2_marcar_papel(papel='NENHUM')
    selecionar(porta)
    bpy.ops.caffmob.armario_v2_marcar_papel(papel='porta')
    bpy.data.objects.remove(intrusa, do_unlink=True)

    resultado = bpy.ops.caffmob.armario_v2_converter_pecas()
    root = next((obj for obj in ctx.scene.objects if getattr(obj, 'btm_armario', None) is not None
                 and build.e_raiz(obj)), None)
    check("converter peça por peça cria o armário", resultado == {'FINISHED'} and root is not None, str(resultado))
    if root is None:
        return
    armario = root.btm_armario
    check("medidas vêm das peças apontadas",
          abs(armario.largura - 1000.0) < 1.0 and abs(armario.altura - 2400.0) < 1.0
          and abs(armario.profundidade - 510.0) < 1.0,
          f"{armario.largura:.0f} × {armario.altura:.0f} × {armario.profundidade:.0f} mm")
    check("presença por papel apontado",
          armario.lateral_esq_ativa and armario.lateral_dir_ativa and armario.base_inf_ativa
          and armario.base_sup_ativa and armario.porta_ativa and not armario.fundo_ativo)
    check("conversão não gera peça nenhuma", not pecas(root), f"{len(pecas(root))} peça(s)")
    check("originais ficam ocultas e fora do corte",
          all(obj.hide_viewport and obj.btm_cut_exclude for obj in (esquerda, direita, base, topo, porta)))
    check("as marcas da conversão são limpas", not ponte.pecas_marcadas(ctx.scene))

    selecionar(root)
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    geradas = [caixa(item)[0] for item in por_papel(root, 'LATERAL')]

    def mais_perto(alvo):
        return min(geradas, key=lambda canto: abs(canto[0] - alvo[0]) + abs(canto[2] - alvo[2]))

    mesma = len(geradas) == 2 and all(
        abs(mais_perto(caixa(original)[0])[i] - caixa(original)[0][i]) < 1.0
        for original in (esquerda, direita) for i in range(3))
    check("Gerar cai onde as peças originais estavam", resultado == {'FINISHED'} and mesma,
          f"{sorted(geradas)} vs {sorted(caixa(item)[0] for item in (esquerda, direita))}")

    # Separar as peças soltas de uma malha única.
    env.clean_scene()
    junto = cubo("Malha com duas peças", 0.0, 0.0, 0.0, 0.1, 0.1, 0.1)
    solta = cubo("Peça solta", 0.3, 0.0, 0.0, 0.4, 0.1, 0.1)
    selecionar(junto)
    solta.select_set(True)
    bpy.context.view_layer.objects.active = junto
    bpy.ops.object.join()
    selecionar(junto)
    antes = len([obj for obj in ctx.scene.objects if obj.type == 'MESH'])
    resultado = bpy.ops.caffmob.armario_v2_separar_pecas()
    depois = len([obj for obj in ctx.scene.objects if obj.type == 'MESH'])
    check("Separar peças da malha devolve as peças soltas",
          resultado == {'FINISHED'} and depois == antes + 1, f"{antes} → {depois} malha(s)")


def script():
    ctx = bpy.context
    check("importador .skp registrado", bpy.types.CAFFMOB_OT_import_skp.is_registered)
    check("marcação, conversão e separação registradas",
          bpy.types.CAFFMOB_OT_armario_v2_marcar_papel.is_registered
          and bpy.types.CAFFMOB_OT_armario_v2_converter_pecas.is_registered
          and bpy.types.CAFFMOB_OT_armario_v2_separar_pecas.is_registered)
    root = run_dobradica(ctx)
    run_lista(ctx, root)
    run_skp(ctx)
    run_conversao(ctx)


try:
    script()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")

print(f"blender_026_dobradica_lista_conversao_smoke: "
      f"{'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
