"""Medidas reais e edição segura de módulos (feature 080, T006 e T022; CA-01 a CA-07, CA-11 a CA-14).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_080_medidas_reais.py

Por família (BTM, FACE_FRAME, CLOSETS, AUTHORED, FRAMELESS): um módulo com escala própria 0,8125 em X, um sob um
Empty com escala 2 em X e um espelhado (−0,75 em X).
- Leitura (CA-01): a medida mostrada é parâmetro × escala do eixo no mundo; ler não escreve nada (CA-14).
- Escrita (CA-02): a medida digitada vira medida física, a raiz fica com escala ±1 (o espelho fica), os eixos não
  editados guardam a medida física, o pai não muda e os descendentes não recriados ficam na mesma pose física.
- Recusas (CA-04), sobreposição aceita (CA-11), falha injetada com rollback (CA-06), editor e Redimensionar na mesma
  transação, substituição de 650 mm (CA-05), salvar e reabrir (CA-14).
O banco do Padrão de Dimensões é descartável (o do portão, ou um temporário quando roda sozinho).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

_TMP = tempfile.TemporaryDirectory(prefix="caffmob_080_")
os.environ.setdefault("CAFFMOB_DRAW_STANDARDS_DB", os.path.join(_TMP.name, "padroes.sqlite3"))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _authored_env as authored_env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import leaf  # noqa: E402
from caffmob_draw.collision import guard  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import classify, editing, element_size, module_resize, resize  # noqa: E402

CTX = bpy.context
FAILS = []
FAMILIES = ('BTM', 'FACE_FRAME', 'CLOSETS', 'AUTHORED', 'FRAMELESS')
TOL = 1e-4                  # 0,1 mm (RNF-01)


def check(cond, msg):
    print(("OK    " if cond else "FALHA ") + msg)
    if not cond:
        FAILS.append(msg)


def close(a, b, tol=TOL):
    return abs(a - b) <= tol


# Montagem ---------------------------------------------------------------------------------------------------

@guard.suspended()
def build(family, name, x):
    if family == 'BTM':
        assert bpy.ops.caffmob.cabinet_builder(width=0.8) == {'FINISHED'}
        root = CTX.object
    elif family == 'FRAMELESS':
        cab = tf.BaseCabinet()
        cab.create(name)
        hb_utils.run_calc_fix_until_stable(CTX, cab.obj)
        root = cab.obj
    elif family == 'FACE_FRAME':
        cab = tff.BaseFaceFrameCabinet()
        cab.create(name)
        root = cab.obj
    elif family == 'CLOSETS':
        starter = tc.BaseClosetStarter()
        starter.create_starter(name, bay_qty=2)
        tc.recalculate_closet_starter(starter.obj)
        root = starter.obj
    else:
        root, _body = authored_env.tower(name)
    root.location = (x, 0.0, 0.0)
    env.settle()
    info = classify.classify(root)
    assert info.kind == classify.MODULE and info.library == family, (family, info.kind, info.library)
    return root


@guard.suspended()
def under_scaled_parent(root, scale_x=2.0):
    parent = bpy.data.objects.new(root.name + " pai", None)
    CTX.collection.objects.link(parent)
    parent.location = root.location.copy()
    parent.scale = (scale_x, 1.0, 1.0)
    env.settle()
    root.parent = parent
    root.matrix_parent_inverse = Matrix.Identity(4)
    root.matrix_basis = Matrix.Identity(4)        # na origem do pai, escala própria 1: o pai estica o módulo
    env.settle()
    return parent


def set_scale(root, scale):
    with guard.suspended():
        root.scale = scale
        env.settle()


def info_of(root):
    return classify.classify(root)


def physical(root):
    info = info_of(root)
    return tuple(editing.get_dimension(info, f) for f in ('width', 'depth', 'height'))


def params(root):
    return module_resize.read_params(root, info_of(root).library)


def world_extent(root, axis=0):
    """Medida física do conjunto num eixo do mundo: caixa de todas as malhas visíveis do módulo (raiz incluída)."""
    xs = []
    for obj in [root] + list(root.children_recursive):
        if obj.type != 'MESH' or not obj.visible_get():
            continue
        xs += [(obj.matrix_world @ Vector(c))[axis] for c in obj.bound_box]
    return (max(xs) - min(xs)) if xs else 0.0


def root_extent(root, axis):
    """Caixa avaliada da própria raiz (a gaiola do FRAMELESS), em unidades do mundo."""
    evaluated = root.evaluated_get(CTX.evaluated_depsgraph_get())
    values = [(root.matrix_world @ Vector(c))[axis] for c in evaluated.bound_box]
    return max(values) - min(values)


def state(root):
    """O que ler não pode mudar (CA-14): parâmetros, transformação, objetos e as poses deles."""
    objs = [root] + list(root.children_recursive)
    return (params(root), tuple(root.matrix_basis.col[i][j] for i in range(4) for j in range(4)),
            len(bpy.data.objects), sorted((o.name, tuple(round(v, 6) for row in o.matrix_world for v in row))
                                          for o in objs))


def add_leaf(root):
    """Folha de porta do usuário presa à raiz (agregado não recriado pelo gerador)."""
    with guard.suspended():
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=root.matrix_world @ Vector((0.1, -0.6, 0.3)))
        obj = CTX.object
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world
        env.settle()
        leaf.make_leaf(obj, root)
        env.settle()
    return obj


def add_free_child(root):
    """Agregado simples (não folha) do usuário, filho da raiz."""
    with guard.suspended():
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=root.matrix_world @ Vector((0.2, -0.2, 0.9)))
        obj = CTX.object
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world
        obj.btm_aggregate.is_aggregate = True
        env.settle()
    return obj


def matrix_error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))


# Casos ------------------------------------------------------------------------------------------------------

def case_read(family, x):
    root = build(family, f"{family} leitura", x)
    p = params(root)
    check(all(close(a, b) for a, b in zip(physical(root), p)), f"{family}: sem escala, mostra o parâmetro {p}")
    if family == 'FRAMELESS':
        # Inferência do roadmap (D-02): Dim Y é a profundidade.
        extent_y = root_extent(root, 1)
        check(close(extent_y, p[1], 0.05), f"{family}: Dim Y é a profundidade (Dim Y {p[1] * 1000:.0f} mm, "
                                           f"caixa em Y {extent_y * 1000:.0f} mm)")
    set_scale(root, (0.8125, 1.0, 1.0))
    before = state(root)
    phys = physical(root)
    check(close(phys[0], p[0] * 0.8125) and close(phys[1], p[1]) and close(phys[2], p[2]),
          f"{family}: escala própria 0,8125 mostra {phys[0] * 1000:.1f} mm de largura")
    for _ in range(3):
        physical(root)
        editing.editable_dimensions(info_of(root))
    env.settle()
    check(state(root) == before, f"{family}: ler e selecionar não escreve nada")
    return root


def case_write_own_scale(family, x):
    root = build(family, f"{family} escala", x)
    kept = add_free_child(root) if family != 'AUTHORED' else None
    p = params(root)
    set_scale(root, (0.8125, 1.0, 1.0))
    kept_world = kept.matrix_world.copy() if kept is not None else None
    members = {o.name: o.matrix_world.copy() for o in root.children} if family == 'AUTHORED' else {}
    target = p[0]
    editing.set_dimension(CTX, info_of(root), 'width', target)
    env.settle()
    phys = physical(root)
    check(tuple(root.scale) == (1.0, 1.0, 1.0), f"{family}: depois de editar, escala própria {tuple(root.scale)}")
    check(close(phys[0], target), f"{family}: largura física {phys[0] * 1000:.2f} mm = {target * 1000:.0f}")
    check(close(phys[1], p[1]) and close(phys[2], p[2]), f"{family}: profundidade e altura guardam a medida física")
    check(close(params(root)[0], target), f"{family}: parâmetro = medida física ({params(root)[0]:.4f})")
    if family != 'AUTHORED':
        # O autoral não tem gerador: membros FIXED não esticam (regra da 066); lá vale a pose dos membros, abaixo.
        extent = world_extent(root, 0)
        check(close(extent, target, 2e-3), f"{family}: o conjunto mede {extent * 1000:.1f} mm no mundo")
    if kept is not None:
        check(matrix_error(kept.matrix_world, kept_world) < TOL, f"{family}: agregado do usuário na mesma pose física")
    for name, world in members.items():
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.btm_member.rule == 'FIXED':
            check(matrix_error(obj.matrix_world, world) < TOL,
                  f"{family}: membro fixo {name} na mesma pose física depois de assar")
    # Repetir a mesma medida não muda nada.
    before = state(root)
    editing.set_dimension(CTX, info_of(root), 'width', target)
    env.settle()
    check(state(root) == before, f"{family}: repetir {target * 1000:.0f} mm não muda nada")
    return root


def case_frameless_depth(x):
    root = build('FRAMELESS', "FRAMELESS profundidade", x)
    set_scale(root, (1.0, 0.8, 1.0))
    editing.set_dimension(CTX, info_of(root), 'depth', 0.5)
    env.settle()
    check(close(root_extent(root, 1), 0.5, 1e-3) and close(params(root)[1], 0.5),
          f"FRAMELESS: profundidade 500 mm vai para Dim Y (caixa {root_extent(root, 1) * 1000:.1f} mm)")


def case_mirror(family, x):
    root = build(family, f"{family} espelho", x)
    p = params(root)
    set_scale(root, (-0.75, 1.0, 1.0))
    check(close(physical(root)[0], p[0] * 0.75), f"{family}: espelhado mostra largura positiva")
    editing.set_dimension(CTX, info_of(root), 'width', 0.9)
    env.settle()
    check(tuple(root.scale) == (-1.0, 1.0, 1.0), f"{family}: o espelho fica (escala {tuple(root.scale)})")
    check(close(physical(root)[0], 0.9), f"{family}: espelhado com 900 mm")
    return root


def case_parent(family, x):
    root = build(family, f"{family} pai", x)
    parent = under_scaled_parent(root, 2.0)
    p = params(root)
    check(close(physical(root)[0], p[0] * 2.0), f"{family}: sob pai com escala 2 mostra o dobro")
    editing.set_dimension(CTX, info_of(root), 'width', 1.0)
    env.settle()
    check(tuple(parent.scale) == (2.0, 1.0, 1.0), f"{family}: o pai não muda")
    check(close(physical(root)[0], 1.0), f"{family}: 1000 mm físicos sob o pai")
    check(close(params(root)[0], 0.5), f"{family}: parâmetro compensado ({params(root)[0]:.4f})")
    return root


def case_injected_failure(family, x):
    root = build(family, f"{family} falha", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    kept = add_free_child(root) if family != 'AUTHORED' else None
    before_params, before_scale = params(root), tuple(root.scale)
    before_world = kept.matrix_world.copy() if kept is not None else None
    module_resize._FAIL_AFTER_FIRST_WRITE[0] = True
    try:
        editing.set_dimension(CTX, info_of(root), 'width', 0.7)
        raised = False
    except Exception:
        raised = True
    finally:
        module_resize._FAIL_AFTER_FIRST_WRITE[0] = False
    env.settle()
    check(raised, f"{family}: a falha injetada é propagada")
    check(all(close(a, b) for a, b in zip(params(root), before_params)), f"{family}: rollback dos parâmetros")
    check(tuple(root.scale) == before_scale, f"{family}: rollback da escala {tuple(root.scale)}")
    if kept is not None:
        check(matrix_error(kept.matrix_world, before_world) < TOL, f"{family}: rollback da pose do agregado")
    check(close(physical(root)[0], before_params[0] * 0.8125), f"{family}: medida física de antes")
    # Depois do rollback, a próxima edição funciona.
    editing.set_dimension(CTX, info_of(root), 'width', 0.7)
    env.settle()
    check(close(physical(root)[0], 0.7), f"{family}: depois do rollback, editar funciona")


def case_refusals(x):
    root = build('BTM', "BTM recusas", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    before = state(root)
    for bad in (3.5, 0.0, -0.01, float('nan'), float('inf'), "abc"):
        try:
            editing.set_dimension(CTX, info_of(root), 'width', bad)
            refused, message = False, ""
        except ValueError as exc:
            refused, message = True, str(exc)
        check(refused, f"BTM: {bad!r} recusado ({message})")
    check(state(root) == before, "BTM: as recusas não mudam nada")
    try:
        editing.set_dimension(CTX, info_of(root), 'width', 3.5)
    except ValueError as exc:
        text = str(exc)
        check(root.name in text and ("3" in text and "100" in text or "0,1" in text or "0.1" in text),
              f"BTM: a recusa de 3500 mm diz o alvo e a faixa física ({text})")


def case_overlap(x):
    a = build('BTM', "BTM vizinho A", x)
    b = build('BTM', "BTM vizinho B", x + 0.8)
    editing.set_dimension(CTX, info_of(a), 'width', 1.2)
    env.settle()
    check(close(physical(a)[0], 1.2), "BTM: aumentar até sobrepor o vizinho é aceito (sem veto por colisão)")
    return a, b


def case_leaf(x):
    root = build('BTM', "BTM folha", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    door = add_leaf(root)
    closed = door.matrix_world.copy()
    editing.set_dimension(CTX, info_of(root), 'width', 0.8)
    env.settle()
    check(matrix_error(door.matrix_world, closed) < TOL, "BTM: folha do usuário na mesma pose física depois de assar")
    leaf.apply_fraction(door, 1.0)
    env.settle()
    leaf.apply_fraction(door, 0.0)
    env.settle()
    check(matrix_error(door.matrix_world, closed) < TOL, "BTM: abrir e fechar a folha volta à mesma pose")


def case_editor(x):
    from caffmob_draw.cabinet_editor import bridge
    import dataclasses
    root = build('BTM', "BTM editor", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    current = bridge.read_state(root)
    check(close(current.dimensions[0], 0.65), f"editor: lê a largura física ({current.dimensions[0] * 1000:.1f} mm)")
    limits = bridge.library_limits(root, 'BTM')
    check(close(limits['width'][1], 3.0), f"editor: faixa física da largura {limits.get('width')}")
    target = dataclasses.replace(current, dimensions=(0.9, 0.6, 0.5))
    bridge.apply_state(CTX, root, target)
    env.settle()
    phys = physical(root)
    check(close(phys[0], 0.9) and close(phys[2], 0.6) and close(phys[1], 0.5),
          f"editor: as 3 medidas aplicadas numa transação ({[round(v * 1000, 1) for v in phys]})")
    check(tuple(root.scale) == (1.0, 1.0, 1.0), "editor: escala assada")


def case_resize(x):
    root = build('BTM', "BTM redimensionar", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    el = element_size.element(root)
    resize.resize(CTX, el, 0.7)
    env.settle()
    check(close(physical(root)[0], 0.7) and tuple(root.scale) == (1.0, 1.0, 1.0),
          f"Redimensionar: 700 mm físicos com escala assada ({physical(root)[0] * 1000:.1f} mm)")


def case_replace(x):
    assert bpy.ops.caffmob.library_insert_model(model_id="balcao_1p") == {'FINISHED'}
    root = CTX.view_layer.objects.active
    root.location = (x, 0.0, 0.0)
    with guard.suspended():
        root.btm_cabinet.width = 0.8
        root.scale = (0.8125, 1.0, 1.0)
        env.settle()
    authored_env.select([root])
    assert bpy.ops.caffmob.library_replace_selected(model_id="gaveteiro_4g") == {'FINISHED'}
    new = CTX.view_layer.objects.active
    env.settle()
    check(close(physical(new)[0], 0.65), f"substituir: o gaveteiro mede {physical(new)[0] * 1000:.1f} mm reais")
    check(tuple(new.scale) == (1.0, 1.0, 1.0), f"substituir: destino com escala {tuple(new.scale)}")
    check(close(new.btm_cabinet.width, 0.65), "substituir: parâmetro = medida física")


def case_panel(x):
    """O campo do painel (T017): lê a medida física e grava pela transação; a próxima edição não é recusada."""
    from caffmob_draw.target import snapshot
    from caffmob_draw.ui import object_properties as op
    root = build('BTM', "BTM painel", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    authored_env.select([root])
    snapshot.refresh(CTX)
    sel = CTX.scene.btm_selection
    check(close(sel.width, 0.65), f"painel: mostra {sel.width * 1000:.1f} mm")
    sel.width = 0.8
    check(CTX.window_manager.get(op.ERROR_KEY) is None, "painel: sem erro ao gravar 800 mm")
    check(close(sel.width, 0.8) and tuple(root.scale) == (1.0, 1.0, 1.0),
          f"painel: depois de gravar mostra {sel.width * 1000:.1f} mm com escala assada")
    sel.width = 0.7
    check(CTX.window_manager.get(op.ERROR_KEY) is None and close(physical(root)[0], 0.7),
          "painel: a edição seguinte não é recusada por mudança de pose")
    sel.width = 3.5
    message = CTX.window_manager.get(op.ERROR_KEY) or ""
    check("3000" in message and close(physical(root)[0], 0.7), f"painel: 3500 mm recusado com a faixa ({message})")


def case_save_reopen(x):
    root = build('BTM', "BTM salvar", x)
    set_scale(root, (0.8125, 1.0, 1.0))
    editing.set_dimension(CTX, info_of(root), 'width', 0.8)
    env.settle()
    name = root.name
    path = os.path.join(_TMP.name, "080_salvar.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    env.settle()
    again = bpy.data.objects[name]
    check(close(physical(again)[0], 0.8) and tuple(again.scale) == (1.0, 1.0, 1.0),
          "salvar e reabrir conserva medida e escala")
    before = state(again)
    physical(again)
    check(state(again) == before, "reabrir e ler não muda nada")
    editing.set_dimension(bpy.context, classify.classify(again), 'width', 0.75)
    env.settle()
    check(close(physical(again)[0], 0.75), "depois de reabrir, a próxima edição funciona")


def main():
    env.clean_scene()
    x = 0.0
    for family in FAMILIES:
        for case in (case_read, case_write_own_scale, case_mirror, case_parent, case_injected_failure):
            try:
                case(family, x)
            except Exception:
                traceback.print_exc()
                FAILS.append(f"{family}: {case.__name__} levantou")
            x += 3.0
    for case in (case_frameless_depth, case_refusals, case_overlap, case_leaf, case_editor, case_resize,
                 case_replace, case_panel):
        try:
            case(x)
        except Exception:
            traceback.print_exc()
            FAILS.append(f"{case.__name__} levantou")
        x += 3.0
    try:
        case_save_reopen(x)
    except Exception:
        traceback.print_exc()
        FAILS.append("case_save_reopen levantou")
    if FAILS:
        print(f"blender_080_medidas_reais: {len(FAILS)} falha(s)")
        for item in FAILS:
            print("  - " + item)
        sys.exit(1)
    print("blender_080_medidas_reais: OK")


main()
