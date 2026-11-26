# Legacy impact: 027

> Data: 2026-11-26
> Feature: `027-janela-plano-corte-e-medicao-malha` (fases 1 a 8 executadas; matriz 14/14)
> Política de edição do legado: `allowLegacyEdits: true`, `allowedPaths: ["***", "caffmob_draw/*", "tests/*"]`
> (liberação irrestrita na prática: `***` casa com qualquer arquivo da raiz e `caffmob_draw/*`/`tests/*` com os pacotes).

## 1. Arquivos afetados

| Arquivo | Componente (`architecture.md`) | Tipo | Severidade | Justificativa |
|---------|-------------------------------|------|------------|---------------|
| `caffmob_draw/promob/cameras.py` | Promob / câmeras | regra-alterada | HIGH | Coleção única `CAMERAS` e câmera sem Empty nem Track To: o alvo virou ponto guardado (`btm_camera_alvo`) com migração do Empty antigo |
| `caffmob_draw/__init__.py` | Preferências do add-on | regra-nova | LOW | `espessura_aresta` (0,2 px) e `aplicar_em_todos` (ligada); nenhuma preferência existente mudou de tipo |
| `caffmob_draw/overlays/arestas.py` | Camada de desenho (`gpu`) | componente-novo | MEDIUM | Handler `POST_VIEW` que desenha as arestas pretas com a espessura da preferência, com cache por objeto invalidado pelo depsgraph |
| `caffmob_draw/overlays/__init__.py` | Camada de desenho | regra-alterada | LOW | `arestas` entra em `_MODULES`; `register`/`unregister` seguem simétricos |
| `caffmob_draw/ui/view_mode.py` | Interface lateral / modo de vista | regra-alterada | HIGH | A vista não liga mais `overlay.show_wireframes`; o interruptor Linhas agora vale para o desenho próprio, e trocar o modo redesenha as vistas |
| `caffmob_draw/ui/view_mode_core.py` | Interface lateral / modo de vista | regra-alterada | HIGH | `settings` devolve `show_wireframes: False` e `edges`; `THRESHOLD`/`OPACITY` deixaram de existir |
| `caffmob_draw/armario_v2/exibicao.py` | Armário v2 / exibição | regra-alterada | LOW | Só a documentação do módulo; o mecanismo (`btm_view_mode` + `btm_view_lines`) continua o mesmo |
| `caffmob_draw/target/multi_apply.py` | Alvo da seleção | componente-novo | HIGH | Leitura e escrita das quatro medidas na seleção múltipla, com a mesma régua do painel |
| `caffmob_draw/target/resolver.py` | Alvo da seleção | delta-de-dados | MEDIUM | `Target.multi_sizes` novo; `multi_thickness` continua, agora derivado dele |
| `caffmob_draw/target/snapshot.py` | Alvo da seleção | regra-alterada | MEDIUM | `_with_multi` passou a montar as quatro medidas em vez de só a espessura |
| `caffmob_draw/target/adapters/other.py` | Alvo da seleção | regra-alterada | MEDIUM | A seção “Comuns aos selecionados” mostra largura, altura, profundidade e espessura |
| `caffmob_draw/target/ops.py` | Alvo da seleção | regra-nova | MEDIUM | `caffmob.target_multi_apply`: diálogo de confirmação e aplicação em todos num passo de Desfazer |
| `caffmob_draw/ui/object_properties.py` | Janela de propriedades | regra-alterada | HIGH | `multi_width/height/depth/thickness` são `StringProperty` (vazio com `?` quando diverge), com confirmação e dica no hover |
| `caffmob_draw/data/translations/027_arestas_multiplos.json` | i18n | regra-nova | LOW | 13 chaves com `pt_BR` e `en_US` |
| `tests/blender_010_view_mode_smoke.py`, `tests/blender_024_exibicao.py`, `tests/blender_024_visual.py`, `tests/test_view_mode.py`, `tests/blender_067_onda1_tipos.py` | Provas | regra-alterada | MEDIUM | As provas passaram a cobrir o novo contrato (arestas próprias, campo vazio, confirmação) |

## 2. Diff conceitual por componente

