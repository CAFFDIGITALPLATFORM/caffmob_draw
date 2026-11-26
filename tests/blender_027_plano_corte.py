"""Janela própria do plano de corte (027, T009; RF-01).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_027_plano_corte.py

- o núcleo (`cutting/plan_window_core.py`) achata as faixas do otimizador em retângulos absolutos, enquadra a chapa,
  responde o hit test e conta o aproveitamento;
- a janela (`cutting/plan_window.py`) está registrada: operador `caffmob.cut_plan_window`, painéis da categoria
  "Plano de Corte" e um único handler de desenho;
- sem peças na cena o operador recusa abrir (CANCELLED), sem quebrar;
- `unregister()` devolve a cena ao estado anterior (nenhum handler sobrando).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.cutting import plan_window, plan_window_core as core  # noqa: E402
from caffmob_draw.cutting.nesting import NestingPart, optimize_nesting  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(name)


def _payload():
    parts = [
        NestingPart("p1", "Lateral", 600.0, 800.0, material="MDF Branco", thickness=18.0, module_ref="Armário A"),
        NestingPart("p2", "Prateleira", 300.0, 500.0, material="MDF Branco", thickness=18.0, module_ref="Armário A"),
        NestingPart("p3", "Fundo", 600.0, 2000.0, material="MDF Branco", thickness=18.0, module_ref="Armário B"),
    ]
    return optimize_nesting(parts, sheet_width=2750.0, sheet_height=1830.0, refilo_top=10.0, refilo_bottom=10.0,
                            refilo_left=10.0, refilo_right=10.0, kerf=4.0)


def main():
    payload = _payload()
    sheets = core.sheets_of(payload)
    check("o otimizador devolve uma chapa", len(sheets) == 1, str(len(sheets)))
    sheet = sheets[0] if sheets else {}
    placed = core.placed(sheet)
    check("as três peças viram retângulos", len(placed) == 3, str(len(placed)))
    check("retângulo com medidas", all(p['width'] > 0 and p['height'] > 0 for p in placed), str(placed[:1]))
    check("peça guarda nome e módulo", all(p['name'] and p['module'] for p in placed))
    check("chapa em milímetros", core.bounds(sheet) == ((0.0, 0.0), (2750.0, 1830.0)), str(core.bounds(sheet)))
    dentro = all(0.0 <= p['x'] and p['x'] + p['width'] <= 2750.0 and 0.0 <= p['y'] and p['y'] + p['height'] <= 1830.0
                 for p in placed)
    check("peça inteira dentro da chapa", dentro, str([(p['x'], p['y']) for p in placed]))

    alvo = placed[0]
    centro = (alvo['x'] + alvo['width'] / 2.0, alvo['y'] + alvo['height'] / 2.0)
    check("hit test acha a peça pelo centro", core.part_at(placed, *centro) is alvo)
    canto = (2750.0 - 1.0, 1830.0 - 1.0)
    check("canto da chapa respeita o refilo", core.part_at(placed, *canto) is None, str(core.part_at(placed, *canto)))

    aproveitamento = core.utilization(sheet)
    check("aproveitamento entre 0 e 100", 0.0 < aproveitamento <= 100.0, str(aproveitamento))
    resumo = core.summary(sheet)
    check("resumo conta as peças", resumo['parts'] == 3, str(resumo))
    check("resumo traz a área em m²", resumo['used_area_m2'] > 0.0, str(resumo['used_area_m2']))
    check("título da chapa", "Chapa 1/1" in core.sheet_title(sheet, 0, 1), core.sheet_title(sheet, 0, 1))
    check("medida da peça em mm", core.part_size_label(alvo).endswith("mm"), core.part_size_label(alvo))
    check("peça com módulo no título", "›" in core.part_title(alvo), core.part_title(alvo))

    # A janela em si precisa de uma janela do Blender; aqui se confere o registro e a sessão.
    s = plan_window.Sessao(payload)
    check("sessão com as chapas do cache", len(s.sheets) == 1 and s.sheet() is not None)
    check("sessão começa na primeira chapa", s.index == 0)
    check("sessão sem seleção", s.selected is None and s.hover is None)
    check("desenho sem área não quebra", plan_window.draw_plan(bpy.context) is None)

    check("operador da janela registrado", hasattr(bpy.types, "CAFFMOB_OT_cut_plan_window"))
    check("handler de desenho registrado", bool(plan_window._draw_handle))
    classes = [c for c in plan_window.classes if issubclass(c, bpy.types.Panel)]
    check("painéis da janela na categoria do plano",
          all(c.bl_category == plan_window.CATEGORIA and c.bl_space_type == 'IMAGE_EDITOR' for c in classes),
          str([(c.__name__, c.bl_category) for c in classes]))

    try:
        resultado = bpy.ops.caffmob.cut_plan_window()
    except RuntimeError as exc:                 # `self.report({'ERROR'})` vira exceção fora da interface
        resultado = {'CANCELLED'} if "marcenaria" in str(exc) else str(exc)
    check("sem peças o operador recusa abrir", resultado == {'CANCELLED'}, str(resultado))
    check("reload sem janela aberta não cria sessão", plan_window.reload(bpy.context) is None)
    check("fechar sem janela aberta não quebra", plan_window.close(bpy.context) is None)
    plan_window.go_to(3)
    check("navegar sem sessão não quebra", plan_window.sessao() is None)

    # Registro simétrico: nada de handler sobrando quando o add-on sai.
    plan_window.unregister()
    check("unregister remove o handler de desenho", not plan_window._draw_handle)
    check("unregister remove os painéis", not hasattr(bpy.types, "BTM_PT_CutPlanHeader"))
    plan_window.register()
    check("register devolve o handler", bool(plan_window._draw_handle))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"blender_027_plano_corte: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    sys.exit(1 if FAILURES else 0)
