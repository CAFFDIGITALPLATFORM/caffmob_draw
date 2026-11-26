# Changelog do CAFFMob Draw

## 1.35.0 — 2026-11-26

### Paridade restante do Construtor e padrão completo da Biblioteca (026)

- **Toolbar completa** na janela 023: montagem, limpeza, vistas dividida/frontal/lateral, cotas, portas,
  abrir/fechar tudo, **Apenas Laterais**, plano de corte, export JSON, tema e painel lateral (N restaura).
- **Titlebar** com dimensões, contrato de chapas, export e tema; **sete abas em uma linha horizontal**.
- **Export JSON + cutlist** com schema `caffmob.armario.v1`, spec, peças e grupos agregados; o painel de peças
  exporta o mesmo payload.
- **Menu de contexto** (botão direito) com duplicar, medida, espelhar e apagar. A duplicata grava
  `ajustes.duplicada` e **sobrevive ao Gerar**.
- **Popover de medida** (largura/altura/profundidade) e **arraste de peças** por press→move→release, com ajuste
  dx/dy/dz e limite de 3 px para não confundir com clique.
- **Apenas Laterais** liga as duas laterais, desliga base/fundo e gera somente chapas `LATERAL`.
- **Light/Dark** no preview: as cores das peças passam a ser lidas em tempo de desenho; a Biblioteca ganhou tokens
  Dark e botão de tema.
- **Biblioteca**: categorias do documento (**Armários, Portas, Janelas, Armários autorais**), “Armários” com todo o
  acervo, grade de Blocos **2×3** e alvo de toque mínimo de **44 px** no cabeçalho.
- Provas: `blender_026_parity` **23/23**, `blender_025_place` **16/16**, `blender_023_fase7` **36/36**, UI 012
  **9/9**, card **38/38**, puros **109**, i18n **3/3** (36 chaves novas), `check_api.py` 638 arquivos, smoke OK.
- Auditoria 026 em `_reversa_forward/026-paridade-total-construtor-biblioteca/audit/cross-check.md`: 0/0/0/0.

### Como a numeração foi calculada

`1.34.0 + 1 recurso novo de paridade = 1.35.0` (minor).

## 1.34.0 — 2026-11-26

### Criação e posicionamento do armário v2 (025)

- **Criar armário** abre o Construtor v2 direto na Vista 3D, sem criar a janela própria da 023; a janela continua
  disponível por **Abrir Janela**.
- Depois de **Aplicar** — no painel da Vista 3D e no rodapé da janela 023 — a janela pergunta **“Onde adicionar o
  armário?”** com **Escolher na viewport** e **Cursor 3D**. O aviso é agendado para o popup sobreviver ao operador de
  Aplicar.
- **Escolher** oculta o armário real e mostra uma **caixa de arame** de 8 vértices/12 arestas/0 faces, nas medidas do
  spec, acompanhando o mouse no piso. As setas **cima/baixo/esquerda/direita** viram a frente para 0°/90°/180°/270°,
  **R** soma 90°, o **clique** confirma e **Esc/botão direito** restauram posição, giro e visibilidade.
- **Cursor 3D** posiciona a raiz no cursor preservando o giro; as chapas filhas acompanham. Sem viewport, o modo
  Escolher cai no Cursor 3D.
- **Biblioteca**: a galeria de blocos/texturas passa a usar a paleta **Light** do mockup (`#FFFBF5` janela,
  `#FFF8EC` sidebar, `#F5EFE3` card, `#2B1A0E` tinta, `#B45309` primário, `#0E7C74` teal), mantendo abas, busca,
  grade, seleção e filtros.
- Provas: `tests/blender_025_place.py` **16/16** na janela real; `test_placement_025` + `test_library_style_025`
  **7/7**; card **38/38**, UI 012 **9/9**, puros **36**, puros amplos **54**, i18n **3/3** (28 chaves novas nos
  catálogos `armario_v2.json`/`library.json`), smoke 017 OK, `check_api.py` sem API desconhecida.

### Como a numeração foi calculada

`1.33.3 + 1 recurso novo = 1.34.0` (minor, fluxo de criação/posicionamento e aparência da galeria).

## 1.33.3 — 2026-11-26

### Editor de Armário (ensaio 004)

- `tests/blender_004_cabinet_editor_smoke.py` deixou de abrir o editor 2D removido em 021/T027 e passou a provar o
  contrato atual do Construtor v2: guarda do móvel legado, abertura do armário vazio, Montar Caixa, Aplicar e
  Cancelar. O ensaio voltou a **11/11, exit 0** na janela real.
- O card da Biblioteca segue **38/38** e `tests/blender_012_library_ui.py` segue **9/9**; puros e `check_api.py`
  verdes. O A004 do 021 não tem mais ensaio de GUI vermelho.

### Como a numeração foi calculada

`1.33.2 + 1 correção = 1.33.3` (patch, sem recurso novo).

## 1.33.2 — 2026-11-26

### Biblioteca (ensaios de GUI)

- `tests/blender_012_library_ui.py` atualizado ao fluxo atual: a coluna inclui Dormitório e "Criar armário" abre o
  Construtor de Armários v2 (021), deixando o armário ativo, em vez do diálogo antigo; o ensaio voltou a 9/9.
