# Cápsula de reprodução · BUG-20261117-EELF

## Ambiente

- Commit base: `88c63c7e` (master, merge do PR #42), árvore limpa em `caffmob_draw/` e `tests/` no início do ciclo
- Sistema: Windows, Git Bash
- Blender: 5.2.0 LTS, locale `pt_BR`
- Addon instalado: `bl_ext.mobi_caff_digital.caffmob_draw`
- Python do host: 3.14.6 (usado só para o cliente MCP, fora do Blender)

## Comando executado

1. Sondagem somente leitura pelo servidor MCP do Blender (127.0.0.1:9877), cliente `.blender-mcp/_mcp.py`:

   ```
   py -3 .blender-mcp/_mcp.py <probe>
   ```

   Saída relevante:

   ```
   btm_wall_editor.tool ....... ["SELECT", "DRAW", "INVERT", "ADD_NODE", "REMOVE_NODE"]
   ```

   Exit code: 0.

2. Leitura do código do modal e do modelo: `caffmob_draw/walls2d/ops_editor.py`, `props.py`, `model.py`.

3. Não dirigi o modal pela UI. O editor é um operador modal com janela própria, e iniciá-lo por socket pode deixar a
   sessão do titular presa no modal. A ausência da ferramenta já está provada pelo enum registrado no addon em execução.
   Reprodução de UI fica para o teste de eventos do Gate 1.

## Resultado

O enum `tool` do addon instalado não tem `MOVE`, e nenhum ramo do modal translada parede: `_handle_click` no modo
SELECT só inicia arraste de vértice (`self.dragging = node`) e o `MOUSEMOVE` só chama `chain.move_node(k, point)`.
`model.py` não expõe translação de trecho nem de conjunto.

## Taxa e determinismo

- Taxa: 1/1 pela via de inspeção (enum + código). Nenhuma tentativa de UI executada.
- Classificação: determinística. Não é intermitente: a capacidade não existe em nenhum caminho.

## Critério de reprodução para o Gate 1

Um teste que afirme a existência da ferramenta `MOVE` e do método de translação falha hoje e deve passar depois da
correção:

```
py -3 -c "..."              # enum da sessão
blender --background --factory-startup --python-exit-code 1 --python tests/test_walls2d_move.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_EELF_move.py
```
