"""Catálogo de estruturas de caixa (feature 015, T014; RN-02, RN-03, D-01, D-06). Python puro.

Cada estrutura é a receita de um tipo de armário do Construtor do Promob ("Inferior c/ Divisória", "Armário"…): o
ambiente da galeria, o grupo de montagem (INFERIOR, SUPERIOR, DESPENSEIRO), as peças marcadas por padrão e as
medidas iniciais. O catálogo é dado (`data/cabinet_structures.json`, contrato em
`_reversa_forward/015-construtor-armario-promob/interfaces/catalogo-estruturas.md`): estrutura nova não pede código.

`parse` nunca levanta exceção: o que está errado sai com aviso que diz qual estrutura e por quê (princípio VIII).
`legacy_structure` dá a estrutura equivalente a um módulo de antes da 015 (RN-22).
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..data.i18n import tr

SCHEMA_VERSION = 1
CATALOG = Path(__file__).resolve().parents[1] / "data" / "cabinet_structures.json"

GROUPS = ('INFERIOR', 'SUPERIOR', 'DESPENSEIRO')
GROUP_TYPE = {'INFERIOR': 'BASE', 'SUPERIOR': 'WALL', 'DESPENSEIRO': 'TALL'}
CABINET_TYPES = ('BASE', 'WALL', 'TALL')
ASSEMBLIES = ('LATERAL', 'BASE')
ROLES = ('LEFT', 'RIGHT', 'DIVIDERS', 'BOTTOM', 'TOP', 'BACK', 'STRETCHER_FRONT', 'STRETCHER_BACK',
         'STRETCHER_FULL', 'TOP_LINEAR', 'TOE_KICK', 'FEET', 'CASTERS', 'KICK_GRANITE', 'CLOSURE', 'VIEWS',
         'VIEWS_TALL', 'BASE_TOP_RECESSED')
DIVISION_VARIANTS = ('CORTA_SAR', 'C_REB', 'MONTANTE', 'INVISIBLE', 'CORREDICA', 'ARAMADA', 'NAO_DIVIDE_FUNDO')
_ID = re.compile(r'^[a-z0-9_]+$')


@dataclass(frozen=True)
class Environment:
    id: str
    label_pt: str
    label_en: str
    line: str


@dataclass(frozen=True)
class Structure:
    id: str
    environment: str
    group: str
    label_pt: str
    label_en: str
    assembly: str
    sides_to_floor: bool
    bays: int
    width_mm: float
    height_mm: float      # 0 = do Padrão de Dimensões
    depth_mm: float       # 0 = do Padrão de Dimensões
    components: tuple     # ((papel, ligado), ...) na ordem do arquivo
    division_variants: tuple
    order: int

    @property
    def cabinet_type(self):
        return GROUP_TYPE[self.group]

    def has(self, role):
        """O papel vem marcado por padrão? Papel ausente da receita = desmarcado."""
        return dict(self.components).get(role, False)


@dataclass(frozen=True)
class Catalog:
    environments: tuple
    structures: tuple
    legacy: tuple         # ((linha ou "*", tipo, id), ...)
    warnings: tuple

    def by_id(self, structure_id):
        return next((s for s in self.structures if s.id == structure_id), None)

    def environment(self, env_id):
        return next((e for e in self.environments if e.id == env_id), None)

    def by_environment(self, env_id):
        return sorted((s for s in self.structures if s.environment == env_id), key=lambda s: (s.order, s.id))

    def legacy_structure(self, line, cabinet_type):
        """Id da estrutura equivalente a um módulo de antes da 015; vale a primeira entrada que casa."""
        for entry_line, entry_type, structure_id in self.legacy:
            if entry_type == cabinet_type and entry_line in (line, '*'):
                return structure_id
        return None


EMPTY = Catalog((), (), (), ())


def _number(value, name, sid, warnings, allow_null=False, minimum=0.0):
    if value is None and allow_null:
        return 0.0
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < minimum:
        warnings.append(tr("Estrutura {}: {} inválido").format(sid, name))
        return None
    return float(value)


def _structure(item, env_ids, seen, warnings):
    if not isinstance(item, dict):
        warnings.append(tr("Estrutura ilegível ignorada"))
        return None
    sid = item.get('id')
    if not isinstance(sid, str) or not _ID.match(sid):
        warnings.append(tr("Estrutura sem identificador válido ignorada"))
        return None
    if sid in seen:
        warnings.append(tr("Estrutura {}: identificador repetido").format(sid))
        return None
    if item.get('environment') not in env_ids:
        warnings.append(tr("Estrutura {}: ambiente desconhecido").format(sid))
        return None
    if item.get('group') not in GROUPS:
        warnings.append(tr("Estrutura {}: grupo desconhecido").format(sid))
        return None
    assembly = item.get('assembly', 'LATERAL')
    if assembly not in ASSEMBLIES:
        warnings.append(tr("Estrutura {}: montagem desconhecida").format(sid))
        return None
    components = item.get('components')
    if not isinstance(components, dict):
        warnings.append(tr("Estrutura {}: sem componentes").format(sid))
        return None
    unknown = [role for role in components if role not in ROLES]
    if unknown:
        warnings.append(tr("Estrutura {}: peça desconhecida ({})").format(sid, ", ".join(sorted(unknown))))
        return None
    if any(not isinstance(v, bool) for v in components.values()):
        warnings.append(tr("Estrutura {}: componente sem verdadeiro/falso").format(sid))
        return None
    variants = item.get('division_variants', [])
    if not isinstance(variants, list) or any(v not in DIVISION_VARIANTS for v in variants):
        warnings.append(tr("Estrutura {}: variante de divisão desconhecida").format(sid))
        return None
    size = item.get('size_mm') or {}
    if not isinstance(size, dict):
        warnings.append(tr("Estrutura {}: medidas ilegíveis").format(sid))
        return None
    width = _number(size.get('width'), "largura", sid, warnings, minimum=1.0)
    height = _number(size.get('height'), "altura", sid, warnings, allow_null=True)
    depth = _number(size.get('depth'), "profundidade", sid, warnings, allow_null=True)
    bays = item.get('bays', 1)
    if isinstance(bays, bool) or not isinstance(bays, int) or not 1 <= bays <= 10:
        warnings.append(tr("Estrutura {}: número de vãos fora de 1 a 10").format(sid))
        return None
    if None in (width, height, depth):
        return None
    order = item.get('order', 0)
    return Structure(sid, item['environment'], item['group'], str(item.get('label_pt') or sid),
                     str(item.get('label_en') or item.get('label_pt') or sid), assembly,
                     bool(item.get('sides_to_floor', False)), bays, width, height, depth,
                     tuple(components.items()), tuple(variants), order if isinstance(order, int) else 0)


def parse(text):
    """`Catalog` com as estruturas válidas e os avisos; versão desconhecida devolve o catálogo vazio."""
    try:
        data = json.loads(text)
    except ValueError:
        return Catalog((), (), (), (tr("Catálogo de estruturas inválido"),))
    if not isinstance(data, dict) or data.get('schema-version') != SCHEMA_VERSION:
        return Catalog((), (), (), (tr("Catálogo de estruturas em versão desconhecida"),))
    warnings = []
    environments = []
    for env in data.get('environments') or []:
        if isinstance(env, dict) and isinstance(env.get('id'), str) and env.get('line'):
            environments.append(Environment(env['id'], str(env.get('label_pt') or env['id']),
                                            str(env.get('label_en') or env.get('label_pt') or env['id']),
                                            str(env['line'])))
        else:
            warnings.append(tr("Ambiente ilegível ignorado"))
    env_ids = {e.id for e in environments}
    structures, seen = [], set()
    for item in data.get('structures') or []:
        structure = _structure(item, env_ids, seen, warnings)
        if structure is not None:
            seen.add(structure.id)
            structures.append(structure)
    legacy = []
    for entry in data.get('legacy_map') or []:
        if not isinstance(entry, dict) or entry.get('cabinet_type') not in CABINET_TYPES:
            warnings.append(tr("Entrada de equivalência ilegível ignorada"))
            continue
        if entry.get('structure') not in seen:
            warnings.append(tr("Equivalência para estrutura inexistente: {}").format(entry.get('structure')))
            continue
        legacy.append((str(entry.get('line') or '*'), entry['cabinet_type'], entry['structure']))
    return Catalog(tuple(environments), tuple(structures), tuple(legacy), tuple(warnings))


_cache = [None]


def load(path=None):
    """Catálogo do pacote (guardado em memória); arquivo ausente ou ilegível = catálogo vazio com aviso."""
    if path is None and _cache[0] is not None:
        return _cache[0]
    target = Path(path) if path is not None else CATALOG
    try:
        text = target.read_text(encoding='utf-8')
    except OSError:
        catalog = Catalog((), (), (), (tr("Catálogo de estruturas não encontrado"),))
    else:
        catalog = parse(text)
    if path is None:
        _cache[0] = catalog
    return catalog


def reload():
    _cache[0] = None
    return load()


def get(structure_id):
    """Estrutura do catálogo do pacote, ou None (id vazio ou desconhecido)."""
    return load().by_id(structure_id) if structure_id else None
