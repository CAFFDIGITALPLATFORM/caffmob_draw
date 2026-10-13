# Legacy impact: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12` (rodada 1: Fase 1, Fase 2 e núcleos puros; T006 com `/impeccable`; rodada 2: T018; rodada 3: T026 a T028;
> rodada 4: T029; rodada 5: T020, T021, T023, T025, T030 a T047, feature completa)
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/object_library/requirements.md`

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/object_library/retexture.py` | Biblioteca de objetos, material de imagem (`_reversa_sdd/object_library/requirements.md#RN-17`) | regra-alterada | MEDIUM | `image_material` ganha altura, veio e id do catálogo; a chamada antiga continua igual (quadrado, mesmo nome, mesmo reaproveitamento) |
| `caffmob_draw/blender_manifest.toml` | Integrações e distribuição (`_reversa_sdd/architecture.md#Integrações e distribuição`) | delta-de-contrato-externo | MEDIUM | Permissão `network` declarada; a extensão passa a pedir acesso à internet ao Blender |
| `.gitignore` | Integrações e distribuição | delta-de-dados | LOW | Imagens em tamanho real fora do git; catálogo e miniaturas versionados |
| `caffmob_draw/texture_library/catalog_core.py` | Catálogo de texturas (novo) | componente-novo | LOW | Núcleo puro de RN-01 a RN-04 |
| `caffmob_draw/texture_library/catalog.py` | Catálogo de texturas (novo) | componente-novo | LOW | Leitura do `catalog.json` com cache |
| `caffmob_draw/texture_library/download_core.py` | Downloads (novo) | componente-novo | LOW | Fila, retomada, verificação, recuo e protocolo |
| `caffmob_draw/texture_library/auth_core.py` | Conta CAF Mob (novo) | componente-novo | LOW | Código de dispositivo e sessão |
| `caffmob_draw/library_panel/grid_core.py` | Biblioteca CAFFMob (`library_panel/`), núcleo novo | componente-novo | LOW | Grade, rolagem, retângulo e três estados; ainda não ligado ao desenho |
| `caffmob_draw/textures/catalog.json`, `caffmob_draw/textures/thumbs/**` | Catálogo de texturas (dados do pacote) | delta-de-dados | LOW | 12 fabricantes e 1.209 texturas (T015) |
| `tools/texturas_importar.py` | Ferramenta de desenvolvedor | componente-novo | LOW | Gera catálogo, miniaturas e o pacote do servidor; fora do pacote |
| `caffmob_draw/library_panel/layout_core.py` | Biblioteca CAFFMob, layout (`_reversa_sdd/library_panel/design.md#F-07`) | regra-alterada | LOW | Acrescenta o rótulo com maximizar (opcional, padrão desligado), o layout do retângulo maximizado (`max_layout`, `hit_max`) e as linhas da coluna de filtros; a coluna do estado aberto não muda |
| `caffmob_draw/library_panel/style.py` | Biblioteca CAFFMob, tokens (novo) | componente-novo | LOW | Tokens da direção visual CAFF MOBI DRAW (T006) |
| `caffmob_draw/library_panel/props.py` | Biblioteca CAFFMob, estado de sessão (`_reversa_sdd/library_panel/design.md`) | delta-de-dados | LOW | `mode`, `pinned`, `rect`, `scroll`, `tab` e filtros; `open` passa a ser derivado de `mode` e continua gravável como na 012 |
| `caffmob_draw/library_panel/draw.py` | Biblioteca CAFFMob, desenho (`_reversa_sdd/library_panel/design.md#F-09`) | regra-alterada | MEDIUM | Rótulo e coluna nos tokens CAFF MOBI DRAW (Noite, ícone, botão de maximizar); estado MAX desenhado (cabeçalho, coluna de fabricantes, grade com miniaturas e recorte, rodapé de download). O desenho só lê o estado |
| `caffmob_draw/library_panel/draw_kit.py`, `thumbs_gpu.py` | Biblioteca CAFFMob, desenho (novos) | componente-novo | LOW | Primitivas com o blend religado; miniaturas em `GPUTexture` por timer, sem `Image` no arquivo |
| `caffmob_draw/library_panel/grid_core.py` | Biblioteca CAFFMob, grade | regra-alterada | LOW | Largura mínima do retângulo de 420 para 560 px (cabeçalho completo); célula de 188 px (T006) |
| `caffmob_draw/assets/caffmobi_draw_icon.*`, `caffmob_draw/assets/fonts/Sora-SemiBold.ttf` + `OFL.txt` | Integrações e distribuição | delta-de-dados | LOW | Ícone oficial CAFF MOBI DRAW (SVG do canvas da família CAFF, PNG pelo Inkscape) e a fonte Sora (OFL) no pacote |
| `tools/biblioteca_mocks.py`, `_reversa_forward/014-texturas-fabricantes-grade/mocks/` | Ferramenta de desenvolvedor | componente-novo | LOW | Mocks renderizados da direção visual; fora do pacote |
| `caffmob_draw/operators/viewport_hud.py` | HUD da viewport | regra-nova | LOW | `occupied_rects(context, area)`: botões do HUD, navegador de cenas fixado e aviso de medidas, em pixels da região; o HUD em si não muda (T029) |
| `caffmob_draw/overlays/element_toast.py` | Aviso de medidas do elemento | regra-alterada | LOW | O cálculo do retângulo sai do desenho para `_layout`/`rect`; o aviso continua igual na tela e no tempo (T029) |
| `caffmob_draw/texture_library/downloader.py`, `downloads.py`, `auth.py` | Downloads e conta CAF Mob (novos) | delta-de-contrato-externo | MEDIUM | Primeiro código do plugin que acessa a rede: subprocesso sem `bpy` (download com retomada e sha256, chamadas JSON), ponte por timer no thread principal e login por código de dispositivo; nada sem `bpy.app.online_access` e sem servidor configurado (T020, T021, T023) |
| `caffmob_draw/texture_library/apply.py`, `bump.py` | Aplicar textura (novo) sobre a personalização (`_reversa_sdd/customize/requirements.md#RN-05`) | regra-nova | MEDIUM | Textura do catálogo aplicada a peça, frente, módulo ou objeto; grava na personalização (peça herdada em `btm_custom.material`; armário CAFFMob no grupo "CAIXA" ou em `front_material`); veio pela variante `ROTATED`; relevo do fabricante quando há (T025, T045) |
| `caffmob_draw/texture_library/ops_account.py`, `ops_apply.py`, `handlers.py`, `__init__.py` | Texturas, operadores e handlers (novos) | componente-novo | MEDIUM | Entrar, sair, baixar tudo, cancelar; aplicar à seleção e tamanho real; `load_post` refaz o caminho das imagens para o cache, `load_pre` encerra a rede; `unregister` desfaz tudo (T035, T037, T038, T046) |
| `caffmob_draw/__init__.py` | Preferências e registro | regra-alterada | LOW | `textures_server_url` (vazio até a publicação) e a seção "Conta CAF Mob" nas preferências; registra `texture_library` depois do painel (T036, T038) |
| `caffmob_draw/library_panel/ops_click.py` | Biblioteca CAFFMob, clique (`_reversa_sdd/library_panel/requirements.md#RN-13`, `#RN-14`) | regra-alterada | MEDIUM | Estado MAX: botões, mover, redimensionar, rolagem, abas, filtros, célula que vira arraste; fixo, clique fora segue para a cena sem fechar e Esc não é consumido; categoria abre a grade da aba Blocos em vez do popover (T030, T040) |
| `caffmob_draw/library_panel/ops_search.py`, `ops_drag.py`, `__init__.py` | Biblioteca CAFFMob, busca e arraste (novos) | componente-novo | MEDIUM | Busca digitada ao vivo; arraste de textura (ray-cast e aplicação) e de bloco (modelo pronto no ponto da soltura, módulo salvo pela inserção existente), uma etapa de desfazer (T031, T032, T034) |
| `caffmob_draw/library_panel/draw.py` (rodada 5) | Biblioteca CAFFMob, desenho | regra-alterada | LOW | Grade de blocos com miniatura do módulo salvo, coluna de categorias na aba Blocos, cursor da busca; o estado da célula passa a vir da fila de download (corrige a consulta a uma função inexistente, que escondia o "Baixando") |
| `caffmob_draw/customize/ops_library.py`, `caffmob_draw/object_library/ops.py` | Inserção de módulo salvo e de objeto | regra-alterada | LOW | Propriedade oculta `from_drag`: vinda do arraste, a soltura do botão confirma; por clique, nada muda (T033) |
| `build.py` | Empacotamento | regra-nova | LOW | Exige `textures/catalog.json` e todas as miniaturas listadas; recusa qualquer outro arquivo em `textures/` (imagem em tamanho real) (T039) |
| `caffmob_draw/data/translations/library.json` | Tradução | delta-de-dados | LOW | 61 textos novos com inglês; `tools/i18n_scan.py` sem pendência (T041) |
| `tools/texturas_importar.py` (rodada 5) | Ferramenta de desenvolvedor | regra-alterada | LOW | O manifesto do servidor ganha os 15 relevos como itens `<id>.bump` (1.224 itens) |
| `tests/blender_012_library_ui.py` | Testes da 012 | regra-alterada | LOW | A verificação "categoria abre o popover" virou "categoria abre a grade da aba Blocos" (RN-14 mudou por pedido do titular) |
| `tests/_bootstrap.py` | Infra de testes puros | regra-alterada | LOW | Pacote `texture_library` acrescentado aos stubs |
| `tests/fake_texture_server.py` e `tests/test_*`/`tests/blender_014_*` | Testes | componente-novo | LOW | Servidor falso do contrato, testes puros e provas |

