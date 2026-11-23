# Legacy Impact: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-21`
> Política de edição do legado na execução: `allowLegacyEdits: true`, `allowedPaths` com os doze globs da feature,
> entre eles `caffmob_draw/armario_v2/**`, `caffmob_draw/assets/slides/**`,
> `caffmob_draw/data/translations/armario_v2.json`, `caffmob_draw/cutting/*.py`, `caffmob_draw/__init__.py`,
> `caffmob_draw/cabinet_editor/__init__.py` e `tests/test_017_*.py`.

## 1. Arquivos afetados até aqui

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/assets/slides/slide-st48-0200-0.obj` | Ativos (corrediça 3D) | componente-novo | LOW | Modelo telescópico do anexo, 254.513 bytes, empacotado sem mudança no `build.py` (T001) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | componente-novo | LOW | Catálogo de área nova com 59 entradas em `pt_BR` e `en_US` (T002 e os 20 textos de enum de T003) |
| `caffmob_draw/armario_v2/props.py` | Dados do construtor v2 | componente-novo | LOW | Seis PropertyGroups (armário, divisão, gaveta, interno, parte e contrato de chapas) com `register()`/`unregister()` próprios (T003) |
| `caffmob_draw/armario_v2/__init__.py` | Registro do construtor v2 | componente-novo | LOW | Cascata `_MODULES = ('props',)`, import tardio e `unregister()` simétrico ao `register()` (T004) |
| `_reversa_forward/017-construtor-armario-v2/investigation.md` | Documentação da feature | regra-alterada | LOW | Seção 7 registra tamanho, hash, contagem de objetos e o empacotamento (T001) |
| `tests/test_017_spec.py` | Harness do núcleo v2 | componente-novo | LOW | 7 casos: faixas das medidas, encontro das chapas nas duas montagens, orientações, espessuras e fundo (T005) |
| `tests/test_017_vaos.py` | Harness do núcleo v2 | componente-novo | LOW | 8 casos: árvore de vãos `s0`/`s0.b`, quatro variantes de cada eixo, matriz e duplicar com o mínimo de 80 mm (T006) |
| `tests/test_017_chapas.py` | Harness do núcleo v2 | componente-novo | LOW | 5 casos: contrato vazio, padrão e injeção do hospedeiro, conferência maior/maior e menor/menor, bloqueio ligado e desligado (T007) |
| `tests/test_017_gavetas.py` | Harness do núcleo v2 | componente-novo | LOW | 4 casos: folga de 3 mm em 760 mm, dez modelos, separador de 6 mm e quatro afastadores independentes (T008) |
| `tests/test_017_portas.py` | Harness do núcleo v2 | componente-novo | LOW | 4 casos: duas folhas com dobradiça alternada, fórmula da deslizante, exclusividade e recuo por papel (T009) |
| `tests/test_017_internos.py` | Harness do núcleo v2 | componente-novo | LOW | 4 casos: posições do mockup, faixa editável, interno preso ao vão e desempate isolado de 50 mm (T010) |
| `tests/test_017_resumo.py` | Harness do núcleo v2 | componente-novo | LOW | 2 casos: linha de estado em texto e lista de peças com marca de fora-da-chapa, sem ferragem (T011) |
| `caffmob_draw/armario_v2/spec.py` | Núcleo do construtor v2 | componente-novo | LOW | Spec imutável em mm: 17 medidas, `validate`, encontro das chapas, orientações, fundo e profundidade útil (T012) |
| `caffmob_draw/armario_v2/vaos.py` | Núcleo do construtor v2 | componente-novo | LOW | Árvore de vãos `s0`/`s0.b`, quatro variantes por eixo, matriz e duplicar com mínimo de 80 mm (T013) |
| `caffmob_draw/armario_v2/chapas.py` | Núcleo do construtor v2 | componente-novo | LOW | Contrato de oito papéis, `contrato_vazio`, `padrao` 2750 × 1830 e injeção do hospedeiro (T014) |
| `caffmob_draw/armario_v2/conferencia.py` | Núcleo do construtor v2 | componente-novo | LOW | Comparação maior/maior e menor/menor, violações com medida e decisão de bloquear ou avisar (T015) |
| `caffmob_draw/armario_v2/gavetas.py` | Núcleo do construtor v2 | componente-novo | LOW | Bloco com folga de 3 mm, dez modelos, separadores de 6 mm e quatro afastadores (T016) |
| `caffmob_draw/armario_v2/portas.py` | Núcleo do construtor v2 | componente-novo | LOW | Portas de abrir a 95°, deslizantes pela fórmula, exclusividade e recuo por papel (T017) |
| `caffmob_draw/armario_v2/internos.py` | Núcleo do construtor v2 | componente-novo | LOW | Posições do mockup, faixa editável e desempate de 50 mm idempotente (T018) |
| `caffmob_draw/armario_v2/resumo.py` | Núcleo do construtor v2 | componente-novo | LOW | Linha de estado em texto e lista de peças com marca de fora-da-chapa (T019) |
| `caffmob_draw/armario_v2/build.py` | Geração do armário v2 | componente-novo | LOW | `pecas` em mm e `gerar` em metros: malha por chapa com `btm_armario_parte`, raiz vazia na coleção própria, fundo por fixação e quatro acabamentos com vidro e alumínio (T020) |
| `tests/test_017_vaos.py` | Harness do núcleo v2 | regra-alterada | LOW | Dois casos novos (36 no total): caminhos únicos com divisória e prateleira no mesmo vão e vertical dentro de coluna com prateleiras (correção de T013) |
| `tests/test_017_build.py` | Harness do núcleo v2 | componente-novo | LOW | 6 casos puros da lista de chapas: caixa nas duas montagens, fundo nas duas fixações, divisórias, frentes de gaveta e chapas da caixa da gaveta em 6 mm (T020) |
| `caffmob_draw/armario_v2/anim.py` | Animação do armário v2 | componente-novo | LOW | Timer de 16 ms com 18 quadros por alvo, curso lido de `btm_armario_parte`, estado em `btm_armario.aberto`, `_handles` removido no fim/alvo apagado/novo toque/`unregister`/`load_post` e o operador `caffmob.armario_v2_alternar` com um único `undo_push` no último quadro (T022) |
| `caffmob_draw/armario_v2/__init__.py` | Registro do construtor v2 | regra-alterada | LOW | `_MODULES` passa de `('props',)` para `('props', 'anim')`, como T004 previu; `ops` continua de fora por causa do `bl_idname` dividido (T022) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 59 para 75 entradas: os 16 textos de `ops.py` (pendência de T021) e de `anim.py`, nas duas línguas (T022) |
| `caffmob_draw/armario_v2/panel.py` | Painel do construtor v2 | componente-novo | MEDIUM | `BTM_PT_ArmarioV2` na sidebar `CAFFMob Draw` com as sete abas, sub-abas, cabeçalho, janela vazia, aviso do móvel antigo sem comandos, contrato semeado do Padrão de Dimensões e os botões de T021/`anim` (T023) |
| `caffmob_draw/armario_v2/ops.py` | Operadores do construtor v2 | regra-alterada | MEDIUM | `Montar Caixa` novo (RF-01, sem ação no plano) e `Abrir` cria o armário vazio quando a cena não tem armário v2, recusando num móvel da construção antiga (T023) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 75 para 85 entradas: os dez textos do painel e a dica de Montar Caixa (T023) |
| `caffmob_draw/armario_v2/menu.py` | Menu de contexto do armário v2 | componente-novo | MEDIUM | Abrir/Fechar, Duplicar e Excluir em `VIEW3D_MT_object_context_menu` por `_append`/`_remove`, filtrados pelo armário da hierarquia (T024) |
| `caffmob_draw/armario_v2/ops.py` | Operadores do construtor v2 | regra-alterada | MEDIUM | `semear_contrato` mudou para cá (fora do draw), novo operador de semear e guarda `_dividido` que segura só o `Abrir` enquanto o editor 2D antigo ocupar o `bl_idname` (T023 corrigido, T024) |
| `caffmob_draw/armario_v2/__init__.py` | Registro do construtor v2 | regra-alterada | LOW | `_MODULES` passa a `('props', 'anim', 'ops', 'panel', 'menu')`; `ops` entra antes de `panel` para os botões existirem (T023 corrigido, T024) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 85 para 91 entradas: os seis textos do menu e da semente do contrato (T024) |
| `caffmob_draw/armario_v2/hud.py` | Estado do armário na vista 3D | componente-novo | MEDIUM | Handler `POST_PIXEL` com os alternadores da caixa (só com o armário vazio), o inspetor da peça escolhida e o realce da seleção; clique por operador em keymap `3D View` com `PASS_THROUGH` fora dos botões (T025) |
| `caffmob_draw/armario_v2/__init__.py` | Registro do construtor v2 | regra-alterada | LOW | `_MODULES` passa a `('props', 'anim', 'ops', 'panel', 'menu', 'hud')` (T025) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 91 para 100 entradas: os papéis por extenso do inspetor e o texto do operador do clique (T025) |
| `caffmob_draw/armario_v2/ponte.py` | Módulos de biblioteca no motor novo | componente-novo | HIGH | Lê medida, montagem, espessuras, presença, portas e divisões do módulo e gera o armário v2; oculta e marca o módulo antigo com `btm_cut_exclude` só quando a geração passa, com reversão pelo Recriar do módulo (T026) |
| `caffmob_draw/armario_v2/panel.py` | Painel do construtor v2 | regra-alterada | MEDIUM | Módulo de biblioteca deixa de ser "móvel antigo" e ganha a aba do módulo com o Gerar pelo motor novo; o armário vindo de módulo ganha o Recriar do módulo (T026) |
| `caffmob_draw/armario_v2/__init__.py` | Registro do construtor v2 | regra-alterada | LOW | `_MODULES` passa a `('props', 'anim', 'ops', 'panel', 'menu', 'hud', 'ponte')` (T026) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 100 para 112 entradas: avisos, aba do módulo e textos dos dois operadores (T026) |
| `caffmob_draw/armario_v2/panel.py` | Painel do construtor v2 | regra-alterada | MEDIUM | `raiz_da_selecao` separada de `raiz_da_cena`: a seleção de módulo de biblioteca vence o recuo para o primeiro armário da coleção, e o `poll` aceita módulo de biblioteca (correção de T026 em 2026-11-22) |
| `caffmob_draw/cabinet_editor/__init__.py` | Registro do editor 2D | regra-alterada | HIGH | `_modules()` passa a `(data_props, previews, gallery, reflow_handler)`: `window`, `ops_editor`, `ops_actions`, `panels*` e `props` saem do registro, e com `props` sai o `WindowManager.btm_cabinet_editor` (T027) |
| `caffmob_draw/collision/guard.py` | Colisão | regra-alterada | MEDIUM | `_MANAGED` fica só com `caffmob.move_over_dialog`: o modal do editor 2D, já sem registro desde T027, sai da lista de modais gerenciados (T028) |
| `caffmob_draw/stick/settle.py` | Grudar | regra-alterada | MEDIUM | `_MOVE_IDS` perde `caffmob.cabinet_editor_modal` e mantém os seis modais de movimento; o assentar não espera mais por um operador que não existe (T028) |

**Nenhum arquivo preexistente do addon foi editado.** As ações executadas criam arquivos novos (um binário de
ativo, o catálogo de tradução, os PropertyGroups e a cascata do pacote v2, mais os sete arquivos de teste puro) e,
no catálogo de T002, acrescentam entradas. Nada do legado mudou: `caffmob_draw/armario_v2/` é o pacote novo e ainda
não está registrado na extensão (isso é T030).

## 1.1 Arquivos afetados na execução de T036 a T040 (2026-11-23)

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/armario_v2/corredica.py` | Núcleo do construtor v2 | componente-novo | LOW | Medidas do conjunto ST48 em mm, duas corrediças por gaveta, recuo do trilho, casamento dos quatro objetos do OBJ com as três marcas e peças de ferragem com `papel` vazio (T036) |
| `caffmob_draw/armario_v2/props.py` | Dados do construtor v2 | regra-alterada | LOW | `ferragem` (`NENHUMA`, `TRILHO_EXT`, `TRILHO_INT`, `GAIOLA`) em `BTM_PG_ArmarioParte` (T037) |
| `caffmob_draw/armario_v2/build.py` | Geração do armário v2 | regra-alterada | MEDIUM | OBJ importado uma vez por sessão (malhas com usuário falso, objetos do import removidos), conjunto por gaveta, queda para o conjunto de reserva sem o arquivo e `ferragem` gravada na peça (T037) |
| `caffmob_draw/armario_v2/anim.py` | Animação do armário v2 | regra-alterada | LOW | A gaiola passa a ser reconhecida por `ferragem == 'GAIOLA'`, no lugar de `PAPEIS_GAIOLA` (T037) |
| `caffmob_draw/data/translations/armario_v2.json` | Tradução | regra-alterada | LOW | Catálogo de 136 para 139 entradas: `Trilho externo`, `Trilho interno` e `Gaiola`; `Nenhuma` reaproveitada de `operators.json` (T037) |
| `tests/test_017_corredica.py` | Harness do núcleo v2 | componente-novo | LOW | 8 casos puros da corrediça, incluindo a ausência no plano de chapa (T038) |
| `tests/blender_017_armario_smoke.py` | Harness do construtor v2 | regra-alterada | LOW | `run_corredica`: OBJ e conjunto de reserva, marcas de ferragem, gaiola a 50% do curso e corte sem corrediça (T039) |
| `tests/blender_017_reabrir_smoke.py` | Harness do construtor v2 | componente-novo | LOW | Reabertura por arquivo em `tempdir`: `btm_armario`, `snapshot` e peças iguais depois de `open_mainfile` (T040) |

