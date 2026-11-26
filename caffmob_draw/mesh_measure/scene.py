"""Leitura da malha medida e estado da janela V-Ray Mesh Measure (027, T010 e T011; RF-02).

A malha é lida **uma vez** na abertura (ou ao recarregar) para uma fotografia em coordenadas de mundo: vértices,
triângulos e as partes soltas (componentes conexos das arestas) com a caixa e as três medidas de cada uma. Nada aqui
altera o objeto do usuário: a janela só lê e desenha.

O alvo é o objeto de malha ativo/selecionado; quando não há seleção, vale o último objeto escolhido pelo conta-gotas
(guardado na cena em `btm_mesh_measure_target`, porque o atributo é do projeto e não da sessão).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import core
from .camera import Camera

TARGET_KEY = "btm_mesh_measure_target"

# Cores estáveis por parte (a mesma parte mantém a cor entre leituras, porque a ordem é a dos vértices).
PALETTE = [
    (0.94, 0.48, 0.16, 1.0), (0.23, 0.51, 0.96, 1.0), (0.06, 0.73, 0.51, 1.0),
    (0.92, 0.70, 0.03, 1.0), (0.55, 0.36, 0.96, 1.0), (0.93, 0.29, 0.60, 1.0),
    (0.20, 0.75, 0.85, 1.0), (0.75, 0.75, 0.35, 1.0),
]


class Part:
    """Parte solta da malha: os vértices, a caixa, as medidas e a cor sólida."""

    def __init__(self, index, name, vertices, lo, hi, color):
        self.index = index
        self.name = name
        self.vertices = list(vertices)
        self.lo = lo
        self.hi = hi
        self.center = core.center(lo, hi)
        self.size_mm = core.size_mm(lo, hi)
        self.color = color
        self.visible = True

    def cycle_color(self):
        """Passa para a próxima cor da paleta (cor sólida da parte, T013)."""
        self.color = PALETTE[(PALETTE.index(self.color) + 1) % len(PALETTE)] if self.color in PALETTE else PALETTE[0]
        return self.color


class Malha:
    """Fotografia da malha em coordenadas de mundo, com os triângulos já separados por parte."""

    def __init__(self, name, vertices, triangles, parts):
        self.name = name
        self.vertices = vertices
        self.triangles = triangles      # [(a, b, c, índice da parte, cor do material)]
        self.parts = parts
        self.bounds = core.bounds(vertices)

    def part(self, index):
        return self.parts[index] if 0 <= index < len(self.parts) else None

    def parts_bounds(self):
        return [(part.lo, part.hi) for part in self.parts]

    def visible_parts(self):
        return [part for part in self.parts if part.visible]

    def vertex_count(self):
        return len(self.vertices)

    def triangle_count(self):
        return len(self.triangles)


def mesh_objects(context):
    """Objetos de malha da cena, em ordem alfabética (para o seletor do painel)."""
    return sorted((obj for obj in context.scene.objects if obj.type == 'MESH'), key=lambda o: o.name)


def selected_mesh(context):
    """Malha ativa (ou a primeira selecionada) na cena, ou None."""
    active = context.active_object
    if active is not None and active.type == 'MESH':
        return active
    return next((obj for obj in context.selected_objects if obj.type == 'MESH'), None)


def target(context):
    """Malha medida: a selecionada; sem seleção, a última escolhida pelo conta-gotas."""
    obj = selected_mesh(context)
    if obj is not None:
        return obj
    name = context.scene.get(TARGET_KEY, "")
    obj = bpy.data.objects.get(name) if name else None
    return obj if obj is not None and obj.type == 'MESH' else None


def set_target(context, name):
    context.scene[TARGET_KEY] = name


def _material_color(obj, index):
    materials = getattr(obj.data, 'materials', None) or []
    if 0 <= index < len(materials) and materials[index] is not None:
        color = getattr(materials[index], 'diffuse_color', None)
        if color is not None:
            return (float(color[0]), float(color[1]), float(color[2]), 1.0)
    return PALETTE[index % len(PALETTE)]


def snapshot(obj):
    """Lê a malha do objeto (coordenadas de mundo, partes soltas e triângulos) sem tocar no objeto."""
    mesh = obj.data
    matrix = obj.matrix_world
    vertices = [tuple(matrix @ vertex.co) for vertex in mesh.vertices]
    edges = [(edge.vertices[0], edge.vertices[1]) for edge in mesh.edges]
    groups = core.connected_parts(len(vertices), edges)
    parts = []
    part_of = {}
    for index, group in enumerate(groups):
        lo, hi = core.bounds([vertices[i] for i in group])
        parts.append(Part(index, tr("Parte {}").format(index + 1), group, lo, hi, PALETTE[index % len(PALETTE)]))
        for vertex_index in group:
            part_of[vertex_index] = index
    triangles = []
    for polygon in mesh.polygons:
        color = _material_color(obj, polygon.material_index)
        indices = list(polygon.vertices)
        for k in range(1, len(indices) - 1):          # polígono vira leque de triângulos
            triangles.append((indices[0], indices[k], indices[k + 1], part_of.get(indices[0], 0), color))
    return Malha(obj.name, vertices, triangles, parts)


class Sessao:
    """Janela aberta: malha, câmera, representação, encaixe, unidades, medidas e views da impressão."""

    def __init__(self, malha):
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None
        self.malha = malha
        self.obj_name = malha.name
        self.camera = Camera()
        self.fitted = False           # a primeira passada de desenho enquadra a malha na área real
        self.representation = 'SOLIDO'
        self.snap_mode = 'AMBOS'
        self.snap_threshold_mm = 20.0
        self.unit = 'MM'
        self.rounded = False
        self.mostrar_medidas = True
        self.hover = None
        self.selected = None
        self.hits = []                # [(retângulo em pixels, parte)] do último desenho
        self.medidas = []             # medidas manuais: {'a': ponto, 'b': ponto}
        self.pending = None           # primeiro ponto da medida em andamento
        self.views = []               # views da impressão: {'name', 'camera', 'size_pct', 'proportion'}
        self.print_preview = False
        self.sheet = 'A3_PAISAGEM'
        self.sheet_zoom = 1.0
        self.rect = (0.0, 0.0, 1.0, 1.0)   # último retângulo desenhado, em pixels

    # Câmera e projeção ------------------------------------------------------------------------------------
    def set_projection(self, projection):
        if projection in core.PROJECTIONS:
            self.camera.projection = projection
        return self.camera.projection

    def fit(self, rect):
        self.camera.fit(self.malha.bounds, rect)
        return self

    # Encaixe nas extremidades -----------------------------------------------------------------------------
    def candidates(self):
        return core.snap_candidates(self.malha.bounds, self.malha.parts_bounds(), self.snap_mode)

    def snap(self, point):
        """Aplica o encaixe configurado; devolve (ponto, encaixou)."""
        if self.snap_mode == 'OFF':
            return tuple(point), False
        return core.snap(point, self.candidates(), self.snap_threshold_mm / 1000.0)

    def nearest_vertex(self, point, threshold_m):
        """Vértice mais próximo dentro do limite (o encaixe solto das medidas manuais)."""
        best, dist = None, float(threshold_m)
        for vertex in self.malha.vertices:
            d = ((vertex[0] - point[0]) ** 2 + (vertex[1] - point[1]) ** 2 + (vertex[2] - point[2]) ** 2) ** 0.5
            if d <= dist:
                best, dist = vertex, d
        return (best, True) if best is not None else (tuple(point), False)

    # Partes e medidas -------------------------------------------------------------------------------------
    def toggle_part(self, index):
        part = self.malha.part(index)
        if part is not None:
            part.visible = not part.visible
        return part.visible if part is not None else False

    def visible_parts(self):
        return self.malha.visible_parts()

    def part_labels(self):
        """Medidas de cada parte visível, como saem na janela e no painel."""
        return [(part, " × ".join(core.format_mm(v, self.unit, self.rounded, suffix=False) for v in part.size_mm))
                for part in self.visible_parts()]

    def add_measure(self, a, b):
        if a is None or b is None:
            return None
        result = core.measure(a, b)
        item = {'a': tuple(a), 'b': tuple(b), 'label': core.measure_label(result, self.unit, self.rounded),
                'distance_mm': result['distance_mm']}
        self.medidas.append(item)
        self.pending = None
        return item

    def clear_measures(self):
        self.medidas.clear()
        self.pending = None

    # Views e impressão ------------------------------------------------------------------------------------
    def create_view(self):
        """Guarda a câmera atual como uma view com badge (V1, V2, ...)."""
        view = {'name': core.view_name(len(self.views)), 'camera': self.camera.state(),
                'size_pct': 100.0, 'proportion': 'LIVRE'}
        self.views.append(view)
        return view

    def layout(self):
        return core.print_layout(self.sheet, self.views)

    def view_camera(self, view):
        """Câmera própria da view (a principal não arrasta as views da impressão)."""
        camera = Camera(**view['camera'])
        camera.projection = self.camera.projection
        return camera


_session = []


def sessao():
    """Janela aberta, ou None."""
    return _session[0] if _session else None


def keep(session):
    _session[:] = [session]
    return session


def forget():
    _session.clear()
