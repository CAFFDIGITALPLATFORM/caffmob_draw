# Configurador de Dimensões e produção

Guia rápido para quem projeta e produz móveis planejados no CAFFMob Draw.
Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**.

## 1. Unidade de medida

Em **CONFIGURAÇÕES › Unidade & Precisão**, escolha milímetros, centímetros ou metros.
Os campos, as cotas e as listas passam a usar essa unidade, com vírgula decimal.
Ao digitar uma medida, aceite tanto `755,5` quanto `755.5`. Também pode digitar com sufixo, como `60cm` ou `0,6m`; o sufixo vale mais que a unidade escolhida.
Frações e pés/polegadas não são aceitos.

## 2. Padrão de Dimensões

O Padrão de Dimensões é a regra da empresa que todos os módulos seguem: medidas externas por linha (cozinha, dormitório, banheiro, sala, escritório), matéria-prima, espessura, limite de chapa e fitas de borda de cada componente.

- **Padrão Brasil** e **Padrão EUA (HB5)** vêm prontos e são somente leitura.
- Para ajustar, use **Duplicar** (ícone de cópia). A cópia passa a ser a definição ativa.
- O menu com o nome da definição troca a definição ativa. Depois da troca vêm as perguntas de **Aplicar o padrão à
  cena** (abaixo).

### Montagem: lateral passante ou base passante

O padrão também define a montagem da caixa dos armários CAFFMob:
- **Lateral passante** (padrão): as laterais vão do piso ao topo; base e tampo ficam entre elas.
- **Base passante**: a base ocupa a largura toda e as laterais ficam em cima dela. O tampo continua entre as laterais.

A montagem fica no Configurador (abaixo da árvore) e pode ser trocada em cada armário, no editor de armário (aba
Estrutura) ou na seção Selecionado. A lista de corte segue a montagem de cada armário.

### Aplicar o padrão à cena

Quando o padrão global muda (Configurador, Aplicar ou troca da definição ativa), o sistema pergunta:
1. **"Aplicar a todos os módulos existentes na cena?"**, com as contagens. **Sim** atualiza os armários CAFFMob que
   seguem o padrão: chapas e medidas da linha de cada um (a largura fica). **Cancelar** (Não) deixa a cena como está;
   só os armários novos usam o padrão.
2. Se houver armários com **padrão próprio** (montagem, espessura ou medida mudadas à mão) ou criados com outro
   padrão, vem a segunda pergunta: **"Aplicar também nos móveis que diferem do padrão global anterior?"**. **Sim**
   leva esses também ao padrão; **Cancelar** (Não) os deixa como estão.

**Não aplicável**: itens importados (SketchUp, OBJ), objetos da biblioteca de objetos e armários das bibliotecas
antigas ainda não convertidos não mudam. Converta os antigos para CAFFMob para que eles recebam o padrão.

### Configurador

Em **CONFIGURAÇÕES › Padrão de Dimensões**, clique em **Abrir Configurador de Dimensões**.

1. Na árvore à esquerda, clique numa linha (ex.: *Cozinhas*) para abrir. Depois abra *Chapas › Lateral*.
2. Clique num parâmetro (ex.: *Espessura da Chapa*). À direita aparecem a imagem de referência, o campo do valor e a faixa permitida.
3. Digite o valor e confirme. Um valor fora da faixa aparece em vermelho e não é aceito.
4. Use **Buscar** para filtrar por nome (ex.: "fita").
5. Embaixo ficam as **alterações pendentes**, com o valor anterior e o novo.
6. **Aplicar** grava a definição; em seguida vêm as perguntas de **Aplicar o padrão à cena**.
7. Fechar sem aplicar descarta as alterações.

Depois de aplicar, uma janela mostra três listas:
- os módulos atualizados;
- as medidas manuais preservadas;
- os parâmetros que só valem para a lista de peças, porque ainda não têm destino nas bibliotecas.

### Fitas de borda

Os lados 1 e 2 são as bordas do comprimento da peça; os lados 3 e 4 são as bordas da largura.
A fita só entra na peça quando o módulo tem fita naquela borda. A espessura vem do componente no padrão.

### Arquivos do padrão

- **Exportar / Importar** grava e lê a definição em `.btmdim.json` (para levar o padrão a outro computador ou projeto).
- **Importar do Promob** lê o arquivo de configuração de dimensões exportado pelo Promob (`DIMENSIONEXPORT`, `.xml`).
  - A nova definição recebe o nome do arquivo.
  - O relatório mostra quantos atributos foram reconhecidos.
  - Os não reconhecidos são guardados e voltam iguais em **Exportar p/ Promob**.
  - A definição importada não vira ativa sozinha: use o menu da definição ativa.
  - A montagem vai num atributo próprio, `CAFF_MONTAGEM` (`LATERAL` ou `BASE`), no fim do arquivo exportado. O
    Promob ignora esse atributo; um arquivo sem ele é lido como lateral passante.

## 3. Lista de peças e plano de corte

Em **Produção/Projeto** › **Plano de corte**:

1. **Calcular Plano de Corte** lê as peças reais dos módulos e monta a lista. Cada peça traz componente, medidas de corte, espessura, matéria-prima, acabamento e fitas. O cálculo distribui as peças em chapas, separadas por matéria-prima, espessura e acabamento.
2. **Peças maiores que o limite de chapa** do componente aparecem em vermelho, com a medida e o lado que excede.
3. Se você mover ou alterar um módulo depois do cálculo, aparece o aviso **"O projeto mudou: recalcule o plano de corte."**

Os tamanhos de chapa, o refilo, a espessura da serra, a rotação e o veio ficam em **CONFIGURAÇÕES › Limites & Configurações de Chapas MDF**.

## 4. Exportar a produção

- **Exportar JSON Global** grava, num só arquivo, o projeto, o padrão usado, os materiais, os módulos, as peças e o plano de corte, em mm. Desmarque **Incluir dados do cliente** para enviar o arquivo a terceiros sem nome e contato do cliente.
- **Importar JSON Global** lê um arquivo exportado (inclusive da versão antiga) e mostra o resumo.
- **Exportar Peças (CSV)** gera uma planilha, com uma linha por peça e a quantidade numa coluna. O arquivo usa separador `;`, vírgula decimal e valores em mm, e abre direto no Excel/LibreOffice e em otimizadores de corte.
  - Colunas: id, módulo, peça, componente, comprimento, largura, espessura, quantidade, matéria-prima, acabamento, fitas 1–4, veio e situação.

## 5. Arquivos antigos

Ao abrir um projeto feito antes do Padrão de Dimensões, as configurações antigas de espessuras e componentes que tinham sido alteradas viram a definição **Migrada**, que passa a ser a ativa.
Projetos com gabinetes do CAFFMob Draw sem configuração própria começam no **Padrão EUA (HB5)**, para não mudar medidas já desenhadas. Os demais começam no **Padrão Brasil**.
