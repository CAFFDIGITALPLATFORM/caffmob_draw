# Direção visual: BIBLIOTECA CAFFMOB (T006, feature 014)

> Data: `2026-10-12` · Decisão do titular: brief confirmado, "mais marca CAFF" com a identidade **CAFF MOBI DRAW** e
> Sora no título.
> Fonte da marca: canvas "CAFF Digital — Família de Ícones" (artboard "Família de produtos CAFF", card CAFF MOBI
> DRAW).
> Gerador dos mocks: `tools/biblioteca_mocks.py`, desenho real na GPU do Blender 5.2 (`GPUOffScreen`), com as
> miniaturas reais do catálogo.

## 1. Direção

- **Estratégia de cor:** contida, com a marca presente. As superfícies vêm da família **Noite** da CAFF MOBI DRAW,
  translúcidas sobre a cena. O **laranja CAFF** fica só para seleção, ação principal e o ícone. Teal, azul e vermelho
  são reservados a estados, e todo estado vem sempre também em texto (PRODUCT.md, "Accessibility").
- **Cena:** projetista na loja ou no escritório, monitor grande, Blender no tema escuro, cena 3D cinza-clara. O painel
  é uma placa escura e calma que flutua sem roubar a atenção do modelo; a marca aparece no cabeçalho e na seleção.
- **Referências:** catálogo do Promob (fabricante › coleção › acabamento), Asset Browser do Blender (grade com nome e
  arraste para a cena) e painel de assets do Figma (busca no topo, densidade, seções recolhíveis).

## 2. Tokens

Cores em RGBA (0 a 1) para o desenho na GPU; o hex é a referência.

| Token | Hex | RGBA | Uso |
|-------|-----|------|-----|
| `surface` | `#10302F` | (0.063, 0.188, 0.184, 0.96) | Fundo do painel (Noite, 96%) |
| `surface_raised` | `#16403E` | (0.086, 0.251, 0.243, 0.98) | Cabeçalho, coluna de filtros |
| `surface_hover` | `#1F5250` | (0.122, 0.322, 0.314, 1.0) | Hover de célula e de linha |
| `surface_sunken` | `#0B2322` | (0.043, 0.137, 0.133, 1.0) | Fundo da miniatura, busca, chip da conta |
| `border` | branco 10% | (1, 1, 1, 0.10) | Bordas e divisórias |
| `border_strong` | branco 22% | (1, 1, 1, 0.22) | Campo ativo, botão secundário |
| `text` | `#EEF4F2` | (0.933, 0.957, 0.949, 1) | Texto principal (12,7:1 sobre `surface`) |
| `text_muted` | `#C9D6D2` | (0.788, 0.839, 0.824, 1) | Texto secundário (9,4:1) |
| `text_subtle` | `#93ADA8` | (0.576, 0.678, 0.659, 1) | Contagens, "Não baixada", placeholder (5,9:1) |
| `accent` | `#F07A2A` | (0.941, 0.478, 0.165, 1) | Seleção (borda de 2 px), aba ativa, ação principal, fixar ligado |
| `accent_ink` | `#10302F` | (0.063, 0.188, 0.184, 1) | Texto sobre o laranja (5,1:1) |
| `accent_tint` | `#F07A2A` 18% | (0.941, 0.478, 0.165, 0.18) | Linha selecionada na coluna de filtros; fundo do botão fixar ligado |
| `success` | `#1BB3AD` | (0.106, 0.702, 0.678, 1) | "Baixada", conta conectada |
| `info` | `#5BC0FF` | (0.357, 0.753, 1.0, 1) | Progresso, aviso de rede, espera do login |
| `error` | `#FF6B5E` | (1.0, 0.420, 0.369, 1) | "Falhou · tentar de novo" (fora da paleta CAFF; quente e legível no Noite) |
| `cream`, `orange`, `blue_spark` | `#FFF4EA`, `#D35400`, `#2EA8F5` | | Só no ícone CAFF MOBI DRAW |

**Tipografia.**

| Token | Tamanho | Fonte | Uso |
|-------|---------|-------|-----|
| `small` | 10 px | fonte da interface do Blender (`blf` 0) | Contagens, linha de estado da célula, rótulo "Fabricantes" |
| `label` | 11 px | Blender | Rótulo "BIBLIOTECA CAFFMOB", nomes de textura, chip da conta, busca |
| `body` | 12 px | Blender | Abas, coluna de filtros, botões, mensagens |
| `title` | 14 px | **Sora SemiBold** (`blf.load`, licença OFL, arquivo e `OFL.txt` no pacote) | Só o título "Biblioteca" e títulos de estado vazio |
| `code` | 22 px | monoespaçada do Blender (`blf` 1) | Código de dispositivo do login |

Tudo multiplicado pela escala da interface (`preferences.system.ui_scale`), como o painel atual.

**Espaços, raios e tempos.**

