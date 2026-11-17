"""Reprodução e regressão do BUG-20261117-EELF: ferramenta Mover no Editor de Paredes.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_EELF_move.py

1. Reprodução: a ferramenta MOVE existe no enum do painel (hoje não existe);
2. Reprodução: mover desloca as paredes ativas e um passo de desfazer devolve o rascunho;
3. Regressão: arrastar vértice continua mudando só o vértice (o caminho de hoje não pode mudar);
4. Regressão: mover não altera espessura, altura nem tipo de parede.
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.walls2d import model, props  # noqa: E402

ctx = bpy.context
state = ctx.window_manager.btm_wall_editor

# 1. Reprodução: a ferramenta Mover existe no painel do editor.
ids = [item.identifier for item in state.bl_rna.properties["tool"].enum_items]
assert "MOVE" in ids, "ferramentas do editor hoje: {}".format(ids)
state.tool = "MOVE"
assert state.tool == "MOVE"

# 2. Reprodução: mover desloca as paredes ativas, sem mudar o comprimento delas.
s = props.start(model.WallPlan([model.rectangle(3.6, 2.4, thickness=0.15)]), ctx.scene.name)
chain = s.plan.chains[0]
x0_antes, y0_antes = chain.nodes[0]
x1_antes, y1_antes = chain.nodes[1]
comprimento = chain.length(0)
s.plan.move_segments([(0, 0)], 0.5, 0.0)
assert abs(chain.nodes[0][0] - (x0_antes + 0.5)) < 1e-9, chain.nodes
assert abs(chain.nodes[1][0] - (x1_antes + 0.5)) < 1e-9, chain.nodes
assert abs(chain.nodes[0][1] - y0_antes) < 1e-9 and abs(chain.nodes[1][1] - y1_antes) < 1e-9
assert abs(chain.length(0) - comprimento) < 1e-9, chain.length(0)

# 2b. Um movimento é um passo de desfazer.
s.checkpoint()
assert s.undo(), "o movimento não entrou no desfazer"
assert abs(s.plan.chains[0].nodes[0][0] - x0_antes) < 1e-9, s.plan.chains[0].nodes

# 3. Regressão: arrastar vértice continua mudando só o vértice (caminho antigo).
chain = s.plan.chains[0]
comprimento_vizinho = chain.length(1)
x, y = chain.nodes[1]
chain.move_node(1, (x, y + 0.3))
assert abs(chain.length(1) - comprimento_vizinho) > 1e-6, chain.length(1)
assert abs(chain.nodes[0][1] - y0_antes) < 1e-9              # o outro nó não andou

# 4. Regressão: mover não altera espessura, altura nem tipo.
chain.set_segment_value(1, "thickness", 0.2)
chain.set_segment_value(1, "wall_type", "MURETA")
espessura, altura, tipo = chain.segments[1].thickness, chain.segments[1].height, chain.segments[1].wall_type
s.plan.move_segments([(0, 1)], 0.0, 0.25)
assert abs(chain.segments[1].thickness - espessura) < 1e-9
assert abs(chain.segments[1].height - altura) < 1e-9
assert chain.segments[1].wall_type == tipo

props.end()
print("blender_bug_EELF_move: OK")
