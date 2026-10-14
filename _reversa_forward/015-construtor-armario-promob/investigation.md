# Investigation: 015-construtor-armario-promob

> Pesquisa de fundo do plano. As fontes primárias são os vídeos do Construtor de Armários do Promob, com as legendas,
> os prints e as notas em `inputs/` (índice: `inputs/README.md`), e o código do pacote `caffmob_draw/`.

## 1. Por que balcão, aéreo e torre saem iguais hoje

Levantamento no código em 2026-10-14, com confirmação nos trechos citados:

- **A malha não recebe o tipo.** `generate_cabinet_mesh(obj, w, h, d, t, shelves, structure, back_setback,
  assembly)` (`caffmob_draw/geometry/mesh_gen.py:246`) monta sempre LEFT, RIGHT, BOTTOM, TOP e BACK com as contas de
  `cabinet_editor/structure.layout` (`structure.py:93-120`). Não existe rodapé, sarrafo nem travessa na malha.
- **O tipo só escolhe medidas.** `standards/cabinet_defaults.py:22-32` (`FALLBACK`, `EXTERNAL`) dá altura,
  profundidade e Z por tipo. `operators/cabinet_builder.py:92-93` só sobe o aéreo para `found.z`.
- **O corte também ignora o tipo.** `cutting/part_sources.py:217` (`synthetic_records`) deduz laterais, bases, fundo,
  uma prateleira e as portas sem olhar o tipo.
- **Contraste com as outras bibliotecas.** Elas já constroem por tipo:
  - frameless: `create_base_carcass` com rodapé e travessas, `create_tall_carcass`, `create_upper_carcass`
    (`product_libraries/frameless/types_frameless.py:125, 315, 457`);
  - face frame: o solver decide rodapé e travessas pelo tipo (`solver_face_frame.py:79, 82`).

## 2. O que o Promob faz (resumo das notas)

| Achado | Evidência |
|---|---|
| O construtor começa por "Selecione uma estrutura de caixa para iniciar a construção", com abas Cozinhas, Cozinhas - Portas Embutidas, Dormitórios e Salas | `prints/Or7qXPijqLA-0049-construtor-tipos-de-estrutura.jpg` |
| Cada estrutura tem a sua lista de componentes marcados | `notas-grupo-a.md#2` |
| O balcão "Inferior c/ Divisória" tem Laterais, Divisória, Base Inferior, Sarrafo Frontal e Sarrafo Traseiro; não tem Base Superior | `prints/L6TMT6wV-xs-0040-inferior-c-divisoria-sarrafos-15mm.jpg` |
| O roupeiro "Armário" tem Base Inferior, Base Superior e Rodapés; 2500 de altura com 2384 de vão interno | `prints/-nGTqK7rTto-0122-aba-estrutura-componentes.jpg` |
| Montagem e fundo ficam numa configuração nomeada, separada para Inferior, Superior e Despenseiro | `prints/jtEjP6DrzpM-0025-*`, `-0041-*` |
| Largura do vão = (L − (N+1)·e)/N | 6 casos em `notas-grupo-a.md#5` e `notas-grupo-b.md#2.2` |
| Porta de correr é um conjunto sobre a caixa inteira, com três sistemas | `notas-grupo-b.md#2.4` |
| Gaveta: folgas A a H, fundo de 6, corrediça escolhida em Modelos | `notas-grupo-c.md#3` |

## 3. Alternativas avaliadas

| # | Alternativa | Prós | Contras | Veredito |
|---|---|---|---|---|
| A | **Receita de estrutura em JSON + `carcass_parts` único** (escolhida) | Estrutura nova sem código; 3D e corte de uma fonte só; legado intocado | Esquema novo para manter e validar | Escolhida (D-01, D-02) |
| B | Reusar as carcaças do frameless (`create_*_carcass`) | Já existem rodapé e travessas | Outra biblioteca (HB5), com drivers e prompts; o editor 008 e o corte do `btm` não leem essa estrutura; trazê-la acopla duas pilhas | Descartada |
| C | Uma função Python por tipo no `mesh_gen` | Simples para 3 tipos | 20 ou mais estruturas viram 20 funções; o corte duplica a conta; contraria o princípio III | Descartada |
| D | Galeria como diálogo `UILayout` com `template_icon_view` | Pouco código | Sem a identidade CAFF MOBI (contraria Q3 a); miniaturas como PNG fixo | Descartada |
| E | Converter os módulos antigos no `load_post` | Projeto fica uniforme | Muda o plano de corte de projeto orçado ao abrir (contraria Q2 a) | Descartada |

## 4. Padrões aplicáveis no repositório

- **Catálogo como dado + núcleo puro que valida e avisa:** `library_panel/models_core.py` (012) e
  `texture_library/catalog_core.py` (014).
- **Atributo do CAFF no XML do Promob:** `CAFF_MONTAGEM` em `standards/io_promob.py:61`; o Promob ignora o ID
  desconhecido.
- **Painel desenhado na GPU com tokens da marca:**
  - `library_panel/style.py`, `draw_kit.py`, `grid_core.py` e `draw.py`;
  - a fonte Sora em `assets/fonts/Sora-SemiBold.ttf`, carregada com `blf.load` (`draw.py:35, 283`).
- **Árvore de componentes com caixa de marcar:** `cabinet_editor/catalog.py:149` (`TREE`) e `btm_structure.extras`.
- **Peças reais filhas da raiz:** `CabinetPart` (`scene_parts.py`), para internos e divisões (RN-CABINET_EDITOR-11).

## 5. API do Blender a confirmar no RAG antes de codar

| Uso | Símbolo | Onde conferir |
|---|---|---|
| Desenho da galeria | `bpy.types.SpaceView3D.draw_handler_add` (`POST_PIXEL`) e remoção em todos os caminhos | `docs/rag/project/02_padroes_blender_5_2.md` (modal+GPU) |
| Cache das miniaturas | `gpu.types.GPUOffScreen`, `gpu.state.scissor_set` | `python3 docs/rag/tools/rag_search.py --symbol gpu.types.GPUOffScreen` |
| Fonte | `blf.load`, `blf.size`, `blf.draw` | `rag_search.py --symbol blf.load` |
| Propriedade nova | `bpy.props.StringProperty(update=...)`; leitura por atributo, nunca `obj["..."]` | `docs/rag/project/03_compatibilidade_5x.md` |

## 6. Fontes externas

- Vídeos e playlists: `inputs/README.md#Vídeos` (24 vídeos, 2 fora do escopo).
- Identidade CAFF MOBI: canvas "CAFF Digital — Família de Ícones", artboard "Família de produtos CAFF", card CAFF MOBI
  (`inputs/README.md#Design de referência`).
- Direção visual já aprovada pelo titular para a GPU: `_reversa_forward/014-texturas-fabricantes-grade/design-direction.md`.
