"""Porta única da interface das bibliotecas herdadas (feature 012, T048; D-01, RN-12, RN-14).

Frameless, face frame e closets (e a biblioteca de molduras, que depende deles) saem da interface: armário novo é
sempre CAFFMob. O código delas fica registrado só para abrir e converter arquivos antigos (`legacy/convert.py`); a
remoção do código é de uma feature seguinte. Todo ponto de entrada da interface herdada pergunta aqui
(`legacy_ui`), que lê a preferência avançada `show_legacy_libraries` (desligada por padrão).
"""

import bpy  # type: ignore

LEGACY_LIBRARIES = frozenset({'FRAMELESS', 'FACE_FRAME', 'CLOSETS'})


def _preferences(context):
    package = __package__.rsplit('.', 1)[0]
    addon = context.preferences.addons.get(package) if context is not None else None
    return getattr(addon, 'preferences', None)


def legacy_ui(context=None):
    """A interface das bibliotecas herdadas aparece? Só com a preferência de suporte ligada."""
    prefs = _preferences(context or bpy.context)
    return bool(getattr(prefs, 'show_legacy_libraries', False))


def is_legacy(obj):
    """`obj` é a raiz de um armário de biblioteca herdada?"""
    from ..selection import classify
    return classify.module_library(obj) in LEGACY_LIBRARIES


def legacy_roots(scene):
    """Raízes de armários herdados da cena, sem as que estão dentro de outro armário herdado."""
    roots = [obj for obj in scene.objects if is_legacy(obj)]
    names = {obj.name for obj in roots}
    out = []
    for obj in roots:
        parent = obj.parent
        nested = False
        while parent is not None:
            if parent.name in names:
                nested = True
                break
            parent = parent.parent
        if not nested:
            out.append(obj)
    return out
