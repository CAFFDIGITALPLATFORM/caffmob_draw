"""Inventário e não repetição da barra lateral (feature 005, T005-T008, T033; RF-08, RF-09, D-11, D-12).

Run (verificação):
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_005_sidebar_inventory.py
Gravar a linha de base (uma vez, com a interface antiga):
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_005_sidebar_inventory.py -- --baseline

A camada falsa (`ui/layout_probe.py`) desenha a barra lateral em 8 contextos com todos os grupos abertos e registra
cada operador e a seção que o desenhou. O teste de inventário exige que todo operador da linha de base tenha um caminho
depois (barra lateral, menu do botão direito ou HUD). O de não repetição proíbe o mesmo operador (com os mesmos
argumentos de escopo) em duas seções da barra lateral.
"""

import json
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types, hb_utils  # noqa: E402
from caffmob_draw.geometry_free import mesh as geo_mesh  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.stick import link  # noqa: E402
from caffmob_draw.ui import layout_probe, sidebar_proxy  # noqa: E402

BASELINE = Path(__file__).resolve().parent / "fixtures" / "sidebar_inventory_baseline.json"
CATEGORY = "CAFFMob Draw"
# Argumentos que mudam o que o operador faz (o mesmo operador com outro escopo não é repetição).
SCOPE_ARGS = ('kind', 'scope', 'mode', 'action', 'target', 'front', 'redo', 'move_up', 'scene_name', 'object_name',
              'filepath', 'index', 'opening_type', 'product_name', 'cabinet_name', 'name', 'cabinet_type', 'path',
              'library', 'appliance_name', 'part_name', 'category', 'item_name', 'group')

ctx = bpy.context
scene = ctx.scene


# Contextos -------------------------------------------------------------------------------------------------
def _box_mesh(name, lo, hi, location):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(tuple(lo[i] if v.co[i] < 0 else hi[i] for i in range(3)))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    scene.collection.objects.link(obj)
    return obj


def build_scene():
    env.clean_scene()
    wall = hb_types.GeoNodeWall()
    wall.create("Parede")
    wall.set_input('Length', 4.0)
    wall.set_input('Thickness', 0.15)
    wall.set_input('Height', 2.6)
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.location = (0.5, -1.0, 0.0)
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    ff.obj.location = (3.0, -1.0, 0.0)
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    starter.obj.location = (6.0, -1.0, 0.0)
    tc.recalculate_closet_starter(starter.obj)
    bpy.ops.caffmob.cabinet_builder(width=0.6)
    quick = ctx.object
    quick.location = (9.0, -1.0, 0.0)
    plate = geo_mesh.create_object(ctx, 'PLACA', name="Placa")
    plate.location = (11.0, -1.0, 0.0)
    painel = _box_mesh("Painel", (0.0, -0.3, 0.0), (0.018, 0.3, 2.0), (13.0, -1.0, 0.0))
    nicho = _box_mesh("Nicho", (-0.15, -0.1, -0.15), (0.15, 0.1, 0.15), (13.4, -1.0, 1.0))
    env.settle()
    link.stick(nicho, painel, Vector((13.018, -1.0, 1.0)), Vector((1.0, 0.0, 0.0)))
    env.settle()
    return {'nada': None, 'parede': wall.obj, 'frameless': base.obj, 'face_frame': ff.obj,
            'closets': starter.obj, 'btm': quick, 'geometria': plate, 'grudado': nicho}


def select(obj):
    for o in ctx.view_layer.objects:
        o.select_set(False)
    ctx.view_layer.objects.active = obj
    if obj is not None:
        obj.select_set(True)


# Captura ---------------------------------------------------------------------------------------------------
class _FakeSpace:
    """A viewport que não existe em segundo plano: sombreamento sólido (mostra o aviso de cor por objeto)."""
    type = 'VIEW_3D'

    class shading:  # noqa: N801
        color_type = 'MATERIAL'
        type = 'SOLID'

    class overlay:  # noqa: N801
        show_overlays = True
        grid_scale = 1.0


