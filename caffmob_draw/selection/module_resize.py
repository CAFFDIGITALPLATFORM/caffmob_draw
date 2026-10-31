"""Transação de edição dimensional de módulo (feature 080, D-03 a D-12; RN-02 a RN-07, RF-01 a RF-04, RF-11).

Um ponto só para o painel, o editor de armário, o Redimensionar e a substituição. Para as 5 famílias (BTM,
FACE_FRAME, CLOSETS, AUTHORED, FRAMELESS):
1. valida o valor físico contra os limites gerais e o parâmetro convertido contra a faixa da propriedade do gerador
   (recusa, nunca corta) e recusa módulo vindo de biblioteca, com override ou com malha compartilhada;
2. guarda o estado (parâmetros, `btm_overrides`, `matrix_basis` da raiz e dos descendentes que o gerador não recria);
3. assa a escala própria da raiz: ±1 por eixo, rotação e posição mantidas;
4. grava as 3 medidas com uma regeneração só;
5. devolve os descendentes não recriados à pose física anterior (e converte o repouso das folhas da raiz);
6. confere a pós-condição (medida física ≤ 0,1 mm por eixo);
7. em qualquer erro, volta tudo e regenera de novo a partir dos parâmetros antigos.

Roda dentro de `guard.reconfigure`, que suspende o guarda sem veto por colisão e aceita a pose nova no fim.
"""

import math

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import N_, tr
from ..target import module_geometry as mg
from . import classify

FAMILIES = ('BTM', 'FACE_FRAME', 'CLOSETS', 'AUTHORED', 'FRAMELESS')
GN_DIM = {'width': 'Dim X', 'depth': 'Dim Y', 'height': 'Dim Z'}
_PROPS = {'BTM': 'btm_cabinet', 'FACE_FRAME': 'face_frame_cabinet', 'CLOSETS': 'hb_closet_starter'}
_UNBOUNDED = 1e30
_FAIL_AFTER_FIRST_WRITE = [False]       # só os ensaios ligam (CA-06: falha depois da 1.ª mutação)


class PostconditionError(mg.ModuleGeometryError):
    """O gerador produziu outra medida (corte, arredondamento, recálculo que falhou em silêncio)."""


def handles(info):
    return info is not None and info.kind == classify.MODULE and info.library in FAMILIES


# Leitura ----------------------------------------------------------------------------------------------------

def _geo(obj):
    from .. import hb_types
    return hb_types.GeoNodeObject(obj)


def read_params(root, family):
    """Parâmetros do gerador (largura, profundidade, altura), em unidades da cena, no referencial da raiz."""
    if family == 'AUTHORED':
        size = root.btm_authored.size_local
        return (size[0] / 1000, size[1] / 1000, size[2] / 1000)
    if family in _PROPS:
        group = getattr(root, _PROPS[family])
        return tuple(float(getattr(group, f)) for f in mg.FIELDS)
    geo = _geo(root)
    values = []
    for index, field in enumerate(mg.FIELDS):
        try:
            value = geo.get_input(GN_DIM[field])
        except Exception:
            value = None
        if value is None:                         # FRAMELESS sem a entrada: a caixa local (dimensions ÷ |própria|)
            own = abs(root.scale[index]) or 1.0
            value = root.dimensions[index] / own
        values.append(float(value))
    return tuple(values)


def measure(root, family):
    """(parâmetros, escala própria com sinal, escala de cada eixo no mundo, medida física)."""
    params = read_params(root, family)
    world = mg.axis_scales(root.matrix_world)
    own = tuple(float(v) for v in root.scale)
    return params, own, world, mg.physical(params, world)


def physical_of(info, field):
    _params, _own, _world, phys = measure(info.root, info.library)
    return phys[mg.AXIS[field]]


def param_range(root, family, field):
    """Faixa da propriedade do gerador (`hard_min/hard_max`), ou None quando não há limite próprio."""
    if family not in _PROPS:
        return None
    prop = type(getattr(root, _PROPS[family])).bl_rna.properties[field]
    low, high = float(prop.hard_min), float(prop.hard_max)
    if abs(low) > _UNBOUNDED and abs(high) > _UNBOUNDED:
        return None
    return (low if abs(low) <= _UNBOUNDED else -math.inf, high if abs(high) <= _UNBOUNDED else math.inf)


