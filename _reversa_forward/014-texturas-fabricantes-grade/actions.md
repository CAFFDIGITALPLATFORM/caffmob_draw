# Actions: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`
> Roadmap: `_reversa_forward/014-texturas-fabricantes-grade/roadmap.md` (revisão 2, D-01 a D-18)
> Data delta: `_reversa_forward/014-texturas-fabricantes-grade/data-delta.md`
> Interfaces: `interfaces/servidor-texturas.md` (HTTP), `interfaces/catalogo-texturas.md` (arquivo)
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 47 |
| Paralelizáveis (`[//]`) | 20 |
| Maior cadeia de dependência | 11 (T003 → T004 → T005 → T020 → T021 → T023 → T035 → T036 → T038 → T044 → T047) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Prova D-05: script com janela (`xvfb-run`) que carrega 40 PNGs de 256 px por `bpy.utils.previews`, converte `image_pixels_float` em `gpu.types.GPUTexture(size, data=Buffer)` e desenha com o shader `IMAGE` num handler `POST_PIXEL`. Imprime: pixels vazios no primeiro acesso (sim/não), tempo por miniatura e quantos quadros até ficarem prontos; repete pela reserva `bpy.data.images.load` + `gpu.texture.from_image` | - | `[//]` | `tests/blender_014_thumb_probe.py` | 🟡 | `[X]` |
| T002 | Prova D-07: script com janela (`--enable-event-simulate`) com um modal de teste que começa num retângulo desenhado, recebe `LEFTMOUSE` PRESS, `MOUSEMOVE` de 20 px e RELEASE sobre um cubo. Imprime a sequência de eventos, o objeto do ray-cast na soltura e se um `caffmob.object_insert('INVOKE_DEFAULT')` chamado no meio assume o mouse e confirma na soltura | - | `[//]` | `tests/blender_014_drag_probe.py` | 🟡 | `[X]` |
| T003 | Servidor falso do contrato (`interfaces/servidor-texturas.md`) com `http.server`: `/v1/auth/device`, `/auth/token` (pendente, sucesso, `slow_down`), `/auth/refresh` (com rotação), `/auth/logout`, `/me/entitlements`, `/textures/catalog` (ETag), `/textures/<id>/file` (200, 206 com `Range`, 302). Contas, permissões e falhas injetáveis (401 após N, 403, 404, 429 com `Retry-After`, corte no meio do arquivo) por argumentos de linha de comando | - | `[//]` | `tests/fake_texture_server.py` | 🟢 | `[X]` |
| T004 | Prova D-11 e D-12: com o servidor falso, um subprocesso sem `bpy` (`sys.executable`) faz o login por código e baixa uma imagem, escrevendo JSON por linha. O Blender (com janela) lê o pipe num `bpy.app.timers` e mede se a interface redesenha a cada 0,1 s durante o download. Testa o corte com retomada por `Range` e fecha o Blender com o download em andamento, conferindo que não sobra processo | T003 | - | `tests/blender_014_net_probe.py` | 🟡 | `[X]` |
| T005 | Registrar o resultado das provas T001, T002 e T004 em `investigation.md` §6 e confirmar ou trocar as decisões D-05, D-07, D-11 e D-12 (reserva adotada, quando houver) | T001, T002, T004 | - | `_reversa_forward/014-texturas-fabricantes-grade/investigation.md` | 🟡 | `[X]` |
| T006 | Direção visual com `/impeccable` (D-18): cores, tipografia, espaçamento, raio, sombra e estados (hover, selecionado, arrastando, "não baixada", baixando com progresso, erro, login com código). Saída em tokens nomeados para o núcleo de layout, com um mock por estado do painel (minimizado, aberto, maximizado e fixo) | - | `[//]` | `_reversa_forward/014-texturas-fabricantes-grade/design-direction.md` | 🟢 | `[X]` |
| T007 | `.gitignore`: ignorar `dist/texturas-servidor/` e qualquer imagem em `caffmob_draw/textures/` fora de `thumbs/`, mantendo `catalog.json` e `thumbs/**` versionados (D-03) | - | `[//]` | `.gitignore` | 🟢 | `[X]` |
| T008 | Manifesto: `network = "Download manufacturer textures from the CAF Mob server"` em `[permissions]` (D-14) | - | `[//]` | `caffmob_draw/blender_manifest.toml` | 🟢 | `[X]` |
## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Teste puro de `texture_library/catalog_core`: entram só os 12 fabricantes (comparação sem caixa); ficam fora `.bump`, `.bump2`, `.resources`, `.specular`, `.txt` e a pasta `Bumps`; coleção pela subpasta e "Geral" para imagem solta; nome legível ("Carvalho_Avela_Design.jpg" → "Carvalho Avela Design"); id estável com sufixo `-2` em colisão; `size-mm` de chapa inteira (2.750 × 1.850 → 1 px = 1 mm) e padrão de 600 mm no maior lado; relevo `.bump` associado; leitura do `catalog.json` com `schema-version` errada vira catálogo vazio com aviso | - | `[//]` | `tests/test_texture_catalog.py` | 🟢 | `[X]` |
| T010 | Teste puro de `library_panel/grid_core`: colunas pela largura (≥ 4 colunas em 1.920 px); rolagem limitada entre 0 e o fim; acerto de célula com borda e rolagem; retângulo limitado à região visível e fora dos retângulos proibidos do HUD; mover e redimensionar com tamanho mínimo; transições dos três estados (MIN, OPEN, MAX) e fixo | - | `[//]` | `tests/test_library_grid.py` | 🟢 | `[X]` |
| T011 | Teste puro de `texture_library/download_core`: fila sem duplicar id; até 4 paralelos; retomada a partir do tamanho do `.part`; sha256 diferente descarta e tenta uma vez; recuo 2, 4, 8 s para 5xx e `Retry-After` para 429; leitura das linhas JSON do subprocesso (progresso, concluído, erro); cancelamento | - | `[//]` | `tests/test_texture_download.py` | 🟢 | `[X]` |
| T012 | Teste puro de `texture_library/auth_core`: estados do código de dispositivo (pendente, `slow_down` soma 5 s, negado, expirado, sucesso); renovação com rotação do token; 401 na renovação limpa a sessão; formato do `session.json` sem senha nem token de acesso; sessão de outro `server` é ignorada | - | `[//]` | `tests/test_texture_auth.py` | 🟢 | `[X]` |
## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T013 | `catalog_core.py` puro: classificação de RN-01 a RN-04 a partir de uma lista de caminhos e dimensões, ids, `size-mm`, relevo e leitura e validação do `catalog.json` (D-02); passa T009 | T009 | `[//]` | `caffmob_draw/texture_library/catalog_core.py` | 🟢 | `[X]` |
| T014 | Script de desenvolvedor (Blender em segundo plano): lê a pasta do titular, usa `catalog_core`, gera miniaturas de 256 px, escreve `caffmob_draw/textures/catalog.json` com sha256 e bytes, e `dist/texturas-servidor/` (`files/` + `manifest.json`); idempotente e com relatório por fabricante (`interfaces/catalogo-texturas.md`) | T013 | - | `tools/texturas_importar.py` | 🟢 | `[X]` |
| T015 | Rodar a importação com `/home/theleoinfo/Downloads/materials/textures` e conferir 12 fabricantes e 1.209 itens; catálogo e miniaturas prontos para versionar | T014, T007 | - | `caffmob_draw/textures/catalog.json` | 🟢 | `[X]` |
| T016 | `catalog.py`: lê `catalog.json` do pacote uma vez (cache), expõe fabricantes, coleções, itens, busca sem caixa e sem acento e o caminho da miniatura; arquivo ausente vira "Texturas não instaladas" (D-02, D-17) | T013 | - | `caffmob_draw/texture_library/catalog.py` | 🟢 | `[X]` |
| T017 | `grid_core.py` puro: layout da grade, rolagem, acerto, limites do retângulo e desvio dos retângulos proibidos (D-01, D-06, D-11); passa T010 | T010 | `[//]` | `caffmob_draw/library_panel/grid_core.py` | 🟡 | `[X]` |
| T018 | `layout_core.py`: estado minimizado (só o rótulo, como hoje), coluna do estado aberto sem mudança e layout do retângulo maximizado (cabeçalho com maximizar/fixar/minimizar, abas, filtros, busca e área da grade), usando `grid_core` e os tokens de T006 | T017, T006 | - | `caffmob_draw/library_panel/layout_core.py` | 🟡 | `[X]` |
| T019 | `download_core.py` puro: fila, retomada, verificação, recuo e protocolo das linhas JSON (D-11); passa T011 | T011 | `[//]` | `caffmob_draw/texture_library/download_core.py` | 🟢 | `[X]` |
| T020 | `downloader.py`: script **sem `bpy`**, rodado com `sys.executable`; `urllib.request` com `Range`, `.part`, sha256 e rename atômico; não manda `Authorization` em redirecionamento para outro domínio; até 4 downloads paralelos dentro do processo; JSON por linha no stdout; sai quando o stdin fecha | T019, T005 | - | `caffmob_draw/texture_library/downloader.py` | 🟢 | `[X]` |
| T021 | `downloads.py`: ponte no thread principal. Inicia o subprocesso, manda pedidos, lê o pipe sem bloquear num `bpy.app.timers`, guarda o progresso em memória, chama de volta ao concluir, cancela e encerra o processo (D-11) | T020 | - | `caffmob_draw/texture_library/downloads.py` | 🟢 | `[X]` |
| T022 | `auth_core.py` puro: máquina de estados do código de dispositivo, renovação e formato da sessão (D-12, D-13); passa T012 | T012 | `[//]` | `caffmob_draw/texture_library/auth_core.py` | 🟡 | `[X]` |
| T023 | `auth.py`: chamadas de login, renovação e sair pelo subprocesso de rede (sem bloquear a interface); `session.json` em `extension_path_user("auth")` com permissão 0600; token de acesso só em memória; nada é feito sem `bpy.app.online_access` (D-12, D-13, D-14) | T022, T021 | - | `caffmob_draw/texture_library/auth.py` | 🟡 | `[X]` |
| T024 | `image_material(path, width_mm, height_mm, rotated=False)`: escala por eixo no Mapping, variante de veio girada 90°, `btm_texture_id` e `btm_texture_rotated`; a chamada antiga `image_material(path, size_mm)` continua como caso quadrado (D-08) | - | `[//]` | `caffmob_draw/object_library/retexture.py` | 🟢 | `[X]` |
| T025 | `apply.py`: aplicar uma textura do catálogo a um alvo. Se a imagem estiver no cache, cria o material (T024) e aplica por `common.set_cutpart_material`, com a precedência da personalização (RN-05) e o veio pela orientação da peça (RN-06). Se não estiver, enfileira o download (T021) e aplica ao concluir. Sem conta, sem internet ou sem permissão: aviso, nada muda | T016, T021, T024 | - | `caffmob_draw/texture_library/apply.py` | 🟡 | `[X]` |
## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T026 | Estender `BTM_PG_LibraryState` com `mode`, `pinned`, `rect`, `scroll`, `tab`, `manufacturer`, `collection` e `search`; `open` passa a ser derivado de `mode` (data-delta §6, D-10) | T018 | - | `caffmob_draw/library_panel/props.py` | 🟢 | `[X]` |
| T027 | Miniaturas na GPU pelo caminho confirmado em T005: carga só das células visíveis, cache por id e liberação no `unregister` (D-05) | T005, T016 | - | `caffmob_draw/library_panel/thumbs_gpu.py` | 🟡 | `[X]` |
| T028 | `draw.py`: desenhar os três estados, a grade com miniatura e nome, rolagem com `gpu.state.scissor_set`, a marcação "não baixada", o progresso por célula e o estado da conta no cabeçalho, com os tokens de T006 | T026, T027, T006 | - | `caffmob_draw/library_panel/draw.py` | 🟡 | `[X]` |
| T029 | O HUD expõe os retângulos ocupados (HUD, navegação, avisos e cotas de tela) por região, para o painel não cobrir (D-11) | - | `[//]` | `caffmob_draw/operators/viewport_hud.py` | 🟡 | `[X]` |
| T030 | `ops_click.py`: botões maximizar, fixar e minimizar; mover pelo cabeçalho e redimensionar pela borda; rolagem pela roda dentro do retângulo; com o painel fixo, clique fora segue para a cena sem fechar; limites de T029 aplicados | T028, T029 | - | `caffmob_draw/library_panel/ops_click.py` | 🟡 | `[X]` |
| T031 | Busca digitada no retângulo: clique no campo ativa a digitação capturada (letras, Backspace, Enter, Esc), filtro ao vivo pela busca do catálogo (D-17) | T030 | - | `caffmob_draw/library_panel/ops_search.py` | 🟡 | `[X]` |
| T032 | `ops_drag.py`: modal `caffmob.library_drag` para textura. Limiar de 6 px × escala, miniatura sob o cursor, ray-cast e `classify` na soltura, chama `apply` (T025); no vazio, aviso curto; Esc cancela; uma etapa de desfazer (D-07) | T025, T030 | - | `caffmob_draw/library_panel/ops_drag.py` | 🟡 | `[X]` |
| T033 | Inserções existentes aceitam começar a partir de um arraste: propriedade oculta que confirma na soltura do botão em `caffmob.object_insert` e `caffmob.module_insert` (sem mudar o comportamento por clique) | T032 | - | `caffmob_draw/customize/ops_library.py` | 🟡 | `[X]` |
| T034 | `ops_drag.py` para bloco: ao sair do retângulo, chama a inserção do tipo do bloco (modelo pronto pelo construtor, módulo salvo ou objeto) em `INVOKE_DEFAULT` com a origem de arraste de T033 | T033 | - | `caffmob_draw/library_panel/ops_drag.py` | 🟡 | `[X]` |
| T035 | `ops_account.py`: operadores Entrar (mostra o código, abre o navegador, acompanha), Sair (apaga a sessão e avisa o servidor) e Baixar tudo (só com `download_all`, progresso total e cancelar) (RN-11, RN-12, D-15) | T023, T021 | - | `caffmob_draw/texture_library/ops_account.py` | 🟡 | `[X]` |
| T036 | Preferências: `textures_server_url` e a seção "Conta CAF Mob" (e-mail, Entrar/Sair, Baixar tudo, aviso quando o acesso à internet do Blender está desligado) em `BTM_AddonPreferences` (data-delta §5) | T035 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T037 | Handler `load_post` (`@persistent`) que refaz o caminho dos materiais com `btm_texture_id` para o cache do usuário e avisa uma vez os ids fora do catálogo (D-09) | T025 | - | `caffmob_draw/texture_library/handlers.py` | 🟡 | `[X]` |
| T038 | Registrar o pacote `texture_library` (classes, handler, timers) e, no `unregister` e no `load_pre`, encerrar o subprocesso, liberar as texturas GPU e remover handlers e timers (princípio VII) | T027, T035, T037, T036 | - | `caffmob_draw/texture_library/__init__.py` | 🟢 | `[X]` |
| T039 | `build.py`: exige `catalog.json` e todas as miniaturas listadas, e recusa empacotar se houver imagem em tamanho real em `caffmob_draw/textures/` fora de `thumbs/` (D-04) | T015 | `[//]` | `build.py` | 🟢 | `[X]` |
| T040 | O conteúdo da categoria (modelos prontos e módulos salvos) passa para a grade do retângulo com miniatura; o popover sai da rota principal e fica só como reserva para a coluna "Mais…" | T028 | - | `caffmob_draw/library_panel/popover.py` | 🟡 | `[X]` |
| T046 | Ajuste do tamanho real da textura aplicada (RF-06): operador que muda largura e altura em mm do material da peça selecionada, mantendo a proporção por padrão | T025 | - | `caffmob_draw/texture_library/ops_apply.py` | 🟡 | `[X]` |
## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T041 | Textos novos de interface em português com tradução (estados do painel, Texturas, busca, "não baixada", progresso, conta, avisos de rede e de permissão) | T036, T040 | - | `caffmob_draw/data/translations/library.json` | 🟢 | `[X]` |
| T042 | Fumaça com janela do painel: minimizar, abrir, maximizar, fixar e clicar na cena sem fechar, mover e redimensionar, nenhum botão do HUD coberto, ≥ 4 colunas em 1.920 px, rolagem | T030 | `[//]` | `tests/blender_014_panel_smoke.py` | 🟡 | `[X]` |
| T043 | Fumaça com janela do arraste: textura sobre a frente (só a frente muda), sobre a lateral (veio no comprimento), no vazio (aviso, nada muda), Esc (nada), bloco até o piso (insere e um Ctrl+Z remove) | T034 | - | `tests/blender_014_drag_smoke.py` | 🟡 | `[X]` |
| T044 | Integração contra o servidor falso: login por código, sob demanda com progresso, segunda vez sem baixar, retomada após corte, Baixar tudo com e sem permissão, 401 com renovação, 403, `online_access` desligado sem erro, sessão sobrevive a reiniciar, Sair apaga a sessão, nenhum processo órfão | T038 | `[//]` | `tests/blender_014_textures_net.py` | 🟡 | `[X]` |
| T045 | Relevo da textura (RF-14, Could): quando o catálogo tem `bump`, ligar o mapa de relevo ao material no modo de vista com textura | T025 | `[//]` | `caffmob_draw/texture_library/bump.py` | 🟡 | `[X]` |
| T047 | Atualizar `interfaces/servidor-texturas.md` com o que as provas e os testes fixaram (exemplos reais de request e response do servidor falso) e um passo a passo curto para o time do site validar a implementação contra `tests/fake_texture_server.py` | T044 | - | `_reversa_forward/014-texturas-fabricantes-grade/interfaces/servidor-texturas.md` | 🟢 | `[X]` |
## Notas de execução

