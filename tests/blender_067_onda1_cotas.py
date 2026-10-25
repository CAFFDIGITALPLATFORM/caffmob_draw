"""Cotas da seleção (feature 067, T020; RF-015, RF-018, RF-027 a RF-029, D-07).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda1_cotas.py

- os 15 tipos têm cota ou "indisponível para <motivo>";
- lado sem referência nunca vira 0: o painel diz "sem referência";
- "Mover: <alvo>": a peça autoral anda sozinha no escopo Peça; a peça gerada pelo módulo nunca é alvo móvel;
- o setter e o operador recusam quando a referência mudou depois da leitura;
- a cota só existe com seleção; nenhuma chave de cotas na interface;
- a cota de parede não move a parede.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
import _desempenho_067 as perf  # noqa: E402
from caffmob_draw.overlays import side_cotas  # noqa: E402
from caffmob_draw.target import snapshot, view  # noqa: E402
from caffmob_draw.ui import layout_probe  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

FAILURES = []
ROOT = Path(__file__).resolve().parents[1]


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def target_of(obj):
    fx.select([obj])
    bpy.context.view_layer.update()
    return snapshot.ensure(bpy.context)


def drawn(obj):
    target_of(obj)
    recorder = layout_probe.Recorder()
    op.panel_mode = lambda _c: 'COMPLETE'
    op.draw_selected(layout_probe.Probe(recorder), perf.CTX)
    return {r['name'] for r in recorder.records if r['kind'] == 'prop'}


def run():
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False
    state = bpy.context.window_manager.btm_target
    for name, obj in vars(s).items():
        sections = {sec.id: sec for sec in view.build(target_of(obj), view.COMPLETE).sections}
        cotas = sections.get('cotas')
        fields = [i for i in (cotas.items if cotas else ()) if isinstance(i, view.Field)]
        notes = [i for i in (cotas.items if cotas else ()) if isinstance(i, view.Note)]
        check(bool(fields) != bool(notes) and (fields or "indisponível" in notes[0].text),
              f"{name}: cota ou indisponível com motivo")

    # Lado sem referência nunca é 0: o cubo solto longe de tudo não tem referência à esquerda e à direita.
    far = s.free
    far.location = (-40.0, -40.0, 0.2)
    env.settle()
    target_of(far)
    found = side_cotas.records(bpy.context)
    props = drawn(far)
    for side, field in (('LEFT', 'cota_esquerda'), ('RIGHT', 'cota_direita')):
        if side not in found:
            check(field not in props, f"{side}: sem referência, sem campo com 0")

    # Alvo móvel e escopo.
    target_of(s.member)
    state.cota_scope = 'PART'
    check(side_cotas.moving_object(bpy.context, refresh=True) == s.member, "escopo Peça: a peça autoral anda sozinha")
    state.cota_scope = 'ASSEMBLY'
    check(side_cotas.moving_object(bpy.context, refresh=True) == s.authored, "escopo Conjunto: anda o armário")
    state.cota_scope = 'PART'
    target_of(s.part)
    check(side_cotas.moving_object(bpy.context, refresh=True) == s.hb_module,
          "peça gerada pelo módulo nunca é alvo móvel: anda o módulo")

    # Referência mudou depois da leitura: recusa.
    target_of(s.free)
    mover = side_cotas.moving_object(bpy.context, refresh=True)
    pose = tuple(mover.matrix_world.translation)
    mover.location.x += 0.5
    env.settle()
    try:
        side_cotas.check_unchanged(bpy.context, mover.session_uid, pose)
        refused = False
    except ValueError:
        refused = True
    check(refused, "a cota recusa quando o alvo andou depois da leitura")

    # Só com seleção.
    for other in list(bpy.context.selected_objects):
        other.select_set(False)
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.update()
    snapshot.ensure(bpy.context)
    check(side_cotas.moving_object(bpy.context, refresh=True) is None and not side_cotas.records(bpy.context),
          "sem seleção, nenhuma cota")

    # Nenhuma chave de cotas na interface.
    sources = [(ROOT / "caffmob_draw" / p).read_text(encoding='utf-8') for p in ("ui/panels.py", "collision/panels.py")]
    check(not any('"show_side_dimensions"' in src for src in sources), "nenhuma chave \"Medidas laterais\" na interface")

    # Cota de parede: indisponível, e nada move a parede.
    target_of(s.wall)
    before = s.wall.matrix_world.copy()
    check(not side_cotas.BTM_OT_FixedCotaEdit.poll(bpy.context), "o clique na cota não existe para a parede")
    try:
        side_cotas.apply_fixed(bpy.context, 'LEFT', 1.0)
    except ValueError:
        pass
    check(s.wall.matrix_world == before, "a cota não move a parede")


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda1_cotas: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
