# Roadmap: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`
> Requirements: `_reversa_forward/014-texturas-fabricantes-grade/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature cresce sobre a BIBLIOTECA CAFFMOB que já existe (`library_panel/`, feature 012), desenhada na viewport por
um draw handler `POST_PIXEL` e operada por itens de keymap `head=True`. O painel ganha três estados (minimizado,
aberto, maximizado). O maximizado é um retângulo flutuante, móvel e redimensionável, que pode ser fixado, com uma
grade de miniaturas e rolagem.

As texturas vêm de um catálogo novo (`texture_library/`). Um núcleo puro classifica a pasta do titular e gera um
`catalog.json`. As imagens dos 12 fabricantes e as miniaturas de 256 px vão para o pacote. A aplicação reaproveita o
material de imagem da biblioteca de objetos (`object_library/retexture.image_material`), estendido para chapa
retangular e veio. O arraste é um modal curto que nasce no painel:
- **textura:** ray-cast na soltura e aplicação na peça sob o mouse;
- **bloco:** passa a peça para a inserção que já existe (`caffmob.object_insert`, `caffmob.module_insert`,
  `caffmob.library_insert_model`) já seguindo o mouse.

Duas provas abrem as fases de risco: miniatura na GPU sem poluir `bpy.data`, e arraste do painel para a cena.

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Simples por fora, milimétrico por dentro | Minimizado continua só "BIBLIOTECA CAFFMOB"; a grade mostra imagem e nome; tamanho real, veio e caminhos ficam escondidos | respeita |
| II. Medir antes de cortar | A pasta do titular foi medida (1.209 texturas, 365 a 2.750 px, relevos à parte); duas ações de prova (D-05, D-07) antes do núcleo de UI | respeita |
| III. Nada pregado | Fabricantes aceitos, tamanho padrão (600 mm), faixa de chapa inteira e tamanho da miniatura vêm do catálogo e de constantes nomeadas no núcleo, não espalhados | respeita |
| IV. Cada camada na espessura certa | Núcleos puros novos (`texture_library/catalog_core.py`, `library_panel/grid_core.py`) testáveis fora do Blender; desenho só mostra e despacha | respeita |
| V. Encaixes padronizados | Shader `IMAGE` por `compat.get_builtin_shader()`; a aplicação passa pela API pública `retexture.image_material` e `common.set_cutpart_material` | respeita |
| VI. Chapas padrão | Reaproveita `hb_gpu_draw`, `ops_click`, `classify`, os modais de inserção e o material de imagem existentes | respeita |
| VII. Caixote no esquadro | Coleção de previews, texturas GPU, handlers e keymaps novos removidos no `unregister`; teste próprio por fase | respeita |
| VIII. Fita de borda | Pasta ausente, imagem ilegível, catálogo inválido e textura não instalada viram aviso | respeita |
| IX. Aproveitamento milimétrico | Catálogo lido uma vez e em cache; miniaturas carregadas só para as células visíveis; nada relê o disco a cada redesenho. O pacote cresce cerca de 576 MB, por decisão do titular (RN-07) | respeita, com o custo de tamanho registrado em Riscos |

Nenhum conflito com princípio.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | A grade e o retângulo maximizado são desenhados na viewport, estendendo o `library_panel/` (POST_PIXEL e keymap `head=True` da 012) | RN-09 pede retângulo flutuante, móvel, redimensionável, fixável e que não cubra o HUD; só o desenho próprio controla posição, tamanho e desvio do HUD. Reabre a D-15 da 012 por pedido do titular (RN-08) | Asset Shelf nativo (região fixa na borda da área, sem fixar nem mover, só arrasta asset marcado e não roda o construtor de armário); popover nativo (fecha ao sair do mouse, sem fixar) | 🟡 |
| D-02 | Novo pacote `texture_library/`: `catalog_core.py` puro (classificação de RN-01 a RN-04 a partir de uma listagem de arquivos) e `catalog.py` (lê `catalog.json` do pacote, com cache) | Princípio IV: regra testável sem Blender; o catálogo é dado, não código (princípio III) | Varrer as pastas a cada abertura (lento: o legado relê o disco a cada redesenho, RNF de desempenho) | 🟢 |
| D-03 | Texturas no pacote em `caffmob_draw/textures/<fabricante>/<coleção>/<arquivo>`, com `catalog.json` e `thumbs/<id>.png` (256 px). Um script de desenvolvedor (`tools/texturas_importar.py`, rodado no Blender em segundo plano) copia os 12 fabricantes da pasta do titular, gera as miniaturas e o catálogo | RN-07 (no pacote); miniatura gerada uma vez (RNF de desempenho) | Importar no computador de cada usuário (descartado pelo titular); miniatura gerada em tempo de uso (atrasa a primeira abertura) | 🟢 |
| D-04 | No git ficam só `catalog.json` e `thumbs/` (~25 MB); as imagens originais ficam em `.gitignore`. O `build.py` recusa empacotar se uma imagem do catálogo faltar, como já faz com os `.blend` de nós. Num clone sem as imagens, a área Texturas mostra o aviso "Texturas não instaladas" | O CLAUDE.md não versiona artefatos grandes; o pacote continua completo (RN-07); clone sem imagens não quebra (princípio VIII) | Versionar 576 MB no git (repositório pesado para sempre); Git LFS (dependência e configuração nova sem pedido) | 🟡 |
| D-05 | A miniatura vira `GPUTexture` a partir da coleção `bpy.utils.previews` (`ImagePreview.image_pixels_float`, `docs/rag/blender-api/corpus/bpy.types.ImagePreview.md#bpy.types.ImagePreview.image_pixels_float`), com `gpu.types.GPUTexture(size, data=Buffer)` (`docs/rag/blender-api/corpus/gpu.types.md#gpu.types.GPUTexture.__init__`). Só as células visíveis carregam; cache por id; tudo sai no `unregister`. **Ação de prova antes do núcleo** | Não cria `Image` em `bpy.data` (não suja o arquivo do usuário); custo só do que aparece | `bpy.data.images.load` + `gpu.texture.from_image` (`gpu.texture.md#gpu.texture.from_image`) como reserva, se a prova mostrar pixels vazios no preview | 🟡 |
| D-06 | Rolagem da grade pela roda do mouse dentro do retângulo, com recorte por `gpu.state.scissor_set` (`gpu.state.md#gpu.state.scissor_set`). A coluna de categorias do estado aberto segue a decisão "Mais…" (pergunta 88) | A grade tem centenas de células (Duratex tem 106); sem rolagem não cabe. A pergunta 88 vale para a coluna, não para a grade | Paginação com botões (mais cliques, princípio I) | 🟡 |
| D-07 | O arraste é um modal novo (`caffmob.library_drag`), iniciado quando o botão é pressionado numa célula e o mouse anda mais que um limiar (6 px × escala). **Textura:** desenha a miniatura sob o cursor; na soltura, `scene.ray_cast` resolve o objeto e `classify` resolve a peça, e a textura é aplicada. **Bloco:** ao sair do retângulo, chama a inserção existente em `INVOKE_DEFAULT`, que já segue o mouse e confirma no clique ou na soltura. **Ação de prova antes do núcleo** | RN-10 com as mesmas regras de encaixe da inserção atual (princípio VI); Ctrl+Z de uma etapa vem do `UNDO` dos operadores | Drag-and-drop nativo de asset (não alcança o construtor de armário nem o alvo por peça) | 🟡 |
| D-08 | `retexture.image_material(path, size_mm)` ganha a forma `image_material(path, width_mm, height_mm, rotated=False)`: escala por eixo no Mapping (chapa retangular) e rotação de 90° na variante de veio, mantendo a chamada antiga como caso quadrado | RN-04 e RN-06; uma função só para imagem própria e catálogo (princípio VI) | Função nova paralela (duas fontes de verdade para o material de imagem) | 🟢 |
| D-09 | O material de catálogo guarda `btm_texture_id` (id do catálogo) além de `btm_texture_path`. No `load_post`, materiais com `btm_texture_id` têm o caminho da imagem refeito para a pasta do pacote instalado | O caminho absoluto do pacote muda entre computadores (RNF de portabilidade) | Empacotar a imagem no `.blend` do projeto (faz o arquivo crescer a cada textura usada) | 🟡 |
| D-10 | O estado do painel (modo, posição, tamanho, fixo, rolagem, fabricante, coleção, busca) fica no `WindowManager.btm_library` (sessão), estendendo o PropertyGroup da 012 | RN-09: o estado vale para a sessão e não vai para o arquivo, como hoje | Guardar na cena (vazaria para o arquivo) | 🟢 |
| D-11 | Desvio do HUD: o núcleo `grid_core` recebe os retângulos proibidos (HUD, navegação, avisos) e limita a posição e o tamanho do painel. Os retângulos vêm do `viewport_hud`, que já sabe onde estão os widgets (`click_hits_widget`) | RN-09 e RF-16 sem acoplar o desenho ao HUD (princípio V) | Posições fixas no canto (quebra com outro layout de tela) | 🟡 |
| D-12 | A busca é um campo do retângulo: um clique ativa a digitação, capturada pelo modal do painel (letras, Backspace, Enter, Esc). O filtro é por fabricante, coleção e nome, sem caixa e sem acento | RF-04; sem abrir janela nativa por cima do painel | Popover nativo com campo de texto (fecha ao mover o mouse e cobre o painel) | 🟡 |
| D-13 | A direção visual (cores, tipografia, espaçamento, estados de hover, seleção e arraste) é definida com o fluxo `/impeccable` numa ação própria antes da fase de UI; o núcleo de layout recebe esses valores como constantes nomeadas | Pedido do titular (requirements, RNF de usabilidade) | Desenhar direto no código e ajustar depois | 🟢 |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou aberta no `requirements.md`. Ficam registradas só as premissas técnicas das decisões 🟡,
cada uma coberta por uma ação de prova ou de teste:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| `ImagePreview.image_pixels_float` traz os pixels depois do carregamento sob demanda e vira `GPUTexture` | RNF de desempenho; RN-08 | Usar a reserva de D-05 (imagens em `bpy.data` removidas no `unregister` e antes de salvar) |
| Um modal iniciado no painel consegue passar a inserção para o operador existente e confirmar na soltura | RN-10 | O bloco passa a entrar no clique depois do arraste, e não na soltura (o critério do RF-11 muda) |
| A faixa de 1.830 a 2.750 px identifica as imagens de chapa inteira | RN-04 | Algumas texturas ficam na escala errada até o ajuste manual (RF-06) |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Biblioteca CAFFMob (`library_panel/`) | `_reversa_sdd/architecture.md#Limites e organização`; `_reversa_sdd/library_panel/requirements.md#RN-12` | regra-alterada | Três estados; o maximizado é um retângulo flutuante, móvel, redimensionável e fixável, com grade e rolagem; deixa de ter posição fixa no canto superior esquerdo |
| Layout do painel (`library_panel/layout_core.py`) | `_reversa_sdd/library_panel/design.md#F-07` | regra-alterada | Ganha o layout do retângulo e o desvio do HUD; a coluna do estado aberto não muda |
| Grade (`library_panel/grid_core.py`) | n/a | componente-novo | Núcleo puro: células por largura, rolagem, acerto de célula, limite de posição e tamanho |
| Clique e arraste do painel (`library_panel/ops_click.py`, novo `ops_drag.py`) | `_reversa_sdd/library_panel/requirements.md#RN-13` | regra-alterada | Com o painel fixo, clique fora não fecha; arrastar célula abre o modal de arraste |
| Popover da categoria (`library_panel/popover.py`) | `_reversa_sdd/library_panel/requirements.md#RN-15` | regra-alterada | O conteúdo da categoria passa para a grade do retângulo; o popover sai da rota principal |
| Catálogo de texturas (`texture_library/`) | n/a | componente-novo | `catalog_core` puro, `catalog` com cache, miniaturas na GPU, aplicação da textura |
| Material de imagem (`object_library/retexture.py`) | `_reversa_sdd/object_library/requirements.md#RN-17` | regra-alterada | Escala por eixo, variante de veio e `btm_texture_id`; a chamada antiga continua valendo |
| Inserção existente (`object_library/ops.py`, `customize/ops_library.py`, `library_panel/popover.py:library_insert_model`) | `_reversa_sdd/object_library/requirements.md#RN-14` | contrato-alterado | Aceitam começar a partir de um arraste (confirmação na soltura) |
| HUD (`operators/viewport_hud.py`) | `_reversa_sdd/architecture.md#Fluxos entre componentes` | contrato-novo | Expõe os retângulos ocupados para o painel não cobrir |
| Empacotamento (`build.py`) | `_reversa_sdd/architecture.md#Integrações e distribuição` | regra-alterada | Confere as imagens do `catalog.json` e recusa pacote incompleto |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `catalog.json` novo no pacote;
  - PropertyGroup de sessão `btm_library` estendido;
  - duas propriedades ID novas nos materiais de textura (`btm_texture_id`, `btm_texture_size_mm` como par);
  - nenhuma migração de arquivo de projeto.
