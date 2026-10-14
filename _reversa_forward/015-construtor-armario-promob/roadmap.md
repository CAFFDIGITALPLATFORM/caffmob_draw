# Roadmap: Construtor de armário CAFF MOBI com a arquitetura do Promob

> Identificador: `015-construtor-armario-promob`
> Data: `2026-10-14`
> Requirements: `_reversa_forward/015-construtor-armario-promob/requirements.md`
> Escopo (clarify Q1): arquitetura por tipo (RF-01 a RF-13), Cozinhas e Dormitórios completos e o design CAFF MOBI.
> Salas, Escritórios, Outros, caixa de gaveta (RF-18) e conjunto deslizante "Sobre a caixa" (RF-19, RF-20) ficam fora.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Hoje o módulo CAFF MOBI (`btm`) tem um tipo que só escolhe as medidas: `generate_cabinet_mesh`
(`caffmob_draw/geometry/mesh_gen.py:246`) e `synthetic_records` (`caffmob_draw/cutting/part_sources.py:217`) montam
sempre as mesmas cinco chapas.

A mudança tem três partes:

1. **Estrutura de caixa como dado.** Um catálogo JSON, `data/cabinet_structures.json`, lido por um núcleo puro
   `cabinet_editor/structures_core.py`, descreve cada estrutura:
   - o ambiente e o grupo de montagem;
   - as peças da caixa;
   - os componentes opcionais;
   - as medidas.
2. **Uma única função de peças.** A nova `structure.carcass_parts(...)` devolve as peças da caixa a partir da
   receita: laterais, bases, sarrafos, rodapé, fundo e tampo linear. A malha 3D e o plano de corte chamam a mesma
   função, então os dois nunca divergem.
3. **Módulo ligado à estrutura.** O módulo guarda só o identificador da estrutura (`btm_cabinet.structure_id`).

O fluxo novo começa numa galeria desenhada na GPU com os tokens CAFF MOBI da 014, aberta antes do editor de 7 abas
da 008. Os catálogos de Divisões, Gavetas e Internos passam a filtrar pelo ambiente da estrutura, e Dormitórios ganha
cabideiros, calceiros, sapateiras e porta-cintos.

Os módulos antigos (sem `structure_id`) continuam com a construção de hoje. Eles passam a ter estrutura só quando o
projetista abre o editor ou reaplica o padrão (RN-22).

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Simples por fora, milimétrico por dentro | O projetista escolhe uma estrutura numa galeria; peças, encontros e contas ficam na receita e no núcleo | respeita |
| II. Medir antes de cortar | A receita vem de 192 prints e 23 legendas (`inputs/`). As APIs `gpu`, `blf` e `bpy.utils.previews` são conferidas no RAG antes do código (`docs/rag/project/02_padroes_blender_5_2.md`) | respeita |
| III. Nada pregado | Estruturas em JSON. Largura do sarrafo, recuo da prateleira e queda do tubo saem do código: `mesh_gen.SHELF_SETBACK` = 0,02 e `extras.KICK_SETBACK` passam a vir do Padrão de Dimensões, com fallback nomeado | respeita |
| IV. Cada camada na espessura certa | `structures_core`, `carcass_parts` e `gallery_core` são puros e testáveis fora do Blender; `gallery.py` e `window.py` só desenham e despacham | respeita |
| V. Encaixes padronizados | Uma API (`carcass_parts`) serve malha e corte; a galeria reaproveita `library_panel/draw_kit.py` e `style.py` | respeita |
| VI. Chapas padrão: reaproveitar antes de criar | Reaproveita a árvore de extras da 008 (`btm_structure.extras`), os componentes SAR/ROD/TRA/TAMP do Configurador, os campos de rodapé do padrão e a mecânica de `CAFF_MONTAGEM` | respeita |
| VII. Caixote no esquadro | Um teste puro por estrutura do catálogo (lista de peças e medidas de corte) e uma fumaça `blender_015_*`. As fumaças 006, 008 e 012 continuam verdes | respeita |
| VIII. Fita de borda | Estrutura inválida no JSON é pulada com aviso que diz qual e por quê (RF-02); estrutura desconhecida num módulo cai na construção antiga com aviso | respeita |
| IX. Aproveitamento milimétrico | A galeria desenha miniaturas a partir da receita, com cache por estrutura e tamanho; nada é recalculado por evento de mouse sem mudança | respeita |
| X. Regulagem pelo projetista | Medidas, espessuras e peças marcadas ficam editáveis no padrão e na árvore (RN-23) | respeita |
| XI. Ergonomia do projetista | Nomes e fluxo do Construtor do Promob ("Selecione uma estrutura de caixa", "Inferior c/ Divisória", "Tipo: …") | respeita |

