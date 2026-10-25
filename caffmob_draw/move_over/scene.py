"""Camada de cena do "Mover Sobre" (T017; D-16, RN-05, RN-08, RN-09, RN-11).

- A (arrastado) e B (referência) são as raízes devolvidas pelo classificador (frente e peça contam como o módulo).
- As caixas são calculadas no referencial de B (posição e rotação de B, sem escala); A assume a rotação de B antes do
  alinhamento (RN-08). Todas as bibliotecas e o módulo rápido têm a frente em −Y e o fundo em Y ≈ 0; uma parede como B
  tem a face da frente em Y = 0 (os módulos ficam do lado −Y).
- Se B está numa parede, A passa a ser filho dessa parede (mantendo a posição no mundo), para as cotas continuarem
  valendo. `restore()` devolve pai e posição originais.
- 067 (onda 6, D-24; RF-121 a RF-125): a orientação de A no referencial de B é um quaternion (`orientation`), e o
  giro é em torno de um pivô escolhido entre os cantos e o centro da caixa local de A (`pivot`), pelo eixo da vista
  (planta: vertical; frontal: profundidade), com `M = T(P)·R(N,θ)·T(−P)·M0` (`rotation.rotate_about`). Escolher o
  pivô ou a âncora não move nada. `rotation` (graus em Z) continua valendo para quem já usava, pelo centro da base.
"""


from mathutils import Matrix, Vector  # type: ignore

from ..aggregates import group
from ..data.i18n import tr
from ..selection import classify
from . import align, reposition
from . import rotation as rot


def _frame(obj):
    loc, rot, _scale = obj.matrix_world.decompose()
    return Matrix.LocRotScale(loc, rot, None)


def tree_corners(obj, depsgraph):
    """Cantos (mundo) da árvore de malhas visíveis do objeto: frentes e puxadores contam, como no Substituir
    (questions.md, pergunta 16). Parede usa a própria caixa; item grudado num filho tem a caixa dele; peça vazia
    (tampo ou avental desligados, caixa num ponto só) não conta."""
    corners, stack = [], [obj]
    while stack and not obj.get('IS_WALL_BP'):
        node = stack.pop()
        if group.is_body(node) and not node.hide_get() and node.display_type not in {'WIRE', 'BOUNDS'}:
            local = [Vector(c) for c in node.evaluated_get(depsgraph).bound_box]
            if (local[6] - local[0]).length > 1e-9:          # diagonal da caixa (canto mín. → máx.)
                corners += [node.matrix_world @ c for c in local]
        stack += [c for c in node.children if not getattr(getattr(c, 'btm_stick', None), 'is_stuck', False)]
    return corners or [obj.matrix_world @ c for c in group.object_corners(obj, depsgraph)]


def _box(corners):
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def _local_box(obj, depsgraph):
    """Caixa da árvore visível do objeto no seu espaço (posição e rotação), já com a escala do objeto."""
    to_frame = _frame(obj).inverted()
    return _box([to_frame @ c for c in tree_corners(obj, depsgraph)])


def _wall_of(obj):
    parent = obj.parent
    return parent if parent is not None and parent.get('IS_WALL_BP') else None