## Diff conceitual por componente

**Biblioteca de objetos, material de imagem.** A RN-17 dizia: material "Textura: <arquivo> <tamanho> mm", projeção em
caixa, escala `1/(mm/1000)` nos três eixos, reaproveitado por caminho e tamanho. Agora:
- o mesmo material aceita largura e altura (escala X pela largura, Y e Z pela altura);
- uma variante de veio, com rotação de 90° e nome `<nome> ROTATED` (a convenção que `common.rotated` já procura);
- o id do catálogo (`btm_texture_id`);
- o reaproveitamento passa a considerar também o veio.

Para quem chama com dois argumentos nada muda: mesmo nome, tamanho gravado como número e mesma escala. Isso está
provado pela `blender_009_library_smoke` e pela `blender_bug_QZSO_object_library`, verdes.

**Biblioteca CAFFMob, layout (T018).** `panel_layout` ganha `with_maximize` (padrão desligado): quem chama como na 012
recebe exatamente o mesmo rótulo e a mesma coluna, como provam `test_library_layout` e a `blender_012_library_ui`,
verdes. As funções novas (`max_layout`, `hit_max`, `sidebar_rows`, `maximize_button`) ainda não são usadas pelo desenho
nem pelo clique, que mudam na Fase 4 (T028, T030).