**Câmeras.** Uma coleção só (`CAMERAS`), com cor de etiqueta aleatória e adoção das câmeras soltas; a coleção antiga
`Câmeras do Promob` é reaproveitada, não duplicada. Nenhuma câmera cria Empty nem Track To: o alvo é um ponto guardado
na câmera e a orientação é feita por código; cenas antigas migram na primeira leitura.

**Modo de vista.** O interruptor Linhas deixou de pedir o wireframe ao Blender (cor do tema, espessura fixa). Quem
desenha é `overlays/arestas.py`, em preto, com `lineWidth` vindo de `espessura_aresta`; “Somente textura” desliga o
interruptor e nada é desenhado (sem aresta e sem vértice). O `color_type` da vista continua sendo `TEXTURE`.

**Seleção múltipla.** As propriedades de item leem a medida de cada selecionado: valor comum aparece escrito na
unidade do projeto; valores diferentes deixam o campo vazio com `?`. Editar pede confirmação
(“Você está prestes a aplicar transformação em todos os objetos ativos: Confirma?”), aplica em todos de uma vez e
gasta **um** passo de Desfazer. A preferência desligada aplica só no objeto ativo.

## 3. Preservadas

- Fluxo 025 (Criar → Aplicar → Escolher/Cursor 3D, caixa de arame, setas, clique, Esc): `blender_025_place` OK.
- Paridade 026 (toolbar, export, titlebar, abas, menu, medida, arraste, cutlist, Apenas Laterais, Light/Dark,
  Biblioteca): `blender_026_parity` OK e `blender_023_fase7` 36/36.
- Biblioteca 012 e detalhe: OK no Blender do Windows.
- Modo de vista gravado no arquivo e reaplicado no `load_post` (010): OK.
- Câmeras: `blender_cameras_colecao` 27/27.

## 4. Modificadas

- “Linhas liga o wireframe do Blender com limiar 0,5 e opacidade 0,6” → “Linhas desenha arestas pretas próprias com a
  espessura da preferência; o wireframe do Blender fica desligado”.
- “Seleção múltipla só mostra a espessura e aplica direto” → “mostra as quatro medidas, fica vazia com `?` quando
  diverge, e aplica com confirmação num passo de Desfazer”.
- “Câmera usa Empty alvo e restrição Track To” → “câmera aponta por código para um ponto guardado nela”.

## 6. Rodada T009–T014: janela do plano de corte e V-Ray Mesh Measure

> Data: `2026-11-26` · Fases 4 a 8 executadas · Matriz fechada (14/14)

| Arquivo | Componente (`architecture.md`) | Tipo | Severidade | Justificativa |
|---------|-------------------------------|------|------------|---------------|
| `caffmob_draw/ui/panels.py` | Barra lateral / Produção › Plano de corte | regra-alterada | HIGH | O botão de destaque passou a abrir a janela (`caffmob.cut_plan_window`); o cálculo antigo ficou como “Recalcular Plano de Corte” e continua no caminho (provas e inventário da barra lateral dependem dele) |
| `caffmob_draw/cutting/plan_window.py` | Produção / janela do plano de corte | componente-novo | HIGH | Janela própria no padrão de `canvas2d/window.py`: handler `POST_PIXEL`, painéis da categoria `Plano de Corte`, modal de navegação, operadores de chapa/zoom/recálculo/fechar |
| `caffmob_draw/cutting/plan_window_core.py` | Produção / geometria do plano | componente-novo | MEDIUM | Núcleo puro: achata as faixas do otimizador em retângulos, enquadra a chapa, hit test, aproveitamento e rótulos |
| `caffmob_draw/cutting/plan_render.py` | Produção / prévia em RGBA | regra-nova | LOW | Aliás público `module_color` para a janela usar a mesma cor por módulo dos rasters e do SVG (nenhuma função mudou) |
| `caffmob_draw/cutting/__init__.py` | Produção / registro do pacote | regra-alterada | LOW | `plan_window` entra no `register`/`unregister` |
| `caffmob_draw/mesh_measure/core.py` | Medição de malha / núcleo | componente-novo | MEDIUM | Partes soltas (componentes conexos), medidas, unidades absoluta/arredondada, snap, medidas manuais e leiaute das folhas |
| `caffmob_draw/mesh_measure/camera.py` | Medição de malha / câmera orbital | componente-novo | MEDIUM | Câmera orbital com yaw/pitch, perspectiva e ortográfica, enquadrar e pan |
| `caffmob_draw/mesh_measure/scene.py` | Medição de malha / leitura da malha | componente-novo | HIGH | Fotografia da malha em coordenadas de mundo (partes, triângulos, materiais) e a sessão da janela, sem tocar no objeto do usuário |
| `caffmob_draw/mesh_measure/draw.py` | Medição de malha / desenho | componente-novo | MEDIUM | Cinco representações, sombreado por degraus, medidas por parte e manuais, folha de impressão com views e badges |
| `caffmob_draw/mesh_measure/window.py` | Medição de malha / janela | componente-novo | HIGH | Janela, modal, conta-gotas na Vista 3D, seletor de malha e os painéis (camadas, medidas, unidades/snap, impressão) |
| `caffmob_draw/__init__.py` | Registro do add-on | regra-alterada | LOW | `mesh_measure` entra no hot-reload, na importação e no `register`/`unregister` |
| `caffmob_draw/data/translations/027_plano_corte.json` | i18n | regra-nova | LOW | 39 chaves com `pt_BR` e `en_US` |
| `caffmob_draw/data/translations/027_medicao_malha.json` | i18n | regra-nova | LOW | 84 chaves com `pt_BR` e `en_US` |
| `tests/blender_027_plano_corte.py` | Provas | componente-novo | LOW | 29 verificações do núcleo e do registro da janela do plano |
| `tests/blender_027_medicao_malha.py` | Provas | componente-novo | LOW | 81 verificações da medição (partes, câmera, snap, unidades, representações, impressão, operadores) |
| `tests/blender_027_janelas.py` | Provas | componente-novo | LOW | 18 verificações com janela real: abrir, desenhar, trocar representação, montar a folha e fechar |

