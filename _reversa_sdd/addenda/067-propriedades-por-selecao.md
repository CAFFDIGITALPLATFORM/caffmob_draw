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

## Atualização 2026-10-25 (onda 4, addon 1.12.0)

Onda 4 da 067 (fita de borda visual): ações T010, T028, T029, T068 a T072, T104 a T106, T134, na branch
`feat/067-onda4-fita`. A onda não muda regra 🟢 da extração (D-32); só acrescenta.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| n/a | `edgeband/` | componente-novo | Fita de borda visual: bordas expostas por geometria no referencial do componente, faixa única para bordas coplanares (0,1 mm), sincronia por `params_hash` num timer |
| `_reversa_sdd/cutting/` | `part_sources` | regra-nova | Objeto com `btm_cut_exclude` não entra no plano de corte; as linhas `Edge L1/L2/W1/W2` e o `edges_present` não mudam (D-22) |
| `_reversa_sdd/collision/` | `scan._skip` | regra-nova | A fita visual fica fora da colisão |
| `_reversa_sdd/texture_library/` | `apply._meshes` | regra-nova | A fita visual não é alvo de textura do módulo |
| n/a | `Object.btm_edgeband`, `Object.btm_cut_exclude` | delta-de-dados | Metadados da faixa (dono, chaves das bordas, espessura, largura aparente, material ou cor lisa) |

## Atualização 2026-10-25 (onda 5, addon 1.13.0)

Onda 5 da 067 (gavetas e frentes por subvão no módulo rápido, mecanismos e editor animado, contato real da folha,
editor de armário e frente pelo papel): ações T011, T128, T030 a T032, T073 a T079, T107 a T109, T135, T136, T145,
T154 a T157, T166 e T173, na branch `feat/067-onda5-animados`.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/customize/requirements.md` | RN-07 (frentes do `btm` sem gavetas) | regra-alterada | O módulo rápido aceita DRAWERS (caixas reais) e frentes por subvão (ver -v002) |
| `_reversa_sdd/domain.md` | RN-AGGREGATES-07 (contato da folha pela caixa) | regra-alterada | A folha é testada pelas malhas reais das peças; o vidro fixo do próprio autoral sai por papel (ver -v002) |
| `_reversa_sdd/selection/requirements.md` | RN-03 (frente pelo sufixo do nome) | regra-alterada | Frente só por tag ou papel; M-08 grava o papel nas portas antigas (ver -v002) |
| `_reversa_sdd/cutting/` | aviso de corte desatualizado | regra-alterada | A porta do módulo rápido pela dobradiça e o Empty pela marca, não pelo nome |
| `_reversa_sdd/inspection/` | adaptador do módulo rápido | regra-alterada | Empty pela marca, porta direita pela dobradiça; corrige a posição do Empty (a porta não girava) |
| `_reversa_sdd/cabinet_editor/` | `library_opening`, catálogo e vista | regra-alterada | No módulo rápido a frente vai no subvão pelo caminho dele; catálogo só com executor validado; arraste de divisória com um passo e Esc |
| n/a | `mechanisms/`, `geometry/subspace_fronts.py`, `geometry/door_names.py` | componente-novo | Registro de mecanismos (giro, basculante, correr, gaveta) pelos dados; frentes por vão; sufixos só no construtor |
| n/a | `hb_part_role`, `btm_front_hinge`, `btm_door_controller`, `btm_space_fronts` | delta-de-dados | Papel, dobradiça e marca gravados pelo construtor e pela M-08; pedido de frente por vão na raiz |

### Versões novas das regras superadas na onda 5 (067 D-32, RF-143)

- **customize RN-07 (-v002):** o `btm` aceita `DOOR_LEFT`, `DOOR_RIGHT`, `DOUBLE_DOORS`, `FLIP_UP`, `DRAWERS` e
  `OPEN`. DRAWERS gera caixas reais (frente e caixa), com `Spec.front == DRAWERS` e a contagem; pedido não suportado é
  recusado e o operador termina `CANCELLED`. No editor, a frente vai no subvão escolhido, pelo caminho dele, e
  convive com a frente de outro subvão.
- **RN-AGGREGATES-07 (-v002):** o contato da folha é testado pelas malhas reais das peças dela (também quando a
  folha é um grupo), cada uma encolhida 1 mm; saem do teste a folha, o pivô, os descendentes, as folhas irmãs, o pai
  (esquadria) ou a raiz do módulo do pai e, no armário autoral, a raiz e o vidro fixo (membro Frente fixa); a lateral
  e as outras peças do autoral continuam contando.
- **selection RN-03 (-v002):** frente = marca de `FRONT_TAGS` ou `hb_part_role` ∈ {`DOOR`, `DRAWER_FRONT`,
  `PULLOUT_FRONT`, `TILT_OUT`, `FRONT_PIVOT`, `CLOSET_DOOR_FRONT`, `CLOSET_DRAWER_FRONT`}. O nome não conta. As portas
  do módulo rápido ganham o papel e a dobradiça do construtor, e a M-08 grava os mesmos campos nos arquivos antigos.

## Atualização 2026-10-25 (onda 6, addon 1.14.0)

Onda 6 da 067 (rotação no Mover sobre em torno de um eixo, pivô e âncora, gesto de face): ações T033, T034, T080 a
T086, T110 a T112, T137, T176 e T125, na branch `feat/067-onda6-mover-sobre`.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/move_over/requirements.md` | RN-03 (rotação em Z pelo centro da base) | regra-alterada | A rotação é uma orientação em quaternion, em qualquer eixo das vistas, em torno do pivô escolhido (ver -v002) |
| `_reversa_sdd/move_over/requirements.md` | RN-13 (posição salva `{delta, rotation, b_side}`) | regra-alterada | A posição salva leva também `orientation`, `pivot` e `anchor`; a M-07 completa as antigas (ver -v002) |
| `_reversa_sdd/domain.md` | RN-MOVE_OVER-03 e RN-MOVE_OVER-12 | regra-alterada | Mesmas regras no resumo do domínio; leia pelas versões -v002 abaixo |
| n/a | `move_over/rotation.py`, `move_over/dialog_rotate.py` | componente-novo | Núcleo puro da rotação (eixo-ângulo, giro em torno de ponto, ângulo assinado com unwrap, passo de 15°) e a camada do diálogo (alças, campos de ângulo, histórico local, pan e zoom por painel) |
| n/a | `move_over/ops_drag.py` | regra-nova | Gesto de face: o clique fixa o pino na face sob o cursor; soltar faz da face o pai com a matriz mundial preservada; cancelar devolve o pai |
| n/a | `Scene.btm_saved_positions[].orientation`, `.pivot`, `.anchor` | delta-de-dados | Campos novos da posição salva, preenchidos pela M-07 nos arquivos antigos (pivô e âncora `BASE_CENTER`) |

