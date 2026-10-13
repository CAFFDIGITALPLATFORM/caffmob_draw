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

- `bpy.app.online_access`: `docs/rag/blender-api/corpus/bpy.app.md#bpy.app.online_access` (D-14).
- `bpy.app.timers.register(function, *, first_interval=0, persistent=False)`:
  `docs/rag/blender-api/corpus/bpy.app.timers.md#bpy.app.timers.register` (ponte do subprocesso, D-11).
- Threads: `docs/rag/project/04_armadilhas.md#Threads`. Thread Python com Blender rodando derruba o programa;
  trabalho independente vai para subprocesso com JSON, e o resultado é aplicado no thread principal. Isso decide D-11.

## 4.1 Onde guardar as texturas (revisão 2, 2026-10-12)

Levantamento sobre a plataforma de extensões do Blender (extensions.blender.org):
- O limite de upload começou em 10 MB, em 2024, e foi aumentado. A referência mais recente aponta cerca de 200 MB,
  e pacotes de 213 MB e de 750 MB foram rejeitados com o erro 413. Não há documento oficial com o número.
- A plataforma só aceita conteúdo compatível com a GPL. As imagens dos fabricantes não são GPL, então não podem ir no
  pacote publicado lá, seja qual for o tamanho.
- O ZIP instalado por "Install from Disk" não tem esse limite. Mas um pacote de 600 MB obrigaria o usuário a baixar
  tudo de novo a cada atualização de código.

Fontes:
- https://projects.blender.org/infrastructure/extensions-website/pulls/8
- https://projects.blender.org/infrastructure/extensions-website/issues/130
- https://projects.blender.org/infrastructure/extensions-website/issues/222
- https://projects.blender.org/infrastructure/extensions-website/issues/328
- https://extensions.blender.org/about/

Decisão do titular: modelo híbrido (RN-07). Catálogo e miniaturas no pacote; imagens no servidor da CAF Mob.

## 4.2 Login da conta CAF Mob

| Alternativa | Senha passa pelo Blender | Suporta login social e 2FA do site | Complexidade no plugin | Escolha |
|-------------|--------------------------|-------------------------------------|------------------------|---------|
| **Código de dispositivo (OAuth 2.0 Device Authorization Grant, RFC 8628)** | Não | Sim, tudo acontece no navegador | Baixa: pedir código, abrir navegador, consultar | D-12 |
| Usuário e senha no plugin | Sim (campo de propriedade, histórico de desfazer, memória) | Não | Baixa | Descartada (RNF de segurança) |
| Redirecionamento para um servidor local (loopback, `127.0.0.1:<porta>`) | Não | Sim | Média: servidor HTTP local dentro do Blender e porta livre | Reserva, se o site não suportar o código de dispositivo |

Referência: RFC 8628, https://www.rfc-editor.org/rfc/rfc8628.

## 4.3 Rede sem travar o Blender

| Alternativa | Toca `bpy` fora do thread principal | Dependência nova | Escolha |
|-------------|--------------------------------------|------------------|---------|
| **Subprocesso com o Python do Blender (`sys.executable`), `urllib.request`, JSON por linha, timer lendo o pipe** | Não | Nenhuma | D-11 |
| Thread Python com `urllib` | Risco (guia do projeto proíbe thread viva com Blender) | Nenhuma | Descartada |
| `requests` em wheel | Não, mas pede subprocesso do mesmo jeito | Wheel a mais | Descartada |

## 5. Provas a executar (princípio II)

1. **Prova de D-05, miniatura na GPU.** Carregar 40 miniaturas pela coleção de previews, converter
   `image_pixels_float` em `GPUTexture` e desenhar com o shader `IMAGE` numa janela (`xvfb-run`). Registrar aqui:
   - se os pixels vêm vazios no primeiro acesso;
   - o tempo por miniatura;
   - a memória usada.
2. **Prova de D-07, arraste.** Com `--enable-event-simulate`: pressionar numa célula, mover 20 px e soltar sobre um
   cubo. Para textura, conferir que o material muda só no cubo. Para bloco, conferir que a inserção existente assume
   o mouse e confirma na soltura. Registrar a sequência de eventos recebida pelo modal.
3. **Prova de D-11 e D-12, conta e download.** Com o servidor falso (`tests/fake_texture_server.py`):
   - código de dispositivo até a sessão gravada em 0600;
   - download de uma imagem pelo subprocesso, com o timer aplicando o resultado e a interface respondendo durante o
     download (redesenho a cada 0,1 s);
   - corte da conexão no meio do download e retomada com `Range`;
   - fechar o Blender com o download em andamento sem deixar processo órfão.
   Registrar aqui os tempos e o comportamento.

## 6. Resultado das provas (2026-10-12, Blender 5.2.0 LTS, `xvfb-run`)

