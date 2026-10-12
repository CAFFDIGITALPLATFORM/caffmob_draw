"""Porta e janela reais dentro da caixa da parede (feature 010, T017-T018; RN-01 a RN-04, RN-10, D-10 a D-12).

A caixa (`GeoNodeCage` com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP`) continua sendo o furo que corta a parede (R-04 a R-08).
`sync` monta dentro dela:
- um grupo **FRAME** (marco, guarnições, ferragens do marco; na janela, também trilhos e peitoril), filho da caixa;
- uma folha **LEAF** por folha da porta (giro, `leaf.make_leaf`) ou da janela (correr, com parada no batente e no
  montante da outra folha, como a 007).

Também passa a caixa para arame (a colisão da folha ignora objetos em arame) e esconde o texto "DOOR"/"WINDOW" na
vista 3D. A montagem só é refeita quando a assinatura (medidas, tipo, lado e sentido) muda. Ao refazer, a abertura
das folhas e a marcação de peça de produção voltam como estavam.

Lado e sentido vêm do símbolo 2D (`GeoNodeDoorSwing`), medidos no Blender 5.2: `Swing Inside` desenha o arco no lado
−Y da caixa, e `Is Left` põe a dobradiça em x = largura da caixa.
"""

import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from .. import hb_types
from ..aggregates import apply, collision, group, leaf
from ..inspection import room_door_leaf
from . import build, door_core, props, window_core

DOOR_FLAG, WINDOW_FLAG = 'IS_ENTRY_DOOR_BP', 'IS_WINDOW_BP'
SWING_MAX = 90.0
PART_PROP = 'btm_opening_part'       # objeto criado pela montagem (os demais são do usuário e ficam, DT-05)


def is_opening(obj):
    return obj is not None and (obj.get(DOOR_FLAG) or obj.get(WINDOW_FLAG))


def _swing(cage):
    """(objeto do símbolo 2D, Is Left, Swing Inside, Is Double) ou Nones. Só o símbolo de giro conta: cota ou texto
    2D pendurado na caixa não (questions.md, pergunta 23)."""
    for child in cage.children:
        if child.get('IS_2D_ANNOTATION'):
            swing = hb_types.GeoNodeObject(child)
            if not (swing.has_modifier() and swing.has_input('Swing Inside')):
                continue
            try:
                return (child, bool(swing.get_input('Is Left')), bool(swing.get_input('Swing Inside')),
                        bool(swing.get_input('Is Double')))
            except Exception:
                return child, True, True, False
    return None, None, None, None


def kind_of(cage):
    if cage.get(WINDOW_FLAG):
        return 'WINDOW'
    data = cage.btm_opening_real
    swing, _left, _inside, double = _swing(cage)
    if data.kind not in ('NONE', 'DOOR', 'DOUBLE_DOOR'):
        return data.kind
    if swing is None:
        return 'OPEN_DOOR' if data.kind == 'NONE' else data.kind
    return 'DOUBLE_DOOR' if double else 'DOOR'      # simples ou dupla segue o símbolo (Toggle Double Door, DT-03)


def _dims(cage):
    geo = hb_types.GeoNodeCage(cage)
    return geo.get_input('Dim X'), geo.get_input('Dim Y'), geo.get_input('Dim Z')


def signature(cage):
    kind = kind_of(cage)
    dims = _dims(cage)
    _swing_obj, left, inside, _double = _swing(cage)
    return "{}|{:.5f}|{:.5f}|{:.5f}|{}|{}|v{}".format(kind, *dims, left, inside, props.MODEL_VERSION)


def _parts(cage, kind):
    width, wall, height = _dims(cage)
    if kind == 'WINDOW':
        return window_core.window_parts(width, height, wall)
    _swing_obj, left, inside, _double = _swing(cage)
    double = kind == 'DOUBLE_DOOR'
    leaf_w, leaf_h = door_core.leaf_size(width, height, double=double)
    return door_core.door_parts(leaf_w, leaf_h, wall, hinge='RIGHT' if left else 'LEFT',
                                side='NEG_Y' if inside or inside is None else 'POS_Y', double=double,
                                open_door=kind == 'OPEN_DOOR')


def _remember(assembly):
    """(abertura de cada folha, folhas marcadas como peça de produção) da montagem anterior."""
    opens, production = {}, set()
    if assembly is None:
        return opens, production
    for obj in [assembly] + list(assembly.children_recursive):
        agg = getattr(obj, 'btm_aggregate', None)
        if agg is not None and agg.is_aggregate and agg.kind == 'LEAF':
            opens[obj.name.split(".")[0]] = agg.open_value
        if agg is not None and agg.is_aggregate and agg.production_part:
            production.add(obj.name.split(".")[0])
    return opens, production


def _created(assembly, cage):
    """Objetos criados pela montagem; montagem antiga, sem a marca: os de nome da caixa (todos começam por ele)."""
    tree = [assembly] + list(assembly.children_recursive)
    if any(obj.get(PART_PROP) for obj in tree):
        return [obj for obj in tree if obj.get(PART_PROP)]
    base = cage.name.split(".")[0]
    return [obj for obj in tree if obj.name.startswith(base)]


def clear(cage):
    """Apaga a montagem; o que o usuário pendurou nela fica, filho da caixa, no mesmo lugar (questions.md, pergunta 26)."""
    assembly = cage.btm_opening_real.assembly
    if assembly is None or assembly.name not in bpy.data.objects:
        return
    created = _created(assembly, cage)
    names = {obj.name for obj in created}
    for obj in list(assembly.children_recursive):
        if obj.name not in names and obj.parent is not None and obj.parent.name in names:
            _parent_keep(obj, cage)
    for obj in created:
        if obj.name in bpy.data.objects:
            data = obj.data if obj.type == 'MESH' else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.meshes.remove(data)
    cage.btm_opening_real.assembly = None


