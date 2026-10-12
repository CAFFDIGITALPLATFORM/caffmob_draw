# Biblioteca de objetos (object_library) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/object_library/` (9 arquivos Python, 907 linhas, e 6 itens embutidos em `items/`) em 2026-10-10. A árvore de trabalho não tem alterações sem commit nesta pasta (`git status --short caffmob_draw/object_library` vazio); a unit entrou no commit `fa24c0e` e não mudou depois. Confirmação de código não implica validação visual no Blender. 🟡 marca prioridade ou intenção inferida; 🔴 marca lacuna que exige validação no host.

## Visão Geral

🟢 Biblioteca de **objetos não paramétricos do ambiente** (portas, janelas, cooktops, mesas, cadeiras, decoração), da feature 009 (incremento I2). Cada item são três arquivos com o mesmo nome-base (`<item_id>.blend`, `.json`, `.png`) dentro da pasta da categoria, em duas raízes: a **embutida** (`caffmob_draw/object_library/items/`, só leitura) e a **do usuário** (`extension_path_user(<pacote>, path="object_library")`). A seção Inserir › Objetos da barra lateral lista os itens por categoria, com miniatura e busca; um clique insere o item no cursor 3D e, na viewport, ele acompanha o mouse até um clique soltar. O usuário acrescenta a seleção (ou um arquivo 3D) à própria biblioteca e retexturiza parte ou item inteiro com um acabamento do plugin ou uma imagem própria em escala real. Fontes: `__init__.py`, `store.py`, `item_io.py`, `ops.py`, `panels.py`, `retexture.py` (docstrings).

🟢 É distinta da Biblioteca CAFFMob de móveis paramétricos (`_reversa_sdd/library_panel/`, RN-15 de lá) e da biblioteca de módulos salvos (`_reversa_sdd/customize/`, `library_io`), embora reutilize a mecânica desta (`libraries.write` + manifesto JSON + miniatura) (`item_io.py`, docstring). Não faz download, não usa rede nem banco de dados.

## Responsabilidades