**Biblioteca CAFFMob, desenho (T026 a T028).** O painel muda de aparência nos estados da 012: o rótulo deixa o azul
`BG_TITLE` e o cinza `BG` pela placa Noite com o ícone CAFF MOBI DRAW, e a coluna aberta ganha o botão de maximizar. O
comportamento (onde fica, ordem dos itens, clique e clique fora) não muda: a `blender_012_library_ui` segue verde. O
estado MAX é desenhado por inteiro, mas só fica alcançável pelo clique na T030. Três achados medidos no Blender 5.2
viraram regra de código:
- o framebuffer do POST_PIXEL tem o tamanho da região, então o recorte usa coordenadas da região e liga o teste de
  scissor;
- a miniatura é convertida fora do desenho, por timer (criar e remover `Image` dentro do desenho não é seguro);
- o `blf` desliga o blend, que é religado em cada primitiva.

**HUD e aviso de medidas (T029).** O HUD passa a responder quais áreas da tela o plugin ocupa: os botões, o navegador de cenas quando fixado e o aviso de medidas enquanto aparece. A biblioteca maximizada usa essa lista para não cobrir nenhuma delas. As cotas de seleção ficam de fora de propósito: acompanham os objetos e fariam o retângulo pular a cada giro da vista. 🟡

**Integrações e distribuição.** O manifesto declara `network`, e agora há código que acessa a rede: o subprocesso de
download e as chamadas da conta. Tudo passa por `downloads.unavailable_reason()`, que barra sem `bpy.app.online_access`
e sem `textures_server_url` (vazio até a publicação). O `build.py` garante que o pacote leva só o catálogo e as
miniaturas.

