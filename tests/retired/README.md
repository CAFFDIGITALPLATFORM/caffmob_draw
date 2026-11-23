# Fumaças aposentadas

Arquivos que dirigiam a interface do **editor de armário 2D** (features 004, 006 e 008). A **T027 da feature 017 (D-04)**
tirou essa interface do registro: `bpy.ops.caffmob.cabinet_editor` hoje é o `Abrir` do armário v2 e recusa módulo de
biblioteca com *"Este móvel é da construção antiga: recrie pelo construtor novo para editar"* (RN-23).

As duas fumaças morrem no **primeiro** `open_editor`, antes de qualquer conferência, e por isso foram aposentadas em
2026-11-22 (T034 da 017). Não foram apagadas: ficam como registro da superfície removida, com o roteiro original.

| Arquivo | O que dirigia | Onde a regra sobrevive |
|---|---|---|
| `blender_006_cabinet_editor_tabs_smoke.py` | abas e painéis do editor, `REMOVE_PART`/`ADD_DIVISION`, inserção múltipla, Ctrl+Z interno, Confirmar = um desfazer, plano de corte, reabrir o `.blend` | `tests/test_cabinet_editor_divisions.py`, `test_cabinet_editor_structure.py`, `test_cabinet_editor_state.py`, `test_cabinet_editor_validate.py`, `test_cabinet_editor_elevation.py` |
| `blender_008_construtor_smoke.py` | `insert_payload` das sete abas, Aplicar/Cancelar, extras, ferragens, furação no corte, JSON com `hardware`, caso 800 × 2250 × 550 | `tests/test_cabinet_bays.py`, `test_cabinet_catalog.py`, `test_cabinet_extras.py`, `test_cabinet_slides.py`, `test_structure_gallery.py`, `test_production_contracts.py` |

## Lacuna que fica sem prova

Os núcleos puros continuam cobertos, mas **a aplicação na cena** que só essas duas fumaças exercitavam de ponta a ponta
ficou sem prova em Blender: `scene_divisions`, `scene_interiors`, `scene_slides` e a ferragem de `hardware.collect`
depois do Inserir. Fechar isso pede uma fumaça própria, dirigindo os `scene_*` direto (sem janela e sem a sessão do
editor), ou a volta do editor 2D.

## Como rodar, se a interface voltar

Com a interface 2D registrada de novo, os dois arquivos voltam a rodar de `tests/`:

```bash
xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/retired/blender_006_cabinet_editor_tabs_smoke.py
xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/retired/blender_008_construtor_smoke.py
```

O caminho de `site-packages` do projeto é resolvido por `parents[1]`, então `import _blender_env` continua achando
`tests/_blender_env.py` daqui.
