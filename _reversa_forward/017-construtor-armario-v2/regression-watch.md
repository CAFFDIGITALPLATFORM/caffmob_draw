# Regression Watch: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-21`
> Fonte: `_reversa_sdd/domain.md` e `_reversa_sdd/cutting/requirements.md` (regras 🟢) e o `legacy-impact.md` desta feature

## 1. Watch principal

Esta feature **remove do registro** a interface do editor 2D (T027) e **mexe no caminho de origem das peças**
(T029/T035), então as regras 🟢 adjacentes a esses dois pontos entram no watch desde já, mesmo antes de o código
ser tocado. Elas precisam continuar verdadeiras nas próximas extrações.

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `domain.md`, `cabinet_editor` (RN-CABINET_EDITOR-01) | Confirmação grava um passo de desfazer; Cancelar devolve o armário ao estado da abertura | presença | Cancelar deixar peças alteradas, ou uma edição gerar dois passos de desfazer |
| W002 | `domain.md`, `cabinet_editor` (RN-CABINET_EDITOR-02) | Erro bloqueante impede OK e Aplicar | presença | Erro de faixa ou de chapa permitir confirmar e gravar geometria parcial |
| W003 | `domain.md`, `cabinet_editor` (RN-CABINET_EDITOR-11) | Divisões, extras, internos e deslizantes continuam filhos diretos da raiz do módulo | presença | Peça nova nascer aninhada noutra peça, quebrando o normalizador da seleção |
| W004 | `domain.md`, `cabinet_editor` (RN-CABINET_EDITOR-12) | Vãos em cadeia (`s0`, `s0.b`…) com o mesmo formato de `cabinet_editor.bays` | redação | Caminho de vão novo não casar com o do editor antigo, quebrando `ponte.py` |
| W005 | `cutting/requirements.md`, Origem das peças | Objeto marcado como excluído (`btm_cut_exclude`) ou oculto não entra no plano de corte, por nenhum adaptador | presença | Peça do mesmo móvel aparecer duas vezes, com medidas diferentes (A001) |
| W006 | `cutting/requirements.md`, Origem das peças | O corte lê as peças dos módulos e da geometria livre, sem alterar o que já existe | regressão | Armário antigo sumir do corte, ou o adaptador novo listar malha sem papel gravado |
| W007 | `cabinet_editor/gallery.py` (RN-21/RN-22 da 015) | "Criar armário" da biblioteca continua abrindo a galeria de estruturas | presença | `bpy.ops.caffmob.structure_gallery` levantar `AttributeError` ou o fluxo cair no diálogo antigo (A002) |
| W008 | `data/i18n.py` (RN-20) | Todo texto novo tem `pt_BR` e `en_US` e cada msgid pertence a um arquivo só | automática | `tests/test_i18n_coverage.py` falhando por texto sem tradução ou msgid duplicado |
| W009 | `build.py` (RNF de compatibilidade) | O pacote continua empacotando o ativo da corrediça e recusando empacotar sem os `.blend` obrigatórios | automática | `assets/slides/slide-st48-0200-0.obj` ausente do ZIP, ou `build.py` recusando por causa dele |
| W010 | `cabinet_editor/structure.py` (RN-04) | `carcass_lengths` continua com o mesmo contrato de montagem lateral passante / base passante | regressão | `spec.py` reimplementar a conta e divergir do editor antigo |

## 2. Histórico de re-extrações