**Downloads e conta (T020, T021, T023).** Um processo por sessão, iniciado no primeiro uso, encerrado no `unregister`,
no `load_pre` e ao trocar o servidor. Ele fala JSON por linha, e o thread principal lê num timer que só existe
enquanto o processo vive. A sessão fica em `extension_path_user("auth")/session.json` (0600), sem token de acesso e
sem senha. Os comportamentos de rede fixados pelos testes estão no `interfaces/servidor-texturas.md` §7.

**Aplicar textura (T025, T045, T046).** A textura do catálogo usa o mesmo material de imagem da RN-17 e entra pela
mesma função das bibliotecas (`common.set_cutpart_material`). A escolha fica gravada onde a personalização já lê, para
refazer o módulo não desfazer a textura:
- peça das bibliotecas herdadas em `btm_custom.material` (precedência peça > grupo > vão);
- armário CAFFMob na caixa (grupo "CAIXA") ou nas frentes (`front_material`, todas as portas do módulo).
O veio (RN-06, 🟡) supõe o comprimento da peça no eixo X local e o veio da imagem no lado maior: imagem em pé numa
peça usa a variante `ROTATED`.

**Biblioteca CAFFMob, clique, busca e arraste (T030 a T034, T040).** O estado MAX fica alcançável e completo. Duas
regras 🟢 da 012 mudam por pedido do titular:
- RN-13: com o retângulo fixo, o clique fora segue para a cena sem fechar e o Esc não é consumido;
- RN-14: escolher uma categoria abre a grade dela no retângulo (aba Blocos), e não mais o popover, que fica de reserva.
Nos estados MIN e OPEN o clique continua o da 012. As inserções de módulo e de objeto ganham `from_drag` sem mudar o
clique.

**Handlers (T037).** `load_post` aponta as imagens do catálogo para o cache deste computador e avisa uma vez os ids
fora do catálogo instalado. `load_pre` encerra a rede.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` e dos requisitos dos componentes que continuam intactas:
- RN-LIBRARY_PANEL-01: fixas primeiro, categorias do usuário depois, pastas soltas viram COZ.
- `_reversa_sdd/library_panel/requirements.md#RN-16`: o título "BIBLIOTECA CAFFMOB" não passa por tradução.
- `_reversa_sdd/library_panel/requirements.md#RN-15`: o conteúdo do popover não mudou; ele só deixou de ser a rota
  principal (ver Modificadas, RN-14).
- RN-OBJECT_LIBRARY-01, RN-OBJECT_LIBRARY-02 e RN-OBJECT_LIBRARY-03 (a retextura afeta a cena, não a biblioteca).
- `_reversa_sdd/customize/requirements.md#RN-05` (precedência peça > grupo > vão) e `#RN-13` (variante `ROTATED`): a
  aplicação de textura grava e usa exatamente essas convenções.
- Inserção de módulo salvo e de objeto por clique: mesmo comportamento (o `from_drag` só vale vindo do arraste).

## Modificadas

- `_reversa_sdd/object_library/requirements.md#RN-17` (🟢): o material de imagem passa a ter variantes (chapa
  retangular, veio, id do catálogo), mantendo o comportamento antigo para a chamada quadrada. (W001, W002)
- `_reversa_sdd/architecture.md#Integrações e distribuição` (🟢): permissão `network` e código de rede; o pacote não
  leva imagem de fabricante em tamanho real. (W003)
- `_reversa_sdd/library_panel/design.md#F-09` (🟢): o desenho troca as cores da 012 pelos tokens CAFF MOBI DRAW, ganha
  o ícone e o botão de maximizar e desenha três estados. (W004)
- `_reversa_sdd/library_panel/requirements.md#RN-13` e RN-LIBRARY_PANEL-02 (🟢): fixo, o retângulo maximizado não
  fecha com clique fora nem com Esc; o clique fora segue para a cena. Solto, e nos estados MIN e OPEN, vale a regra da
  012. (W005)
- `_reversa_sdd/library_panel/requirements.md#RN-14` e RN-LIBRARY_PANEL-03 (🟢): a categoria abre a grade no
  retângulo maximizado (aba Blocos), com miniatura do módulo salvo; o popover sai da rota principal. (W006)
