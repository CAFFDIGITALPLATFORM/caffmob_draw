# Actions: Frente do objeto no Mover Sobre

> Identificador: `022-mover-sobre-frente`
> Data: `2026-11-24`
> Roadmap: `_reversa_forward/022-mover-sobre-frente/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 12 |
| Paralelizáveis (`[//]`) | 6 |
| Maior cadeia de dependência | 5 |

## Fase 1, Núcleo puro

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar `frente_core.py` com `yaw_of`, `wall_candidates`, `decide`, `GAP_MAX` e `DISAGREE_MAX`, sem `bpy` | - | `[//]` | `caffmob_draw/move_over/frente_core.py` | 🟢 | `[ ]` |
| T002 | Criar ensaios puros da decisão: propriedade vence, parede perto vale, parede longe não vale, eixo para módulo, conflito marca ambíguo e ausência de evidência marca ambíguo | T001 | `[//]` | `tests/test_move_over_frente_core.py` | 🟢 | `[ ]` |
| T003 | Adicionar helpers de remapeamento de índice de eixo entre base da vista e base do objeto, com ensaio dos quatro lados | T001 | `[//]` | `caffmob_draw/move_over/frente_core.py` | 🟢 | `[ ]` |

## Fase 2, Janela

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Montar `view_frame = b_frame @ Rz(yaw)` no `MoveOver`, decidindo a frente ao abrir e ao trocar B, com cache da decisão | T001 | - | `caffmob_draw/move_over/scene.py` | 🟢 | `[ ]` |
| T005 | Converter arraste, ímã, cota, alças e giro por vista para a base da vista (`to_view`/`from_view`), preservando `delta` na base do objeto | T003, T004 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[ ]` |
| T006 | Ler `SIDE_AXIS`/`SIDE_FACE` na base da vista mantendo "Na frente"/"Atrás" como lados do objeto | T003, T004 | - | `caffmob_draw/move_over/encostar.py` | 🟢 | `[ ]` |
| T007 | Desenhar o indicador de frente nas duas vistas a partir de `view_frame` | T004 | `[//]` | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[ ]` |

## Fase 3, Propriedade e pergunta

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Implementar `caffmob.move_over_front` (diálogo com os quatro lados e "usar o eixo"), gravando `btm_front_yaw` em um passo de `UNDO` e sem gravar nada ao cancelar | T001 | `[//]` | `caffmob_draw/move_over/ops_front.py` | 🟢 | `[ ]` |
| T009 | Disparar a pergunta ao abrir a janela quando a decisão vier ambígua, e expor a origem da frente (propriedade/parede/eixo) no status da janela | T004, T008 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[ ]` |
| T010 | Registrar o operador novo e garantir remoção limpa no `unregister` | T008 | - | `caffmob_draw/move_over/__init__.py` | 🟢 | `[ ]` |

## Fase 4, Fechamento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Registrar rótulos novos em `pt_BR` e `en_US` e validar a cobertura i18n | T007, T009 | `[//]` | `caffmob_draw/data/translations/feature_022.json` | 🟢 | `[ ]` |
| T012 | Criar fumaça no Blender 5.2 (pergunta, gravação, reabertura, `Ctrl+Z`, `yaw = 0` idêntico) e rodar suíte completa + `build.py` | T005, T006, T009, T010, T011 | - | `tests/blender_022_mover_sobre_frente.py` | 🟢 | `[ ]` |

## Notas de execução

> Reservado para `/reversa-coding` registrar avisos ou observações durante a execução.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-to-do` (12 ações em 4 fases) | reversa |
