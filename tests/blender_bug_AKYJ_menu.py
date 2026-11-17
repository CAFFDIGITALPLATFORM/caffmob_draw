"""Reprodução e regressão do BUG-20261117-AKYJ: ações da caixa de contexto no editor de paredes.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_AKYJ_menu.py

1. Reprodução: inverter o sentido de todas as paredes ativas existe e é um passo de desfazer;
2. Reprodução: a Direção (lado da espessura) alcança as paredes ativas, não só o trecho selecionado;
3. Reprodução: cada tipo de parede tem cor própria e o NORMAL mantém o cinza atual do editor;
4. Regressão: no modo Desenhar o botão direito continua encerrando o lápis (não abre caixa);
5. Regressão: a ferramenta Inverter Sentido por clique continua invertendo uma parede só.
"""

import inspect
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.walls2d import cores, menu_contexto as mc, model, ops_editor, props  # noqa: E402

ctx = bpy.context

# 0. A caixa existe como capacidade (hoje não existe).
assert hasattr(props, 'inverter_ativas'), "props sem inverter_ativas"
assert hasattr(props, 'aplicar_direcao'), "props sem aplicar_direcao"

# 1. Reprodução: inverter atinge todas as paredes ativas e um único desfazer devolve.
s = props.start(model.WallPlan([model.rectangle(3.6, 2.4, thickness=0.15),
                                model.Chain([(5.0, 0.0), (8.0, 0.0)], [model.Segment()])]), ctx.scene.name)
s.multi = [(0, 0), (1, 0)]
s.selected = (1, 0)
lados_antes = [chain.side for chain in s.plan.chains]
nos_antes = [list(chain.nodes) for chain in s.plan.chains]
assert props.inverter_ativas(s) is True, "nada foi invertido"
for antes, chain in zip(lados_antes, s.plan.chains):
    assert chain.side != antes, (antes, chain.side)
assert [list(c.nodes) for c in s.plan.chains] != nos_antes, "os nós não mudaram de ordem"
assert s.undo(), "inverter não entrou no desfazer"
assert [c.side for c in s.plan.chains] == lados_antes, [c.side for c in s.plan.chains]
assert [list(c.nodes) for c in s.plan.chains] == nos_antes

# 2. Reprodução: a Direção em lote aplica em todas as ativas, com um passo de desfazer.
s.multi = [(0, 0), (1, 0)]
s.selected = (0, 0)
lados_antes = [c.side for c in s.plan.chains]
assert props.aplicar_direcao(s, 'RIGHT') is True, "a direção não foi aplicada"
assert [c.side for c in s.plan.chains] == ['RIGHT', 'RIGHT'], [c.side for c in s.plan.chains]
assert s.undo(), "a direção não entrou no desfazer"
assert [c.side for c in s.plan.chains] == lados_antes, [c.side for c in s.plan.chains]

# 3. Reprodução: cor por tipo, com o NORMAL no cinza atual do editor.
assert cores.cor('NORMAL') == ops_editor.COLORS['wall'], cores.cor('NORMAL')
assert len({cores.cor(t) for t in model.WALL_TYPES}) == 3, [cores.cor(t) for t in model.WALL_TYPES]

# 4. Regressão: o modo Desenhar continua encerrando o lápis com o botão direito.
fonte = inspect.getsource(ops_editor.BTM_OT_WallEditorModal._handle_draw)
assert 'RIGHTMOUSE' in fonte and '_finish_drawing' in fonte, fonte[:400]
assert mc.abre_menu('DRAW', 'RIGHTMOUSE', 'PRESS') is False

# 5. Regressão: a ferramenta Inverter Sentido por clique continua invertendo uma parede só.
s.multi = []
s.selected = (1, 0)
lado_do_zero = s.plan.chains[0].side
s.plan.chains[1].invert()
assert s.plan.chains[0].side == lado_do_zero, "a cadeia vizinha não podia mudar"

props.end()
print("blender_bug_AKYJ_menu: OK")
