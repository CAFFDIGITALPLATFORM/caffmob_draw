# Legacy impact: 015-construtor-armario-promob

> Data: `2026-10-14`
> Feature: Construtor de armário CAFF MOBI com a arquitetura do Promob
> Base: `_reversa_sdd/architecture.md` (re-extração 2026-10-10), `_reversa_sdd/domain.md`
> Execução: `actions.md` T001 a T044; registro em `progress.jsonl`

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/cabinet_editor/structures_core.py` | cabinet_editor | componente-novo | MEDIUM | Catálogo de estruturas de caixa (D-01) |
| `caffmob_draw/data/cabinet_structures.json` | data | delta-de-contrato-externo | MEDIUM | Arquivo novo do catálogo (`interfaces/catalogo-estruturas.md`) |
| `caffmob_draw/cabinet_editor/structure.py` | cabinet_editor (`structure`) | regra-nova | HIGH | `carcass_parts`: peças por estrutura, fonte única de malha e corte (D-02 a D-04, D-09) |
| `caffmob_draw/cabinet_editor/structure_inputs.py` | cabinet_editor | componente-novo | MEDIUM | Lê do módulo e do padrão as entradas de `carcass_parts` |
| `caffmob_draw/geometry/mesh_gen.py` | geometry | regra-alterada | HIGH | Módulo com estrutura monta a malha pela estrutura; sem estrutura, como antes |
| `caffmob_draw/cutting/part_sources.py` | cutting | regra-alterada | HIGH | Módulo com estrutura gera um registro por peça da estrutura; sem estrutura, idêntico (fixture) |
| `caffmob_draw/cutting/json_exporter.py`, `part_extractor.py` | cutting | delta-de-contrato-externo | HIGH | JSON de produção 2.2.0 → 2.3.0 (`modules[].structure_id`, status novos) |
| `caffmob_draw/cutting/hardware.py` | cutting | regra-nova | LOW | Códigos de ferragem de roupeiro; aramada e corrediça contam pela divisão |
| `caffmob_draw/data/properties.py` | data | delta-de-dados | MEDIUM | `btm_cabinet.structure_id` |
| `caffmob_draw/cabinet_editor/data_props.py` | cabinet_editor | delta-de-dados | MEDIUM | Itens no fim dos enums; `btm_division.variant` e `bay_width` |
| `caffmob_draw/cabinet_editor/state.py` | cabinet_editor | regra-alterada | MEDIUM | Instantâneo e assinatura do rascunho com estrutura e chapas presentes |
| `caffmob_draw/cabinet_editor/bridge.py` | cabinet_editor | regra-alterada | HIGH | Migração ao abrir (RN-22), `set_structure`, `set_bay_width`, internos de roupeiro, variantes de divisão |
| `caffmob_draw/cabinet_editor/ops_editor.py` | cabinet_editor | regra-alterada | MEDIUM | Migração depois do instantâneo do Cancelar |
| `caffmob_draw/cabinet_editor/bays.py` | cabinet_editor | regra-alterada | MEDIUM | Largura de vão digitável (RN-14, D-15) |
| `caffmob_draw/cabinet_editor/divisions.py`, `scene_divisions.py` | cabinet_editor | regra-nova | MEDIUM | Invisível e Somente Divisão sem peça; Corta Sar corta os sarrafos |
| `caffmob_draw/cabinet_editor/catalog.py`, `props.py` | cabinet_editor | regra-alterada | MEDIUM | Itens por ambiente; árvore com peças da estrutura; campos virtuais novos |
| `caffmob_draw/cabinet_editor/extras.py`, `scene_extras.py` | cabinet_editor | regra-alterada | MEDIUM | Com estrutura, rodapé da 008 não gera peça; rodízios; recuo do rodapé pelo padrão |
| `caffmob_draw/cabinet_editor/wardrobe.py`, `scene_interiors.py` | cabinet_editor | componente-novo | LOW | Internos de roupeiro |
| `caffmob_draw/cabinet_editor/gallery_core.py`, `gallery.py`, `__init__.py` | cabinet_editor | componente-novo | MEDIUM | Galeria "Selecione uma estrutura de caixa" (GPU, tokens CAFF MOBI) |
| `caffmob_draw/cabinet_editor/window.py` | cabinet_editor (vista) | regra-alterada | LOW | Cores da família Noite; "Tipo: …" em Sora |
| `caffmob_draw/cabinet_editor/panels*.py`, `ops_actions.py` | cabinet_editor (UI) | regra-alterada | LOW | Filtro por ambiente, vão digitável, modo dos deslizantes, inserção dos itens novos |
| `caffmob_draw/customize/adapters/btm.py` | customize | regra-alterada | HIGH | Vão das divisões e vista do editor pela estrutura |
| `caffmob_draw/operators/cabinet_builder.py` | operators | regra-alterada | HIGH | `structure_id`: o módulo nasce com a estrutura |
| `caffmob_draw/library_panel/ops_cabinet.py`, `models_core.py`, `popover.py` | library_panel | regra-alterada | MEDIUM | "Criar armário" abre a galeria; modelos com estrutura |
| `caffmob_draw/data/library_models.json` | data | delta-de-dados | LOW | `structure_id` por modelo |
| `caffmob_draw/standards/group_assembly.py`, `model.py`, `api.py` | standards | regra-nova | MEDIUM | Montagem por grupo na definição e no rascunho |
| `caffmob_draw/standards/cabinet_defaults.py` | standards | regra-nova | MEDIUM | Medidas e parâmetros por estrutura (D-19) |
| `caffmob_draw/standards/sync.py`, `operators/ops_standards.py` | standards | regra-alterada | HIGH | Reaplicar o padrão migra o módulo antigo; diálogo conta os que mudam |
| `caffmob_draw/standards/io_json.py`, `io_promob.py` | standards | delta-de-contrato-externo | MEDIUM | `group_assembly` e atributos `CAFF_*` novos (`interfaces/padrao-dimensoes-io.md`) |
| `caffmob_draw/data/dimension_schema.py` | data | delta-de-dados | MEDIUM | 3 campos externos por linha |
| `caffmob_draw/data/i18n.py`, `translations/construtor_015.json` | data | regra-alterada | LOW | Nomes das estruturas no catálogo de tradução; 117 textos |
| `caffmob_draw/assets/dimension_refs/ext_*.png` (3) | assets | delta-de-dados | LOW | Imagens de referência dos campos novos |
| `tools/render_dimension_refs.py` | ferramentas | regra-alterada | LOW | Caminho antigo `blendertomob/` corrigido; `--only` |
| `caffmob_draw/cabinet_editor/thumbnails/*.png` (24 novas), `tools/render_cabinet_thumbnails.py` | cabinet_editor (UI) | delta-de-dados | LOW | Miniaturas dos itens novos do catálogo; `--only-missing` não regrava as da 008 |
| `tests/` (asserções de versão do JSON, `test_cabinet_catalog`) | testes | regra-alterada | LOW | 2.2.0 → 2.3.0; o teste das divisões da 008 confere os itens dela sem contar os novos por ambiente |

## Diff conceitual por componente

**cabinet_editor e geometry.** Antes, o tipo do módulo CAFF MOBI só escolhia medidas, e a malha era sempre de cinco
chapas. Agora o módulo pode ter uma estrutura de caixa do catálogo. Com estrutura, `carcass_parts` monta as peças:
- o balcão com sarrafos no lugar da Base Superior;
- o roupeiro com rodapé dentro da altura;
- a variante "até Piso" com as laterais no chão;
- o fundo pelo tipo do grupo.

A malha, o vão das divisões, a vista do editor e o corte leem dessa mesma função. Sem estrutura, todo o caminho antigo
fica intacto: a regressão do corte é comparada com uma fixture gravada antes da mudança.

**Editor.** Ao abrir um módulo antigo, ele passa para a estrutura equivalente depois do instantâneo, então o Cancelar
devolve a construção antiga. A árvore mostra as peças da estrutura. As abas filtram o catálogo pelo ambiente. Também
entram:
- a largura de vão digitável;
- as divisões sem peça (Invisível, Somente Divisão) e o Corta Sar;
- os internos de roupeiro;
- o seletor de modo dos deslizantes, com "Sobre a caixa" desabilitado.

**Produção.** O plano de corte lista "Sarrafo frontal", "Rodapé frontal", "Travessa traseira" etc. O fundo usa
FUN_SUP e FUN_ALT nos grupos SUPERIOR e DESPENSEIRO. O JSON vai para 2.3.0 com `structure_id`.

**Padrão de Dimensões.** Entram três medidas por linha e a montagem por grupo, ambas editáveis, além da ida e volta
em JSON e XML. Reaplicar o padrão migra os módulos antigos.

**Biblioteca.** "Criar armário" abre a galeria. Os modelos prontos nascem com estrutura.

## Desvios e limites registrados nesta rodada

- **Gavetas de dormitório (T032):** Interna p/ trilho, Sapateira, Prateleira Corrediça e Externas usam o caminho de
  gavetas da biblioteca. O módulo CAFF MOBI não tem gavetas, então nele aparece o aviso que já existia. A "de baixo
  mais alta" não é aplicada (🟡).
- **Fundos ENCAIXADO e REBAIXADO (D-09):** dão a mesma geometria e o mesmo corte. A diferença de rebaixo não é
  modelada (🟡).
- **Divisórias c/ Reb, Não Divide o Fundo e Montante:** só ficam gravadas, porque o fundo já é uma peça única (🟡).
- **Sapateira:** é chapa reta, sem inclinação (🟡).
- **Galeria (D-11):** a miniatura usa cache da geometria por estrutura em vez de `GPUOffScreen`.
- **Estruturas com mais de um vão:** nascem com 1 vão; o Número de vãos é ajustado no editor.
- **`STRUCTURE_UNKNOWN`:** vai no módulo (`modules[].limit_status`), e não numa peça.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam valendo como estavam:
- RN-CABINET_EDITOR-01 (fila, desfazer só no OK ou no Aplicar, Cancelar reaplica o instantâneo; o instantâneo ganhou
  campos, a regra é a mesma)
- RN-CABINET_EDITOR-02 a RN-CABINET_EDITOR-11 (erros, faixas, ajustes automáticos, remoção KEEP/EXTEND/SHRINK,
  divisões por subvão, subvão mínimo de 50, material da divisória, filhos diretos da raiz)
- RN-CABINET_EDITOR-13, -14, -16 a -21 (distanciador, base superior recuada, gavetas e portas no vão da biblioteca,
  painel p/ eletro, deslizantes no vão, fundo recuado, montagem LATERAL/BASE, clique na vista)
- RN-STANDARDS-01 a -11, -13 a -19, -21 a -24 (unidades, embutidas, duplicação, validação, rascunho, plano,
  migrações, importações e escrita atômica)
- RN-LIBRARY_PANEL-01 e -02

## Modificadas

| Regra (🟢) | Antes | Depois |
|---|---|---|
| RN-CABINET_EDITOR-12 | N vãos de largura sempre igual | Largura de um vão pode ser digitada; os livres dividem o resto; o último é calculado |
| RN-CABINET_EDITOR-15 | Pés e rodapés ficam abaixo da caixa; o módulo não é levantado | Vale só sem estrutura. Com estrutura, o rodapé levanta a caixa dentro da altura total; pés e rodízios continuam abaixo |
| RN-STANDARDS-12 | O fundo usa FUN_INF em todos os tipos | Vale só sem estrutura. Com estrutura: FUN_INF, FUN_SUP ou FUN_ALT pelo grupo |
| RN-STANDARDS-20 | O XML reexporta o `raw` e só acrescenta `CAFF_MONTAGEM` | Acrescenta também `CAFF_GRUPO_*`, `CAFF_SARRAFO_*`, `CAFF_RECUO_PRAT_*` e `CAFF_CABIDEIRO_*` no fim |
| RN-LIBRARY_PANEL-03 | Modelos com medidas do padrão e largura explícita | Também nascem com a estrutura de caixa do modelo (ou a equivalente) |
| Contrato JSON de produção (008, 2.2.0) | `schema_version` 2.2.0 | 2.3.0, com `modules[].structure_id` e ferragens novas |
