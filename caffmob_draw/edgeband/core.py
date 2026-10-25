"""Núcleo puro da fita de borda visual (feature 067, T068; D-21; RF-080 a RF-083). Sem `bpy`.

As peças entram como caixas no referencial do componente (o dono), em metros: `Box(uid, lo, hi)`. Assim a rotação e a
escala do componente não mudam a conta, e a frente não precisa estar em −Y (RF-082).

- `narrow_faces(box)`: as quatro faces estreitas de uma chapa (perpendiculares aos dois eixos que não são a
  espessura), com a chave `"<uid>|<eixo><sinal>"`, estável enquanto a peça existir (RF-083).
- `exposed(boxes)`: as faces estreitas que nenhuma outra peça encosta (borda coberta pela peça vizinha não tem fita).
- `merge(faces)`: faces no mesmo plano (tolerância de 0,1 mm) que se encostam por um lado inteiro viram uma faixa
  só: três chapas de 15 mm empilhadas dão uma faixa de 45 mm, sem emendas (RF-081).
- `label_state(pedidas, existentes)`: CREATE ("Criar e aplicar fita de borda"), CHANGE ("Mudar cor da fita") ou
  MIXED (lista as faltantes e oferece criar nelas), RF-080.
- `band_uid(chaves)` e `params_hash(faixa)`: a faixa é identificada pelas bordas que cobre (repetir não duplica) e
  só é refeita quando a geometria dela muda.
"""

import hashlib
import json
from dataclasses import dataclass

TOL = 1e-4                      # 0,1 mm
CREATE, CHANGE, MIXED = 'CREATE', 'CHANGE', 'MIXED'
_COVER = 0.5                    # fração da face encostada por outra peça para a borda contar como coberta


@dataclass(frozen=True)
class Box:
    uid: str
    lo: tuple
    hi: tuple

    def size(self, axis):
        return self.hi[axis] - self.lo[axis]

    @property
    def thickness_axis(self):
        return min(range(3), key=self.size)


@dataclass(frozen=True)
class Face:
    key: str
    axis: int                   # eixo da normal
    sign: int                   # +1 ou −1
    pos: float                  # coordenada do plano no eixo da normal
    rect: tuple                 # ((lo, hi) no 1º eixo do plano, (lo, hi) no 2º), eixos em ordem crescente

    @property
    def plane_axes(self):
        return tuple(a for a in range(3) if a != self.axis)

    @property
    def area(self):
        return (self.rect[0][1] - self.rect[0][0]) * (self.rect[1][1] - self.rect[1][0])


@dataclass(frozen=True)
class Band:
    keys: tuple                 # chaves das bordas cobertas, ordenadas
    axis: int
    sign: int
    pos: float
    rect: tuple

    @property
    def uid(self):
        return band_uid(self.keys)

    def size(self):
        """(comprimento, largura aparente) da faixa: o lado maior e o menor do retângulo."""
        a = self.rect[0][1] - self.rect[0][0]
        b = self.rect[1][1] - self.rect[1][0]
        return max(a, b), min(a, b)


def edge_key(uid, axis, sign):
    return f"{uid}|{'XYZ'[axis]}{'+' if sign > 0 else '-'}"


def narrow_faces(box):
    t = box.thickness_axis
    faces = []
    for axis in range(3):
        if axis == t:
            continue
        others = tuple(a for a in range(3) if a != axis)
        rect = tuple((box.lo[a], box.hi[a]) for a in others)
        for sign in (-1, +1):
            pos = box.hi[axis] if sign > 0 else box.lo[axis]
            faces.append(Face(edge_key(box.uid, axis, sign), axis, sign, pos, rect))
    return faces


