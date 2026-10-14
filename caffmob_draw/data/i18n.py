"""Tradução da interface do CAFFMob Draw: pt_BR e en_US (BUG-20261007-FLZO).

O texto escrito no código é a chave (msgid), em português ou em inglês. O catálogo fica em `translations/*.json`,
um arquivo por área: `{"texto do código": {"pt_BR": "...", "en_US": "..."}}`. As duas línguas são obrigatórias (o teste
`tests/test_i18n_coverage.py` confere). Cada texto é registrado nos contextos padrão (`*`) e de operador (`Operator`),
porque o Blender traduz o `bl_label` dos operadores no contexto `Operator`.

As traduções de um add-on valem para o Blender inteiro. Por isso um texto-fonte em inglês de uma palavra só ("Size",
"Render") entra só no contexto padrão, com a tradução de uso geral; no contexto de operador vale a do próprio Blender.
Texto com sentido próprio do plugin não pode ser uma palavra genérica (ex.: o botão de vão livre é "Open Passage").
Quando o texto não pode mudar (ex.: o nome de um item do catálogo também é o id dele, "Range"), a entrada leva
`"contexto"` e é registrada só nesse contexto; quem desenha passa o mesmo contexto (`text_ctxt`, `tr(texto, contexto)`).

O Blender já traduz rótulos, dicas, nomes de propriedade e `self.report`. Texto desenhado ou montado não passa por ele:
- `tr("texto")` traduz na hora (use `tr("Comprimento: {}").format(valor)` em vez de f-string);
- `N_("texto")` só marca o texto para o catálogo, quando quem desenha é que traduz (ex.: `canvas2d.draw.text`).

O módulo não importa `bpy` no topo: o código puro (`walls2d/model.py`, `data/units.py`) usa `tr` nas mensagens e roda
nos testes sem o Blender, onde o texto sai como está no código.
"""

import json
import os

LOCALES = ('pt_BR', 'en_US')
CONTEXTS = ('*', 'Operator')
FOLDER = os.path.join(os.path.dirname(__file__), 'translations')


def tr(msgid, context=None):
    """Texto traduzido para o idioma atual da interface do Blender (fora do Blender, o próprio texto)."""
    try:
        import bpy  # type: ignore
    except ImportError:
        return msgid
    return bpy.app.translations.pgettext_iface(msgid, context)


def N_(msgid):
    """Marca o texto para o catálogo sem traduzir (quem desenha traduz)."""
    return msgid


def _schema_entries():
    """Rótulos do esquema do Padrão de Dimensões (label_pt → label_en), gerados do próprio esquema."""
    from . import dimension_schema as schema
    pairs = [(param.label_pt, param.label_en) for param in schema.PARAMS.values()]
    pairs += [(comp.label_pt, comp.label_en) for comp in schema.COMPONENTS]
    pairs += [(pt, en) for _code, pt, en in schema.LINES]
    return {pt: {'pt_BR': pt, 'en_US': en} for pt, en in pairs}


def _structure_entries():
    """Nomes das estruturas de caixa e dos ambientes (feature 015), do próprio catálogo (label_pt → label_en)."""
    path = os.path.join(os.path.dirname(__file__), 'cabinet_structures.json')
    try:
        with open(path, encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {}
    items = list(data.get('environments') or []) + list(data.get('structures') or [])
    return {i['label_pt']: {'pt_BR': i['label_pt'], 'en_US': i.get('label_en') or i['label_pt']}
            for i in items if isinstance(i, dict) and i.get('label_pt')}


def load_catalog():
    catalog = _schema_entries()
    catalog.update(_structure_entries())
    for name in sorted(os.listdir(FOLDER)):
        if name.endswith('.json'):
            with open(os.path.join(FOLDER, name), encoding='utf-8') as handle:
                catalog.update(json.load(handle))
    return catalog


def translations_dict():
    """Formato de `bpy.app.translations.register`: só as entradas que mudam o texto."""
    result = {locale: {} for locale in LOCALES}
    for msgid, entry in load_catalog().items():
        generic = entry.get('en_US') == msgid and ' ' not in msgid.strip()
        contexts = (entry['contexto'],) if 'contexto' in entry else CONTEXTS[:1] if generic else CONTEXTS
        for locale in LOCALES:
            text = entry.get(locale)
            if text and text != msgid:
                for context in contexts:
                    result[locale][(context, msgid)] = text
    return result


def register():
    import bpy  # type: ignore
    bpy.app.translations.register(__name__, translations_dict())


def unregister():
    import bpy  # type: ignore
    bpy.app.translations.unregister(__name__)
