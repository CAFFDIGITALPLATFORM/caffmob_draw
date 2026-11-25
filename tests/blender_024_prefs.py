"""Preferência de exibição do armário (feature 024, T009; RN-01, D-08).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_024_prefs.py

- `exibicao_armario` tem exatamente dois itens (`TEXTURA_SO`/`TEXTURA_LINHAS`), padrão `TEXTURA_SO`;
- `cabinet_color` continua existindo e com o mesmo padrão (é lido por `ops_placement.py:40`);
- nenhuma preferência vizinha sumiu.

O add-on é registrado pelo `_blender_env` fora de `preferences.addons`, então o teste lê o RNA da classe.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import caffmob_draw  # noqa: E402
from caffmob_draw.armario_v2 import exibicao  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    classe = getattr(caffmob_draw, 'BTM_AddonPreferences', None)
    check("classe de preferências existe", classe is not None)
    if classe is None:
        return
    rna = classe.bl_rna.properties
    enum = rna.get('exibicao_armario')
    check("exibicao_armario registrado", enum is not None)
    if enum is not None:
        ids = [item.identifier for item in enum.enum_items]
        check("dois itens", ids == ['TEXTURA_SO', 'TEXTURA_LINHAS'], str(ids))
        padrao = getattr(enum, 'default', None)
        check("padrão TEXTURA_SO", padrao == 'TEXTURA_SO', str(padrao))
    cor = rna.get('cabinet_color')
    valores = list(getattr(cor, 'default_array', []) or []) if cor is not None else []
    check("cabinet_color intacto", tuple(round(c, 3) for c in valores) == (0.0, 0.5, 0.7, 0.3), str(valores))
    for nome in ('wall_color', 'door_window_color', 'annotation_color', 'annotation_highlight_color',
                 'obstacle_color', 'show_legacy_libraries', 'panel_mode', 'use_viewport_hud', 'designer_name'):
        check(f"preferência {nome} intacta", rna.get(nome) is not None)
    check("variante sem linhas", exibicao.linhas('TEXTURA_SO') is False)
    check("variante com linhas", exibicao.linhas('TEXTURA_LINHAS') is True)
    check("catálogo responde", bpy.app.translations.pgettext_iface("Somente textura") != "")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
