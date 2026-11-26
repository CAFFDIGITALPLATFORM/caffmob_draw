# Adendo: Biblioteca CAFFMob — acervo por ambiente, card de detalhe e arraste

> Identificador: `biblioteca-acervo-detalhe-arraste`
> Data: `2026-11-26`
> Cenário: `legado`
> Extração de referência: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`,
> `_reversa_sdd/library_panel/design.md` e `_reversa_sdd/library_panel/requirements.md`
> Registro da entrega: `_reversa_forward/024-materiais-uv-preferencias/progress.jsonl`
> (`BIBLIOTECA-AMBIENTE`, `BIBLIOTECA-DETALHE`, `BIBLIOTECA-DETALHE-ARRASTE`, `BIBLIOTECA-DETALHE-VERIFICACAO`).
> Esta entrega não tem pasta própria em `_reversa_forward/` nem `legacy-impact.md`; o delta abaixo vem do progresso,
> do `CHANGELOG.md` 1.33.0 e da especificação da `library_panel`.

## Vigência

Vigente desde 2026-11-26.

## Resumo da entrega

A Biblioteca passou a ter acervo por ambiente: cada modelo e preset declara `environments` (COZ, DOR, BAN, SAL, ESC) e a
grade mostra só o acervo da categoria aberta, com **Dormitório** promovido a categoria fixa; catálogo antigo sem a chave
continua aparecendo em todos. Clicar num módulo da grade abre um **card branco de detalhe** com nome, ambiente, largura,
altura e profundidade pré-preenchidas pelo catálogo e pelo Padrão de Dimensões, mais o seletor dos cinco ambientes. O
botão **Inserir módulo** valida contra o Padrão de Dimensões (máximos do módulo, três faces contra a chapa máxima e
espessura da lateral), recusa medida inválida com mensagem no próprio card e, quando aceita, chama
`caffmob.library_insert_model` com `width_mm`/`height_mm`/`depth_mm`/`line`. Arrastar a célula cujo card está aberto
leva as mesmas medidas e ambiente; sem card, o arraste mantém o comportamento anterior, com os valores do catálogo.
Presets sem variação continuam inserindo com a largura do catálogo. O filtro por ambiente e a criação via
`caffmob.cabinet_builder` — com `structure_id` lido pelo Editor de Armário V2 — foram provados intactos.

Registros concluídos: **4** (`BIBLIOTECA-AMBIENTE`, `BIBLIOTECA-DETALHE`, `BIBLIOTECA-DETALHE-ARRASTE`,
`BIBLIOTECA-DETALHE-VERIFICACAO`), sem nenhum aberto; versão **1.33.0**.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/library_panel/design.md` | Visão de Camadas | componente-novo | Entram `detail_core.py` (núcleo puro do card e da validação) e `ops_detail.py` (digitação, confirmação e recusa); `ops_drag.py` e `popover.py` passam a receber medidas e linha |
| `_reversa_sdd/library_panel/design.md` | Interface — Estado (`props.py`) | delta-de-dados | `BTM_PG_LibraryState` ganha `detail_open`, `detail_key/model/name/line`, `detail_width/height/depth/thickness` e `detail_field/text/error`; `caffmob.library_insert_model` e `caffmob.library_drag` aceitam `width_mm`/`height_mm`/`depth_mm`/`line` |
| `_reversa_sdd/library_panel/design.md` | Fluxo Principal (F-10, F-13, F-14) | regra-alterada | O clique na célula (MAX) abre o card branco; Inserir valida e chama `library_insert_model` com as medidas/ambiente do card; arrastar a célula do card leva as mesmas medidas |
| `_reversa_sdd/library_panel/requirements.md` | Regras de Negócio (RN-01) | regra-alterada | **Dormitório** (`DOR`) passa a ser categoria fixa ao lado de Cozinha, Banheiro, Sala e Home office, e o acervo da categoria mostra só os modelos do ambiente |
| `_reversa_sdd/library_panel/requirements.md` | Regras de Negócio (RN-09) | regra-alterada | Inserir modelo passa a aceitar largura, altura, profundidade e linha do card; sem card, mantém a largura explícita do JSON e o padrão para o resto; presets sem variação continuam com os valores do catálogo |
| `_reversa_sdd/library_panel/requirements.md` | Regras de Negócio (RN-13) | regra-alterada | Com o card aberto, os cliques no card pertencem a ele; clicar fora (fora da grade) fecha; clicar na grade segue para seleção/arraste |
| `_reversa_sdd/library_panel/requirements.md` | Requisitos Funcionais (RF-05) | regra-alterada | A inserção do modelo pronto passa pelo card de detalhe, com validação contra o Padrão de Dimensões antes de criar |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-nova | Validação do card: máximos do módulo, três faces (largura × altura, largura × profundidade, altura × profundidade) contra a chapa máxima e espessura da lateral; a recusa deixa mensagem no card e não cria peça |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-nova | Cada modelo/preset declara `environments`; sem a chave, aparece em todos, mantendo o catálogo antigo válido |
| `_reversa_sdd/architecture.md` | Limites e organização | regra-alterada | A criação da Biblioteca continua em `caffmob.cabinet_builder`; o módulo carrega `structure_id` (ex.: `coz_inferior_divisoria`) e segue compatível com o Editor de Armário V2 |

## Regras sob vigilância

Nenhum item de vigilância próprio desta entrega foi registrado — não existe `regression-watch.md` da Biblioteca. A
prova ficou nos ensaios `tests/test_library_detail.py` (card, validação, `insert_props`) e
`tests/blender_biblioteca_detalhe.py` (filtro por ambiente, card, inserção, arraste, preset sem variação e estrutura do
Editor de Armário V2).

## Fontes

- `_reversa_forward/024-materiais-uv-preferencias/progress.jsonl` (registros `BIBLIOTECA-*`)
- `CHANGELOG.md` (seção 1.33.0)
- `_reversa_sdd/library_panel/design.md`
- `_reversa_sdd/library_panel/requirements.md`
- `caffmob_draw/library_panel/` (código: `detail_core.py`, `ops_detail.py`, `ops_drag.py`, `ops_click.py`, `popover.py`)
- `tests/test_library_detail.py`
- `tests/blender_biblioteca_detalhe.py`
