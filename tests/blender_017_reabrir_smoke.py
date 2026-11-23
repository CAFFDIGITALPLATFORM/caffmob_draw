"""Teste de fumaça da reabertura por arquivo da 017 (T040; RN-17, D-02, D-20, RF-20).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_017_reabrir_smoke.py

O armário v2 grava tudo o que a edição precisa em `Object.btm_armario` (D-02): medidas, montagem, divisões, gavetas,
portas, deslizante, fundo e o instantâneo do Cancelar. Esta fumaça prova que o estado **volta do arquivo**:

1. abrir num projeto limpo cria o armário e semeia o contrato de chapas;
2. montar três vãos com uma divisória e duas prateleiras, quatro gavetas e folha deslizante;
3. gerar e salvar em `tempdir` com `save_as_mainfile`;
4. reabrir com `open_mainfile` e conferir que `Object.btm_armario` devolve as mesmas medidas, montagem, divisões,
   gavetas, portas, deslizante e fundo, que o `snapshot` sobreviveu e que a coleção continua com as mesmas peças de
   papel gravado (e as mesmas peças de ferragem da corrediça).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.armario_v2 import build, gavetas as gavetas_mod, ops, vaos  # noqa: E402

FAILURES = []


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FAILURES.append(nome)


def raiz_v2():
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY' and any(colecao.name == build.COLECAO for colecao in obj.users_collection):
            return obj
    return None


def selecionar(obj):
    for outro in [item for item in bpy.context.view_layer.objects if item is not None]:
        outro.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def pecas(root):
    return [filho for filho in root.children if getattr(filho, 'btm_armario_parte', None) is not None]


def estado(root):
    """Retrato do armário: spec, coleções, estado de geração e as peças com papel e ferragem."""
    armario = root.btm_armario
    divisoes = [(item.uid, item.eixo, item.vao, round(item.posicao, 6), item.tipo, item.espessura)
                for item in armario.divisoes]
    gavetas = [(item.uid, item.vao, item.indice, round(item.altura, 6), item.modelo, item.separador_colunas,
                item.separador_linhas, item.afastador_frente, item.afastador_tras, item.corredica_3d)
               for item in armario.gavetas]
    internos = [(item.uid, item.vao, item.tipo, round(item.altura, 6)) for item in armario.internos]
    montagem = (
        armario.tipo_montagem, armario.orientacao_frente, armario.orientacao_tras,
        round(armario.largura, 6), round(armario.altura, 6), round(armario.profundidade, 6),
        armario.lateral_esq_ativa, armario.lateral_dir_ativa, armario.base_inf_ativa, armario.base_sup_ativa,
        armario.porta_ativa, armario.porta_folhas, armario.porta_dobradica,
        armario.deslizante_ativa, armario.deslizante_folhas, round(armario.deslizante_sobreposicao, 6),
        armario.deslizante_material, armario.deslizante_base, round(armario.trilho_profundidade, 6),
        armario.fundo_ativo, armario.fundo_fixacao, round(armario.fundo_recuo, 6),
        armario.acabamento, armario.bloquear_chapa, armario.gerado, armario.snapshot,
    )
    pecas_ = sorted((item.name, item.btm_armario_parte.papel, item.btm_armario_parte.ferragem)
                    for item in pecas(root))
    return montagem, divisoes, gavetas, internos, pecas_


def montar(root):
    """Três vãos com uma divisória e duas prateleiras, quatro gavetas e folha deslizante."""
    armario = root.btm_armario
    armario.lateral_esq_ativa = armario.lateral_dir_ativa = True
    armario.base_inf_ativa = armario.base_sup_ativa = True
    armario.fundo_ativo = True
    spec = ops.spec_do_armario(root)
    divisoes, _vertical = vaos.inserir_vertical([], spec, 's0', 'movel_s_recuo')
    divisoes, _prateleira = vaos.inserir_horizontal(divisoes, spec, 's0.b', 'prat_fixa')
    divisoes, _outra = vaos.inserir_horizontal(divisoes, spec, 's0.b', 'prat_fixa')
    ops.gravar_divisoes(armario, divisoes)
    for gaveta in gavetas_mod.bloco(700.0, 4, vao='s0'):
        item = armario.gavetas.add()
        item.uid, item.vao, item.indice = gaveta.uid, gaveta.vao, gaveta.indice
        item.altura, item.modelo = gaveta.altura, gaveta.modelo
        item.corredica_3d = True
    armario.deslizante_ativa = True
    return ops.spec_do_armario(root)


def roteiro():
    ctx = bpy.context
    env.clean_scene()
    for obj in [item for item in ctx.view_layer.objects if item is not None]:
        obj.select_set(False)
    ctx.view_layer.objects.active = None
    resultado = bpy.ops.caffmob.cabinet_editor()
    root = raiz_v2()
    check("Abrir cria o armário vazio", resultado == {'FINISHED'} and root is not None, str(resultado))
    selecionar(root)
    spec = montar(root)
    resultado = bpy.ops.caffmob.armario_v2_gerar()
    antes = estado(root)
    papeis = sorted({papel for _nome, papel, _ferragem in antes[4] if papel})
    ferragens = sorted({ferragem for _nome, _papel, ferragem in antes[4] if ferragem not in ('', 'NENHUMA')})
    check("Gerar monta os três vãos, as quatro gavetas e a deslizante",
          resultado == {'FINISHED'} and len(antes[2]) == 4 and len(antes[1]) == 3 and len(papeis) >= 5,
          f"{len(antes[1])} divisões, {len(antes[2])} gavetas, papéis {papeis}")
    check("a corrediça está na cena antes de salvar", ferragens == ['GAIOLA', 'TRILHO_EXT', 'TRILHO_INT'],
          str(ferragens))
    check("o spec montado é o que a cena mostra",
          spec.largura == 1000.0 and spec.deslizante_ativa and spec.fundo_ativo)

    nome = root.name
    with tempfile.TemporaryDirectory(prefix="caffmob_017_reabrir_") as pasta:
        caminho = os.path.join(pasta, "armario_v2.blend")
        bpy.ops.wm.save_as_mainfile(filepath=caminho, copy=True)
        check("o arquivo foi salvo", os.path.exists(caminho), caminho)
        bpy.ops.wm.open_mainfile(filepath=caminho)
        root = bpy.data.objects.get(nome)
        check("o armário volta na abertura do arquivo", root is not None, str(nome))
        if root is None:
            return
        depois = estado(root)
        check("medidas, montagem, divisões, gavetas, portas, deslizante e fundo voltam iguais",
              depois[0] == antes[0] and depois[1] == antes[1] and depois[2] == antes[2] and depois[3] == antes[3],
              "montagem/spec ou coleções diferentes")
        check("o instantâneo do Cancelar sobreviveu", bool(depois[0][-1]) and depois[0][-1] == antes[0][-1])
        check("a coleção continua com as mesmas peças de papel gravado",
              depois[4] == antes[4] and bool([item for item in depois[4] if item[1]]),
              f"{len(antes[4])} → {len(depois[4])} peça(s)")
        selecionar(root)
        bpy.ops.caffmob.armario_v2_aplicar()          # o ponto de retorno passa a ser o estado reaberto
        guardado = estado(root)
        root.btm_armario.largura = 1200.0
        resultado = bpy.ops.caffmob.armario_v2_gerar()
        check("o armário reaberto continua editável e gera",
              resultado == {'FINISHED'} and abs(ops.spec_do_armario(root).largura - 1200.0) < 1e-6,
              str(resultado))
        resultado = bpy.ops.caffmob.armario_v2_cancelar()
        depois = estado(root)
        check("Cancelar devolve o instantâneo fixado depois de reabrir",
              resultado == {'FINISHED'} and depois == guardado, str(resultado))


try:
    roteiro()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")

print(f"blender_017_reabrir_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
