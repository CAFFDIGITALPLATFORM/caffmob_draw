"""Edição da chapa pelo painel (feature 067, D-06, D-12; RF-007, RF-008, RN-05).

- Peça autoral (membro de armário autoral ou peça solta de armário autoral): os vértices do lado positivo do eixo
  semântico andam pela diferença e a face oposta fica parada. Sem modificador e sem `stretch.resize`: só esta peça
  muda, nunca irmãos nem o envelope do armário. Malha compartilhada vira cópia própria antes; dado linked é recusado.
  Se algo falhar no meio, a malha volta pela cópia.
- Geometria livre: a medida vai ao `btm_geometry` (largura, profundidade, altura ou espessura, pelo plano) e a malha
  é refeita pelo gerador dela.
- Peça de módulo de biblioteca: recusada com o motivo e a ação "Adotar como autoral" (D-06).

O passo de Desfazer é o da edição do campo no painel (o mesmo sistema de memória do Ctrl+Z, T007).
"""

from ..data.i18n import tr
from . import part_geometry


class PartEditError(ValueError):
    """Edição recusada (mensagem pronta para o usuário)."""


def _check_editable(obj):
    if obj.library is not None or obj.override_library is not None:
        raise PartEditError(tr("A peça vem de outro arquivo (linked): edite no arquivo de origem."))
    if obj.data is not None and obj.data.library is not None:
        raise PartEditError(tr("A malha da peça vem de outro arquivo (linked): edite no arquivo de origem."))


def _own_mesh(obj):
    """Malha compartilhada com irmãos vira cópia só desta peça (RF-008)."""
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    return obj.data


def _axis_extent(mesh, axis):
    values = [v.co[axis] for v in mesh.vertices]
    return min(values), max(values)


def resize_authored(obj, axis, length):
    """Leva a medida da peça no eixo local `axis` a `length` (unidades da cena, já com a escala acumulada)."""
    _check_editable(obj)
    length = part_geometry.validate_length(length)
    _units, scales = part_geometry.scale_axes(obj.matrix_world)
    mesh = _own_mesh(obj)
    if not mesh.vertices:
        raise PartEditError(tr("A peça não tem malha para editar."))
    low, high = _axis_extent(mesh, axis)
    target_local = length / scales[axis]
    delta = target_local - (high - low)
    if abs(delta) < 1e-9:
        return False
    middle = (low + high) / 2.0
    backup = [v.co.copy() for v in mesh.vertices]
    try:
        for vertex in mesh.vertices:
            if vertex.co[axis] > middle:
                vertex.co[axis] += delta
        mesh.update()
    except Exception:
        for vertex, co in zip(mesh.vertices, backup):
            vertex.co = co
        mesh.update()
        raise
    return True


# Placa: eixo local → campo do `btm_geometry` (o eixo da espessura recebe `thickness`, `geometry_free/mesh.size`).
_PLATE_AXES = {'XY': ('width', 'depth', 'thickness'), 'XZ': ('width', 'thickness', 'height'),
               'YZ': ('thickness', 'depth', 'height')}
_BOX_AXES = ('width', 'depth', 'height')


def geometry_field(geometry, axis):
    if geometry.kind == 'PLACA':
        return _PLATE_AXES.get(geometry.plane, _PLATE_AXES['YZ'])[axis]
    return _BOX_AXES[axis]


def resize_geometry(obj, axis, length):
    """Geometria livre: grava a medida no campo do eixo e deixa o gerador refazer a malha."""
    _check_editable(obj)
    length = part_geometry.validate_length(length)
    _units, scales = part_geometry.scale_axes(obj.matrix_world)
    name = geometry_field(obj.btm_geometry, axis)
    setattr(obj.btm_geometry, name, length / scales[axis])
    from ..geometry_free import mesh
    mesh.update(obj)
    return True


def resize(target, obj, field, length):
    """Edita a medida `field` ('part_a', 'part_b' ou 'part_thickness') do alvo; recusa peça de biblioteca."""
    from . import resolver as r
    if target.measures is None:
        raise PartEditError(tr(target.measure_error) if target.measure_error else tr("Medida da peça indisponível."))
    index = {'part_a': 0, 'part_b': 1}.get(field)
    axis = target.measures.thickness.axis if index is None else target.measures.face[index].axis
    if target.kind == r.GEOMETRY:
        return resize_geometry(obj, axis, length)
    if target.kind == r.MEMBER or (target.kind == r.PART and target.detail == 'AUTHORED'):
        return resize_authored(obj, axis, length)
    raise PartEditError(tr("Esta peça é gerada pelo módulo: {}").format(target.owner_name)
                        + " " + tr("Para editá-la, adote o módulo como armário autoral."))

