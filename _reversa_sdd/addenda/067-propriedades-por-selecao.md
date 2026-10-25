# Adendo: 067-propriedades-por-selecao

- **Feature:** 067, nova interface do CAFFMob Draw: as propriedades pertencem ao objeto selecionado
- **Data:** 2026-10-24
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)
- **Entrega:** sincronização parcial, onda 1 (versão 1.9.0 ainda por publicar), commits `e307ccf2` e `cd507483` na
  branch `feat/067-onda1-selecao`. As ondas 2 a 7 complementam este adendo com seções `## Atualização`

## Vigência

Vigente desde 2026-10-24.

## Resumo da entrega

A 067 troca o painel por tipo do objeto ativo por um painel relacional ao selecionado, em 7 ondas. A onda 1 entrega:

- **Alvo resolvido:** um alvo da seleção (snapshot) refeito fora do draw, lido pelo painel, pelo menu do botão direito
  e pelas cotas. Os 15 tipos da auditoria têm adaptador próprio, e o tipo desconhecido cai num fallback rotulado.
- **Cabeçalho e modos:** o cabeçalho mostra tipo, escopo e caminho do dono, com "Selecionar conjunto". Os modos
  Essencial e Completa ficam nas preferências; a Completa guarda toda capacidade da 1.8.0.
- **Chapa:** mostra as próprias medidas. A de biblioteca é somente leitura com o motivo; a autoral edita a própria
  malha. Construir → Chapa nasce do Padrão de Dimensões ativo com o material "MDF Branco".
- **Cotas:** fixas sempre para a seleção, sem chave, no escopo Peça ou Conjunto; as antigas viram ação na Completa.
- **Padrão de Dimensões:** persiste num banco local (`padroes.sqlite3`), com exportar e importar tudo.
- **Corte e revestimento:** o veio da peça vai ao corte; o revestimento é editado num rascunho e refeito só em
  "Aplicar".

