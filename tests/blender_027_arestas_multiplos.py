"""Arestas do viewport e medidas na seleção múltipla (027, T004 a T008; RF-03, RF-04).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_027_arestas_multiplos.py

- a preferência "Espessura da aresta" existe com 0,2 px e o handler das arestas pretas está registrado (o wireframe do
  Blender fica desligado: as linhas são desenhadas por `overlays/arestas.py`);
- "Aplicar transformações em todos os selecionados" existe ligada por padrão;
- três chapas 15/15/18: o painel fica vazio com "?" na espessura, e a confirmação
  (`caffmob.target_multi_apply`) aplica 18 nas três de uma vez; largura de chapa não é editável e fica de fora;
- a espessura comum é escrita na unidade do projeto.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
import caffmob_draw as addon  # noqa: E402
from caffmob_draw.data import units  # noqa: E402
from caffmob_draw.geometry_free import mesh as geometry_mesh  # noqa: E402
from caffmob_draw.overlays import arestas  # noqa: E402
from caffmob_draw.target import multi_apply, snapshot  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402
from caffmob_draw.ui import view_mode_core  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(name)


class Preferencias:
    """Preferências de mentira: o pacote registrado direto não entra em `preferences.addons`."""

    espessura_aresta = 1.5
    aplicar_em_todos = True


def main():
    # O add-on é registrado pelo `_blender_env` fora de `preferences.addons`: o teste lê o RNA da classe.
    props = addon.BTM_AddonPreferences.bl_rna.properties
    check("preferência espessura_aresta existe", props.get('espessura_aresta') is not None)
    check("espessura padrão 0,2 px", abs(props['espessura_aresta'].default - 0.2) < 1e-6,
          str(props['espessura_aresta'].default))
    check("arestas.espessura cai no padrão sem preferências salvas", abs(arestas.espessura() - 0.2) < 1e-9,
          str(arestas.espessura()))
    check("espessura ajustável pela preferência", abs(arestas.valor(Preferencias()) - 1.5) < 1e-9,
          str(arestas.valor(Preferencias())))
    check("handler das arestas registrado", arestas._handler is not None)
    check("cache descartado no depsgraph", arestas._ao_atualizar in bpy.app.handlers.depsgraph_update_post)
    arestas.forget()
    check("desenho sem vista 3D não quebra", arestas._draw() is None)

    settings = view_mode_core.settings('TEXTURE', True, 'MATERIAL')
    check("modo de vista entrega as arestas ao overlay",
          settings['edges'] is True and settings['show_wireframes'] is False, str(settings))
    check("sem Linhas o overlay não desenha nada", view_mode_core.settings('TEXTURE', False, '')['edges'] is False)

    check("preferência aplicar_em_todos existe", props.get('aplicar_em_todos') is not None)
    check("aplicar em todos ligada por padrão", props['aplicar_em_todos'].default is True)

    # Três chapas com espessuras diferentes (o cenário da RF-04).
    sheets = []
    for i, thickness in enumerate((0.015, 0.015, 0.018)):
        g = geometry_mesh.create_object(bpy.context, 'PLACA')
        g.btm_geometry.plane, g.btm_geometry.thickness = 'XZ', thickness
        geometry_mesh.update(g)
        g.location = (5.0 + i, 5.0, 0.0)
        sheets.append(g)
    env.settle()
    fx.select(sheets, sheets[0])
    target = snapshot.ensure(bpy.context)
    check("alvo é seleção múltipla", target is not None and target.kind == 'MULTIPLE')
    check("as quatro medidas da seleção são lidas",
          target is not None and len(target.multi_sizes) == 3 and all(len(s) == 4 for s in target.multi_sizes))
    check("espessuras 15/15/18", target is not None
          and [round(s[3], 6) for s in target.multi_sizes] == [0.015, 0.015, 0.018])
    check("largura de chapa não é editável aqui", target is not None and all(s[0] is None for s in target.multi_sizes))
    check("o painel vê a espessura divergente", op._multi_multiplos(target, 'multi_thickness'))
    check("campo vazio com ? quando divergem", bpy.context.scene.btm_selection.multi_thickness == "",
          repr(bpy.context.scene.btm_selection.multi_thickness))

    resultado = bpy.ops.caffmob.target_multi_apply('EXEC_DEFAULT', field='thickness', value='18')
    check("a confirmação aplica nas três", resultado == {'FINISHED'}, str(resultado))
    check("as três ficaram com 18", [round(g.btm_geometry.thickness, 6) for g in sheets] == [0.018, 0.018, 0.018],
          str([round(g.btm_geometry.thickness, 6) for g in sheets]))
    env.settle()
    snapshot.ensure(bpy.context)
    comum = units.format_length(0.018, unit=units.get_scene_length_unit())
    check("a espessura comum aparece no campo", bpy.context.scene.btm_selection.multi_thickness == comum,
          f"{bpy.context.scene.btm_selection.multi_thickness!r} != {comum!r}")

    done, ignored, failures = multi_apply.apply(bpy.context, tuple(target.selected_uids), 'width', 0.8)
    check("largura de chapa fica fora, sem erro", done == 0 and ignored == 3 and not failures,
          f"done={done} ignored={ignored} failures={failures}")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"blender_027_arestas_multiplos: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    sys.exit(1 if FAILURES else 0)
