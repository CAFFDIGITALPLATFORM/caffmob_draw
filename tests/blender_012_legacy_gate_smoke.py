"""Fumaça da porta das bibliotecas herdadas (feature 012, T056; RF-13, RN-12; D-01 a D-05, D-28).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_legacy_gate_smoke.py

Sem a extensão instalada, a preferência `show_legacy_libraries` não existe: a porta fica fechada, como no padrão.
Um layout falso registra o que cada desenho tenta mostrar.
- Porta fechada: Inserir sem seletor nem galerias herdadas; Meus módulos só com os módulos salvos; HUD sem os modos
  herdados e com Mover Sobre, Seleção por componente e Abrir portas; menu de contexto sem o submenu do armário
  herdado; Desenhos 2D sem a biblioteca de molduras; seleção por componente sem modos; `product_tab` neutro.
- Porta aberta (preferência simulada): tudo volta.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils, legacy  # noqa: E402
from caffmob_draw.legacy import gate  # noqa: E402
from caffmob_draw.operators import viewport_hud as hud  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import component_select  # noqa: E402
from caffmob_draw.ui import context_menu, my_modules, sidebar_insert, sidebar_project  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


class Recorder:
    """Layout falso: aceita qualquer chamada e registra props, operadores e menus pedidos."""

    def __init__(self, log=None):
        self.log = log if log is not None else []

    def __getattr__(self, name):
        if name == 'recorder':
            return None
        if name == 'panel_prop':
            return lambda *a, **k: (Recorder(self.log), Recorder(self.log))

        def call(*args, **kwargs):
            if name in ('prop', 'operator', 'menu', 'prop_enum', 'operator_menu_enum', 'template_list'):
                self.log.append((name,) + tuple(a for a in args if isinstance(a, str)))
            return Recorder(self.log)
        return call

    def __setattr__(self, name, value):
        if name == 'log':
            object.__setattr__(self, name, value)

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


def drawn(fn, *args):
    rec = Recorder()
    fn(rec, *args)
    return rec.log


def main():
    env.clean_scene()
    cab = tf.BaseCabinet()
    cab.create("Antigo")
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    ctx.view_layer.objects.active = cab.obj
    original_gate = gate.legacy_ui

    for opened in (False, True):
        gate.legacy_ui = (lambda context=None: True) if opened else original_gate
        tag = "aberta" if opened else "fechada"
        check(f"porta {tag}", gate.legacy_ui(ctx) is opened)
        log = drawn(sidebar_insert.draw, ctx)
        has_tab = any(entry[:2] == ('prop', 'product_tab') for entry in log)
        check(f"Inserir com a porta {tag}: seletor herdado {'aparece' if opened else 'some'}", has_tab is opened,
              str([e for e in log if e[0] == 'prop'][:4]))
        log = drawn(my_modules.draw, ctx)
        check(f"Meus módulos com a porta {tag}", any(e[:2] == ('prop', 'my_modules_filter') for e in log) is opened)
        modes = any(button.visible(ctx) for button in hud._MODE_BUTTONS)
        check(f"HUD com a porta {tag}: modos herdados {'aparecem' if opened else 'somem'}", modes is opened)
        general = [hud._MOVE_OVER_BUTTON.visible(ctx), hud._COMPONENT_SELECT_BUTTON.visible(ctx),
                   hud._OPEN_DOOR_BUTTON.visible(ctx) if not opened else True]   # aberta: regra herdada (Parts)
        check(f"HUD com a porta {tag}: botões gerais continuam", all(general), str(general))
        check(f"menu de contexto do herdado com a porta {tag}",
              context_menu._legacy_menu_hidden(ctx, cab.obj) is (not opened))
        check(f"seleção por componente com a porta {tag}", (component_select.cabinet_modes(ctx.scene) == {})
              is (not opened))
    gate.legacy_ui = original_gate

    check("molduras fora dos Desenhos 2D", 'HOME_BUILDER_PT_molding_library' in sidebar_project.LEGACY_CHILDREN)
    ctx.scene.home_builder.product_tab = 'FACE FRAME'
    ctx.scene.hb_frameless.frameless_selection_mode = 'Parts'
    check("product_tab e modos de seleção voltam aos valores de fábrica", legacy.neutralize_product_tab(ctx)
          and ctx.scene.home_builder.product_tab == 'FRAMELESS'
          and ctx.scene.hb_frameless.frameless_selection_mode == 'Cabinets')
    check("raiz herdada detectada", gate.legacy_roots(ctx.scene) == [cab.obj])


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_012_legacy_gate_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
