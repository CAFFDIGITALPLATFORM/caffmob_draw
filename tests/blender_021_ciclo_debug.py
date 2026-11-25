"""Evidência do ciclo /reversa-debugger da 021, no Blender `--background`.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_021_ciclo_debug.py

Cobre o que é comportamental e verificável sem GPU:
- botão global de colisão: o operador executa sem exceção e alterna as duas chaves; o desenho do cabeçalho emite
  o botão com o rótulo do estado;
- armário do zero: montar a caixa cria as cinco chapas e o Gerar repete o resultado;
- redimensionar: largura nova, mesmo número de peças, caixa coerente e nenhuma peça degenerada;
- editar cada peça do armário pelo lote (mover 10 mm e voltar), peça por peça;
- janela do editor: o operador de abrir é chamado no `--background` e o resultado é registrado (sem janela, ele não
  pode duplicar área; isso é o que só uma sessão gráfica prova).

O que NÃO é afirmado aqui: aparência igual ao mockup, clique real, toque longo, desenho dos painéis e o modal.
"""

import sys
from pathlib import Path

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402

from caffmob_draw.armario_v2 import build, panel_window, window  # noqa: E402
from caffmob_draw.ui import header_collision  # noqa: E402

PASS, FAIL = [], []


def check(nome, ok, detalhe=""):
    (PASS if ok else FAIL).append(nome if ok else f"{nome} :: {detalhe}")
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)


def limpar_cena():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def pecas(root):
    return [filho for filho in root.children if filho.btm_armario_parte.papel]


def caixa_da_peca(obj):
    """(min, max) do mundo, sem depender de bpy.context.view_layer."""
    pontos = [obj.matrix_world @ v.co for v in obj.data.vertices] if obj.type == 'MESH' else []
    if not pontos:
        return None
    return ([min(p[i] for p in pontos) for i in range(3)],
            [max(p[i] for p in pontos) for i in range(3)])


class _LayoutFalso:
    def __init__(self):
        self.itens = []

    def row(self, **_kw):
        return self

    def operator(self, idname, **kw):
        self.itens.append((idname, kw.get('text', '')))


def main():
    limpar_cena()
    contexto = bpy.context
    cena = contexto.scene

    # --- (b) botão global de colisão -----------------------------------------------------------------------------
    settings = cena.btm_settings
    settings.collision_global = True
    settings.block_penetration = True
    try:
        resultado = bpy.ops.caffmob.toggle_global_collision()
        erro = None
    except Exception as exc:                     # noqa: BLE001 - a evidência é o texto do erro, se houver
        resultado, erro = None, f"{type(exc).__name__}: {exc}"
    check("colisão: operador do cabeçalho executa sem erro", erro is None, erro)
    check("colisão: desliga as duas chaves",
          not settings.collision_global and not settings.block_penetration,
          (settings.collision_global, settings.block_penetration))
    bpy.ops.caffmob.toggle_global_collision()
    check("colisão: religa as duas chaves",
          settings.collision_global and settings.block_penetration,
          (settings.collision_global, settings.block_penetration))

    layout = _LayoutFalso()
    header_collision.draw_header_collision(type("S", (), {"layout": layout})(), contexto)
    check("colisão: cabeçalho emite o botão com o estado",
          layout.itens and layout.itens[0][0] == "caffmob.toggle_global_collision"
          and "ON" in layout.itens[0][1], layout.itens)

    # --- (c1) armário do zero -------------------------------------------------------------------------------------
    cena.btm_armario_contrato.configurado = True
    root = build.criar_raiz(cena)
    contexto.view_layer.objects.active = root
    root.select_set(True)
    bpy.ops.caffmob.armario_v2_montar_caixa()
    quantas = len(pecas(root))
    check("armário do zero: montar caixa cria as cinco chapas", quantas == 5, quantas)
    bpy.ops.caffmob.armario_v2_gerar()
    check("armário do zero: Gerar repete o resultado", len(pecas(root)) == quantas, len(pecas(root)))

    # --- (c2) redimensionar sem deformar -------------------------------------------------------------------------
    armario = root.btm_armario
    antes = len(pecas(root))
    armario.largura = 900.0
    contexto.view_layer.objects.active = root
    root.select_set(True)
    bpy.ops.caffmob.armario_v2_gerar()
    depois = pecas(root)
    caixas = [caixa_da_peca(obj) for obj in depois]
    largura_total = max(c[1][0] for c in caixas) - min(c[0][0] for c in caixas)
    degeneradas = [obj.name for obj, c in zip(depois, caixas)
                   if min(c[1][i] - c[0][i] for i in range(3)) < 1e-4]
    check("redimensionar: mesmo número de peças", len(depois) == antes, (antes, len(depois)))
    check("redimensionar: largura acompanha o módulo", 0.85 <= largura_total <= 0.95, largura_total)  # metros
    check("redimensionar: nenhuma peça degenerada", not degeneradas, degeneradas)

    # --- (c3) editar cada peça pelo lote -------------------------------------------------------------------------
    s = window.JanelaSessao()
    s.armario_root = root
    window.iniciar_sessao(s)
    sem_edicao = []
    for obj in pecas(root):
        base = obj.location.x
        window.definir_selecao(s, [{"nome": obj.name, "vista": "FRONTAL"}])
        window.aplicar_lote(root, s, "MOVER_DIR", 10.0)
        deslocou = abs(obj.location.x - (base + 10.0)) < 1e-6
        window.aplicar_lote(root, s, "MOVER_ESQ", 10.0)
        if not deslocou or abs(obj.location.x + base) > 1e-6:
            sem_edicao.append(obj.name)
    check("editar cada peça: o lote move e devolve todas", not sem_edicao, sem_edicao)

    # --- (c4) as sete abas do editor existem e estão registradas -------------------------------------------------
    registradas = [cls for cls, _rotulo, _icone in
                   [(panel_window.BTM_PT_ArmarioV2WindowEstrutura, 1, 1)] if cls.is_registered]
    paineis = [getattr(panel_window, nome) for nome in dir(panel_window)
               if nome.startswith("BTM_PT_ArmarioV2Window")]
    check("editor: as sete abas têm painel registrado",
          len(panel_window.ABAS) == 7 and len(paineis) >= 7
          and all(cls.is_registered for cls in paineis) and registradas, len(paineis))

    # --- (a) abrir a janela: o que o `--background` consegue dizer ------------------------------------------------
    try:
        resultado_janela = bpy.ops.caffmob.armario_v2_window_open('EXEC_DEFAULT')
        erro_janela = None
    except Exception as exc:                     # noqa: BLE001
        resultado_janela, erro_janela = None, f"{type(exc).__name__}: {exc}"
    # Sem janela, o `poll` recusa por contexto: é a fronteira do `--background`, não um defeito do operador.
    check("janela: no --background o operador recusa por contexto (esperado)",
          resultado_janela is None and erro_janela is not None
          and ("poll" in erro_janela or "context" in erro_janela),
          (resultado_janela, erro_janela))

    print({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL}, flush=True)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