### Versões novas das regras superadas na onda 6 (067 D-32, RF-143)

- **move_over RN-03 (-v002):** ao abrir a janela, A continua assumindo a rotação de B (escala mantida, origem no mesmo
  ponto do mundo). A rotação pedida pelo usuário é uma orientação de A no referencial de B, composta como
  `M = T(P)·R(N,θ)·T(−P)·M0`: `N` é o eixo da vista em que se gira (planta = Z, frontal = Y, a profundidade de B),
  `P` é o pivô escolhido entre o centro, o centro da base e os 8 cantos da caixa de A (padrão: centro da base) e
  fica imóvel. Escolher o pivô (Ctrl+clique) ou a âncora (Alt+clique) não move nada. O campo Rotação lê e grava o
  ângulo em torno de Z pelo centro da base, como antes; os campos de ângulo de cada vista aceitam digitação, o arraste
  da alça anda de 15° em 15° (Shift: fino), R zera o giro e Esc restaura. Confirmar é um passo de Undo.
- **move_over RN-13 (-v002):** posição salva = `{delta, rotation, b_side, orientation, pivot, anchor}`. `delta`,
  `rotation` e `b_side` seguem a regra anterior; `orientation` é o quaternion de A no referencial de B. Aplicar:
  com `orientation`, fixa pivô, âncora e orientação; sem ela (posição antiga), gira `rotation` em Z pelo centro da
  base; depois desloca A para repetir o `delta`. A M-07, no carregamento, grava nas posições antigas a orientação
  equivalente a `rotation` e pivô e âncora `BASE_CENTER`. Continuam em `Scene.btm_saved_positions`, com as 4 últimas
  na janela.

## Atualização 2026-10-25 (onda 7, addon 1.15.0 depois da publicação do MOBI)