class ContextProxy:
    """`bpy.context` com `space_data` simulado; o resto vem do contexto real."""

    space_data = _FakeSpace()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


CTX = ContextProxy()


def _panels():
    def subclasses(cls):
        out = []
        for sub in cls.__subclasses__():
            out.append(sub)
            out += subclasses(sub)
        return out
    found = []
    for cls in subclasses(bpy.types.Panel):
        if getattr(cls, 'bl_space_type', '') != 'VIEW_3D' or getattr(cls, 'bl_region_type', '') != 'UI':
            continue
        if getattr(cls, 'bl_category', '') != CATEGORY or not getattr(cls, 'is_registered', False):
            continue
        found.append(cls)
    return found


def _path(cls, by_id):
    names = [sidebar_proxy.label_of(cls)]
    parent = getattr(cls, 'bl_parent_id', '')
    while parent and parent in by_id:
        names.insert(0, sidebar_proxy.label_of(by_id[parent]))
        parent = getattr(by_id[parent], 'bl_parent_id', '')
    return " › ".join(names)


def capture_sidebar(recorder, errors, context_name):
    panels = _panels()
    by_id = {getattr(c, 'bl_idname', c.__name__): c for c in panels}
    for cls in panels:
        probe = layout_probe.Probe(recorder)
        with recorder.section(_path(cls, by_id)):
            try:
                sidebar_proxy.draw_panel(cls, probe, CTX, header=True)
            except Exception as exc:          # noqa: BLE001 - qualquer erro de desenho é um achado
                errors.append(f"{context_name}: {cls.__name__}: {exc.__class__.__name__}: {exc}")


def capture_context_menu(recorder, errors, context_name):
    menu = bpy.types.VIEW3D_MT_object_context_menu
    funcs = list(getattr(menu.draw, '_draw_funcs', []))
    for func in funcs:
        if func is menu.draw._draw_funcs[0] and getattr(func, '__module__', '').startswith('bl_ui'):
            continue
        if not getattr(func, '__module__', '').startswith('caffmob_draw'):
            continue
        probe = layout_probe.Probe(recorder)
        proxy = type('MenuProxy', (), {'layout': probe})()
        with recorder.section("[menu]"):
            try:
                func(proxy, CTX)
            except Exception as exc:          # noqa: BLE001
                errors.append(f"{context_name}: menu {func.__name__}: {exc}")


def capture_hud(recorder):
    from caffmob_draw.operators import viewport_hud
    with recorder.section("[hud]"):
        for idname in viewport_hud.inventory_operators():
            recorder.add('operator', idname)


def open_all_library_sections():
    """Abre as seções recolhíveis das galerias (`show_*`) para inventariar todos os itens."""
    for attr in ('hb_frameless', 'hb_face_frame', 'hb_closets'):
        props = getattr(scene, attr, None)
        if props is None:
            continue
        for prop in props.bl_rna.properties:
            if prop.identifier.startswith('show_') and prop.type == 'BOOLEAN' and not prop.is_readonly:
                setattr(props, prop.identifier, True)


def pick_obstacle_type():
    """O botão de inserir obstáculo só aparece com um tipo escolhido (o padrão é um cabeçalho da lista)."""
    obs = getattr(scene, 'hb_obstacles', None)
    if obs is None:
        return
    from caffmob_draw import hb_props_obstacles
    for item in hb_props_obstacles.get_obstacle_items(obs, ctx):      # itens dinâmicos
        if item[0] and not item[0].startswith('HEADER_'):
            obs.obstacle_type = item[0]
            return


def product_tabs():
    hb = getattr(scene, 'home_builder', None)
    if hb is None:
        return [None]
    return [item.identifier for item in hb.bl_rna.properties['product_tab'].enum_items]