Ações concluídas: **63 de 176** (onda 1 inteira, menos a versão 1.9.0, o aceite do titular, este adendo e o fechamento
do #142).

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|---|---|---|---|
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Limites e organização | componente-novo | Camada nova `target/` (resolvedor, snapshot, capacidades, CommandRouter, ViewModel e adaptadores) entre `selection` e `ui`; o painel Selecionado passa a depender dela |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Fluxos entre componentes | regra-alterada | O fluxo 3 (seleção → cotas → mover) passa pelo snapshot do alvo, com escopo Peça ou Conjunto; a peça gerada pelo módulo nunca é alvo móvel |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Persistência e unidades | delta-de-dados | Além do `.blend`, o Padrão de Dimensões da marcenaria fica em `extension_path_user(<pacote>, "standards")/padroes.sqlite3` |
| `_reversa_sdd/selection/requirements.md` | RN-16 | regra-alterada | O painel não mostra as dimensões do módulo numa peça ou frente; `editable_dimensions` continua valendo para quem a chama |
| `_reversa_sdd/selection/requirements.md` | RN-21 | regra-alterada | `element_size.element` continua mapeando frente e peça para o módulo (aviso e Redimensionar), mas o painel mede a própria peça |
| `_reversa_sdd/overlays/requirements.md` e `addenda/bug-BUG-20261023-HYCE-v001.md` | Cotas fixas | regra-alterada | Leia a versão `-v002` abaixo: sem a chave "Medidas laterais", cotas sempre para a seleção |
| `_reversa_sdd/addenda/066-reparo-do-addon-caffmob.md` | D-10, RF-013, RF-014, RF-020 | regra-removida | A chave das cotas sai da interface; "chave desligada não desenha" e "as laterais suprimem as antigas" não valem mais |
| `_reversa_sdd/standards/requirements.md` | Responsabilidades e RN-10 a RN-19 | delta-de-dados | Os operadores do padrão gravam também no banco local; abrir arquivo traz do banco os uids que faltam e nunca grava nele (067 D-26, D-27) |
| `_reversa_sdd/cutting/requirements.md` | Origem das peças (`part_sources`) | regra-alterada | `PartRecord.grain` sai de `btm_part.grain` (H → HORIZONTAL, V → VERTICAL) nas peças CUTPART e na geometria livre; sem `btm_part`, NONE |
| `_reversa_sdd/aggregates/requirements.md` | Agregados e folhas | regra-alterada | Os botões do armário autoral ganham `poll` com motivo; `member_remove` sem membro devolve `CANCELLED` |
| `_reversa_sdd/ui/requirements.md` | Seção Selecionado e Construir | regra-alterada | Selecionado desenha o ViewModel do alvo (Essencial/Completa); Construir por finalidade (Ambiente, Móveis, Chapas e peças, Iluminação) |
| `_reversa_sdd/geometry_free/requirements.md` | Criação | componente-novo | `caffmob.geometry_sheet` (Construir → Chapa) e o material "MDF Branco" achado pela marca `btm_builtin_material` |

### Versões `-v002` das regras superadas (067 D-32, RF-143)

- **Cotas fixas (HYCE-v002, ver `bug-BUG-20261023-HYCE-v002.md`):** as quatro cotas fixas aparecem sempre que há
  seleção com alvo móvel, sem a chave "Medidas laterais", que continua registrada só para ler arquivos antigos. O alvo
  vem do snapshot, no escopo de `WindowManager.btm_target.cota_scope`. Parede, piso, teto, porta, janela, luz e câmera
  soltas dizem "indisponível para <motivo>". As cotas antigas (afastamento, anterior, posterior, Mover na Parede) só
  aparecem em "Cotas antigas" da Completa, para módulo.
- **selection RN-16 (-v002):** campos de dimensão do painel por tipo: módulo e porta/janela como antes; peça, frente,
  membro, folha e geometria mostram duas medidas da face e a espessura da própria peça (`target/part_geometry`).
- **selection RN-21 (-v002):** sem mudança em `element_size`; o painel deixa de usá-lo para medir.
- **standards (-v002):** o padrão da marcenaria persiste fora do arquivo; arquivo novo recebe as definições do banco e
  a última ativa; uid igual com conteúdo diferente vale o do arquivo, dentro do arquivo.

## Regras sob vigilância

W001, W002, W003, W004 e W005, em `caff_systems:_reversa_forward/067-propriedades-por-selecao/regression-watch.md`.

## Fontes

- `caff_systems:_reversa_forward/067-propriedades-por-selecao/legacy-impact.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/regression-watch.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/requirements.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/roadmap.md` (D-02 a D-13, D-26 a D-29, D-32)
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/progress.jsonl`

## Atualização 2026-10-25 (onda 2, addon 1.10.0)

Onda 2 da 067 (acabamentos por domínio, soltar textura com pergunta, assistente de classificação e o U): ações T009,
T023 a T026, T057 a T064, T096 a T099, T132, T174 e T175, na branch `feat/067-onda2-acabamentos`.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/customize/requirements.md` | RN-13 (grupos de material pela função da peça) | regra-alterada | Os grupos viram os domínios INTERNAL, EXTERNAL, FRONTS e EDGE (`customize/finish_core`); ver RN-13 (-v002) abaixo |
| `_reversa_sdd/domain.md` | RN-CUSTOMIZE-10 (grupos de material) | regra-alterada | A parte dos grupos vira domínio por face ou por peça; a parte do veio (`ROTATED`) muda na onda 3 |
| `_reversa_sdd/customize/` | Personalização do armário autoral | regra-alterada | Materiais habilitados quando há papéis de acabamento cadastrados; frentes, puxadores, divisões e estilos continuam recusados |
| `_reversa_sdd/library_panel/` | Soltar textura | regra-alterada | Soltar abre "Onde deseja aplicar a textura?" (`caffmob.finish_drop`); o download espera o OK |
| `_reversa_sdd/geometry/` | Construtor BTM (`mesh_gen`) | delta-de-dados | Atributo de face `btm_face_role` (1 interna, 2 aparente, 3 borda) gravado pelo construtor |
| `_reversa_sdd/aggregates/` | Criar componente | componente-novo | `caffmob.component_from_selection` (U em Object Mode) sobre `ops_authored.adopt` |
| n/a | `Object.btm_finish`, `btm_part.finish_role` | delta-de-dados | Atribuição por domínio na raiz do dono ou na peça; M-03 migra os grupos antigos com origem MIGRATED, sem mudar a aparência |

### Versões `-v002` das regras superadas na onda 2 (067 D-32, RF-143)

- **customize RN-13 (-v002):** o acabamento de um móvel é por domínio. Interno cobre as faces internas da caixa e do
  fundo, prateleiras e divisórias; Externo cobre as faces aparentes da caixa (inclusive a face de trás do fundo) e as
  frentes; Frentes cobre só as frentes, que nascem com veio V e têm o veio próprio; Fita cobre as bordas das chapas.
  O papel vem do construtor: por face no atributo `btm_face_role` do módulo BTM, por peça nas bibliotecas HB (pelo
  componente do Padrão de Dimensões, `spec.group_of_component`, o fundo seguindo a caixa) e no armário autoral (pelo
  assistente ou pelo papel do membro). Peça sem papel não recebe acabamento por suposição: o assistente classifica.
  A escolha fica em `btm_finish` (dono ou peça) e volta depois do rebuild.
- **RN-CUSTOMIZE-10 (-v002, parte dos grupos):** os grupos CAIXA, FUNDO, INTERNO e FRENTES de `btm_custom` são lidos
  só pela migração M-03 e pelo caminho antigo de reaplicação dos arquivos que ainda não tiveram acabamento novo; a
  parte do veio pela variante `<nome> ROTATED` continua valendo até a onda 3.

Regras sob vigilância desta onda: ver `regression-watch.md` da 067 (itens da onda 2).

## Atualização 2026-10-25 (onda 3, addon 1.11.0)

Onda 3 da 067 (veio por objeto, sem a variante `ROTATED`): ações T008, T027, T065 a T067, T101 a T103, T133 e
T165, na branch `feat/067-onda3-veio`.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/domain.md` | RN-CUSTOMIZE-10 (veio pela variante `<nome> ROTATED`) | regra-alterada | O veio é girado por objeto pelo serviço de veio; a variante não é mais criada (ver -v003 abaixo) |
| `_reversa_sdd/object_library/` | `retexture.image_material` | regra-alterada | Um material por textura, com o grafo Attribute (Object `btm_grain_rot`) → Vector Rotate → Mapping; calibração `btm_image_grain_axis` |
| `_reversa_sdd/texture_library/` | `apply` (RN-06 do veio) | regra-alterada | Sai a variante girada pela proporção da imagem; o giro sai de `btm_part.grain` e da calibração |
| `_reversa_sdd/cutting/` | veio no corte | regra-alterada | O veio visual e o de corte são o mesmo dado (`btm_part.grain`); mudar um muda o outro |
| n/a | `Object["btm_grain_rot"]`, `Material["btm_image_grain_axis"]` | delta-de-dados | Giro Euler por objeto e calibração da imagem; M-05 converte objetos com `<nome> ROTATED` |

### Versões novas das regras superadas na onda 3 (067 D-32, RF-143)

- **RN-CUSTOMIZE-10 (-v003, parte do veio; a parte dos grupos ficou na -v002 da onda 2):** o veio de uma peça é
  `btm_part.grain` (NONE, H ou V na face semântica da peça instalada). A textura gira por objeto: o material de imagem
  é um só, e o nó Attribute (tipo Object) lê `btm_grain_rot` (Euler XYZ) antes da escala métrica do Mapping, que
  todas as imagens do material compartilham. O giro é calculado pela calibração da imagem (`btm_image_grain_axis`, H
  ou V; o palpite inicial vem da proporção) e pelos eixos da projeção (BOX: face X → (Z, Y), face Y → (X, Z), face Z
  → (Y, X); UV: (X, Y)), medidos por render no protótipo T008. A variante `<nome> ROTATED` não é mais criada; a que
  já existe é lida, e a M-05 dá à peça o veio V e o giro equivalente, trocando pelo material de origem na primeira
  edição de veio. Os `ROTATED` internos das bibliotecas HB (montantes e travessas) não mudam.
