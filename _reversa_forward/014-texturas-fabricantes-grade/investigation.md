# Investigação: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`

## 1. A pasta do titular (medida em 2026-10-12)

`/home/theleoinfo/Downloads/materials/textures`: 15.281 arquivos, 3,1 GB, em quatro pastas: `cinex` (221 arquivos),
`fabrica` (8.311), `padroes` (6.649) e `revest` (100).

`fabrica/` tem 127 fabricantes. Os 12 de chapas aceitos (RN-01), com imagens sem relevo:

| Fabricante | Texturas | Coleções | Tamanho |
|------------|---------:|---------:|--------:|
| Arauco | 107 | 8 | 31 MB |
| Berneck | 83 | 10 | 53 MB |
| Duratex | 106 | 16 | 34 MB |
| Eucatex | 106 (+19 arquivos `.bump`) | 2 | 45 MB |
| Fibraplac | 36 | 6 | 11 MB |
| Floraplac | 171 | 11 | 75 MB |
| Formica | 124 (+18 imagens na pasta "Bumps" e 6 arquivos `.bump`) | 11 | 81 MB |
| Greenplac | 156 | 9 | 108 MB |
| Guararapes | 134 | 13 | 85 MB |
| Lopar | 56 | 1 | 23 MB |
| Placas do Brasil | 75 | 12 | 36 MB |
| Sudati | 55 | 6 | 22 MB |
| **Total** | **1.209** | | **~576 MB** |

Observações:
- As coleções são subpastas (Duratex › Design, Arauco › Tons_do_Brasil › Matt). Algumas têm dois níveis; RN-02 usa a
  subpasta de primeiro nível como coleção, e o `catalog_core` registra a subcoleção no nome do item quando ela existir.
- Dimensões amostradas: de 365 × 365 px (Eucatex BP TX Premium) a 1.850 × 2.750 px (Arauco Tons do Brasil). As
  imagens de chapa inteira (1.820 a 1.850 × 2.750 px) batem com as medidas de chapa em mm, o que sustenta 1 px = 1 mm
  (RN-04).
- Relevos: arquivos `<imagem>.jpg.bump` ao lado da imagem (Formica, Eucatex) e uma pasta `Bumps` com imagens PNG/JPG
  e uma legenda `.txt` (Formica). Viram RF-14 (Could).
- A estrutura (fabricante, coleção, `.bump`, `.resources`) é a da biblioteca de texturas do Promob, que o titular já
  usa (princípio II: medir os arquivos com que o projeto conversa).

## 2. O que existe no legado

- **Biblioteca CAFFMob** (`library_panel/`):
  - desenho `POST_PIXEL` sempre ativo (`draw.py:118-120`);
  - layout puro (`layout_core.py`);
  - clique por keymap `head=True` com `PASS_THROUGH` fora do painel (`ops_click.py`);
  - popover nativo de 2 colunas sem miniatura (`popover.py:18-58`).
- **Inserir › Objetos** (`object_library/panels.py:13-46`): é a única grade com miniatura, via
  `template_icon(scale=4.0)` e `bpy.utils.previews` com chave `caminho:mtime` (`previews.py`).
- **Material de imagem** (`object_library/retexture.py:71-94`): `image_material(path, size_mm)`, com projeção em caixa
  sobre coordenadas de objeto, escala `1/(mm/1000)` nos 3 eixos e reaproveitamento por caminho e tamanho. Aplicado
  por `customize/adapters/common.set_cutpart_material`, que já trata a variante "ROTATED" do veio em Stile e Rail.
- **Inserção que segue o mouse**: três rotas.
  - `caffmob.object_insert` (`object_library/ops.py:56-145`, com a região WINDOW resolvida desde o BUG W2DP);
  - `caffmob.module_insert` (`customize/ops_library.py:79-160`, `PlacementMixin` com encaixe e R para girar);
  - `caffmob.library_insert_model` (chama o construtor direto, sem modal).
- **Asset Shelf** (`hb_assets.py:324-340`): registrado, mas sem assets próprios.
- **Código morto** (`catalog/`): navegador antigo com grade, não registrado. Serve só de referência.

## 3. Alternativas avaliadas para a grade e o retângulo

| Alternativa | Atende RN-09 (flutua, move, redimensiona, fixa, não cobre o HUD) | Arrastar bloco do CAFFMob | Arrastar textura até a peça | Custo |
|-------------|------------------------------|---------------------------|-----------------------------|-------|
| **Desenho próprio na viewport (escolhida, D-01)** | Sim: posição e tamanho são nossos | Sim, pela inserção existente | Sim, por ray-cast e `classify` | Alto: rolagem, digitação e miniaturas na GPU |
| Asset Shelf nativo | Não: região presa à borda da área; não fixa nem flutua | Não: só faz append de objeto, não roda o construtor | Parcial: solta material no objeto inteiro, não na peça | Baixo |
| Popover ou painel N nativo | Não: popover fecha ao sair; painel N não flutua sobre a cena | Só por botão, sem arraste | Só por botão | Baixo |
| Janela separada (editor próprio, como o Editor de Paredes) | Parcial: é outra janela, não flutua sobre a cena | Difícil: arraste entre janelas | Difícil | Alto |

## 4. APIs confirmadas no corpus 5.2

- `gpu.texture.from_image(image)`: `docs/rag/blender-api/corpus/gpu.texture.md#gpu.texture.from_image` (reserva de D-05).
- `gpu.types.GPUTexture.__init__(size, *, layers=0, is_cubemap=False, format='RGBA8', data=None)`:
  `docs/rag/blender-api/corpus/gpu.types.md#gpu.types.GPUTexture.__init__`.
- `bpy.types.ImagePreview.image_pixels_float`:
  `docs/rag/blender-api/corpus/bpy.types.ImagePreview.md#bpy.types.ImagePreview.image_pixels_float`.
- `gpu.state.scissor_set(x, y, xsize, ysize)`: `docs/rag/blender-api/corpus/gpu.state.md#gpu.state.scissor_set`.
- Shader builtin `IMAGE`, válido no 5.2: `docs/rag/project/03_compatibilidade_5x.md` (nomes `2D_`/`3D_` não existem).
- `SpaceView3D.draw_handler_add`: `docs/rag/blender-api/corpus/bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.draw_handler_add`.
- `AssetShelf` (avaliado e descartado): `docs/rag/blender-api/corpus/bpy.types.AssetShelf.md`.

## 5. Provas a executar (princípio II)

1. **Prova de D-05, miniatura na GPU.** Carregar 40 miniaturas pela coleção de previews, converter
   `image_pixels_float` em `GPUTexture` e desenhar com o shader `IMAGE` numa janela (`xvfb-run`). Registrar aqui:
   - se os pixels vêm vazios no primeiro acesso;
   - o tempo por miniatura;
   - a memória usada.
2. **Prova de D-07, arraste.** Com `--enable-event-simulate`: pressionar numa célula, mover 20 px e soltar sobre um
   cubo. Para textura, conferir que o material muda só no cubo. Para bloco, conferir que a inserção existente assume
   o mouse e confirma na soltura. Registrar a sequência de eventos recebida pelo modal.

## 6. Resultado das provas

_Pendente: preenchido pelas ações de prova do `actions.md`._
