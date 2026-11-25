"""Sonda do /reversa-debugger (2026-11-24) para a feature 021, em `--background`.

Responde com evidência executável, sem GUI, às perguntas de interface:
  (a) o Editor de Armário abre?
  (b) o botão global de colisão do viewport erra? (operador, strings e handler)
  (c) criar do zero, redimensionar sem perder/deformar peças e editar peça a peça?

    blender --background --factory-startup --python-exit-code 1 --python <este arquivo>
"""

import json
import sys
import traceback
from pathlib import Path

import bpy

AQUI = Path(__file__).resolve()
ROOT = AQUI.parents[4]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402  (registra o add-on)

from caffmob_draw.cabinet_editor import bridge, ops_editor  # noqa: E402
from caffmob_draw.data import i18n  # noqa: E402
from caffmob_draw.ui import header_collision  # noqa: E402

PASS, FAIL = [], []


def check(nome, ok, detalhe=""):
    (PASS if ok else FAIL).append(nome if ok else f"{nome} :: {detalhe}")
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)


def limpar():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def secao(nome, fn):
    try:
        fn()
    except Exception:
        check(nome, False, "exceção " + traceback.format_exc(limit=4))


CTX = bpy.context
SCENE = CTX.scene


# (a) Qual editor responde a `caffmob.cabinet_editor` ----------------------------------------
def editor_abre():
    limpar()
    rna = bpy.ops.caffmob.cabinet_editor.get_rna_type()
    check("editor: o idname é do construtor v2 (017 T027 aposentou o editor 2D)",
          rna.name == "Abrir armário v2", rna.name)
    check("editor: a classe do editor 2D está fora do registro",
          ops_editor.BTM_OT_CabinetEditor.is_registered is False,
          ops_editor.BTM_OT_CabinetEditor.is_registered)
    from caffmob_draw.armario_v2 import ops as v2ops
    check("editor: o Abrir do v2 está registrado", v2ops.BTM_OT_ArmarioV2Abrir.is_registered)
    resultado = bpy.ops.caffmob.cabinet_editor()
    root = CTX.view_layer.objects.active
    check("editor: abre num projeto limpo criando a raiz v2", "FINISHED" in resultado and root is not None,
          resultado)
    abas = tuple(ops_editor.props.TAB_ITEMS)
    check("editor 2D: sete abas existem no código (aposentadas)", len(abas) == 7, [a[0] for a in abas])


# (b) Botão global de colisão ----------------------------------------------------------------
def colisao():
    settings = SCENE.btm_settings
    settings.collision_global = True
    try:
        r = bpy.ops.caffmob.toggle_global_collision()
        erro = ""
    except Exception:
        r, erro = None, traceback.format_exc(limit=3)
    check("colisão: desliga sem erro", r == {"FINISHED"} and settings.collision_global is False, f"{r} {erro}")
    try:
        bpy.ops.caffmob.toggle_global_collision()
        erro = ""
    except Exception:
        erro = traceback.format_exc(limit=3)
    check("colisão: religa sem erro", settings.collision_global is True and not erro, erro)
    check("colisão: block_penetration acompanha", bool(getattr(settings, "block_penetration", True)) is True,
          getattr(settings, "block_penetration", None))
    chamadas = []

    class _Botao:
        def operator(self, idname, **kw):
            chamadas.append((idname, kw))

    class _Linha:
        def row(self, **_kw):
            return _Botao()

    class _Layout:
        def row(self, **_kw):
            return _Botao()

    try:
        header_collision.draw_header_collision(type("S", (), {"layout": _Layout()})(), CTX)
        erro_desenho = ""
    except Exception:
        erro_desenho = traceback.format_exc(limit=3)
    check("colisão: desenha no cabeçalho sem erro", not erro_desenho, erro_desenho)
    check("colisão: botão aponta para o operador",
          bool(chamadas) and chamadas[-1][0] == "caffmob.toggle_global_collision", chamadas[-1:])
    check("colisão: rótulo do estado atual",
          bool(chamadas) and chamadas[-1][1].get("text") == "Colisão: ON", chamadas[-1:])
    faltando = []
    for texto in ("Colisão: ON", "Colisão: OFF", "Colisões ativadas", "Colisões desativadas"):
        try:
            if not i18n.tr(texto):
                faltando.append(texto)
        except Exception as exc:
            faltando.append(f"{texto} ({exc!r})")
    check("colisão: rótulos traduzem em pt_BR", not faltando, faltando)