def _to_world(cage, objs):
    for obj in objs:
        obj.matrix_world = cage.matrix_world @ obj.matrix_world


def _parent_keep(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = world


def _align(obj, cage):
    """Gira o grupo (Empty) para os eixos da caixa, sem mexer nas peças: o "correr para +X" e o lado da dobradiça da
    folha (003/007) são medidos nos eixos do grupo, e a caixa pode estar girada com a parede."""
    kids = [(child, child.matrix_world.copy()) for child in obj.children]
    rotation = cage.matrix_world.to_quaternion().to_matrix().to_4x4()
    obj.matrix_world = Matrix.Translation(obj.matrix_world.translation) @ rotation
    for child, world in kids:
        child.matrix_world = world


def _style_cage(context, cage):
    """Caixa em arame (só referência), texto escondido na vista 3D; o símbolo 2D continua."""
    show = getattr(context.scene.home_builder, 'show_entry_door_and_window_cages', True)
    cage.display_type = 'WIRE'
    cage.show_in_front = False
    cage.hide_set(not show)
    for child in cage.children:
        if child is cage.btm_opening_real.assembly:
            continue
        if child.type == 'FONT' or 'Text' in child.name:      # o texto "DOOR"/"WINDOW"; o símbolo de giro fica
            child.hide_viewport = True


def sync(context, cage, force=False):
    """Monta (ou refaz) a porta ou janela real da caixa; devolve True se montou algo."""
    if not is_opening(cage):
        return False
    data = cage.btm_opening_real
    sig = signature(cage)
    if not force and data.signature == sig and data.assembly is not None and data.assembly.name in bpy.data.objects:
        return False
    kind = kind_of(cage)
    opens, production = _remember(data.assembly)
    clear(cage)
    room_door_leaf.remove_leaves(cage)      # folha cinza da porta de ambiente (005) de arquivos antigos
    collection = cage.users_collection[0] if cage.users_collection else context.scene.collection
    context.view_layer.update()
    built = build.build(_parts(cage, kind), collection)
    for obj in built.values():
        obj.name = "{} {}".format(cage.name.split(".")[0], obj.name)
    _to_world(cage, built.values())
    context.view_layer.update()
    frame_objs = [o for key, o in built.items() if key[0] in (door_core.FRAME, door_core.FRAME_HW)]
    frame = group.create_group(frame_objs, 'FRAME', cage.name.split(".")[0] + " - montagem")
    for obj in frame_objs:
        obj[collision.OPENING_FRAME_PROP] = frame.name     # a folha não esbarra no próprio marco
    _align(frame, cage)
    _parent_keep(frame, cage)
    context.view_layer.update()
    leaves = sorted({key[1] for key in built if key[1] is not None})
    _swing_obj, left, inside, _double = _swing(cage)
    sashes = []
    for index in leaves:
        body = built[(door_core.LEAF, index)]
        sash = group.create_group([body], 'LEAF', "{} - folha {}".format(cage.name.split(".")[0], index + 1))
        hardware = built.get((door_core.LEAF_HW, index))
        if hardware is not None:            # ferragens filhas da folha: o eixo de giro é o canto da folha, não
            _parent_keep(hardware, body)    # o da caixa com as maçanetas (a folha da 003 gira pelo canto da caixa)
        _align(sash, cage)
        _parent_keep(sash, frame)
        sashes.append((index, sash))
    context.view_layer.update()
    for index, sash in sashes:
        if kind == 'WINDOW':
            travel = window_core.travel(_dims(cage)[0])     # até o batente do marco (o marco não é obstáculo)
            leaf.make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X' if index == 0 else 'NEG_X', travel=travel)
            apply._write(sash, 'travel', travel)
        else:
            hinge = ('RIGHT' if left else 'LEFT') if kind == 'DOOR' else ('LEFT' if index == 0 else 'RIGHT')
            sign = 'OUT' if inside or inside is None else 'IN'
            leaf.make_leaf(sash, frame, 'SWING', hinge=hinge, swing_sign=sign, max_angle=SWING_MAX)
        base = sash.name.split(".")[0]
        if base in opens and opens[base] > 0.0:
            sash.btm_aggregate.open_value = opens[base]
        if base in production:
            sash.btm_aggregate.production_part = True
    for obj in [frame] + list(frame.children_recursive):
        obj[PART_PROP] = True
    data.kind = kind
    data.assembly = frame
    data.signature = sig
    data.model_version = props.MODEL_VERSION
    _style_cage(context, cage)
    return True


def sync_each(context, cages, force=False):
    """`sync` em cada caixa; a falha de uma não impede as outras (EC-11). Devolve (montadas, nomes que falharam)."""
    done, failed = 0, []
    for cage in cages:
        try:
            done += bool(sync(context, cage, force=force))
        except Exception as exc:
            print(f"CAFFMob Draw: porta/janela real não montada em {cage.name} ({exc})")
            failed.append(cage.name)
    return done, failed


def openings(scene):
    return [o for o in scene.objects if is_opening(o)]


def outdated(scene):
    """Caixas sem a porta/janela real ou de uma versão anterior do gerador."""
    return [o for o in openings(scene) if o.btm_opening_real.model_version < props.MODEL_VERSION
            or o.btm_opening_real.assembly is None]