- Detalhe completo em: `_reversa_forward/014-texturas-fabricantes-grade/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Pasta de texturas do titular → catálogo do pacote | arquivo | `_reversa_forward/014-texturas-fabricantes-grade/interfaces/catalogo-texturas.md` |

## 8. Plano de migração

1. Projetos antigos não mudam: materiais "Textura: …" sem `btm_texture_id` continuam com o caminho que já tinham.
2. O estado do painel é de sessão: a primeira abertura depois de atualizar o plugin começa minimizada, na posição da
   012.
3. O desenvolvedor roda `tools/texturas_importar.py` uma vez para trazer as imagens. O `build.py` passa a exigir as
   imagens antes de gerar o ZIP.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Pacote com cerca de 576 MB: download e instalação lentos; limite de tamanho na plataforma de extensões | médio | médio | Medir o ZIP final; se passar de um limite da plataforma, reabrir com o titular a recompressão (JPG qualidade 85) ou um pacote de texturas à parte |
| Pixels do preview vazios no primeiro desenho (carregamento sob demanda) | médio | médio | Ação de prova de D-05; redesenho quando os pixels chegam; reserva por `bpy.data.images` |
| Desenhar centenas de miniaturas por quadro deixa a viewport lenta | médio | baixo | Só as células visíveis; texturas GPU em cache; batch por célula; meta de 60 quadros com 40 células visíveis |
| O arraste interfere na seleção nativa e no keymap do HUD | alto | médio | Prova de D-07 com eventos simulados; o keymap só captura o evento quando ele cai no painel |
| Textura de chapa inteira na escala errada (faixa de RN-04) | baixo | médio | RF-06 (ajuste por textura); teste com as amostras medidas |
| Clone sem as imagens (D-04) | baixo | alto | Aviso claro na área Texturas; `build.py` recusa empacotar |
| Material com caminho do pacote quebrado em outro computador | médio | médio | D-09 refaz o caminho no `load_post`; teste de salvar e abrir |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Provas de D-05 (miniatura na GPU) e D-07 (arraste para a cena) registradas em `investigation.md`
- [ ] Direção visual definida com `/impeccable` (D-13) antes da fase de UI
- [ ] Testes puros de `catalog_core` e `grid_core` e fumaças com janela do arraste e do retângulo fixo passando
- [ ] `ruff check caffmob_draw/` limpo e `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
- [ ] `build.py` gera o ZIP com as 1.209 texturas e recusa quando falta alguma
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-12 | Versão inicial gerada por `/reversa-plan` | reversa |
