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
| T001 | Criar `frente_core.py` com `yaw_from_normal`, `wall_candidate`, `nearest_wall`, `decide`, `decide_for_wall`, `face_of` e `DISAGREE_MAX`, sem `bpy` | - | `[//]` | `caffmob_draw/move_over/frente_core.py` | 🟢 | `[X]` |
| T002 | Criar ensaios puros da decisão: propriedade vence, parede perto e longe valem, parede ao lado não vale, eixo para módulo, conflito marca ambíguo e ausência de evidência marca ambíguo | T001 | `[//]` | `tests/test_move_over_frente_core.py` | 🟢 | `[X]` |
| T003 | Traduzir a face do `stick` da base da vista para a base de B (`face_of`), com ensaio dos quatro lados | T001 | `[//]` | `caffmob_draw/move_over/frente_core.py` | 🟢 | `[X]` |

## Fase 2, Janela

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Montar `view_frame = b_frame @ Rz(yaw)` no `MoveOver`, decidindo a frente ao abrir | T001 | - | `caffmob_draw/move_over/scene.py` | 🟢 | `[X]` |
| T005 | Manter arraste, ímã, cota, alças e giro por vista no referencial girado (mesma base de `delta`), sem conversão extra | T004 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[X]` |
| T006 | Manter `SIDE_AXIS`/`SIDE_FACE` com o mesmo significado (frente em −Y da vista) e traduzir só a face do `stick` | T003, T004 | - | `caffmob_draw/move_over/encostar.py` | 🟢 | `[X]` |
| T007 | Desenhar o indicador de frente (rótulo da origem + seta) na vista da planta | T004 | `[//]` | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[X]` |

## Fase 3, Propriedade e pergunta

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Implementar `caffmob.move_over_front` (diálogo com os quatro lados e "usar o eixo"), gravando `btm_front_yaw` em um passo de `UNDO` e sem gravar nada ao cancelar | T001 | `[//]` | `caffmob_draw/move_over/ops_front.py` | 🟢 | `[X]` |
| T009 | Disparar a pergunta ao abrir a janela quando a decisão vier ambígua (fora do arraste), expor a origem da frente na vista e oferecer o botão "Frente do objeto" | T004, T008 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[X]` |
| T010 | Registrar o operador novo e garantir remoção limpa no `unregister` | T008 | - | `caffmob_draw/move_over/__init__.py` | 🟢 | `[X]` |

## Fase 4, Fechamento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Registrar rótulos novos em `pt_BR` e `en_US` e validar a cobertura i18n | T007, T009 | `[//]` | `caffmob_draw/data/translations/feature_022.json` | 🟢 | `[X]` |
| T012 | Criar fumaça no Blender 5.2 (parede, ambiguidade, propriedade, `yaw = 0` idêntico, operador) e rodar a suíte | T005, T006, T009, T010, T011 | - | `tests/blender_022_mover_sobre_frente.py` | 🟢 | `[X]` |

## Notas de execução

- T005/T006 dispensaram conversão entre bases: girar o referencial de B (`b_frame @ Rz(yaw)`) mantém `delta`, `box_b`
  e as vistas no mesmo espaço, então arraste, ímã, cota, alças, `SIDE_AXIS` e `SIDE_FACE` continuam válidos — só a
  face gravada pelo `stick` é traduzida (`face_of`).
- A pergunta automática não dispara no caminho de arraste (`from_drag`), para não interromper o gesto: nesse caminho a
  frente vem da parede/eixo e o botão "Frente do objeto" permite trocar.
- Evidência: `tests/test_move_over_frente_core.py` 17/17, `tests/blender_022_mover_sobre_frente.py` 10/10,
  `test_i18n_coverage` 3/3 e suíte pura do runner 187/187 em 2026-11-24.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-to-do` (12 ações em 4 fases) | reversa |
