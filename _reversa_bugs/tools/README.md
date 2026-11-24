# Reversa Debugger executável

`reversa_debugger.py` roda as duas suítes do projeto arquivo a arquivo, guarda a saída de cada ensaio,
classifica as falhas e grava o relatório no próprio repositório. Não altera testes nem código.

## Execução completa

```bash
python3 _reversa_bugs/tools/reversa_debugger.py \
  --suite all \
  --blender /opt/blender/blender \
  --pure-timeout 45 \
  --blender-timeout 360 \
  --out _reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-debugger
```

Saída:

- `report.md` — placar, falhas, diagnóstico e bugs abertos;
- `results.json` — resultado por arquivo, com exit, duração, log e classificação;
- `pure/<teste>.log` e `blender/<teste>.log` — stdout/stderr de cada ensaio.

Código de saída: `0` sem defeito candidato, `1` com defeito candidato, `2` erro de configuração.

## Classificação

- **defeito**: falha sem bloqueio externo identificado; exige correção.
- **ambiente**: rede, MOBI de ensaio ou extensão instalada indisponível; não é defeito de produto.
- **performance**: timeout ou percentil fora do alvo em ensaio de tempo (`066`, `067`).
- **obsoleto**: o próprio ensaio declara que a funcionalidade foi removida.

## Última execução

Em 2026-11-24, exit code `0`: pura **186/186**, Blender **197/203** (5 ambiente, 1 performance, 0 defeitos).
Relatório, logs e `results.json` em
`_reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-debugger/`.