def physical_ranges(info, limits):
    """Faixa física de cada eixo para o módulo: o que o painel e o editor mostram e conferem."""
    root, family = info.root, info.library
    _params, own, world, _phys = measure(root, family)
    ancestor = mg.ancestor_scales(world, own)
    return {f: mg.physical_range(limits[f], param_range(root, family, f), ancestor[mg.AXIS[f]])
            for f in mg.FIELDS}


# Validação --------------------------------------------------------------------------------------------------

def _refuse_unsafe(root, family):
    if root.library is not None:
        raise mg.ModuleGeometryError(N_("Este módulo vem de outro arquivo (vinculado): edite no arquivo original."))
    if root.override_library is not None:
        raise mg.ModuleGeometryError(N_("Este módulo é um override de biblioteca: torne-o local antes de editar."))
    if family == 'BTM' and root.type == 'MESH' and root.data is not None and root.data.users > 1:
        raise mg.ModuleGeometryError(N_("A malha deste módulo é compartilhada com outro objeto: torne-a única antes de editar."))


def _validate(root, family, own, world, edits, limits):
    ancestor = mg.ancestor_scales(world, own)
    return {f: mg.check_value(f, v, limits[f], param_range(root, family, f), ancestor[mg.AXIS[f]])
            for f, v in edits.items()}


# Estado e rollback ------------------------------------------------------------------------------------------

def _is_unmanaged(obj, family):
    """Descendente que o gerador não recria nem reposiciona."""
    if family == 'AUTHORED':
        return True
    if 'btm_leaf_base' in obj:                            # pivô de folha
        return True
    for attr, flag in (('btm_division', 'is_division'), ('btm_extra', 'is_extra'),
                       ('btm_aggregate', 'is_aggregate')):
        data = getattr(obj, attr, None)
        if data is not None and getattr(data, flag, False):
            return True
    member = getattr(obj, 'btm_member', None)
    return bool(member is not None and member.uid)


