"""Câmera orbital da janela V-Ray Mesh Measure (027, T012; RF-02). Python puro, sem `bpy`.

Uma `Camera` olha para um alvo e gira em volta dele (yaw/pitch), aproxima e desloca no plano da tela. `project` leva um
ponto do mundo (metros) a um pixel do retângulo de desenho, em perspectiva ou em ortográfica — é o que permite desenhar
o mesmo objeto em janela cheia, nas views e na folha de impressão sem depender do Blender.
"""

import math

WORLD_UP = (0.0, 0.0, 1.0)
PITCH_LIMIT = 89.0


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _normalize(a):
    length = math.sqrt(_dot(a, a))
    return (a[0] / length, a[1] / length, a[2] / length) if length > 1e-12 else (0.0, 0.0, 1.0)


class Camera:
    """Câmera orbital: alvo, giro em volta dele, distância, abertura e projeção."""

    def __init__(self, target=(0.0, 0.0, 0.0), yaw=-45.0, pitch=25.0, distance=3.0, projection='PERSP',
                 fov=35.0, ortho_scale=2.0):
        self.target = tuple(float(v) for v in target)
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.distance = float(distance)
        self.projection = projection if projection in ('PERSP', 'ORTHO') else 'PERSP'
        self.fov = float(fov)
        self.ortho_scale = float(ortho_scale)

    # Estado ------------------------------------------------------------------------------------------------
    def state(self):
        """Instantâneo da câmera (para as views da impressão não acompanharem a câmera principal)."""
        return {'target': self.target, 'yaw': self.yaw, 'pitch': self.pitch, 'distance': self.distance,
                'projection': self.projection, 'fov': self.fov, 'ortho_scale': self.ortho_scale}

    def copy(self, **changes):
        camera = Camera(**self.state())
        for key, value in changes.items():
            setattr(camera, key, value)
        return camera

    # Geometria ---------------------------------------------------------------------------------------------
    def direction(self):
        """Direção da câmera para o alvo (o olho fica no lado oposto)."""
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        return (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch))

    def eye(self):
        return _add(self.target, _scale(self.direction(), self.distance))

    def basis(self):
        """(frente, direita, cima) da câmera, em coordenadas do mundo."""
        forward = _scale(self.direction(), -1.0)
        right = _normalize(_cross(forward, WORLD_UP))
        up = _cross(right, forward)
        return forward, right, up

    # Navegação ---------------------------------------------------------------------------------------------
    def orbit(self, dx_deg, dy_deg):
        self.yaw = (self.yaw + dx_deg) % 360.0
        self.pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT, self.pitch + dy_deg))

    def zoom(self, factor):
        """Aproxima (`factor` > 1) ou afasta; na ortográfica, mexe na escala."""
        if self.projection == 'ORTHO':
            self.ortho_scale = max(1e-4, self.ortho_scale / factor)
        else:
            self.distance = max(0.01, self.distance / factor)

    def pan(self, dx_px, dy_px, rect):
        """Desloca o alvo no plano da tela, na proporção de pixels por metro da vista."""
        width, height = max(1.0, rect[2]), max(1.0, rect[3])
        if self.projection == 'ORTHO':
            per_pixel = self.ortho_scale / height
        else:
            per_pixel = 2.0 * self.distance * math.tan(math.radians(self.fov) / 2.0) / height
        _forward, right, up = self.basis()
        self.target = _sub(self.target, _add(_scale(right, dx_px * per_pixel), _scale(up, dy_px * per_pixel)))
        return width, height

    def fit(self, bounds, rect, margin=1.15):
        """Enquadra a caixa `bounds` = (lo, hi) na vista, olhando do ângulo atual."""
        lo, hi = bounds
        self.target = ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, (lo[2] + hi[2]) / 2.0)
        radius = max(math.dist(self.target, canto) for canto in
                     [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        radius = max(radius, 1e-4)
        aspect = max(1.0, float(rect[2]) / max(1.0, float(rect[3]))) if rect else 1.0
        self.distance = radius / math.sin(math.radians(self.fov) / 2.0) * margin
        self.ortho_scale = 2.0 * radius * margin * aspect
        return self

    # Projeção ----------------------------------------------------------------------------------------------
    def project(self, point, rect):
        """(x, y, profundidade) do ponto no retângulo, ou None quando ele fica atrás da câmera."""
        x, y, width, height = float(rect[0]), float(rect[1]), max(1.0, float(rect[2])), max(1.0, float(rect[3]))
        forward, right, up = self.basis()
        eye = self.eye()
        v = _sub(point, eye)
        depth = _dot(v, forward)
        if self.projection == 'ORTHO':
            scale = max(1e-6, self.ortho_scale)
            return (x + width / 2.0 + _dot(v, right) / scale * width,
                    y + height / 2.0 + _dot(v, up) / scale * height, depth)
        if depth <= 1e-6:
            return None
        half = math.tan(math.radians(self.fov) / 2.0)
        aspect = width / height
        return (x + width / 2.0 + _dot(v, right) / (depth * half * aspect) * (width / 2.0),
                y + height / 2.0 + _dot(v, up) / (depth * half) * (height / 2.0), depth)

    def project_all(self, points, rect):
        """Projeta uma lista de pontos; pontos atrás da câmera viram None (a mesma posição da lista)."""
        return [self.project(point, rect) for point in points]

    def pixels_per_meter(self, rect):
        """Quantos pixels um metro ocupa no alvo (para desenhar as cotas no tamanho da tela)."""
        height = max(1.0, float(rect[3]))
        if self.projection == 'ORTHO':
            return height / max(1e-6, self.ortho_scale)
        return height / (2.0 * self.distance * math.tan(math.radians(self.fov) / 2.0))
