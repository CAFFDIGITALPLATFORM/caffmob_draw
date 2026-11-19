"""Núcleo do seletor de sobreposição (feature 016, T004 a T006; D-01, D-05).

O que não precisa do Blender: a ordem dos achados, o estado do seletor (marcados, foco, rolagem) e a geometria do
painel em pixels. Puro, como `selection/classify.py` e `selection/component.py`, para rodar nos testes sem `bpy`.

O painel é o do artefato de referência: 390 px de largura, linhas de 25 px, cabeçalho de 78 px, rodapé de 62 px e no
máximo 12 linhas visíveis. O estado do seletor morre com a sessão: nada aqui é gravado na cena.
"""

ROW_H = 25
WIDTH = 390
HEADER = 78
FOOTER = 62
MAX_VISIBLE = 12

# Respostas de `action_at` para o clique no painel.
ROW = 'row'
HEADER_HIT = 'header'
FOOTER_HIT = 'footer'
OUTSIDE = 'outside'


def rank(hits):
    """Objetos dos achados `(distância, objeto)`, do mais próximo ao mais distante, sem repetir.

    O operador monta a lista com a distância em mundo que o `ray_cast` devolve; uma mesma malha pode aparecer mais de
    uma vez quando o raio a cruza por partes, e a lista mostra o objeto uma vez só (RN-02).
    """
    ordered = sorted(hits, key=lambda item: item[0])
    found, seen = [], set()
    for _distance, obj in ordered:
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        found.append(obj)
    return found


class Picker:
    """Estado do seletor: achados ordenados, marcados, item em foco e primeira linha visível.

    O foco é um índice em `hits`, não o objeto, para a lista sobreviver a um objeto apagado no meio da inspeção.
    """

    def __init__(self, hits):
        self.hits = list(hits)
        self.staged = set()
        self.focus = 0 if self.hits else -1
        self.scroll = 0

    def __len__(self):
        return len(self.hits)

    def entry(self, index):
        return self.hits[index] if 0 <= index < len(self.hits) else None

    @property
    def focused(self):
        return self.entry(self.focus)

    def visible(self):
        """Linhas da janela visível, na ordem da lista."""
        return self.hits[self.scroll:self.scroll + MAX_VISIBLE]

    def is_staged(self, index):
        obj = self.entry(index)
        return obj is not None and obj in self.staged

    def toggle(self, index):
        obj = self.entry(index)
        if obj is None:
            return
        if obj in self.staged:
            self.staged.discard(obj)
        else:
            self.staged.add(obj)

    def mark_all(self):
        self.staged = set(self.hits)

    def invert(self):
        self.staged = set(self.hits) - self.staged

    def add(self, index):
        obj = self.entry(index)
        if obj is not None:
            self.staged.add(obj)

    def remove(self, index):
        obj = self.entry(index)
        if obj is not None:
            self.staged.discard(obj)

    def move(self, delta):
        """Anda o foco e mantém a linha em foco visível (RF-09)."""
        if not self.hits:
            return
        self.focus = max(0, min(len(self.hits) - 1, self.focus + delta))
        self.keep_visible()

    def scroll_by(self, delta):
        """Rola a lista sem mexer no foco nem nos marcados (RF-03)."""
        limit = max(0, len(self.hits) - MAX_VISIBLE)
        self.scroll = max(0, min(limit, self.scroll + delta))

    def keep_visible(self):
        if not self.hits:
            self.scroll = 0
            return
        if self.focus < self.scroll:
            self.scroll = self.focus
        elif self.focus >= self.scroll + MAX_VISIBLE:
            self.scroll = self.focus - MAX_VISIBLE + 1
        self.scroll = max(0, min(self.scroll, max(0, len(self.hits) - MAX_VISIBLE)))


def confirm_selection(hits, staged, original, original_active, focus):
    """Seleção final do `Enter`: o que está fora da lista continua, o que está nela vira o marcado (RF-10, RF-12).

    Marcar soma à seleção anterior e desmarcar um objeto que já estava selecionado tira ele, sem tocar no resto.
    Devolve `(seleção, ativo)`: o item em foco vira o ativo quando está marcado; senão fica o ativo anterior, se
    continuar selecionado, ou o primeiro da seleção.
    """
    inside = {id(obj) for obj in hits}
    chosen = {id(obj) for obj in staged}
    selection = [obj for obj in original if id(obj) not in inside] + [obj for obj in hits if id(obj) in chosen]
    if focus is not None and any(obj is focus for obj in selection):
        active = focus
    elif original_active is not None and any(obj is original_active for obj in selection):
        active = original_active
    else:
        active = selection[0] if selection else None
    return selection, active


def in_rect(point, rect):
    x, y, w, h = rect
    return x <= point[0] <= x + w and y <= point[1] <= y + h


def rows_rect(rect):
    """Retângulo das linhas dentro do painel (entre o cabeçalho e o rodapé)."""
    x, y, w, h = rect
    return (x, y + FOOTER, w, h - HEADER - FOOTER)


def panel_rect(mouse, region, count):
    """Painel ao lado do cursor, preso à região; perto da borda ele vira para o outro lado."""
    width = WIDTH
    height = HEADER + ROW_H * max(1, min(count, MAX_VISIBLE)) + FOOTER
    region_w, region_h = region
    x = mouse[0] + 18
    if x + width > region_w - 8:
        x = mouse[0] - 18 - width
    x = max(8, min(x, region_w - width - 8))
    y = mouse[1] - height / 2.0
    y = max(8, min(y, region_h - height - 8))
    return (x, y, width, height)


def row_at(point, rect, scroll, count):
    """Índice do achado sob o ponto, contando a rolagem; `None` fora das linhas."""
    rows = rows_rect(rect)
    if not in_rect(point, rows):
        return None
    row = int((rows[1] + rows[3] - point[1]) // ROW_H)
    index = scroll + row
    return index if 0 <= index < count else None


def action_at(point, rect, scroll, count):
    """O que o clique no ponto pede: `('row', i)`, `('footer', None)`, `('header', None)` ou `('outside', None)`."""
    index = row_at(point, rect, scroll, count)
    if index is not None:
        return (ROW, index)
    if in_rect(point, rect):
        return (FOOTER_HIT, None) if point[1] <= rect[1] + FOOTER else (HEADER_HIT, None)
    return (OUTSIDE, None)