### Prova de D-05, miniatura na GPU (`tests/blender_014_thumb_probe.py`, T001): confirmada

`PROVA_D05 {'A': {'prontas': 40, 'vazias_no_1o_acesso': 0, 'redesenhos': 1, 'ms_por_miniatura': 23.69,
'tamanho': (256, 256), 'images_em_bpy_data': 0}, 'B': {'prontas': 40, 'ms_por_miniatura': 1.86,
'images_em_bpy_data': 40}}`

- **Caminho A (escolhido):** `bpy.utils.previews` → `image_pixels_float` → `GPUTexture`. As 40 miniaturas ficam
  prontas logo no primeiro acesso, sem pixels vazios, e nenhum `Image` é criado em `bpy.data`. D-05 está mantida.
- **Custo:** cerca de 24 ms por miniatura, quase tudo na cópia dos pixels para o `Buffer` em Python. A reserva (B) é
  mais rápida (1,9 ms), mas cria 40 imagens no arquivo do usuário.
- **Consequência para a T027:**
  - carregar no máximo um orçamento de cerca de 8 ms por quadro (2 ou 3 miniaturas) e redesenhar até completar as
    visíveis;
  - copiar os pixels com `foreach_get` num `array('f')` em vez de fatiar a lista, para reduzir o custo;
  - nada de carregar as 1.209 de uma vez.

### Refinamento de D-05 na T027 (`tests/blender_014_thumbs_gpu.py`)

A medição com as miniaturas reais (256 px) mostrou duas coisas:
- pelos previews, o custo é de cerca de 25 ms por miniatura, mesmo com `foreach_get`: o peso está na decodificação,
  não na cópia;
- carregando a `Image` com `bpy.data.images.load`, copiando os pixels para um `GPUTexture` próprio e removendo a
  `Image` na mesma conversão, o custo cai para cerca de 9 ms, e nenhuma `Image` fica no arquivo.

A T027 usa essa segunda via. Como criar e remover data-blocks dentro do callback de desenho não é seguro, a conversão
roda num timer fora do desenho, com orçamento de 8 ms por chamada, e pede o redesenho. Resultado: 40 miniaturas em
0,96 s, e cada chamada fica em 11 ms.

### Prova de D-07, arraste (`tests/blender_014_drag_probe.py`, T002): confirmada

`PROVA_D07 {'textura': {'atingido': 'Cube', 'eventos': 7, 'release_recebido': True, 'cor_aplicada': True},
'bloco': {'insert_invocado': True, 'mousemove_no_insert': 2, 'release_no_insert': True, ...}}`

- **Textura:** o modal que nasce no retângulo recebe os `MOUSEMOVE` e a soltura (`LEFTMOUSE RELEASE`); o ray-cast na
  soltura acerta o objeto sob o mouse.
- **Bloco:** um segundo modal chamado em `INVOKE_DEFAULT` de dentro do primeiro, que termina em seguida, recebe os
  `MOUSEMOVE` seguintes e a soltura do mesmo botão. A passagem para a inserção existente (D-07) funciona.
- **Cuidado para a T033:** o `event` que chega no `invoke` do segundo modal não é o evento corrente (veio como
  `LEFTMOUSE RELEASE`). A inserção iniciada por arraste não deve ler o evento do `invoke`; ela confirma no primeiro
  `LEFTMOUSE RELEASE` recebido no `modal`.

### Prova de D-11 e D-12, conta e download em subprocesso (`tests/blender_014_net_probe.py`, T004): confirmada

`PROVA_D11 {'login': True, 'retomada': True, 'hash_ok': True, 'redesenhos': 38, 'maior_intervalo_s': 0.066,
'tempo_total_s': 1.87, 'sai_ao_fechar_stdin': True}`

- **Login:** o código de dispositivo funciona contra o servidor falso (`tests/fake_texture_server.py`).
- **Download:** 4 MB, com corte da conexão na metade. A retomada com `Range` completa o arquivo, e o sha256 confere
  antes do rename.
- **Interface:** enquanto o subprocesso baixa, a vista redesenha a cada 0,05 s, com no máximo 0,066 s entre quadros.
  O timer no thread principal não trava. D-11 está mantida.
- **Sem processo órfão:** o subprocesso termina sozinho quando o stdin fecha, que é o que acontece quando o Blender
  sai.
- **Duas lições para T020 e T021:**
  - quando o servidor corta a conexão, o `read` devolve fim de arquivo sem exceção. O worker precisa comparar o
    tamanho baixado com o esperado e tratar a diferença como queda (retomar);
  - depois que o subprocesso termina, a ponte precisa esvaziar o pipe numa leitura final, senão as últimas mensagens
    (como `done`) se perdem.
- **Ambiente:** a primeira execução da prova travou no `xvfb-run` antes de qualquer subprocesso (colisão de display
  virtual). As execuções seguintes rodaram normalmente. Não é efeito do código.