| Grupo | Valores |
|-------|---------|
| Espaçamento | `xs` 4 · `sm` 8 · `md` 12 · `lg` 16 · `xl` 24 px |
| Raio | painel 8 · célula 6 · controle 5 · chip 10 px |
| Medidas do maximizado | cabeçalho 36 · coluna de filtros 180 · célula 140 × 188 (miniatura 140, nome em até 2 linhas, linha de estado) · espaço 8 · rodapé de download 28 px |
| Sombra | 5 camadas de 3 px, alfa de 0,045 a 0,01, deslocada 3 px para baixo (quase imperceptível; separa a placa da cena) |
| Tempo | hover 120 ms; abrir e fechar 160 ms com saída exponencial, ou instantâneo; sem animação decorativa |

## 3. Regras

1. **Laranja só onde há decisão:** borda da célula selecionada, aba ativa, botão principal ("Abrir o navegador") e
   fixar ligado. Nada de laranja em estado inativo.
2. **Estado em texto, sempre.** A linha de estado da célula diz "Baixada", "Não baixada", "Arraste para aplicar" (no
   hover), "Baixando 62%" ou "Falhou · tentar de novo". O selo no canto (nuvem, check, alerta) é reforço, nunca a
   única pista.
3. **Seleção na coluna de filtros por fundo** (`accent_tint`), sem tarja lateral colorida.
4. **Nomes com até 2 linhas**, cortados com reticências; a linha de estado vem logo abaixo do nome.
5. **Rolagem com recorte** (`gpu.state.scissor_set`) na área da grade: nenhuma célula invade o cabeçalho ou o rodapé.
6. **O painel não cobre o HUD:** nos mocks, o botão "Navegar" do HUD fica sempre visível (RN-09, RF-16).
7. **Ícones em traço** de 1,3 a 1,8 px, todos do mesmo desenho: fixar, minimizar, fechar, maximizar, buscar, nuvem,
   check, alerta, setas e sem rede.

## 4. Mocks (`mocks/`)

| Arquivo | Estado |
|---------|--------|
| `00-tokens.png` | Folha de tokens: cores, tipografia e ícone |
| `01-minimizado.png` | Minimizado: só o rótulo com o ícone, à direita do HUD |
| `02-aberto.png` | Aberto: coluna de categorias (Texturas como categoria), botão de maximizar no rótulo |
| `03-maximizado-texturas.png` | Maximizado e fixo, Duratex › Design. Células em todos os estados (baixada, hover, selecionada, não baixada, baixando 62%, erro), coluna de filtros com contagens, rodapé de download e conta conectada |
| `04-login-conta.png` | Conta desconectada: código de dispositivo, "Abrir o navegador", "Cancelar" e "Aguardando a confirmação no navegador…" |
| `05-arrastando.png` | Arraste: célula de origem esmaecida, miniatura sob o cursor, a porta de destino destacada em laranja e o rótulo "Soltar na porta: Carvalho Avela Design" |
| `06-vazio-sem-internet.png` | Sem internet (faixa azul) e busca sem resultado, com "Limpar busca" |

## 5. Notas para a implementação (T018, T028)

- **O `blf` desliga o blend ao desenhar texto.** Toda primitiva translúcida (retângulo, linha, imagem) precisa de
  `gpu.state.blend_set('ALPHA')` antes de desenhar, senão sai opaca. Isso foi descoberto no mock, onde a sombra virou
  uma moldura preta.
- **Ícone CAFF MOBI DRAW:** no mock, ele é redesenhado em geometria e fica serrilhado a 16–20 px. No plugin, usar um
  PNG gerado do SVG oficial (64 e 128 px) carregado como `GPUTexture` pela mesma via das miniaturas (D-05).
- **Sora:** vai para `caffmob_draw/textures/fonts/` (ou `assets/fonts/`) junto com o `OFL.txt`, é carregada uma vez
  por `blf.load` e descarregada no `unregister` (`blf.unload`).
- **Grade:** a célula passa a 140 × 188, e `library_panel/grid_core.CELL_H` já foi atualizado para 188 nesta ação.
- **Contraste (calculado, WCAG):**

  | Texto | `surface` | `surface_raised` | `surface_hover` |
  |-------|-----------|------------------|-----------------|
  | `text` | 12,7 | 10,3 | 7,9 |
  | `text_muted` | 9,4 | 7,6 | 5,9 |
  | `text_subtle` | 5,9 | 4,8 | **3,7** |
  | `success` | 5,5 | **4,4** | **3,4** |
  | `info` | 7,0 | 5,7 | **4,4** |
  | `error` | 5,1 | **4,1** | **3,2** |
  | `accent_ink` sobre `accent` | 5,1 | | |

  Os valores em negrito ficam abaixo de 4,5:1. Por isso:
  - em célula com hover ou selecionada (fundo `surface_hover`), a linha de estado usa `text_muted` e mantém o selo
    colorido como reforço;
  - na coluna de filtros (`surface_raised`), contagens em `text_subtle` (4,8:1) e nada de texto em teal ou vermelho.
