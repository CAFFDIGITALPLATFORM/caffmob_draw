# Cross-check: 011-selecao-por-componente

> Data: `2026-10-09`
> Gerado por `/reversa-audit` (somente leitura: nenhum artefato da feature foi alterado).
> Artefatos analisados:
> - [`requirements.md`](../requirements.md)
> - [`roadmap.md`](../roadmap.md)
> - [`actions.md`](../actions.md)
> - apoio: [`data-delta.md`](../data-delta.md), `_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md`
>
> A feature já foi codificada (28 de 28 ações `[X]`). Por isso os achados apontam divergências de documentação; nenhum
> deles bloqueia o código entregue.

## Resumo

| Severidade | Quantidade |
|------------|-----------:|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 5 |
| LOW | 3 |

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Cobertura | O RF-11 (guia do usuário) não tem decisão no roadmap. Só as ações T027 e T028 o cobrem | `requirements.md` §5 RF-11; `roadmap.md` §3 (ausente) |
| A002 | MEDIUM | Cobertura | A mitigação do risco "Alt + clique × Emular mouse de 3 botões" promete que a seção Selecionado lista as peças da raiz. Não há ação para isso; o guia só manda desligar o interruptor | `roadmap.md` §9; `actions.md` (ausente); T027 |
| A003 | MEDIUM | Consistência | Premissa do roadmap: apagar uma peça intermediária leva os descendentes, mesmo com o interruptor desligado. A RN-09 diz "Desligado, a seleção e a exclusão de uma peça voltam ao comportamento do Blender: só a peça" | `requirements.md` RN-09; `roadmap.md` §4 |
| A004 | MEDIUM | Cobertura | O RNF de desempenho (menos de 50 ms com 2.000 objetos e 10 níveis) não tem ação que meça. O roadmap só cita a meta na mitigação | `requirements.md` §6; `roadmap.md` §9; `actions.md` (ausente) |
| A005 | MEDIUM | Consistência | Roadmap e actions nomeiam os operadores `btm.component_pick`, `btm.component_click` e `btm.wall_region`. A entrega usou `caffmob.*`, registrado só no histórico do roadmap | `roadmap.md` §1, D-03, D-04, D-10; `actions.md` T010, T012, T018 |
| A006 | MEDIUM | Consistência | O roadmap (§1 e §5) põe propriedades, Alt + clique e keymaps em `selection/component_select.py`. O actions divide em `component_props.py`, `component_select.py` e `component_pick.py` | `roadmap.md` §1, §5; `actions.md` T001, T009, T010 |
| A007 | LOW | Consistência | O D-10 e o T018 falam em desenho `POST_VIEW`; o texto da região exige `POST_PIXEL`. O D-10 também fala em `UNDO` "só na confirmação", mas a região é estado de sessão, sem undo | `roadmap.md` D-10; `actions.md` T018 |
| A008 | LOW | Sanidade do actions | O T003 (testes de exclusão) usa os objetos simulados do arquivo do T004, mas não declara a dependência | `actions.md` T003 |
| A009 | LOW | Sanidade do actions | A descrição do T012 contém um checkbox literal ("marcar `[X]`"), que pode confundir contadores de progresso que procuram `[X]` fora da coluna Status | `actions.md` T012 |

## Impacto e direção dos achados HIGH

**A001, RF-11 sem decisão no roadmap.** O guia foi escrito (T027, T028), então não falta entrega. Falta
rastreabilidade: quem ler só o roadmap não sabe que a feature tem documentação de usuário, nem onde ela fica.
Direção: edição manual do `roadmap.md` (uma decisão ou uma linha no critério de pronto apontando
`docs/usuario/selecao-por-componente.md` e a seção nova de `editor-paredes-e-mover-sobre.md`).

## Itens verificados que passaram

**Cobertura, requisito → decisão**
- RF-01 e RF-02 → D-01, D-02. RF-03 → D-05, D-06. RF-04 → D-09. RF-05 → D-02, D-03. RF-06 → D-01 (regra 1), D-05.
- RF-07 → D-08. RF-08 → D-04. RF-09 → D-10, D-11, D-12. RF-10 → D-11, D-12. RF-12 → D-07.

**Cobertura, decisão → ação**
- D-01 → T004, T006. D-02 → T009. D-03 → T011, T012. D-04 → T010. D-05 → T003, T008, T013. D-06 → T014.
- D-07 → T006, T009. D-08 → T001, T016, T017. D-09 → T015. D-10 → T002, T018, T020. D-11 → T005, T007.
- D-12 → T019.

