# Notas do grupo C: curso "PROMOB PLUS" (canal Wattila), gavetas e maneiras de fazer módulos

Levantamento feito em 2026-10-14 a partir de legendas automáticas (com erros de reconhecimento) e de frames
extraídos dos vídeos. Convenções:

- Fonte: `<id> [mm:ss]`. Para prints, o `mmss` do nome do arquivo é o instante do frame.
- **VISTO**: lido na tela (rótulo, valor, barra de status). **DITO**: narração (legenda, às vezes truncada ou errada).
- Versões vistas na barra de título: Promob Plus 5.38.7.7 (aulas 1, 3, 4, 5, 6, 9), 5.38.12.7 (vídeo de gavetas),
  5.37.9.13 (vídeo das três maneiras). As bibliotecas mudam entre versões (ex.: profundidade do balcão 550 x 560 mm).
- Fora do escopo: **aulas 7 e 8** do curso tratam de render e não foram analisadas. A **aula 2** (paredes, portas e
  janelas) não está neste grupo; a aula 3 começa com a janela já colocada.
- Prints: `inputs/prints/` (59 arquivos deste grupo).

---

## 1. Por vídeo

### Ww5hO_awl7Q: aula 1, configurações e ferramentas (4 min)

**Resumo.** Apresenta a tela inicial, as Preferências (Ferramentas > Preferências) e os Dados do Cliente. Mostra a
navegação 3D (zoom com a roda, arrastar com a roda pressionada, girar com o botão direito) e a lógica do catálogo em
abas encadeadas "de cima para baixo". Não constrói nada; é a base da interface.

