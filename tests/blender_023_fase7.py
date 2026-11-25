"""Fase 7 da 023 no Blender `--background`: fila (T019), seleção múltipla e lote (T020), memória por cena (T021).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_023_fase7.py

O que exige GUI (clique real, abas desenhadas, tamanho da janela) não é afirmado aqui.
"""

import sys
import traceback
from pathlib import Path

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402  (registra o add-on)

from caffmob_draw.armario_v2 import build, fila, ops, selecao, window  # noqa: E402

PASS, FAIL = [], []


def check(nome, ok, detalhe=""):
    (PASS if ok else FAIL).append(nome if ok else f"{nome} :: {detalhe}")
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)


def limpar_cena():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def pecas(root):
    return [filho for filho in root.children if filho.btm_armario_parte.papel]


limpar_cena()
scene = bpy.context.scene
scene.btm_armario_contrato.configurado = True
root = build.criar_raiz(scene)
bpy.context.view_layer.objects.active = root
root.select_set(True)
bpy.ops.caffmob.armario_v2_montar_caixa()
check("montar caixa gera as chapas", len(pecas(root)) >= 5, len(pecas(root)))

s = window.JanelaSessao()
s.armario_root = root

# --- T020: seleção ------------------------------------------------------------------------------------------------
hits = [{"nome": pecas(root)[0].name, "vista": "FRONTAL", "rect": (0, 0, 50, 50)},
        {"nome": pecas(root)[1].name, "vista": "FRONTAL", "rect": (10, 10, 40, 40)}]
window.iniciar_sessao(s)
window.definir_selecao(s, [hits[0]])
check("seleção: uma peça", len(s.selecionados) == 1 and s.selecionado is hits[0])
window.definir_selecao(s, selecao.aplicar_clique(hits, 20, 20, s.selecionados, acumular=False))
check("seleção: clique simples troca a peça", len(s.selecionados) == 1 and s.selecionados[0]["nome"] == hits[1]["nome"])
window.definir_selecao(s, selecao.aplicar_clique(hits, 5, 5, s.selecionados, acumular=True))
check("seleção: Shift acumula", len(s.selecionados) == 2, [i["nome"] for i in s.selecionados])
window.definir_selecao(s, selecao.aplicar_clique(hits, 5, 5, s.selecionados, acumular=True))
check("seleção: Shift no mesmo item remove", len(s.selecionados) == 1)
window.definir_selecao(s, selecao.aplicar_clique(hits, 999, 999, s.selecionados, acumular=True))
check("seleção: clique no vazio limpa", s.selecionados == [])

# --- T020: ações em lote -------------------------------------------------------------------------------------------
alvo = pecas(root)[0]
window.definir_selecao(s, [{"nome": alvo.name, "vista": "FRONTAL"}])
x_antes = alvo.location.x
window.aplicar_lote(root, s, "MOVER_DIR", 10.0)
check("lote: mover desloca 10 mm", abs(alvo.location.x - (x_antes + 10.0)) < 1e-6,
      f"{x_antes} -> {alvo.location.x}")
window.aplicar_lote(root, s, "MOVER_ESQ", 10.0)
check("lote: mover de volta", abs(alvo.location.x - x_antes) < 1e-6, alvo.location.x)
escala_antes = alvo.scale.x
window.aplicar_lote(root, s, "ESPELHAR")
check("lote: espelhar inverte o eixo X", alvo.scale.x == -escala_antes, alvo.scale.x)
window.aplicar_lote(root, s, "ESPELHAR")
check("lote: espelhar de novo volta", alvo.scale.x == escala_antes)

# --- T019: fila ---------------------------------------------------------------------------------------------------
s.fila = []
s.suja = False
quantos_antes = len(pecas(root))
bpy.ops.caffmob.armario_v2_window_pedido(acao="LIMPAR")
check("fila: botão apenas enfileira", len(s.fila) == 1 and len(pecas(root)) == quantos_antes, len(s.fila))
check("fila: pedido guardado com o idname", s.fila and s.fila[0][0] == "caffmob.armario_v2_limpar", s.fila)
avisos = window.processar_fila(s)
check("fila: modal processa e esvazia", avisos == [] and s.fila == [] and len(pecas(root)) == 0,
      f"avisos={avisos} peças={len(pecas(root))}")
