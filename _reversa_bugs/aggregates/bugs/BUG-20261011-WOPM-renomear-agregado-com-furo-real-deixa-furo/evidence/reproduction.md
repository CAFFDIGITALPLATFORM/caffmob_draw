# Cápsula de reprodução (lote 19)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_WOPM_perforate_rename.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_WOPM_perforate_rename.py (exit 1):
FALHA WOPM (arquivo novo): um BOOLEAN e um CPM_CUTOUT, com o nome novo ['Agregado (furo): Nicho', 'Agregado (furo): Nicho renomeado'] ['Agregado: Nicho', 'Agregado: Nicho renomeado']
FALHA WOPM (arquivo novo): a usinagem exporta um furo só 2
FALHA WOPM (arquivo novo): desligar Perfurar remove tudo ['Agregado (furo): Nicho'] ['Agregado: Nicho']
FALHA WOPM (arquivo antigo): um BOOLEAN e um CPM_CUTOUT, com o nome novo ['Agregado (furo): Nicho', 'Agregado (furo): Nicho renomeado'] ['Agregado: Nicho', 'Agregado: Nicho renomeado']
FALHA WOPM (arquivo antigo): a usinagem exporta um furo só 2
FALHA WOPM (arquivo antigo): desligar Perfurar remove tudo ['Agregado (furo): Nicho'] ['Agregado: Nicho']
blender_bug_WOPM_perforate_rename: FALHAS: WOPM (arquivo novo): um BOOLEAN e um CPM_CUTOUT, com o nome novo, WOPM (arquivo novo): a usinagem exporta um furo só, WOPM (arquivo novo): desligar Perfurar remove tudo, WOPM (arquivo antigo): um BOOLEAN e um CPM_CUTOUT, com o nome novo, WOPM (arquivo antigo): a usinagem exporta um furo só, WOPM (arquivo antigo): desligar Perfurar remove tudo
```
