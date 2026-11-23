"""Teste de fumaça da feature 017 (T033): o construtor de armário v2 de ponta a ponta, sem janela.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_017_armario_smoke.py

O `tests/_blender_env.py` registra o add-on inteiro, então tudo aqui passa pelos `bl_idname` de verdade:

1. registro real: o `Abrir` do armário assume `caffmob.cabinet_editor` (o editor 2D saiu em T027), painel,
   operadores, menu de contexto, HUD, propriedades e o contrato de chapas na cena;
2. abrir num projeto limpo cria o armário vazio e semeia o contrato; Montar Caixa gera a caixa;
3. contrato ausente recusa; chapa de 3000 bloqueia e, com o bloqueio desligado, gera com aviso;
4. bloco de gavetas entra no corte sem peça de ferragem; corrediça do OBJ e conjunto de reserva com as três marcas
   (trilho externo, interno e gaiola), e a gaiola andando metade do curso da gaveta;
5. deslizante com base por dentro recua prateleira e gavetas na profundidade do trilho;
6. Abrir/Fechar grava `btm_armario.aberto` e leva a frente 72% da profundidade; o segundo toque volta ao fechado;
6.1. contra-frente e peça de trás saem como travessa de 90 mm, trocam de eixo com a orientação, entram no corte e
   saem quando a presença é desmarcada;
6.2. os cinco operadores de inserção criam divisória, prateleira, matriz, bloco de gavetas e interno no vão ativo e
   recusam sem escrever quando a peça não cabe;
7. Cancelar devolve o instantâneo da abertura;
8. módulo de biblioteca: Gerar pelo motor novo oculta e marca o antigo, e o corte deixa de listar as peças dele;
9. móvel sem `btm_armario` (construção antiga): Abrir recusa, avisa e não cria armário nenhum;
10. `unregister()` sem operador, propriedade, menu, HUD, timer ou contrato pendurado.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.armario_v2 import anim, build, hud, menu, ops, panel, ponte, vaos  # noqa: E402
from caffmob_draw.cutting import part_extractor  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def raiz_v2():
    for obj in bpy.data.objects:
        if obj.type != 'EMPTY':
            continue
        if any(colecao.name == build.COLECAO for colecao in obj.users_collection):
            return obj
    return None


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


def papel(item):
    return item.btm_armario_parte.papel


def por_papel(root, nome):
    return [item for item in pecas(root) if papel(item) == nome]


def corte(ctx):
    return part_extractor.extract_production_parts(ctx)[0]


def profundidade(item):
    """Profundidade (Y) da peça em mm, a partir da caixa da malha."""
    minimo = min(v.co.y for v in item.data.vertices)
    maximo = max(v.co.y for v in item.data.vertices)
    return (maximo - minimo) * 1000.0


def centro_y(item):
    """Y do centro da peça em mm, no mundo: a malha carrega a posição e a animação mexe no objeto."""
    pontos = [item.matrix_world @ vertice.co for vertice in item.data.vertices]
    return sum(ponto.y for ponto in pontos) / len(pontos) * 1000.0


def modulo_antigo(nome="Módulo antigo", largura=0.8):
    """Módulo `btm` de antes da 017: `btm_plane` de módulo e `btm_cabinet` preenchido, sem `btm_armario`."""
    objeto = bpy.data.objects.new(nome, bpy.data.meshes.new(nome))
    bpy.context.scene.collection.objects.link(objeto)
    objeto.btm_plane.object_kind = 'MODULE'
    objeto.btm_cabinet.width = largura
    objeto.btm_cabinet.height = 0.9
    objeto.btm_cabinet.depth = 0.55
    objeto.btm_cabinet.thickness = 0.015
    return objeto


def passo_frames(alvo):
    """Roda os quadros do timer da animação à mão: em `--background` não há laço de eventos que o acorde."""
    funcao = anim._handles.get(alvo.name)
    registrado = funcao is not None and bpy.app.timers.is_registered(funcao)
    for _ in range(anim.QUADROS + 2):
        if funcao is None:
            break
        funcao()
        funcao = anim._handles.get(alvo.name)
    return registrado


def run_registro():
    check("Abrir do armário registrado", ops.BTM_OT_ArmarioV2Abrir.is_registered)
    check("Gerar/Montar/Cancelar/Alternar registrados",
          all(cls.is_registered for cls in (ops.BTM_OT_ArmarioV2Gerar, ops.BTM_OT_ArmarioV2MontarCaixa,
                                            ops.BTM_OT_ArmarioV2Cancelar, anim.BTM_OT_ArmarioV2Alternar)))
    check("painel do construtor registrado", panel.BTM_PT_ArmarioV2.is_registered)
    check("duplicar e excluir registrados", all(cls.is_registered for cls in menu.classes))
    check("operadores da ponte registrados",
          all(cls.is_registered for cls in (ponte.BTM_OT_ArmarioV2GerarDoModulo,
                                            ponte.BTM_OT_ArmarioV2RecriarDoModulo)))
    check("propriedades penduradas no Object e na Scene",
          hasattr(bpy.types.Object, 'btm_armario') and hasattr(bpy.types.Object, 'btm_armario_parte')
          and hasattr(bpy.types.Scene, 'btm_armario_contrato'))
    check("editor 2D antigo fora do registro", not hasattr(bpy.types.WindowManager, 'btm_cabinet_editor'))
    check("HUD com handler de desenho", len(hud._handles) >= 1, str(len(hud._handles)))
    # O Blender não expõe as funções anexadas ao menu (guardadas no C, e `remove` não reclama quando falta), então o
    # menu é conferido pelo que ele desenha, em `run_gavetas`, e pelas classes depois do `unregister`.


def run_construtor(ctx):
    env.clean_scene()
    selecionar(None)
    resultado = bpy.ops.caffmob.cabinet_editor()
    root = raiz_v2()
    check("Abrir num projeto limpo cria o armário vazio", resultado == {'FINISHED'} and root is not None,
          str(resultado))
    check("Abrir não cria passo de desfazer nem peça", root is not None and not pecas(root),
          f"{len(pecas(root)) if root is not None else '?'} peças")
    check("Abrir grava o instantâneo", bool(root.btm_armario.snapshot) if root is not None else False)
    check("Abrir semeia o contrato de chapas", ctx.scene.btm_armario_contrato.configurado)
    selecionar(root)
    resultado = bpy.ops.caffmob.armario_v2_montar_caixa()
    papeis = sorted(papel(item) for item in pecas(root))
    check("Montar Caixa gera as quatro chapas e o fundo", resultado == {'FINISHED'} and papeis == [
        'BASE_INF', 'BASE_SUP', 'FUNDO', 'LATERAL', 'LATERAL'], str(papeis))
    check("Montar Caixa marca o armário como gerado", root.btm_armario.gerado)
    return root


def run_contrato(ctx, root):
    antes = len(pecas(root))
    ctx.scene.btm_armario_contrato.configurado = False
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    check("sem contrato o Gerar recusa e não mexe nas peças",
          resultado == {'CANCELLED'} and len(pecas(root)) == antes, str(resultado))
    ctx.scene.btm_armario_contrato.configurado = True
    root.btm_armario.largura = 3000.0
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    check("chapa de 3000 bloqueia o Gerar", resultado == {'CANCELLED'} and len(pecas(root)) == antes,
          str(resultado))
    root.btm_armario.bloquear_chapa = False
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    base = por_papel(root, 'BASE_INF')[0].btm_armario_parte.comprimento_mm
    check("sem bloqueio gera com aviso e a base passa da chapa",
          resultado == {'FINISHED'} and abs(base - 2970.0) < 0.01 and len(pecas(root)) == antes, f"{base} mm")
    root.btm_armario.largura = 1000.0
    root.btm_armario.bloquear_chapa = True
    bpy.ops.caffmob.armario_v2_gerar()


class LayoutFalso:
    """Layout mínimo para desenhar o menu sem interface: guarda os `bl_idname` pedidos."""

    def __init__(self):
        self.itens = []

    def separator(self):
        pass

    def operator(self, idname, **_kw):
        self.itens.append(idname)


def run_gavetas(ctx, root):
    armario = root.btm_armario
    gaveta = armario.gavetas.add()
    gaveta.vao, gaveta.indice, gaveta.altura, gaveta.modelo = 's0', 0, 700.0, 's_cf_reta'
    gaveta.corredica_3d = True
    gaveta.separador_colunas = 2
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    frentes = por_papel(root, 'FRENTE_GAVETA')
    separadores = [item for item in pecas(root) if papel(item) == 'SEPARADOR']
    check("bloco de gavetas gera a frente e as chapas da caixa", resultado == {'FINISHED'} and len(frentes) == 1
          and bool(separadores), f"{len(frentes)} frente(s), {len(separadores)} separador(es)")
    selecionar(frentes[0])
    layout = LayoutFalso()
    menu.desenhar_menu(layout, ctx)
    check("menu de contexto oferece Abrir/Fechar na frente",
          'caffmob.armario_v2_alternar' in layout.itens, str(layout.itens))
    itens = corte(ctx)
    ferragem = [item for item in itens if item.source == 'ARMARIO_V2' and
                (not item.component or item.component == 'UNCLASSIFIED')]
    corredica = [item for item in itens if item.source == 'ARMARIO_V2' and 'CORREDIÇA' in item.name.upper()]
    check("corte lista o armário v2 sem peça de ferragem",
          itens and not ferragem and not corredica, str([item.name for item in ferragem + corredica][:4]))
    return frentes[0]


def run_peca_escolhida(ctx, root):
    """O inspetor só reconhece peça de armário v2: papel gravado **e** raiz v2 acima (T034)."""
    selecionar(root)
    na_raiz = panel._peca_escolhida(ctx)
    hud_na_raiz = hud._peca(ctx)
    frente = por_papel(root, 'FRENTE_GAVETA')[0]
    selecionar(frente)
    na_peca = panel._peca_escolhida(ctx)
    hud_na_peca = hud._peca(ctx)
    malha = bpy.data.meshes.new('Chapa solta')
    solta = bpy.data.objects.new('Chapa solta', malha)
    ctx.scene.collection.objects.link(solta)
    solta.btm_armario_parte.papel = 'LATERAL'
    selecionar(solta)
    com_papel_sem_raiz = panel._peca_escolhida(ctx)
    hud_solta = hud._peca(ctx)
    bpy.data.objects.remove(solta, do_unlink=True)
    check("inspetor ignora a raiz, o objeto solto e aceita a peça",
          na_raiz == '' and com_papel_sem_raiz == '' and na_peca == frente.name,
          f"raiz {na_raiz!r}; solta {com_papel_sem_raiz!r}; peça {na_peca!r}")
    # A comparação é feita com a chapa solta ainda na cena: depois do `remove` a seleção fica vazia e `None` não
    # provaria filtro nenhum.
    check("HUD usa o mesmo critério do painel (raiz, solta com papel e peça)",
          hud_na_raiz is None and hud_solta is None and hud_na_peca is frente,
          f"raiz {hud_na_raiz!r}; solta {getattr(hud_solta, 'name', hud_solta)!r}; "
          f"peça {getattr(hud_na_peca, 'name', hud_na_peca)!r}")


def run_deslizante(ctx, root):
    selecionar(root)
    armario = root.btm_armario
    spec = ops.spec_do_armario(root)
    divisoes, _prateleira = vaos.inserir_horizontal([], spec, 's0', 'prat_fixa')
    ops.gravar_divisoes(armario, divisoes)
    bpy.ops.caffmob.armario_v2_gerar()
    prateleira = por_papel(root, 'PRATELEIRA')
    if not prateleira:
        check("deslizante: prateleira de partida", False)
        return
    antes = profundidade(prateleira[0])
    gaveta_antes = centro_y(por_papel(root, 'FRENTE_GAVETA')[0])
    armario.deslizante_ativa = True
    armario.deslizante_base = 'DENTRO'
    armario.trilho_profundidade = 70.0
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    depois = profundidade(por_papel(root, 'PRATELEIRA')[0])
    gaveta_depois = centro_y(por_papel(root, 'FRENTE_GAVETA')[0])
    check("deslizante por dentro recua a prateleira em 70 mm",
          resultado == {'FINISHED'} and abs((antes - depois) - 70.0) < 0.01, f"{antes:.1f} → {depois:.1f} mm")
    check("deslizante por dentro recua a frente da gaveta em 70 mm",
          abs((gaveta_depois - gaveta_antes) - 70.0) < 0.01, f"{gaveta_antes:.1f} → {gaveta_depois:.1f} mm")
    check("a lateral continua na profundidade total",
          abs(profundidade(por_papel(root, 'LATERAL')[0]) - spec.profundidade) < 0.01)
    armario.deslizante_ativa = False
    bpy.ops.caffmob.armario_v2_gerar()


def de_ferragem(root, nome):
    return [item for item in pecas(root) if getattr(item.btm_armario_parte, 'ferragem', 'NENHUMA') == nome]


def da_gaveta(item, indice):
    """A peça pertence à gaveta `indice`: o sufixo que o `build` usa para agrupar e a animação para andar junto."""
    if ' da gaveta ' not in item.name:
        return False
    return item.name.rsplit(' da gaveta ', 1)[1].split()[0] == str(indice)


def run_corredica(ctx, root):
    """T039: duas corrediças por gaveta, com o OBJ e com o conjunto de reserva, e a gaiola a meio curso."""
    selecionar(root)
    armario = root.btm_armario
    while len(armario.gavetas):
        armario.gavetas.remove(0)
    for indice in range(4):
        gaveta = armario.gavetas.add()
        gaveta.vao, gaveta.indice, gaveta.altura, gaveta.modelo = 's0', indice, 180.0, 's_cf_reta'
        gaveta.corredica_3d = True
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    externos = de_ferragem(root, 'TRILHO_EXT')
    internos = de_ferragem(root, 'TRILHO_INT')
    gaiolas = de_ferragem(root, 'GAIOLA')
    papel_vazio = all(not item.btm_armario_parte.papel for item in externos + internos + gaiolas)
    check("corrediça do OBJ: duas por gaveta com trilho externo, interno e gaiola",
          resultado == {'FINISHED'} and len(externos) == 8 and len(internos) == 8 and len(gaiolas) >= 8
          and papel_vazio, f"{len(externos)} externo(s), {len(internos)} interno(s), {len(gaiolas)} gaiola(s); "
          f"papel vazio {papel_vazio}")
    check("corrediça entra como peça da mesma gaveta",
          all(' da gaveta ' in item.name for item in externos + internos + gaiolas)
          and len([indice for indice in range(1, 5) if [item for item in externos if da_gaveta(item, indice)]]) == 4,
          str(sorted({item.name.rsplit(' da gaveta ', 1)[-1] for item in externos})))
    itens = corte(ctx)
    check("plano de corte segue sem peça de corrediça",
          not [item for item in itens if 'CORREDI' in item.name.upper()],
          str([item.name for item in itens if 'CORREDI' in item.name.upper()][:4]))

    caminho = build._caminho_obj
    build._caminho_obj = lambda: Path('/caminho/que/nao/existe/slide-st48-0200-0.obj')
    build._modelos.clear()
    try:
        resultado = bpy.ops.caffmob.armario_v2_gerar()
        reserva = [item for item in pecas(root) if getattr(item.btm_armario_parte, 'ferragem', 'NENHUMA')
                   not in ('', 'NENHUMA')]
        marcas = sorted({item.btm_armario_parte.ferragem for item in reserva})
        check("sem o OBJ a geração cai no conjunto de reserva com as mesmas três marcas",
              resultado == {'FINISHED'} and len(reserva) == 24 and marcas == ['GAIOLA', 'TRILHO_EXT', 'TRILHO_INT']
              and all(not item.btm_armario_parte.papel for item in reserva),
              f"{len(reserva)} peça(s): {marcas}")
    finally:
        build._caminho_obj = caminho
        build._modelos.clear()
    bpy.ops.caffmob.armario_v2_gerar()
    frente = por_papel(root, 'FRENTE_GAVETA')[0]
    gaiola = [item for item in de_ferragem(root, 'GAIOLA') if da_gaveta(item, 1)][0]
    y_antes = centro_y(gaiola)
    anim.alternar(frente)
    passo_frames(frente)
    curso = frente.btm_armario_parte.curso_mm
    deslocamento = abs(centro_y(gaiola) - y_antes)
    check("Abrir/Fechar move a gaiola a 50% do curso da gaveta",
          abs(deslocamento - curso * 0.5) < 0.01, f"{deslocamento:.2f} mm de {curso * 0.5:.2f} mm")
    anim.alternar(frente)
    passo_frames(frente)


def run_animacao(ctx, root):
    armario = root.btm_armario
    frente = por_papel(root, 'FRENTE_GAVETA')[0]
    y_fechado = centro_y(frente)
    aberto = anim.alternar(frente)
    registrado = passo_frames(frente)
    y_aberto = centro_y(frente)
    curso = frente.btm_armario_parte.curso_mm
    check("Abrir agenda o timer da animação", aberto is True and registrado)
    check("frente da gaveta abre 72% da profundidade",
          abs(abs(y_aberto - y_fechado) - curso) < 0.01, f"{curso:.1f} mm; {abs(y_aberto - y_fechado):.1f} mm")
    check("Abrir grava o estado no armário", armario.aberto is True)
    anim.alternar(frente)
    passo_frames(frente)
    check("segundo toque fecha e volta a peça",
          abs(centro_y(frente) - y_fechado) < 1e-3 and armario.aberto is False, f"{centro_y(frente):.3f} mm")
    check("nenhum timer sobrou de pé", not anim._handles and not anim._animacoes)


def extensao(item, eixo):
    """Extensão da peça em mm no eixo pedido ('x', 'y' ou 'z'), no mundo."""
    pontos = [item.matrix_world @ vertice.co for vertice in item.data.vertices]
    valores = [getattr(ponto, eixo) for ponto in pontos]
    return (max(valores) - min(valores)) * 1000.0


def run_travessas(ctx, root):
    """T044: contra-frente e peça de trás geradas como travessa de 90 mm, com presença e no corte."""
    selecionar(root)
    armario = root.btm_armario
    for colecao in (armario.divisoes, armario.gavetas, armario.internos):
        while len(colecao):
            colecao.remove(0)
    armario.contra_frente_ativa = True
    armario.peca_tras_ativa = True
    armario.orientacao_frente = 'EM_PE'
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    frente = por_papel(root, 'CONTRA_FRENTE')
    tras = por_papel(root, 'PECA_TRAS')
    medida = frente[0].btm_armario_parte if frente else None
    check("contra-frente e peça de trás geradas como travessa de 90 mm",
          resultado == {'FINISHED'} and len(frente) == 1 and len(tras) == 1 and medida is not None
          and abs(medida.comprimento_mm - 970.0) < 0.01 and abs(medida.largura_mm - 90.0) < 0.01
          and abs(medida.espessura_mm - 15.0) < 0.01,
          f"{len(frente)} frente(s), {len(tras)} trás; "
          f"{getattr(medida, 'comprimento_mm', '?')} × {getattr(medida, 'largura_mm', '?')} × "
          f"{getattr(medida, 'espessura_mm', '?')} mm")
    if frente:
        alto, fundo = extensao(frente[0], 'z'), extensao(frente[0], 'y')
        check("contra-frente em pé: 90 mm na altura e 15 mm na profundidade",
              abs(alto - 90.0) < 0.01 and abs(fundo - 15.0) < 0.01, f"z {alto:.1f}; y {fundo:.1f}")
    armario.orientacao_frente = 'DEITADA'
    bpy.ops.caffmob.armario_v2_gerar()
    frente = por_papel(root, 'CONTRA_FRENTE')
    check("contra-frente deitada troca o eixo de 90 mm",
          bool(frente) and abs(extensao(frente[0], 'y') - 90.0) < 0.01
          and abs(extensao(frente[0], 'z') - 15.0) < 0.01,
          f"y {extensao(frente[0], 'y') if frente else '?'}; z {extensao(frente[0], 'z') if frente else '?'}")
    nomes = [item.name.upper() for item in corte(ctx) if item.source == 'ARMARIO_V2']
    check("corte lista as duas travessas",
          any('CONTRA' in nome for nome in nomes) and any('TRÁS' in nome for nome in nomes),
          str([nome for nome in nomes if 'CONTRA' in nome or 'TRÁS' in nome]))
    armario.peca_tras_ativa = False
    bpy.ops.caffmob.armario_v2_gerar()
    nomes = [item.name.upper() for item in corte(ctx) if item.source == 'ARMARIO_V2']
    check("desmarcar a peça de trás remove só ela da cena e do corte",
          not por_papel(root, 'PECA_TRAS') and len(por_papel(root, 'CONTRA_FRENTE')) == 1
          and not any('TRÁS' in nome for nome in nomes), str([n for n in nomes if 'TRÁS' in n]))
    armario.contra_frente_ativa = False
    armario.orientacao_frente = 'EM_PE'
    bpy.ops.caffmob.armario_v2_gerar()


def run_insercao(ctx, root):
    """T051: os cinco operadores de inserção (D-21), no vão ativo, com recusa sem escrita."""
    selecionar(root)
    armario = root.btm_armario
    for colecao in (armario.divisoes, armario.gavetas, armario.internos):
        while len(colecao):
            colecao.remove(0)
    for classe in (ops.BTM_OT_ArmarioV2InserirDivisoria, ops.BTM_OT_ArmarioV2InserirPrateleira,
                   ops.BTM_OT_ArmarioV2InserirMatriz, ops.BTM_OT_ArmarioV2CriarBlocoGavetas,
                   ops.BTM_OT_ArmarioV2InserirInterno):
        check(f"{classe.bl_idname} com passo de desfazer", 'UNDO' in classe.bl_options)
    vao = ops.vao_ativo(armario)
    resultado = bpy.ops.caffmob.armario_v2_inserir_divisoria()
    check("Inserir divisória cria a peça no vão ativo e gera",
          resultado == {'FINISHED'} and len(armario.divisoes) == 1 and armario.divisoes[0].vao == vao
          and bool(por_papel(root, 'DIVISORIA')),
          f"{len(armario.divisoes)} divisória(s) no vão {vao!r}")
    resultado = bpy.ops.caffmob.armario_v2_inserir_prateleira()
    check("Inserir prateleira cria a segunda peça",
          resultado == {'FINISHED'} and len(armario.divisoes) == 2 and bool(por_papel(root, 'PRATELEIRA')))
    armario.matriz_linhas, armario.matriz_colunas = 2, 1
    armario.matriz_prioridade = 'VERTICAL'
    resultado = bpy.ops.caffmob.armario_v2_inserir_matriz()
    verticais = [item for item in armario.divisoes if item.eixo == 'VERTICAL']
    check("Inserir matriz de 2 × 1 cria uma divisória e duas prateleiras por vão",
          resultado == {'FINISHED'} and len(verticais) == 2 and len(armario.divisoes) == 7,
          f"{len(verticais)} vertical(is), {len(armario.divisoes)} no total")
    armario.bloco_quantidade, armario.bloco_altura = 2, 400.0
    resultado = bpy.ops.caffmob.armario_v2_criar_bloco_gavetas()
    check("Criar bloco de gavetas grava as gavetas e gera as frentes",
          resultado == {'FINISHED'} and len(armario.gavetas) == 2
          and [item.indice for item in armario.gavetas] == [0, 1]
          and len(por_papel(root, 'FRENTE_GAVETA')) == 2)
    antes = len(armario.gavetas)
    armario.bloco_altura = 3000.0
    resultado = bpy.ops.caffmob.armario_v2_criar_bloco_gavetas()
    check("bloco que não cabe recusa sem escrever",
          resultado == {'CANCELLED'} and len(armario.gavetas) == antes, str(resultado))
    armario.bloco_altura = 400.0
    armario.interno_tipo = 'CALCEIRO'
    resultado = bpy.ops.caffmob.armario_v2_inserir_interno()
    internos = list(armario.internos)
    check("Inserir interno cria o calceiro na posição inicial",
          resultado == {'FINISHED'} and len(internos) == 1 and internos[0].tipo == 'CALCEIRO'
          and abs(internos[0].altura - 480.0) < 0.01, str([(i.tipo, i.altura) for i in internos]))


def run_cancelar(ctx, root):
    """O instantâneo é o da abertura, quando o armário ainda estava vazio: Cancelar volta para lá."""
    selecionar(root)
    armario = root.btm_armario
    guardado = armario.largura
    armario.largura = 1200.0
    bpy.ops.caffmob.armario_v2_gerar()
    antes = len(pecas(root))
    resultado = bpy.ops.caffmob.armario_v2_cancelar()
    check("Cancelar devolve o instantâneo da abertura",
          resultado == {'FINISHED'} and abs(armario.largura - guardado) < 1e-6 and not pecas(root)
          and not armario.gerado and not armario.gavetas, f"{antes} → {len(pecas(root))} peças")


def run_ponte(ctx, root):
    base = tf.BaseCabinet()
    base.create("Balcao")
    base.obj.location.x = 4.0
    env.settle()
    antes = corte(ctx)
    do_modulo = [item for item in antes if item.module_ref == base.obj.name]
    check("corte lista as peças do módulo de biblioteca antes de Gerar", bool(do_modulo), f"{len(do_modulo)} peças")
    selecionar(base.obj)
    resultado = bpy.ops.caffmob.armario_v2_gerar_do_modulo()
    novo = bpy.data.objects.get(ctx.view_layer.objects.active.name) if ctx.view_layer.objects.active else None
    check("Gerar pelo motor novo cria o armário v2", resultado == {'FINISHED'} and novo is not None
          and novo.btm_armario.gerado and novo.btm_armario.origem == base.obj.name, str(resultado))
    check("módulo antigo oculto e marcado",
          base.obj.hide_viewport and base.obj.btm_cut_exclude)
    depois = corte(ctx)
    restantes = [item for item in depois if item.module_ref == base.obj.name]
    check("corte não duplica as peças do módulo convertido", not restantes, str([r.name for r in restantes][:4]))
    check("corte lista as peças do armário v2 do módulo",
          bool([item for item in depois if item.source == 'ARMARIO_V2' and item.module_ref == novo.name]),
          str(sorted({item.module_ref for item in depois if item.source == 'ARMARIO_V2'})))
    nome_novo = novo.name
    selecionar(novo)
    resultado = bpy.ops.caffmob.armario_v2_recriar_do_modulo()
    check("Recriar do módulo devolve o módulo e apaga o armário",
          resultado == {'FINISHED'} and not base.obj.hide_viewport and bpy.data.objects.get(nome_novo) is None,
          str(resultado))
    return base.obj


def run_ponte_btm(ctx):
    """Caso do A001: módulo `btm` convertido — o caminho sintético não pode continuar emitindo as peças dele."""
    antigo = modulo_antigo("Módulo btm")
    antigo.btm_cabinet.shelves = 1
    selecionar(antigo)
    antes = [item for item in corte(ctx) if item.module_ref == antigo.name]
    resultado = bpy.ops.caffmob.armario_v2_gerar_do_modulo()
    raiz = ctx.view_layer.objects.active
    check("Gerar pelo motor novo num módulo btm",
          resultado == {'FINISHED'} and raiz is not None and raiz.btm_armario.origem == antigo.name, str(resultado))
    depois = [item for item in corte(ctx) if item.module_ref == antigo.name]
    check("corte não duplica as peças do módulo btm convertido", bool(antes) and not depois,
          f"{len(antes)} → {len(depois)} peças")
    selecionar(raiz)
    bpy.ops.caffmob.armario_v2_recriar_do_modulo()
    check("Recriar devolve o módulo btm ao corte",
          bool([item for item in corte(ctx) if item.module_ref == antigo.name]) and not antigo.hide_viewport)


def run_construcao_antiga(ctx):
    antigo = modulo_antigo()
    selecionar(antigo)
    largura = antigo.btm_cabinet.width
    armarios = [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and getattr(obj, 'btm_armario', None)
                is not None and any(colecao.name == build.COLECAO for colecao in obj.users_collection)]
    liberado = ops.BTM_OT_ArmarioV2Abrir.poll(ctx)
    depois = [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and getattr(obj, 'btm_armario', None)
              is not None and any(colecao.name == build.COLECAO for colecao in obj.users_collection)]
    check("Abrir num móvel sem btm_armario recusa", liberado is False)
    pecas_do_antigo = [filho for filho in antigo.children if filho.btm_armario_parte.papel]
    check("móvel da construção antiga intocado",
          antigo.btm_cabinet.width == largura and not antigo.btm_armario.gerado and not pecas_do_antigo,
          f"largura {largura} → {antigo.btm_cabinet.width}; gerado {antigo.btm_armario.gerado}; "
          f"{len(pecas_do_antigo)} peça(s)")
    check("nenhum armário v2 foi criado para ele", len(depois) == len(armarios), f"{len(armarios)} → {len(depois)}")


def run_unregister(ctx):
    timers = list(anim._handles.values())
    addon_ok = True
    try:
        import caffmob_draw as addon
        addon.unregister()
    except Exception:
        traceback.print_exc()
        addon_ok = False
    check("unregister sem exceção", addon_ok)
    check("propriedades removidas",
          not hasattr(bpy.types.Object, 'btm_armario') and not hasattr(bpy.types.Object, 'btm_armario_parte')
          and not hasattr(bpy.types.Scene, 'btm_armario_contrato') and not hasattr(bpy.types.Object, 'btm_plane'))
    check("operadores e painel do armário desregistrados",
          not any(cls.is_registered for cls in (ops.BTM_OT_ArmarioV2Abrir, ops.BTM_OT_ArmarioV2Gerar,
                                                panel.BTM_PT_ArmarioV2, anim.BTM_OT_ArmarioV2Alternar,
                                                menu.BTM_OT_ArmarioV2Duplicar, menu.BTM_OT_ArmarioV2Excluir)))
    # `MENU.remove` não levanta quando a função falta, então "sem sobras" aqui é a classe do item fora do registro.
    check("HUD e timers limpos", not hud._handles and not hud._keymaps and not anim._handles
          and not anim._animacoes and not any(bpy.app.timers.is_registered(f) for f in timers),
          f"{len(timers)} timer(s)")


def script():
    ctx = bpy.context
    run_registro()
    root = run_construtor(ctx)
    run_contrato(ctx, root)
    run_gavetas(ctx, root)
    run_peca_escolhida(ctx, root)
    run_deslizante(ctx, root)
    run_corredica(ctx, root)
    run_animacao(ctx, root)
    run_travessas(ctx, root)
    run_insercao(ctx, root)
    run_cancelar(ctx, root)
    run_ponte(ctx, root)
    run_ponte_btm(ctx)
    run_construcao_antiga(ctx)
    run_unregister(ctx)


try:
    script()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")

print(f"blender_017_armario_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
os._exit(1 if FAILURES else 0)
