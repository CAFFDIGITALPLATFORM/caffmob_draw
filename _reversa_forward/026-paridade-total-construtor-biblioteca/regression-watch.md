# Regression watch: 026

## 1. Provas novas

| Prova | Comando | Resultado |
|-------|---------|-----------|
| Núcleo puro 026 | `python -m unittest test_armario_026_parity` | OK (payload, cutlist, tema, grade 2 colunas, alvo 44 px) |
| Blender 026 | `blender --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_026_parity.py` | OK, 23 checagens; export, vista, tema, duplicata+Gerar, medida, laterais, menu e modal de arraste |

## 2. Regressão

| Prova | Resultado |
|-------|-----------|
| `blender_025_place.py` | OK, 16/16 |
| `blender_023_fase7.py` | OK, 36/36 |
| `blender_012_library_ui.py` | OK, 9/9 |
| `blender_biblioteca_detalhe.py` | OK, 38/38 |
| `blender_smoke.py` | `BLENDER_SMOKE_OK` |
| Puros amplos (build, corte, janela, UV, MDF, view, placement, library, 026) | 109 testes OK |
| `test_i18n_coverage` | 3/3 OK |
| `check_api.py` | 638 arquivos, nenhuma API desconhecida |

## 3. Lint

`ruff check caffmob_draw/armario_v2 caffmob_draw/library_panel` continua com 7 achados **pré-existentes** de outras
features (`drawer_detect_core` F401, `panel.py` F841, `panel_window.py` F401 de `ops`, `preview.py` F401 de `bpy`,
`draw.py` E731 da 073, `models_core.py` F841, `ops_replace.py` F401). Nenhum foi introduzido pela 026.

## 4. O que não foi verificado

- Não houve inspeção visual humana das telas; o tema é provado por tokens e pelo caminho de desenho.
- O popup de medida foi executado por `EXEC_DEFAULT`; o diálogo nativo não é capturado por screenshot.
- O menu de contexto foi provado pelo `draw`; o clique direito real não foi automatizado.