Onda 7 da 067 (sincronia do Padrão de Dimensões com o MOBI da marcenaria): ações T139 a T141, T149, T150 e T160 a T163,
na branch `feat/067-onda7-sincronia`. O servidor fica no `caff_systems` (`feat/067-onda7-padroes-mobi`). A versão
1.15.0 só sai depois que a produção anunciar a capacidade `padroes_de_dimensao` (T167, T168). A onda não muda regra
🟢 da extração além da que a onda 1 já superou no `standards/` (D-32).

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/standards/` | banco local `padroes.sqlite3` (onda 1) | delta-de-dados | Esquema 2: `operacao_pendente` (a `Idempotency-Key` da escrita pendente) e a tabela `conflito`; o banco do esquema 1 migra ao abrir |
| n/a | `standards/sync_core.py`, `standards/sync_cloud.py` | componente-novo | Decisão por uid com o documento sem o envelope (`version`, `updated_at`, `source`) e a ordem das chamadas a `/api/draw/v2/padroes-de-dimensao` |
| `_reversa_sdd/standards/` | operadores e painel do padrão | regra-nova | "Conflitos de padrão" no painel, com "Manter a minha"/"Manter a da nuvem" e "Manter apagado"/"Manter a edição"; nada muda antes da escolha |
| n/a | descoberta na conexão (`mobi/api_v2.na_conexao`) | regra-nova | Conectar dispara a sincronia do padrão; sem a capacidade, ela não faz nada |

Regras da sincronia (RF-034, RF-035): conteúdo igual dos dois lados adota a versão da nuvem, sem conflito, também na
primeira vez; só um lado mudou segue sozinho (baixar, ou enviar com `If-Match`); os dois mudaram é conflito de edição;
um apagou e o outro editou é conflito apagar × editar; apagado de um lado e intacto do outro propaga a exclusão. O
disparo é no login, na abertura com conta ligada e 5 s depois da última gravação no banco, sempre num timer. Sem
rede, sem conta ou sem a capacidade, as linhas continuam `sujo`.

## Atualização 2026-10-26 (onda 8, addon 1.17.0)

Onda 8 da 067 (unidade única, várias paredes no editor e parede e abertura do CAFF MOBI no painel): ações T177 a
T213, na branch `feat/067-onda8-paredes-e-unidades`, a partir da 1.16.0 (`933c3c96`).

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/selection/requirements.md` | RN-01 (precedência do classificador) | regra-alterada | A parede e a abertura do CAFF MOBI são reconhecidas antes do `OTHER` (ver -v002) |
| `_reversa_sdd/selection/requirements.md` | RN-07 (raiz do componente) | regra-alterada | A raiz da abertura do CAFF MOBI conta como vão: a peça clicada sobe até ela (ver -v002) |
| `_reversa_sdd/hb_core/requirements.md` | RN-34 (unidade da cena = `btm_unit`) | regra-alterada (só o momento) | A regra continua; a unidade de cena do Blender passa a ser alinhada a ela ao abrir, no arquivo novo, na importação do MOBI e no menu de unidades (`units.alinhar_cena`) |
| `_reversa_sdd/walls2d/requirements.md` | RF-03 (selecionar face) | regra-alterada | A, retângulo e Shift+clique selecionam vários trechos; espessura, pés-direitos e tipo em lote num passo de desfazer. RN-16 continua: Del apaga um trecho |
| `_reversa_sdd/selection/` | `editing.get_dimension` | regra-alterada | A abertura do MOBI mede pelo documento (largura, altura) e pelas peças (profundidade), não pela caixa do Empty |
| n/a | `walls2d/selecao_classica.py`, `mobi/editar_v2_core.py`, `target/mobi_fields.py` | componente-novo | Seleção de vários trechos; edição do documento do MOBI pelo painel; campos `WindowManager.btm_mobi` |
| n/a | `caffmob.mobi_editar_entidade`, `caffmob.mobi_selecionar_abertura` | componente-novo | Grava a medida no documento e remonta a cena; seleciona a abertura da lista da parede |
| n/a | "Editar segmento" (`caffmob.mobi_editar_segmento`) | regra-alterada | Some com documento v2; no v1, campos de texto na unidade do projeto |

### Versões novas das regras superadas na onda 8 (067 D-32, RF-143)

- **selection RN-01 (-v002):** sem módulo, o laço dos ancestrais (inclusive) testa por nó, primeiro,
  `caffmob_tipo == 'abertura'` → `ROOM_DOOR` (entidade com `tipo` DOOR) ou `WINDOW`, biblioteca `MOBI`, com a raiz no
  próprio nó; `caffmob_tipo == 'parede'` → `WALL`/`MOBI`. Depois segue a ordem de antes (`IS_ENTRY_DOOR_BP`,
  `IS_WINDOW_BP`, `btm_kind`…). `LIBRARY_LABELS['MOBI']` = "CAFF MOBI". Consequência: parede e abertura do MOBI saem
  do Mover Sobre (`movable_root` None, motivo de parede e abertura) e não ganham escala no painel.
- **selection RN-07 (-v002):** regra (1) da raiz do componente: algum ancestral (inclusive) é vão, agora também a raiz
  da abertura do MOBI (`caffmob_tipo == 'abertura'`); o resto não muda.