### Diff conceitual

**Plano de corte.** A extração das peças, o otimizador (`cutting/nesting.py`) e o cache da cena
(`btm_nesting_json_cache`) continuam a fonte do plano; o que mudou é a apresentação. `caffmob.cut_plan_window`
calcula o plano quando falta cache ou quando `cut_plan_stale` está ligado e abre uma janela própria com desenho em
GPU: chapa, refilo tracejado, peças coloridas por módulo com nome e medidas, aproveitamento no rodapé e navegação por
roda/arraste/setas. O painel lateral lista as chapas, as peças da chapa atual, o resumo e as exportações que já
existiam. O operador antigo (`caffmob.calculate_nesting`) não foi removido: virou “Recalcular Plano de Corte”, e a
janela usa a mesma função de cálculo (`operators/ops_cutting.calculate`).

**V-Ray Mesh Measure.** Pacote novo, isolado do resto do add-on: lê a malha uma vez em coordenadas de mundo, separa as
partes soltas pelas arestas, mede a caixa de cada uma e desenha numa janela própria. Nada é escrito na cena além da
chave `btm_mesh_measure_target` (o nome da última malha medida, para o projeto lembrar). Nenhum modificador, camada ou
material do usuário é tocado: as representações são só desenho.

### Preservadas

- O fluxo 025 (criar armário abre a viewport; Aplicar pergunta Escolher/Cursor 3D) e a paridade 026 (toolbar, export,
  titlebar, abas, menu, medida, arraste, cutlist, Apenas Laterais, Light/Dark) continuam: `blender_025_place` 16/16 e
  `blender_026_parity` 23/23 nesta rodada.
- O motor OpCut (`cutting/opcut_core.py`, `plan_export.py`, `ops_opcut.py`) e suas exportações HTML/SVG/PDF seguem
  intocados; `blender_021_mcp_e2e` 52/52, incluindo a prévia RGBA e o painel.
- As arestas pretas e as medidas da seleção múltipla (T004–T008) não mudaram nesta rodada.
- O inventário da barra lateral continua fechado (`blender_005_sidebar_inventory` OK): nenhum operador antigo perdeu
  caminho e o novo não duplica seção.

### Modificadas

- A entrada do plano de corte: quem pede o plano na barra lateral recebe a janela, não só o cálculo. O aviso de plano
  desatualizado, o resumo e as exportações continuam os mesmos, agora também dentro da janela.
- `cutting.plan_render` ganhou o nome público `module_color`; a função privada e o raster continuam iguais.
