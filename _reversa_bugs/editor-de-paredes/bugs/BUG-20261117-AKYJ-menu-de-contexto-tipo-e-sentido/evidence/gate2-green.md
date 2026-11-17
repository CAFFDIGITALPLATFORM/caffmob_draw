# Gate 2 · change set e verde · BUG-20261117-AKYJ (#145)

Aprovado pelo titular em 2026-11-17 (plano em `fix/plan.html`).

## Change set aplicado

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/menu_contexto.py` (novo) | layout, alvo, regra de abertura e o estado mostrado nas seis linhas |
| CHG-002 | code | `caffmob_draw/walls2d/cores.py` (novo) | cor por tipo de parede, com o NORMAL no cinza atual |
| CHG-003 | code | `caffmob_draw/walls2d/props.py` | `menu` na sessão, `inverter_ativas`, `aplicar_direcao`, `aplicar_tipo` e `estado_da_caixa` |
| CHG-004 | code | `caffmob_draw/walls2d/ops_editor.py` | botão direito abre a caixa no modo Selecionar, clique executa, Esc e clique fora fecham, desenho da caixa e cor por tipo na planta |
| CHG-005 | code | `caffmob_draw/walls2d/classico_v2.py` | mesma caixa na cena v2 sobre a parede, com a navegação por botão direito preservada no vazio, e cor por tipo |
| CHG-006 | configuration | `caffmob_draw/data/translations/walls2d.json` | `Múltiplas` e `Inverter sentido` em pt_BR e en_US |

Diffs: `fix/CHG-001.diff` a `fix/CHG-006.diff`. Os de `props.py` e `ops_editor.py` carregam também o change set do
#146, que está no mesmo working tree sem commit.

## Prova do verde

```text
=== puro ===
Ran 10 tests in 0.013s
OK                                                        exit=0

=== blender ===
blender_bug_AKYJ_menu: OK                                 exit=0

=== i18n scan ===
340 textos, 226 únicos; sem tradução: 0; dinâmicos: 0     exit=0

=== i18n coverage ===
Ran 3 tests in 3.828s
OK                                                        exit=0

=== regressões de walls2d ===
test_walls2d_model      OK    test_walls2d_history    OK
test_walls2d_selecao    OK    test_walls2d_move       OK
test_walls2d_studio     OK    test_walls2d_heights    OK
test_walls2d_convert    OK

=== py_compile ===
exit=0

=== colunas acima de 120 ===
nenhuma linha nova (as apontadas pelo awk já estavam no arquivo antes desta correção)
```

`ruff` não existe neste host (`No module named ruff`); no lugar dele, `py_compile` e a checagem de coluna.

## Não coberto

- O modal não foi exercitado com janela e mouse: a abertura da caixa é provada pelo módulo puro e pela regra de
  abertura, não por um clique real na tela.
- A caixa na cena v2 compila e é desenhada pelo mesmo código, mas não tem teste automatizado: montar um documento
  v2 completo no teste de fundo ficou fora do escopo desta correção.