- `tests/blender_biblioteca_detalhe.py` ganhou a recusa específica da chapa máxima, com um padrão temporário de
  600 × 1000 mm: 1200 × 2700 × 900 mm é recusado com mensagem de chapa e nenhuma peça é criada; a prova do card ficou
  38/38, exit 0.
- A captura do card aberto (`biblioteca_detalhe.png`) foi regerada com 550 × 800 × 500 mm em Dormitório.

### Como a numeração foi calculada

`1.33.1 + 1 correção = 1.33.2` (patch, sem recurso novo).

## 1.33.1 — 2026-11-26

### Construtor de Armário v2 (021, T033)

- O painel lateral usava `icon='MOD_LENGTHWISE'`, removido no Blender 5.2; a caixa "Travessas" levantava `TypeError`
  e o painel não terminava de desenhar. Trocado por `MOD_LENGTH` (`armario_v2/panel.py`).
- As sete abas passam a uma grade de 2 colunas (4 linhas), e o título/atalhos e "Montagem"/"Vão ativo" ficam em
  linhas separadas: os rótulos completos do mockup aparecem na largura padrão da barra lateral, sem "Estr..." ou
  "Const...".
- `tests/blender_021_panel_visual.py` captura o painel numa janela real; a comparação com o mockup está em
  `_reversa_forward/021-plano-corte-camadas-gaveteiro/visual-parity.md`.

### Como a numeração foi calculada

`1.33.0 + 1 correção = 1.33.1` (patch, sem recurso novo).

## 1.33.0 — 2026-11-26

### Biblioteca

- Card branco de detalhe do módulo antes de inserir: clicar num módulo da grade abre um card claro com o nome, o
  ambiente, largura, altura e profundidade pré-preenchidos pelo catálogo e pelos padrões do Padrão de Dimensões, mais o
  seletor de ambiente (Cozinha, Banheiro, Dormitório, Sala, Home office) e os botões Inserir e Cancelar
  (`library_panel/detail_core.py`, `library_panel/ops_detail.py`, `library_panel/draw.py`, `library_panel/props.py`).
- Confirmar passa as medidas e o ambiente escolhidos para `caffmob.library_insert_model`, que agora aceita
  `width_mm`/`height_mm`/`depth_mm` e os repassa ao construtor de armários; módulos de preset sem variação continuam
  usando os valores do JSON (`library_panel/popover.py`).
- Arrastar o módulo cujo card está aberto leva as mesmas medidas e o ambiente definidos nele; sem card, o arraste
  mantém o comportamento anterior, com os valores do catálogo (`library_panel/ops_drag.py`, `library_panel/ops_click.py`).
- Validação contra o Padrão de Dimensões: máximos do módulo, faces de chapa (largura × altura, largura × profundidade,
  altura × profundidade) contra a chapa máxima do fornecedor e espessura da lateral. Medida inválida é recusada com
  mensagem no card e nada é criado; o filtro de acervo por ambiente e a galeria do Editor de Armário V2 continuam
  intactos.

### Como a numeração foi calculada

`1.32.0 + 1 feature entregue = 1.33.0`, mantendo a convenção do repositório de uma minor por entrega.

## 1.32.0 — 2026-11-25

Primeiro incremento desde a 1.27.0 (2026-11-23). Entre uma e outra entraram cinco features com código no pacote, sem
que a versão do manifesto acompanhasse — o que este lançamento corrige.

### Entrou desde a 1.27.0

- **020 — Conversão em armário:** leitura da seleção como um móvel, papéis por peça (laterais, bases, fundo e porta),
  armário v2 no envelope das peças, origem não destrutiva e geração sob demanda (`armario_v2/ponte.py`,
  `armario_v2/converter.py`).
- **021 — Plano de corte e camadas:** plano de corte em camadas, coleções de cena organizadas e conversão em gaveteiro
  (`cutting/`, `data/layers.py`).
- **022 — Frente do Mover Sobre:** a frente do objeto passa a ser considerada no encoste e no movimento.
- **023 — Janela do Construtor de Armários:** janela própria com preview frontal e corte lateral, painel de 7 abas,
  fila de pedidos com um passo de desfazer e edição do armário v2 (`armario_v2/window.py`, `canvas2d/`).
- **024 — Materiais, UV e preferência de exibição:** textura MDF clara empacotada, UV por face com veio, preferência
  de exibição por armário e aviso de migração (`armario_v2/mdf_core.py`, `face_uv_core.py`, `exibicao.py`).

### Biblioteca

- Acervo por ambiente: o catálogo de modelos e presets declara `environments` e a grade da Biblioteca mostra só o que
  pertence à categoria aberta (`library_panel/models_core.py`, `library_panel/draw.py`,
  `data/library_models.json`).
- Categoria fixa **Dormitório** (linha `DOR`), que faltava para o acervo de dormitório ficar acessível sem criar
  categoria manual (`library_panel/categories_core.py`).
- Módulos de dormitório, banheiro, sala e escritório no catálogo: roupeiro, cômoda, gabinete e espelheira de banheiro,
  buffet e estante de sala, armário de arquivo.

### Como a numeração foi calculada

`1.27.0 + 5 features entregues (020, 021, 022, 023, 024) = 1.32.0`, mantendo a convenção do repositório de uma minor
por entrega. A 019 (`redimensionar-e-colisao`) continua pausada, com apenas `requirements.md`, e não entra na conta.

## 1.27.0 — 2026-11-23

Textura por UV, veio em graus e conta-gotas por parte (feature 018).
