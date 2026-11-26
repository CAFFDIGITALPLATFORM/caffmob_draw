# Legacy impact: 027

> Data: 2026-11-26
> Feature: `027-janela-plano-corte-e-medicao-malha` (fases 1 a 3 executadas; fases 4 e 5 abertas)
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
