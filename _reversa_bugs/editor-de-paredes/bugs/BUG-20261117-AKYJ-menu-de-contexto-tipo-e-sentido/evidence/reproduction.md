# Cápsula de reprodução · BUG-20261117-AKYJ (#145)

- **Commit base:** `88c63c7e` (master), árvore com o fix do #146 aplicado mas sem commit.
- **Ambiente:** Windows, Blender 5.2.0 LTS, `pt_BR`; addon instalado `bl_ext.mobi_caff_digital.caffmob_draw`.
- **Comando:** leitura de `caffmob_draw/walls2d/` mais a sondagem MCP registrada em
  `../../intake/sondagem-mcp-20261117.md` (enum de ferramentas e valores de `line` e `wall_type` no addon instalado).
- **Determinismo:** determinístico, 1/1. A ausência é estrutural, não depende de estado.

## O que acontece hoje

| passo | resultado real |
|---|---|
| botão direito sobre uma parede, ferramenta Selecionar/Mover | **nada acontece**. `_handle` não tem ramo para `RIGHTMOUSE`; o evento não é `LEFTMOUSE` nem `MOUSEMOVE`, então cai em `return False` e passa adiante |
| botão direito durante o desenho | encerra o lápis (`_handle_draw`: `if event.type in {'ESC', 'RIGHTMOUSE'}: self._finish_drawing(s)`) |
| inverter o sentido de uma parede | trocar para a ferramenta Inverter Sentido, clicar na parede, voltar para Selecionar/Mover (quatro passos) |
| trocar o tipo de parede | campo `wall_type` no painel Painel, um trecho por vez; a cor não muda |
| trocar a Direção (lado da espessura) | `_side_set` aplica só em `s.segment()`, nunca no lote (`s.lote()`) |

## Discrepância com o relato

O relato diz "o botão direito cancela em vez de abrir menu". No modo **Selecionar** ele não cancela nada: fica sem
efeito. Quem encerra o modal com o botão direito é o **modo Desenhar**, e ali encerrar o lápis é o comportamento
correto, que a correção tem de preservar.

## Evidência de ausência

- `grep "bpy.types.Menu" caffmob_draw/walls2d/` não devolve nada: não existe menu no editor.
- `grep "call_menu\|popup_menu" caffmob_draw/walls2d/` não devolve nada.
- `draw_plan` pinta todo trecho com `COLORS['wall']`; o dicionário `COLORS` (`ops_editor.py:46`) não tem cor por tipo.
- `props.py:245` `_line_set` só grava `s.line` (a linha de medição, global) e `_side_set` só o trecho selecionado.
- `model.Chain.invert` existe (`model.py:273`) e é o que a ferramenta Inverter Sentido usa, uma cadeia por clique.

## O que já existe no próprio projeto e pode ser reaproveitado

- `studio_painel.py` já desenha uma lista suspensa no mesmo canvas `POST_PIXEL`: `menu_rects`, `alvo(pixel)` e
  `clicar(...)`, com as opções empilhadas a partir da caixa do controle. É o padrão da casa para menu desenhado.
- `selecao_classica.aplicar(plan, selecao, campo, valor)` já aplica um campo em vários trechos e desfaz tudo se o
  modelo recusar um valor, com `CAMPOS_DO_LOTE = ('thickness', 'height', 'end_height', 'wall_type')`.
- `props.lote()` devolve os trechos ativos quando são mais de um.