- 🟢 Definir as 7 categorias, o formato do manifesto `caffmob_draw.object_item` v1, o id estável e a busca por nome, em Python puro (`catalog.py`).
- 🟢 Listar os itens das duas raízes, montar caminhos, renomear nomes repetidos, apagar itens do usuário e checar a origem dos embutidos, sem `bpy` (`store.py`).
- 🟢 Marcar a raiz de um item no objeto (`Object.btm_object_item`) e guardar o estado de sessão da seção (`WindowManager.btm_object_library`) (`props.py`).
- 🟢 Salvar um item (`.blend` + manifesto + miniatura) e inserir um item na cena (`item_io.py`).
- 🟢 Retexturizar malhas com acabamento do plugin ou imagem própria (`retexture.py`).
- 🟢 Carregar miniaturas sob demanda (`previews.py`) e desenhar as seções Inserir › Objetos e Selecionado › Retexturizar (`panels.py`).
- 🟢 Expor 5 operadores `caffmob.object_*` (`ops.py`).
- 🟢 Fora da responsabilidade (contratos citados, não redescritos): grupo de peças, folha, esquadria, agregado e peça de produção (`_reversa_sdd/aggregates/`: `group.is_group`, `group.create_group`, `btm_aggregate`), importação de arquivos 3D incluindo SketchUp (`_reversa_sdd/aggregates/` RF-14 a RF-16, `caffmob.import_model`), aplicação de material em peça `GeoNodeCutpart` (`_reversa_sdd/customize/`, `adapters/common.set_cutpart_material`), versão do addon (`customize/library_io._addon_version`), miniatura e caixa envolvente (`library_common.thumbnail/world_box`), raiz do componente na seleção (`_reversa_sdd/selection/`, `component.py` precedência 5), Mover Sobre e colisão (`_reversa_sdd/move_over/`, `_reversa_sdd/collision/` EC-15), sincronização de padrões (`standards/sync._other_roots`), casca da barra lateral (`ui/sidebar*.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Categorias, nesta ordem (chave, rótulo `N_`, ícone): `DOORS` "Portas" `MESH_PLANE`; `WINDOWS` "Janelas" `MESH_GRID`; `COOKTOPS` "Cooktops e eletros" `MESH_CIRCLE`; `TABLES` "Mesas" `MESH_CUBE`; `SEATING` "Cadeiras e assentos" `MESH_CONE`; `DECOR` "Decoração" `MESH_MONKEY`; `OTHER` "Outros" `MESH_ICOSPHERE`. | catalog.py:CATEGORIES |
| RN-02 | 🟢 Manifesto válido: dicionário com `format == "caffmob_draw.object_item"`, `version == 1`, `item_id`, `name` e `root` strings não vazias após `strip()`, e `item_id` casando `^[a-z0-9]+(-[a-z0-9]+)*$`. Categoria fora das 7 vira `OTHER`; `features` fora da lista de 7 são descartadas; `size_mm` vira `float` e é cortado a 3 posições (ausente = `[0,0,0]`). | catalog.py:read_manifest |
| RN-03 | 🟢 Id novo = `slug(nome) + "-" + token_hex(3)` (6 hex); `slug` = NFKD → ASCII → minúsculas → cada sequência fora de `[a-z0-9]` vira `-` → `strip("-")`; vazio vira `"item"`. Itens embutidos usam id fixo sem token (`porta-lisa-80`). | catalog.py:slug/new_item_id; tools/build_object_library.py:ITEMS |
| RN-04 | 🟢 Busca: com texto não vazio, mantém o item cujo `slug(nome)` contém `slug(texto)`; texto vazio ou só espaços mantém todos (ignora acentos, caixa e pontuação). | catalog.py:search |
| RN-05 | 🟢 Um item só é listado se o manifesto for válido **e** existir `<pasta>/<pasta da categoria>/<entry.item_id>.blend`; senão vira aviso `"<caminho>: <motivo>"` (ou `"<caminho>: falta o .blend"`). A miniatura é opcional. Embutidos vêm antes dos do usuário; dentro de cada raiz, pastas e arquivos em ordem alfabética. | store.py:_scan/list_items |
| RN-06 | 🟢 A categoria exibida é a do manifesto (`entry.category`), não a da pasta física. | store.py:by_category |
| RN-07 | 🟢 Um item é endereçado na UI pela chave `"<U|B>:<categoria>:<item_id>"` (U = do usuário, B = embutido); toda ação relê o disco para achar o item pela chave. | ops.py:item_key/find_item |
| RN-08 | 🟢 Itens embutidos não podem ser apagados (`PermissionError("item embutido")`); apagar um do usuário remove `.blend`, `.json`, `.png` e `.blend1` do mesmo nome-base, após confirmação. A UI só mostra o botão de remover nos itens do usuário. | store.py:delete; ops.py:BTM_OT_ObjectLibraryRemove; panels.py:draw_insert |
| RN-09 | 🟢 Biblioteca embutida não pode conter item cuja `source` comece (sem caixa, após `strip`) por "3D Warehouse" (licença proíbe redistribuir). Checado ao gerar os embutidos e ao empacotar; não é checado ao listar. | store.py:check_bundled; tools/build_object_library.py:main; build.py (checagem de ativos) |
| RN-10 | 🟢 Nome repetido ao acrescentar: compara o nome (após `strip`) com os **nomes exatos dos itens do usuário na mesma categoria**; `RENAME` (padrão) gera "Nome 2", "Nome 3"… (primeiro sufixo livre a partir de 2); `REPLACE` regrava sobre o `item_id` do item existente. | ops.py:BTM_OT_ObjectLibraryAdd.execute; store.py:unique_name; item_io.py:existing_names |
| RN-11 | 🟢 A raiz de um item salvo é um grupo de peças: se a seleção tem um só objeto de topo que já é grupo (`btm_group.is_group`) ou raiz de item, ele é a raiz; senão as **malhas de topo** da seleção são agrupadas num grupo `PLAIN` novo com o nome do item. Seleção sem malha de topo é recusada. | item_io.py:prepare_root |
| RN-12 | 🟢 As conversões (grupo, esquadria, folha de giro/correr, agregado, peça de produção) ficam nos próprios objetos e voltam com a cópia ao inserir; o manifesto só as **descreve** em `features`, na ordem `GROUP, FRAME, LEAF_SWING, LEAF_SLIDE, AGGREGATE, PRODUCTION_PART, TEXTURED`. | props.py (docstring); item_io.py:features_of |
| RN-13 | 🟢 Inserir anexa (append, não link) todos os objetos do `.blend` à coleção ativa (ou à da cena), tira o fake user deles, põe a raiz no cursor 3D, seleciona só a raiz e a torna ativa. | item_io.py:insert; ops.py:BTM_OT_ObjectInsert._load |
| RN-14 | 🟢 Inserção interativa (área `VIEW_3D`): a raiz acompanha o mouse no plano horizontal `z = cursor.z`; clique esquerdo solta (um passo de desfazer); Esc ou botão direito cancelam **e removem** os objetos carregados; botão do meio e roda passam adiante (navegar a vista). Fora da `VIEW_3D`, insere direto no cursor. **Exceção confirmada:** invocado pelo botão da barra lateral (região `UI`), o modal recebe a região `UI` e `region_data = None`, então a raiz **não** acompanha o mouse; o clique esquerdo a solta no cursor 3D (EC-10). _(Revisão 2026-10-10: sonda com xvfb-run e eventos simulados: pela região WINDOW a raiz andou até (3.41, -2.92, 0); pela UI ficou em (0, 0, 0); _follow viu region UI e rv3d None (ops.py:91-94))_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-59):** corrigir: quando `context.region_data` for `None`, `_follow` acha a região `WINDOW` da área e converte `event.mouse_x/y` para as coordenadas dela; o caso entra no teste do modal (TT-03). Pendência de implementação: DT-01. | ops.py:BTM_OT_ObjectInsert.invoke/modal |
| RN-15 | 🟢 Retexturizar vale para a **cópia na cena**; salvar de novo na biblioteca é opcional. Escopo `PART` = objetos selecionados (ou o ativo se nada selecionado); `ITEM` = árvore da raiz de item do ativo (ou do próprio ativo). Só malhas mudam. | retexture.py (docstring); ops.py:_scope_objects; retexture.py:targets |
| RN-16 | 🟢 Acabamentos oferecidos = materiais dos 3 `.blend` de materiais das bibliotecas legadas (frameless, face frame, closets) ∪ materiais do arquivo cujo nome não começa por `.`, ordenados sem caixa. Material já no arquivo tem prioridade; senão é anexado do `.blend` de origem. | retexture.py:LIBRARIES/finish_names/_finish |
| RN-17 | 🟢 Imagem própria: material "Textura: <arquivo> <tamanho:g> mm", projeção em caixa sobre coordenadas de objeto, escala `1 / max(tamanho_mm/1000, 1e-4)` nos 3 eixos; reaproveita material com o mesmo caminho absoluto e tamanho (tolerância 1e-6). Formatos do seletor: png, jpg, jpeg, tif, tiff, webp. Tamanho 1–100000 mm, padrão 600. | retexture.py:image_material; ops.py:BTM_OT_ObjectRetextureImage |
| RN-18 | 🟢 Desfazer: inserir, acrescentar e retexturizar entram (`{'REGISTER', 'UNDO'}`); remover da biblioteca não (`{'REGISTER'}`; altera só arquivos externos). Arquivos gravados ou apagados em disco nunca são desfeitos. | ops.py (bl_options) |
| RN-19 | 🟢 A seção Retexturizar só aparece em Selecionado quando há ao menos uma malha selecionada. | ui/sidebar_selected.py:draw |

## Requisitos Funcionais

🟡 Prioridades inferidas de `_reversa_forward/009-mira-calculo-skp-biblioteca/requirements.md` (RF-06 a RF-10: Must para biblioteca, acrescentar e conversões; Should para itens iniciais e retextura) e dos testes existentes.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Listar itens embutidos e do usuário por categoria, com miniatura, busca por nome e aviso de arquivos ignorados | Must | CA-01, CA-02, CA-03 |
| RF-02 | 🟢 Inserir um item no cursor 3D, com posicionamento interativo e cancelamento que remove o item | Must | CA-04, CA-05, CA-06, CA-07 |
| RF-03 | 🟢 Acrescentar a seleção ou um arquivo 3D à biblioteca do usuário, com categoria, nome, origem, autor, licença e tratamento de nome repetido | Must | CA-08, CA-09, CA-10, CA-11 |
| RF-04 | 🟢 Conversões do item (grupo, esquadria, folha, agregado, peça de produção) preservadas ao salvar e inserir | Must | CA-12 |
| RF-05 | 🟢 Remover item do usuário; embutidos protegidos | Should | CA-13, CA-14 |
| RF-06 | 🟢 Retexturizar parte ou item com acabamento do plugin | Should | CA-15, CA-16 |
| RF-07 | 🟢 Retexturizar com imagem própria em escala real | Should | CA-17, CA-18 |
| RF-08 | 🟢 Seis itens embutidos modelados pelo projeto (origem "CAFFMob Draw", GPL-3.0-or-later), sem modelo do 3D Warehouse | Should | CA-19 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Integridade de arquivo | `.blend` e `.json` gravados em temporários na pasta de destino (`mkstemp`) e movidos com `os.replace`; temporários removidos em `OSError`/`RuntimeError`. Não é transação entre os dois arquivos nem inclui a miniatura. Ressalva: o `.json` temporário só entra na lista de limpeza depois do `json.dump`, então uma falha durante a escrita dele deixa o `.tmp` na pasta _(Revisão 2026-10-10: item_io.py:109-112)_ | item_io.py:save | 🟢 |
| Segurança de caminho | `item_id` restrito a `[a-z0-9-]` pela regex: um manifesto não consegue apontar para fora da pasta da categoria. Ressalva: `re.match` com `$` aceita um `\n` final (`"abc\n"` passa), sem permitir sair da pasta _(Revisão 2026-10-10: catalog.py:32,73; conferido em Python)_ | catalog.py:_ID/read_manifest; store.py:paths_for | 🟢 |
| Licenciamento | Embutidos sem origem "3D Warehouse" (gerador e `build.py` recusam) | store.py:check_bundled; build.py | 🟢 |
| Separação do cálculo | `catalog.py` e `store.py` sem `bpy` (testáveis fora do Blender) | imports; tests/test_object_library.py | 🟢 |
| Desempenho da UI | Miniaturas em `bpy.utils.previews` com chave `caminho:mtime` (carregadas uma vez por versão do arquivo). **Sem cache da listagem**: cada redesenho da seção relê as duas pastas e todos os manifestos | previews.py:icon_id; panels.py:draw_insert → item_io.all_items | 🟢 |
| i18n | Textos de UI por `tr`/`N_`; catálogo `data/translations/object_library.json` | panels.py; ops.py; catalog.py | 🟢 |
| Ciclo de vida | `unregister` remove operadores, coleção de previews, `WindowManager.btm_object_library` e `Object.btm_object_item` (ordem inversa de `props → previews → ops`) | __init__.py; props.py; previews.py; ops.py | 🟢 |
| Compatibilidade | Pasta do usuário por `bpy.utils.extension_path_user` (regra do projeto para arquivos do usuário) | item_io.py:user_dir | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual. CA-01 a CA-03, CA-13, CA-14 e CA-19 são cobertos em parte por `tests/test_object_library.py` (10 testes puros, executados em 2026-10-10: OK). CA-04, CA-08, CA-10, CA-12, CA-13, CA-15, CA-17, CA-19 estão em `tests/blender_009_library_smoke.py` (precisa do Blender; não executado nesta extração). O modal (CA-05 a CA-07) não tem teste automatizado. _(Revisão 2026-10-10: blender_009_library_smoke executado no Blender 5.2.0 LTS: 17 verificações OK, inclusive o 2º Blender; CA-05 e CA-06 conferidos por sonda com eventos simulados quando o modal é invocado na região WINDOW)_

```gherkin
CA-01 — Listagem das duas raízes
Dado um item válido na raiz embutida (DOORS, com .png) e outro na do usuário (TABLES, sem .png), e um "quebrado.json" inválido
Quando list_items(embutida, usuário) é chamado
Então devolve [embutido (user=False, thumb≠None), usuário (user=True, thumb=None)] e 1 aviso

CA-02 — Busca sem acento e sem caixa
Dado os itens "Porta lisa" e "Mesa"
Quando a busca é "LIS" (ou "  ")
Então resta só "Porta lisa" (ou os dois)

CA-03 — Categoria vazia
Dado a categoria SEATING sem itens
Quando a seção Inserir › Objetos desenha
Então mostra a dica inativa "Nenhum objeto nesta categoria" (com busca preenchida: "Nenhum objeto com esse nome") e ainda o botão "Acrescentar à biblioteca"

CA-04 — Inserir sem interação
Dado o cursor 3D em (2, 0, 0) e o item embutido "Porta lisa 80"
Quando caffmob.object_insert(key="B:DOORS:porta-lisa-80") roda por execute
Então a raiz fica em x = 2, é a única selecionada e ativa, o relatório é INFO "Porta lisa 80 inserido" e devolve FINISHED

CA-05 — Posicionar e soltar
Dado o operador invocado numa área VIEW_3D
Quando o mouse se move e o botão esquerdo é pressionado
Então a raiz segue a interseção do raio da vista com o plano z = cursor.z, o texto do cabeçalho é limpo e devolve FINISHED (um passo de desfazer)

CA-06 — Cancelar
Dado o operador em modal
Quando Esc ou o botão direito são pressionados
Então todos os objetos carregados são removidos de bpy.data, o cabeçalho é limpo e devolve CANCELLED

CA-07 — Item ausente ou corrompido
Dado uma chave que não corresponde a nenhum item (ou um .blend sem a raiz do manifesto nem objeto sem pai marcado como item)
Quando caffmob.object_insert roda
Então reporta ERROR "Objeto não encontrado na biblioteca" (ou "Item corrompido: <nome>", depois de remover os objetos anexados) e devolve CANCELLED

CA-08 — Acrescentar a seleção
Dado uma porta inserida selecionada sozinha (raiz de item)
Quando caffmob.object_library_add(name="Porta copiada", category='DOORS', source="Teste") roda
Então surgem <usuário>/DOORS/porta-copiada-<6 hex>.blend|.json|.png, o manifesto tem format/version corretos e "Porta copiada" aparece em existing_names('DOORS')

CA-09 — Pedido inválido
Dado nome só com espaços, ou nenhuma seleção e nenhum arquivo, ou seleção sem malha de topo
Quando o operador executa
Então reporta ERROR "Dê um nome ao objeto" / "Selecione o objeto ou escolha um arquivo" / "A seleção não tem malhas" e devolve CANCELLED sem gravar

CA-10 — Nome repetido
Dado "Meu teste" já salvo pelo usuário em DECOR
Quando acrescento outro "Meu teste" com RENAME e depois com REPLACE
Então os nomes do usuário em DECOR ficam ["Meu teste", "Meu teste 2"] (o REPLACE regrava o item_id de "Meu teste")

CA-11 — Falha de gravação
Dado a pasta da categoria sem permissão de escrita
Quando o operador salva
Então reporta ERROR "Não foi possível gravar o item em <pasta>: <erro>", remove os temporários e devolve CANCELLED

CA-12 — Conversões voltam
Dado a porta salva pelo usuário com folha de giro de 90°
Quando ela é inserida noutra sessão do Blender
Então a folha continua de giro até 90°

CA-13 — Remover item do usuário
Dado "Meu teste 2" do usuário
Quando caffmob.object_library_remove é confirmado
Então os arquivos .blend/.json/.png/.blend1 somem, INFO "Meu teste 2 removido da biblioteca" e FINISHED

CA-14 — Embutido protegido
Dado a chave de um item embutido
Quando caffmob.object_library_remove executa
Então reporta ERROR "Os objetos que vêm com o plugin não podem ser removidos", nada é apagado e devolve CANCELLED

CA-15 — Acabamento numa parte
Dado o tampo da "Mesa 120 x 80" selecionado e um acabamento do plugin
Quando caffmob.object_retexture_finish(finish=<nome>, scope='PART') executa
Então só o tampo recebe o material, INFO "1 peça(s) com <nome>" e FINISHED

CA-16 — Acabamento sem efeito
Dado um acabamento inexistente ou uma seleção sem malha
Quando o operador executa
Então reporta WARNING "Nada mudou: acabamento ausente ou seleção sem malhas" e devolve CANCELLED

CA-17 — Imagem em escala real
Dado madeira.png e tamanho 600 mm
Quando aplico a imagem no tampo
Então o material tem Image Texture com projeção BOX e Mapping com escala 1/0,6; aplicar de novo a mesma imagem e tamanho reaproveita o mesmo material

CA-18 — Imagem inválida
Dado nenhum arquivo escolhido (ou arquivo que o Blender não abre)
Quando caffmob.object_retexture_image executa
Então reporta ERROR "Escolha uma imagem" (ou "Não foi possível abrir a imagem: <erro>") e devolve CANCELLED

CA-19 — Pacote limpo
Dado os manifestos embutidos
Quando check_bundled é aplicado (ou build.py empacota)
Então não há item com origem "3D Warehouse…"; há 6 itens em DOORS, WINDOWS, COOKTOPS, TABLES e DECOR (2), sem avisos
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| RF-01 listagem, RF-02 inserção | Must | 🟡 Caminho de toda utilização; RF-06 da feature 009 é Must |
| RF-03 acrescentar, RF-04 conversões | Must | 🟡 RF-08/RF-09 da 009 são Must; base para usar modelos importados (SketchUp/OBJ) |
| RF-05 remover | Should | 🟡 Gestão da biblioteca; há alternativa manual (apagar arquivos) |
| RF-06, RF-07 retexturizar | Should | 🟡 RF-10 da 009 é Should; acabamento também é trocável por outros caminhos |
| RF-08 itens embutidos | Should | 🟡 RF-07 da 009 é Should; a biblioteca funciona vazia |
| Checagem de origem "3D Warehouse" | Must | 🟡 Regra de licença com bloqueio no build |
| Cache da listagem | Won't (no código atual) | 🟢 Não existe; cada redesenho relê o disco |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---|---|---|
| `caffmob_draw/object_library/__init__.py` | `_modules`, `register`, `unregister` | 🟢 |
| `caffmob_draw/object_library/catalog.py` | `FORMAT`, `VERSION`, `BUNDLED_SOURCE`, `FORBIDDEN_BUNDLED_SOURCE`, `CATEGORIES`, `CATEGORY_KEYS`, `CATEGORY_ITEMS`, `FEATURES`, `ManifestError`, `Entry`, `slug`, `new_item_id`, `read_manifest`, `to_manifest`, `search` | 🟢 (testes puros) |
| `caffmob_draw/object_library/store.py` | `BUNDLED_DIR`, `Item`, `paths_for`, `_scan`, `list_items`, `by_category`, `unique_name`, `delete`, `check_bundled` | 🟢 (testes puros) |
| `caffmob_draw/object_library/props.py` | `BTM_PG_ObjectItem`, `BTM_PG_ObjectLibraryUI`, `register`, `unregister` | 🟢 |
| `caffmob_draw/object_library/item_io.py` | `user_dir`, `all_items`, `tree`, `root_of`, `prepare_root`, `features_of`, `existing_names`, `save`, `insert` | 🟢 |
| `caffmob_draw/object_library/retexture.py` | `LIBRARIES`, `PATH_PROP`, `SIZE_PROP`, `library_materials`, `finish_names`, `_finish`, `targets`, `apply_finish`, `image_material`, `apply_image` | 🟢 |
| `caffmob_draw/object_library/previews.py` | `icon_id`, `unregister` | 🟢 |
| `caffmob_draw/object_library/panels.py` | `draw_insert`, `draw_retexture`, `_key` | 🟢 |
| `caffmob_draw/object_library/ops.py` | `item_key`, `find_item`, `_scope_objects`, `SCOPE_ITEMS`, `BTM_OT_ObjectInsert`, `BTM_OT_ObjectLibraryRemove`, `BTM_OT_ObjectLibraryAdd`, `_finish_items`, `BTM_OT_ObjectRetextureFinish`, `BTM_OT_ObjectRetextureImage` | 🟢 |
| `caffmob_draw/object_library/items/*/*` | 6 itens embutidos (gerados por `tools/build_object_library.py`) | 🟢 |
