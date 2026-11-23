# Actions: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Roadmap: `_reversa_forward/017-construtor-armario-v2/roadmap.md`
> Pacote da extensão: `caffmob_draw/` (a cópia espelhada da raiz não é editada)

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 51 |
| Paralelizáveis (`[//]`) | 25 |
| Maior cadeia de dependência | 11 (T005 → T012 → T014 → T015 → T020 → T021 → T023 → T027 → T030 → T033 → T034) |

Fases: preparação 4, testes 7, núcleo 9, integração 28, polimento 3.

T041 a T051 entraram depois do clarify de 2026-11-23 (decisões D-21 e D-22, achados A001 a A004 da auditoria de mockup): T041 é núcleo e fica na Fase 3, os outros dez são integração. Só T042 e T045 são `[//]`. As cadeias novas são curtas (T041 → T043 → T044 e T045 → T046 → T049 → T051) e não alteram a maior cadeia.

T035 entrou depois do cross-check (achado A001), com ID novo: nenhum ID foi reciclado. T036 a T040 entraram depois da segunda auditoria (achados A012 e A013), também com IDs novos, e só T036 e T040 são `[//]`. A T039 abre uma segunda cadeia de 11 pelo mesmo T033 (T005 → T012 → T014 → T015 → T020 → T021 → T023 → T027 → T030 → T033 → T039), o que não muda a métrica do Resumo. T027 e T003 foram reescritos pelas decisões de 2026-11-21 (A002 e A003).

Três decisões de decomposição não estão no roadmap §5 e ficam registradas aqui: `vaos.py` existe porque RN-11 (duplicar) e RN-12 (inserção múltipla) não tinham módulo atribuído na lista de núcleos do roadmap; `corredica.py` existe porque o RN-08 também não tinha (D-19); e o núcleo tem nove módulos, não sete.

Regra de leitura: cada linha é um bloco coerente de um turno. `Dependências` lista IDs que precisam estar `[X]` antes; `Paralelismo` marca `[//]` quando a ação toca arquivo diferente das vizinhas da mesma onda e não depende de nenhuma delas.

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Copiar o modelo da corrediça telescópica de `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/assets/slide-st48-0200-0.obj` para `caffmob_draw/assets/slides/slide-st48-0200-0.obj` (o diretório não existe hoje), conferir que `build.py` o inclui no ZIP por empacotar `caffmob_draw/` inteiro e anotar em `investigation.md` o tamanho do arquivo e a contagem de objetos que ele traz (RN-08, D-12) | - | `[//]` | `caffmob_draw/assets/slides/slide-st48-0200-0.obj` | 🟢 | `[X]` |
| T002 | Criar o catálogo `armario_v2.json` com os textos em `pt_BR` e `en_US`, nos contextos padrão e de operador: nome do painel, sete abas, sub-abas de Divisões e de Gavetas, dez modelos de frente, rótulos de Gerar/Aplicar/Cancelar/Montar Caixa/Limpar/Abrir/Fechar/Duplicar/Excluir, avisos de contrato ausente, peça fora da chapa, vão insuficiente e móvel da construção antiga, e rótulos da barra de estado; conferir que nenhuma chave colide com `construtor_015.json`, `cabinet_editor.json` ou `drawers_072.json` (RN-20, RF-21) | - | `[//]` | `caffmob_draw/data/translations/armario_v2.json` | 🟢 | `[X]` |
| T003 | Criar `armario_v2/props.py` com os PropertyGroups do `data-delta.md`: `BTM_PG_ArmarioV2` (medidas em mm com `subtype='DISTANCE'`/`unit='LENGTH'`, montagem, oito espessuras por papel, porta, deslizante, fundo, acabamento, aba e sub-abas, as quatro flags de presença `lateral_esq_ativa`/`lateral_dir_ativa`/`base_inf_ativa`/`base_sup_ativa` em `False` (D-18, confirmado em 2026-11-21: presença por flag, sem enum de montagem), `aberto`, `gerado`, `origem`, `snapshot`) mais as coleções `BTM_PG_ArmarioDivisao`, `BTM_PG_ArmarioGaveta` e `BTM_PG_ArmarioInterno`; e `BTM_PG_ArmarioParte` e `BTM_PG_ContratoChapas`; todo `bpy.props` lido por atributo, cada anotação com `# type: ignore` e `register()`/`unregister()` próprios (D-02, D-11) | - | - | `caffmob_draw/armario_v2/props.py` | 🟢 | `[X]` |
| T004 | Criar `armario_v2/__init__.py` que declara a cascata de submódulos do pacote e expõe `register()`/`unregister()` encadeando por ora só `props`; `unregister()` precisa desfazer exatamente o que `register()` fez, para a ação T029 só acrescentar entradas nas cascatas (D-01, D-05) | T003 | - | `caffmob_draw/armario_v2/__init__.py` | 🟢 | `[X]` |

## Fase 2, Testes

