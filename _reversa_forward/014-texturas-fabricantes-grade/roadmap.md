# Roadmap: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12` (revisão 2: armazenamento híbrido com servidor CAF Mob)
> Requirements: `_reversa_forward/014-texturas-fabricantes-grade/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature cresce sobre a BIBLIOTECA CAFFMOB que já existe (`library_panel/`, feature 012), desenhada na viewport por
um draw handler `POST_PIXEL` e operada por itens de keymap `head=True`. O painel ganha três estados (minimizado,
aberto, maximizado). O maximizado é um retângulo flutuante, móvel, redimensionável e fixável, com uma grade de
miniaturas e rolagem.

As texturas seguem o modelo **híbrido** (RN-07):
- o pacote leva só o catálogo e as miniaturas de 256 px;
- as imagens em tamanho real ficam no servidor da CAF Mob e vão para a pasta do usuário da extensão quando usadas, ou
  todas de uma vez no modo offline (RN-12);
- o acesso exige a conta CAF Mob (RN-11), por um login que abre o navegador e nunca passa a senha pelo Blender;
- a rede roda num **subprocesso** cujo progresso o thread principal lê por timer, sem threads tocando `bpy`.

A aplicação reaproveita o material de imagem da biblioteca de objetos (`object_library/retexture.image_material`),
estendido para chapa retangular e veio. O arraste é um modal curto que nasce no painel.

Esta feature define o contrato HTTP do servidor (RN-14). Os testes rodam contra um servidor falso local, porque o
site ainda não publicou o serviço.

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Simples por fora, milimétrico por dentro | Minimizado continua só "BIBLIOTECA CAFFMOB"; grade com imagem e nome; download, sessão e caminhos ficam escondidos; o login é um código e um botão | respeita |
| II. Medir antes de cortar | Pasta do titular medida (1.209 texturas); limite da plataforma de extensões levantado; três ações de prova (D-05, D-07, D-12) antes do núcleo | respeita |
| III. Nada pregado | Endereço do servidor nas preferências; fabricantes aceitos e tamanhos padrão no catálogo; tempos de espera em constantes nomeadas | respeita |
| IV. Cada camada na espessura certa | Núcleos puros novos (`catalog_core`, `grid_core`, `download_core`, `auth_core`) testáveis fora do Blender; desenho só mostra e despacha; o subprocesso não importa `bpy` | respeita |
| V. Encaixes padronizados | Shader `IMAGE` por `compat.get_builtin_shader()`; aplicação pela API pública `retexture.image_material` e `common.set_cutpart_material`; contrato HTTP versionado (`/v1`) | respeita |
| VI. Chapas padrão | Reaproveita `hb_gpu_draw`, `ops_click`, `classify`, os modais de inserção, o material de imagem e o padrão subprocesso + timer já usado no projeto | respeita |
| VII. Caixote no esquadro | Previews, texturas GPU, handlers, keymaps, timers e subprocessos encerrados no `unregister` | respeita |
| VIII. Fita de borda | Sem internet, sessão expirada, 401/403/404/5xx, download interrompido e arquivo corrompido viram aviso, nunca erro Python | respeita |
| IX. Aproveitamento milimétrico | Catálogo lido uma vez; miniaturas só das células visíveis; download só do que é usado; arquivo baixado conferido por hash e nunca baixado de novo | respeita |

Nenhum conflito com princípio.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | A grade e o retângulo maximizado são desenhados na viewport, estendendo o `library_panel/` (POST_PIXEL e keymap `head=True` da 012) | RN-09 pede retângulo flutuante, móvel, redimensionável, fixável e que não cubra o HUD; só o desenho próprio controla isso. Reabre a D-15 da 012 por pedido do titular (RN-08) | Asset Shelf nativo (região presa na borda, sem fixar nem flutuar, não roda o construtor); popover nativo (fecha ao sair do mouse) | 🟡 |
| D-02 | Novo pacote `texture_library/`: `catalog_core.py` puro (RN-01 a RN-04 a partir de uma listagem de arquivos) e `catalog.py` (lê o `catalog.json` do pacote, com cache) | Princípio IV; o catálogo é dado (princípio III) | Varrer pastas a cada abertura (o legado relê o disco a cada redesenho) | 🟢 |
| D-03 | Um script de desenvolvedor (`tools/texturas_importar.py`, no Blender em segundo plano) gera, a partir da pasta do titular, **duas saídas**: (a) `caffmob_draw/textures/catalog.json` + `thumbs/` (no pacote e no git, ~25 MB); (b) `dist/texturas-servidor/` com as imagens em tamanho real e um `manifest.json` (sha256 e bytes por id), pronto para subir ao servidor, **fora** do pacote e do git | RN-07 (híbrido); miniatura gerada uma vez (RNF de desempenho) | Imagens no pacote (descartado na sessão 2) | 🟢 |
| D-04 | O `build.py` exige o `catalog.json` e todas as miniaturas, e **recusa** empacotar se encontrar imagem em tamanho real dentro de `caffmob_draw/textures/` | Garante RF-01 ("o pacote não contém imagem em tamanho real") e o limite e a regra GPL da plataforma | Confiar na disciplina manual | 🟢 |
| D-05 | A miniatura vira `GPUTexture` a partir de `bpy.utils.previews` (`ImagePreview.image_pixels_float`, `docs/rag/blender-api/corpus/bpy.types.ImagePreview.md#bpy.types.ImagePreview.image_pixels_float`) com `gpu.types.GPUTexture(size, data=Buffer)` (`gpu.types.md#gpu.types.GPUTexture.__init__`); só as células visíveis carregam; cache por id. **Ação de prova** | Não cria `Image` em `bpy.data` | `bpy.data.images.load` + `gpu.texture.from_image` como reserva | 🟡 |
| D-06 | Rolagem da grade pela roda do mouse dentro do retângulo, com recorte por `gpu.state.scissor_set` (`gpu.state.md#gpu.state.scissor_set`); a coluna do estado aberto segue o "Mais…" (pergunta 88) | A grade tem centenas de células | Paginação com botões (mais cliques) | 🟡 |
| D-07 | Arraste por um modal novo (`caffmob.library_drag`), disparado ao pressionar numa célula e mover mais que 6 px × escala. **Textura:** ray-cast e `classify` na soltura, depois aplicação (passando por D-11 se a imagem não estiver baixada). **Bloco:** ao sair do retângulo, chama a inserção existente em `INVOKE_DEFAULT`, que segue o mouse e confirma. **Ação de prova** | RN-10 com as regras de encaixe atuais (princípio VI) | Drag-and-drop nativo de asset (não alcança o construtor nem a peça) | 🟡 |
| D-08 | `retexture.image_material(path, size_mm)` passa a `image_material(path, width_mm, height_mm, rotated=False)`: escala por eixo e variante de veio; a chamada antiga vira o caso quadrado | RN-04, RN-06; uma função só (princípio VI) | Função paralela | 🟢 |
| D-09 | O material de catálogo guarda `btm_texture_id`. No `load_post`, o caminho da imagem é refeito para o **cache do usuário** (`extension_path_user("textures")`); se a imagem não estiver baixada, o material fica e a textura entra na fila sob demanda na próxima vez que for usada | O caminho muda entre computadores (RNF de portabilidade) | Empacotar a imagem no `.blend` do projeto | 🟡 |
| D-10 | Estado do painel na sessão (`WindowManager.btm_library` estendido) | RN-09 | Guardar na cena | 🟢 |
| D-11 | **Download em subprocesso**: `texture_library/downloader.py` é um script sem `bpy`, rodado com o Python do Blender (`sys.executable`) por `subprocess.Popen`. Usa `urllib.request` com retomada (`Range`), grava em `<arquivo>.part`, confere sha256 e renomeia atômico. Fala JSON por linha no stdout (progresso, concluído, erro). O thread principal lê sem bloquear num `bpy.app.timers.register` (`docs/rag/blender-api/corpus/bpy.app.timers.md#bpy.app.timers.register`) e aplica o resultado. Um processo por fila, com até 4 downloads paralelos dentro dele | `docs/rag/project/04_armadilhas.md#Threads`: thread com Blender rodando derruba; trabalho independente vai para subprocesso, com o resultado aplicado no thread principal. A biblioteca padrão dispensa dependência nova | Thread Python (proibida pelo guia do projeto); wheel `requests` (dependência a mais sem ganho) | 🟢 |
| D-12 | **Login por código de dispositivo** (OAuth 2.0 Device Authorization Grant, RFC 8628): o plugin pede um código ao servidor, mostra o código e abre o navegador na página da CAF Mob; o projetista entra lá e o plugin recebe a sessão (token de acesso curto + token de renovação). A senha nunca passa pelo Blender. **Ação de prova** com o servidor falso | RN-11 e o RNF de segurança ("a senha nunca é gravada"); funciona com login social e 2FA do site sem mudar o plugin | Usuário e senha num campo do plugin (a senha passaria pelo Blender e pelo histórico de desfazer das propriedades) | 🟡 |
| D-13 | Sessão guardada em `extension_path_user("auth")/session.json`, com permissão 0600: token de renovação, validade e e-mail da conta, nunca a senha. O token de acesso fica só em memória. "Sair" apaga o arquivo e avisa o servidor | RN-11; RNF de segurança | Chaveiro do sistema operacional (dependência nativa por plataforma, fora do Python do Blender) | 🟡 |
| D-14 | Antes de qualquer acesso, `bpy.app.online_access` (`docs/rag/blender-api/corpus/bpy.app.md#bpy.app.online_access`) precisa ser verdadeiro; senão a área Texturas mostra o aviso de RN-13. O manifesto ganha `network` em `[permissions]` | Regra das extensões do Blender e RNF de rede | Acessar a rede sem checar (bloqueado pela plataforma) | 🟢 |
| D-15 | O "Baixar tudo" consulta `GET /v1/me/entitlements` e só é oferecido com `download_all: true`; baixa pela mesma fila de D-11, com progresso total e cancelamento | RN-12, RF-19 | Liberar para qualquer conta | 🟢 |
| D-16 | Contrato HTTP definido aqui (`interfaces/servidor-texturas.md`), versionado em `/v1`. Os testes usam um **servidor falso** local (`tests/fake_texture_server.py`, `http.server` da biblioteca padrão) que atende o contrato; o endereço vem das preferências (`textures_server_url`) | RN-14; o site ainda não publicou o serviço | Esperar o site ficar pronto (bloqueia a feature) | 🟢 |
| D-17 | Busca no retângulo por digitação capturada pelo modal do painel; filtro por fabricante, coleção e nome, sem caixa e sem acento | RF-04 | Popover com campo de texto | 🟡 |
| D-18 | Direção visual (cores, tipografia, espaçamento, estados de hover, seleção, arraste, "não baixada", progresso e login) definida com `/impeccable` numa ação própria antes da fase de UI | Pedido do titular (requirements, RNF de usabilidade) | Desenhar direto no código | 🟢 |