# (c1) Criar do zero -------------------------------------------------------------------------
NOVO = {}


def criar():
    limpar()
    r = bpy.ops.caffmob.cabinet_editor()          # Abrir do v2: cria a raiz num projeto limpo (RF-01 da 017)
    root = CTX.view_layer.objects.active
    check("criar: raiz v2 do zero em um passo", "FINISHED" in r and root is not None, r)
    if root is None:
        return
    bpy.ops.caffmob.armario_v2_montar_caixa()
    bpy.ops.caffmob.armario_v2_gerar()
    bpy.context.view_layer.update()
    pecas = bridge.parts(CTX, root)
    NOVO["root"] = root.name
    NOVO["pecas"] = len(pecas)
    check("criar: peças geradas", len(pecas) >= 5, [(p.kind, p.name) for p in pecas])
    colecao = root.users_collection[0].name if root.users_collection else None
    check("criar: raiz na camada Marcenaria", colecao == "Marcenaria", colecao)


# (c2) Redimensionar sem perder nem deformar -------------------------------------------------
def redimensionar():
    root = bpy.data.objects.get(NOVO.get("root", ""))
    if root is None:
        check("redimensionar: módulo disponível", False, "sem raiz")
        return
    antes = bridge.parts(CTX, root)
    largura = root.btm_armario.largura
    try:
        root.btm_armario.largura = largura + 200.0
        bpy.ops.caffmob.armario_v2_gerar()
        bpy.context.view_layer.update()
        erro = ""
    except Exception:
        erro = traceback.format_exc(limit=3)
    depois = bridge.parts(CTX, root)
    check("redimensionar: sem exceção", not erro, erro)
    check("redimensionar: mesmas peças", len(depois) == len(antes), f"{len(antes)} -> {len(depois)}")
    magras = [p.name for p in depois if abs(p.rect[2] - p.rect[0]) < 1e-6 or abs(p.rect[3] - p.rect[1]) < 1e-6]
    check("redimensionar: nenhuma peça achatada", not magras, magras[:3])
    check("redimensionar: largura aplicada", abs(root.btm_armario.largura - (largura + 200.0)) < 1e-4,
          f"{largura:.1f} -> {root.btm_armario.largura:.1f}")


# (c3) Editar cada categoria de peça dentro do construtor ------------------------------------
def editar_pecas():
    root = bpy.data.objects.get(NOVO.get("root", ""))
    if root is None:
        check("editar: módulo disponível", False, "sem raiz")
        return
    from caffmob_draw.armario_v2 import panel
    chaves = sorted(panel.ABAS)
    antes = len(bridge.parts(CTX, root))
    falhas = []
    roteiro = (
        ("estrutura", lambda: setattr(root.btm_armario, "espessura_lateral", "18")),
        ("divisão", lambda: bpy.ops.caffmob.armario_v2_inserir_divisoria()),
        ("prateleira", lambda: bpy.ops.caffmob.armario_v2_inserir_prateleira()),
        ("gavetas", lambda: (setattr(root.btm_armario, "bloco_quantidade", 2),
                             bpy.ops.caffmob.armario_v2_criar_bloco_gavetas())),
    )
    def selecionar():
        for o in CTX.view_layer.objects:
            o.select_set(o is root)
        CTX.view_layer.objects.active = root

    for nome, acao in roteiro:
        try:
            selecionar()
            acao()
            selecionar()
            bpy.ops.caffmob.armario_v2_gerar()
            bpy.context.view_layer.update()
        except Exception:
            falhas.append(nome + ": " + traceback.format_exc(limit=2))
    check("editar: cada aba edita sem exceção", not falhas, falhas[:2])
    depois = bridge.parts(CTX, root)
    check("editar: peças crescem com as edições", len(depois) > antes, f"{antes} -> {len(depois)}")
    check("editar: sete abas do mockup no construtor", len(chaves) == 7, sorted(chaves))


for nome, fn in (("a-editor", editor_abre), ("b-colisao", colisao), ("c1-criar", criar),
                 ("c2-redimensionar", redimensionar), ("c3-editar-pecas", editar_pecas)):
    secao(nome, fn)

print(json.dumps({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL, "novo": NOVO}, ensure_ascii=False))
