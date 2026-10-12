"""Categorias da Biblioteca CAFFMob (feature 012, T013; D-17, RN-02 a RN-04). Python puro.

As fixas (Cozinha, Banheiro, Sala, Home office) vêm do pacote, cada uma com a linha do Padrão de Dimensões. As do
usuário ficam em `categories.json` na biblioteca do usuário (`library_panel/categories.py`), com nome e linha. Cada
categoria é também uma pasta de módulos de `customize/library_io` (pastas que já existiam viram categoria COZ).
"""

import json
from collections import namedtuple

from ..customize import manifest
from ..data.i18n import N_, tr

Category = namedtuple('Category', 'name line fixed')

LINES = ('COZ', 'DOR', 'BAN', 'SAL', 'ESC')
LINE_LABELS = {'COZ': N_("Cozinha"), 'DOR': N_("Dormitório"), 'BAN': N_("Banheiro"), 'SAL': N_("Sala"),
               'ESC': N_("Escritório")}
FIXED = (
    Category("Cozinha", 'COZ', True),
    Category("Banheiro", 'BAN', True),
    Category("Sala", 'SAL', True),
    Category("Home office", 'ESC', True),
)
DEFAULT_LINE = 'COZ'
SCHEMA_VERSION = 1

EMPTY = N_("Digite um nome para a categoria")
REPEATED = N_("Já existe uma categoria com esse nome")
INVALID_CHAR = N_("O nome não pode ter < > : \" / \\ | ? * nem terminar em ponto")
INVALID_FILE = N_("Arquivo de categorias inválido; as categorias do usuário foram ignoradas")


def all_categories(user):
    """Fixas e depois as do usuário, na ordem em que foram criadas."""
    return list(FIXED) + list(user)


def _key(name):
    return name.strip().casefold()


def validate_name(name, user):
    """None se o nome serve; senão o motivo (texto traduzível)."""
    clean = (name or "").strip()
    if not clean:
        return EMPTY
    if manifest.file_stem(clean) != clean:          # a pasta da categoria tem de ser a do módulo salvo (pergunta 57)
        return INVALID_CHAR
    if _key(clean) in {_key(c.name) for c in all_categories(user)}:
        return REPEATED
    return None


def parse(text):
    """(categorias do usuário, avisos). Arquivo vazio = nenhuma; inválido = nenhuma, com aviso."""
    if not (text or "").strip():
        return [], []
    try:
        data = json.loads(text)
    except ValueError:
        return [], [tr(INVALID_FILE)]
    items = data.get('categories', []) if isinstance(data, dict) else []
    categories, warnings = [], []
    fixed = {_key(c.name) for c in FIXED}
    for item in items:
        if not isinstance(item, dict) or not str(item.get('name') or "").strip():      # null = ausente (F-06)
            warnings.append(tr("Categoria sem nome ignorada"))
            continue
        name = str(item['name']).strip()
        if _key(name) in fixed or _key(name) in {_key(c.name) for c in categories}:
            warnings.append(tr("Categoria repetida ignorada: {}").format(name))
            continue
        line = item.get('line')
        if line not in LINES:
            warnings.append(tr("Linha desconhecida na categoria {}: usada Cozinha").format(name))
            line = DEFAULT_LINE
        categories.append(Category(name, line, False))
    return categories, warnings


def dump(user):
    return json.dumps({"schema-version": SCHEMA_VERSION,
                       "categories": [{"name": c.name, "line": c.line} for c in user]},
                      ensure_ascii=False, indent=2)


def merge_folders(user, folders):
    """Acrescenta as pastas de módulos que ainda não são categoria (linha COZ); ignora as fixas e as ocultas."""
    known = {_key(c.name) for c in all_categories(user)}
    merged = list(user)
    for folder in folders:
        if folder.startswith('.') or _key(folder) in known:
            continue
        merged.append(Category(folder, DEFAULT_LINE, False))
        known.add(_key(folder))
    return merged


def with_line(user, name, line):
    """Troca a linha de uma categoria do usuário."""
    return [Category(c.name, line if _key(c.name) == _key(name) else c.line, False) for c in user]
