"""Leitura e escrita de dimensões por tipo de objeto (T015; RN-03, D-10).

Cada biblioteca guarda as medidas num lugar diferente:
- frameless: inputs `Dim X/Y/Z` da raiz (via `compat`), registrando medida manual (`btm_overrides`, 001 RN-23);
- face frame: `root.face_frame_cabinet.width/height/depth` (o `update` recalcula o gabinete);
- closets: `root.hb_closet_starter.width/height/depth`;
- módulo rápido: `root.btm_cabinet.width/height/depth`;
- porta e janela de ambiente (Home Builder 5): inputs `Dim X` (largura) e `Dim Z` (altura); peitoril = `location.z`;
- parede (Home Builder 5): inputs `Length`, `Height`, `End Height`, `Thickness`, com recálculo das esquadrias.

Valores fora do domínio levantam `ValueError("Valor Inválido: …")` sem alterar nada.
"""

from ..data.i18n import N_, tr
from .. import hb_types
from ..data import units
from . import classify

DIM_FIELDS = ('width', 'height', 'depth')
DIM_LABELS = {'width': N_("Largura"), 'height': N_("Altura"), 'depth': N_("Profundidade")}
GN_DIM = {'width': 'Dim X', 'depth': 'Dim Y', 'height': 'Dim Z'}
WALL_FIELDS = {'length': ('Length', N_("Comprimento")), 'height': ('Height', N_("Pé-direito inicial")),
               'end_height': ('End Height', N_("Pé-direito final")), 'thickness': ('Thickness', N_("Espessura"))}
LIMITS = {'width': (0.01, 10.0), 'height': (0.01, 10.0), 'depth': (0.005, 10.0),
          'length': (0.05, 100.0), 'end_height': (0.5, 10.0), 'thickness': (0.01, 2.0), 'sill': (0.0, 5.0)}
WALL_LIMITS = {'height': (0.5, 10.0)}


def _check(field, value, label, limits=None):
    lo, hi = (limits or LIMITS)[field]
    if not lo <= value <= hi:
        unit = units.get_scene_length_unit()
        raise ValueError(tr("Valor Inválido: {} deve estar entre {} e {} (recebido: {}).").format(tr(label), units.format_length(lo, unit), units.format_length(hi, unit), units.format_length(value, unit)))


def _geo(obj):
    return hb_types.GeoNodeObject(obj)


def has_dimensions(info):
    return info is not None and info.kind in (classify.MODULE, classify.ROOM_DOOR, classify.WINDOW,
                                              classify.GEOMETRY, classify.OBSTACLE)


def editable_dimensions(info):
    """Campos de dimensão editáveis para o tipo (obstáculos e objetos sem fonte conhecida são só leitura)."""
    if info is None:
        return ()
    if info.kind == classify.MODULE:
        return DIM_FIELDS
    if info.kind in (classify.ROOM_DOOR, classify.WINDOW) and info.library == 'HB':
        return ('width', 'height')
    return ()


def _mobi_dimension(info, field):
    """Abertura do CAFF MOBI (067 onda 8, D-41): a raiz é um Empty, sem medida própria; vale o documento (mm). A
    profundidade é a das peças, que a montagem fez com a espessura do trecho."""
    import json
    obj = info.obj
    if field == 'depth':
        return max((c.dimensions.y for c in obj.children), default=0.0)
    try:
        entidade = json.loads(obj.get('caffmob_abertura') or obj.get('caffmob_entidade_v2') or '{}')
    except ValueError:
        entidade = {}
    return entidade.get({'width': 'largura', 'height': 'altura'}[field], 0) / 1000


def _module_family(info):
    """Módulo das 5 famílias (080 D-01): a medida é física, pelo `module_geometry`; frente e chapa mostram a do
    módulo dono, como antes."""
    from . import module_resize
    return (info.kind in (classify.MODULE, classify.FRONT, classify.PART) and info.root is not None
            and info.library in module_resize.FAMILIES)


def get_dimension(info, field):
    if info.library == 'MOBI' and info.kind in (classify.ROOM_DOOR, classify.WINDOW):
        return _mobi_dimension(info, field)
    if _module_family(info):
        from . import module_resize
        return module_resize.physical_of(info, field)
    obj = info.root if info.kind in (classify.MODULE, classify.FRONT, classify.PART) else info.obj
    library = info.library
    if library == 'AUTHORED':
        return obj.btm_authored.size_local[{'width': 0, 'depth': 1, 'height': 2}[field]] / 1000
    if info.kind == classify.MODULE or info.kind in (classify.FRONT, classify.PART):
        if library == 'FACE_FRAME' and getattr(obj, 'face_frame_cabinet', None) is not None:
            return getattr(obj.face_frame_cabinet, field)
        if library == 'CLOSETS' and getattr(obj, 'hb_closet_starter', None) is not None:
            return getattr(obj.hb_closet_starter, field)
        if library == 'BTM' and getattr(obj, 'btm_cabinet', None) is not None:
            return getattr(obj.btm_cabinet, field)
    if getattr(obj, 'home_builder', None) is not None and obj.home_builder.mod_name and field in GN_DIM:
        try:
            value = _geo(obj).get_input(GN_DIM[field])
        except Exception:
            value = None
        if value is not None:
            return _door_leaf(info, field, value, to_hole=False)
    d = obj.dimensions
    return {'width': d.x, 'depth': d.y, 'height': d.z}[field]