Nenhum conflito.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Catálogo de estruturas em `caffmob_draw/data/cabinet_structures.json`, lido e validado por `cabinet_editor/structures_core.py` (Python puro, padrão de `library_panel/models_core.py`). Item inválido é pulado com aviso | RN-02, RF-02, princípio III | Estrutura em classes Python por tipo (exige código para cada estrutura nova); estrutura dentro do `.blend` (não versiona nem diff) | 🟢 |
| D-02 | Nova função pura `structure.carcass_parts(recipe, w, h, d, thick, states, settings, params, back_setback, assembly)` → lista de `Part(role, box, component, name, length, width, edges)`. `generate_cabinet_mesh` e `synthetic_records` passam a chamá-la quando o módulo tem `structure_id`; sem ele seguem `layout` e `carcass_lengths` como hoje | Uma fonte única para 3D e corte (RN-10, RF-10); legado intocado (RN-22) | Duplicar a conta no corte (diverge); estender `layout` com flags (vira função de 15 parâmetros e quebra o legado) | 🟢 |
| D-03 | Papéis novos da caixa: `STRETCHER_FRONT`, `STRETCHER_BACK` (componente SAR), `STRETCHER_FULL` (Sarrafo Inteiro, SAR), `TOP_LINEAR` (Tampo Linear, TAMP), `TOE_KICK` (Rodapé da estrutura, ROD), `REAR_RAILS` (travessas traseiras do fundo "Travessas", TRA). `TOP` continua sendo a "Base Superior". Os papéis novos são ligados e desligados pela árvore da 008 (`btm_structure.extras`, chaves novas), sem novos `has_*` no `btm_cabinet` | Reaproveita a árvore com caixa de marcar (RN-12) e não mexe nos enums `ROLE_ITEMS` gravados em arquivos | Acrescentar `has_stretcher_*` e `thickness_*` ao `btm_cabinet` (cresce o PropertyGroup para cada peça nova) | 🟢 |
| D-04 | Com `structure_id`, a chave "Rodapés" da árvore é o rodapé da estrutura: a caixa sobe a altura do rodapé e a altura total fica igual (RN-05). Sem `structure_id`, os rodapés da 008 continuam abaixo da caixa (RN-CABINET_EDITOR-15). Pés e rodízios continuam abaixo da caixa nos dois casos | Mesmo comportamento do Promob nas estruturas novas sem quebrar módulos antigos | Mudar o comportamento da 008 para todos (muda o plano de corte de projetos orçados, contraria Q2) | 🟡 |
| D-05 | `btm_cabinet.structure_id` (texto; vazio = construção antiga). O `cabinet_type` (BASE/WALL/TALL) continua existindo, preenchido pelo grupo da estrutura, para as medidas do padrão e a altura de instalação | Mudança mínima no modelo; `cabinet_defaults` e as 4 bibliotecas seguem funcionando | Ampliar o enum `cabinet_type` para dezenas de valores (enum gravado por índice, frágil) | 🟢 |
| D-06 | Migração preguiçosa (RN-22): `bridge` (abrir o editor) e `standards/sync.apply_to_module` (reaplicar) preenchem `structure_id` pela tabela `legacy_map` do catálogo: (linha, tipo) → estrutura; ex. (COZ, BASE) → `coz_inferior_divisoria`. Abrir o `.blend` não muda nada | Clarify Q2 (a) | Converter no `load_post` (muda o corte sozinho, contraria Q2); botão "Converter todos" (Q2 c, não escolhido) | 🟢 |
| D-07 | Padrão de Dimensões: três campos novos por linha em Dimensões Externas: `stretcher_width` (100), `shelf_setback` (20), `hanger_rod_drop` (70). Os campos de rodapé (`toe_kick_height` 100, `toe_kick_setback` 50) já existem e passam a valer para o rodapé da estrutura | RN-23, Q5; `data/dimension_schema.py:145-161` já tem o mecanismo de campo numérico por linha | Constantes no núcleo (princípio III) | 🟢 |
| D-08 | Montagem por grupo (RN-08): a definição do padrão ganha `group_assembly` = {INFERIOR, SUPERIOR, DESPENSEIRO: {assembly LATERAL/BASE, back_kind ENCAIXADO/REBAIXADO/PREGADO/TRAVESSAS, rear_stretcher HORIZONTAL/VERTICAL}}, gravado no JSON do padrão e no XML como atributos `CAFF_GRUPO_*`, como o `CAFF_MONTAGEM` da 012. Sem valor no padrão, vale o da estrutura | Precedente `standards/io_promob.py:61` (CAFF_MONTAGEM); o Promob ignora IDs desconhecidos | Campos numéricos codificados (ilegível); uma montagem global só (contraria RN-08) | 🟡 |
| D-09 | Tipos de fundo (geometria e corte): ENCAIXADO = o fundo de hoje; REBAIXADO = a mesma caixa, com o corte +2 × rebaixo de 8 por lado (o "+16" de hoje); PREGADO = fundo sobre a face traseira, com a largura e a altura externas; TRAVESSAS = fundo encaixado entre duas travessas traseiras (TRA, 100 de largura). O fundo "Inteiro Recuado" da 008 continua como opção do módulo | Nomes do Configurador (`prints/jtEjP6DrzpM-0041-*`); medidas não vistas ficam como padrão editável | Só ENCAIXADO (contraria RN-08) | 🟡 |
| D-10 | Galeria de estruturas: `cabinet_editor/gallery_core.py` (puro: abas por ambiente, grade, hit-test, teclado) e `cabinet_editor/gallery.py` (operador modal `caffmob.structure_gallery`, desenho `POST_PIXEL` no `VIEW_3D`). Reaproveita `library_panel/draw_kit.py`, `style.py` e a Sora (`assets/fonts/Sora-SemiBold.ttf`). OK cria o módulo pelo `caffmob.cabinet_builder` com `structure_id` e abre o editor; Cancelar e Esc não criam nada nem geram passo de desfazer | Clarify Q3 (a); mesma mecânica validada na 014 | Diálogo `UILayout` com `template_icon_view` (sem cor da marca, contraria Q3); janela separada | 🟢 |
| D-11 | Miniaturas desenhadas ao vivo a partir da receita: elevação frontal das peças de `carcass_parts` em traço CAFF (contorno `TEXT_MUTED`, vão em teal `SUCCESS`), com cache em `GPUOffScreen` por (estrutura, escala) | Estrutura nova ganha miniatura sem arquivo (RF-02); traço único (RN-21) | PNGs gerados por script (somem do sincronismo quando a receita muda) | 🟡 |
| D-12 | Vista do editor (`cabinet_editor/window.py`): as constantes `FILL`, `EDGE`, `SELECTED`, `BACKGROUND` passam a vir de `library_panel/style.py` (Noite, laranja para a seleção, teal para o vão alvo), e o cabeçalho "Tipo: <estrutura>" é desenhado em Sora. Os painéis `UILayout` não mudam | Clarify Q3 (a) | Tema próprio do Blender (afeta toda a interface do usuário) | 🟢 |
| D-13 | Catálogo das abas (`cabinet_editor/catalog.py`): cada item ganha `environments` (vazio = todos) e as abas filtram pelo ambiente da estrutura. Itens novos: Montante, Invisível (divide, sem peça, fora do corte), Somente Divisão, Corrediça, Aramada, Corta Sar, c/ Reb, Não Divide o Fundo; Gavetas: Interna p/ trilho, Sapateira, Prateleira Corrediça, Externas; Internos: Cabideiro 01, Cabideiro 02, Cab Extensível, Tubo, Tubo s/ Reforço, Calceiros (Madeira Esq/Central/Dir, Aramado Esq/Dir), Sapateiras, Porta Cintos/Gravatas | RN-15, RN-16, RN-17 | Abas diferentes por ambiente (duplica painéis) | 🟢 itens / 🟡 geometria |
| D-14 | Internos de dormitório como `btm_extra` (kinds novos `HANGER_ROD`, `PANTS_RACK`, `SHOE_RACK`, `BELT_RACK`, acrescentados no fim do enum). O tubo, o calceiro aramado e o porta-cintos são ferragens (lista de ferragens da 008); o calceiro de madeira e a sapateira são chapas (`CabinetPart`) | Mesmo caminho dos internos da 008 (`scene_interiors.py`) | Objetos soltos fora do módulo (somem do corte) | 🟢 |
| D-15 | Largura de vão digitável (RF-14): `bays.py` ganha `widths` explícitos; digitar um vão redistribui a diferença entre os vizinhos imediatos, igualmente. Sem largura digitada, vale a fórmula de vãos iguais | RN-14 (`L6TMT6wV-xs [1:03]`) | Redistribuir em todos os vãos (o Promob mexe nos vizinhos) | 🟡 |
| D-16 | `data/library_models.json` ganha `structure_id` por modelo. `models_core` valida; sem o campo, vale o `legacy_map` | RN-13, RF-13 | Duplicar os modelos como estruturas | 🟢 |
| D-17 | Aba Deslizantes ganha o seletor de modo "No vão" / "Sobre a caixa"; "Sobre a caixa" aparece desabilitado com "Disponível numa próxima versão" | Q4 (a) com Q1 (b): a interface já nasce com os dois modos sem implementar o segundo | Não mostrar nada agora (o projetista não sabe que vem) | 🟡 |
| D-19 | Medidas iniciais: a largura vem da estrutura (500 no Inferior c/ Divisória, 1000 no Armário); altura e profundidade vêm do Padrão de Dimensões da linha e do grupo (hoje 720 × 550 no balcão BR). Os valores do Promob (700) são referência e entram só pelo padrão | Princípio III e RN-23: uma fonte de medida só; o padrão BR do projeto usa 720 sem tampo | Fixar 700 no catálogo (duas fontes de altura, divergentes) | 🟢 |
| D-18 | Textos novos pelo `tr()` com catálogo pt-BR/en-US (padrão do repo); nomes das estruturas com `label_pt` e `label_en` no JSON | RF-22 | Traduzir só a interface (galeria em inglês com nomes em português) | 🟢 |