## 4. Premissas

Nenhuma `[DÚVIDA]` aberta no `requirements.md`. Premissas técnicas das decisões 🟡, cada uma com ação de prova ou
teste:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| `ImagePreview.image_pixels_float` traz os pixels e vira `GPUTexture` | RNF de desempenho; RN-08 | Usar a reserva de D-05 |
| O modal do painel passa a inserção para o operador existente e confirma na soltura | RN-10 | O bloco entra no clique depois do arraste (muda o critério do RF-11) |
| O site da CAF Mob vai implementar o fluxo de código de dispositivo (D-12) e o contrato de D-16 | RN-11, RN-14 | Trocar o login por outro fluxo do contrato; o plugin isola o login em `auth_core` |
| A faixa de 1.830 a 2.750 px identifica as imagens de chapa inteira | RN-04 | Ajuste manual (RF-06) |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Biblioteca CAFFMob (`library_panel/`) | `_reversa_sdd/architecture.md#Limites e organização`; `_reversa_sdd/library_panel/requirements.md#RN-12` | regra-alterada | Três estados; o maximizado é flutuante, móvel, redimensionável e fixável, com grade e rolagem |
| Layout do painel (`library_panel/layout_core.py`) | `_reversa_sdd/library_panel/design.md#F-07` | regra-alterada | Layout do retângulo e desvio do HUD |
| Grade (`library_panel/grid_core.py`) | n/a | componente-novo | Núcleo puro: células, rolagem, acerto, limites |
| Clique e arraste (`library_panel/ops_click.py`, novo `ops_drag.py`) | `_reversa_sdd/library_panel/requirements.md#RN-13` | regra-alterada | Painel fixo não fecha ao clicar fora; arrastar célula abre o modal |
| Popover da categoria (`library_panel/popover.py`) | `_reversa_sdd/library_panel/requirements.md#RN-15` | regra-alterada | O conteúdo da categoria passa para a grade |
| Catálogo de texturas (`texture_library/catalog_core.py`, `catalog.py`) | n/a | componente-novo | Classificação e leitura do catálogo do pacote |
| Downloads (`texture_library/download_core.py`, `downloader.py`, `downloads.py`) | n/a | componente-novo | Fila, retomada e hash (núcleo puro), subprocesso sem `bpy` e ponte por timer |
| Conta (`texture_library/auth_core.py`, `auth.py`, `ops_account.py`) | n/a | componente-novo | Código de dispositivo, sessão em disco, renovação e sair |
| Material de imagem (`object_library/retexture.py`) | `_reversa_sdd/object_library/requirements.md#RN-17` | regra-alterada | Escala por eixo, veio e `btm_texture_id`; caminho no cache do usuário |
| Inserção existente (`object_library/ops.py`, `customize/ops_library.py`, `library_insert_model`) | `_reversa_sdd/object_library/requirements.md#RN-14` | contrato-alterado | Aceitam começar a partir de um arraste |
| HUD (`operators/viewport_hud.py`) | `_reversa_sdd/architecture.md#Fluxos entre componentes` | contrato-novo | Expõe os retângulos ocupados |
| Preferências (`__init__.py`, `BTM_AddonPreferences`) | `_reversa_sdd/architecture.md#Persistência e unidades` | regra-alterada | `textures_server_url` e a seção Conta CAF Mob |
| Manifesto (`blender_manifest.toml`) | `_reversa_sdd/architecture.md#Integrações e distribuição` | regra-alterada | `network` em `[permissions]` |
| Empacotamento (`build.py`) | `_reversa_sdd/architecture.md#Integrações e distribuição` | regra-alterada | Exige catálogo e miniaturas; recusa imagem em tamanho real no pacote |
| Servidor CAF Mob (externo) | n/a | contrato-novo | Login por código, sessão, catálogo, download com `Range`, permissões |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `catalog.json` no pacote, com sha256 e bytes por item;
  - `manifest.json` do servidor;
  - PropertyGroup de sessão `btm_library` estendido;
  - preferências `textures_server_url`;
  - arquivos de usuário `auth/session.json` e o cache `textures/` com `.part`;
  - propriedades ID nos materiais;
  - nenhuma migração de projeto.