def _overlap(a, b):
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def covered(face, other, tol=TOL):
    """A peça `other` encosta na face (fica do lado de fora dela, colada) cobrindo boa parte da área?"""
    axis = face.axis
    touching = abs((other.lo[axis] if face.sign > 0 else other.hi[axis]) - face.pos) <= tol
    inside = other.lo[axis] - tol <= face.pos <= other.hi[axis] + tol and other.size(axis) > 2 * tol
    if not (touching or inside):
        return False
    a, b = face.plane_axes
    area = _overlap(face.rect[0], (other.lo[a], other.hi[a])) * _overlap(face.rect[1], (other.lo[b], other.hi[b]))
    return face.area > 0 and area / face.area >= _COVER


def exposed(boxes, tol=TOL):
    out = []
    for box in boxes:
        for face in narrow_faces(box):
            if not any(other is not box and covered(face, other, tol) for other in boxes):
                out.append(face)
    return out


def _same(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def _join(r1, r2, tol):
    """União de dois retângulos do mesmo plano quando ela é um retângulo (lado inteiro encostado); senão None."""
    for d in (0, 1):
        o = 1 - d
        if _same(r1[d], r2[d], tol) and (abs(r1[o][1] - r2[o][0]) <= tol or abs(r2[o][1] - r1[o][0]) <= tol):
            joined = [None, None]
            joined[d] = (min(r1[d][0], r2[d][0]), max(r1[d][1], r2[d][1]))
            joined[o] = (min(r1[o][0], r2[o][0]), max(r1[o][1], r2[o][1]))
            return tuple(joined)
    return None


def merge(faces, tol=TOL):
    """Faixas: faces coplanares (mesmo eixo, sinal e plano) que se encostam por um lado inteiro viram uma só."""
    by_side = {}
    for face in faces:
        by_side.setdefault((face.axis, face.sign), []).append(face)
    groups = []
    for (axis, sign), side in sorted(by_side.items()):
        side.sort(key=lambda f: f.pos)
        current = [side[0]]
        for face in side[1:]:
            if face.pos - current[-1].pos <= tol:        # mesmo plano dentro da tolerância
                current.append(face)
            else:
                groups.append((axis, sign, current))
                current = [face]
        groups.append((axis, sign, current))
    bands = []
    for axis, sign, group in groups:
        items = [([f.key], f.rect, f.pos) for f in group]
        changed = True
        while changed:
            changed = False
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    joined = _join(items[i][1], items[j][1], tol)
                    if joined is not None:
                        items[i] = (items[i][0] + items[j][0], joined, items[i][2])
                        del items[j]
                        changed = True
                        break
                if changed:
                    break
        bands += [Band(tuple(sorted(keys)), axis, sign, pos, rect) for keys, rect, pos in items]
    return bands


def label_state(requested, existing):
    """(estado, faltantes) do botão da fita no escopo pedido."""
    requested = list(dict.fromkeys(requested))
    have = set(existing)
    missing = [k for k in requested if k not in have]
    if not requested or len(missing) == len(requested):
        return CREATE, missing
    if not missing:
        return CHANGE, []
    return MIXED, missing


def band_uid(keys):
    return hashlib.sha256("|".join(sorted(keys)).encode()).hexdigest()[:16]


def params_hash(band, thickness, offset):
    data = [band.axis, band.sign, round(band.pos, 5), [[round(v, 5) for v in r] for r in band.rect],
            round(thickness, 6), round(offset, 6)]
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]


def band_box(band, thickness, offset):
    """(lo, hi) da malha da faixa: fora da face, afastada `offset` (contra z-fighting), com a espessura `thickness`,
    dentro do retângulo da própria face (sem sobrepor a faixa vizinha na quina)."""
    a, b = (x for x in range(3) if x != band.axis)
    lo, hi = [0.0] * 3, [0.0] * 3
    lo[a], hi[a] = band.rect[0]
    lo[b], hi[b] = band.rect[1]
    start = band.pos + band.sign * offset
    end = band.pos + band.sign * (offset + thickness)
    lo[band.axis], hi[band.axis] = min(start, end), max(start, end)
    return tuple(lo), tuple(hi)


def dumps(values):
    return json.dumps(list(values))


def loads(text):
    try:
        value = json.loads(text or "[]")
    except ValueError:
        return []
    return [str(v) for v in value] if isinstance(value, list) else []
