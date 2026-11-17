# Gate 1 · testes e vermelho · BUG-20261117-AKYJ (#145)

Aprovado pelo titular em 2026-11-17 com o plano (`fix/plan.html`).

## Testes criados

| arquivo | intenção | cobre |
|---|---|---|
| `tests/test_walls2d_menu_contexto.py` | reprodução e regressão | ordem e valores das seis linhas da caixa, "Múltiplas" quando a Direção diverge, caixa dentro da região em qualquer ponto de clique, alvo por linha e nada fora, regra de abertura (só botão direito no modo Selecionar; nunca no Desenhar), cor por tipo e o NORMAL no cinza do editor |
| `tests/blender_bug_AKYJ_menu.py` | reprodução e regressão | `inverter_ativas` inverte todas as ativas em um passo de desfazer, `aplicar_direcao` alcança as ativas, cor por tipo igual ao `COLORS['wall']` no NORMAL, modo Desenhar continua encerrando o lápis com o botão direito, ferramenta Inverter Sentido por clique segue intacta |

## Prova do vermelho

```text
=== puro ===
  File "tests\test_walls2d_menu_contexto.py", line 13, in <module>
    from caffmob_draw.walls2d import cores, menu_contexto as mc
ImportError: cannot import name 'cores' from 'caffmob_draw.walls2d' (unknown location)
exit=1

=== blender ===
  File "tests\blender_bug_AKYJ_menu.py", line 20, in <module>
    from caffmob_draw.walls2d import cores, menu_contexto as mc, model, ops_editor, props
ImportError: cannot import name 'cores' from 'caffmob_draw.walls2d'
Error: script failed, file: 'tests/blender_bug_AKYJ_menu.py', exiting.
exit=1
```

O vermelho é estrutural: a capacidade não existe. Depois do change set os mesmos dois comandos têm de sair `OK`.