def capture_all():
    contexts = build_scene()
    # 063: exercita os botões contextuais das listas, sem iniciar pedidos.
    state = ctx.window_manager.btm_caffmob
    state.ambientes.clear()
    state.modelos.clear()
    item = state.ambientes.add()
    item.id, item.nome = 'ambiente-teste', 'Ambiente de teste'
    item = state.modelos.add()
    item.id, item.nome, item.escopo = 'titular', 'Modelo de teste', 'titular'
    state.biblioteca = 'titular'
    state.proximo_ambiente = 'pagina-2' 
    open_all_library_sections()
    pick_obstacle_type()
    result = {'sidebar': {}, 'paths': {}, 'errors': []}
    for name, obj in contexts.items():
        select(obj)
        env.settle()
        side = layout_probe.Recorder()
        tabs = product_tabs() if name == 'nada' else [None]
        for tab in tabs:
            if tab is not None:
                scene.home_builder.product_tab = tab
            capture_sidebar(side, result['errors'], name)
        if tabs[0] is not None:
            scene.home_builder.product_tab = tabs[0]
        paths = layout_probe.Recorder()
        capture_context_menu(paths, result['errors'], name)
        if hasattr(__import__('caffmob_draw.operators.viewport_hud', fromlist=['x']), 'inventory_operators'):
            capture_hud(paths)
        result['sidebar'][name] = side.records
        result['paths'][name] = paths.records
    return result


def operator_names(records):
    return {r['name'] for r in records if r['kind'] == 'operator'}


# Verificações ------------------------------------------------------------------------------------------------
def retired_prefixes():
    """Operadores aposentados de propósito (feature 012, T055; D-06): ficam fora da conta do RF-08."""
    path = Path(__file__).resolve().parent / "fixtures" / "sidebar_retired_012.json"
    return tuple(json.loads(path.read_text(encoding='utf-8'))['operator_prefixes'])


def missing_capabilities(baseline, current):
    """RF-08: operadores da linha de base sem caminho agora (em nenhum contexto), menos os aposentados."""
    before = set()
    for records in baseline['sidebar'].values():
        before |= operator_names(records)
    for records in baseline.get('paths', {}).values():
        before |= operator_names(records)
    after = set()
    for name in current['sidebar']:
        after |= operator_names(current['sidebar'][name]) | operator_names(current['paths'][name])
    retired = retired_prefixes()
    return sorted(name for name in before - after if not name.startswith(retired))


def repeated(current):
    """RF-09: (contexto, operador, args de escopo) desenhado por mais de uma seção da barra lateral."""
    out = []
    for name, records in current['sidebar'].items():
        seen = {}
        for r in records:
            if r['kind'] != 'operator':
                continue
            scope = tuple(sorted((k, str(v)) for k, v in r['args'].items() if k in SCOPE_ARGS))
            key = (r['name'], scope)
            top = r['section'].split(" › ")[0] if r['section'] else ""
            seen.setdefault(key, set()).add(top if top else r['section'])
        for (op, scope), sections in seen.items():
            if len(sections) > 1:
                out.append((name, op, scope, sorted(sections)))
    return sorted(out)


def main():
    baseline_mode = "--baseline" in sys.argv
    current = capture_all()
    if baseline_mode:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        data = {'sidebar': {k: [r for r in v if r['kind'] == 'operator'] for k, v in current['sidebar'].items()},
                'paths': {k: [r for r in v if r['kind'] == 'operator'] for k, v in current['paths'].items()},
                'errors': current['errors']}
        BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str) + "\n", encoding='utf-8')
        ops = set()
        for records in data['sidebar'].values():
            ops |= operator_names(records)
        print(f"linha de base gravada: {len(ops)} operadores; erros de desenho: {len(current['errors'])}")
        for err in current['errors']:
            print("  ", err)
        return
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
    problems = []
    for err in current['errors']:
        problems.append(f"erro de desenho: {err}")
    lost = missing_capabilities(baseline, current)
    if lost:
        problems.append(f"capacidade perdida (RF-08): {lost}")
    reps = repeated(current)
    if reps:
        for name, op, scope, sections in reps:
            problems.append(f"repetido (RF-09) em '{name}': {op} {dict(scope)} → {sections}")
    for p in problems:
        print("FALHA", p)
    assert not problems, f"{len(problems)} problema(s) na barra lateral"
    print("OK blender_005_sidebar_inventory")


main()