## 1.2 Arquivos afetados na execução de T041 a T051 (2026-11-23)

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/armario_v2/spec.py` | `armario_v2` (núcleo) | regra-alterada | MEDIUM | RN-04 passa a valer como travessa de 90 mm, com a orientação trocando o eixo dos 90 mm (D-22) |
| `caffmob_draw/armario_v2/build.py` | `armario_v2` (cena) | regra-alterada | MEDIUM | duas peças novas, `CONTRA_FRENTE` e `PECA_TRAS`, com componente `TRA`, no topo interno |
| `caffmob_draw/armario_v2/props.py` | `armario_v2` (dados) | delta-de-dados | LOW | duas presenças e nove campos de interface, todos com padrão, sem migração |
| `caffmob_draw/armario_v2/ops.py` | `armario_v2` (cena) | regra-nova | LOW | cinco operadores de inserção e três gravadores de coleção |
| `caffmob_draw/armario_v2/panel.py` | `armario_v2` (cena) | regra-alterada | LOW | botões de inserção nas três abas e a caixa Travessas na Estrutura |
| `caffmob_draw/data/translations/armario_v2.json` | i18n | contrato-alterado | LOW | 27 entradas novas (139 → 166), nas duas línguas |

Nada fora de `caffmob_draw/armario_v2/` e do catálogo foi tocado: o corte continua lendo `btm_armario_parte` por
`part_sources.armario_v2_records`, e as duas peças novas caem nele como qualquer chapa do armário, com `componente`
`TRA`. O `part_extractor.limit_status` não mudou. A inserção também não abriu caminho novo no legado: os operadores
chamam `vaos`, `gavetas` e `internos` do próprio pacote e regravam as mesmas coleções que o Duplicar do menu já regravava.

## 2. Impacto previsto no legado (ainda não executado)

| Arquivo afetado | Componente | Tipo | Severidade | Ação | Justificativa |
|-----------------|------------|------|------------|------|---------------|
| `caffmob_draw/cabinet_editor/__init__.py` | Registro do editor 2D | regra-alterada | HIGH | T027 (**executado em 2026-11-22**) | `_modules()` deixa de registrar `window`, `ops_editor`, `ops_actions` e `panels*`; `gallery` permanece (A002). Os núcleos puros seguem importáveis |
| `caffmob_draw/collision/guard.py` | Colisão | regra-alterada | MEDIUM | T028 (**executado em 2026-11-22**) | `caffmob.cabinet_editor_modal` sai de `_MANAGED` |
| `caffmob_draw/stick/settle.py` | Grudar | regra-alterada | MEDIUM | T028 (**executado em 2026-11-22**) | Mesma remoção da lista de modais gerenciados |
| `caffmob_draw/cutting/part_sources.py` | Corte | regra-alterada | CRITICAL | T029, T035 | Adaptador `armario_v2_records` e filtro de `btm_cut_exclude` em `iter_modules` (A001) |
| `caffmob_draw/cutting/part_extractor.py` | Corte | regra-alterada | MEDIUM | T015 | `limit_status` passa a delegar para `armario_v2.conferencia`, se o import não arrastar `bpy` |
| `caffmob_draw/__init__.py` | Registro da extensão | regra-alterada | MEDIUM | T030 | `armario_v2` na lista de submódulos, no import e nas cascatas de registro |
| `caffmob_draw/blender_manifest.toml` | Empacotamento | dado-alterado | LOW | T031 | Versão `1.25.0` → `1.26.0` |

## 3. Contratos que não podem quebrar

- `cabinet_editor.structure.carcass_lengths` continua com a mesma assinatura: o `spec.py` a reusa em vez de duplicar a conta.
- Os seis adaptadores de `part_sources` e `PartRecord` continuam com os mesmos campos; o adaptador novo é aditivo.
- `standards.api.active_definition` continua sendo a fonte do contrato de chapas.
- O móvel gerado pelo construtor antigo continua na cena e no corte, intocado (RF-26).
- `build.py` continua recusando empacotar sem os `.blend` obrigatórios; o ativo novo não entra nessa checagem.

## 4. Observações

- A política liberou `"***"`, que casa com qualquer caminho; na prática a execução foi irrestrita. Ainda assim, o
  escopo seguido foi o das tabelas de `actions.md`.
- `caffmob_draw/armario_v2/` nasceu em T003 com `props.py` e ganhou em T004 o `__init__.py` que encadeia
  `register()`/`unregister()`; o registro na extensão só em T030, então nada do addon importa o pacote ainda.
- O `data-delta.md` foi corrigido para dizer "nove espessuras no armário, oito no contrato" — a `espessura_folha`
  não existe no contrato de chapas. O código de T003 já seguia a tabela; só a prosa estava ambígua.
- Os sete testes da Fase 2 já fixam a API que T012 a T019 precisam cumprir (`spec`, `vaos`, `chapas`, `conferencia`,
  `gavetas`, `portas`, `internos`, `resumo`). Eles rodam sem `bpy` e ficam em skip declarado enquanto o módulo não
  existir; o skip nomeia a ação que o libera, então a Fase 3 não precisa editar teste nenhum para começar a valer.
- **D-10 parcial, com motivo.** `spec.carcass_lengths` reusa `cabinet_editor.structure.carcass_lengths` na montagem
  lateral passante, mas a base passante é calculada no `spec.py`: a função da feature 012 mantém o topo entre as
  laterais, e a RN-04 da 017 manda as duas bases cobrirem a largura. A regra antiga não foi alterada; quem lê o
  watch W010 deve comparar só a montagem lateral passante até o `/reversa-sync` decidir qual leitura vale.
- A semeadura do contrato a partir de `standards.api.active_definition` não está em `chapas.py` porque precisa da cena
  do Blender: o painel (T023) lê o padrão ativo e injeta por `apply_host_contract`, que já está pronto e testado.
- `cutting/part_extractor.limit_status` continua com a conta própria por enquanto: a delegação para
  `armario_v2.conferencia` fica em T029/T034, porque `part_extractor` carrega `bpy` e o núcleo novo não pode
  importá-lo. Até lá existem duas implementações da mesma comparação, com o teste puro cobrindo a nova.
- **Correção de T013 em 2026-11-22:** os caminhos de vão passaram a ser reservados por irmandade antes da recursão
  (colunas `.b`, faixas `.a`) e `vaos.regioes` separa a região do vão (referencial das divisórias) da célula onde o
  conteúdo é colocado. Nada disso toca o legado: `cabinet_editor.bays` continua sendo o formato de referência.
- **T020 cria a coleção `CAFFMob Armário v2`** e objetos novos nela; o armário antigo e a coleção do construtor
  anterior não são tocados. `limpar()` só apaga filhas da raiz com `btm_armario_parte`.
- **T020 completado em 2026-11-22:** `build.py` passou a importar `bpy`/`bmesh`/`mathutils` dentro das funções de
  cena, então `build.pecas` é testável sem Blender e as chapas da caixa da gaveta entram no plano de corte com as
  medidas de `gavetas.chapas` (separadores de 6 mm e quatro afastadores).
- **T021 em 2026-11-22:** `ops.py` só chama `build.gerar` e `build.limpar`, que trabalham na coleção `CAFFMob
  Armário v2` e nas filhas da raiz vazia; nada do editor 2D, do construtor anterior ou do corte é lido ou alterado.
  O `bl_idname` `caffmob.cabinet_editor` é reusado de propósito (D-03) e só passa a existir quando o editor antigo sair
  do registro em T027 — até lá `_MODULES` não carrega o `ops`.
- W004 ganhou cobertura pura: `tests/test_017_vaos.py` fixa o formato de caminho de vão (`s0`, `s0.b`, `s0.b.b`)
  igual ao de `cabinet_editor.bays`, que é a premissa de `ponte.py`.
- **T022 em 2026-11-22:** `anim.py` só mexe nas filhas da raiz do armário v2 (matriz de mundo das próprias peças) e
  agenda timer próprio; não toca no editor 2D, no construtor antigo nem no corte. O `undo_push` é o mesmo operador do
  Blender que o resto do pacote já usa, chamado uma vez no fim da animação, então o passo de desfazer continua sendo
  um por comando (W001).
- **Pendência de i18n de T021 fechada em T022:** o `tests/test_i18n_coverage.py` só rodou agora e acusou 13 textos de
  `ops.py` sem tradução — nada no legado mudou, o catálogo da área é que estava incompleto. W008 voltou a ficar verde
  com os 16 textos novos nas duas línguas.
- **T023 em 2026-11-22:** o painel só lê o armário v2 e as coleções; para o móvel da construção antiga ele só desenha o
  aviso, sem tocar em `btm_cabinet`/`btm_structure`. A exceção é `Abrir` criar a raiz vazia quando a cena não tem
  armário v2 — objeto novo na coleção `CAFFMob Armário v2`, nada do construtor anterior é alterado, e a chamada é
  recusada quando a seleção é um móvel antigo (RN-23, RF-26).
- **Lacuna do plano em T023:** o mockup tem os botões "+ Inserir Divisória/Prateleira/Matriz/Gavetas", mas nenhuma ação
  previu esses operadores. O painel edita o que está gravado e a inserção fica com o Duplicar de T024 e o HUD de T025;
  se o titular quiser inserção explícita no painel, isso vira ação nova, não improviso aqui.
- **Contrato semeado pelo painel.** A escrita acontece na primeira vez que o painel desenha com o contrato vazio, e só
  em `Scene.btm_armario_contrato` (grupo da própria feature). Sem Padrão de Dimensões ativo, a API devolve os padrões do
  esquema BR (2750 × 1830, fundo 6 mm, o resto 15 mm), o mesmo fallback do corte.
- **T023 corrigido e T024 em 2026-11-22:** o painel não escreve mais no contrato durante o desenho (a escrita foi para
  `ops.semear_contrato`, chamada no `Abrir` e pelo botão), então desenhar a sidebar não altera o arquivo. O menu de
  contexto de `menu.py` só desenha itens quando a seleção está sob um objeto com `btm_armario`; móvel da construção
  antiga continua sem item e sem alteração. Duplicar/Excluir escrevem só na coleção do próprio armário v2 e refazem as
  peças dele.
- **Guarda do `bl_idname` dividido (D-03).** `ops.register` registra todas as classes menos `Abrir` enquanto o editor
  2D antigo ainda responder por `caffmob.cabinet_editor`; nenhum operador do legado é reescrito nem desregistrado. A
  guarda desaparece sozinha em T027, quando o editor antigo sair.
- **T026: módulos de biblioteca passam pelo motor novo.** Nenhum operador, propriedade ou adaptador das bibliotecas
  antigas foi alterado: a ponte só **lê** o módulo (`btm_cabinet`, `btm_structure`, `scene_divisions`) e grava o
  resultado no armário v2 novo. O módulo antigo é preservado, apenas oculto e marcado com `btm_cut_exclude` — marcas que
  `cutting/part_sources` e o resto do pipeline já respeitavam —, e o Recriar do módulo devolve exatamente os objetos
  que foram marcados, gravados na raiz do armário v2.
- **Risco de duplicação no corte, aberto de propósito.** A conversão não apaga o módulo, então o caminho sintético do
  corte (`iter_modules`) ainda pode listar as peças do módulo oculto. O achado A001 e a ação T035 tratam disto; até lá,
  a proteção existente é `btm_cut_exclude` e `_visible`, que o T035 vai fechar em `iter_modules`.
- **T027 em 2026-11-22:** a interface do editor 2D sai do registro, mas nenhum arquivo dela foi apagado — `window`,
  `ops_editor`, `ops_actions`, `panels*` e `props` continuam no pacote, só não são mais registrados pela cascata. O
  `WindowManager.btm_cabinet_editor` deixa de existir, e nada fora de `cabinet_editor` o lia (só os `panels*`
  removidos e `props`, que agora ficam inertes). `data_props`, `previews`, `gallery` e `reflow_handler` continuam
  registrados: o primeiro sustenta `btm_structure`/`btm_division`/`btm_extra`, lidos por `structure_inputs`,
  `cutting/part_extractor`, `customize/reapply` e `library_panel`; o último fica inerte porque só o modal removido
  iniciava `props.session()`.
- **T028 em 2026-11-22:** as duas listas de modais gerenciados eram as últimas referências a
  `caffmob.cabinet_editor_modal` fora de `cabinet_editor/`, e só classificam operador em andamento. Nada de propriedade,
  handler ou adaptador foi tocado; `grep` em `collision/` e `stick/` não acha mais o nome. Como o modal já não é
  registrado desde T027, a remoção só evita que o guarda trate como "assistido" um `bl_idname` que nunca mais casa.
- **Correção de painel em 2026-11-22 (T026):** a aba do módulo de biblioteca voltou a aparecer com outro armário v2 na
  cena. A causa era o recuo de `raiz_da_cena` para a coleção acontecer antes da checagem de módulo; agora a seleção
  manda. Nada do legado foi tocado — a correção é só leitura de seleção e desenho.
- **Estado de abertura no armário, não na peça.** O §2 do `data-delta` tem um `aberto` booleano em `BTM_PG_ArmarioV2`,
  então o flag registra o último alvo animado; o rótulo do menu (`anim.estado`/`anim.rotulo`) lê a geometria, que é o
  que continua correto com várias gavetas e depois de reabrir o arquivo. Um estado por peça exigiria campo novo no
  delta — fica registrado como lacuna, sem inventar dado.
- **T031 e T032 em 2026-11-23.** Só `caffmob_draw/blender_manifest.toml` (versão `1.25.0` → `1.26.0`) e o caminho de
  mensagens do núcleo puro mudaram: `spec.validate`, `chapas.pode_gerar`, `vaos.duplicar`,
  `conferencia.Violacao.texto()` e `resumo.linha_estado` passaram a montar o texto com `tr(...)` só nos literais, sem
  tocar em nenhuma conta, medida ou regra. O `data/i18n.py` do legado continua sendo a única fonte de tradução e não
  foi alterado; os cinco módulos seguem sem importar `bpy` (o pacote `data` é stubado nos testes, e `data/i18n.py` só
  importa `json`/`os` no topo). O catálogo `armario_v2.json` foi de 112 para 136 entradas, sem tocar em catálogo de
  outro módulo: `vão {}` reaproveita a entrada de `customize.json` justamente para não duplicar msgid.
- **T036 a T040 em 2026-11-23.** A corrediça só escreve no armário v2: `build` cria objetos na coleção
  `CAFFMob Armário v2`, todos filhos da raiz vazia, e o import do OBJ não deixa objeto nenhum na cena (as malhas ficam
  com usuário falso e são compartilhadas). Nada do editor 2D, do construtor anterior ou do corte foi alterado. O único
  ponto novo de leitura no legado é o import de `bpy.ops.wm.obj_import`, o mesmo operador que `promob/complemento.py`
  já usava, agora com `global_scale=MM` porque o OBJ está em milímetros. A reabertura não mudou código de produção:
  a fumaça nova só exercita o que `Object.btm_armario` já gravava (D-02).
