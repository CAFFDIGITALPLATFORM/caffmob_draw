# Legacy impact: 011-selecao-por-componente

> Gerado por `/reversa-coding` em 2026-10-09.
> Feature: seleção por componente, exclusão em profundidade e porta e janela na região marcada.
> Âncora: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/selection/component.py` (novo) | Seleção (`architecture.md#1`, camada de interação) | componente-novo | MEDIUM | Raiz do componente e plano de exclusão, puros (D-01, D-05) |
| `caffmob_draw/selection/component_select.py` (novo) | Seleção | componente-novo | HIGH | Handler `depsgraph_update_post` que muda a seleção do usuário em toda a cena (D-02) |
| `caffmob_draw/selection/component_pick.py` (novo) | Seleção | componente-novo | MEDIUM | Keymap no "3D View": Alt + clique e clique que limpa a isenção (D-04) |
| `caffmob_draw/selection/component_props.py` (novo) | Seleção | delta-de-dados | LOW | `Scene.btm_component_select` (salvo) e `WindowManager.btm_component_exempt` |
| `caffmob_draw/__init__.py` | Registro da extensão | regra-alterada | LOW | Registra e remove os três módulos novos da seleção |
| `caffmob_draw/aggregates/ops_aggregate.py` | Agregados (003), exclusão por X/Delete | regra-alterada | HIGH | O poll passa também com descendentes; apaga a subárvore inteira (`delete_components`); a pergunta dos agregados ignora as folhas de porta, janela e esquadria |
| `caffmob_draw/operators/doors_windows.py` | Aberturas de parede (`domain.md#2.2`) | regra-alterada | HIGH | `delete_door_window` apaga em profundidade; a inserção ganha o estado "na região" (`place_in_region`, `modal_in_region`, `confirm_placement`) |
| `caffmob_draw/aggregates/ops_import.py` | Importação OBJ/FBX/glTF (003) | regra-alterada | MEDIUM | Várias malhas viram um grupo PLAIN; uma raiz Empty vira o grupo |
| `caffmob_draw/aggregates/ops_group.py` | Montar esquadria (007) | regra-alterada | MEDIUM | Aceita o grupo importado selecionado e desfaz esse grupo antes de montar |
| `caffmob_draw/openings/region_core.py`, `region_props.py`, `region.py` (novos) | Aberturas de parede | componente-novo | MEDIUM | Encaixe exato na região, estado de sessão, operador modal com desenho `POST_PIXEL` e Esc na vista 3D |
| `caffmob_draw/openings/__init__.py` | Pacote `openings` | regra-alterada | LOW | Registra os módulos da região |
| `caffmob_draw/ui/view3d_sidebar.py` | Barra lateral, bloco do topo | regra-alterada | LOW | Interruptor "Seleção por componente" abaixo dos modos de seleção |
| `caffmob_draw/operators/viewport_hud.py` | HUD da viewport | regra-alterada | LOW | Botão do interruptor com o estado escrito |
| `caffmob_draw/ui/sidebar_build.py` | Barra lateral, Construir › Aberturas | regra-alterada | LOW | "Marcar região", medidas editáveis e "Limpar região" |
| `caffmob_draw/data/translations/*.json` | i18n | regra-alterada | LOW | 29 textos novos em pt-BR/en-US |
| `tests/blender_007_window_smoke.py` | Testes | regra-alterada | LOW | O OBJ importado entra num grupo; "Montar esquadria" parte do grupo |

## Diff conceitual por componente

**Seleção.** Antes, clicar numa peça selecionava a peça. Agora, com o interruptor ligado (padrão), um handler troca
cada peça selecionada pela raiz do componente:
- porta ou janela;
- grupo mais alto (SketchUp, OBJ);
- item da biblioteca;
- armário no modo Cabinets.

Agregados e itens grudados continuam componentes próprios. O handler não age:
- fora do modo objeto;
- com modal da extensão ou `transform` rodando;
- com o interruptor desligado.

Alt + clique seleciona a peça e a deixa isenta até um clique sem Alt.

**Exclusão.** Antes, X/Delete só passava pelo `caffmob.delete_with_aggregates` quando havia agregados ou itens
grudados, e o `delete_door_window` apagava só os filhos diretos, deixando folha e ferragens da porta real na cena.
Agora:
- os dois apagam a subárvore inteira, de baixo para cima, e tiram o furo da parede;
- itens grudados são soltos no lugar;
- agregados próprios seguem a pergunta de sempre;
- parede, piso e teto continuam no Delete do Blender.

**Importação.** Antes, as malhas do OBJ entravam soltas e selecionadas. Agora entram num grupo com o nome do arquivo,
e o "Montar esquadria" aceita esse grupo.

**Aberturas.** A inserção de porta e janela continua a de hoje sem região. Com uma região marcada e válida, o vão
nasce com a largura e a altura exatas da região:
- a porta vai do piso ao topo da região;
- a janela usa a base da região como peitoril;
- Enter ou clique confirma, pelo mesmo `cut_wall` + `sync`;
- uma região inválida avisa e cai no modo de hoje.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- **R-01, R-02, R-03** (paredes e piso): não tocadas.
- **R-04, aderência ao segmento**: a porta na região é filha da parede, com rotação zero no espaço dela e `Dim Y`
  igual à espessura; o furo continua pelo `cut_wall` de sempre.
- **R-05, movimento constrangido**: o arraste no modo de inserção não mudou; no estado "na região" não há arraste.
- **R-06, clamping de limites**: a região que passa da ponta da parede é recusada (`region_core.OUTSIDE`), e os cantos
  da região são limitados à parede.
- **R-07, transição entre segmentos**: não tocada (só no modo de hoje).
- **R-08, peitoril fixo de portas**: a porta na região tem peitoril 0 mesmo quando a região começa acima do piso; a
  janela fica entre 0 e a altura da parede.
- **R-09, R-10** (plano de corte): não tocadas.

## Modificadas

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida. As mudanças de comportamento estão em regras
novas desta feature (RN-01 a RN-12 do `requirements.md`) e nas observações do `regression-watch.md`.
