# Regression Watch: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Gerado por: `/reversa-coding` (T012)

## Cobertura dos requisitos funcionais

| RF | Descrição | Coberto por | Status |
|----|-----------|-------------|--------|
| RF-01 | Abrir janela própria igual ao mockup (preview dividido, 7 abas, empty state, OK/Aplicar/Cancelar) | T001, T002, T003, T005, T006, T007, T011, T013, T014 | Implementado (paridade pixel em T018) |
| RF-02 | Construir o armário dentro da janela (laterais, bases, prateleiras, divisórias, gavetas, internos, portas, deslizantes, fundo) | T006, T009, T015, T016 | Implementado (clique seleciona peça; hits medidos) |
| RF-03 | Validar medidas em tempo real (erro bloqueia OK/Aplicar) | `validar.py` (GEO-001/GEO-002) + `ops.py` | Implementado e coberto por `tests/test_janela_023_core.py` |
| RF-04 | OK grava passo de desfazer e fecha a janela | T002 (`BTM_OT_ArmarioV2WindowOK`) | Implementado |
| RF-05 | Aplicar grava passo de desfazer sem fechar | T002 (`BTM_OT_ArmarioV2WindowAplicar`) | Implementado |
| RF-06 | Cancelar/restaurar instantâneo inicial | T002 (`BTM_OT_ArmarioV2WindowCancelar`, modal ESC) | Implementado |
| RF-07 | Empty state "Janela de Armário Vazia" com Montar Caixa | T007 | Implementado |

## Pontos de atenção para regressão

1. **Painel da Vista 3D inalterado**: a nova janela é adicionada sobre o construtor v2 existente; o painel `CAFFMob Draw` na Vista 3D (`armario_v2/panel.py`) continua funcionando igual. Não remover nem alterar `_MODULES` existentes além de acrescentar `window`, `ops_window`, `panel_window`.

2. **`bl_idname` não colide**: `caffmob.cabinet_editor` é o `Abrir` do editor 2D antigo (já fora de registro desde 017/T027). A janela própria usa `caffmob.armario_v2_window_open` (novo `bl_idname`, sem colisão).

3. **Sessão única**: o `poll` de `WindowOpen` bloqueia abertura de segunda janela enquanto uma estiver aberta (`janela_existe()`). Não remover essa guarda.

4. **Draw handler**: o `POST_PIXEL` handler é registrado na área do Image Editor na abertura e removido no fechamento (`close_window`). Verificar que não vaza handlers ao fechar a janela pelo sistema (X).

5. **Instantâneo (snapshot)**: `snapshot_de`/`aplicar_snapshot` de `ops.py` são reutilizados para o Cancelar da janela. Qualquer mudança nos campos de `BTM_PG_ArmarioV2` afeta o instantâneo.

6. **Contrato de chapas**: `semear_contrato` é chamado na abertura. Se o Padrão de Dimensões não estiver configurado, o Gerar recusa (`chapas.pode_gerar`).

7. **Pixel-perfeito**: as cores do preview usam a paleta do mockup (`COR_*` em `preview.py`). Blender UI (panéis/botões) segue o tema do Blender; apenas o preview desenhado com `gpu` usa as cores do mockup.

## Testes de regressão sugeridos

- Abrir janela própria em projeto vazio → cria raiz, abre Image Editor, não trava.
- Abrir → montar caixa → OK → peças geradas na cena, janela fecha, Ctrl+Z desfaz tudo.
- Abrir → montar caixa → Aplicar → alterar medida → Cancelar → volta ao estado do Aplicar.
- Abrir → ESC → instantâneo restaurado, aviso "alterações descartadas".
- Tentar abrir segunda janela → `poll` recusa com mensagem.
