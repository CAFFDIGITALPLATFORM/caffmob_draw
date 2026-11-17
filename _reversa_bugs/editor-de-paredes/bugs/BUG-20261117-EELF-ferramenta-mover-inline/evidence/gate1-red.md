# Gate 1: prova vermelha (2026-11-17)

Os dois testes abaixo foram escritos antes da correção e falham no código de hoje, cada um pelo motivo certo.

## 1. `tests/test_walls2d_move.py` (modelo puro)

```
py -3 tests/test_walls2d_move.py
EXIT: 1
```

```
ERROR: test_move_zero_nao_muda_o_rascunho (__main__.MoverParedeTest.test_move_zero_nao_muda_o_rascunho)
Traceback (most recent call last):
  File "tests/test_walls2d_move.py", line 74, in test_move_zero_nao_muda_o_rascunho
    plan.move_segments([(0, 1)], 0.0, 0.0)
    ^^^^^^^^^^^^^^^^^^
AttributeError: 'WallPlan' object has no attribute 'move_segments'

... (mesmo erro nos outros 5 casos)

Ran 6 tests in 0.004s
FAILED (errors=6)
```

Motivo: a translação de trechos não existe no modelo. É a capacidade pedida, não um defeito de sintaxe do teste.

## 2. `tests/blender_bug_EELF_move.py` (addon carregado, 5.2)

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_EELF_move.py
EXIT: 1
```

```
Traceback (most recent call last):
AssertionError: ferramentas do editor hoje: ['SELECT', 'DRAW', 'INVERT', 'ADD_NODE', 'REMOVE_NODE']
Error: script failed, file: 'tests/blender_bug_EELF_move.py', exiting.
```

Motivo: a ferramenta `MOVE` não está registrada no enum do painel. O teste para no primeiro caso e os demais (mover,
desfazer, regressão do vértice, propriedades) nem chegam a rodar.

## O que cada teste prova depois da correção

| teste | prova |
|---|---|
| `test_move_um_trecho_desloca_os_dois_nos` | a parede anda inteira, sem mudar de comprimento |
| `test_vizinha_estica_com_o_no_compartilhado` | regra aprovada em 2026-11-17: o nó compartilhado anda e a vizinha estica, mudando comprimento e ângulo |
| `test_move_dois_trechos_juntos` | seleção múltipla move em bloco |
| `test_move_nao_muda_espessura_altura_nem_tipo` | mover não mexe em propriedades |
| `test_move_zero_nao_muda_o_rascunho` | movimento nulo não gera passo de desfazer |
| `test_indice_invalido_levanta` | índice fora do plano é recusado |
| `blender_bug_EELF_move.py` 1 e 2 | ferramenta no enum e movimento dentro do desfazer |
| `blender_bug_EELF_move.py` 3 e 4 | regressão: arrastar vértice e propriedades intactos |
