"""Protótipo da premissa 2 (feature 067, T006; D-03): o snapshot é refeito pelos handlers antes do redesenho.

Em segundo plano não há laço de eventos, então o msgbus do ativo não é entregue; quem refaz o snapshot aqui é o
`depsgraph_update_post` que a troca de seleção dispara no `view_layer.update()`. O ensaio confere:
1. depois de cada troca, `snapshot.current()` já tem o alvo certo sem ninguém chamar `ensure` (o draw só lê);
2. resolver custa pouco: p95 de `refresh` com o cache vazio ≤ 2 ms;
3. a troca de seleção até o painel desenhado fica em p95 ≤ 50 ms na cena de 461 objetos.
O caminho do msgbus (troca do ativo sem update do depsgraph) fica para o QA na interface (onboarding §2).
"""

import json
import sys
import time
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _desempenho_067 as perf  # noqa: E402
from caffmob_draw.target import snapshot  # noqa: E402

targets = perf.build_scene()
misses = []


def check(obj):
    # O ativo pode não ser `obj`: a seleção por componente promove a peça ao módulo dono.
    active = bpy.context.view_layer.objects.active
    target = snapshot.current(bpy.context)
    if target is None or active is None or active.session_uid not in target.selected_uids:
        misses.append(obj.name)


perf.measure(targets, rounds=2)
total = perf.percentiles(perf.measure(targets, before_draw=check))
assert not misses, f"snapshot não refeito pelo handler em {len(misses)} trocas: {misses[:5]}"

costs = []
for _round in range(20):
    for obj in targets:
        perf.select(obj)
        bpy.context.view_layer.update()
        snapshot.forget()
        start = time.perf_counter()
        snapshot.refresh(bpy.context)
        costs.append((time.perf_counter() - start) * 1000.0)
refresh = perf.percentiles(costs)
print("PROTO_SNAPSHOT", json.dumps({'troca_ate_painel': total, 'refresh': refresh}), flush=True)
assert refresh['p95'] <= 2.0, refresh
assert total['p95'] <= 50.0, total
print("PROTO_SNAPSHOT_OK", flush=True)