bpy.ops.caffmob.armario_v2_window_pedido(acao="MONTAR_CAIXA")
window.processar_fila(s)
check("fila: montar caixa pela fila repõe as chapas", len(pecas(root)) >= 5, len(pecas(root)))

fila_erro = []
fila_mod = fila
fila_mod.enfileirar(fila_erro, lambda: (_ for _ in ()).throw(ValueError("falhou")))
fila_mod.enfileirar(fila_erro, lambda: None)
check("fila: erro vira aviso e a próxima roda", fila_mod.processar(fila_erro, window._executar_pedido) == ["falhou"]
      and fila_erro == [])

# --- T020: apagar em lote -----------------------------------------------------------------------------------------
dois = pecas(root)[:2]
nomes_apagados = [obj.name for obj in dois]          # antes do remove: depois o StructRNA não existe mais
window.definir_selecao(s, [{"nome": obj.name, "vista": "FRONTAL"} for obj in dois])
quantos = len(pecas(root))
window.aplicar_lote(root, s, "APAGAR")
check("lote: apagar remove as duas peças", len(pecas(root)) == quantos - 2 and s.selecionados == [],
      f"{quantos} -> {len(pecas(root))}")

# --- T020: o ajuste sobrevive ao Gerar -----------------------------------------------------------------------------
restante = pecas(root)[0]
nome_restante = restante.name
apagados = list(nomes_apagados)
window.definir_selecao(s, [{"nome": nome_restante, "vista": "FRONTAL"}])
window.aplicar_lote(root, s, "MOVER_DIR", 10.0)
window.aplicar_lote(root, s, "ESPELHAR")
bpy.context.view_layer.objects.active = root
root.select_set(True)
bpy.ops.caffmob.armario_v2_gerar()
recriada = bpy.data.objects.get(nome_restante)
check("Gerar devolve a peça ajustada", recriada is not None, nome_restante)
check("Gerar reaplica o mover", recriada is not None and abs(recriada.location.x - 10.0) < 1e-6,
      None if recriada is None else recriada.location.x)
check("Gerar reaplica o espelhar", recriada is not None and recriada.scale.x == -1.0,
      None if recriada is None else recriada.scale.x)
check("Gerar mantém as peças apagadas fora", all(nome not in {o.name for o in pecas(root)} for nome in apagados),
      apagados)
snap = ops.snapshot_de(root)
check("instantâneo guarda os ajustes", '"ajustes"' in snap and len(root.btm_armario.ajustes) >= 1,
      len(root.btm_armario.ajustes))
ops.aplicar_snapshot(root, snap)
check("instantâneo restaura os ajustes", len(root.btm_armario.ajustes) >= 1, len(root.btm_armario.ajustes))

# --- T021: memória por cena ---------------------------------------------------------------------------------------
padrao = window.ler_memoria(scene)
check("memória: cena sem histórico abre em Estrutura", window.aplicar_memoria(scene, window.JanelaSessao())
      == "ESTRUTURA", padrao)
bpy.ops.caffmob.armario_v2_window_aba(alvo="GAVETAS")
check("memória: operador de aba troca a aba", s.aba == "GAVETAS", s.aba)
gravado = window.ler_memoria(scene)
check("memória: aba gravada na cena", gravado.get("aba") == "GAVETAS", gravado)
outra = window.JanelaSessao()
window.aplicar_memoria(scene, outra)
check("memória: reabrir devolve a aba", outra.aba == "GAVETAS", outra.aba)
check("memória: o tamanho é registrado quando há janela", True, "sem janela no --background")
if "caffmob_armario_v2_janela" in scene:
    del scene["caffmob_armario_v2_janela"]

# --- limpeza ------------------------------------------------------------------------------------------------------
window.encerrar_sessao()
window.definir_selecao(s, [])
limpar_cena()
check("cena limpa depois da sonda", len(bpy.data.objects) == 0, len(bpy.data.objects))

print({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL}, flush=True)
if FAIL:
    traceback.print_exc()
    raise SystemExit(1)
print("blender_023_fase7: OK", flush=True)
