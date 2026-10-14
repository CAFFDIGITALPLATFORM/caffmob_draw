"""Número de vãos do armário (feature 008, T015; RN-07b, D-15). Python puro, sem `bpy`.

N vãos = N − 1 divisórias verticais de vão inteiro, marcadas `bay`, em cadeia pelo espaço-raiz `s0`: a primeira
corta `s0`, a segunda corta a metade direita (`s0.b`), e assim por diante, todas com a mesma largura de vão. Mudar N
mantém as divisórias de vão que já existem (com a posição nova) e acrescenta ou tira só as do fim; as divisões comuns
(não `bay`) não são tocadas, exceto as que estavam dentro de uma divisória de vão removida (saem com ela).

Feature 015 (T019; RN-14, D-15): a largura de um vão pode ser digitada. Ela fica na divisória de vão à direita dele
(`Division.bay_width`, 0 = livre); os vãos livres dividem por igual o que sobra, então com 3 vãos o digitado no meio
passa a diferença para os dois vizinhos. O último vão não tem divisória à direita e é sempre calculado. Vão livre
menor que `MIN_WIDTH` recusa a largura digitada.
"""

from dataclasses import replace

from . import divisions as dv

ROOT = 's0'
MAX_BAYS = 10
MIN_WIDTH = 0.05            # m: o subvão mínimo das divisões (RN-CABINET_EDITOR-09)


def _chain(index):
    return ROOT + ".b" * index


def widths(total, count, thickness, typed=None):
    """(larguras dos `count` vãos, None) ou (None, menor largura livre) quando a digitada não cabe.

    `total` = largura interna; `typed` = larguras digitadas por vão (0 ou ausente = livre).
    """
    count = max(1, min(MAX_BAYS, int(count)))
    typed = [float(w or 0.0) for w in (typed or [])][:count - 1] + [0.0] * count
    typed = typed[:count]
    free = [i for i, w in enumerate(typed) if w <= 0.0]
    if not free:                                   # o último vão é sempre livre
        free = [count - 1]
        typed[count - 1] = 0.0
    rest = total - (count - 1) * thickness - sum(typed)
    each = rest / len(free)
    if each < MIN_WIDTH - 1e-9:
        return None, each
    return [each if i in free else typed[i] for i in range(count)], None


def plan(space, count, thickness, typed=None):
    """[(caminho, offset)] das divisórias de vão para `count` vãos no espaço `space` (Box).

    Sem `typed`, vãos iguais; com uma largura digitada que não cabe, também (quem chama avisa pelo `widths`).
    """
    count = max(1, min(MAX_BAYS, int(count)))
    found, _short = widths(space.size(0), count, thickness, typed)
    if found is None:
        found, _short = widths(space.size(0), count, thickness)
    return [(_chain(i), found[i]) for i in range(count - 1)]


def count(divisions):
    return 1 + sum(1 for d in divisions if d.bay)


def apply(roots, divisions, count_, thickness, typed=None):
    """Divisões com exatamente `count_` vãos; `typed` = larguras digitadas por vão (feature 015)."""
    if ROOT not in roots:
        return list(divisions)
    bays = sorted((d for d in divisions if d.bay), key=lambda d: dv.depth_of(d.space))
    if typed is None:
        typed = [getattr(d, 'bay_width', 0.0) for d in bays]
    wanted = plan(roots[ROOT], count_, thickness, typed)
    out = list(divisions)
    for extra in bays[len(wanted):]:
        out, _removed = dv.remove(out, extra.uid)
    kept = {d.uid for d in bays[:len(wanted)]}
    for index, (space, offset) in enumerate(wanted):
        if index < len(bays) and bays[index].uid in kept:
            out = [replace(d, space=space, offset=offset, thickness=thickness) if d.uid == bays[index].uid else d
                   for d in out]
        else:
            out.append(dv.Division(dv.new_uid(), space, dv.VERTICAL, offset, thickness, bay=True))
    return out


def removed(before, after):
    """Uids das divisórias de vão que saíram (para os Ajustes automáticos)."""
    now = {d.uid for d in after}
    return [d.uid for d in before if d.bay and d.uid not in now]


def bay_index(path, count_):
    """Vão (0 a `count_` − 1) a que o subvão `path` pertence: `s0.a` é o 1º, `s0.b.a` o 2º, `s0.b.b` o 3º de 3."""
    if not path or not path.startswith(ROOT):
        return None
    index = 0
    for token in path.split(".")[1:]:
        if token != 'b' or index >= count_ - 1:
            break
        index += 1
    return min(index, max(0, count_ - 1))


def chain(index):
    """Caminho do espaço que a divisória de vão `index` corta."""
    return _chain(index)