**Fluxo.**
1. Ferramentas > Preferências > Geral > Projeto: escolher a pasta onde os projetos serão salvos (DITO `[0:19]`–`[0:41]`).
2. Ambiente > Tipo de Preenchimento: o autor prefere "Texturas com Linhas" (DITO `[0:48]`–`[1:05]`).
3. Medidas: deixar sempre em milímetros, "quanto mais preciso melhor" (DITO `[1:15]`–`[1:22]`).
4. Dados do Cliente: código do projeto (ex.: 101), nome do cliente, dados da empresa; "Ir para o projeto" (DITO `[1:30]`–`[2:06]`).
5. Ambiente 3D: catálogo de módulos no topo, favoritos, navegação com o mouse (DITO `[2:06]`–`[3:20]`).
6. Catálogo: clica a biblioteca (ex.: Tramontina), a linha de baixo mostra as subcategorias e assim por diante; o
   painel de Materiais segue o mesmo padrão (DITO `[3:25]`–`[3:57]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `Ww5hO_awl7Q-0022-preferencias-arvore-idioma.jpg` | Árvore de Preferências: Geral (Idiomas, Projeto, Impressora PDF, Dicas de Operação), Ambiente (Cor de Fundo, Tipo de Preenchimento, Construção de Paredes, Movimentação, HotPoints, Luzes, Parede), Medidas, Internet, Listagem. Idioma "Auto (pt-BR)". |
| `Ww5hO_awl7Q-0032-preferencias-pasta-projetos.jpg` | Geral > Projeto: "Salvar projetos em:" com a caixa "Procurar Pasta" aberta (pasta "Curso"). |
| `Ww5hO_awl7Q-0102-preferencias-tipo-preenchimento.jpg` | Opções: Preenchimento com Linhas, Preenchimento, **Texturas com Linhas** (marcada), Texturas, Apresentação, HidePB, Hide, Sem Preenchimento; caixa "Carregar todos os projetos com o tipo de preenchimento selecionado". |
| `Ww5hO_awl7Q-0112-preferencias-movimentacao.jpg` | Ambiente > Movimentação: "Incremento da movimentação: 50"; "Desenhar somente Caixa de Contorno" (desmarcada). |
| `Ww5hO_awl7Q-0120-preferencias-medidas.jpg` | Medidas > Unidade de Medida: "Formatos usuário: Milímetro"; exemplo 150 → 150. |
| `Ww5hO_awl7Q-0142-dados-do-cliente-empresa.jpg` | Dados do Cliente (Código 01, Nome, CPF/CNPJ, Telefone, Celular, Endereço, Bairro, Cidade, UF, CEP, E-mail, Endereço de Entrega, Observações) e Dados da Empresa; botão "Ir para o projeto". |
| `Ww5hO_awl7Q-0232-ambiente-3d-piso-propriedades.jpg` | Ambiente 3D com catálogo Decore > Portas; propriedades do Piso: Largura 5000, Altura 5, Profundidade 5000, Camada Piso. |
| `Ww5hO_awl7Q-0402-catalogo-tramontina-cooktops.jpg` | Biblioteca Tramontina > Cooktops (Prime, Perfecta, Standard): Penta 5GX 70 HE, Square Touch 4EI etc. Mostra o catálogo em 3 níveis de abas. |

### 7yfwF-BIyl8: aula 3, construindo geometria (bancada) (5 min)

**Resumo.** Usa a ferramenta de geometria livre (não o construtor de armários) para fazer a base de alvenaria da
bancada e a bancada em si: retângulo desenhado no piso, depois ajustado pelo Editor de Geometria e pelas
propriedades. Termina com "Construir Lineares" para fechar a bancada. Resultado: "bancada com a base própria, pronta
para receber os armários" (DITO `[4:59]`–`[5:07]`).

**Fluxo.**
1. Menu de geometria: Construir Geometria / Circular / Retangular / Poligonal / Lineares (VISTO `0120`).
2. Geometria Retangular: clique no ponto inicial e no final com o botão esquerdo; botão direito na aresta para digitar a medida (DITO `[1:30]`–`[2:03]`).
3. "Geralmente bancada o padrão dela é 60 de profundidade, então a gente coloca 600 milímetros" (DITO `[2:05]`–`[2:09]`).
4. A altura (espessura) da geometria vem por padrão 150 (DITO `[2:28]`–`[2:31]`, VISTO `0137`: Altura 150).
5. Base: altura de 10 cm, "geralmente ela é mais ou menos nessa faixa" (DITO `[3:03]`–`[3:09]`; VISTO `0314`: Altura 100).
6. Editar Geometria: muda a profundidade da base para 500 "porque tem 10 centímetros" de recuo (DITO `[3:53]`–`[4:06]`).
7. Construir Lineares para os trechos restantes; botão direito finaliza (DITO `[4:30]`–`[4:59]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `7yfwF-BIyl8-0120-menu-construir-geometria.jpg` | Menu: Construir Geometria, Construir Geometria Circular, Retangular, Poligonal, Construir Lineares, Editar Geometria..., Adicionar Vértice, Remover Vértice, Aparar Geometria. Painel de propriedades de uma janela (Cotas, Dimensões 1600x1200x180, Orçamento, Outras, Perfurante Furar Sim / Profundidade 150). |
| `7yfwF-BIyl8-0137-geometria-retangular-medidas.jpg` | Ferramenta Construir Geometria Retangular: Largura 0, Profundidade 0, **Altura 150**, Afastamento 0, caixa "Furar". Status: "Para selecionar o plano de inserção, clique com o botão direito do mouse sobre o plano desejado." |
| `7yfwF-BIyl8-0154-editor-de-geometria.jpg` | Editor de Geometria: abas Editor de Forma / Editor de Perfil; Deslocamento 100; Aresta selecionada (Corda 506,9, Ângulo Absoluto 180, Ângulo Relativo 270, Ângulo do Arco 0, Flecha 0, Raio 253,4, Área 1,42 m²); Forma Base (Comprimento 4704,7, Largura 3623,6, X, Y); "Alterar plano pai ao movimentar". Geometria 506,9x150x2808,6. |
| `7yfwF-BIyl8-0234-editor-geometria-secao-geometria.jpg` | Mesma janela com a aresta longa selecionada (Corda 2808,6, Ângulo Absoluto 270). |
| `7yfwF-BIyl8-0314-base-bancada-propriedades.jpg` | Base: Largura 600, **Altura 100**, Profundidade 2808,6; Posição Absoluta Z 0; Camada "Geometria"; Perfurante Furar Não. Status "Geometria (600x150x2808,6)". |
| `7yfwF-BIyl8-0444-construir-lineares-parametros.jpg` | Construir Lineares: Comprimento 300, Ângulo 10, Altura 150, Afastamento 0, **Espessura 18**, Incr. Linear 50, Incr. Angular 5, Orientação Esquerda, "Utilizar valores como padrão"; cota na tela "295,4<10". |

### -YuVfTyKyPY: aula 4, criando bancada de cozinha (5 min)

**Resumo.** Decora a bancada criada na aula 3: cuba e torneira do catálogo Decore, granito aplicado pelo painel
Materiais (arrastar e soltar ou pincel/conta-gotas), rodapé feito com Construir Lineares e teto. Não monta armário; é a
preparação do ambiente.

**Fluxo.**
1. Decore > Cozinhas > Misturadores/Torneiras e Cubas: arrastar e soltar sobre a bancada (DITO `[0:15]`–`[0:48]`).
2. Rotacionar pela Movimentação se cair virada (DITO `[0:48]`–`[0:56]`).
3. Materiais > Mármores | Granitos > Granito > Preto; ao soltar, pergunta onde aplicar (DITO `[1:07]`–`[1:42]`).
4. Pincel: botão direito copia o material de uma peça, esquerdo aplica (DITO `[2:00]`–`[2:21]`).
5. Rodapé: Construir Lineares contornando a parede; "minha base tem 10 cm de altura, vou colocar o rodapé com dez também" (DITO `[3:05]`–`[4:05]`).
6. Construir teto (DITO `[4:35]`–`[4:40]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `-YuVfTyKyPY-0047-cuba-inserida-cotas.jpg` | Decore > Cozinhas > Cubas (CR Dupla, Redonda, Quadrada, ..., 9 - Retangular). Cuba Retangular 470x140x300; Camada Decore; **Perfurante Furar Sim, Profundidade 180** (a cuba fura a bancada). Cotas 1672 / 733,7. |
| `-YuVfTyKyPY-0116-materiais-granito-aplicar.jpg` | Painel Materiais > Mármores | Granitos > Granito: Absoluto, Amsterdan, Fênix, Ouro Preto, Qualiti, São Gabriel; filtros por cor. Propriedades da Parede: Espessura 150, Pé-direito Inicial/Final 2600, Comprimento 3323,6. |
| `-YuVfTyKyPY-0230-aplicar-material-perfil-face-tudo.jpg` | Diálogo "Onde deseja aplicar o material?": Perfil Horizontal / Face / Tudo. Tampo selecionado: Afastamento Piso 840, Largura 600, Altura 150, Profundidade 2808,6, Z 840. |
| `-YuVfTyKyPY-0334-construcao-lineares-finalizar.jpg` | Diálogo "Construção de Lineares": Finalizar construção / Editar perfil; Configurações Cor ou Material; Alinhamento Por Cima / Por Baixo; "Criar segmentos" (cada segmento editado individualmente). |
| `-YuVfTyKyPY-0400-rodape-propriedades.jpg` | Rodapé (geometria): Largura 3884,7, **Altura 100**, Profundidade 159,1; Camada Geometria. |

### Ask6ahTwQrU: aula 5, criando armários (5 min)

**Resumo.** Monta os armários de baixo pela **biblioteca pronta** (Cozinhas > Inferiores): gaveteiro de 4 gavetas,
balcões de porta. Mostra o encaixe automático no espaço livre (cotas até os obstáculos), o ajuste de largura com
aviso quando não cabe e a troca de modelo de porta/puxador em lote pelo painel Modelos.

**Fluxo.**
1. Cozinhas > Inferiores > Balcões / Gaveteiros (DITO `[0:34]`–`[0:46]`).
2. Gaveteiro ao lado do canto: cuidado com a profundidade/abertura da gaveta junto ao outro móvel (DITO `[0:46]`–`[1:12]`, legenda muito truncada).
3. Clique no módulo e na parede: "ele já vai demonstrar a largura onde ele vai encaixar"; dois cliques no catálogo insere direto (DITO `[1:46]`–`[2:11]`).
4. Mover com o botão auxiliar arrastando; vista planta baixa para encostar na parede (DITO `[2:53]`–`[3:25]`).
5. Ajustar largura para fechar o vão: "essa distância tem 190 mm ... vou crescer nesse módulo" (DITO `[3:36]`–`[3:57]`).
6. Puxadores: selecionar com Ctrl e aplicar "puxador madeira gola", "o mais usado"; com tudo selecionado aplica de uma vez (DITO `[4:00]`–`[4:46]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `Ask6ahTwQrU-0049-catalogo-cozinha-inferiores.jpg` | Abas Cozinhas: Inferiores, Despenseiros, Ilhas, Sup Baixos, Sup Médios, Sup Altos, Tampos/Prateleiras, Componentes, Portas/Frentes, Portas/Frentes Parceiros, Caixas, Caixa Gav Parceiros, Composição. Filtros de Inferiores: Cantos, Cantos Bifold, Balcões, Gaveteiros, p/ Eletros, Pias, Diagonais, Cantoneiras. Balcões: Toalheiro 150mm, Adega 150mm, Porta-Latas 200mm, 1P 400mm, Lixeira 400mm, 2P 800mm, 2P Bifold 800mm, Ilha 800mm, Escamoteável 800mm, 2P Curvo 800 mm. |
| `Ask6ahTwQrU-0105-balcao-porta-aberta-interior.jpg` | Balcão 2P 800mm aberto: duas laterais, base, uma prateleira, sem sarrafo visível sob o tampo; painel Aberturas > Portas com ângulo 59°. Cotas até os obstáculos 1339,5 e 1025; marca "150" na parede. |
| `Ask6ahTwQrU-0209-gaveteiro-propriedades.jpg` | Balcão 4 Gavetas **400x700x560**; Largura em lista suspensa (valores fixos); **Entidade > Quantidade Gavetas 4**; Camada Cozinhas-Inferio(r); Z 150. Gaveteiros: 4G 400mm, 4G Curvo 400mm, 4G Côncavo 400mm, 2G+1Gav 400mm, 1G+1P 400mm, Tábua 400mm, 1G+1P Desli 400mm, 1G+2Gav 600mm, 2Gav 800mm, 3G 400. |
| `Ask6ahTwQrU-0221-aviso-sem-espaco-largura.jpg` | Diálogo Inserir: "Não há espaço suficiente para alterar a largura do módulo para 500 no plano selecionado. Deseja alterar a largura do módulo para 463,1?" Sim / Não; "Não mostrar essa mensagem novamente". |
| `Ask6ahTwQrU-0313-reposicionar-planta-frontal.jpg` | Janela Reposicionar: Vista frontal (X 0, Z -700, giro 0) e Planta baixa (X 0, Y -159,1, giro 270); Passo Teclado 10; Posições Salvas. Balcão 2 Gavetões 800x700x560, Quantidade Gavetões 2. |
| `Ask6ahTwQrU-0446-modelos-portas-gola-horizontal.jpg` | Modelos > Portas > Madeira: Reta (marcada), Lisa, Almofada, Fresada, Colonial, Bicolor, Gola Horizontal, Gola Vertical, Borda Alumínio, Cava, Cava Vertical; grupos Alumínio, Vidro, Parceiros (Cozinhas). |
| `Ask6ahTwQrU-0449-modelos-estilo-cozinhas-corredicas.jpg` | Modelos (Todos / Seleção): Caixas Cores > Branco; Portas Madeira > Gola Horizontal; Frentes 1 Puxador > Madeira > Gola; Portas/Frentes - Gola, Externo Caixas, Externo Portas/Frentes, Fita Borda Caixas, Fita Borda Portas/Frentes, Fita Borda Frontal Caixas (todos Cores > Branco); Acessórios: Dobradiças "Padrão - Sem Amortecedor > Reta / Baixa", Acabamento - Dobradiças Aço, **Corrediças 500 Apoiada**; Decore: Maçanetas 1 - Maçaneta. |

### KQs4HQ6f5Sg: aula 6, continuando criação de armários (6,5 min)

**Resumo.** Fogão/cooktop e coifa pelo Localizar Rápido, depois os armários de cima pela biblioteca: Sup Baixos
(basculantes, mais baixos), Sup Médios (portas de giro, um pouco mais altos) e Sup Altos (portas de giro, mais altos).
Coloca geladeira e um aéreo sobre ela com profundidade 600 em vez de 320/350. O autor diz que o modo construtor será
ensinado depois; aqui é "o método rápido" com módulos prontos (DITO `[1:11]`–`[1:24]`).

**Fluxo.**
1. Localizar Rápido: digita "fogão"/"coifa" em vez de navegar pelas abas (DITO `[0:07]`–`[0:16]`).
2. Cooktop: girar 90° se cair virado; sob cooktop não pode haver gaveta alta, ou ela fica mais baixa, ou usa basculante (DITO `[0:41]`–`[1:10]`).
3. Coifa de parede com largura editada para 70 cm (DITO `[2:33]`–`[2:37]`).
4. Superiores: Sup Baixos = basculantes, mais baixos; Sup Médios = "um pouco mais alto, porta de giro, não basculante"; Sup Altos = porta de giro "mais altos ainda", "80 de 90 de altura" (DITO `[3:00]`–`[3:31]`).
5. Geladeira Brastemp: Posição Absoluta Z = 0 para descer ao chão (DITO `[4:20]`–`[4:32]`).
6. Larguras dos aéreos ajustadas para 90 e 90 para fechar o espaço (DITO `[4:41]`–`[4:59]`).
7. Aéreo sobre a geladeira: altura 70, largura 80 e profundidade aumentada; explicar ao cliente "por que é 35 e aqui é 60": com profundidade maior o montador fixa atrás e na lateral, fica mais firme; alternativa: lateral até o chão fechando a geladeira (DITO `[5:08]`–`[6:30]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `KQs4HQ6f5Sg-0145-localizar-rapido.jpg` | Janela Localizar Rápido: "Pesquisar por: coifa", árvore de pastas por fabricante (Arix\Coifas Ilha\, Bosch\Depuradores e Coifas\, Brastemp\..., Cata\Coifas\...); "Foram encontrados 378 itens em 3s." |
| `KQs4HQ6f5Sg-0306-sup-baixos-basculante-catalogo.jpg` | Sup Baixos: 1P 400mm, 1P Basc 700mm, 2P 800mm, 2P Coplanar 800mm, 2P Basc 1200mm, 2P Sistema Correr 1200mm, 2P Correr 1200mm, Nicho 700mm, Adega 45°, 600mm Adega 45° Nichos; filtros Cantos, Armários, Fornos/Microondas, Diagonais, Cantoneiras. Módulo com cota 320 acima e 840 abaixo (até a bancada). Painel ainda mostra valores em transição (Largura 700); altura não confiável neste frame. |
| `KQs4HQ6f5Sg-0325-sup-altos-cantos-catalogo.jpg` | Sup Altos > Cantos: CR Esq 800mm, CR 2P Esq 1176mm, CR Dir 800mm, CR 2P Dir 1176mm, "L" Esq 800mm, "L" Dir 800mm, "L" 2P Esq 800mm, "L" 2P Dir 800mm, Oblíquo 1P, Oblíquo 2P 800mm; Aberturas 0°. |
| `KQs4HQ6f5Sg-0346-sup-altos-2p-propriedades.jpg` | Sup Altos (Adega 150mm, 1P 400mm, 2P 800mm, 3P 1200mm, Fechamento). Módulo **800x950x320**, Posição Absoluta **Z 1650**, Cota Inferior 660; Camada Cozinhas-Super(ior). |
| `KQs4HQ6f5Sg-0513-aereo-sobre-geladeira.jpg` | Aéreo Largura 900, Altura 950, Profundidade 320, Z 1650; geladeira ao lado. |
| `KQs4HQ6f5Sg-0546-aereo-profundidade-alterada.jpg` | Aéreo sobre a geladeira: Largura 800, Altura 700, **Profundidade 600**, Z 1900 (= 1900 + 700 = 2600, alinhado ao pé-direito). |

### WNukGXTt2XY: aula 9, porta-tempero de MDF (5 min)

**Resumo.** Transforma um gaveteiro estreito da biblioteca (Balcão 4 Gavetas 200 mm) num porta-tempero de MDF:
apaga as caixas das gavetas de cima, aplica o modelo Gola na frente **antes** de redimensionar, estica a frente até a
altura da porta vizinha e reposiciona a caixa da gaveta. Alternativa ao porta-temperos aramado de inox.

**Fluxo.**
1. Referência: o porta-latas/porta-temperos de inox existente; "a largura geralmente padrão é 20" (DITO `[0:30]`–`[0:37]`).
2. Insere Gaveteiro 4G e muda a largura para 200 (DITO `[0:53]`–`[1:01]`, VISTO `0106`).
3. Aberturas: abrir todas as gavetas "no modo cascata" para enxergar as caixas (DITO `[1:05]`–`[1:12]`).
4. Um clique seleciona o módulo inteiro (apaga tudo); dois cliques selecionam a peça (frente ou caixa) (DITO `[1:14]`–`[1:33]`).
5. Aplicar o puxador Gola **antes** de mudar a altura da frente: trocar o modelo devolve a frente ao tamanho original (DITO `[1:36]`–`[2:06]`).
6. Altura da porta vizinha 69 cm: Ctrl+C na propriedade, Ctrl+V na frente (DITO `[2:13]`–`[2:30]`).
7. Reposicionar (vista frontal / planta baixa) para encaixar; altura das laterais da caixa reduzida para 10 "para não ficar tão alto" (DITO `[2:37]`–`[3:11]`). Alguns chamam de "porta-latas" (DITO `[3:14]`–`[3:17]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `WNukGXTt2XY-0014-porta-temperos-inox-existente.jpg` | Balcão Porta-Latas **200x700x560** com aramado de inox; Aberturas > Gavetas (abertura 303). |
| `WNukGXTt2XY-0106-gaveteiro-200-propriedades.jpg` | Gaveteiro com Largura 200, Altura 700, Profundidade 560, Quantidade Gavetas 4, Z 0. |
| `WNukGXTt2XY-0112-gavetas-abertas-cascata.jpg` | 4 gavetas abertas em cascata; Aberturas > Gavetas com abertura 400. Corrediças visíveis sob as caixas. |
| `WNukGXTt2XY-0122-caixa-gaveta-c-contra-frente.jpg` | Status: "Caixa Gaveta c/ Contra Frente (144x130,3x491)". A caixa é um item separado da frente. |
| `WNukGXTt2XY-0132-frente-gaveta-selecionada.jpg` | Status: "Frente Reta (194x170,3x18)": frente de 194 mm num módulo de 200 mm. |
| `WNukGXTt2XY-0144-modelos-frente-gola.jpg` | Modelos aba Seleção: Frentes 1 Puxador > Madeira > Reta; Corrediças 500 Apoiada; Puxadores Sem Puxador. |
| `WNukGXTt2XY-0230-frente-altura-propriedades.jpg` | Frente Gola 194x170,3x18 com Altura sendo digitada 690; Camada Cozinhas-Portas; "Afastamento Módulo 0". |
| `WNukGXTt2XY-0500-porta-tempero-mdf-final.jpg` | Render Up do resultado: frente alta com gola e caixa de gaveta baixa atrás, aberta. |

### jtEjP6DrzpM: configurar gavetas no Promob (7,5 min)

**Resumo.** Mostra que as folgas e a construção da gaveta não ficam no módulo: ficam no **Configurador de
Dimensões**, numa configuração nomeada ("COZ - MDF 18 - Fundo encaixado - Sarrafo tras horizontal") aplicável aos
itens selecionados ou existentes. Ajusta as folgas da caixa da gaveta, o fundo (encaixado em canal x pregado por baixo),
a espessura do fundo e a folga da corrediça, conferindo no gaveteiro 3D.

**Fluxo.**
1. Abrir o Configurador de Dimensões e escolher a configuração "padrão Promob cozinhas, chapa de 18" (DITO `[0:07]`–`[0:48]`).
2. Cozinhas > Gavetas > Folgas; a lateral da gaveta destacada em laranja é a "medida base" (DITO `[0:48]`–`[1:09]`).
3. Folgas superiores: "descontar 5 mm" além do padrão → 20 + 5 = 25 na contra-frente e na posterior (DITO `[1:19]`–`[1:46]`).
4. Folgas inferiores: 10 mm de folga + 6 mm do fundo = 16 → 20 + 16 = 36 na contra-frente e na posterior; a inferior lateral não muda (DITO `[1:49]`–`[2:25]`).
5. Gavetas > Fundos: avanço do fundo sobre a lateral 5 mm (vai em canal); sobre a contra-frente, sem canal, 18 = espessura da chapa (DITO `[3:22]`–`[3:58]`).
6. "Aplicar sobre módulos existentes" (DITO `[3:58]`–`[4:04]`).
7. Variante: fundo de 15 mm sem canal, pregado por baixo: Chapas > Gavetas > Fundo, espessura 15; avanços 18 na frente e atrás (DITO `[4:59]`–`[6:25]`).
8. Folga da corrediça: telescópica x invisível; com a invisível a folga cai (VISTO 13 → 5) (DITO `[6:27]`–`[7:21]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `jtEjP6DrzpM-0025-configurador-dimensoes-arvore.jpg` | Configurador de Dimensões; configuração "COZ - MDF 18 - Fundo encaixado - Sarrafo tras horizontal"; árvore Promob > Medidas Máximas; Cozinhas (Dimensões Externas, Chapas, Montagem da Caixa - Inferior, Montagem da Caixa - Superior, Montagem da Caixa - Despenseiro, Eletros, Frentes / Portas, Gavetas, Gavetas Internas / Auxiliares, Cozinhas Cava); Dormitórios, Banheiros, Escritórios, Salas, Finesse, Portábille, Esquadrimed, Perlare, Villaggio, Perfar, Flexa Componentes, Blum. Diversos: A Material, B Largura Máxima da Chapa, C Comprimento Máximo da Chapa, D Espessura da Chapa. Caixas "Aplicar nos itens selecionados" / "Aplicar nos itens existentes". |
| `jtEjP6DrzpM-0041-configurador-lista-configuracoes.jpg` | Lista de configurações: COZ - MDF 18 / MDF 15 com Fundo encaixado, pregado, rebaixado ou travessas e Sarrafo tras horizontal ou vertical; COZ CAVA - MDF 18/15 - Fundo encaixado - Sarrafo tras vertical; DOR - MDF 18/15 - Lateral alinhada com base / Lateral sobre base (fixo) / (auto); configurações do usuário ("ARMÁRIOS CORPO DE 15 - PORTA DE 18MM ...", "ARMARIOS CORPO DE 18 (fundo com Canal)"). |
| `jtEjP6DrzpM-0107-gavetas-folgas-padrao.jpg` | Gavetas > Folgas, padrão: Gavetas Externas: **A Folga Corrediça 13**, **B Folga até Fundo da Caixa 30**; Gavetas: **C Folga Superior Contra-Frente 20, D Superior Lateral 20, E Superior Posterior 20, F Inferior Contra-Frente 20, G Inferior Lateral 20, H Inferior Posterior 20**; há mais um grupo abaixo ("Gavetão", cortado). Desenhos com as cotas A..N. |
| `jtEjP6DrzpM-0219-gavetas-folgas-editadas.jpg` | Após edição: C 25, D 20, E 25, F 36 (sendo digitado), G 20, H 20. Descrição: "Folga Inferior Contra-Frente: define a distância entre a extremidade inferior da frente da gaveta e a contra-frente da caixa da mesma. Altera a altura da contra-frente da caixa da gaveta." Configuração passa a "(alterado)". |
| `jtEjP6DrzpM-0338-gavetas-avanco-fundo.jpg` | Gavetas > Fundos (Vista Frontal / Vista Lateral): **A Avanço Fundo sobre Lateral 5, B Avanço Fundo sobre Frente/Contra Frente 5, C Avanço Fundo sobre Posterior 5, D Recuo Fundo 10**. "Avanço Fundo sobre Lateral: define quanto o fundo avança sobre cada lateral da gaveta." |
| `jtEjP6DrzpM-0514-chapa-fundo-de-gaveta.jpg` | Chapas > Gavetas (Lateral, Lateral Metálica, Contra Frente, Posterior, Fundo) > Fundo de Gaveta: A Material MDF, B Largura Máxima da Chapa 2750, C Comprimento Máximo da Chapa 1830, **D Espessura da Chapa 6**; Integração c/ Plano de Corte: Fita Borda 1..4 = 0. Status: "Lateral de Gaveta 18mm (18x126,3x496)". Lista de chapas: Lateral, Divisória, Base, Fundo - Inferiores, Fundo - Superiores, Traseira, Travessas, Prateleira, Portas / Frentes, Painel p/ Portas, Frente Gav Int, Tampo, Tamponamento, Painel, Especial, Componentes, Gavetas. |
| `jtEjP6DrzpM-0546-gavetas-recuo-fundo.jpg` | Fundos na variante pregada por baixo: A 0, B 18, C 18, D Recuo Fundo 10. "Recuo Fundo: define o deslocamento do fundo da gaveta." |
| `jtEjP6DrzpM-0642-folga-corredica.jpg` | A Folga Corrediça 13 selecionada para edição; "Folga Corrediça: define o afastamento entre a lateral da gaveta e a lateral do módulo. Altera a largura da gaveta." |
| `jtEjP6DrzpM-0708-modelos-corredica-telescopica.jpg` | Folga Corrediça já em **5**; painel Modelos com **Corrediças 500 Telescópica**, Frentes 1 Puxador > Madeira > Reta, Puxadores Sem Puxador. |
| `jtEjP6DrzpM-0738-gaveteiro-3d-resultado.jpg` | Gaveteiro com 4 gavetas, a de cima aberta: caixa com laterais, contra-frente, traseira e fundo; travessa/sarrafo frontal no topo do módulo; frentes sobrepostas. |

### Or7qXPijqLA: três maneiras de fazer módulos no Promob (15 min)

**Resumo.** Constrói o **mesmo** balcão de 1200 x 700 x 550 com 3 portas (2 num vão, 1 no outro) de três formas:
(1) inserção automática da biblioteca, (2) **Construtor de Armários** e (3) composição peça por peça, com calculadora.
Conclui que as três chegam ao mesmo efeito; a peça por peça exige conta manual de folgas e sobreposições.

**Fluxo.**
1. Biblioteca: insere o "Balcão 3 Portas" e edita as medidas na barra de propriedades. "A maneira mais simples e convencional" (DITO `[0:09]`–`[0:31]`).
2. Construtor de Armários: escolhe "módulo de cozinha inferior com divisória" (DITO `[0:41]`–`[0:51]`, VISTO `0049`).
3. Na aba Estrutura, arrastando o mouse copia uma medida existente ou preenche um espaço vazio (DITO `[0:51]`–`[1:07]`).
4. Divisões > Inserção múltipla: três divisórias e exclui uma (DITO `[1:18]`–`[1:35]`).
5. Portas: escolhe o vão, aplica duas portas num e uma no outro; "exatamente igual o efeito do módulo" (DITO `[2:02]`–`[2:36]`).
6. Peça por peça: "exatamente igual a construção de um móvel na vida real, na marcenaria"; parte da medida externa (DITO `[2:40]`–`[3:10]`).
7. Duas laterais de 15 de 700 x 550; duplicar com a ferramenta Arranjo; 1200 - 15 - 15 = 1170 de vão interno (DITO `[3:12]`–`[4:27]`).
8. Base de 1170 ("largura sinal de mais 17": soma direto no campo) e dois sarrafos horizontais (DITO `[4:27]`–`[7:04]`).
9. Regra dita: não montar tudo com "prateleira" girada: o plano de corte aplica fita de borda diferente e a etiqueta sai com o nome errado; usar a peça certa (lateral, base, sarrafo) (DITO `[4:33]`–`[5:17]`).
10. Divisória com fita frontal de 670 de altura; vão livre 1200 - 3 x 15 = 1155; ÷ 3 = 385 por vão (DITO `[7:14]`–`[8:19]`).
11. Prateleira linear centralizada em Y e com profundidade reduzida (DITO `[9:03]`–`[9:21]`).
12. Porta: 3 mm de folga em cima e embaixo → 700 - 6 = 694; cobre 12 mm da lateral e 5 mm da divisória → 385 + 12 + 5 = 402 (DITO `[10:10]`–`[11:08]`, VISTO `1106`: 402 x 694 x 18).
13. Agrupar o gabinete antes de pôr as portas (DITO `[11:20]`–`[11:37]`); porta 3 mm para dentro (DITO `[12:00]`–`[12:16]`).
14. Duas portas num vão de 770: (770 + 12 + 5 - 3) ÷ 2 = 392 (DITO `[13:19]`–`[13:59]`).

| Print | O que mostra (rótulos e valores lidos) |
| :--- | :--- |
| `Or7qXPijqLA-0025-biblioteca-balcao-3-portas-props.jpg` | Biblioteca: "Balcão 3 Portas (1200x700x550)"; Largura 1200 (lista editável), Altura 700, Profundidade 550; marcas de altura na parede 820, 1470, 2010, 2280, 2550. |
| `Or7qXPijqLA-0049-construtor-tipos-de-estrutura.jpg` | Construtor de Armários, "Selecione uma estrutura de caixa para iniciar a construção". Abas: Cozinhas, Cozinhas - Portas Embutidas, Dormitórios, Salas. Cozinhas: Inferior c/ Divisória; Inferior c/ Divisória e Rod; Inferior c/ Divisória até Piso; Inferior c/ Divisória até Piso e Rod; Inferior c/ 2 Laterais até Piso; Inferior c/ 2 Laterais até Piso e Rod; Gaveteiro; Gaveteiro c/ Rodapé; Superior c/ Divisória; Superior c/ 2 Laterais; Torre p/ Eletros; Torre p/ Eletros c/ Rod. |
| `Or7qXPijqLA-0057-construtor-aba-estrutura.jpg` | Abas do construtor: **Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos**. "Tipo: Inferior c/ Divisória". Definições: **Número de vãos 1, Largura total 500, Altura 700, Profundidade 550**. Posição: Inferior esquerda; Cota anterior 0, Cota inferior 800, Cota posterior 4350, Cota superior 1100. Componentes: ☑ Lateral Esquerda 15mm, ☑ Lateral Direita 15mm, ☑ Divisória, ☑ Base Inferior 15mm, ☐ Sarrafo Inteiro 15mm, ☑ Sarrafo Frontal 15mm (lista continua). Movimentação: Passo inicial 0, Passo 10. |
| `Or7qXPijqLA-0130-construtor-aba-divisoes.jpg` | Divisões > Inserção múltipla: peça "Divisória 15", Orientação Prioritária Vertical/Horizontal, grade de células para escolher quantas divisões. Vão selecionado **1170 x 670** num módulo 1200 x 700. |
| `Or7qXPijqLA-0149-construtor-divisao-horizontal-prateleiras.jpg` | Divisões > Horizontal: subabas Prateleiras Móveis / Prateleiras Fixas / Sem Prateleira; itens "Interna c/ Recuo Fron 15mm" e "Interna s/ Recuo Fron 15mm"; botão Inserir. |
| `Or7qXPijqLA-0201-construtor-aba-portas-vaos.jpg` | Portas: subabas Ambas, Inteira, Esquerda, Direita, Basc Inf, Basc Sup; modelos Reta, Lisa, Almofada, Fresada...; "Inserir invertido". Vãos cotados 790 e 380 (largura) e 342,5 e 327,5 (altura) depois de divisória e prateleira. |
| `Or7qXPijqLA-0225-construtor-resultado-3d.jpg` | Módulo do construtor (3 portas) no ambiente, ao lado do balcão de biblioteca equivalente. |
| `Or7qXPijqLA-0258-composicao-pecas-catalogo.jpg` | Cozinhas > Composição: filtros Laterais/Divisórias, Bases, Fundos, Sarrafos, Diversos, Gaveta, Painéis; peças Lateral 15", Micro-ondas 15", Divisória 15", Divisória Fita Fron 15", Lateral/Fundo Península 15". Status do módulo do construtor: "(Item Extra) 1.9999 -> Inferior (1200x700x550)". |
| `Or7qXPijqLA-1106-peca-a-peca-porta-formula-largura.jpg` | Porta Reta avulsa: Largura 402 (sendo digitada), Altura 694, Profundidade 18; Camada Portas. Status "Porta Reta (400x694x18)". Módulo peça a peça com laterais, base, sarrafos, divisória e prateleiras. |

---

## 2. Arquitetura por tipo de armário (consolidado)

O Promob trata balcão, aéreo e alto como **estruturas de caixa diferentes**, não como o mesmo armário com outras
medidas. Isso aparece em três lugares: tipos distintos no Construtor (VISTO `Or7qXPijqLA-0049`), seções distintas no
Configurador de Dimensões ("Montagem da Caixa - Inferior / Superior / Despenseiro", "Fundo - Inferiores / Fundo -
Superiores") (VISTO `jtEjP6DrzpM-0025`, `-0514`) e camadas distintas no módulo (Cozinhas-Inferior, Cozinhas-Superior).

### Balcão (inferior)
- **VISTO**: medidas de biblioteca 1200 x 700 x 550 (`Or7qXPijqLA-0025`, v5.37) e 400/800 x 700 x 560
  (`Ask6ahTwQrU-0209`, `-0313`, v5.38). Altura de caixa 700 nos dois casos.
- **VISTO**: peças do tipo "Inferior c/ Divisória": Lateral Esquerda 15mm, Lateral Direita 15mm, Divisória, Base
  Inferior 15mm, Sarrafo Frontal 15mm marcados; **Sarrafo Inteiro 15mm desmarcado** (`Or7qXPijqLA-0057`). Ou seja,
  o balcão não tem tampo de chapa inteiro: tem sarrafo(s) no alto, porque o tampo é de pedra.
- **VISTO**: com 2 laterais de 15 e base + sarrafo de 15, o vão interno fica 1170 x 670 (`Or7qXPijqLA-0130`).
- **VISTO**: interior do balcão 2P: base, uma prateleira, laterais; sem chapa no topo (`Ask6ahTwQrU-0105`).
- **DITO**: na peça por peça usa duas bases/sarrafos horizontais no alto (sarrafo de cima e "sarrafa" atrás)
  (`Or7qXPijqLA [6:01]`–`[7:04]`); a configuração escolhida diz "Sarrafo tras horizontal" ou "vertical" (VISTO `jtEjP6DrzpM-0041`).
- **VISTO**: variantes de base: "e Rod" (com rodapé), "até Piso" (laterais descem ao chão) e "2 Laterais até Piso"
  (`Or7qXPijqLA-0049`). Na biblioteca o balcão fica a Z 150 ou 100 sobre a base/rodapé (`Ask6ahTwQrU-0209`, `-0221`).
- **VISTO**: variantes de fundo no Configurador: Fundo encaixado, pregado, rebaixado, travessas (`jtEjP6DrzpM-0041`).
- **DITO**: sob cooktop não cabe gaveta alta: usar gaveta mais baixa ou basculante (`KQs4HQ6f5Sg [0:53]`–`[1:10]`).

### Gaveteiro (inferior com gavetas)
- **VISTO**: tipos próprios no Construtor: "Gaveteiro" e "Gaveteiro c/ Rodapé" (`Or7qXPijqLA-0049`).
- **VISTO**: biblioteca: 4G 400, 3G 400, 2Gav 800 (gavetões), 2G+1Gav 400, 1G+1P 400 (gaveta + porta), 1G+2Gav 600,
  Tábua 400 (tábua de corte), 1G+1P Desli; 400 x 700 x 560 com propriedade "Quantidade Gavetas" (`Ask6ahTwQrU-0209`).
- **VISTO**: travessa/sarrafo frontal no topo e caixa de gaveta completa (`jtEjP6DrzpM-0738`).

### Aéreo (superior)
- **VISTO**: três famílias de biblioteca: Sup Baixos (basculantes, nichos, adegas, correr), Sup Médios, Sup Altos
  (1P, 2P, 3P, Adega 150, Fechamento) e cantos (CR, "L", Oblíquo) (`KQs4HQ6f5Sg-0306`, `-0325`, `-0346`).
- **VISTO**: Sup Altos 2P 800: **800 x 950 x 320**, Z 1650 (`KQs4HQ6f5Sg-0346`). Profundidade padrão do aéreo 320.
- **DITO**: profundidade do aéreo "35" (cm) contra "60" do armário sobre a geladeira (`KQs4HQ6f5Sg [5:52]`–`[5:56]`).
  O VISTO é 320; o 35 dito pode ser arredondamento ou outra biblioteca.
- **DITO**: basculante é mais baixo; médio tem porta de giro e é "um pouco mais alto"; alto tem porta de giro e é
  "mais alto ainda", "80 de 90 de altura" (`KQs4HQ6f5Sg [3:00]`–`[3:31]`).
- **VISTO**: tipos no Construtor: "Superior c/ Divisória" e "Superior c/ 2 Laterais" (`Or7qXPijqLA-0049`).
- **VISTO**: Configurador separa "Montagem da Caixa - Superior" e "Fundo - Superiores" (`jtEjP6DrzpM-0025`, `-0514`).
- **VISTO**: as portas de canto superiores têm larguras próprias (CR 2P 1176 mm) (`KQs4HQ6f5Sg-0325`).

### Aéreo sobre geladeira
- **VISTO**: 800 x 700 x 600, Z 1900 (topo em 2600) (`KQs4HQ6f5Sg-0546`).
- **DITO**: profundidade igual à da geladeira para o montador fixar atrás e na lateral; alternativa: lateral até o
  chão fechando a geladeira (`KQs4HQ6f5Sg [5:59]`–`[6:30]`).

### Alto / torre
- **VISTO**: "Torre p/ Eletros" e "Torre p/ Eletros c/ Rod" no Construtor; Despenseiros na biblioteca; seção
  "Montagem da Caixa - Despenseiro" no Configurador (`Or7qXPijqLA-0049`, `Ask6ahTwQrU-0049`, `jtEjP6DrzpM-0025`).
- Nenhum vídeo do grupo C monta um alto; só aparecem os nomes.

### Bancada (tampo e base de alvenaria)
- **Não é armário**: é geometria livre (Construir Geometria Retangular + Editor de Geometria + Construir Lineares).
- **DITO**: profundidade padrão da bancada 600 mm (`7yfwF-BIyl8 [2:05]`); base de ~10 cm (`[3:03]`); base recuada
  para 500 mm de profundidade "porque tem 10 centímetros" (`[3:58]`–`[4:06]`).
- **VISTO**: base 600 x 100 x 2808,6 (`7yfwF-BIyl8-0314`); tampo 600 x 150 x 2808,6 a Z 840 (`-YuVfTyKyPY-0230`);
  geometria retangular nasce com Altura 150 (`7yfwF-BIyl8-0137`).
- **VISTO**: a cuba é "Perfurante" (Furar Sim, Profundidade 180): recorta o tampo (`-YuVfTyKyPY-0047`).
- **VISTO**: material aplicado por "Perfil Horizontal / Face / Tudo" (`-YuVfTyKyPY-0230`).
- Rodapé também é linear: Altura 100 (`-YuVfTyKyPY-0400`).

### Porta-tempero / porta-latas (nicho estreito)
- **VISTO**: biblioteca "Balcão Porta-Latas 200x700x560" com aramado de inox (`WNukGXTt2XY-0014`); também
  "Porta-Latas 200mm" e "Toalheiro 150mm", "Adega 150mm" entre os balcões (`Ask6ahTwQrU-0049`).
- **Versão MDF** = gaveteiro de 200 mm modificado: uma frente alta Gola (194 x 690 x 18) presa a uma caixa de gaveta
  baixa, sobre corrediça (`WNukGXTt2XY-0230`, `-0500`). **DITO**: largura padrão 200 (`[0:35]`–`[0:37]`).

### Outros vistos
- Despenseiros, Ilhas (Ilha 800mm), Escamoteável 800mm, 2P Bifold, 2P Curvo, Lixeira 400mm, Diagonais, Cantoneiras,
  Cantos Bifold (`Ask6ahTwQrU-0049`).
- Sup Baixos: 2P Coplanar, 2P Sistema Correr, 2P Correr, Nicho 700mm, Adega 45° (`KQs4HQ6f5Sg-0306`).
- Abas do Construtor também em "Cozinhas - Portas Embutidas", "Dormitórios", "Salas" (`Or7qXPijqLA-0049`), não abertas.

---

## 3. Gavetas

### Tipos
- **VISTO**: gaveta (frente pequena) e gavetão (frente alta): propriedades "Quantidade Gavetas" e "Quantidade
  Gavetões" (`Ask6ahTwQrU-0209`, `-0313`). No Configurador há "Gavetas Externas", "Gavetas", um grupo cortado abaixo
  ("Gavetão"?) e a pasta "Gavetas Internas / Auxiliares" (`jtEjP6DrzpM-0025`, `-0107`).
- **VISTO**: módulos com combinação: 1G+1P, 2G+1Gav, 1G+2Gav, Tábua (`Ask6ahTwQrU-0209`).
- **VISTO**: aba "Gavetas" no Construtor de Armários (não aberta no vídeo) (`Or7qXPijqLA-0057`).

### Caixa da gaveta
- **VISTO**: peças de chapa da gaveta: Lateral, Lateral Metálica, Contra Frente, Posterior, Fundo
  (`jtEjP6DrzpM-0514`). Frente é item à parte ("Frente Reta", "Frente Gola"); caixa = "Caixa Gaveta c/ Contra Frente"
  (`WNukGXTt2XY-0122`, `-0132`).
- **VISTO**: lateral de gaveta 18 mm: "Lateral de Gaveta 18mm (18x126,3x496)" (`jtEjP6DrzpM-0514`).
- **VISTO**: fundo padrão MDF de 6 mm (`jtEjP6DrzpM-0514`).
- **VISTO**: fundo **encaixado em canal**: avanços 5/5/5 e recuo 10 (`jtEjP6DrzpM-0338`); **pregado por baixo** (fundo
  de 15): avanço lateral 0, frente 18, posterior 18, recuo 10 (`jtEjP6DrzpM-0546`).
- **VISTO**: pasta "Fixação Lateral - Contra Frente" e "Fixação Lateral - Posterior" (como a lateral prende na
  contra-frente/traseira), não abertas (`jtEjP6DrzpM-0107`).

### Folgas (Configurador > Cozinhas > Gavetas > Folgas)
| Campo | Padrão VISTO | Editado no vídeo | Descrição VISTA |
| :--- | :--- | :--- | :--- |
| A - Folga Corrediça | 13 | 5 (corrediça invisível) | afastamento entre a lateral da gaveta e a lateral do módulo; altera a largura da gaveta |
| B - Folga até Fundo da Caixa | 30 | 30 | (não lida) |
| C - Folga Superior Contra-Frente | 20 | 25 | |
| D - Folga Superior Lateral | 20 | 20 | |
| E - Folga Superior Posterior | 20 | 25 | |
| F - Folga Inferior Contra-Frente | 20 | 36 | distância entre a extremidade inferior da frente e a contra-frente da caixa; altera a altura da contra-frente |
| G - Folga Inferior Lateral | 20 | 20 | |
| H - Folga Inferior Posterior | 20 | 36 (DITO; o print mostra 20 antes da edição) | |

Fontes: `jtEjP6DrzpM-0107`, `-0219`, `-0642`, `-0708`; narração `[1:19]`–`[2:25]`, `[6:27]`–`[7:21]`.

### Corrediças
- **VISTO**: corrediça é escolhida no painel **Modelos > Acessórios > Corrediças**: "500 Apoiada" (`Ask6ahTwQrU-0449`,
  `WNukGXTt2XY-0144`) e "500 Telescópica" (`jtEjP6DrzpM-0708`). O "500" parece o comprimento (mm).
- **DITO**: telescópica x invisível mudam a folga lateral (`jtEjP6DrzpM [6:42]`–`[7:21]`, legenda confusa).
- **Dedução** (não dita): caixa de 144 mm num gaveteiro de 200 = 200 - 2 x 15 (laterais do módulo) - 2 x 13 (folga
  corrediça) (`WNukGXTt2XY-0122`). Bate com o padrão A = 13, se as laterais do módulo forem de 15.

### Frentes e distribuição no vão
- **VISTO**: frente de 194 em módulo de 200 (3 mm por lado) e 170,3 de altura em gaveteiro de 700 com 4 gavetas
  (`WNukGXTt2XY-0132`). As 4 gavetas são iguais na biblioteca (não se viu como mudar alturas individuais).
- **DITO**: folga de porta 3 mm em cima e embaixo; folga entre portas 3 mm (`Or7qXPijqLA [10:12]`–`[10:26]`, `[13:29]`–`[13:37]`).
- **DITO**: trocar o modelo da frente (ex.: Gola) devolve a frente ao tamanho original: aplicar o modelo antes de
  redimensionar (`WNukGXTt2XY [1:36]`–`[2:06]`).
- **VISTO**: Aberturas > Gavetas mostra quanto a gaveta abre (303, 400) (`WNukGXTt2XY-0014`, `-0112`).

---

## 4. Três maneiras de fazer módulos

| Maneira | O que é | Quando usar (DITO / VISTO) | Limites |
| :--- | :--- | :--- | :--- |
| **1. Biblioteca (inserção automática)** | Módulo pronto do catálogo (Cozinhas > Inferiores/Sup.../Composição), medidas editadas no painel Propriedades. | "A maneira mais simples e convencional", "mais comum" (`Or7qXPijqLA [0:09]`–`[0:31]`); usada nas aulas 5 e 6 ("o método rápido", `KQs4HQ6f5Sg [1:15]`–`[1:24]`). | **VISTO**: Largura de alguns módulos é lista de valores (`Ask6ahTwQrU-0209`); se não cabe no plano, oferece a largura que cabe (`Ask6ahTwQrU-0221`). Estrutura interna fixa do item. |
| **2. Construtor de Armários** | Editor 2D em janela própria: escolhe o tipo de estrutura (Inferior c/ Divisória, Gaveteiro, Superior, Torre...) e preenche abas Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos. | Quando o módulo não existe pronto ou o cliente quer divisão própria (`WNukGXTt2XY [0:45]`–`[0:53]`: "vai fazer manual o seu móvel da forma que você quiser"). Resultado igual ao da biblioteca (`Or7qXPijqLA [2:22]`–`[2:36]`). | **VISTO**: o resultado vira "(Item Extra) ... Inferior (1200x700x550)" (`Or7qXPijqLA-0258`). Peças de 15 mm conforme o tipo. |
| **3. Composição peça por peça** | Peças avulsas de Cozinhas > Composição (Laterais/Divisórias, Bases, Fundos, Sarrafos, Diversos, Gaveta, Painéis) + Portas/Frentes, posicionadas e medidas à mão, depois agrupadas. | "Exatamente igual a construção de um móvel na vida real" (`Or7qXPijqLA [2:52]`–`[3:01]`). | **DITO**: exige calculadora para vãos, folgas e sobreposições (`[2:47]`–`[2:52]`, `[7:49]`–`[8:17]`). Usar a peça com o nome certo, senão plano de corte e etiqueta saem errados (`[4:33]`–`[5:17]`). Agrupar o gabinete (`[11:20]`–`[11:37]`). |

Geometria livre (aula 3) é uma quarta ferramenta, para bancada, base, rodapé e tampos, não para armário.

### Construtor de Armários: o que se viu de cada aba
- **Estrutura**: Número de vãos, Largura total, Altura, Profundidade, Posição (Inferior esquerda / Livre) e quatro
  cotas até as paredes; lista Componentes com caixas de marcar (laterais, divisória, base, sarrafos); Movimentação
  (Passo inicial 0, Passo 10) (`Or7qXPijqLA-0057`).
- **Divisões**: Vertical ("Interna 15mm / Divisória 15"), Horizontal (Prateleiras Móveis / Fixas / Sem Prateleira;
  "Interna c/ Recuo Fron 15mm", "Interna s/ Recuo Fron 15mm"), Inserção múltipla (grade, orientação prioritária)
  (`Or7qXPijqLA-0130`, `-0149`).
- **Portas**: Ambas, Inteira, Esquerda, Direita, Basc Inf, Basc Sup; modelos; "Inserir invertido"; aplica-se clicando no
  vão (`Or7qXPijqLA-0201`).
- **Gavetas, Internos, Deslizantes, Fundos**: só os nomes das abas foram vistos.

---

## 5. Configurações gerais que afetam a construção

- **Configurador de Dimensões** (o "construtor de regras"): configuração nomeada por linha e chapa, ex. "COZ - MDF 18 -
  Fundo encaixado - Sarrafo tras horizontal"; variantes por espessura (MDF 15/18), tipo de fundo (encaixado, pregado,
  rebaixado, travessas), posição do sarrafo traseiro (horizontal/vertical) e, em dormitórios, base (lateral alinhada
  com base / lateral sobre base). Ao editar vira "(alterado)"; aplica nos itens selecionados e/ou existentes
  (`jtEjP6DrzpM-0025`, `-0041`, `-0219`).
- **Chapas por peça**: cada peça (Lateral, Divisória, Base, Fundo - Inferiores, Fundo - Superiores, Traseira, Travessas,
  Prateleira, Portas/Frentes, Painel p/ Portas, Frente Gav Int, Tampo, Tamponamento, Painel, Especial, Gavetas...) tem
  Material, Largura Máxima da Chapa, Comprimento Máximo da Chapa, Espessura e Fita Borda 1..4 para o plano de corte
  (`jtEjP6DrzpM-0514`). Chapa padrão vista: 2750 x 1830.
- **Espessuras vistas**: caixa 15 mm (construtor e composição, `Or7qXPijqLA-0057`, `-0258`); configuração MDF 18 no
  vídeo de gavetas; lateral de gaveta 18; fundo de gaveta 6; porta/frente 18 (`Or7qXPijqLA-1106`, `WNukGXTt2XY-0132`).
- **Modelos (estilo)**: painel com "Todos" e "Seleção" que define por categoria Caixas, Portas, Frentes, Fitas de
  borda, Dobradiças, Corrediças, Puxadores, Maçanetas; "Aplicar Estilo" (`Ask6ahTwQrU-0449`).
- **Preferências**: unidade Milímetro; incremento de movimentação 50; tipo de preenchimento; pasta do projeto
  (`Ww5hO_awl7Q-0102`, `-0112`, `-0120`).
- **Cotas automáticas**: ao inserir, o módulo mostra a distância até os obstáculos (1339,5 / 1025; 876,3), e a parede
  tem marcas de altura 150, 820, 1470, 2010, 2280, 2550 (`Ask6ahTwQrU-0105`, `Or7qXPijqLA-0025`). As marcas parecem
  as alturas de referência de cozinha (rodapé, bancada, aéreos); a origem delas (HotPoints?) não foi mostrada.
- **Painel de propriedades padrão** de todo item: Cotas (Afastamento Parede/Piso, Cota Anterior, Inferior, Posterior,
  Superior), Dimensões (Largura, Altura, Profundidade, Escalar), Entidade (ex. Quantidade Gavetas), Orçamento, Outras
  (Camada, Observações), Perfurante (Furar, Profundidade), Posição Absoluta, Posição Relativa.

---

## 6. Parâmetros

| Parâmetro (nome exato) | Onde | Padrão | Unid. | Faixa / valores vistos | Fonte |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Número de vãos | Construtor > Estrutura | 1 | — | spinner | `Or7qXPijqLA-0057` |
| Largura total | Construtor > Estrutura | 500 | mm | 1200 no exemplo | `Or7qXPijqLA-0057` |
| Altura | Construtor > Estrutura | 700 | mm | — | `Or7qXPijqLA-0057` |
| Profundidade | Construtor > Estrutura | 550 | mm | — | `Or7qXPijqLA-0057` |
| Posição | Construtor > Estrutura | Inferior esquerda | — | Inferior esquerda, Livre | `Or7qXPijqLA-0057`, `-0130` |
| Lateral Esquerda / Direita 15mm, Divisória, Base Inferior 15mm, Sarrafo Frontal 15mm | Construtor > Componentes | marcados | — | caixa de marcar | `Or7qXPijqLA-0057` |
| Sarrafo Inteiro 15mm | Construtor > Componentes | desmarcado | — | caixa de marcar | `Or7qXPijqLA-0057` |
| Passo inicial / Passo | Construtor > Movimentação | 0 / 10 | mm | — | `Or7qXPijqLA-0057` |
| Quantidade Gavetas | Propriedades > Entidade | 4 (4G) | un | 2 (Gavetões) | `Ask6ahTwQrU-0209`, `-0313` |
| A - Folga Corrediça | Configurador > Gavetas > Folgas | 13 | mm | 5 (invisível) | `jtEjP6DrzpM-0107`, `-0708` |
| B - Folga até Fundo da Caixa | idem | 30 | mm | — | `jtEjP6DrzpM-0107` |
| C..H - Folga Superior/Inferior Contra-Frente/Lateral/Posterior | idem | 20 cada | mm | 25, 36 | `jtEjP6DrzpM-0107`, `-0219` |
| A - Avanço Fundo sobre Lateral | Configurador > Gavetas > Fundos | 5 | mm | 0 (fundo pregado) | `jtEjP6DrzpM-0338`, `-0546` |
| B - Avanço Fundo sobre Frente/Contra Frente | idem | 5 | mm | 18 | idem |
| C - Avanço Fundo sobre Posterior | idem | 5 | mm | 18 | idem |
| D - Recuo Fundo | idem | 10 | mm | — | idem |
| Espessura da Chapa (Fundo de Gaveta) | Configurador > Chapas > Gavetas > Fundo | 6 | mm | 15 (DITO) | `jtEjP6DrzpM-0514`, `[4:59]` |
| Largura / Comprimento Máximo da Chapa | Configurador > Chapas | 2750 / 1830 | mm | — | `jtEjP6DrzpM-0514` |
| Fita Borda 1..4 | Configurador > Chapas | 0 | mm | — | `jtEjP6DrzpM-0514` |
| Corrediças | Modelos > Acessórios | 500 Apoiada | — | 500 Telescópica | `Ask6ahTwQrU-0449`, `jtEjP6DrzpM-0708` |
| Dobradiças | Modelos > Acessórios | Padrão - Sem Amortecedor > Reta / Baixa | — | — | `Ask6ahTwQrU-0449` |
| Portas (modelo) | Modelos | Madeira > Reta | — | Lisa, Almofada, Fresada, Colonial, Bicolor, Gola Horizontal/Vertical, Borda Alumínio, Cava, Cava Vertical | `Ask6ahTwQrU-0446` |
| Altura (geometria retangular) | Construir Geometria Retangular | 150 | mm | — | `7yfwF-BIyl8-0137` |
| Espessura (lineares) | Construir Lineares | 18 | mm | — | `7yfwF-BIyl8-0444` |
| Altura / Ângulo / Incr. Linear / Incr. Angular | Construir Lineares | 150 / 10 / 50 / 5 | mm, ° | — | `7yfwF-BIyl8-0444` |
| Incremento da movimentação | Preferências | 50 | mm | — | `Ww5hO_awl7Q-0112` |
| Profundidade (aéreo Sup Altos) | Biblioteca | 320 | mm | 600 sobre geladeira | `KQs4HQ6f5Sg-0346`, `-0546` |
| Altura (aéreo Sup Altos 2P) | Biblioteca | 950 | mm | 700 | idem |
| Posição Absoluta Z (aéreo) | Propriedades | 1650 | mm | 1900 | idem |
| Altura / Profundidade (balcão) | Biblioteca | 700 / 550 (5.37) ou 560 (5.38) | mm | — | `Or7qXPijqLA-0025`, `Ask6ahTwQrU-0209` |

---

## 7. Regras observadas

1. Balcão, aéreo, gaveteiro e torre são **tipos de estrutura diferentes** desde a escolha inicial do Construtor, com
   montagem e fundo configurados separadamente para inferior, superior e despenseiro (`Or7qXPijqLA-0049`, `jtEjP6DrzpM-0025`).
2. O balcão de cozinha usa **sarrafo frontal** no alto, não tampo inteiro; o sarrafo inteiro é opcional
   (`Or7qXPijqLA-0057`).
3. O vão interno = medida externa - espessuras das peças de caixa: 1200 - 2 x 15 = 1170; 700 - 15 - 15 = 670
   (`Or7qXPijqLA-0130`; DITO `[4:05]`–`[4:24]`).
4. Porta sobreposta: 3 mm de folga em cima, embaixo e entre portas; cobre 12 dos 15 mm da lateral e 5 mm da divisória
   (DITO `Or7qXPijqLA [10:12]`–`[10:45]`, `[13:19]`–`[13:46]`; VISTO 402 x 694 em `-1106`).
5. Frente de gaveta = largura do módulo - 6 (194 em 200) (`WNukGXTt2XY-0132`).
6. Caixa da gaveta é calculada por folgas relativas à frente e ao módulo (Folga Corrediça na largura; folgas
   superior/inferior nas alturas da contra-frente, lateral e traseira) (`jtEjP6DrzpM-0107`, `-0219`, `-0642`).
7. Mudar o tipo de corrediça muda a Folga Corrediça (13 → 5) (`jtEjP6DrzpM-0642`, `-0708`).
8. O fundo da gaveta muda os avanços: em canal avança 5 sobre as laterais; pregado por baixo avança 18 sobre a
   frente e a traseira e 0 nas laterais (`jtEjP6DrzpM-0338`, `-0546`).
9. Regras ficam numa configuração nomeada e reaplicável a itens existentes, não em cada módulo (`jtEjP6DrzpM-0025`).
10. Ao inserir, o módulo se ajusta ao espaço livre; se a largura pedida não cabe, oferece a que cabe
    (`Ask6ahTwQrU-0221`; DITO `[1:46]`–`[1:53]`).
11. Trocar o modelo de frente/porta restaura o tamanho padrão da frente (DITO `WNukGXTt2XY [1:43]`–`[2:06]`).
12. Cada peça tem nome e tipo (lateral, base, sarrafo, prateleira, divisória com fita frontal) porque isso define fita de
    borda e etiqueta no plano de corte (DITO `Or7qXPijqLA [4:49]`–`[5:17]`).
13. Cuba e similares são "perfurantes": furam a peça onde são colocados (`-YuVfTyKyPY-0047`).
14. Aéreo sobre geladeira com profundidade da geladeira (600) para fixação em parede e lateral (DITO `KQs4HQ6f5Sg [5:59]`–`[6:16]`).

---

## 8. Lacunas

- **Construtor**: as abas Gavetas, Internos, Deslizantes e Fundos não foram abertas; o resto da lista de Componentes
  (abaixo de "Sarrafo Frontal 15mm") ficou fora da tela.
- **Tipos superiores e torre no Construtor**: só os nomes; peças e padrões de "Superior c/ Divisória" e "Torre p/
  Eletros" não vistos.
- **Configurador de Dimensões**: não se abriram Dimensões Externas, Montagem da Caixa - Inferior/Superior/Despenseiro,
  Frentes/Portas, Fixação Lateral, Gavetas Internas, Medidas Máximas. As folgas de porta (3 mm) e as sobreposições
  (12/5 mm) só foram DITAS na peça por peça, não vistas como campos.
- **Grupo "Gavetão"** no Configurador de Folgas ficou cortado (`jtEjP6DrzpM-0107`).
- **Distribuição das gavetas**: não se viu como definir alturas diferentes por gaveta; 170,3 por frente em 700 com 4
  gavetas não fecha com uma conta simples a partir dos dados vistos.
- **Cotas dos vãos no construtor**: 790 + 380 = 1170 e 342,5 + 327,5 = 670 somam o vão inteiro sem descontar divisória
  e prateleira; parece cota de eixo, não confirmado (`Or7qXPijqLA-0201`).
- **Aéreo**: profundidade dita 35 x vista 320; altura dos Sup Baixos e Sup Médios não lida com confiança.
- **Tampo**: a "Altura 150" do tampo a Z 840 (`-YuVfTyKyPY-0230`) não foi explicada (espessura padrão da geometria
  nunca alterada?); a narração da aula 3 sobre a altura da bancada está truncada.
- **Corrediça invisível**: a legenda sobre "3 de cada lado"/"5 de cada lado" está confusa; só o valor 5 foi visto.
- Aulas 7 e 8 (render) e aula 2 (paredes) fora deste grupo.
