"""Lista de ferragens do projeto (feature 008, T059; RN-16, D-24).

Núcleo puro (`summarize`, `drawer_items`) e o coletor da cena (`collect`):
- objetos marcados com `btm_hardware` (pés plásticos, pistões, trilhos dos deslizantes) contam 1 cada;
- cada frente de gaveta conta 1 par de corrediça; a do vão marcado com `slide_kind` "BLUM" conta como Blum.

Contrato: `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md` (`hardware[]`).
"""

from ..data.i18n import N_, tr

HARDWARE_PROP = 'btm_hardware'
NAMES = {
    'PE_PLASTICO': N_("Pé plástico"),
    'PISTAO': N_("Pistão"),
    'CORREDICA': N_("Corrediça (par)"),
    'CORREDICA_BLUM': N_("Corrediça Blum (par)"),
    'TRILHO_SUP': N_("Trilho superior deslizante"),
    'TRILHO_INF': N_("Trilho inferior deslizante"),
    # Feature 015 (T040; interfaces/cut-plan-json.md 2.3.0)
    'RODIZIO': N_("Rodízio"),
    'TUBO_CABIDEIRO': N_("Tubo de cabideiro"),
    'CALCEIRO_ARAMADO': N_("Calceiro aramado"),
    'PORTA_CINTOS': N_("Porta cintos/gravatas"),
    'PRATELEIRA_ARAMADA': N_("Prateleira aramada"),
    'CORREDICA_PRATELEIRA': N_("Corrediça de prateleira (par)"),
}
# Variante de divisão (feature 015) que leva ferragem: a aramada é só ferragem; a corrediça tem chapa e par de
# corrediças. A divisão aramada fica oculta na cena, por isso conta pela divisão, e não pela visibilidade.
DIVISION_HARDWARE = {'ARAMADA': 'PRATELEIRA_ARAMADA', 'CORREDICA': 'CORREDICA_PRATELEIRA'}


def _order(row):
    return (row['module_uid'] is None, row['module_uid'] or "", row['code'])


def summarize(items):
    """[(código, módulo)] → linhas {code, name, quantity, module_uid}, somadas e ordenadas (módulo, código)."""
    counts = {}
    for code, module_uid in items:
        counts[(code, module_uid)] = counts.get((code, module_uid), 0) + 1
    rows = [{"code": code, "name": tr(NAMES.get(code, code)), "quantity": n, "module_uid": module_uid}
            for (code, module_uid), n in counts.items()]
    return sorted(rows, key=_order)


def drawer_items(count, module_uid, blum=False):
    """Um par de corrediça por gaveta."""
    return [('CORREDICA_BLUM' if blum else 'CORREDICA', module_uid)] * int(count)


# Coletor da cena -------------------------------------------------------------------------------------------------
def _is_drawer_front(obj):
    return bool(obj.get('IS_DRAWER_FRONT') or obj.get('IS_PULLOUT_FRONT')
                or obj.get('hb_part_role') in ('DRAWER_FRONT', 'PULLOUT_FRONT'))


def _blum(obj, root):
    node = obj.parent
    while node is not None and node is not root.parent:
        custom = getattr(node, 'btm_custom', None)
        if custom is not None and getattr(custom, 'slide_kind', "") == 'BLUM':
            return True
        node = node.parent
    return False


def collect(scene, ensure_uid=True):
    """Linhas de `hardware[]` de todos os módulos visíveis da cena (`ensure_uid=False` na interface)."""
    from .part_sources import _visible, iter_modules
    items = []
    for module in iter_modules(scene, ensure_uid):
        for obj in module.obj.children_recursive:
            division = getattr(obj, 'btm_division', None)
            if division is not None and division.is_division and division.variant in DIVISION_HARDWARE:
                items.append((DIVISION_HARDWARE[division.variant], module.uid))
            if not _visible(obj):
                continue
            code = obj.get(HARDWARE_PROP)
            if code:
                items.append((str(code), module.uid))
            elif _is_drawer_front(obj):
                items += drawer_items(1, module.uid, _blum(obj, module.obj))
    return summarize(items)
