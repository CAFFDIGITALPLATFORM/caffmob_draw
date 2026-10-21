"""Plano dimensional puro, em milímetros no referencial do armário (066, T059).

Cada membro traz uid, box=(mínimo, máximo), rule, refs e params. As referências trazem uid e face.
O resultado contém caixas finais, deslocamento e extensão, sem modificar os dados de entrada.
ANCHORED sem referência acompanha o limite positivo do eixo; com referência conserva a distância à face.
DISTRIBUTE dispõe os centros entre duas faces com margens de meia peça, por index/count.
"""

from dataclasses import dataclass
import math

AXES = {'X': 0, 'Y': 1, 'Z': 2}
RULES = ('FIXED', 'ANCHORED', 'FIT_BETWEEN', 'DISTRIBUTE')


@dataclass(frozen=True)
class Change:
    shift: tuple
    extension: tuple
    box: tuple


def topological(members):
    by_uid = {}
    for member in members:
        uid = member['uid']
        if not uid or uid in by_uid:
            raise ValueError('Identidade de membro ausente ou repetida')
        by_uid[uid] = member
    pending, done, ordered = set(), set(), []

    def visit(uid):
        if uid in pending:
            raise ValueError('Ciclo entre regras dimensionais: ' + uid)
        if uid in done:
            return
        if uid not in by_uid:
            raise ValueError('Referência ausente: ' + uid)
        pending.add(uid)
        for ref in by_uid[uid].get('refs', ()):
            visit(ref['uid'])
        pending.remove(uid)
        done.add(uid)
        ordered.append(uid)

    for uid in by_uid:
        visit(uid)
    return ordered


def _face(box, ref, axis):
    face = ref.get('face', 'POS_' + 'XYZ'[axis])
    if face not in ('NEG_X', 'POS_X', 'NEG_Y', 'POS_Y', 'NEG_Z', 'POS_Z') or face[-1] != 'XYZ'[axis]:
        raise ValueError('Face de referência incompatível com o eixo')
    return box[1 if face.startswith('POS') else 0][axis]


def solve(members, old_size, new_size):
    """Calcula tudo antes de escrever; ciclo, vão negativo ou espessura inviável recusam o plano inteiro."""
    if any(not math.isfinite(v) or v <= 0 for v in (*old_size, *new_size)):
        raise ValueError('Medidas devem ser positivas e finitas')
    by_uid = {m['uid']: m for m in members}
    order = topological(members)
    result = {}
    for uid in order:
        member = by_uid[uid]
        box = tuple(tuple(float(v) for v in row) for row in member['box'])
        if len(box) != 2 or any(len(row) != 3 or any(not math.isfinite(v) for v in row) for row in box):
            raise ValueError('Caixa inválida: ' + uid)
        lengths = [box[1][i] - box[0][i] for i in range(3)]
        if any(v < 0 for v in lengths):
            raise ValueError('Vão negativo: ' + uid)
        params = member.get('params', {})
        axis = AXES.get(params.get('axis', 'X'))
        rule = member.get('rule', 'FIXED')
        if axis is None or rule not in RULES:
            raise ValueError('Regra ou eixo desconhecido: ' + uid)
        refs = member.get('refs', [])
        shift, extension = [0.0] * 3, [0.0] * 3
        if rule == 'ANCHORED':
            if len(refs) > 1:
                raise ValueError('Ancorado aceita uma referência')
            if refs:
                ref = refs[0]
                shift[axis] = (_face(result[ref['uid']].box, ref, axis)
                               - _face(by_uid[ref['uid']]['box'], ref, axis))
            else:
                shift[axis] = new_size[axis] - old_size[axis]
        elif rule in ('FIT_BETWEEN', 'DISTRIBUTE'):
            if len(refs) != 2:
                raise ValueError('A regra exige duas referências: ' + uid)
            start, end = [_face(result[ref['uid']].box, ref, axis) for ref in refs]
            margin = float(params.get('offset_mm', 0))
            start, end = start + margin, end - margin
            if end < start:
                raise ValueError('Vão negativo: ' + uid)
            if rule == 'FIT_BETWEEN':
                minimum = float(params.get('min_size_mm', min((v for v in lengths if v > 1e-6), default=0)))
                if end - start < minimum - 1e-6:
                    raise ValueError('Espessura inviável: ' + uid)
                shift[axis] = start - box[0][axis]
                extension[axis] = end - start - lengths[axis]
                if member.get('role') == 'HARDWARE' and abs(extension[axis]) > 1e-6:
                    raise ValueError('Ferragem não pode ser esticada: ' + uid)
            else:
                count, index = int(params.get('count', 1)), int(params.get('index', 0))
                if count < 1 or not 0 <= index < count or end - start < count * lengths[axis] - 1e-6:
                    raise ValueError('Distribuição inviável: ' + uid)
                free = end - start - lengths[axis]
                position = start + (free * index / (count - 1) if count > 1 else free / 2)
                shift[axis] = position - box[0][axis]
        final = (tuple(box[0][i] + shift[i] for i in range(3)),
                 tuple(box[1][i] + shift[i] + extension[i] for i in range(3)))
        result[uid] = Change(tuple(shift), tuple(extension), final)
    return result
