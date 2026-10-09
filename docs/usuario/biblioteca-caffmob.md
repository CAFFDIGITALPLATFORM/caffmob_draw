# Biblioteca CAFFMob

Guia rápido da biblioteca de armários. Ela fica num painel no **canto superior esquerdo da Viewport 3D**, com o
rótulo **BIBLIOTECA CAFFMOB**, com ou sem os controles da viewport (HUD) ligados. Clique no rótulo para abrir e
fechar; **Esc** ou um clique fora também fecham.

Todo armário é um **armário CAFFMob**, montado por chapas, com as espessuras, as medidas e a montagem do **Padrão de
Dimensões** ativo (ver [Configurador de Dimensões e produção](configurador-e-producao.md)).

## 1. O painel

Aberto, o painel mostra, nesta ordem:
1. **Criar armário**;
2. as categorias **Cozinha**, **Banheiro**, **Sala** e **Home office**, e depois as que você criou;
3. **Criar categoria**.

Cada categoria usa uma linha do padrão: Cozinha → Cozinhas, Banheiro → Banheiros, Sala → Salas, Home office →
Escritórios. Clique numa categoria para ver:
- os **modelos prontos**: balcão 1 porta, balcão 2 portas, aéreo 1 porta, aéreo 2 portas e torre. Eles entram no
  cursor 3D com as medidas e as chapas da linha da categoria (o aéreo, na altura de instalação do padrão);
- os **seus módulos** salvos naquela categoria.

O balcão gaveteiro entra quando o armário CAFFMob tiver gavetas.

## 2. Criar armário

**Criar armário** abre um diálogo já preenchido pelo padrão: tipo (balcão, aéreo, torre), largura, montagem e linha
(a da última categoria aberta). **Criar** põe o armário no cursor 3D e abre o editor de armário nele. Cancelar não
cria nada.

## 3. Criar categoria

**Criar categoria** pede o nome e a linha do padrão (Cozinha, Dormitório, Banheiro, Sala ou Escritório). A categoria
vale para todos os projetos e é também uma pasta da sua biblioteca de módulos. Nome vazio, repetido ou com `/` é
recusado com o motivo. Para trocar a linha de uma categoria sua, use o ícone de ajuste no topo dela.

## 4. Montagem e padrão próprio

- **Lateral passante**: as laterais vão do piso ao topo; base e tampo ficam entre elas (o padrão).
- **Base passante**: a base ocupa a largura toda e as laterais ficam em cima dela.

A montagem vem do padrão e pode ser trocada em cada armário: no editor (aba Estrutura) ou na seção **Selecionado**.
Um armário com montagem, espessura ou medida diferente do padrão fica marcado como **Padrão próprio**; ao mudar o
padrão global, a segunda pergunta decide se ele muda também.

## 5. Bibliotecas antigas

Frameless, face frame, closets e a biblioteca de molduras saíram da interface. Ao abrir um arquivo antigo com esses
armários:
- um aviso diz quantos são, e **Construir** mostra **Converter para CAFFMob**;
- em **Selecionado**, um armário antigo tem **Converter este para CAFFMob**.

A conversão troca cada armário por um armário CAFFMob com as mesmas medidas externas, posição e parede, com as chapas
e a montagem do padrão ativo. O relatório lista o que cada um perdeu (gavetas, frentes especiais, agregados). Um
Ctrl+Z desfaz a conversão inteira.

Os **grupos salvos** das bibliotecas antigas ("Grupos frameless" e "Grupos face frame") também são convertidos: na
primeira vez que o painel abre, ele oferece **Converter grupos antigos** (o mesmo comando fica em Criar categoria).
Cada grupo vira um módulo CAFFMob na categoria **Geral**; um grupo com vários armários vira um módulo por armário. Os
arquivos originais ficam na pasta `cabinet_groups`.

Para suporte, **Preferências › CAFFMob Draw › Avançado › Mostrar bibliotecas herdadas** traz a interface antiga de
volta.

> Os guias [Editor de armário](editor-de-armario.md) e [Módulos personalizáveis](modulos-personalizaveis.md) ainda
> citam as bibliotecas frameless, face frame e closets: essas partes estão descontinuadas.
