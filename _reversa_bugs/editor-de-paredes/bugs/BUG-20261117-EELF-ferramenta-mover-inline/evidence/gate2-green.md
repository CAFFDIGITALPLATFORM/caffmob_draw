# Gate 2: prova verde (2026-11-17)

Change set aplicado com aprovação do titular. Saídas reais, depois da correção.

## 1. Teste de reprodução e regressão no modelo (puro)

```
py -3 tests/test_walls2d_move.py
Ran 6 tests in 0.002s
OK
EXIT: 0
```

## 2. Teste no addon carregado (Blender 5.2, sem janela)

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_EELF_move.py
blender_bug_EELF_move: OK
EXIT: 0
```

Cobre: ferramenta `MOVE` no enum do painel, movimento aplicado, um passo de desfazer devolvendo o rascunho,
arraste de vértice intacto e propriedades (espessura, altura, tipo) preservadas.

## 3. Regressões do editor de paredes

```
test_walls2d_model    EXIT: 0  OK
test_walls2d_history  EXIT: 0  OK
test_walls2d_selecao  EXIT: 0  OK
test_walls2d_studio   EXIT: 0  OK
test_walls2d_heights  EXIT: 0  OK
test_walls2d_convert  EXIT: 0  OK
```

## 4. Cobertura de tradução (as 7 frases novas entraram no catálogo)

```
py -3 tools/i18n_scan.py walls2d --faltando
329 textos, 224 únicos; sem tradução: 0; dinâmicos: 0

py -3 tests/test_i18n_coverage.py
Ran 3 tests
OK
```

## 5. Compilação

```
py -3 -m py_compile <7 arquivos>
EXIT: 0
```

## O que não foi verificado

- **Modal na interface**: não abri o editor com janela para arrastar com o mouse. O gancho do modal
  (`_handle_move`) é provado por leitura e pelo modelo, não por interação real. O teste com janela
  (`tests/blender_002_ui_events.py`) exige `--enable-event-simulate` e uma instância gráfica.
- **ruff**: não está instalado no host (`No module named ruff`). A checagem feita foi de coluna (nenhuma linha nova
  acima de 120) e de compilação.