## 4. Premissas

Não há `[DÚVIDA]` aberta (clarify 2026-10-14). As premissas abaixo vêm dos valores não vistos nos vídeos (lacunas 🟡
do requirements), cada uma como padrão editável:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Peças do Superior, do Gaveteiro, da Torre p/ Eletros e dos cantos (tabela RN-03, linhas 🟡) | §4 RN-03; §10 Lacunas | Peça a mais ou a menos nessas estruturas; corrigível no JSON, sem código |
| Sarrafo deitado (face larga na horizontal), 100 de largura; sarrafo traseiro horizontal por padrão | §4 RN-04; Q5 | Medida de corte errada do sarrafo; corrigível no padrão |
| Rebaixo de 8 por lado no fundo REBAIXADO e travessas de 100 no fundo TRAVESSAS | D-09 | Medida de corte do fundo; corrigível no padrão |
| Corta Sar = a divisória vai até o topo e o sarrafo é cortado em dois; c/ Reb = a divisória tem rebaixo para o fundo passar | §4 RN-15 (🟡) | Divisória com comprimento errado no corte |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| geometry (`mesh_gen`) | `_reversa_sdd/architecture.md#Limites e organização`; `caffmob_draw/geometry/mesh_gen.py:246` | regra-alterada | Com `structure_id`, a malha vem de `carcass_parts`; `SHELF_SETBACK` vem do padrão |
| cabinet_editor (`structure`) | `_reversa_sdd/cabinet_editor/design.md#F-09 structure.layout` | regra-alterada | Nova `carcass_parts` com os papéis novos (D-02, D-03, D-09); `layout` fica para o legado |
| cabinet_editor (`structures_core`) | — | componente-novo | Leitura e validação do catálogo de estruturas; `legacy_map` |
| cabinet_editor (`gallery_core`, `gallery`) | — | componente-novo | Galeria "Selecione uma estrutura de caixa" na GPU |
| cabinet_editor (`catalog`, `extras`, `bays`, `bridge`, `panels*`, `window`) | `_reversa_sdd/cabinet_editor/design.md#catalog.py, extras.py, bays.py…` | regra-alterada | Filtro por ambiente, itens de dormitório, rodapé da estrutura, vão digitável, migração na abertura, "Tipo: <estrutura>", tokens CAFF |
| cutting (`part_sources.synthetic_records`) | `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` | regra-alterada | Com `structure_id`, as peças vêm de `carcass_parts`, com os nomes de papel |
| standards (`dimension_schema`, `cabinet_defaults`, `sync`, `io_json`, `io_promob`, `model`) | `_reversa_sdd/domain.md#standards` | regra-alterada | Campos novos (D-07), `group_assembly` (D-08), migração no reaplicar (D-06) |
| library_panel (`models_core`, `ops_cabinet`) | `_reversa_forward/012-biblioteca-caffmob-chapas/` | regra-alterada | Modelo com `structure_id`; "Criar armário" abre a galeria |
| operators (`cabinet_builder`) | `caffmob_draw/operators/cabinet_builder.py:23` | regra-alterada | `build_module` e o operador recebem `structure_id` |
| arquivo do catálogo de estruturas | — | contrato-novo | `interfaces/catalogo-estruturas.md` |
| JSON/XML do Padrão de Dimensões | `_reversa_sdd/domain.md#standards` (RN-STANDARDS-16, -19, -20) | contrato-alterado | `interfaces/padrao-dimensoes-io.md` |
| exportação de produção (JSON do plano de corte) | `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md` | contrato-alterado | `interfaces/cut-plan-json.md` |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `btm_cabinet.structure_id` novo;
  - chaves novas em `btm_structure.extras` (papéis da estrutura);
  - kinds novos no fim de `EXTRA_KIND_ITEMS` e de `DIVISION_KIND_ITEMS`;
  - três campos numéricos por linha no Padrão de Dimensões e `group_assembly` na definição;
  - `structure_id` nos modelos da biblioteca;
  - arquivo novo `cabinet_structures.json`.

  Nada é removido. Os módulos sem `structure_id` não mudam.