def set_dimension(context, info, field, value):
    from . import module_resize
    if module_resize.handles(info):
        return set_dimensions(context, info, {field: value})
    if info.library == 'AUTHORED':
        _check(field, value, DIM_LABELS[field])
        from ..aggregates import stretch
        size = list(info.root.btm_authored.size_local)
        size[{'width': 0, 'depth': 1, 'height': 2}[field]] = value * 1000
        return stretch.resize(context, info.root, size)
    # 066 RF-012: os parâmetros também crescem sem mudar a matriz; não basta vigiar transformações.
    if field not in editable_dimensions(info):
        return _set_dimension(context, info, field, value)
    _check(field, value, DIM_LABELS[field])
    from ..collision import guard
    obj = info.root if info.kind == classify.MODULE else info.obj
    old = get_dimension(info, field)
    overrides = obj.get('btm_overrides')

    def restore():
        _set_dimension(context, info, field, old)
        if overrides is None:
            if 'btm_overrides' in obj:
                del obj['btm_overrides']
        else:
            obj['btm_overrides'] = overrides

    return guard.reconfigure(obj, lambda: _set_dimension(context, info, field, value), restore)


def set_dimensions(context, info, edits):
    """080 D-04: as medidas físicas do módulo numa transação só (painel, editor, Redimensionar, substituição).
    A recusa diz alvo, campo, valor e faixa física, e nada muda."""
    from . import module_resize
    from ..target import module_geometry as mg
    try:
        return module_resize.apply_physical(context, info, dict(edits), LIMITS)
    except mg.ModuleGeometryError as exc:
        field = getattr(exc, 'field', None) or next(iter(edits))
        raise ValueError(module_resize.describe_refusal(info, field, exc)) from None


def physical_limits(info):
    """Faixa física de cada eixo do módulo (limites gerais × faixa do gerador convertida)."""
    from . import module_resize
    return module_resize.physical_ranges(info, LIMITS)


def _set_dimension(context, info, field, value):
    if field not in editable_dimensions(info):
        raise ValueError(tr("Valor Inválido: {} não é editável para este objeto.").format(tr(DIM_LABELS[field])))
    _check(field, value, DIM_LABELS[field])
    obj = info.root if info.kind == classify.MODULE else info.obj
    if info.kind == classify.MODULE and info.library == 'FACE_FRAME':
        setattr(obj.face_frame_cabinet, field, value)
    elif info.kind == classify.MODULE and info.library == 'CLOSETS':
        setattr(obj.hb_closet_starter, field, value)
    elif info.kind == classify.MODULE and info.library == 'BTM':
        setattr(obj.btm_cabinet, field, value)
    elif _is_hb_opening(info):
        # Porta/janela HB: o mesmo caminho do Redimensionar (questions.md, perguntas 20 e 69): a medida é a da
        # folha, a caixa ganha marco e folga, e a porta real é refeita.
        from ..operators import doors_windows as dw
        _geo(obj).set_input(GN_DIM[field], _door_leaf(info, field, value, to_hole=True))
        dw._sync_opening(context, obj)
    else:
        _geo(obj).set_input(GN_DIM[field], value)
        if info.kind == classify.MODULE:
            from ..standards import sync
            sync.add_override(obj, GN_DIM[field])
            from .. import hb_utils
            hb_utils.run_calc_fix(context, obj)


def _is_hb_opening(info):
    return info.kind in (classify.ROOM_DOOR, classify.WINDOW) and info.library == 'HB'


def _door_leaf(info, field, value, to_hole):
    """Porta HB: medida da caixa ↔ da folha (largura em X, altura em Z); janela e demais: a própria medida."""
    if info.kind != classify.ROOM_DOOR or info.library != 'HB' or field not in ('width', 'height'):
        return value
    from ..operators import doors_windows as dw
    from . import element_size
    axis = 'X' if field == 'width' else 'Z'
    convert = dw._leaf_to_hole if to_hole else dw._hole_to_leaf
    return convert(element_size._door_kind(info.obj), axis, value)


# Peitoril (porta/janela de ambiente) ------------------------------------------------------------------------

def get_sill(info):
    return info.obj.location.z


def set_sill(info, value):
    if info.kind == classify.ROOM_DOOR:
        raise ValueError(tr("Valor Inválido: o peitoril de uma porta é sempre 0."))
    _check('sill', value, "Peitoril")
    info.obj.location.z = value


# Parede -----------------------------------------------------------------------------------------------------

def get_wall(info, field):
    return hb_types.GeoNodeWall(info.obj).get_input(WALL_FIELDS[field][0])


def set_wall(info, field, value):
    if info.library != 'HB':
        raise ValueError(tr("Valor Inválido: esta parede não é editável por aqui."))
    gn_name, label = WALL_FIELDS[field]
    _check(field, value, label, {**LIMITS, **WALL_LIMITS})
    wall = hb_types.GeoNodeWall(info.obj)
    wall.set_input(gn_name, value)
    if field == 'height':
        # Pé-direito final acompanha o inicial (RN-18).
        wall.set_input('End Height', value)
    from ..operators import walls
    walls.update_all_wall_miters()