Os testes puros vêm antes do núcleo, no padrão da 016: cada arquivo fixa o contrato em milímetros e roda sem `bpy`.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Escrever `test_017_spec.py` (unittest puro) cobrindo o spec base: faixas de `largura`/`altura`/`profundidade` e das dezesseis medidas do `data-delta.md`; encontro das chapas em lateral passante e em base passante (comprimento das bases e posição das laterais, RN-04); troca de orientação de contra-frente e de peça de trás trocando altura por profundidade; aceitação de espessura só em 6/15/18/25 com fundo nascendo em 6 e as demais em 15 (RN-05); recuo do fundo encaixado e sobreposto (RN-15) | - | `[//]` | `tests/test_017_spec.py` | 🟢 | `[X]` |
| T006 | Escrever `test_017_vaos.py` (unittest puro) cobrindo a árvore de vãos e as divisões: inserir divisória vertical nas quatro variantes e horizontal nas quatro; matriz de `linhas × colunas` com prioridade por eixo criando divisórias e prateleiras por vão resultante (RN-12); duplicar recusado abaixo de 80 mm livres e peça nova no meio do maior vão livre quando cabe (RN-11); caminho do vão estável entre inserções (mesmo formato de `cabinet_editor.bays`) | - | `[//]` | `tests/test_017_vaos.py` | 🟢 | `[X]` |
| T007 | Escrever `test_017_chapas.py` (unittest puro) cobrindo o contrato e a conferência: contrato vazio recusando geração, contrato semeado pelo padrão e sobrescrito por `apply_host_contract(...)`; peça de 3000 mm em chapa de 2750 listada com nome e medida; comparação do maior lado com o maior limite e do menor com o menor; bloqueio ligado impedindo qualquer peça e desligado gerando com aviso (RN-02, RN-03, RF-03, RF-04) | - | `[//]` | `tests/test_017_chapas.py` | 🟢 | `[X]` |
| T008 | Escrever `test_017_gavetas.py` (unittest puro) cobrindo o bloco de gavetas: quatro gavetas em 760 mm com folgas de 3 mm e alturas iguais; dez modelos de frente aceitos por gaveta e modelo único aplicado a todas; separador de `colunas × linhas` gerando as chapas de 6 mm; quatro afastadores independentes, desmarcar um removendo só aquela chapa (RN-07, RN-09, RF-09, RF-11) | - | `[//]` | `tests/test_017_gavetas.py` | 🟢 | `[X]` |
| T009 | Escrever `test_017_portas.py` (unittest puro) cobrindo portas: duas folhas num armário de 1000 mm com espessura por papel e dobradiça alternada abrindo em sentidos opostos (RF-13); folha deslizante por `(comprimento + (n − 1) × sobreposição) / n` para 2 a 4 folhas; exclusividade entre deslizante e portas de abrir; recuo de divisórias, prateleiras, gavetas e internos na profundidade do trilho com base por dentro e nenhum recuo com base na frente, mantendo laterais e bases na profundidade total (RN-06, RN-14, RF-14) | - | `[//]` | `tests/test_017_portas.py` | 🟢 | `[X]` |
| T010 | Escrever `test_017_internos.py` (unittest puro) cobrindo internos: calceiro e sapateira nascendo a 480 mm do piso do vão e maleiro a 420 mm abaixo do topo; faixa editável `[0, altura do vão − espessura do interno]`; interno preso ao vão escolhido; e a regra de desempate de dois internos na mesma altura (o último vence, o outro sobe 50 mm), que é premissa 🟡 do roadmap §4 e precisa ficar isolada num teste para ser corrigida sem tocar nas abas (RN-13, RF-12) | - | `[//]` | `tests/test_017_internos.py` | 🟡 | `[X]` |
| T011 | Escrever `test_017_resumo.py` (unittest puro) cobrindo o resumo e a lista de peças: linha de estado com dimensões, montagem, vão e peça escolhidos, e conformidade de chapa em texto além da cor; lista com nome, largura, altura, espessura e marca de fora-da-chapa por peça; peça de ferragem (trilho, gaiola) ausente da lista (RN-16, RN-19, RF-18, RF-19) | - | `[//]` | `tests/test_017_resumo.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

Tudo em milímetros, sem `bpy`: `spec`, `vaos`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo`.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Implementar `spec.py` com o spec imutável em milímetros: as dezesseis medidas e suas faixas, montagem e orientações, espessuras por papel, porta, deslizante e fundo, mais `carcass_lengths` por montagem reaproveitando `cabinet_editor.structure.carcass_lengths` em vez de duplicar a conta (D-10); o spec não converte unidade, quem converte é o `build` em T020 (RN-04, RN-05, RN-15) | T005 | - | `caffmob_draw/armario_v2/spec.py` | 🟢 | `[X]` |
| T013 | Implementar `vaos.py` com a árvore de vãos: inserir e remover divisória vertical e horizontal nas quatro variantes, matriz de linhas × colunas com prioridade por eixo, e `duplicar` respeitando o vão livre mínimo de 80 mm e nascendo no meio do maior vão livre, devolvendo recusa com motivo quando não cabe (RN-11, RN-12) | T006, T012 | `[//]` | `caffmob_draw/armario_v2/vaos.py` | 🟢 | `[X]` |
| T014 | Implementar `chapas.py` com o contrato de chapas (chapa máxima, oito espessuras por papel, montagem e orientações padrão, `configurado`), a semeadura a partir de `standards.api.active_definition` com a reserva do `dimension_schema` BR quando não houver padrão ativo, e `apply_host_contract(...)` como função pública de injeção (RN-02, D-11, RF-03) | T007, T012 | `[//]` | `caffmob_draw/armario_v2/chapas.py` | 🟢 | `[X]` |
| T015 | Implementar `conferencia.py`: conferir cada peça do armário contra a chapa máxima comparando maior lado com maior limite e menor com menor, devolver a lista de violações com nome do papel e medida, e decidir entre bloquear a geração ou liberar com aviso conforme `bloquear_chapa` (RN-03, RN-16, RF-04); uma implementação só da comparação, que `cutting/part_extractor.limit_status` passa a delegar (D-09) — se o import de `part_extractor` arrastar `bpy`, a comparação fica no núcleo e `limit_status` delega para ele, nunca o contrário | T014 | `[//]` | `caffmob_draw/armario_v2/conferencia.py` | 🟢 | `[X]` |
| T016 | Implementar `gavetas.py`: distribuir o bloco de gavetas no vão com folga de 3 mm entre gavetas e nas pontas, altura por gaveta pela divisão do bloco descontadas as folgas, os dez modelos de frente por gaveta ou únicos, separador por colunas e linhas em chapa de 6 mm e os quatro afastadores independentes, e o recuo de 70 mm do trilho quando a base do deslizante é por dentro (RN-06, RN-07, RN-09) | T008, T012 | `[//]` | `caffmob_draw/armario_v2/gavetas.py` | 🟢 | `[X]` |
| T017 | Implementar `portas.py`: portas de abrir com folhas, espessura por papel, dobradiça esquerda/direita/alternada e sentido de abertura por folha (95°); porta deslizante de 2 a 4 folhas com sobreposição padrão de 30 mm e largura por `(comprimento + (n − 1) × sobreposição) / n`; exclusividade entre as duas; materiais MDF, vidro e alumínio (RN-10, RN-14) | T009, T012 | `[//]` | `caffmob_draw/armario_v2/portas.py` | 🟢 | `[X]` |
| T018 | Implementar `internos.py`: cabideiro, calceiro, sapateira e maleiro presos ao vão escolhido, com calceiro e sapateira a 480 mm do piso e maleiro a `altura do vão − 420`, posição vertical editável dentro de `[0, altura do vão − espessura do interno]` e a regra de desempate de 50 mm de dois internos na mesma altura (RN-13, premissa 🟡 do roadmap §4) | T010, T012 | `[//]` | `caffmob_draw/armario_v2/internos.py` | 🟡 | `[X]` |
| T019 | Implementar `resumo.py`: linha de estado em texto (dimensões, montagem, vão e peça escolhidos, conformidade de chapa) e lista de peças com nome do papel, comprimento, largura, espessura e marca de fora-da-chapa, pronta para o painel, o inspetor e o adaptador de corte consumirem sem recalcular (RN-16, RN-19) | T011 | `[//]` | `caffmob_draw/armario_v2/resumo.py` | 🟢 | `[X]` |
| T041 | Corrigir a contra-frente e a peça de trás para a travessa do motor anexo: constante `ALTURA_TRAVESSA = 90.0`, as presenças `contra_frente_ativa` e `peca_tras_ativa` no `Spec` (ambas `False`, D-22) e as duas funções devolvendo `{'comprimento': largura_interna, 'altura': ALTURA_TRAVESSA, 'espessura': espessura_base_superior, 'em_pe': orientação == EM_PE}`; atualizar `tests/test_017_spec.py`, que hoje espera 2000 mm em pé e 560 mm deitada, para 90 mm nos dois casos com `em_pe` distinguindo a orientação (RN-04, D-22, RF-05) | T012, T005 | - | `caffmob_draw/armario_v2/spec.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T020 | Implementar `build.py`: emitir as peças a partir do spec em metros (divisão por 1000 num único ponto), uma malha por chapa com `btm_armario_parte` preenchido (papel, componente, comprimento, largura, espessura, material, veio, fitas, `uid`, `movel`, `curso_mm`, `eixo`), raiz vazia do armário na collection própria e peças filhas, fundo encaixado ou sobreposto, e os quatro acabamentos com vidro e alumínio em materiais próprios (RN-19, RN-24, D-02, RF-17) | T012, T013, T015, T016, T017, T018, T003 | - | `caffmob_draw/armario_v2/build.py` | 🟢 | `[X]` |
| T021 | Implementar `ops.py` com o controlador do construtor no `bl_idname` `caffmob.cabinet_editor` (D-03) e os operadores `Gerar`, `Aplicar`, `Cancelar` e `Limpar` com `bl_options = {'REGISTER', 'UNDO'}`: `Gerar` reconstrói a partir do spec e recusa sem contrato, `Cancelar` restaura o `snapshot` JSON gravado na abertura e apaga as peças geradas, `Aplicar` grava um passo sem fechar; abrir o painel não cria passo de desfazer (RN-18, RF-01, RF-22) | T020, T004 | - | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T022 | Implementar `anim.py` com o timer de 16 ms e no máximo 18 quadros por alvo: gaveta a 72% da profundidade com as gaiolas a 50% do curso, folha deslizante a 80% da própria largura com sentidos opostos entre folhas, porta de abrir a 95° no sentido da dobradiça; estado em `btm_armario.aberto`, rótulo sempre da ação oposta, handle em dicionário de módulo removido em todos os caminhos de saída (RN-10, D-08, RF-16) | T021 | - | `caffmob_draw/armario_v2/anim.py` | 🟢 | `[X]` |
| T023 | Implementar `panel.py` com o `BTM_PT_ArmarioV2` na sidebar `View3D > CAFFMob Draw`: sete abas num `EnumProperty`, sub-abas de Divisões (Vertical, Horizontal, Múltipla) e de Gavetas num segundo `EnumProperty`, cabeçalho com tipo e vão ativo, estado de janela vazia com Montar Caixa e Limpar, e o aviso de móvel da construção antiga desabilitando Gerar e Aplicar (RN-01, RN-22, RN-23, D-05, D-14, RF-01, RF-02, RF-26) | T004, T021 | - | `caffmob_draw/armario_v2/panel.py` | 🟢 | `[X]` |
| T024 | Implementar `menu.py` em `VIEW3D_MT_object_context_menu` por `_append`/`_remove`: Abrir/Fechar nas gavetas, portas e folhas com o rótulo oposto ao estado, Duplicar e Excluir só em divisória e prateleira, e os itens filtrados pelo armário ativo subindo a hierarquia até a raiz com `btm_armario`; remoção do item de menu no `unregister` (RN-10, RN-11, RN-22, D-06, RF-25) | T021, T013 | `[//]` | `caffmob_draw/armario_v2/menu.py` | 🟢 | `[X]` |
| T025 | Implementar `hud.py` com o estado à mão na vista 3D: alternadores da estrutura enquanto o armário está vazio, inspetor da peça escolhida e realce da seleção, em `POST_PIXEL` com `canvas2d` e `hb_gpu_draw.point_in_rect`, com os handlers removidos em `unregister` (RN-22, RF-25) | T023 | `[//]` | `caffmob_draw/armario_v2/hud.py` | 🟡 | `[X]` |
| T026 | Implementar `ponte.py`: mapear um módulo de biblioteca (frameless, face frame, closets) para o spec v2 lendo medida e espessuras de `btm_cabinet`/`btm_structure`, montagem de `assembly`, portas de `door_swing` e divisões de `scene_divisions`; e `Gerar` a partir de módulo ocultando o módulo antigo e marcando `btm_cut_exclude`, com reversão por `Recriar do módulo`; módulo sem correspondência completa abre a aba vazia em vez de falhar (RN-21, D-13, RF-24) | T020, T021 | - | `caffmob_draw/armario_v2/ponte.py` | 🟡 | `[X]` |
| T027 | Tirar a interface do registro de `cabinet_editor`: `_modules()` passa a carregar `data_props`, `previews`, `reflow_handler` e `gallery` (mantida pela decisão de 2026-11-21: `library_panel/ops_cabinet.py:46-47` chama `caffmob.structure_gallery` sem guarda), deixando `window`, `ops_editor`, `ops_actions` e `panels*` fora; `WindowManager.btm_cabinet_editor` deixa de ser registrado; os núcleos puros (`structure`, `structures_core`, `divisions`, `structure_inputs`) continuam importáveis para `geometry/mesh_gen.py`, `customize/adapters`, `standards` e `cutting` (D-04) | T023, T021 | - | `caffmob_draw/cabinet_editor/__init__.py` | 🟢 | `[X]` |
| T028 | Tirar `caffmob.cabinet_editor_modal` das listas de modais gerenciados em `collision/guard.py:44` e `stick/settle.py:21`, que passam a tratar só `caffmob.move_over_drag` e `caffmob.move_over_dialog`; sem tocar no resto desses arquivos (roadmap §5) | T027 | `[//]` | `caffmob_draw/collision/guard.py` | 🟢 | `[X]` |
| T029 | Acrescentar o adaptador novo ao corte: `armario_v2_records(scene)` em `part_sources.py` varrendo as malhas com `btm_armario_parte` e ignorando `btm_cut_exclude` e objeto oculto, como `_visible` já faz, devolvendo `PartRecord` com `source="ARMARIO_V2"`; e somar esse adaptador em `extract_production_parts` depois das gavetas, sem duplicar peça de ferragem e sem listar malha sem papel gravado (RN-19, RN-24, RF-19) | T020 | `[//]` | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T030 | Registrar o pacote novo na extensão: `"armario_v2"` em `_submodule_names` (`caffmob_draw/__init__.py:9`), import explícito junto de `customize`/`cabinet_editor`, `armario_v2.register()` depois de `customize.register()` e antes de `cabinet_editor.register()`, e `armario_v2.unregister()` na cascata de desregistro antes de `cabinet_editor.unregister()`; nada pendurado depois de desregistrar (D-05, RF-23) | T027 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T031 | Subir `caffmob_draw/blender_manifest.toml` de `1.25.0` para `1.26.0` e conferir que `python3 build.py` aceita empacotar com o OBJ da corrediça presente (D-16) | - | `[//]` | `caffmob_draw/blender_manifest.toml` | 🟢 | `[X]` |
| T035 | Corrigir a duplicação de peças no corte (achado A001): filtrar em `iter_modules` o módulo oculto ou com `btm_cut_exclude`, para o caminho sintético parar de emitir as peças do módulo convertido, e cobrir com `tests/test_017_corte.py` contando as peças antes e depois de `Gerar` a partir de um módulo de biblioteca (D-17, RN-24, RF-19) | T029 | - | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T036 | Implementar `corredica.py` (núcleo puro, sem `bpy`): medidas em milímetros das três partes do conjunto telescópico ST48 (trilho externo na lateral do vão, trilho interno na caixa da gaveta e as gaiolas a meio curso), posição de cada parte relativa à caixa da gaveta, recuo do trilho quando a base do deslizante é por dentro, lista de peças de ferragem com `papel` vazio e `ferragem` preenchido, e o casamento dos quatro objetos do OBJ com esses papéis para o `build` (RN-08, D-19, RF-10) | T016, T012 | `[//]` | `caffmob_draw/armario_v2/corredica.py` | 🟢 | `[X]` |
| T037 | Acrescentar a `ferragem` (`NENHUMA`, `TRILHO_EXT`, `TRILHO_INT`, `GAIOLA`) a `BTM_PG_ArmarioParte` em `props.py` e instanciar a corrediça em `build.py`: importar `assets/slides/slide-st48-0200-0.obj` uma vez por armário com `bpy.ops.wm.obj_import` (o mesmo do `promob/complemento.py:283`, com `forward_axis='Y'` e `up_axis='Z'`, isolado em `compat.py` se a chamada variar por versão), criar o conjunto por gaveta como filho da caixa da gaveta com `btm_armario_parte` de `papel` vazio e `ferragem` preenchida, cair no conjunto de reserva de T036 quando o arquivo faltar, e fazer `anim.py` ler `ferragem` no lugar de `PAPEIS_GAIOLA` (RN-08, RN-10, D-19, RF-10, RF-16) | T036, T020 | - | `caffmob_draw/armario_v2/build.py` | 🟢 | `[X]` |
| T038 | Escrever `test_017_corredica.py` (unittest puro, sem `bpy`) cobrindo a corrediça do núcleo: duas corrediças por gaveta, as três partes com `ferragem` preenchida e `papel` vazio, trilho externo na lateral do vão e interno na caixa da gaveta, recuo do trilho com base por dentro, mesmas medidas no conjunto de reserva quando não há arquivo, e nenhuma parte listada por `resumo.lista_de_pecas` nem por `conferencia.conferir` como peça de chapa (RN-08, RF-10, RF-19) | T036 | - | `tests/test_017_corredica.py` | 🟢 | `[X]` |
| T039 | Acrescentar à fumaça `blender_017_armario_smoke.py` a conferência da corrediça na cena: bloco de quatro gavetas com `corredica_3d` ligado gera duas instâncias por gaveta com trilho externo, trilho interno e gaiola, filhas da caixa da gaveta e com `papel` vazio; com o OBJ movido para fora do caminho, a geração cai no conjunto de reserva com as mesmas três marcas e Abrir/Fechar continua movendo a gaiola a 50% do curso; e o plano de corte segue sem peça de corrediça (RN-08, RN-10, D-19, RF-10) | T037, T033 | - | `tests/blender_017_armario_smoke.py` | 🟢 | `[X]` |
| T040 | Escrever `blender_017_reabrir_smoke.py` (headless, `--python-exit-code 1`, padrão de `blender_067_ciclo_vida.py`): criar o armário vazio pelo Abrir, montar três vãos com uma divisória e duas prateleiras, quatro gavetas e folha deslizante, gerar, salvar em `tempdir` com `save_as_mainfile`, reabrir com `open_mainfile` e conferir que `Object.btm_armario` devolve as mesmas medidas, montagem, divisões, gavetas, portas, deslizante e fundo, que o `snapshot` sobreviveu e que a coleção continua com as mesmas peças de papel gravado (RN-17, D-02, D-20, RF-20) | T021, T023 | `[//]` | `tests/blender_017_reabrir_smoke.py` | 🟢 | `[X]` |
| T042 | Acrescentar `contra_frente_ativa` e `peca_tras_ativa` a `BTM_PG_ArmarioV2`, logo depois de `orientacao_tras`, ambas `False` e com rótulo e descrição em português (RF-05, D-22) e conferir que `ops._dados` já as leva ao `Spec` sem lista de campos extra | T003, T041 | `[//]` | `caffmob_draw/armario_v2/props.py` | 🟢 | `[X]` |
| T043 | Emitir as duas travessas em `build.pecas`: acrescentar `CONTRA_FRENTE` e `PECA_TRAS` a `COMPONENTES` com o código `TRA`, entre as laterais e no topo interno (`altura - espessura_base_superior`), com a contra-frente na face da frente e a peça de trás encostada na face interna do fundo (ou na face de trás, sem fundo); `EM_PE` deixa os 90 mm na altura e a espessura na profundidade, `DEITADA` troca os dois eixos, e a peça leva `veio='HORIZONTAL'` e a fita da frente (RN-04, D-22, RF-05) | T041, T042 | - | `caffmob_draw/armario_v2/build.py` | 🟡 | `[X]` |
| T044 | Acrescentar à fumaça `blender_017_armario_smoke.py` a conferência das travessas: com as duas flags marcadas, o armário gerado tem uma peça `CONTRA_FRENTE` e uma `PECA_TRAS` de 90 mm entre as laterais; a contra-frente `DEITADA` troca o eixo de 90 mm na caixa da peça; desmarcar uma remove só aquela peça da cena e do plano de corte; e a lista de peças mostra as duas com nome, medida e espessura (RN-04, RN-19, D-22, RF-05, RF-19) | T043, T033 | - | `tests/blender_017_armario_smoke.py` | 🟡 | `[X]` |
| T045 | Levar o vão ativo para o núcleo de operações e criar os gravadores das coleções: `ops.vao_ativo(armario)` com o mesmo critério de `panel._vao_ativo` (índice ativo das três coleções e `s0` sem escolha), `ops.gravar_gavetas` e `ops.gravar_internos` no molde de `gravar_divisoes`, e o painel passando a delegar no `ops.vao_ativo` (D-21) | T021, T023 | `[//]` | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T046 | Criar `caffmob.armario_v2_inserir_divisoria` (eixo `VERTICAL`/`HORIZONTAL`, variante do núcleo e posição opcional) e `caffmob.armario_v2_inserir_matriz` (linhas e colunas de 1 a 5, prioridade por eixo): ler o vão ativo, chamar `vaos.inserir_vertical`/`inserir_horizontal`/`matriz`, regravar com `gravar_divisoes`, gerar quando o armário já foi gerado e reportar aviso sem gravar nada quando o núcleo levantar `ValueError`; `bl_options = {'REGISTER', 'UNDO'}` (RN-11, RN-12, D-21, RF-07) | T045 | - | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T047 | Criar `caffmob.armario_v2_criar_bloco_gavetas`: propriedades de quantidade (1 a 10), altura do bloco em mm e modelo único, chamada a `gavetas.bloco`, gravação com `gravar_gavetas` respeitando o `indice` por gaveta, geração quando o armário já foi gerado e recusa com aviso quando o bloco não cabe no vão (RN-07, D-21, RF-09) | T045 | - | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T048 | Criar `caffmob.armario_v2_inserir_interno` com o tipo em enum (`CABIDEIRO`, `CALCEIRO`, `SAPATEIRA`, `MALEIRO`): altura do vão do caminho ativo por `vaos.regioes`, chamada a `internos.inserir` com a posição inicial do tipo e a espessura da prateleira, gravação com `gravar_internos` e geração quando o armário já foi gerado (RN-13, D-21, RF-12) | T045 | - | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T049 | Desenhar a inserção na aba Divisões do painel: `Inserir divisória` e `Inserir prateleira` no topo da aba, com a variante em enum, e `Inserir matriz` com linhas, colunas e prioridade só na sub-aba `Múltipla`, chamando os operadores de T046 e mantendo a lista de peças existentes como está (D-21, RF-07) | T046 | - | `caffmob_draw/armario_v2/panel.py` | 🟢 | `[X]` |
| T050 | Desenhar a inserção nas abas Gavetas e Internos: campos de quantidade, altura do bloco e modelo mais o botão `Criar bloco de gavetas`, e os quatro botões de interno (`Cabideiro`, `Calceiro`, `Sapateira`, `Maleiro`), chamando os operadores de T047 e T048 (D-21, RF-09, RF-12) | T047, T048 | - | `caffmob_draw/armario_v2/panel.py` | 🟢 | `[X]` |
| T051 | Acrescentar à fumaça `blender_017_armario_smoke.py` o caminho de inserção: a partir do armário montado, chamar os quatro operadores e conferir a peça criada em cada coleção, o vão do cabeçalho igual ao vão da inserção, um único passo de desfazer por clique (`Ctrl+Z` simulado por `bpy.ops.ed.undo`), a matriz de 2 × 1 criando uma divisória e duas prateleiras, e o aviso sem escrita quando a posição cai fora do vão (RN-11, RN-12, RN-18, D-21, RF-07, RF-09, RF-12) | T049, T050 | - | `tests/blender_017_armario_smoke.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T032 | Fechar o catálogo e os textos de operação: completar `armario_v2.json` com toda chave nova que o painel, o menu, o inspetor, a barra de estado e as mensagens de recusa passaram a usar, nas duas línguas e nos dois contextos, e conferir que nenhuma mensagem de erro deixa traceback em contrato ausente, chapa inválida ou modelo da corrediça faltando (RN-20, RF-21, RF-18) | T023, T024, T025, T026 | - | `caffmob_draw/data/translations/armario_v2.json` | 🟢 | `[X]` |
| T033 | Escrever `tests/blender_017_armario_smoke.py` (headless, `--python-exit-code 1`) no padrão das features 004/006/008/016: construtor abre vazio, Montar Caixa gera a caixa, contrato ausente recusa, chapa de 3000 bloqueia e depois gera com aviso, bloco de gavetas com corrediça e sem o OBJ, deslizante recuando os internos, abrir/fechar com estado gravado, Cancelar restaurando o snapshot, módulo de biblioteca ocultando o antigo, armário antigo intocado, corte listando as peças do armário v2 sem a corrediça e `unregister()` sem operador, propriedade, menu ou timer pendurado (roadmap §10) | T021, T022, T023, T026, T029, T030 | - | `tests/blender_017_armario_smoke.py` | 🟢 | `[X]` |
| T034 | Fechar a verificação da feature: `ruff check caffmob_draw/`, `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`, os nove testes puros da 017 (`test_017_build.py` e `test_017_corte.py` incluídos) mais `tests/test_i18n_coverage.py`, e as fumaças `blender_017_armario_smoke.py`, `blender_004_*`, `blender_006_*`, `blender_008_construtor_smoke.py` e `blender_015_*` sem regressão; registrar em Notas de execução o que passou e o que ficou para conferência com janela (roadmap §10) | T032, T033, T031, T028, T035 | - | `_reversa_forward/017-construtor-armario-v2/actions.md` | 🟢 | `[X]` |

## Notas de execução

### 2026-11-21, T001 e T002

- **T001 `[X]`.** `caffmob_draw/assets/slides/` criado; `slide-st48-0200-0.obj` copiado do anexo (254.513 bytes, SHA-256 `209d2ba9bcccb591cdcf4569a4092df5a971c63bc5f97428b439ce79cccb17ba`, idêntico à origem). O arquivo traz **4 objetos** (`slide-st48-0200-0_1` a `_4`, um por trilho/gaiola/trilho interno), 2.572 vértices e 5.156 faces — o conjunto telescópico completo que o RN-08 descreve. `build.py` percorre `caffmob_draw/` inteiro com `os.walk` e só exclui `__pycache__` e o `catalog/` da raiz, então `assets/slides/` entra no ZIP sem mudança no empacotador.
- **T002 `[X]`.** `armario_v2.json` criado com **39 entradas novas** em `pt_BR` e `en_US`: nome do painel, sub-abas de Divisões (Múltipla) e de Gavetas (Sapateiras, Prat. c/ Corrediça), os dez modelos `s_cf_*`/`c_cf_*` com as descrições do `DRAWER_MODEL_ITEMS` do anexo, Montar Caixa, Limpar, estado vazio, os quatro avisos e os rótulos da barra de estado. **11 chaves foram deixadas de fora porque já existem em outro catálogo** e são reaproveitadas: as sete abas (nenhuma faltando), `Vertical` e `Horizontal` (`aggregates.json`), `Internas` (`cabinet_editor.json`), `Externas` (`construtor_015.json`), `Gerar` (`cladding.json`), `Aplicar`, `Cancelar`, `Fechar`, `Duplicar`, `Excluir` (`geral.json`) e `Abrir` (`ui.json`). O teste `tests/test_i18n_coverage.py` passou (3 testes, inclusive unicidade global de msgid e campos `{}` iguais).
- Nenhum arquivo de `caffmob_draw/` fora de `assets/slides/` e `data/translations/armario_v2.json` foi tocado.

### 2026-11-21, T003

- **T003 `[X]`.** `caffmob_draw/armario_v2/props.py` criado com os três grupos do `data-delta.md` e mais as três
  coleções internas do armário:
  - `BTM_PG_ArmarioV2`: medidas externas em mm com `subtype='DISTANCE'`/`unit='LENGTH'`, montagem e orientações,
    as nove espessuras por papel (fundo nascendo em 6, as demais em 15), `bloquear_chapa=True`, as quatro flags de
    presença `lateral_esq_ativa`/`lateral_dir_ativa`/`base_inf_ativa`/`base_sup_ativa` em `False` (D-18), as
    coleções `divisoes`/`gavetas`/`internos`, porta, deslizante, `fundo_ativo`/`fundo_fixacao`/`fundo_recuo`,
    acabamento, aba e sub-abas, `aberto=False`, `gerado=False`, `origem` e `snapshot`.
  - `BTM_PG_ArmarioParte`: papel, componente, medidas de corte, material, veio, as quatro fitas, `uid`, `movel`,
    `curso_mm` e eixo.
  - `BTM_PG_ContratoChapas`: chapa máxima 2750 × 1830, as oito espessuras do contrato, montagem e orientações
    padrão e `configurado=False`.
- `register()` registra as seis classes e pendura `Object.btm_armario`, `Object.btm_armario_parte` e
  `Scene.btm_armario_contrato`; `unregister()` desfaz na ordem inversa com guarda de `hasattr`, para a cascata de T004
  só encadear `props.register()`/`props.unregister()`. Toda anotação leva `# type: ignore` e nada é lido por
  `obj["..."]` (D-02, D-11).
- O `data-delta.md` fala em "oito espessuras", mas a tabela do §2 lista **nove** (a `espessura_folha` da porta
  deslizante não existe no contrato de chapas). O código segue a tabela: nove no armário, oito no contrato.
- O verificador de i18n apontou **20 textos novos** nos itens de enum (medidas, orientações, acabamentos, internos e
  o veio), todos incluídos no `armario_v2.json`, que passou de 39 para **59 entradas**.
- Verificação desta ação: `ruff check caffmob_draw/armario_v2/props.py` sem aviso, `check_api.py` sem
  `[UNKNOWN in 5.2]` e `tests/test_i18n_coverage.py` com os 3 testes OK (0 textos sem tradução). **Não** houve
  execução no Blender: `register()`/`unregister()` só serão exercitados na fumaça de T033.

### 2026-11-21, T004

- **T004 `[X]`.** `caffmob_draw/armario_v2/__init__.py` criado com a cascata `_MODULES = ('props',)` e
  `register()`/`unregister()` percorrendo a **mesma** tupla (invertida no desregistro): o que sai é exatamente o que
  entrou, e as ações seguintes só acrescentam nomes à tupla (D-01, D-05).
- O import é tardio, dentro de `_modules()`, como em `cabinet_editor`: importar `caffmob_draw.armario_v2` fora do
  Blender não carrega `bpy`, então os testes puros da Fase 2 importam `spec`, `vaos` e companhia sem mock. O
  docstring fixa a ordem futura da cascata (`props`, `build`, `ops`, `anim`, `panel`, `menu`, `hud`, `ponte`) e
  anota que os oito núcleos puros nunca entram nela.
- O `data-delta.md` passou a dizer com todas as letras o que o código de T003 já fazia: **nove espessuras no armário**
  (§2) e **oito no contrato** (§4). A diferença é a `espessura_folha`, frente de ferragem que não entra no contrato de
  chapa do fornecedor; quem lê o contrato não deve esperar essa chave.
- Verificação desta ação: `ruff check caffmob_draw/armario_v2/` sem aviso, `check_api.py` sem `[UNKNOWN in 5.2]` e
  carga do pacote com `bpy` simulado — `register()` registrou as seis classes e pendurou `Object.btm_armario`,
  `Object.btm_armario_parte` e `Scene.btm_armario_contrato`, e `unregister()` removeu tudo, sem sobra. Sem execução
  no Blender: o registro real segue para a fumaça de T033.

### 2026-11-21, T005 a T011

- **T005 a T011 `[X]`.** Os sete testes puros da Fase 2 escritos: `tests/test_017_spec.py`, `test_017_vaos.py`,
  `test_017_chapas.py`, `test_017_gavetas.py`, `test_017_portas.py`, `test_017_internos.py` e `test_017_resumo.py`
  (34 casos). Todos usam `import _bootstrap  # noqa: F401` e importam só o pacote puro: nenhum deles carrega `bpy`,
  o que já era possível graças ao import tardio de `armario_v2/__init__.py` (T004).
- **Estado de execução: verdes por skip declarado.** O núcleo que eles exercitam é da Fase 3 (T012 a T019), então
  cada arquivo importa o seu módulo por `importlib` e, se ele ainda não existe, pula a suíte inteira com motivo
  nomeando a ação que a libera: `Ran 34 tests ... OK (skipped=34)`, exit 0. O skip é automático: quando o módulo
  nasce em T012–T019, a suíte passa a rodar sem edição no teste. **Nenhuma asserção foi avaliada nesta rodada**;
  os 34 casos viram verificação de verdade na primeira execução da Fase 3.
- **Contrato fixado pelos testes** (é o que T012–T019 precisam cumprir): `spec.RANGES`, `THICKNESS_FIELDS`,
  `thickness_ok`, `carcass_lengths`, `lateral_offset_z`, `contra_frente`, `peca_de_tras`, `fundo`,
  `profundidade_util`; `vaos.Divisao`/`Vao`, `VARIANTES_VERTICAIS`/`VARIANTES_HORIZONTAIS`, `arvore`,
  `inserir_vertical`, `inserir_horizontal`, `matriz`, `duplicar` (devolve `(lista, nova, motivo)`) e `remover`;
  `chapas.Contrato`/`PAPEIS`/`contrato_vazio`/`padrao`/`apply_host_contract`/`pode_gerar`;
  `conferencia.Peca`/`Violacao`/`Decisao`/`conferir`/`decidir`; `gavetas.Gaveta`/`MODELOS`/`FOLGA`/`alturas`/
  `bloco`/`chapas`; `portas.Folha`/`MATERIAIS`/`ABERTURA_GRAUS`/`portas_de_abrir`/`folhas_deslizantes`/
  `exclusividade`/`recuo_por_papel`; `internos.Interno`/`TIPOS`/`ALTURA_BAIXA`/`MALEIRO_ABAIXO_TOPO`/
  `PASSO_DESEMPATE`/`altura_inicial`/`faixa`/`inserir`/`resolver`; `resumo.linha_estado`/`lista_de_pecas`.
- **As quatro variantes** de divisória (`movel_s_recuo`, `movel_c_recuo`, `montante`, `distanciador`) e de
  prateleira (`prat_s_recuo`, `prat_c_recuo`, `prat_fixa`, `prat_corredica`) saíram do mockup do anexo
  (`mockup_construtor_armarios.html`, aba Divisões): o distanciador duplo tem 30 mm, as variantes `c_recuo` recuam
  15 mm na traseira e a `prat_fixa` recua 20 mm na frente. O `data-delta.md` só lista `FIXA`/`MOVEL`/`ESPACADOR`;
  a variante fica em campo próprio, sem inventar item de enum novo.
- **Divergência de contagem, registrada e não silenciada.** O texto de T005/T012 fala em "dezesseis medidas"; o
  `data-delta.md` §2 lista **dezessete** campos de medida (nove espessuras por papel + oito medidas com faixa). O
  teste `test_todas_as_medidas_do_delta` fixa 9 + 8 = 17 e o delta continua sendo a verdade.
- **Dependência extra de T019.** `resumo.linha_estado` recebe o `spec` e o `conferencia.Violacao`; por isso
  `test_017_resumo.py` só sai do skip quando `spec`, `chapas`, `conferencia` e `resumo` existirem.
- Verificação desta ação: `python3 -m unittest discover -s tests -p 'test_017_*.py' -v` → 34 testes, 0 falhas,
  34 skips com motivo, exit 0; `ruff check` nos sete arquivos sem aviso. Sem Blender, como manda a Fase 2.

### 2026-11-21, T012 a T019

- **T012 `[X]`.** `caffmob_draw/armario_v2/spec.py` criado: `Spec` congelado em milímetros com as **17 medidas** do
  `data-delta.md` (`THICKNESS_FIELDS` com as 9 espessuras + `RANGES` com as 8 medidas de faixa), `thickness_ok`,
  `validate` (faixas, espessuras e exclusividade das portas), `largura_interna`/`altura_interna`,
  `carcass_lengths`, `lateral_offset_z`, `contra_frente`, `peca_de_tras`, `fundo` e `profundidade_util`.
- **D-10 cumprida em parte, por divergência real, não por preguiça.** `carcass_lengths` delega para
  `cabinet_editor.structure.carcass_lengths` na **lateral passante** (mesma regra da feature 012, 2000/2000/970/970).
  Na **base passante** a conta é feita no `spec.py` porque a função antiga mantém o topo entre as laterais
  (1985/1985/1000/970), enquanto a RN-04 desta feature diz que **as duas bases** cobrem a largura
  (1970/1970/1000/1000). O `test_017_spec.py` já fixava os números da RN-04; nenhum teste foi enxugado — o contrato
  não inventou API além do que o §2 e a RN-04/RN-15 pedem. A divergência está no docstring e fica registrada para o
  `/reversa-sync`.
- **T013 `[X]`.** `vaos.py`: `Divisao`/`Vao`, as quatro variantes de cada eixo tiradas do mockup, `arvore` (caminhos
  `s0`, `s0.b`, `s0.b.b`, mesmo formato de `cabinet_editor.bays`), `inserir_vertical`/`inserir_horizontal`, `matriz`
  (as posições são planejadas antes de inserir, por isso a prioridade só muda a **ordem** da lista), `duplicar`
  (recusa quando alguma das metades fica abaixo de 80 mm, novo no meio do maior vão livre) e `remover`.
- **T014 `[X]`.** `chapas.py`: `PAPEIS` com **oito** papéis (sem `espessura_folha`), `Contrato` congelado,
  `contrato_vazio()` recusando geração, `padrao()` (2750 × 1830, fundo 6, demais 15) e `apply_host_contract(...)`
  sobrescrevendo só o que vier. A semeadura a partir de `standards.api.active_definition` precisa da cena do Blender,
  então fica no painel (T023), que injeta o resultado por `apply_host_contract`; o núcleo continua sem `bpy`.
- **T015 `[X]`.** `conferencia.py`: `Peca`, `Violacao` (com `.texto()`), `Decisao`, `conferir` (maior lado com maior
  limite e menor com menor) e `decidir`, que também recusa quando `pode_gerar` aponta contrato ausente. A delegação
  de `cutting/part_extractor.limit_status` para cá **não** foi feita nesta ação: `part_extractor` carrega `bpy` e é
  caminho de corte, então a troca fica junto de T029/T034, com a dependência apontando do corte para o núcleo.
- **T016 `[X]`.** `gavetas.py`: `FOLGA = 3.0`, `alturas` (760 mm e 4 gavetas → 186,25 mm cada), `MODELOS` com os dez
  `s_cf_*`/`c_cf_*`, `bloco` recusando modelo fora da lista, separadores de 6 mm por colunas e linhas e os quatro
  afastadores independentes. A largura do afastador (60 mm) é a do mockup e fica numa constante só.
- **T017 `[X]`.** `portas.py`: `ABERTURA_GRAUS = 95.0`, dobradiça alternada com sentidos opostos, deslizante por
  `(comprimento + (n − 1) × sobreposição) / n`, `exclusividade` e `recuo_por_papel` (70 mm em divisórias, prateleiras,
  gavetas e internos com base por dentro; zero em laterais e bases).
- **T018 `[X]`.** `internos.py`: `Interno`, `TIPOS`, `ALTURA_BAIXA = 480`, `MALEIRO_ABAIXO_TOPO = 420`,
  `PASSO_DESEMPATE = 50`, `altura_inicial`, `faixa`, `inserir` (sempre dentro da faixa) e `resolver` idempotente
  (o último vence, o outro sobe 50 mm — premissa 🟡 isolada para correção sem tocar nas abas).
- **T019 `[X]`.** `resumo.py`: `linha_estado` com dimensões, montagem por extenso, vão, peça e conformidade em texto
  ("chapa: fora da chapa — …"), e `lista_de_pecas` com nome, comprimento, largura, espessura e `fora_da_chapa`,
  omitindo ferragem de papel vazio.
- **Suítes que saíram do skip:** as **sete**. `test_017_spec.py` (7 casos) saiu em T012; `test_017_vaos.py` (8) e
  `test_017_gavetas.py` (4)/`test_017_portas.py` (4)/`test_017_internos.py` (4) em T013/T016/T017/T018;
  `test_017_chapas.py` (5) em T014+T015; `test_017_resumo.py` (2) em T019. As duas mais lentas de liberar foram
  `chapas` e `resumo`, que dependem de mais de um módulo.
- **Verificação:** `python3 -m unittest discover -s tests -p 'test_017_*.py'` → **34 testes, 0 falhas, 0 skips**
  (antes `OK (skipped=34)`), exit 0; `ruff check caffmob_draw/armario_v2/` limpo; os oito módulos importados com
  `_bootstrap` sem carregar `bpy` (`'bpy' in sys.modules` → `False`); `tests/test_i18n_coverage.py` com os 3 testes OK
  (nenhum texto novo de UI nesta rodada). `check_api.py` não foi rodado: nenhum `bpy.props` foi tocado. Nada foi
  executado no Blender; os operadores e a geração real ficam para T020+ e a fumaça de T033.

### 2026-11-22, colisão de caminhos em T013 e T020

- **T013 corrigida (caminhos de vão).** O caminho era reservado na ordem da recursão, então um ramo podia roubar o
  nome do outro: com três colunas (`s0`, `s0.b`, `s0.b.b`) e uma divisória nova dentro de `s0.b`, o filho saía como
  `s0.b.b`, que já era a terceira coluna. Agora `_reservar_todos` reserva **todos** os caminhos irmãos antes de descer,
  colunas usam `.b` e faixas usam `.a`, e o filho que herda o caminho acumula o eixo já aplicado, em vez de reaplicar
  as divisões do pai (era o laço infinito da primeira tentativa). `regioes(dirisoes, spec)` passou a expor
  `{caminho: (x, z, largura, altura)}` em mm: **região** é a primeira medida (referencial das posições das
  divisórias, usada por `inserir_*` e `duplicar`) e **célula** é a última (o primeiro pedaço, onde o conteúdo do vão é
  colocado) — sem essa separação a gaveta de `s0` saía com a largura de antes da divisão.
- **Dois casos novos em `test_017_vaos.py`** (34 → 36): divisória e prateleira no mesmo vão produzem
  `s0`, `s0.a`, `s0.b` sem repetição, com a coluna da direita inteira; e uma vertical dentro de `s0.b` num plano de
  3 × 3 colunas não gera caminho repetido.
- **T020 `[X]`.** `caffmob_draw/armario_v2/build.py` criado em duas camadas: `pecas(spec, divisoes, gavetas, internos)`
  devolve as chapas em **milímetros** sem `bpy` (papel, componente do Padrão de Dimensões, nome, caixa, espessura,
  veio, fitas, `movel`, `curso`, eixo) e `gerar(root, spec, ...)` converte para metros em `MM = 0.001`, cria uma malha
  por chapa com `btm_armario_parte` preenchido, filha da raiz vazia na coleção `CAFFMob Armário v2`, e apaga as peças
  anteriores antes de refazer. `criar_raiz` e `colecao` montam a raiz e a coleção; `materiais(acabamento)` cria os
  quatro acabamentos e vidro/alumínio em materiais próprios (RF-17); `limpar` remove só as filhas com
  `btm_armario_parte`.
- Medidas conferidas no bpy simulado (não no Blender): armário 1000 × 2000 × 560 com as quatro chapas, fundo e uma
  divisória gera **9 peças** — laterais 15 × 560 × 2000, bases 970 × 560 × 15, fundo 970 × 6 × 1970, divisória
  15 × 560 × 1970, calceiro e duas frentes de gaveta com a largura da coluna (485 mm). Base passante em 1200 mm dá
  laterais de 1970 (as duas bases cobrem a largura) e as duas folhas deslizantes saem no material de vidro. Regerar
  mantém 9 filhas, sem duplicar.
- **Pendência de T020 fechada em 2026-11-22.** As chapas da caixa da gaveta passaram a sair de `gavetas.chapas`
  (`_caixa_da_gaveta`): separadores verticais nas divisas das colunas, horizontais nas das linhas, e os quatro
  afastadores no topo das faces, com a caixa recuando `FOLGA` de cada lateral e começando atrás da frente
  (`profundidade − espessura da frente`). As medidas de corte continuam vindo de `gavetas.chapas`; o `build.py` só
  posiciona. O smoke com `bpy` simulado mostrou **11 objetos** para caixa + 1 frente + 1 separador de 2 × 2 (1
  vertical, 1 horizontal) + 4 afastadores, e revelou um erro que o teste agora cobre: os separadores saíam com 15 mm
  (espessura da caixa) em vez dos **6 mm** que o `gavetas.chapas` devolve.
- **Teste puro de `build.pecas`.** `tests/test_017_build.py` acrescentado com 6 casos: caixa em lateral passante e em
  base passante, fundo encaixado e sobreposto, divisórias partindo do vão, frentes de gaveta empilhadas com a folga de
  3 mm (piso interno + 18 mm, 366,5 mm) e as chapas da caixa da gaveta entrando no plano, com o separador em 6 mm e
  nada à frente do armário. Para o teste ser puro, `build.py` passou a importar `bpy`, `bmesh` e `mathutils` **dentro**
  das funções que criam dados na cena — importar o módulo fora do Blender não carrega `bpy` (conferido).
- **Verificação:** `python3 -m unittest discover -s tests -p 'test_017_*.py'` → **42 testes, OK**; `ruff check` nos
  arquivos tocados limpo; `python3 docs/rag/tools/check_api.py` → *OK: no unknown API references found* (o verificador
  lia o `bmesh.md` do docstring como símbolo e acusava `[UNKNOWN in 5.2]`; o texto foi reescrito). **Nada executado no
  Blender:** `gerar` foi exercitado com `bpy`/`bmesh` simulados, o que pega erro de atributo e de conta, não de
  contexto nem de malha real. A fumaça de T033 continua sendo a prova de verdade.

### 2026-11-22, T021: operadores do construtor

- **T021 `[X]`.** `caffmob_draw/armario_v2/ops.py` criado com cinco operadores: `caffmob.cabinet_editor` (abrir, sem
  `UNDO`), `caffmob.armario_v2_gerar`, `caffmob.armario_v2_aplicar`, `caffmob.armario_v2_cancelar` e
  `caffmob.armario_v2_limpar` (os quatro com `{'REGISTER', 'UNDO'}`).
- **Gerar** lê o spec e as três coleções gravadas em `btm_armario`, confere o contrato com `chapas.pode_gerar`,
  valida com `spec.validate`, monta as `conferencia.Peca` pelas medidas de corte e só então chama `build.gerar`.
  Recusa sem contrato (RN-02) e, com `bloquear_chapa` ligado, recusa a peça que passa da chapa (RN-03); com o
  bloqueio desligado gera e devolve os avisos da conferência (RN-16).
- **Medidas de corte:** o cálculo saiu de `gerar` para `build.medidas_de_corte(item)`, usado tanto pelo `gerar`
  quanto pelo `conferencia.Peca` do operador — uma conta só, sem repetir o eixo fino.
- **Cancelar** aplica o `snapshot` JSON da abertura (`spec`, coleções, `gerado`, `aberto`) e refaz as peças a partir
  dele, ou apaga as peças se a abertura ainda não tinha gerado nada; espessura volta como o texto do enum (`"15"`),
  não `15.0`, que o `EnumProperty` rejeitaria. **Aplicar** só grava o passo (`bpy.ops.ed.undo_push`) e fixa o estado
  como novo ponto de retorno, sem fechar — fechar é do `panel.py` (T023).
- **`bl_idname` dividido com o editor 2D (D-03):** `caffmob.cabinet_editor` é o mesmo nome do editor antigo de
  propósito. Não há colisão porque `armario_v2` ainda não está na cascata (`_MODULES` só tem `props`) e, quando
  entrar (T030), o editor antigo já terá saído do registro (T027). A fumaça T033 confere o `unregister()` final.
- **Lacuna declarada (modelo de dados):** §2.1 grava da divisória só `eixo`, `vão`, `posição`, `tipo` e `espessura`.
  Os recuos do mockup não sobrevivem ao round-trip, então `ops.divisoes_do_armario` os devolve em zero; quando T023
  editar a divisória, a variante volta a propor o recuo. Registrado aqui em vez de inventar campo fora do delta.
- **Verificação:** `ruff check caffmob_draw/armario_v2/ tests/test_017_*.py` limpo; `check_api.py` → *OK: no unknown
  API references found*; `python3 -m unittest discover -s tests -p 'test_017_*.py'` → **42 testes, OK** (a refatoração
  de `medidas_de_corte` passou por eles); fumaça de `ops.py` com `bpy`/`bmesh`/`mathutils` simulados: abrir grava o
  instantâneo, Gerar cria 5 peças (4 papéis, duas laterais) e marca `gerado`, sem contrato recusa sem tocar na cena,
  Limpar apaga e baixa a flag, Cancelar devolve largura 1000 e espessura `"15"` e esvazia as divisórias, Aplicar
  empurra `"Armário: Aplicar"` no desfazer e regrava o instantâneo. **Nada executado no Blender** — a prova de
  contexto, painel e `undo_push` real continua em T033.

### 2026-11-22, T022: abrir e fechar animados

- **T022 `[X]`.** `caffmob_draw/armario_v2/anim.py` criado: timer de `INTERVALO = 0.016` s, `QUADROS = 18` por alvo e a
  matriz do estado **fechado** refeita a cada toque a partir do progresso atual, então inverter no meio do caminho não
  acumula erro. A suavização é a do anexo (`p²(3−2p)`) aplicada ao progresso, não ao passo.
- **O curso vem pronto do `build`.** `build.pecas` já grava `curso_mm` com os 72% da profundidade (frente e caixa da
  gaveta) e os 80% da própria largura (folha deslizante), e `eixo` diz o movimento (`Y`, `X` ou `GIRO`). A animação
  lê esses dois campos e não recalcula medida, então não há uma segunda conta de 72%/80% para divergir do corte.
- **Gaveta inteira, não só a frente.** O grupo do alvo junta as peças irmãs com o mesmo sufixo `" da gaveta N"` do
  nome (frente, separadores e afastadores andam juntos) mais os filhos do alvo. A corrediça 3D entra como irmã marcada
  pelo mesmo sufixo e com `papel` em `PAPEIS_GAIOLA`: aí o curso é multiplicado por `CURSO_GAIOLA = 0.5`. T029 precisa
  criar o conjunto com esse nome e no nível da raiz — se pendurar a corrediça na frente, ela anda com a frente a 100%.
- **Folha e porta com sentido oposto de propósito.** Folha usa o índice entre as irmãs `FOLHA` (par para a esquerda),
  igual ao `sentido` de `portas.folhas_deslizantes`; porta usa `porta_dobradica` do armário (`ALTERNADA` alterna por
  folha) e gira em torno da vertical na borda da dobradiça, no `y` da face da frente — o pivô é calculado uma vez no
  início e reaproveitado no segundo toque, porque a caixa já está girada.
- **Um passo de desfazer só no fim.** O operador `caffmob.armario_v2_alternar` (`BTM_OT_ArmarioV2Alternar`) tem
  `bl_options = {'REGISTER'}` e o `bpy.ops.ed.undo_push` roda no último quadro, com o rótulo de `Abrir`/`Fechar` já
  traduzido. Um `UNDO` no `execute` gravaria um passo vazio (a animação ainda não mexeu em nada) e o segundo toque no
  meio deixaria dois passos — o RF-16 pede um só, e nenhum quando o toque só inverte.
- **Handle em `_handles` (nome do alvo → função do timer), removido em todos os caminhos de saída:** fim dos 18 quadros
  (`_concluir`), alvo apagado no meio (`_descartar` dentro do quadro), novo toque no mesmo alvo (`cancelar` antes de
  registrar), `cancelar_tudo()` no `unregister()` e `load_post` (`@persistent`), porque o timer não é persistente e
  morreria com o dicionário ainda cheio.
- **Estado em `btm_armario.aberto`.** É o que o §2 do `data-delta` grava (um booleano no armário, não por peça), então
  o flag recebe o estado do último toque. O rótulo do menu não depende dele: `estado()`/`rotulo()` leem a geometria
  (peça deslocada ou girada = aberta), o que continua certo com várias gavetas no mesmo armário e depois de reabrir o
  arquivo. **Lacuna declarada:** sem estado por peça no modelo, o flag conta só o último alvo animado.
- **`_MODULES` passou a `('props', 'anim')`.** A cascata cresce conforme T004 previu; `ops` continua de fora por causa
  do `bl_idname` dividido (D-03) e entra em T030, depois de T027. Enquanto `armario_v2` não estiver na lista de
  submódulos da extensão (T030), nada disso é registrado de verdade.
- **Tradução fechada de pendência de T021.** O `tests/test_i18n_coverage.py` nunca tinha rodado em T021 e acusou 13
  textos de `ops.py` sem tradução, mais os 3 de `anim.py`. O `armario_v2.json` foi de 59 para **75 entradas** (os 16
  textos nas duas línguas); o teste voltou a `Ran 3 tests ... OK`.
- **Verificação:** `ruff check caffmob_draw/armario_v2/ tests/test_017_*.py` limpo; `check_api.py` → *OK: no unknown API
  references found* (o `#bpy.app.timers.register` num link do docstring era lido como símbolo, o texto foi trocado por
  "RAG do projeto, seção `bpy.app.timers`"); `python3 -m unittest discover -s tests -p 'test_017_*.py'` → **42 testes,
  OK**; `tests/test_i18n_coverage.py` → **3 testes, OK**. Fumaça de `anim.py` com `bpy`, `bpy.app.timers` e `mathutils`
  simulados: gaveta abre 0,3672 m com a gaiola em 0,1836 m, fecha de volta, segundo toque no sexto quadro inverte sem
  passo de desfazer, folhas correm ±0,32 m (sentidos opostos), porta gira 95° em torno da dobradiça e volta a zero,
  alvo apagado no meio descarta o timer, `unregister()` e `load_post` limpam o dicionário; e o `build.pecas` do mesmo
  cenário confirma os 72% e os 80% gravados. **Nada executado no Blender** — timer real, `undo_push` e malha girada
  continuam na fumaça de T033.

### 2026-11-22, T023: painel do construtor na vista 3D

- **T023 `[X]`.** `caffmob_draw/armario_v2/panel.py` criado com `BTM_PT_ArmarioV2` em `View3D > CAFFMob Draw`: as sete
  abas pelo `EnumProperty` `BTM_PG_ArmarioV2.aba` (que já existia desde T003), sub-abas de Divisões e Gavetas em
  `subaba_divisoes`/`subaba_gavetas` com `expand=True`, e o corpo do painel em `draw_painel(layout, context)` — fora da
  classe para a fumaça desenhar com um layout falso sem sessão do Blender.
- **Cabeçalho.** Tipo de montagem por extenso (via `resumo.MONTAGENS`), o vão da peça escolhida na coleção ativa e a
  chapa máxima do contrato. Com uma peça animável selecionada, o botão de Abrir/Fechar de `anim` entra no cabeçalho com
  `anim.rotulo(alvo)`, que já é o texto da ação oposta (RN-10).
- **Vão ativo por falta de campo.** O `§2` do `data-delta` não tem `vao_ativo`; `_vao_ativo` lê o `active_index` das três
  coleções e cai no vão raiz `s0` quando nada está escolhido. **Lacuna declarada**, sem inventar propriedade nova.
- **Janela vazia (RN-01).** Sem nenhuma das quatro chapas da caixa ligada, o painel mostra "Janela de armário vazia" e a
  orientação de ligar as chapas ou usar Montar Caixa; o estado vazio não cria peça nenhuma ao abrir.
- **Móvel da construção antiga (RN-23, RF-26).** `ops.e_construcao_antiga` sobe a hierarquia e reconhece
  `btm_cabinet`/`btm_structure` sem `btm_armario`. O painel desenha só o aviso: nenhum dos cinco comandos aparece, então
  Gerar e Aplicar ficam de fato desabilitados, e nada no móvel é lido ou alterado.
- **Contrato semeado do Padrão de Dimensões (D-11, RF-03).** `semear_contrato(scene)` lê `GLOBAL.max.max_length`,
  `GLOBAL.max.max_width` e a espessura de cada componente `COZ.sheets.<COMP>.thickness` pela API do Padrão (que devolve
  o padrão do esquema quando não há definição ativa), passa por `chapas.apply_host_contract` e encaixa a espessura no
  enum de 6/15/18/25 mm. Roda na primeira vez que o painel desenha com o contrato vazio; depois o usuário sobrescreve
  campo a campo. Sem isso, o armário nasceria sem contrato e o Gerar recusaria sempre.
- **Ações.** `Montar Caixa` (operador novo de `ops`, `caffmob.armario_v2_montar_caixa`), `Limpar`, `Gerar`, `Aplicar` e
  `Cancelar` são os operadores de T021; `Gerar` fica numa coluna desabilitada enquanto `chapas.pode_gerar` tiver motivo,
  com os motivos escritos abaixo do botão (RN-02).
- **Duas peças que faltavam em T021, agora em `ops.py`.** `Montar Caixa` não existia em nenhuma ação (RF-01 o exige) e
  entrou ao lado dos outros quatro, com a mesma base `_ArmarioOperator`; e `Abrir` passou a **criar o armário vazio**
  (`build.criar_raiz`) quando a cena não tem armário v2, porque sem isso o construtor não abria num projeto limpo
  (RF-01). Num móvel da construção antiga `Abrir` não cria nada e avisa (RN-23).
- **Inserção fora do escopo.** O mockup tem "+ Inserir Divisória/Prateleira/Matriz/Gavetas", mas nenhuma ação do plano
  cria esses operadores: o painel edita as coleções gravadas campo a campo e quem insere é o Duplicar do menu (T024) e
  a inserção múltipla do HUD (T025). Registrado como lacuna do plano, sem inventar operador.
- **`_MODULES` passou a `('props', 'anim', 'panel')`.** O painel depende dos operadores de `ops`, que só entram na
  cascata em T030 (depois de T027 tirar o editor antigo do registro), então **T030 precisa inserir `'ops'` antes de
  `'panel'`**; até lá os botões do painel existem mas os `bl_idname` de `ops` não estão registrados.
- **Tradução:** 10 textos novos no `armario_v2.json` (75 → **85 entradas**), incluindo a dica do operador Montar Caixa.
- **Verificação:** `ruff check caffmob_draw/armario_v2/` limpo; `check_api.py` → *OK: no unknown API references found*;
  `test_i18n_coverage.py` → **3 testes, OK**; `test_017_*.py` → **42 testes, OK**. Fumaça de `panel.py` com `bpy`,
  `mathutils`, o `Padrão de Dimensões` e um layout falso: contrato semeado com 2750 × 1830, fundo "6" e o resto "15";
  cabeçalho com montagem, vão e chapa máxima; janela vazia com os cinco comandos e sem Abrir/Fechar; as sete abas com o
  conteúdo próprio; sub-abas filtrando Vertical/Múltipla e Internas/Externas; Abrir/Fechar no cabeçalho com o rótulo
  oposto ao estado; Gerar desabilitado sem chapa máxima e habilitado com o contrato completo; Montar Caixa ligando as
  quatro chapas e o fundo e chamando o `gerar`; `Abrir` criando a raiz na cena vazia e recusando no móvel antigo, que
  mostra só o aviso e nenhum comando. **Nada executado no Blender** — painel real, ícones e o desenho da sidebar
  continuam na fumaça de T033.

### 2026-11-22, correção de T023 e T024: menu de contexto

- **T023 corrigido: o desenho do painel não escreve mais nada.** `semear_contrato` saiu de `panel.py` para `ops.py` e
  deixou de ser chamada em `draw_painel`; agora roda no **`Abrir`** (antes de gravar o instantâneo) e no botão
  `Semear do Padrão de Dimensões`, que aparece na aba Estrutura só enquanto `configurado` é falso. O `draw` ficou só
  leitura: desenhar painel não altera a cena.
- **Cascata resolvida: `_MODULES = ('props', 'anim', 'ops', 'panel', 'menu')`.** O painel dependia dos operadores de
  `ops`, que estava fora da cascata por causa do `bl_idname` dividido (D-03). Em vez de deixar o painel com botões
  mortos, `ops.register` ganhou a guarda `_dividido`: enquanto o editor 2D antigo ainda responder por
  `caffmob.cabinet_editor`, a classe `Abrir` do armário espera a vez e as outras seis entram normalmente; quando T027
  tirar o editor antigo do registro, a guarda deixa de casar e o `Abrir` entra sozinho. `unregister()` continua
  simétrico, porque só desfaz o que está `is_registered`.
- **T024 `[X]`.** `caffmob_draw/armario_v2/menu.py` criado com um gancho em `VIEW3D_MT_object_context_menu` por
  `_append`/`_remove` (D-06), removido no `unregister()`. O menu só desenha quando o objeto ativo sobe a hierarquia até
  um objeto com `btm_armario` — sem armário v2, nem separador aparece (RN-23).
- **Abrir/Fechar** entra na gaveta, na folha deslizante e na porta pelo `anim.animavel`, com o texto de
  `anim.rotulo` (sempre a ação oposta) e o ícone acompanhando o estado; o operador é o de `anim`, então o menu só
  escolhe rótulo e ícone (RN-10, RF-16).
- **Duplicar e Excluir** entram só em divisória e prateleira, decidido por `divisao_da_peca`. A peça de cena não guarda
  o `uid` da divisão que a gerou: o índice do `btm_armario_parte.uid` é aplicado sobre a lista de `build.pecas` e a
  posição entre as peças de divisão dá a entrada da coleção — prateleira de interno cai em `posicao >= len(divisoes)` e
  fica sem os dois itens. Duplicar usa `vaos.duplicar` (meio do maior vão livre, mínimo de 80 mm de cada lado) e
  Excluir usa `vaos.remover`; as duas regravam a coleção com `ops.gravar_divisoes` (espessura de volta como texto do
  enum) e refazem as peças quando o armário estava gerado. Se a geração recusar, `_regerar` devolve a coleção anterior e
  o operador avisa, sem deixar o armário pela metade.
- **Tradução:** seis textos novos e dois reaproveitados (`Duplicar` e `Excluir` já estavam em `geral.json`), catálogo de
  85 para **91 entradas**.
- **Verificação:** `ruff check caffmob_draw/armario_v2/` limpo; `check_api.py` → *OK: no unknown API references found*;
  `test_i18n_coverage.py` → **3 testes, OK**; `test_017_*.py` → **42 testes, OK**. Fumaça com `bpy`/`mathutils`/layout
  falsos: o `draw` deixa o contrato vazio e mostra o botão de semear; `semear_contrato` escreve 2750 × 1830 com fundo
  "6" e não reescreve na segunda chamada; `Abrir` semeia o contrato e grava o instantâneo; o botão recusa sem o grupo
  na cena; `ops.register()` pula só o `Abrir` com o editor antigo presente e registra todos sem ele; menu anexado e
  removido; gaveta com só Abrir/Fechar e rótulo `Abrir`; divisória com Duplicar/Excluir e `divisao_da_peca` achando
  `d1`; prateleira de interno e objeto sem armário sem item nenhum; Duplicar somando a divisão com espessura em texto,
  Excluir devolvendo a uma, e Duplicar recusado em armário estreito sem mexer na coleção. **Nada no Blender** — menu
  real, empilhamento do `VIEW3D_MT_object_context_menu` e geração de malha continuam em T033.

### 2026-11-22, T025: HUD da vista 3D

- **T025 `[X]`.** `caffmob_draw/armario_v2/hud.py` criado com um handler `POST_PIXEL` em `SpaceView3D` que desenha três
  coisas sobre a vista, sempre em leitura: alternadores da estrutura, cartão do inspetor e realce da seleção. `canvas2d`
  para as primitivas e `hb_gpu_draw.point_in_rect` para o teste do clique, como o plano pediu; o handler e o item de
  keymap são removidos no `unregister()`.
- **Alternadores da estrutura.** Cinco botões no canto inferior esquerdo — lateral esquerda, lateral direita, base
  inferior, base superior e fundo — que aparecem só enquanto o armário está vazio, ou seja, com nenhuma das quatro
  chapas da caixa ligada (RN-01, D-18). Os layouts saem de `botoes_da_estrutura(armario, largura_px)`, que devolve
  `(campo, rótulo, retângulo)` em pixels e é a única fonte de verdade do desenho e do clique, e o botão aceso usa a cor
  primária do `canvas2d`.
- **Clique sem modal.** O operador `caffmob.armario_v2_hud_alternar` é ligado a `LEFTMOUSE`/`PRESS` da keymap `3D View`
  (`any=True`, `head=True`, como `library_panel/ops_click.py`), com `poll` restrito a vista 3D, armário v2 na cena e
  caixa vazia. `invoke` acha o campo com `campo_no_ponto`; fora dos botões devolve `PASS_THROUGH`, então seleção, box
  select e menu de contexto continuam chegando na cena. Nada de operador modal — abrir o HUD não desliga o autosave.
- **Inspetor da peça escolhida.** Cartão acima dos alternadores com nome da peça, comprimento × largura × espessura em
  mm, papel por extenso (`ROTULOS`) e, quando a peça passa da chapa do contrato, o aviso `Fora da chapa` na cor de
  alerta. As medidas vêm de `btm_armario_parte` e a conferência é a `conferencia.conferir` do núcleo puro, sem
  recalcular peça nenhuma (RF-19). Sem peça escolhida o cartão não aparece.
- **Realce da seleção.** Doze arestas do volume da peça escolhida, projetadas com
  `view3d_utils.location_3d_to_region_2d` e desenhadas em laranja; se algum canto cai fora da vista, nada é desenhado.
- **Tradução:** sete textos de papel por extenso e dois do operador, em `armario_v2.json` (91 → **100 entradas**).
- **Verificação:** `ruff check caffmob_draw/armario_v2/` limpo; `check_api.py` → *OK: no unknown API references found*;
  `test_i18n_coverage.py` → **3 testes, OK**; `test_017_*.py` → **42 testes, OK**. Fumaça com `bpy`, `mathutils`,
  `canvas2d`, `hb_gpu_draw` e a região falsos: armário vazio reconhecido; cinco alternadores em duas colunas a partir da
  margem, sem estouro da região e sem nada em região estreita; `campo_no_ponto` achando o campo em cada botão e
  devolvendo `None` fora; alternadores sumindo com uma chapa ligada; inspetor com nome, medidas e papel, aviso
  `Fora da chapa` só com contrato configurado e peça grande; cartão acima dos botões e encostando na margem sem eles;
  `desenhar_hud` desenhando cinco botões e o cartão sem escrever no armário, com as 24 pontas do realce; peça sem
  escolha sem realce e sem cartão; clique ligando a lateral, pedindo redesenho, passando direto fora dos botões e
  recusado sem mouse; `register()` pendurando um handler e um item de keymap sem duplicar na segunda chamada, e
  `unregister()` limpando os dois. **Nada executado no Blender** — HUD real, keymap na vista, projeção do realce e a
  convivência com o menu de contexto ficam para a fumaça de T033.

### 2026-11-22, T026: ponte dos módulos de biblioteca

- **T026 `[X]`.** `caffmob_draw/armario_v2/ponte.py` criado: o módulo de biblioteca (frameless, face frame, closets e
  os CAFFMob) vira um `spec.Spec` em milímetros e o motor novo desenha as peças pelo mesmo cálculo (RN-21, RF-24).
- **Leitura.** `modulo_da_selecao` sobe a hierarquia com `classify.module_root` e recusa quem já tem `btm_armario`;
  `medidas_do_modulo` usa `editing.get_dimension` (metros) e devolve `None` quando falta qualquer uma das três;
  `espessuras_do_modulo` parte de `btm_cabinet.thickness`, aplica `thickness_*` e depois as sobrescritas da estrutura,
  encaixando tudo nos itens do enum (6, 15, 18 e 25 mm); `presenca_do_modulo` lê `has_*` e, nas bibliotecas sem
  `btm_cabinet`, assume a caixa inteira; as portas saem de `door_swing` (NONE/LEFT/RIGHT/DOUBLE/FLIP) e as divisões de
  `scene_divisions.read`, convertidas para `vaos.Divisao` em milímetros com o mesmo caminho de vão (`s0`, `s0.b`…).
- **Sem correspondência completa não falha.** `ler_modulo` devolve `(spec, divisões, avisos)`: módulo sem medidas abre a
  aba vazia com o aviso; divisão fora do vão raiz fica de fora com aviso (a árvore do motor novo nasce de um vão só);
  prateleiras das bibliotecas antigas não são convertidas e o aviso pede que sejam refeitas na aba Divisões.
- **Gerar pelo motor novo** (`caffmob.armario_v2_gerar_do_modulo`, `UNDO`). Cria ou reaproveita o armário v2 daquele
  módulo (procura `btm_armario.origem`), grava o spec (espessura como texto do enum), regrava as divisões com
  `ops.gravar_divisoes`, semeia o contrato e chama `ops.gerar_armario`. Só quando a geração passa é que o módulo e as
  malhas filhas são ocultados e marcados com `btm_cut_exclude` — as duas marcas que `cutting/part_sources` já respeita —
  e os nomes marcados ficam em `btm_armario_marcados` na raiz.
- **Recriar do módulo** (`caffmob.armario_v2_recriar_do_modulo`, `UNDO`). Devolve a visibilidade e limpa as marcas
  exatamente dos objetos gravados, apaga as peças e a raiz do armário v2 que saiu do módulo. A reversão só apaga o que
  a conversão criou; o módulo da biblioteca não é tocado além das marcas que ela mesma pôs.
- **Painel.** `movel_antigo` deixa de tratar módulo de biblioteca como móvel antigo (RN-21) e `draw_painel` mostra a
  aba do módulo (`ponte.desenhar_modulo`): biblioteca, nome, medidas, montagem, os avisos e o botão de Gerar. No armário
  vindo de módulo, as ações ganham `Recriar do módulo`.
- **Tradução:** 12 textos novos (avisos, aba do módulo, rótulos e dicas dos dois operadores), catálogo de 100 para
  **112 entradas**.
- **Verificação:** `ruff check caffmob_draw/armario_v2/` limpo; `check_api.py` → *OK: no unknown API references found*;
  `test_i18n_coverage.py` → **3 testes, OK**; `test_017_*.py` → **42 testes, OK**. Fumaça com `bpy`, `mathutils`,
  `cabinet_editor` e `selection` falsos: módulo reconhecido na seleção e o armário v2 recusado como módulo; medidas em
  mm e módulo sem profundidade sem medidas; espessura do cabinet em 18 mm e fundo sobrescrito pela estrutura em 6 mm;
  presença das cinco chapas e caixa inteira nas bibliotecas sem `btm_cabinet`; duas divisões do vão raiz convertidas
  (com tipo, espessura de papel e recuo de frente) e a de `s1` fora com aviso; spec com montagem base passante e porta
  dupla em duas folhas; prateleiras avisadas; aba do módulo com biblioteca, medidas e o botão de Gerar; Gerar criando a
  raiz, gravando spec, divisões e origem, semeando o contrato, ocultando e marcando módulo e malhas e guardando os nomes
  para a reversão, com o instantâneo no fim; geração recusada mantendo o módulo visível e avisando; Recriar devolvendo
  visibilidade e marcas, apagando a raiz e avisando quando o módulo sumiu; `movel_antigo` inalterado para o móvel da
  construção antiga; os dois operadores disponíveis, terminando e registrando/desregistrando. **Nada executado no
  Blender** — módulo real de cada biblioteca, malha gerada pelo motor novo e o corte sem duplicar peça ficam para T033.

### 2026-11-22, correção do painel (T026) e T027: interface do editor 2D fora do registro

- **Correção do painel (T026).** Com um módulo de biblioteca selecionado, a aba do módulo sumia quando havia qualquer
  outro armário v2 na cena: `draw_painel` chamava `raiz_da_cena` primeiro, e essa função cai para o primeiro armário da
  coleção quando a seleção não é um armário. A seleção passou a vencer o recuo: `raiz_da_selecao(context)` devolve só o
  armário v2 da hierarquia da seleção e, se ele não existir e houver módulo escolhido, `ponte.desenhar_modulo` desenha
  a aba do módulo antes de qualquer recuo para a coleção. O `poll` do painel também passou a aceitar módulo de
  biblioteca — antes, num arquivo só com módulos, o painel inteiro ficava invisível.
- **Fumaça com o caso novo:** quatro casos com `bpy`, `selection` e `cabinet_editor` falsos. **(1)** módulo selecionado
  **e** outro armário v2 na coleção — a aba do módulo aparece e o cabeçalho do outro armário não é desenhado (o caso
  que falhava); **(2)** módulo selecionado sem armário v2 na cena — `poll` verdadeiro e aba do módulo; **(3)** sem
  seleção de peça e com armário na coleção — o recuo para a coleção continua valendo; **(4)** móvel da construção
  antiga sem armário v2 — só o aviso, sem aba de armário. `OK: fumaça do painel 017 sem falhas (4 casos, incluindo
  módulo selecionado com armário v2 na cena)`.
- **T027 `[X]`.** `_modules()` de `caffmob_draw/cabinet_editor/__init__.py` passou a devolver
  `(data_props, previews, gallery, reflow_handler)`. Saíram do registro `window`, `ops_editor`, `ops_actions`,
  `panels`, `panels_structure`, `panels_divisions`, `panels_drawers`, `panels_interior`, `panels_doors`,
  `panels_sliding`, `panels_backs` e `props`; com `props` sai também o `WindowManager.btm_cabinet_editor`.
- **O que continua vivo.** `data_props` mantém `btm_structure`, `btm_division` e `btm_extra` nos objetos — é o que
  `structure_inputs`, `cutting/part_extractor`, `customize/reapply` e `library_panel` leem. `previews` registra só o
  ciclo de vida das miniaturas (nada pendurado em `register`). `gallery` continua registrado por causa de
  `library_panel/ops_cabinet.py:46-47` (A002). `reflow_handler` continua com os dois handlers, e o guarda
  `props.session() is not None` segue funcionando sem a propriedade do `WindowManager`, porque a sessão mora em
  `props._session` e só o modal removido a iniciava — na prática os handlers ficam inertes.
- **Núcleos puros intactos.** `structure`, `structures_core`, `divisions`, `structure_inputs`, `elevation`, `validate`,
  `state`, `bays`, `catalog`, `extras`, `slides`, `appliances`, `position`, `bridge`, `scene_*` e `gallery_core`
  continuam importáveis e sem `register()`, então `geometry/mesh_gen.py`, `customize/*`, `standards/*`,
  `cutting/*`, `drawers/gaveteiro.py` e `armario_v2/ponte.py` seguem importando por eles.
- **Guarda do `bl_idname` dividido (D-03).** Com `ops_editor` fora do registro, nada responde por
  `caffmob.cabinet_editor`; `ops._dividido` deixa de casar e o `Abrir` do armário v2 registra na primeira vez que
  `armario_v2.ops` entrar na cascata (T030). A guarda ficou como está: some sozinha, como previsto.
- **Verificação:** `ruff check caffmob_draw/armario_v2/ caffmob_draw/cabinet_editor/__init__.py` → *All checks passed*;
  `py_compile` dos dois arquivos → OK; `check_api.py` → *OK: no unknown API references found* (599 arquivos);
  `test_017_*.py` → **42 testes, OK**. **Nada executado no Blender:** o registro real da cascata, a ausência de
  `WindowManager.btm_cabinet_editor` e o `Abrir` do armário v2 assumindo o `bl_idname` só se comprovam na fumaça de
  T033, depois de T030 registrar o pacote.

### 2026-11-22, T028: o modal do editor 2D sai das listas de modais gerenciados

- **T028 `[X]`.** `collision/guard.py` e `stick/settle.py` deixaram de citar `caffmob.cabinet_editor_modal`: `_MANAGED`
  ficou só com `caffmob.move_over_dialog` e `_MOVE_IDS` com os seis modais restantes (`stick_move`, `stick_to_face`,
  `aggregate_move`, `move_on_wall`, `move_over_drag`, `move_over_dialog`). Só as duas linhas de conjunto mudaram — o
  resto dos dois arquivos (docstrings, índices, varreduras, ímã e migração) ficou intacto, como a ação pede.
- **Por que a remoção é segura.** Desde T027 `ops_editor` saiu do registro de `cabinet_editor`, então nada responde
  por `caffmob.cabinet_editor_modal`; as duas listas eram as últimas referências ao operador fora do próprio
  `cabinet_editor/` (que continua no pacote, mas sem registro). Com o modal fora, o guarda de colisão volta a corrigir
  qualquer translação direta que aconteça com o operador inativo e o assentar não espera mais por ele.
- **Efeito no legado:** nenhum. As duas listas só classificam operador em andamento; não há propriedade, handler ou
  adaptador alterado, e a ausência de um nome que nunca casa é inerte. `grep` em `collision/` e `stick/` não acha mais
  `cabinet_editor_modal`.
- **Verificação:** `ruff check caffmob_draw/collision/guard.py caffmob_draw/stick/settle.py` → *All checks passed*;
  `py_compile` dos dois → OK; `check_api.py` → *OK: no unknown API references found* (599 arquivos); `test_017_*.py` →
  **42 testes, OK**. **Nada executado no Blender:** o guarda e o assentar reais só se comprovam nas fumaças de T033/T034.

### 2026-11-22, T029: adaptador do armário v2 no corte

- **T029 `[X]`.** `part_sources.armario_v2_records(scene)` criado: varre `scene.objects` em ordem de nome, aceita só
  `MESH` com `btm_armario_parte`, visível (`_visible`, como os outros adaptadores) e sem `btm_cut_exclude`, e devolve um
  `PartRecord` por chapa com `source="ARMARIO_V2"`. Sai da lista a malha com `papel` vazio (ferragem: trilho, gaiola),
  que é o que evita a peça duplicada de ferragem (RN-19), e a que não tem comprimento ou largura positiva.
- **Nada é recalculado.** Medidas, componente, papel, veio, fitas e `uid` vêm do que o `build.gerar` gravou
  (`comprimento_mm`, `largura_mm`, `espessura_mm`, `componente`, `veio`, `fita_*`, `uid = <uid do armário>/<papel>/<índice>`).
  O móvel é a raiz encontrada subindo `parent` até o objeto com `btm_armario`: `module_uid` = `btm_uid` da raiz quando
  existe, senão o nome dela; `module_name` = nome da raiz.
- **Material mapeado, não copiado.** `BTM_PG_ArmarioParte.material` guarda a chave do acabamento (`CHAPA`, `VIDRO`,
  `ALUMINIO`), não o nome da matéria-prima. O adaptador traduz por `ARMARIO_V2_MATERIALS`: a chapa comum vira vazio
  (vale o padrão do componente, como o `data-delta` §3 manda) e vidro/alumínio viajam com o próprio nome.
- **Linha vazia, consequência declarada.** O armário v2 não guarda linha do Padrão de Dimensões, então `line=""`,
  igual a `FREE_GEOMETRY`, `STAIRS`, `DRAWERS` e `PROMOB`: sem fita do Padrão e sem `limit_status` calculado por
  componente. A conformidade de chapa do armário continua sendo a do contrato próprio, no HUD e no resumo
  (`conferencia.conferir`). Inventar uma linha (`COZ`) foi descartado: seria supor a linha do projeto.
- **`extract_production_parts` somou o adaptador depois das gavetas** (uma linha, antes de Promob). A lista continua
  ordenada por `module_uid`/`uid`, então as peças do armário caem juntas sob a raiz.
- **`json_exporter.SOURCES` ganhou `"ARMARIO_V2"`.** Não estava no texto da ação, mas `write_global_json` valida o
  próprio payload e recusaria qualquer plano de corte com a fonte nova (o JSON global é o formato de entrega do
  plano). O `SCHEMA_VERSION` ficou em `2.5.0` de propósito: quatro fumas e o `test_production_contracts` fixam a
  versão, e mexer nisso é decisão de contrato (T031/T034), não desta ação.
- **Verificação:** `ruff check` nos três arquivos → *All checks passed*; `python3 docs/rag/tools/check_api.py` →
  *OK: no unknown API references found* (599 arquivos); `test_017_*.py` → **42 testes, OK**. Fumaça com `bpy`,
  `bmesh`, `mathutils` e cena falsas: raiz + lateral + base + folha de vidro + trilho (`papel` vazio) + peça oculta +
  peça com `btm_cut_exclude` + malha sem `btm_armario_parte` → **3 registros**, todos `ARMARIO_V2`, com `module_uid`
  da raiz, componente/medidas/veio/fitas do PropertyGroup, `uid` do `build`, `line` vazia, lateral em `MDF` (padrão) e
  folha em `VIDRO`; `extract_production_parts` devolveu os mesmos 3 `NestingPart` e o `build_global_payload` +
  `validate_global_json` aceitaram o `source` novo. **Nada executado no Blender:** malha real, `hide_viewport` de
  hierarquia e o plano de corte desenhado ficam para a fumaça de T033 e para o `tests/test_017_corte.py` de T035, que
  ainda não existe (nenhum teste versionado cobre este adaptador).

### 2026-11-22, revisão de T029 e T030: armário v2 na cascata da extensão

- **Revisão de T029 com olhos novos.** Uma falha real: esconder o armário é esconder a raiz vazia (olho no `Armário
  v2`), e aí as malhas filhas continuam com `hide_viewport`/`hide_get` falsos — o adaptador listaria as chapas de um
  móvel que o usuário acabou de esconder. Entrou a guarda `if raiz is not None and not _visible(raiz): continue`,
  mantendo o teste de visibilidade por peça que já existia. O docstring ficou preciso: a linha vazia faz a fita do
  Padrão ficar de fora e desliga o limite de chapa do Padrão (antes dava a entender que o adaptador não lia as fitas —
  ele lê, e elas só não viram espessura de fita sem linha).
- **O que a revisão confirmou de bom.** Nenhum `bpy` tocado, tudo lido por atributo; `source="ARMARIO_V2"`; `uid` do
  `build` preservado; ferragem (`papel` vazio) fora; `btm_cut_exclude` respeitado; nada recalculado a partir do spec;
  `line=""` coerente com `FREE_GEOMETRY`/`STAIRS`/`DRAWERS`/`PROMOB`; `ARMARIO_V2` em `json_exporter.SOURCES` sem
  mexer no `SCHEMA_VERSION`.
- **Lacunas que ficam registradas, sem mudança de código.** `_visible` não propaga hierarquia nos adaptadores antigos
  (um módulo oculto ainda lista as filhas pelo caminho CUTPART) — é o mesmo tipo de buraco do achado A001 e mora em
  `iter_modules`/`_cutpart_found`, fora do escopo de T029/T030. E o contrato `json-global-v2.md:57`
  (`_reversa_forward/001-.../interfaces/`) ainda lista só `CUTPART`/`SYNTHETIC`/`FREE_GEOMETRY`; já estava
  desatualizado para STAIRS/DRAWERS/PROMOB desde a 2.4/2.5, então a fonte nova não piorou nada — fica para o
  `/reversa-sync` ou para T034, não para esta ação.
- **T030 `[X]`.** `caffmob_draw/__init__.py`: `"armario_v2"` entrou em `_submodule_names` (hot-reload, entre `customize`
  e `aggregates`), o import explícito entrou logo depois de `from . import cabinet_editor`, `armario_v2.register()`
  ficou **depois de `customize.register()` e antes de `cabinet_editor.register()`**, e `armario_v2.unregister()`
  imediatamente **antes de `cabinet_editor.unregister()`**, como a ação pede. Não é o inverso exato da ordem de
  registro: as duas cascatas são independentes e o texto da ação manda a posição do desregistro.
- **`ops` antes de `panel` já estava feito.** `_MODULES` ficou `('props', 'anim', 'ops', 'panel', 'menu', 'hud', 'ponte')`
  na correção de T023; esta ação conferiu a ordem e **não** mexeu na tupla. `ponte` fica por último porque depende dos
  operadores de `ops` e do painel para desenhar a aba do módulo.
- **Risco aberto para T033.** `Abrir` só se registra se a guarda `_dividido` de `ops.register` não casar — ela checa
  `hasattr(bpy.ops.caffmob, 'cabinet_editor')`, e no Blender real a existência desse atributo para um operador não
  registrado não é garantida nem óbvia. Se a guarda casar errado, o armário sobe sem o `Abrir`; a fumaça de T033 é
  quem prova isso, e o teste tem que abrir o construtor depois do `register()` completo.
- **Verificação:** `ruff check caffmob_draw/__init__.py` e os três arquivos do corte → *All checks passed*;
  `check_api.py` → *OK: no unknown API references found* (599 arquivos); `test_017_*.py` → **42 testes, OK**;
  `test_i18n_coverage.py` → **3 testes, OK**. Fumaça do adaptador com `bpy`/`bmesh`/`mathutils` e cena falsas: armário
  visível lista 1 peça, armário oculto lista 0, peça oculta dentro de armário visível continua fora. Conferência
  estrutural do `__init__` por AST: `register` = `customize`, `armario_v2`, `aggregates`, `stick`, `collision`,
  `cabinet_editor`; `unregister` = `object_library`, `armario_v2`, `cabinet_editor`, `collision`; `"armario_v2"` no
  hot-reload e no import. **Nada executado no Blender:** registro real, handlers, menu, HUD e `unregister()` completo
  continuam na fumaça de T033.

### 2026-11-22, T033: fumaça headless do armário v2 (e sete defeitos reais)

- **T033 `[X]`.** `tests/blender_017_armario_smoke.py` criado e rodado **no Blender 5.2 de verdade**:
  `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_017_armario_smoke.py`
  → `blender_017_armario_smoke: OK`, exit 0. O roteiro é síncrono (nada de laço de eventos em `--background`); a
  animação é dirigida à mão pelos quadros do timer, com `is_registered` conferido antes.
- **Cobre:** registro real (`Abrir` no `caffmob.cabinet_editor`, operadores, painel, menu, HUD, propriedades, contrato,
  editor 2D fora); abrir em projeto limpo cria o armário vazio e semeia o contrato; Montar Caixa gera as quatro chapas
  e o fundo; sem contrato recusa; chapa de 3000 bloqueia e, sem bloqueio, gera com aviso (base de 2970 mm em chapa de
  2730); bloco de gavetas com frente e separador de 6 mm, corte sem ferragem e sem o OBJ da corrediça; deslizante por
  dentro recuando prateleira e frente de gaveta em 70 mm com a lateral inteira; Abrir/Fechar com timer, 367,2 mm de
  curso (72% de 510), estado gravado e segundo toque voltando; Cancelar devolvendo o instantâneo da abertura; módulo de
  biblioteca convertido sem duplicar no corte e Recriar devolvendo; módulo `btm` convertido saindo do corte (7 → 0
  peças) e voltando no Recriar; móvel sem armário recusado e intocado; `unregister()` sem exceção e sem propriedade,
  operador, painel, HUD, timer ou contrato pendurado.
- **Sete defeitos reais, todos corrigidos porque a fumaça não passava sem eles:**
  1. `ops._dividido` usava `hasattr(bpy.ops.caffmob, 'cabinet_editor')`, que é **sempre verdadeiro** — o `Abrir` nunca
     se registrava e o construtor não existia. Agora procura uma classe de operador registrada com aquele `bl_idname`.
  2. `Abrir` herdava o `poll` que exige a raiz na seleção — e é ele quem cria a raiz num projeto limpo. Ganhou `poll`
     próprio, que recusa só o móvel de módulo/construção antiga.
  3. `semear_contrato` lia `GLOBAL.max.max_length`/`max_width`, chaves que **não existem** no esquema (as medidas da
     chapa são `GLOBAL.max.sheet_length_max`/`sheet_width_max`, 1810 e 2730 por padrão). Passa maior com maior.
  4. **A busca de raiz estava errada em todo o pacote:** o `PointerProperty` `btm_armario` existe em *todo* `Object`,
     então `getattr(obj, 'btm_armario', None) is not None` parava na própria peça. O `aberto` ia para a frente da
     gaveta, o menu de contexto nunca aparecia e o `Gerar pelo motor novo` recusava **todo** módulo
     (`ponte.modulo_da_selecao`). Critério único em `build.e_raiz`/`build.raiz_de` (vazio da coleção do construtor),
     usado por `ops`, `anim`, `menu`, `panel` e `ponte`; no corte, `_armario_root` exige o vazio.
  5. `e_construcao_antiga` testava `btm_cabinet`/`btm_structure`, grupos que também existem em todo objeto, e nunca
     reconhecia o móvel antigo. Agora usa as marcas de módulo (`caffmob_modulo`, tags das bibliotecas e
     `btm_plane.object_kind == 'MODULE'`), as mesmas do corte.
  6. **RN-06 não estava ligada:** `build.pecas` nunca chamava `portas.recuo_por_papel`. Agora divisórias, prateleiras,
     internos e gavetas recuam e encurtam a profundidade do trilho quando a deslizante é por dentro.
  7. T035, abaixo.
- **Limites declarados.** O Blender não expõe as funções anexadas a um menu (ficam no C e `remove` não reclama quando
  falta), então o menu é conferido pelo que `desenhar_menu` desenha com um layout falso e pelas classes depois do
  `unregister`. O OBJ da corrediça continua **não instanciado** pelo motor (RN-08 só tem o arquivo empacotado): a
  fumaça prova que a gaveta gera e que a ferragem não entra no corte, não que a corrediça apareça na cena.
  `panel._peca_escolhida` e `hud._peca` ainda aceitam qualquer objeto como peça (mesma família do `btm_armario`
  sempre presente); não apareceu no caminho da fumaça e fica registrado para o polimento.
- **Verificação:** `ruff check` nos arquivos tocados limpo; `check_api.py` → *OK: no unknown API references*;
  `test_017_*.py` → **48 testes, OK**; `test_i18n_coverage.py` → **3 testes, OK**; fumaça no Blender 5.2 → **OK**.
  `ruff check caffmob_draw/` inteiro acusa **21 erros preexistentes** fora desta feature (`caffmob/v2`, `library_panel`,
  `mobi`, `stairs`, `walls2d`, `ui`, `target`, `texture_library`), nenhum em arquivo da 017 — fica para T034 decidir.
- **Não conferido:** o desenho real do painel, do menu e do HUD numa janela (exige Blender com interface, fora do
  escopo headless da T033).

### 2026-11-22, T035: o módulo convertido sai do corte na origem

- **T035 `[X]`.** `part_sources.iter_modules` passou a ignorar módulo oculto ou com `btm_cut_exclude` **antes** de
  classificá-lo, como D-17 pede: o caminho sintético não consulta a marca, e o módulo `btm` convertido continuava
  emitindo as chapas dele ao lado das peças reais do armário v2. Filtrar na origem vale também para `module_entries`
  (o `modules[]` do JSON v2) e para todos os adaptadores que passam por `iter_modules`.
- **`tests/test_017_corte.py`** (unittest puro, 6 casos): conta as peças antes e depois da conversão, imitando a
  composição de `extract_production_parts` para as duas fontes do caso. Antes: módulo visível emite as sintéticas **e**
  as duas peças do armário v2 (o móvel aparece duas vezes, com medidas diferentes — o defeito do A001). Depois de
  ocultar e marcar: só as duas peças do armário. Cobre ainda ocultar sem marcar, marcar sem ocultar e módulo de
  biblioteca vivo seguindo no corte. O `bpy` mínimo é injetado só para a importação de `part_sources` (que puxa
  `compat`) e removido em seguida; nenhuma função exercitada usa `bpy`.
- **Prova no Blender também:** a fumaça de T033 ganhou o caso do módulo `btm` — `Gerar pelo motor novo`, corte de
  **7 → 0** peças do módulo e Recriar devolvendo as 7.
- **Verificação:** `ruff check` limpo; `test_017_corte.py` → **6 testes, OK**; `test_017_*.py` → **48 testes, OK**;
  fumaça `blender_017_armario_smoke.py` → **OK** (exit 0).

### 2026-11-22, T034: verificação fechada, com duas decisões (ruff do legado e fumaças com janela)

- **Inspeção da peça escolhida (pendência da T033).** `panel._peca_escolhida` e `hud._peca` aceitavam **qualquer**
  objeto como peça: testavam `btm_armario_parte is not None`, e o grupo existe em todo `Object` (vazio por padrão).
  Agora há um critério só, `panel.peca_da_selecao`: papel gravado **e** raiz v2 acima (`build.raiz_de`); `_peca_escolhida`
  devolve o nome e o HUD passou a chamar a função do painel em vez de repetir a checagem. Provado na fumaça de T033:
  raiz do armário → `''`, chapa solta com `papel` gravado mas fora da coleção → `''`, peça de verdade → nome; e o HUD
  com uma chapa solta selecionada devolve `None`. `menu._peca` continua como estava: lá `anim.animavel` e
  `divisao_da_peca` já filtram o papel antes de desenhar, então o efeito é o mesmo sem tocar em mais nada.
- **Verificação.** `ruff check caffmob_draw/armario_v2/ tests/blender_017_armario_smoke.py tests/test_017_*.py` →
  *All checks passed*. `check_api.py` → *OK: no unknown API references found* (599 arquivos). `test_017_*.py` → **48
  testes, OK** (nove arquivos, `build` e `corte` inclusive). `test_i18n_coverage.py` → **3 testes, OK**. Fumaça
  `blender_017_armario_smoke.py` no Blender 5.2 → **OK**, exit 0, com **48 conferências e nenhuma falha**. Suíte pura inteira
  (`discover -p 'test_*.py'`) → **1073 testes, 1044 OK**, 28 erros de importação e 1 falha, todos anteriores a esta
  feature: os 28 são `caffmob/v2/contrato.py:2` pedindo `typing.NotRequired` (só Python 3.11+; o `python3` da máquina é
  3.10, o Blender traz 3.11) e a falha é `test_packaging.test_raiz_nao_e_extensao` reclamando do `blender_manifest.toml`
  em `novo_arm_building/`. Nenhum arquivo dos dois casos foi tocado pela 017 (`git status`).
- **Decisão 1, os 21 erros de ruff fora da 017: não corrigir nesta feature.** São preexistentes e estão em arquivos
  que a 017 não toca (`caffmob/v2/forma.py` e `paredes.py`, `library_panel/{draw,models_core,ops_replace}.py`,
  `mobi/{cena,ops_biblioteca}.py`, `stairs/core.py`, `target/adapters/__init__.py`,
  `texture_library/{handlers,ops_account}.py`, `ui/panels.py`, `walls2d/{studio,studio_aberturas}.py`): 6× `E731`,
  5× `E741`, 8× `F401`, 1× `F841`, 1× `W293`. Corrigir de passagem misturaria o diff da 017 com nove arquivos alheios e
  alguns `F401` são reexportações (`target/adapters/__init__.py` importa `resolver as r`) ou imports usados por atributo,
  que precisam de leitura caso a caso, não de `--fix`. **O portão da 017 é `ruff check` nos caminhos da feature**; a
  limpeza do pacote inteiro fica como dívida separada (sugestão: ação própria, com `--fix` só nos `F401`/`W293`
  seguros e revisão dos `E731`/`E741` um por um).
- **Decisão 2, as fumaças com janela 004/006/008/015: ficam superadas pela T027, não são regressão desta rodada.**
  As quatro dirigem o editor 2D (`bpy.ops.caffmob.cabinet_editor`, abas Estrutura/Divisão/Gavetas/Portas, museu de
  estruturas com Enter) — a interface que a T027 tirou do registro por D-04. Hoje `caffmob.cabinet_editor` é o `Abrir`
  do armário v2 (D-03) e ele recusa módulo de biblioteca com *"Este móvel é da construção antiga: recrie pelo
  construtor novo para editar"* (RN-23), que é exatamente o que as quatro encontraram no primeiro passo
  (`RuntimeError ... poll()`). Rodadas em `xvfb-run -a blender --factory-startup --enable-event-simulate`, como os
  próprios docstrings pedem: 004/006/008 param em `open_editor` e a 015 em "Enter abre o editor no módulo novo".
  Nada foi apagado nem reescrito: as quatro ficam no repositório como registro da superfície removida. O que continua
  valendo das features 004/006/008/015 está coberto pelos testes puros (`test_cabinet_editor_*`, `test_cabinet_*`,
  `test_structure_gallery`, `test_module_manifest`, `test_production_contracts` — todos OK na suíte de 1073) e pelas duas
  fumaças headless que passam: `blender_004_collision_smoke` → **OK** e `blender_004_stick_smoke` → **OK**.
- **Não conferido.** Nada da 017 foi olhado numa janela: painel, menu de contexto, HUD, alternadores e realce são
  desenhados por `draw`/`POST_PIXEL` e só o registro e os itens do menu (com layout falso) foram provados. As quatro
  fumaças com janela `004/006/008/015` precisam de reescrita contra a superfície v2 (ou de aposentadoria formal) numa
  ação própria, com decisão do titular.

### 2026-11-22, revisão com olhos novos: inspetor, fumaça e as fumaças com janela

- **O critério do inspetor está certo.** `panel.peca_da_selecao` é o único lugar que decide o que é peça: papel gravado
  em `btm_armario_parte` **e** `build.raiz_de(obj)` (o vazio da coleção do construtor) acima. `_peca_escolhida` só
  formata o nome e o HUD (`_peca`, `linhas_do_inspetor`) só consome o mesmo objeto. Os dois lados do "e" reprovam de
  verdade: a raiz tem o grupo com papel vazio e a chapa solta não tem raiz.
- **Defeito achado na conferência nova (corrigido).** A linha *"HUD usa o mesmo critério do painel"* rodava **depois**
  de `bpy.data.objects.remove(solta)`: sem seleção, `hud._peca` devolvia `None` por vacuidade e a conferência passaria
  mesmo com o filtro do HUD removido. Agora a comparação é feita com a chapa solta ainda na cena e cobre os três
  estados — raiz → `None`, solta com papel → `None`, peça de verdade → o próprio objeto (identidade, não nome), com os
  nomes no detalhe.
- **Leitura.** `peca_da_selecao` passou a checar `obj is None` antes do `getattr`; era inofensivo, mas lia errado.
- **Verificação:** `ruff check caffmob_draw/armario_v2/ tests/blender_017_armario_smoke.py tests/test_017_*.py` → *All
  checks passed*; fumaça 017 no Blender 5.2 → **OK**, exit 0, **48 conferências** (a do HUD agora com os três casos).
- **Fumaças com janela, medidas.** Rodadas em `xvfb-run -a blender --factory-startup --enable-event-simulate`: **006 e
  008 morrem no primeiro `open_editor`** — zero conferências, porque o primeiro módulo já é da construção antiga e o
  `poll` do `Abrir` recusa. **015 chega a sete conferências verdes** (galeria abre / Esc / Enter, estrutura criada,
  corte do Inferior com os dois sarrafos e sem Base superior, medidas do padrão, Superior com Base superior) e morre em
  `run_wardrobe`, no `open_editor`.
- **O que ainda faz sentido (proposta, nada alterado):**
  - **015: reescrever enxuto.** Vale o que não passa pela sessão 2D: galeria (`Esc`/`Enter`, `RUNNING_MODAL`),
    `cabinet_builder(structure_id=...)`, corte por `part_sources` (sarrafos e base superior), Padrão de Dimensões
    reaplicado e o JSON 2.3.0 com `structure_id`. Perde-se o bloco do armário de dormitório (3 vãos, 900 no vão do
    meio, Cabideiro 01, prateleira Invisível) e a conversão do módulo antigo ao abrir — tudo dirigido por
    `s.push(...)`/`props.session`, que não existe mais. O núcleo desses casos tem prova pura (`test_cabinet_bays`,
    `test_cabinet_editor_divisions`, `test_cabinet_catalog`); sem prova de ponta a ponta fica a **aplicação na cena**
    (`scene_divisions`, `scene_interiors` e a ferragem do `hardware.collect` depois do Inserir).
  - **006 e 008: aposentar formalmente.** São o editor 2D inteiro: abas e painéis e `REMOVE_PART`/`ADD_DIVISION`/
    inserção múltipla (006); `insert_payload` das sete abas, Aplicar/Cancelar, furação no corte e JSON com `hardware`
    (008). Nada disso tem equivalente no v2 — o v2 edita `btm_armario` por propriedades, não por sessão; reescrever
    "contra a superfície v2" seria escrever outra fumaça, e as regras que sobrevivem já estão nas puras
    (`test_cabinet_editor_*`, 42 casos, `test_cabinet_extras`, `test_cabinet_slides`, `test_structure_gallery`). A
    lacuna real é a mesma de cima: aplicação na cena.
- **Nada apagado.** Os quatro arquivos seguem no repositório, com o roteiro original, até a decisão do titular.

### 2026-11-22, T034 fechada na prática: 015 enxuta, 006/008 aposentadas e a 017 conferida em janela

- **`blender_015_construtor_smoke.py` reescrita enxuta.** Ficou o que não passa pela sessão do editor 2D: galeria
  (`RUNNING_MODAL`, `Esc` sem criar nada, `Enter` criando o Inferior c/ Divisória), corte por `part_sources` dos dois
  módulos, Padrão de Dimensões com sarrafo de 80 reaplicado e o JSON com `structure_id`. **8 conferências, todas OK**
  em `xvfb-run`. Saiu o bloco do armário de dormitório (3 vãos, 900 no vão do meio, Cabideiro 01, prateleira Invisível)
  e a conversão do módulo antigo ao abrir.
- **Defeito pré-existente, achado agora que a fumaça chega ao fim:** o JSON de produção está em **2.5.0** desde as
  features seguintes e a asserção estava presa em `"2.3.0"`. Ela nunca reprovava porque a fumaça abortava antes, no
  editor. Agora a conferência compara com `json_exporter.SCHEMA_VERSION` e continua exigindo o `structure_id`.
- **006 e 008 aposentadas:** `git mv` para `tests/retired/`, banner `**APOSENTADO**` no docstring, `sys.path` do
  `_blender_env` por `parents[1]` (o `check_reopen` da 006 inclusive) e `tests/retired/README.md` com o motivo, a
  tabela de cobertura substituta e o que continua sem prova. Nenhum roteiro foi reescrito nem apagado.
- **Lacuna registrada:** a **aplicação na cena** que só essas fumaças exercitavam de ponta a ponta
  (`scene_divisions`, `scene_interiors`, `scene_slides` e a ferragem de `hardware.collect` depois do Inserir) fica sem
  prova em Blender até existir uma fumaça própria que dirija os `scene_*` direto, sem janela e sem a sessão do editor.
- **017 conferida em janela.** `tests/_janela_017.py` (sonda, não fumaça de regressão) roda em `xvfb-run` com
  **7 conferências OK** e salva as capturas em `_reversa_forward/017-construtor-armario-v2/audit/janela/`. O que se viu:
  os **cinco alternadores** no canto inferior esquerdo do armário vazio; o **cartão do inspetor** com nome, medidas e
  papel (o aviso `Fora da chapa` só entra quando a peça passa); o **realce laranja** nas arestas da peça escolhida; e o
  **painel** inteiro legível — cabeçalho com `Abrir` da peça, montagem, vão ativo, chapa máxima, janela vazia, as sete
  abas e as quatro sub-abas de gavetas, os campos da gaveta, a linha de estado e as ações (Gerar mais alto por
  `scale_y = 1.4`, Montar Caixa/Limpar/Aplicar/Cancelar).
- **Limites desta conferência.** O **menu de contexto** não foi aberto: exige clique direito sobre a peça sob o cursor e
  a posição do menu não é estável para conferência; os itens dele seguem provados pela camada falsa de layout. A **barra
  lateral** abre com o painel hospedeiro da 005 por cima e o da 017 fica abaixo da dobra, então o corpo do painel foi
  conferido num popup que chama o mesmo `draw_painel` com `layout` real (o recorte da aba na sidebar não foi olhado).
- **Observação, não defeito:** com uma gaveta gerada sem Montar Caixa, o aviso *Janela de armário vazia* continua
  aparecendo — coerente com D-18 (o vazio é definido pelas quatro chapas da caixa), mas vale saber ao ler a captura.

### 2026-11-23, T031 e T032 (máquina Windows, sem Blender)

- **T031 `[X]`.** `caffmob_draw/blender_manifest.toml` de `1.25.0` para `1.26.0`. `python build.py` empacotou o pacote
  inteiro: *Successfully created 'caffmob_draw.zip'*, exit 0, **2367 arquivos**, com
  `assets/slides/slide-st48-0200-0.obj` dentro do ZIP no caminho esperado e o `blender_manifest.toml` do ZIP já em
  `version = "1.26.0"`. Nenhuma checagem do `build.py` (`missing_node_files`, `package_problems`, `texture_problems`,
  `pbr_problems`) olha `assets/`, então o OBJ viaja sem mudança no empacotador — W009 segue verdadeira.
- **T032 `[X]`, e o catálogo fechou de verdade.** `tools/i18n_scan.py armario_v2 --faltando` já dizia *0 sem
  tradução*, mas a varredura só vê texto constante, `tr(...)`/`N_(...)`, `report`, item de enum e `draw`/`blf`. As
  recusas do núcleo puro eram **montadas** com `"texto".format(...)` fora de `tr()`, então saíam em português em
  qualquer idioma da interface. Agora as mensagens nascem sobre o catálogo:
  - `spec.validate`: as duas templates (faixa e espessura) e a exclusividade entre porta de abrir e deslizante, com
    `tr(RANGE_LABELS[...])`/`tr(THICKNESS_LABELS[...])` no nome do campo;
  - `chapas.pode_gerar`: contrato ausente, chapa máxima inválida e papel faltando (`Contrato de chapas sem a {}`);
  - `vaos.duplicar`: divisão não encontrada, sem vão livre e o vão insuficiente com as duas medidas;
  - `conferencia.Violacao.texto()`: `{}: {} mm passa da chapa de {} mm`;
  - `resumo.linha_estado`: dimensões, montagem por extenso, vão, peça e as duas conformidades (`chapa conforme` e
    `chapa: fora da chapa — {}`).
  `tr()` resolve o idioma no momento da mensagem; fora do Blender devolve o texto do código e **nenhum** dos cinco
  módulos passou a carregar `bpy` (`'bpy' in sys.modules` → `False`, conferido com `_bootstrap`).
- **Catálogo reconciliado: 112 → 136 entradas.** 29 chaves novas (16 templates + 13 rótulos de espessura e de porta;
  `Largura`, `Altura` e `Profundidade` já existiam) e **4 órfãs apagadas** — texto que nenhum caminho produzia:
  `A peça {} passa da chapa máxima ({} × {} mm)` (a mensagem real carrega a medida da peça contra o limite, não duas
  medidas de chapa), `Dentro da chapa` (a linha de estado diz `chapa conforme`), `O contrato de chapas não foi
  definido: configure a aba Estrutura antes de gerar` (o `pode_gerar` diz o que falta e o painel já lista os motivos
  sob o botão) e `O vão livre é menor que 80 mm: não cabe outra peça` (a recusa real informa o vão medido). `vão {}`
  reaproveita a entrada de `customize.json` (`opening {}`) para não duplicar msgid.
- **Sem traceback nas três recusas.** Sonda pura: contrato ausente e chapa máxima em zero devolvem motivo em lista (o
  operador avisa com `report` e devolve `CANCELLED`), peça de 3000 mm volta como `Decisao(gera=False, avisos=...)` e,
  com `bloquear_chapa` desligado, gera com o mesmo aviso. `Cancelar` com instantâneo inválido já era `ValueError`
  capturado pelo operador (T021). **Modelo da corrediça ausente não tem caminho de erro porque o OBJ continua não
  instanciado** — o limite declarado na T033 (RN-08 só tem o arquivo empacotado): nada lê o arquivo, então nada
  levanta.
- **Verificação:** `test_i18n_coverage.py` → **3 testes OK** (0 sem tradução, 0 dinâmicos, nenhum msgid duplicado);
  `tools/i18n_scan.py armario_v2 cutting --faltando` → 203 textos, 183 únicos, **0 sem tradução, 0 dinâmicos**;
  `test_017_*.py` → **48 testes OK**; `check_api.py` → *OK*, 599 arquivos; `python build.py` → exit 0. **Não rodado:**
  `ruff` (não existe nesta máquina) e o Blender (a fumaça `blender_017_armario_smoke.py` roda no Linux de referência);
  a tradução em si só se confere numa janela em `en_US`.

### 2026-11-23, T036 a T040 (planejamento da segunda auditoria)

- **Origem.** A segunda passada do `cross-check.md` abriu dois HIGH que o plano não tinha como fechar: o A012 (RN-08 e RF-10, corrediça 3D) e o A013 (RN-17 e RF-20, reabertura por arquivo). O `build.py` só emite chapas, `armario_v2/` não importa OBJ nenhum e a fumaça da 017 nunca chamou `save_as_mainfile` nem `open_mainfile`.
- **`/reversa-plan`, decisões D-19 e D-20.** A corrediça ganha um núcleo puro (`corredica.py`) mais a instanciação no `build`, com o conjunto geométrico de reserva para quando o OBJ falta; a reabertura ganha fumaça própria em `tempdir`, sem mudança de desenho, porque o `Object.btm_armario` de D-02 já é o mecanismo.
- **A decisão que evita defeito no corte.** As partes da corrediça saem com `papel` vazio e um campo novo `ferragem`, porque `part_sources.armario_v2_records` lista toda malha com `papel` gravado: gravar `GAIOLA`/`TRILHO` em `papel` faria o trilho aparecer como chapa no plano de corte, contra o RF-19 e contra o critério de pronto que já exige a corrediça fora da lista. A animação passa a consultar `ferragem`, senão as gaiolas nunca seriam encontradas com a regra de 50% do curso.
- **Nada executado.** T036 a T040 entram com `[ ]`, como o titular pediu: só as ações e o roadmap foram escritos, nenhum arquivo de `caffmob_draw/` ou `tests/` foi tocado nesta rodada.
- **Alinhamentos de documento da mesma rodada.** O `requirements.md` §9 e §10 passam a dizer que o A003 foi decisão confirmada do titular em 2026-11-21, como o D-18 e o próprio `props.py` já diziam (A015); o Resumo deste arquivo corrige a maior cadeia de 10 para 11, passando por T014 e T015 (A016); e o §10 do roadmap deixa de marcar como pendente o que a T032, a T034 e a T035 já fecharam (A019).

### 2026-11-23, execução de T036 a T040

- **T036 `[X]`.** `caffmob_draw/armario_v2/corredica.py` criado: `MEDIDAS` do conjunto ST48 em milímetros (trilho
externo 200 × 35 × 8,5, trilho interno 173,5 × 20 × 6, gaiola 60 × 3,92 × 5,8, lidas do OBJ do anexo), `pecas(caixa,
curso, indice)` com as duas corrediças por gaveta, `recuo(spec)` (o mesmo 70 mm de `portas.recuo_por_papel` quando a
base da deslizante é por dentro), `papel_do_objeto` para casar os quatro objetos do OBJ (`_1` a `_4`) com as três
marcas, e `FERRAGENS`/`PAPEIS_DO_OBJ`. Toda parte sai com `papel` vazio, `ferragem` preenchida, medidas da caixa no
referencial do armário e o `conjunto` (o trilho externo) para o `build` alinhar o modelo importado.
- **T037 `[X]`.** `BTM_PG_ArmarioParte` ganhou `ferragem` (`NENHUMA`, `TRILHO_EXT`, `TRILHO_INT`, `GAIOLA`, em
`FERRAGEM_ITEMS`). `build.py` importa o OBJ **uma vez** com `bpy.ops.wm.obj_import(forward_axis='Y', up_axis='Z',
global_scale=MM)`, deita o conjunto (`ROTACAO_MODELO`, comprimento em Y e altura em Z), guarda as malhas com usuário
falso e remove os objetos do import, então nada sobra na cena; cada gaveta com `corredica_3d` recebe as duas
corrediças, com malha compartilhada e o conjunto alinhado pelo canto do trilho externo. Sem o arquivo, `_objetos_da_peca`
cai no conjunto de reserva de `corredica.pecas` (as mesmas três caixas). `anim.py` passou a reconhecer a gaiola por
`ferragem == 'GAIOLA'`, no lugar de `PAPEIS_GAIOLA`. O adaptador de corte continua descartando `papel` vazio, então a
corrediça não entra no plano de chapa (RF-19).
- **T038 `[X]`.** `tests/test_017_corredica.py` com 8 casos puros: duas corrediças por gaveta, `papel` vazio e
`ferragem` preenchida nas três partes, trilho externo por fora da caixa e interno por dentro, gaiola a meio curso,
curso do interno e da gaiola, recuo com a base por dentro (70 mm) e sem ela (0), conjunto de reserva com as medidas de
`MEDIDAS` e a corrediça fora de `resumo.lista_de_pecas` e de `conferencia.conferir`.
- **T039 `[X]`.** A fumaça ganhou `run_corredica`: bloco de quatro gavetas gera 8 trilhos externos, 8 internos e 16
gaiolas (duas por conjunto no OBJ) com `papel` vazio e agrupados por `" da gaveta N"`; com o caminho do OBJ trocado
por um inexistente, a geração cai no conjunto de reserva com 24 peças e as mesmas três marcas; e Abrir/Fechar move a
gaiola exatamente `0,5 × curso` (183,6 mm de 367,2 mm). O plano de corte segue sem peça de corrediça.
- **T040 `[X]`.** `tests/blender_017_reabrir_smoke.py` criado no padrão de `blender_067_ciclo_vida.py`: abre o armário,
monta três vãos (uma divisória e duas prateleiras), quatro gavetas e folha deslizante, gera, salva em `tempdir` com
`save_as_mainfile`, reabre com `open_mainfile` e confere que `Object.btm_armario` devolve as mesmas medidas, montagem,
divisões, gavetas, internos, portas, deslizante, fundo, o `snapshot` e as mesmas 62 peças (com as marcas de ferragem).
Depois de reabrir, Aplicar fixa o novo ponto de retorno, Gerar com 1200 mm funciona e Cancelar devolve o estado fixado.
- **Divergência declarada em T039.** A ação pede as corrediças "filhas da caixa da gaveta", mas o `build` não cria um
objeto para a caixa: as chapas da gaveta são filhas da raiz, agrupadas pelo sufixo `" da gaveta N"`, que é o critério
que `anim._grupo` já usa desde T022. As corrediças seguem o mesmo agrupamento, então a fumaça confere o sufixo em vez
da paternidade. Criar um vazio por caixa só para pendurar as peças mudaria a hierarquia que o menu e o HUD percorrem.
- **Aviso de MTL no import.** O OBJ referencia `slide-st48-0200-0.mtl`, que não existe no pacote (só o OBJ foi copiado
em T001); o Blender registra `cannot read from MTL file` e importa a geometria sem material, que é o que a corrediça
usa (material de alumínio do armário). Nenhuma peça depende do MTL.
- **Verificação:** `test_017_*.py` → **56 testes OK** (48 + 8 de `test_017_corredica.py`);
`tests/test_i18n_coverage.py` → **3 OK** (o catálogo `armario_v2.json` foi de 136 para 139 entradas: `Trilho externo`,
`Trilho interno` e `Gaiola`; `Nenhuma` já existia em `operators.json` e não foi duplicado); `check_api.py` → *OK: no
unknown API references found* (600 arquivos); `blender_017_armario_smoke.py` no Blender 5.2 → **OK, 52 conferências
verdes**; `blender_017_reabrir_smoke.py` → **OK, 11 conferências verdes**. `ruff` não existe nesta máquina (segue sem
rodar, como nas rodadas anteriores).


### 2026-11-23, T041 a T051 (insercao e travessas)

- **T041 `[X]`.** `spec.ALTURA_TRAVESSA = 90.0`, as presencas `contra_frente_ativa` e `peca_tras_ativa` no `Spec` e as
  duas funcoes devolvendo `{'comprimento': largura_interna, 'altura': 90, 'espessura': base superior, 'em_pe': ...}`.
  A leitura anterior (painel da altura total ou da profundidade) fecharia a frente do armario; a mudanca esta na
  premissa do roadmap §4 e o `test_017_spec.py` acompanhou (2000/560 mm viram 90 mm nos dois casos, com `em_pe`).
- **T042 `[X]`, com desvio registrado.** As duas flags entraram em `BTM_PG_ArmarioV2` e, junto delas, a caixa
  **Travessas** na aba Estrutura. Sem o checkbox nao havia caminho de uso para o RF-05: a flag so seria ligavel por
  Python. O desvio e de interface, nao de modelo.
- **T043 `[X]`.** `build.pecas` emite as duas travessas com componente `TRA`, no topo interno, entre as laterais; a peca
  de tras encosta na face interna do fundo quando o fundo esta ativo. `em pe` mantem 90 mm na altura e a espessura na
  profundidade; `deitada` troca os dois eixos.
- **T044 `[X]`.** `run_travessas` na fumaca: 5 conferencias verdes, incluindo a medida de corte 970 x 90 x 15 mm, a
  troca de eixo na caixa da peca e a saida do corte ao desmarcar a presenca.
- **T045 `[X]`.** `ops.vao_ativo` (mesmo criterio do cabecalho), `gravar_gavetas` e `gravar_internos`; o painel passou a
  delegar no `ops.vao_ativo`, entao o vao do cabecalho e o da insercao sao o mesmo por construcao.
- **T046 a T048 `[X]`, com dois desvios.** Sao cinco operadores: `inserir_divisoria`, `inserir_prateleira` (dois em vez
  de um com eixo, porque o enum de variante depende do eixo), `inserir_matriz`, `criar_bloco_gavetas` e
  `inserir_interno`. Este ultimo usa o tipo gravado no armario e **um** botao, nao quatro: o `layout.operator` do
  Blender nao leva parametro, e quatro classes iguais so para fixar o tipo seriam codigo repetido. O tipo continua em
  enum, como a acao pedia.
- **T049 e T050 `[X]`.** Aba Divisoes com variante e botao por eixo e a caixa da matriz na sub-aba Multipla; aba Gavetas
  com quantidade, altura do bloco, modelo e botao; aba Internos com o tipo e o botao.
- **T051 `[X]`.** `run_insercao` na fumaca: 11 conferencias verdes, incluindo a matriz 2 x 1 (2 verticais e 7 pecas no
  total), o bloco de 2 gavetas com as frentes na cena, a recusa sem escrita quando o bloco nao cabe e o calceiro a
  480 mm. O passo de desfazer foi conferido pela flag `UNDO` nos cinco operadores, **nao** por `Ctrl+Z` real: em
  `--background` o desfazer global nao e confiavel.
- **Verificacao desta rodada:** `test_017_*.py` com **57 casos OK** (um novo no spec); `test_i18n_coverage` OK com
  **166 entradas** no catalogo (27 novas); `check_api.py` sem `[UNKNOWN in 5.2]` em 600 arquivos;
  `blender_017_armario_smoke.py` verde com as **16 conferencias novas**; `blender_017_reabrir_smoke.py` verde com 11.
  `ruff` continua ausente nesta maquina, entao a checagem de estilo segue sem rodar.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-to-do` a partir do roadmap da 017 | reversa |
| 2026-11-21 | Fechamento do cross-check: T035 acrescentado (A001), T027 mantém `gallery` (A002), T003 cria as flags de presença (A003), T034 passa a cobrir o teste de corte | reversa |
| 2026-11-21 | T001 e T002 executados e marcados `[X]`; A003 confirmado por flags de presença (sem enum) | reversa |
| 2026-11-21 | T003 executado: PropertyGroups do armário, da peça e do contrato; 20 textos de enum no catálogo | reversa |
| 2026-11-21 | T004 executado: cascata de registro do pacote `armario_v2`; delta de dados explicita nove espessuras no armário e oito no contrato | reversa |
| 2026-11-21 | Fase 2 fechada: T005 a T011 executados, sete suítes puras (34 casos) escritas e verdes por skip declarado até T012–T019 | reversa |
| 2026-11-21 | Fase 3 fechada: T012 a T019 executados, oito módulos puros (`spec`, `vaos`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo`) e os 34 casos sem skip | reversa |
| 2026-11-22 | T013 corrigida: colisão de caminhos de vão com divisórias e prateleiras no mesmo vão, dois casos novos (36 no total); T020 executado com `build.py` e a coleção do armário | reversa |
| 2026-11-22 | T020 completado: chapas da caixa da gaveta no plano de corte e teste puro de `build.pecas` (`test_017_build.py`, 6 casos; 42 no total) | reversa |
| 2026-11-22 | T021 executado: `ops.py` com abrir/Gerar/Aplicar/Cancelar/Limpar sobre `build.gerar`, instantâneo JSON do Cancelar e recusa sem contrato; T034 passa a contar nove testes puros | reversa |
| 2026-11-22 | T022 executado: `anim.py` com timer de 16 ms, 18 quadros por alvo, curso lido do `build`, `btm_armario.aberto` e handle removido em todos os caminhos; 16 textos de i18n de T021/T022 no catálogo | reversa |
| 2026-11-22 | T023 executado: `panel.py` com as sete abas, sub-abas, cabeçalho, janela vazia e aviso do móvel antigo; `ops.py` ganhou Montar Caixa e o Abrir que cria o armário vazio; 10 textos no catálogo | reversa |
| 2026-11-22 | T023 corrigido (semente do contrato saiu do draw para o Abrir e um botão) e cascata com `ops` pela guarda do `bl_idname`; T024 executado com o menu de contexto | reversa |
| 2026-11-22 | T025 executado: `hud.py` com alternadores da estrutura, inspetor da peça e realce da seleção em `POST_PIXEL` | reversa |
| 2026-11-22 | T026 executado: `ponte.py` com a leitura do módulo de biblioteca, o Gerar pelo motor novo e o Recriar do módulo | reversa |
| 2026-11-22 | Painel corrigido: a seleção de módulo de biblioteca vence o recuo para a coleção de armários v2, com caso novo na fumaça | reversa |
| 2026-11-22 | T027 executado: interface do editor 2D fora do registro de `cabinet_editor`, `gallery` mantida | reversa |
| 2026-11-22 | T028 executado: `caffmob.cabinet_editor_modal` sai de `_MANAGED` (colisão) e de `_MOVE_IDS` (assentar) |
| 2026-11-22 | T029 revisado e T030 executado: armário oculto sai do corte; `armario_v2` entra na cascata da extensão entre `customize` e `cabinet_editor` | reversa |
| 2026-11-22 | T033 executado e rodado no Blender 5.2: fumaça headless verde, com sete defeitos reais corrigidos (guarda do `bl_idname`, `poll` do Abrir, semente do contrato, raiz do armário em todo o pacote, construção antiga, RN-06 e `e_construcao_antiga`) | reversa |
| 2026-11-22 | T035 executado: `iter_modules` ignora módulo oculto/`btm_cut_exclude`; `tests/test_017_corte.py` com 6 casos contando as peças antes e depois da conversão | reversa |
| 2026-11-22 | T034 executado: inspetor de peça do painel/HUD só aceita peça do armário v2 (papel e raiz); verificação fechada com 48 testes puros da 017, suíte de 1073, check_api e fumaça 017; 21 erros de ruff do legado e as quatro fumaças com janela superadas pela T027 documentados como decisão | reversa |
| 2026-11-22 | Revisão com olhos novos da T034: conferência do HUD na fumaça era vácua (rodava depois do `remove`) e passou a cobrir os três estados; fumaças com janela medidas (006/008 zero conferências, 015 sete) e proposta de reescrever a 015 enxuta e aposentar 006/008, sem apagar nada | reversa |
| 2026-11-22 | T034 executada na prática: 015 reescrita enxuta com 8 conferências verdes e a versão do JSON corrigida para a do exportador (2.5.0); 006/008 movidas para `tests/retired/` com README e a lacuna de aplicação na cena registrada; 017 conferida em janela pela sonda `tests/_janela_017.py`, com capturas do painel, do HUD e do realce | reversa |
| 2026-11-22 | T029 executado: adaptador `armario_v2_records` no corte, somado em `extract_production_parts`; `ARMARIO_V2` entra em `json_exporter.SOURCES` | reversa |
| 2026-11-22 | T029 revisado: armário oculto também tira as chapas do corte; T030 executado: `armario_v2` na cascata da extensão (hot-reload, import, registro entre `customize` e `cabinet_editor`) | reversa |
| 2026-11-23 | T031 executado: manifesto em `1.26.0` e `build.py` empacotando com o OBJ da corrediça (2367 arquivos, exit 0) | reversa |
| 2026-11-23 | T032 executado: as recusas do núcleo (`spec`, `chapas`, `vaos`, `conferencia`, `resumo`) passam por `tr()`; 29 chaves novas e 4 órfãs fora do catálogo (136 entradas) | reversa |
| 2026-11-23 | Segunda auditoria: T036 a T040 acrescentados para fechar A012 (corrediça 3D) e A013 (reabertura por arquivo), com D-19 e D-20 no roadmap; Resumo corrigido para 40 ações, 23 `[//]` e cadeia 11 (A016) | reversa |
| 2026-11-23 | T036 a T040 executados: `corredica.py` (núcleo puro), `ferragem` em `BTM_PG_ArmarioParte`, OBJ e conjunto de reserva no `build`, gaiola por `ferragem` na `anim`, `test_017_corredica.py` (8 casos) e as fumaças da corrediça e da reabertura | reversa |
| 2026-11-23 | T041 a T051 acrescentados pelo `/reversa-to-do` do clarify de 2026-11-23: inserção pela interface (D-21) e travessa de contra-frente e peça de trás (D-22); Resumo em 51 ações, 25 `[//]` e núcleo com 9 | reversa |
| 2026-11-23 | T041 a T051 executados: travessa de 90 mm no spec e no build com duas presenças, cinco operadores de inserção com geração no mesmo passo, painel das três abas, 27 entradas novas no catálogo e 16 conferências novas na fumaça | reversa |