- Os IDs T046 e T047 foram criados depois dos demais na mesma geração; os números seguem estáveis e não serão
  reciclados.
- T033 toca dois operadores relacionados (`customize/ops_library.py` e `object_library/ops.py`); o arquivo alvo
  indicado é o principal.
- Rodada 1 (2026-10-12):
  - **Feitas:** Fase 1 menos a T006, Fase 2 inteira e os núcleos T013, T014, T015, T016, T017, T019, T022 e T024.
  - **T006 adiada:** precisa do `/impeccable` com o titular (direção visual); é a próxima, porque destrava T018,
    T028 e a parte visual da Fase 4.
  - **Provas:** as três confirmaram o plano (`investigation.md` §6), com dois ajustes para T020/T021 (fim de arquivo
    sem exceção quando a conexão cai e leitura final do pipe) e um para T027 (orçamento de carga por quadro).
  - **T015:** 1.209 texturas de 12 fabricantes, 5 avisos de nome repetido na mesma coleção (resolvidos com sufixo).
    As miniaturas somam 55 MB, e não os ~25 MB estimados no plano. O pacote continua muito abaixo do limite da
    plataforma, mas o roadmap e o data-delta citam a estimativa antiga.
  - **RN-04:** as chapas da Eucatex de 1.820 × 2.750 px ficam fora da faixa de chapa inteira (1.830 a 2.750) e
    recebem o padrão de 600 mm. Vale confirmar com o titular se a faixa deve começar em 1.800.

- Rodada 5 (2026-10-12): T020, T021, T023, T025 e T030 a T047. **As 47 ações estão concluídas.**
  - **Rede:** subprocesso, ponte e conta testados contra o servidor falso (`test_texture_downloader`, 7 cenários;
    `blender_014_textures_net`, 24 verificações). O `textures_server_url` fica vazio até a publicação.
  - **Defeito achado e corrigido:** o desenho consultava `downloads.state_of`, que não existia; o `except` escondia o
    erro e a célula nunca mostraria "Baixando".
  - **Mudanças de regra 🟢 da 012 (pedido do titular):** painel fixo não fecha com clique fora nem Esc (W005);
    categoria abre a grade da aba Blocos em vez do popover (W006). O teste da 012 foi atualizado.
  - **T045 (relevo):** o relevo do fabricante vira item `<id>.bump` no servidor; o importador foi rodado de novo
    (manifesto com 1.224 itens; catálogo do pacote igual).
  - **Fora da cobertura automática:** o arraste de módulo salvo (passagem para `caffmob.module_insert`), as
    preferências desenhadas no Blender com a extensão instalada e o navegador abrindo no login real.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-12 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-12 | Rodada 5 do `/reversa-coding`: todas as ações concluídas | reversa |
