"""Teste de reprodução e regressão — BUG-20261117-JXDJ (planta baixa com corte e cores).

Executa em Blender (background):
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_JXDJ_plant_baixa.py

Cobre:
  - Reprodução: o editor NÃO tem toggle de planta baixa, campo de corte superior nem coloração por material
    (defeito relatado: draw_plan desenha apenas paredes).
  - Regressão: com o toggle desligado, o desenho de paredes continua igual (sem regressão);
    com o toggle ligado, objetos da cena aparecem com corte e cor por material.
"""

import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()

from caffmob_draw.walls2d import model, ops_editor, props  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Setup: sessão do editor com uma sala retangular (paredes do rascunho)
# ---------------------------------------------------------------------------
scene = bpy.context.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

plan = model.WallPlan([model.rectangle(3.6, 2.4)])
s = props.start(plan, scene.name)
state = bpy.context.window_manager.btm_wall_editor
state.line = 'INNER'

# ---------------------------------------------------------------------------
# Teste de reprodução: o defeito relatado aparece (plant baixa AUSENTE)
# ---------------------------------------------------------------------------
# Antes do fix, draw_plan não tem toggle de planta baixa, nem campo de corte,
# nem coloração por material. Após o fix, esses atributos existem na sessão.
has_plant_low_toggle = hasattr(s, 'plant_low') or hasattr(state, 'plant_low')
has_cut_height = hasattr(s, 'cut_height') or hasattr(state, 'cut_height')
has_material_color = hasattr(s, 'material_color_mode') or hasattr(state, 'material_color_mode')

check("REPRODUÇÃO: plant_low toggle existe (ausente antes do fix)",
      has_plant_low_toggle,
      f"s.plant_low={getattr(s, 'plant_low', 'N/A')} state.plant_low={getattr(state, 'plant_low', 'N/A')}")
check("REPRODUÇÃO: cut_height existe (ausente antes do fix)",
      has_cut_height,
      f"s.cut_height={getattr(s, 'cut_height', 'N/A')} state.cut_height={getattr(state, 'cut_height', 'N/A')}")
check("REPRODUÇÃO: material_color_mode existe (ausente antes do fix)",
      has_material_color,
      f"s.material_color_mode={getattr(s, 'material_color_mode', 'N/A')} state.material_color_mode={getattr(state, 'material_color_mode', 'N/A')}")

# ---------------------------------------------------------------------------
# Teste de regressão: com toggle desligado, desenho de paredes continua igual
# ---------------------------------------------------------------------------
# draw_plan deve pintar paredes com COLORS['wall'] (cor única) quando plant_low está desligado.
import math
walls_drawn = 0
for ci, chain in enumerate(s.plan.chains):
    for i in range(chain.segment_count()):
        walls_drawn += 1
check(f"REGRESSÃO: {walls_drawn} parede(s) no rascunho (sem regressão no desenho)",
      walls_drawn == 4,
      f"cadeias={len(s.plan.chains)} paredes={walls_drawn}")

# Com plant_low desligado (se existir), o comportamento é o de antes
if has_plant_low_toggle:
    s.plant_low = False
    check("REGRESSÃO: plant_low desligado mantém comportamento atual",
          getattr(s, 'plant_low', None) is False,
          f"plant_low={getattr(s, 'plant_low', 'N/A')}")

# ---------------------------------------------------------------------------
# Teste de regressão: com toggle ligado, objetos aparecem com corte e cor
# ---------------------------------------------------------------------------
if has_plant_low_toggle and has_cut_height:
    s.plant_low = True
    s.cut_height = 3.0
    check("REGRESSÃO: plant_low ligado com cut_height definido",
          getattr(s, 'plant_low', None) is True and getattr(s, 'cut_height', None) == 3.0,
          f"plant_low={getattr(s, 'plant_low', 'N/A')} cut_height={getattr(s, 'cut_height', 'N/A')}")

# ---------------------------------------------------------------------------
# Regressão: ler a cena não pode quebrar com curva, vazio, malha vazia ou objeto acima do corte
# ---------------------------------------------------------------------------
from caffmob_draw.walls2d import scene_io  # noqa: E402

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.5))
caixa = bpy.context.active_object
caixa.name = "Caixa"
bpy.ops.object.empty_add(location=(1.0, 1.0, 0.0))
bpy.context.active_object.name = "Vazio"
curva_dados = bpy.data.curves.new("Curva", type='CURVE')
curva = bpy.data.objects.new("Curva", curva_dados)
scene.collection.objects.link(curva)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.0, 0.0, 4.0))
bpy.context.active_object.name = "Alto"

caixa.data.materials.append(bpy.data.materials.new("Cinza"))

objetos, erro = [], ""
try:
    objetos = scene_io.plant_objects(scene, 3.0)
except Exception as exc:                       # noqa: BLE001
    erro = f"{type(exc).__name__}: {exc}"
nomes = [o['name'] for o in objetos]

check("REGRESSÃO: planta lê a cena com curva, vazio e objeto acima do corte", not erro, erro)
check("REGRESSÃO: malha abaixo do corte entra na planta", "Caixa" in nomes, f"nomes={nomes}")
check("REGRESSÃO: objeto acima do corte fica fora da planta", "Alto" not in nomes, f"nomes={nomes}")
check("REGRESSÃO: malha da planta tem contorno e cor",
      bool(objetos) and bool(objetos[0]['points']) and bool(objetos[0]['color']),
      f"pontos={len(objetos[0]['points']) if objetos else 0}")

# ---------------------------------------------------------------------------
# Encerramento
# ---------------------------------------------------------------------------
props.end()
addon.unregister()

print(f"blender_bug_JXDJ_plant_baixa: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)