def _root_leaves(root):
    return [o for o in root.children_recursive
            if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF' and o.btm_aggregate.parent_ref == root]


def _top_unmanaged(root, family, skip):
    """Descendentes não recriados mais altos na árvore (os filhos deles seguem junto)."""
    out = []

    def walk(node):
        for child in node.children:
            if child in skip:
                continue
            if _is_unmanaged(child, family):
                out.append(child)
            else:
                walk(child)
    walk(root)
    return out


class _State:
    def __init__(self, root, family, physical_before):
        from ..standards import sync
        self.root, self.family = root, family
        self.physical_before = physical_before
        self.params = read_params(root, family)
        self.basis = root.matrix_basis.copy()
        self.world = root.matrix_world.copy()
        self.overrides = root.get(sync.OVERRIDES_PROP)
        self.leaves = _root_leaves(root)
        skip = set(self.leaves)
        skip.update(p for p in (o.btm_aggregate.pivot for o in self.leaves) if p is not None)
        self.kept = [(o, o.matrix_world.copy(), o.matrix_basis.copy()) for o in _top_unmanaged(root, family, skip)]
        self.leaf_data = [(o, {k: (o[k].to_list() if hasattr(o[k], 'to_list') else o[k])
                               for k in ('btm_leaf_rest', 'btm_leaf_manual_base') if k in o},
                           o.btm_aggregate.travel, o.matrix_world.copy()) for o in self.leaves]
        self.authored = None
        if family == 'AUTHORED':
            from ..aggregates import stretch
            self.authored = stretch.Snapshot(root)

    def restore(self, context):
        from ..standards import sync
        root = self.root
        if self.authored is not None:
            self.authored.restore()
            context.view_layer.update()
            return
        root.matrix_basis = self.basis
        if self.overrides is None:
            if sync.OVERRIDES_PROP in root:
                del root[sync.OVERRIDES_PROP]
        else:
            root[sync.OVERRIDES_PROP] = self.overrides
        _write(context, root, self.family, self.params, mark=False)
        for obj, data, travel, _world in self.leaf_data:
            if not _alive(obj):
                continue
            for key, value in data.items():
                obj[key] = value
            obj.btm_aggregate.travel = travel
        for obj, _world, basis in self.kept:
            if _alive(obj):
                obj.matrix_basis = basis
        context.view_layer.update()
        from ..aggregates import leaf
        for obj, _data, _travel, _world in self.leaf_data:
            if _alive(obj):
                fraction = leaf.current_fraction(obj)
                leaf.rebuild_pivot(obj)
                leaf.apply_fraction(obj, fraction)
        context.view_layer.update()


def _alive(obj):
    try:
        return obj.name in bpy.data.objects and bpy.data.objects[obj.name] == obj
    except ReferenceError:
        return False


# Escrita ----------------------------------------------------------------------------------------------------

def _write(context, root, family, params, mark=True, previous=None):
    """Grava as 3 medidas com uma regeneração só. `mark` registra a medida manual dos campos que mudaram."""
    values = dict(zip(mg.FIELDS, params))
    changed = [f for i, f in enumerate(mg.FIELDS) if previous is None or abs(params[i] - previous[i]) > 1e-12]
    if family == 'BTM':
        from ..data import properties
        cab = root.btm_cabinet
        with properties.suspended_geometry():
            for field, value in values.items():
                setattr(cab, field, value)
        properties.update_cabinet_geom(cab, context)
    elif family == 'FACE_FRAME':
        from ..product_libraries.face_frame import types_face_frame
        with types_face_frame.suspend_recalc():
            for field, value in values.items():
                setattr(root.face_frame_cabinet, field, value)
            _maybe_fail()
    elif family == 'CLOSETS':
        from ..product_libraries.closets import props_closets, types_closets
        from ..standards import sync
        starter = root.hb_closet_starter
        types_closets._RECALCULATING.add(id(root))
        try:
            for field, value in values.items():
                setattr(starter, field, value)
        finally:
            types_closets._RECALCULATING.discard(id(root))
        if mark:
            # O mesmo critério do callback do starter: altura e profundidade diferentes do padrão da cena.
            for field in ('height', 'depth'):
                default = props_closets._scene_default(starter, field, context.scene)
                if field in changed and default is not None and abs(values[field] - default) > 1e-9:
                    sync.add_override(root, field)
        _maybe_fail()
        types_closets.recalculate_closet_starter(root)
    elif family == 'FRAMELESS':
        from .. import hb_utils
        from ..standards import sync
        geo = _geo(root)
        for field, value in values.items():
            geo.set_input(GN_DIM[field], value)
            if mark and field in changed:
                sync.add_override(root, GN_DIM[field])
        _maybe_fail()
        hb_utils.run_calc_fix(context, root)
    else:
        raise mg.ModuleGeometryError(N_("Família de módulo sem edição de medidas."))
    if family == 'BTM':
        _maybe_fail()


def _maybe_fail():
    if _FAIL_AFTER_FIRST_WRITE[0]:
        raise RuntimeError("falha injetada pelo ensaio (080 CA-06)")


def _bake(context, state, signs):
    """Escala própria da raiz → ±1; os descendentes não recriados guardam o `matrix_world`; as folhas da raiz têm o
    repouso, a base manual e o curso convertidos para o referencial novo."""
    root = state.root
    root.scale = signs
    context.view_layer.update()
    convert = root.matrix_world.inverted_safe() @ state.world          # referencial velho → novo, só escala
    from ..aggregates import leaf
    for obj, data, travel, _world in state.leaf_data:
        front = leaf.front_frame(root)
        canon = front.inverted() @ convert @ front
        if 'btm_leaf_rest' in data:
            obj['btm_leaf_rest'] = [v for row in (canon @ leaf._matrix(data['btm_leaf_rest'])) for v in row]
        if 'btm_leaf_manual_base' in data:
            obj['btm_leaf_manual_base'] = list(canon @ Vector(data['btm_leaf_manual_base']))
        agg = obj.btm_aggregate
        if agg.motion in ('SLIDE', 'DRAWER'):
            direction = Vector((1.0, 0.0, 0.0)) if agg.motion == 'SLIDE' else Vector((0.0, 1.0, 0.0))
            agg.travel = travel * (canon.to_3x3() @ direction).length


def _rekeep(context, state):
    """Depois da regeneração: os não recriados voltam à pose física guardada, do mais alto para o mais baixo."""
    context.view_layer.update()
    for obj, world, _basis in state.kept:
        if _alive(obj):
            parent_world = obj.parent.matrix_world if obj.parent is not None else Matrix.Identity(4)
            obj.matrix_basis = (parent_world @ obj.matrix_parent_inverse).inverted_safe() @ world
    context.view_layer.update()
    from ..aggregates import leaf
    for obj, _data, _travel, _world in state.leaf_data:
        if _alive(obj):
            fraction = leaf.current_fraction(obj)
            leaf.rebuild_pivot(obj)
            leaf.apply_fraction(obj, fraction)
    context.view_layer.update()


def _apply_authored(context, state, plan):
    from ..aggregates import stretch
    root = state.root
    if any(abs(float(s) - sign) > 1e-9 for s, sign in zip(root.scale, plan.scale)):
        _bake(context, state, plan.scale)
        # Sem escala própria, a caixa local passa a valer a medida física ÷ ancestrais: o tamanho guardado acompanha
        # antes de as regras de estiramento rodarem (elas partem da caixa medida dos membros).
        _params, own, world, phys = measure(root, 'AUTHORED')
        ancestor = mg.ancestor_scales(world, own)
        root.btm_authored.size_local = tuple(state_phys / a * 1000 for state_phys, a in
                                             zip(state.physical_before, ancestor))
        _rekeep(context, state)
        _maybe_fail()
    stretch.resize(context, root, [p * 1000 for p in plan.params])


def _postcondition(state, plan):
    root, family = state.root, state.family
    _params, own, _world, phys = measure(root, family)
    for i, field in enumerate(mg.FIELDS):
        if abs(phys[i] - plan.physical[i]) > mg.TOLERANCE:
            raise PostconditionError(N_("O gerador não produziu a medida pedida; nada foi alterado."))
    if any(abs(o - s) > 1e-6 for o, s in zip(own, plan.scale)):
        raise PostconditionError(N_("A escala do módulo não foi assada; nada foi alterado."))


def apply_physical(context, info, edits, limits):
    """Aplica `edits` ({campo: medida física}) ao módulo `info` numa transação. Devolve o `BakePlan`."""
    if not handles(info):
        raise mg.ModuleGeometryError(N_("Família de módulo sem edição de medidas."))
    root, family = info.root, info.library
    _refuse_unsafe(root, family)
    params, own, world, phys = measure(root, family)
    edits = _validate(root, family, own, world, edits, limits)
    plan = mg.bake_plan(params, own, world, edits)
    if not plan.changed:
        return plan
    state = _State(root, family, phys)

    def apply():
        if family == 'AUTHORED':
            _apply_authored(context, state, plan)
        else:
            if any(abs(float(s) - sign) > 1e-9 for s, sign in zip(root.scale, plan.scale)):
                _bake(context, state, plan.scale)
            _write(context, root, family, plan.params, previous=params)
            _rekeep(context, state)
        context.view_layer.update()
        _postcondition(state, plan)

    def restore():
        state.restore(context)

    from ..collision import guard
    guard.reconfigure(root, apply, restore)
    from ..target import snapshot
    # A 3x3 mudou: o snapshot é refeito com a pose nova, para a próxima edição não ser recusada por "mudou de
    # posição" e o painel ler a medida nova logo em seguida (D-12).
    snapshot.forget()
    try:
        snapshot.refresh(context)
    except (AttributeError, ReferenceError):
        pass
    return plan


def describe_refusal(info, field, exc):
    """Mensagem da recusa com alvo, campo, valor e faixa física (RF-04)."""
    from ..data import units
    from .editing import DIM_LABELS
    if isinstance(exc, mg.PhysicalRangeError):
        unit = units.get_scene_length_unit()
        return tr("Valor Inválido: {} de {} deve estar entre {} e {} (recebido: {}).").format(
            tr(DIM_LABELS[exc.field]), info.root.name, units.format_length(exc.low, unit),
            units.format_length(exc.high, unit), units.format_length(exc.value, unit))
    return tr("Valor Inválido: {} de {}: {}").format(tr(DIM_LABELS[field]), info.root.name, tr(str(exc)))