- Detalhe completo em: `_reversa_forward/014-texturas-fabricantes-grade/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Servidor de texturas da CAF Mob (login, sessão, catálogo, download, permissões) | HTTP | `_reversa_forward/014-texturas-fabricantes-grade/interfaces/servidor-texturas.md` |
| Pasta de texturas do titular → catálogo do pacote e pacote do servidor | arquivo | `_reversa_forward/014-texturas-fabricantes-grade/interfaces/catalogo-texturas.md` |

## 8. Plano de migração

1. Projetos antigos não mudam: materiais "Textura: …" sem `btm_texture_id` continuam como imagem própria.
2. O estado do painel é de sessão: a primeira abertura depois de atualizar começa minimizada.
3. O desenvolvedor roda `tools/texturas_importar.py` uma vez. Versiona catálogo e miniaturas, e entrega
   `dist/texturas-servidor/` para quem publica no servidor da CAF Mob.
4. Enquanto o site não publica o serviço, `textures_server_url` aponta para um servidor provisório que siga o mesmo
   contrato. Sem servidor, a grade funciona e as texturas aparecem como "não baixada".

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| O site da CAF Mob demora a publicar o serviço | alto | alto | Contrato fechado nesta feature; servidor falso nos testes; endereço configurável para servidor provisório; a grade e o arraste de blocos não dependem do servidor |
| Token de renovação exposto em disco | alto | baixo | Arquivo 0600 na pasta do usuário da extensão; token revogável no servidor; "Sair" apaga e revoga; nunca no `.blend` nem em logs |
| Subprocesso órfão ao fechar o Blender ou desligar a extensão | médio | médio | `unregister` e `load_pre` encerram o processo; o processo sai sozinho se o stdin fechar |
| Download corrompido ou pela metade usado como textura | médio | baixo | `.part` + sha256 + rename atômico; arquivo final só existe se o hash conferir |
| Pixels do preview vazios no primeiro desenho | médio | médio | Prova de D-05; reserva por `bpy.data.images` |
| Arraste interfere na seleção nativa e no keymap do HUD | alto | médio | Prova de D-07 com eventos simulados |
| Pacote passar do limite da plataforma | baixo | baixo | Só catálogo e miniaturas (~25 MB); `build.py` mede e recusa imagem em tamanho real |
| Limite de requisições do servidor no "Baixar tudo" | médio | médio | No máximo 4 em paralelo; recuo progressivo ao receber 429 e 5xx |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Provas de D-05, D-07 e D-12 registradas em `investigation.md`
- [ ] Direção visual definida com `/impeccable` (D-18) antes da fase de UI
- [ ] Testes puros de `catalog_core`, `grid_core`, `download_core` e `auth_core`; testes de integração contra o servidor falso (login, download sob demanda, retomada, baixar tudo, 401, 403, sem internet); fumaças com janela do arraste e do retângulo fixo
- [ ] `ruff check caffmob_draw/` limpo e `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
- [ ] `build.py` gera um ZIP sem nenhuma imagem em tamanho real, com catálogo e 1.209 miniaturas
- [ ] `interfaces/servidor-texturas.md` entregue ao time do site
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-12 | Versão inicial gerada por `/reversa-plan` (texturas no pacote) | reversa |
| 2026-10-12 | Revisão 2: modelo híbrido com servidor CAF Mob, conta por código de dispositivo, download em subprocesso, contrato HTTP | reversa |