class MoveOver:
    def __init__(self, context, obj_a, obj_b):
        self.context = context
        self.a = classify.movable_root(obj_a)
        self.b = classify.reference_root(obj_b)
        if self.a is None or self.b is None or self.a == self.b:
            raise ValueError(tr("Esses objetos não podem ser usados no Mover Sobre."))
        info_b = classify.classify(self.b)
        self.b_is_wall = info_b.kind == classify.WALL
        self.original_parent = self.a.parent
        self.original_matrix = self.a.matrix_world.copy()
        self.original_parent_inverse = self.a.matrix_parent_inverse.copy()
        depsgraph = context.evaluated_depsgraph_get()
        self.b_frame = _frame(self.b)
        self.b_frame_inv = self.b_frame.inverted()
        self.box_b = _local_box(self.b, depsgraph)
        self.a_local_box = _local_box(self.a, depsgraph)
        _loc, _rot, self.a_scale = self.a.matrix_world.decompose()
        self.origin_in_b = self.b_frame_inv @ self.original_matrix.translation
        self.delta = Vector((0.0, 0.0, 0.0))
        self.orientation = rot.IDENTITY        # quaternion de A no referencial de B (067 D-24)
        self.pivot = 'BASE_CENTER'             # pivô do giro (ponto local de A)
        self.anchor = 'C000'                   # âncora das coordenadas (ponto local de A)

    # Orientação, pivô e âncora (067 onda 6) -------------------------------------------------------------
    @property
    def rotation(self):
        """Graus em torno do vertical (o campo Rotação e as posições salvas antigas)."""
        return rot.angle_about(self.orientation, 'Z') % 360.0

    @rotation.setter
    def rotation(self, degrees):
        self.set_axis_angle('plan', degrees, pivot='BASE_CENTER', preview=False)

    def origin(self):
        return tuple(self.origin_in_b + self.delta)

    def _set_origin(self, origin):
        self.delta = Vector(origin) - self.origin_in_b

    def point_local(self, key):
        return rot.local_point(self.a_local_box, key)

    def point_in_b(self, key):
        return rot.world_point(self.origin(), self.orientation, self.point_local(key))

    def set_pivot(self, key):
        rot.local_point(self.a_local_box, key)                 # valida; nada se move (RF-121)
        self.pivot = key

    def set_anchor(self, key):
        rot.local_point(self.a_local_box, key)
        self.anchor = key

    def rotate(self, view, degrees, pivot=None, preview=True):
        """Gira `degrees` no eixo da vista em torno do pivô (que fica parado)."""
        origin, self.orientation = rot.rotate_about(self.origin(), self.orientation,
                                                    self.point_local(pivot or self.pivot),
                                                    rot.AXES[rot.VIEW_AXIS[view]], degrees)
        self._set_origin(origin)
        if preview:
            self.preview()

    def set_axis_angle(self, view, degrees, pivot=None, preview=True):
        """Leva o giro no eixo da vista ao ângulo `degrees` (o campo de ângulo da vista)."""
        current = rot.angle_about(self.orientation, rot.VIEW_AXIS[view])
        self.rotate(view, float(degrees) - current, pivot, preview)

    def set_orientation(self, orientation, preview=True):
        """Orientação absoluta, com o pivô parado (posições salvas, reset, histórico)."""
        pivot_point = self.point_in_b(self.pivot)
        self.orientation = rot.normalize(tuple(orientation))
        local = rot.rotate_vector(self.orientation, self.point_local(self.pivot))
        self._set_origin(rot.sub(pivot_point, local))
        if preview:
            self.preview()

    def state(self):
        """Instantâneo para o histórico local do diálogo (RF-127)."""
        return (tuple(self.delta), tuple(self.orientation), self.pivot, self.anchor)

    def set_state(self, state, preview=True):
        delta, orientation, self.pivot, self.anchor = state
        self.delta = Vector(delta)
        self.orientation = tuple(orientation)
        if preview:
            self.preview()

    def anchor_coords(self, relative=True):
        """Coordenadas da âncora: relativas a B (`Rb⁻¹(world(pA) − world(pB))`) ou absolutas no projeto."""
        local = Vector(self.point_in_b(self.anchor))
        if relative:
            return tuple(local - Vector(self.box_b[0]))
        return tuple(self.b_frame @ local)

    # Caixas ---------------------------------------------------------------------------------------------
    def _unrotated_box(self, delta=None):
        d = self.delta if delta is None else Vector(delta)
        offset = self.origin_in_b + d
        lo, hi = self.a_local_box
        return (tuple(lo[i] + offset[i] for i in range(3)), tuple(hi[i] + offset[i] for i in range(3)))

    def box_a(self, delta=None):
        """Caixa de A no referencial de B, com a rotação de B, a orientação pedida e o deslocamento atual."""
        if self.orientation == rot.IDENTITY:
            return self._unrotated_box(delta)
        d = self.delta if delta is None else Vector(delta)
        origin = tuple(self.origin_in_b + d)
        lo, hi = self.a_local_box
        corners = [rot.world_point(origin, self.orientation, (x, y, z))
                   for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        return _box(corners)

    def original_box_a(self):
        """Caixa de A como está antes de mexer (rotação original), no referencial de B — para a tela inicial."""
        depsgraph = self.context.evaluated_depsgraph_get()
        to_original = self.original_matrix @ self.a.matrix_world.inverted_safe()     # A pode já estar em prévia
        return _box([self.b_frame_inv @ (to_original @ c) for c in tree_corners(self.a, depsgraph)])

    # Alinhar --------------------------------------------------------------------------------------------
    def align_to(self, targets):
        """Aplica os alvos (lista de `align.Target`) sobre a posição atual; devolve o novo deslocamento."""
        step = align.combine(targets, self.box_a(), self.box_b, self.b_is_wall)
        for i in range(3):
            if step[i]:
                self.delta[i] += step[i]
        self.preview()
        return tuple(self.delta)

    def set_gap(self, axis, value):
        """Define a distância de A a B num eixo (0 = X, 1 = profundidade, 2 = altura), como nos campos da janela."""
        box_a, box_b = self.box_a(), self.box_b
        if axis == 0:
            # Mantém o lado em que A está: à direita de B se o centro de A estiver à direita.
            if (box_a[0][0] + box_a[1][0]) >= (box_b[0][0] + box_b[1][0]):
                self.delta[0] += (box_b[1][0] + value) - box_a[0][0]
            else:
                self.delta[0] += (box_b[0][0] - value) - box_a[1][0]
        elif axis == 1:
            self.delta[1] += (box_b[0][1] + value) - box_a[0][1]
        else:
            self.delta[2] += (box_b[0][2] + value) - box_a[0][2]
        self.preview()

    def gaps(self):
        return align.gaps(self.box_a(), self.box_b)

    def set_min(self, point):
        """Põe o canto mínimo de A em `point` (referencial de B), como a janela Encostar (BUG-20261022-RQR5)."""
        lo = self.box_a()[0]
        for i in range(3):
            self.delta[i] += point[i] - lo[i]
        self.preview()

    # Cena -----------------------------------------------------------------------------------------------
    def _target_matrix(self):
        from mathutils import Quaternion  # type: ignore
        loc = self.b_frame @ (self.origin_in_b + self.delta)
        _l, b_rot, _s = self.b_frame.decompose()
        return Matrix.LocRotScale(loc, b_rot @ Quaternion(self.orientation), self.a_scale)

    # Reposicionar (feature 003, RF-22 a RF-26) --------------------------------------------------------------
    def set_rotation(self, degrees):
        """Rotação em Z pelo centro da base (feature 003); o pivô escolhido fica como estava."""
        self.set_axis_angle('plan', float(degrees) % 360.0, pivot='BASE_CENTER')

    def nudge(self, delta):
        for i in range(3):
            self.delta[i] += delta[i]
        self.preview()

    def world_min(self):
        """Canto mínimo de A no projeto (valores absolutos, só exibição)."""
        return tuple(self.b_frame @ Vector(self.box_a()[0]))

    def set_world(self, axis, value):
        """Move A para o canto mínimo dele ficar em `value` no eixo `axis` do projeto (modo absoluto)."""
        current = Vector(self.world_min())
        target = current.copy()
        target[axis] = value
        self.delta += self.b_frame_inv.to_3x3() @ (target - current)
        self.preview()

    def saved(self):
        data = reposition.save_position(self.box_a(), self.box_b, self.rotation)
        data.update(orientation=tuple(self.orientation), pivot=self.pivot, anchor=self.anchor)   # 067 RF-127
        return data

    def apply_saved(self, saved):
        if saved.get('orientation') and any(saved['orientation']):
            self.pivot = saved.get('pivot') or self.pivot
            self.anchor = saved.get('anchor') or self.anchor
            self.set_orientation(saved['orientation'], preview=False)
        else:
            self.set_axis_angle('plan', float(saved['rotation']) % 360.0, pivot='BASE_CENTER', preview=False)
        step = reposition.apply_position(saved, self.box_a(), self.box_b)
        for i in range(3):
            self.delta[i] += step[i]
        self.preview()

    def preview(self):
        wall = _wall_of(self.b) if not self.b_is_wall else self.b
        if wall is not None and self.a.parent != wall:
            self.a.parent = wall
            self.a.matrix_parent_inverse = Matrix.Identity(4)
        self.a.matrix_world = self._target_matrix()

    def restore(self):
        self.a.parent = self.original_parent
        self.a.matrix_parent_inverse = self.original_parent_inverse
        self.a.matrix_world = self.original_matrix

    def overlapping(self):
        """Objetos que A penetraria na posição atual: o coletor do guarda de colisão (feature 066, D-08), com
        qualquer corpo físico como obstáculo (RF-002), não só módulos."""
        from ..collision import guard
        return guard.overlapping(self.a, self._target_matrix())