- Detalhe completo em: `_reversa_forward/015-construtor-armario-promob/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Catálogo de estruturas (`cabinet_structures.json`) | arquivo | `_reversa_forward/015-construtor-armario-promob/interfaces/catalogo-estruturas.md` |
| Padrão de Dimensões: JSON do CAFF e XML do Promob | arquivo | `_reversa_forward/015-construtor-armario-promob/interfaces/padrao-dimensoes-io.md` |
| Exportação de produção (JSON do plano de corte) | arquivo | `_reversa_forward/015-construtor-armario-promob/interfaces/cut-plan-json.md` |

## 8. Plano de migração

1. Nada converte ao abrir o `.blend`. Módulos sem `structure_id` usam `layout` e `carcass_lengths` como hoje (D-02).
2. Ao abrir um módulo antigo no editor, `bridge` aplica o `legacy_map` (D-06). O instantâneo de Cancelar é tirado
   **antes** da conversão, então Cancelar devolve a construção antiga.
3. Ao reaplicar o padrão, `sync.apply_to_module` converte os módulos selecionados pelo plano da 012. O diálogo de
   reaplicar já mostra quantos módulos mudam; acrescenta a linha "N módulos passam para a estrutura nova".
4. Padrões salvos antes desta feature: os campos novos assumem os valores de fábrica (100, 20, 70) e `group_assembly`
   fica vazio, valendo o da estrutura. Os importadores JSON e XML aceitam o arquivo sem os campos novos.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| A malha e o corte divergirem nas estruturas novas | alto | baixo | Uma função só (D-02) e um teste que compara as peças da malha com os registros do corte por estrutura |
| Números do plano de corte mudarem em módulos antigos | alto | baixo | Caminho antigo intocado sem `structure_id`; teste de regressão dos uids sintéticos da 008 |
| Enum gravado por índice corromper arquivos | alto | baixo | Itens novos só no fim de `EXTRA_KIND_ITEMS` e `DIVISION_KIND_ITEMS`; fumaça que abre um `.blend` da 014 |
| XML do Promob recusar atributos `CAFF_GRUPO_*` | médio | baixo | Mesmo mecanismo do `CAFF_MONTAGEM` (o Promob ignora IDs desconhecidos); teste de ida e volta |
| Peças inferidas (🟡) das estruturas não vistas | médio | médio | Ficam em JSON, corrigíveis sem código; pendência de conferir num Promob instalado (§4) |
| Galeria GPU lenta com muitas miniaturas | baixo | baixo | Cache por (estrutura, escala) (D-11); só células visíveis desenhadas (`grid_core`) |
| Volume da feature (catálogo, galeria, 3 abas, padrão, corte) | médio | médio | Fases independentes no `actions.md`: núcleo e corte primeiro, galeria e design depois, dormitório por último; cada fase com teste |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Um teste puro por estrutura de Cozinhas e Dormitórios (peças e medidas de corte do caso de referência da §7 do
      requirements)
- [ ] `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erro
- [ ] Fumaça nova `tests/blender_015_*` verde, e as fumaças 006, 008 e 012 continuam verdes
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-14 | Versão inicial gerada por `/reversa-plan` | reversa |