| Data | Escopo | Resultado |
|------|--------|-----------|
| 2026-11-21 | T001 e T002: ativo da corrediça e catálogo novo | Nenhuma regra 🟢 tocada; W008 e W009 verificadas e verdadeiras |
| 2026-11-21 | T003: PropertyGroups do armário v2 | Nenhuma regra 🟢 tocada; W008 conferida de novo (73 textos, 0 sem tradução, catálogo com 59 entradas) |
| 2026-11-21 | T004: cascata de registro do pacote `armario_v2` | Nenhuma regra 🟢 tocada; o pacote ainda não está registrado na extensão, então W001–W010 seguem inalteradas |
| 2026-11-21 | T005 a T011: sete suites puras da Fase 2 | Nenhuma regra 🟢 tocada; W004 passa a ter teste puro do formato de caminho de vão. As suites ficam em skip declarado até T012–T019 criarem os módulos, então nada é verificado ainda |
| 2026-11-21 | T012 a T019: oito módulos puros do núcleo | Nenhuma regra 🟢 tocada no legado. W004 verificada de verdade (`test_017_vaos` verde, caminhos `s0`/`s0.b`/`s0.b.b`); W010 vale só na lateral passante, ver observação; os 34 casos rodam sem skip |
| 2026-11-22 | Correção de caminhos em T013 e T020 (`build.py`) | Nenhuma regra 🟢 tocada. W004 segue verdadeira e agora com 10 casos: caminhos únicos com divisórias e prateleiras no mesmo vão; W009 não muda (nenhum ativo novo). 36 casos verdes |
| 2026-11-22 | T020 completo: caixa da gaveta e teste puro de `build.pecas` | Nenhuma regra 🟢 tocada. W006 ganha cobertura pura do lado do armário v2: o plano lista separador e afastador com papel gravado. 42 casos verdes |
| 2026-11-22 | T022: `anim.py` e o catálogo de tradução | Nenhuma regra 🟢 tocada. W001 conferida de novo: a animação empurra um único passo de desfazer, só no último quadro. W008 estava vermelha desde T021 (13 textos de `ops.py` sem tradução) e voltou a verde com os 16 textos novos no catálogo |
| 2026-11-22 | T023: `panel.py`, Montar Caixa e o Abrir que cria o armário vazio | Nenhuma regra 🟢 tocada. W001 e W002 seguem: o painel não grava nada, só desenha, e os comandos são os operadores de T021. W008 verde com os 10 textos novos. RF-26 ganhou a primeira superfície real: o painel reconhece o móvel antigo e não oferece comando |
| 2026-11-22 | T023 corrigido (semente fora do draw, `ops` na cascata) e T024: menu de contexto | Nenhuma regra 🟢 tocada. W001 e W002 conferidas de novo: o draw ficou só leitura e Duplicar/Excluir passam por operador com `UNDO`, com rollback quando a geração recusa. W008 verde com os 6 textos novos. Nenhum operador ou menu do legado foi desregistrado |
| 2026-11-22 | T025: `hud.py` na vista 3D | Nenhuma regra 🟢 tocada. W001 e W002 valem também para o HUD: o desenho não escreve no armário e o único caminho de escrita é o operador do clique, com `UNDO`. O item de keymap é `LEFTMOUSE`/`PRESS` com `PASS_THROUGH` fora dos botões e `poll` restrito a armário vazio, então seleção, box select e menu de contexto seguem recebendo o clique. W008 verde com os 9 textos novos. Handler e keymap removidos no `unregister()` |
| 2026-11-22 | T026: `ponte.py` e a aba do módulo no painel | RN-21 é 🟢 e passa a valer: o módulo de biblioteca é editado pelo motor novo. Nenhum operador ou adaptador da biblioteca foi desregistrado ou reescrito; o módulo só é ocultado e marcado, e só quando a geração passa. W001 e W002 seguem: a ponte só lê o módulo e grava no armário v2. W008 verde com os 12 textos novos. Fica aberto o risco de peça duplicada no corte pelo caminho sintético (A001), tratado em T035 |
| 2026-11-22 | Correção do painel (T026): seleção de módulo vence o recuo para a coleção | Nenhuma regra 🟢 tocada; a aba do módulo de biblioteca volta a aparecer com outro armário v2 na cena e o `poll` aceita arquivo só com módulos. Fumaça simulada com 4 casos, o novo incluído |
| 2026-11-22 | T028: `caffmob.cabinet_editor_modal` sai dos modais gerenciados | Nenhuma regra 🟢 tocada. Guarda de colisão e assentar só classificam operador em andamento, e o modal não é registrado desde T027, então a remoção é inerte. `grep` em `collision/` e `stick/` sem o nome; W001–W010 inalteradas |
| 2026-11-22 | T027: interface do editor 2D fora do registro de `cabinet_editor` | Nenhuma regra 🟢 removida: W001–W004 continuam valendo, agora no construtor v2 (a interface 2D apenas deixa de existir). `data_props`, `previews`, `gallery` e `reflow_handler` seguem registrados; W007 coberto porque `gallery` foi mantido. W008 e W009 não mudam. O `Abrir` do armário v2 passa a poder registrar (guarda de D-03 sem casar) |

## 3. Arquivadas

## 4. Observações

- W007 é o único watch que depende de uma decisão de escopo já tomada (A002: `gallery` permanece registrado). Se o
  T027 um dia tirar `gallery` de `_modules()`, W007 vira falha garantida em `library_panel/ops_cabinet.py:46`.
- W005 e W006 só podem ser exercitados dentro do Blender; a ação T035 prevê o teste puro de contagem antes e depois
  de `Gerar` a partir de um módulo, que cobre o caso central em `tests/test_017_corte.py`.
- W004 está coberto por teste puro desde T006: `tests/test_017_vaos.py` exige `s0`, `s0.b` e `s0.b.b` como caminhos
  de vão, o mesmo formato de `cabinet_editor.bays`. Se `vaos.py` inventar outro formato, a violação aparece já em
  `test_017_vaos.py`, antes de `ponte.py` quebrar no Blender.