**Cobertura, cenários Gherkin**
- Os 12 cenários têm ação:
  - maçaneta → T009, T023;
  - caixa → T011;
  - excluir a porta → T013, T014, T023;
  - OBJ → T015, T023;
  - agregado → T023;
  - Alt + clique → T010, T011;
  - armário no modo gabinete → T023;
  - interruptor desligado → T023;
  - porta e janela na região → T019, T024;
  - região que não cabe → T024;
  - sem região → T024.

**Consistência**
- Os IDs citados existem: RN-01 a RN-12, RF-01 a RF-12, D-01 a D-12, T001 a T028.
- O `data-delta.md` bate com o roadmap §6: `btm_component_select`, `btm_component_exempt`, `btm_wall_region`.
- Não há `interfaces/`, e o roadmap §7 diz n/a.

**Coerência com o legado**
- Nenhuma decisão contradiz regra 🟢 do `_reversa_sdd/domain.md`:
  - R-04: a abertura na região é filha da parede, com a espessura dela;
  - R-06: a região fora da parede é recusada;
  - R-08: a porta tem peitoril 0, e a janela fica entre o piso e a altura da parede.
- `_reversa_sdd/architecture.md#3` existe. As seções `hb_placement/requirements.md` e `domain.md#2.2` existem.

**Sanidade do actions**
- Todas as dependências apontam para IDs existentes, e não há ciclo.
- Maior cadeia: 7 (T004 → T006 → T009 → T010 → T021 → T023 → T026), igual ao resumo.
- Nenhum par de ações `[//]` divide arquivo alvo. Os pares no mesmo arquivo têm a segunda ação sem `[//]` e
  dependente da primeira:
  - T006 e T008;
  - T010 e T012;
  - T014 e T019;
  - T023 e T026.
- O resumo bate: 28 ações, 21 `[//]`.

## Fora do escopo desta auditoria: pedido novo recebido nos argumentos

Os argumentos desta execução trazem um **pedido de feature nova**. A auditoria não implementa nem planeja; o caminho
é `/reversa-requirements` com esse texto. A pré-checagem abaixo foi feita só lendo o código, para alimentar os
requisitos:

| Parte do pedido | O que já existe | Lacuna |
|-----------------|-----------------|--------|
| Biblioteca fora da barra lateral, num painel flutuante compacto no topo da viewport, com o título "BIBLIOTECA CAFFMOB" | A galeria fica em Inserir na barra lateral (`ui/sidebar_insert.py`, por biblioteca frameless, face frame e closets, mais `object_library/`). O HUD da viewport já desenha botões no topo (`operators/viewport_hud.py`) | Nenhum painel flutuante próprio; decidir entre um widget do HUD e um popover no cabeçalho da viewport |
| Primeiro botão "Criar armário"; depois as categorias Cozinha, Banheiro, Sala, Home office e "Criar categoria" | O construtor de armário (008) e o editor de armário (004/006) existem | Não há categorias de ambiente nem categoria criada pelo usuário; definir onde a categoria fica salva (biblioteca do usuário, `extension_path_user`) |
| Todo armário segue o padrão global de dimensões do arquivo anexado | O anexo é **idêntico** a `tests/fixtures/dimensionexport_me_moveis.xml`. Já existem o importador `standards/io_promob.py`, o modelo `standards/model.py` (chaves como `COZ.sheets.LAT.thickness`) e a sincronização `standards/sync.py` | Confirmar se **todos** os caminhos de criação (bibliotecas legadas, módulo rápido, construtor 008) leem o padrão. Hoje a migração cobre espessuras de carcaça, fundo, porta e prateleira (`standards/migration.py`) |
| Montagem por chapas, com espessura e **base passante ou lateral passante** | Espessuras por chapa existem no padrão | Nenhuma ocorrência de "passante" nem equivalente (`through`) no código: a regra de montagem é nova |
| Manifesto anexo | Documento de princípios de produto e arquitetura (componentização, nada fixo no código, interface que esconde a complexidade) | Candidato a `.reversa/principles.md` via `/reversa-principles`; o projeto ainda não tem esse arquivo |

Pontos a esclarecer no `/reversa-clarify` da feature nova:
1. Os armários já colocados mudam quando o padrão global muda, ou só os novos seguem o padrão?
2. "Base passante" ou "lateral passante" é escolhido por módulo, por categoria ou só no padrão global?
3. As categorias trazem só armários do CAFFMob, ou também itens da biblioteca de objetos (009)?