- Os 34 casos de T005 a T011 só valem como verificação quando T012 a T019 criarem os módulos do núcleo: até lá a
  execução é `OK (skipped=34)`, sem asserção avaliada. O relatório de cada ação da Fase 3 deve citar a suíte que
  saiu do skip. **Fechado em 2026-11-21:** a Fase 3 criou os oito módulos e a execução passou a `Ran 34 tests … OK`,
  sem skip nenhum.
- W006 tem agora duas metades: a de cena (adaptador `armario_v2_records`, T029) continua só no Blender; a de dados
  passou a ter teste puro em `tests/test_017_build.py`, garantindo que separador e afastador chegam ao plano com papel
  e medidas, em vez de sumirem.
- A correção de T013 mexeu no que **este repositório** produz, não no legado: os caminhos ganharam sufixo por eixo
  (colunas `.b`, faixas `.a`) e a reserva é feita por irmandade. Se uma extração futura de `cabinet_editor.bays`
  encontrar só um formato, isso é divergência de nomenclatura, não regressão do legado.
- T021 não abre watch novo: os operadores só chamam o que T020 já criou, e a fumaça com `bpy` simulado mostrou o
  Cancelar devolvendo a espessura como texto do enum (`"15"`) — o mesmo formato que o `EnumProperty` aceita na volta.
  O `undo_push` de Aplicar e a colisão de `bl_idname` com o editor antigo só se resolvem de verdade no Blender (T033).
- T022 não cria watch item: a animação trabalha por matriz de mundo nas peças do próprio armário v2 e não altera nada do
  legado. O ponto a vigiar na fumaça é o timer: `_handles`/`_animacoes` precisam ficar vazios depois de `unregister()`,
  de arquivo novo e do alvo apagado no meio da animação; qualquer sobra aparece em T033.
- W008 ficou vermelha entre T021 e T022 porque o teste de i18n só rodou no fechamento de T022; ele agora faz parte da
  verificação de toda ação que cria texto de interface, não só da T034.
- T023 toca o único ponto sensível do legado até aqui: `Abrir` passa a criar um objeto novo na cena quando não existe
  armário v2. O objeto nasce na coleção própria (`CAFFMob Armário v2`) e a criação é recusada quando a seleção é um
  móvel da construção antiga, então o móvel antigo continua intocado (W006, RF-26). Na fumaça de T033, conferir que
  abrir num arquivo com móvel antigo não cria coleção nem objeto e mantém as peças no corte.
- `_MODULES` está em `('props', 'anim', 'ops', 'panel', 'menu', 'hud', 'ponte')`. **T027 executado:** `ops_editor` saiu
  do registro de `cabinet_editor`, então nada responde por `caffmob.cabinet_editor`, `ops._dividido` deixa de casar e
  o `Abrir` do armário v2 registra quando `ops` entrar na cascata (T030). A guarda ficou intacta de propósito: se
  `caffmob.cabinet_editor` voltar ao registro antes de T030, ela volta a segurar o `Abrir` em vez de duplicar o
  `bl_idname`. Conferência real (registro, `WindowManager.btm_cabinet_editor` ausente) fica para a fumaça de T033.
- T028 não abre watch item: as duas listas de modais gerenciados eram as últimas referências ao modal do editor 2D fora
  de `cabinet_editor/` e não guardam regra de domínio, só decidem se uma translação em andamento é corrigida. O ponto a
  conferir nas fumaças de T033/T034 é que a colisão volta a valer para G/gizmo com o editor 2D inativo e que o assentar
  não espera um operador sem registro.
- **T027 é a mudança de maior alcance no legado até aqui**, e ainda não foi verificada no Blender: a cascata real de
  `register()`/`unregister()` de `cabinet_editor` precisa ser exercitada em T033. O que não pode acontecer: algum
  módulo fora dos quatro registrados depender do que saiu (o caso conhecido é `reflow_handler` lendo
  `props.session()`, que continua funcionando sem a propriedade do `WindowManager`). W007 continua verde enquanto
  `gallery` estiver em `_modules()`; se alguém o tirar, o "Criar armário" da biblioteca quebra em
  `library_panel/ops_cabinet.py:46`.
- W010 precisa de leitura cuidadosa: `spec.carcass_lengths` reusa a função antiga só na montagem lateral passante. Na
  base passante as duas bases cobrem a largura (RN-04 da 017), o que a função da 012 não faz. Se uma extração futura
  encontrar as duas regras na mesma chave de watch, isso é divergência de leitura, não regressão.
