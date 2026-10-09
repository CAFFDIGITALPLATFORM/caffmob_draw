# Editor de paredes, propriedades, "Mover Sobre" e geometria

Guia rápido das ferramentas da planta e do posicionamento.
Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**.

## 1. Editor de Paredes (planta 2D)

Abra por **Construir** › **Editor de Paredes**, pelo menu do botão direito de uma parede (**Editar Paredes…**) ou
pelo grupo **Parede** da janela de propriedades.
O editor abre numa janela própria, com a planta vista de cima. Ele só mostra paredes.
Paredes feitas com o construtor antigo (camada nova) aparecem tracejadas, só como referência. Se elas estiverem
selecionadas ao abrir o editor, ele pergunta:
- **Converter para paredes editáveis:** viram trechos normais da planta; no OK, são trocadas por paredes normais do CAFFMob Draw no mesmo lugar.
- **Só referência:** continuam tracejadas.
Nada vai para o 3D até você clicar em **OK** (no fim do painel). **Cancelar** (ou **Esc**) fecha sem mudar nada; se você
já mudou algo, ele pergunta antes de descartar.

**Medidas:** a **linha interna (tracejada)** é a medida real, o espaço útil. A **externa (contínua)** é a interna mais
a espessura das paredes. Tudo o que você digita vale para a linha interna, salvo quando você seleciona a externa.

**Navegar:** arraste com o botão do meio para mover a vista. A roda aproxima e afasta. **Home** ou **Enquadrar Tudo** mostram todas as paredes.

**Ferramentas** (painel da direita):
- **Mira:** nos modos Selecionar/Mover e Construir Parede, duas linhas finas atravessam a vista pelo cursor, uma
  horizontal e uma vertical. Quando o cursor chega a uns **8 px** da altura (Y) ou do alinhamento (X) de um vértice de
  qualquer parede, a linha correspondente **trava** nele:
  - a linha fica destacada;
  - uma guia tracejada vai até o vértice, que ganha um anel.

  O clique sai **pareado**: a mesma coordenada exata do vértice, mesmo que ele esteja do outro lado da planta. As
  duas linhas podem travar juntas. Segure **Shift** para desenhar sem o alinhamento (a trava reta e o ímã continuam).
- **Contas na medida:** em qualquer lugar onde você digita uma medida, dá para escrever uma conta com `+ - * /` e
  parênteses: `2*8`, `200/2`, `(3000-150)/2`. O resultado aparece ao lado (`= 16 mm`) antes do Enter. Cada número
  pode ter unidade (`1,5m+20`); sem unidade, vale a do projeto. Uma conta inválida (`10/0`) mostra **Valor Inválido**
  e não muda nada.
- **Selecionar/Mover:**
  - Clique na linha **interna** (tracejada) ou na **externa** de uma parede e **digite a nova medida** em mm, depois **Enter**. Exemplo: clique na interna de 2.400, digite `3000` e Enter; a interna vira 3.000 e a externa 3.000 + espessuras.
  - Clique num **vértice** (quadrado) e digite: muda o trecho que termina nele.
  - **Backspace** corrige a digitação; **Esc** apaga o que foi digitado.
  - A seta mostra o sentido do trecho. Arraste um vértice para mudar o desenho; perto da horizontal ou da vertical, o trecho trava reto.
  - **Delete** remove o trecho selecionado.
- **Construir Parede** (lápis):
  1. Clique no ponto inicial.
  2. Mova o mouse na direção da parede e digite o comprimento (por exemplo `3000`) e **Enter**, ou clique no ponto
     final.
  3. A direção fica **travada**: a seta no último ponto mostra qual é ("→ 0°"). Os próximos Enter seguem nela, e mover
     o mouse **não** muda a direção. Por exemplo, `100` Enter, `285` Enter, `2*8` Enter, `200/2` Enter e `2000` Enter
     criam cinco paredes seguidas, de 100, 285, 16, 100 e 2000 mm, para o mesmo lado. Cada Enter é uma parede
     separada, também depois do OK.
  4. Para mudar de direção:
     - **setas do teclado:** → 0°, ↑ 90°, ← 180°, ↓ 270°, sem criar parede;
     - **clique na nova direção:** cria a parede até o ponto clicado, e a direção dela passa a valer para os próximos
       Enter.
  5. Para fechar a sala, volte ao ponto inicial: perto dele (15 px) o cursor **gruda** no ponto, que fica destacado com "Fechar". Clique e responda **Sim** a "Deseja fechar a parede?". Chegar ao início digitando a medida, ou arrastando o último vértice até ele, faz a mesma pergunta; **Não** mantém o desenho aberto. A espessura vai sozinha para o lado de fora, qualquer que seja o sentido em que você desenhou.
  6. **Esc** termina o desenho aberto.
- **Inverter Sentido**, **Adicionar Vértice** (divide o trecho clicado) e **Remover Vértice** (une os dois trechos do vértice clicado).

**Painel** (trecho selecionado):
- **Linha:** interna ou externa.
- **Comprimento:** medido na linha escolhida.
- **Ângulo Absoluto**, **Ângulo Relativo** e **Bloquear Ângulo**.
- **Espessura**, **Pé-direito Inicial** e **Pé-direito Final**.
- **Direção (Esquerda/Direita):** para que lado da linha interna a parede cresce. Trocar a Direção passa a espessura para o outro lado sem mudar a medida interna. Em paredes já existentes, no OK elas mudam de sentido e os itens presos ficam onde estão.
- **Tipo:** Normal; Divisória (100 mm); Mureta (1.100 mm).

Um valor fora da faixa mostra **Valor Inválido** e não muda o desenho.
O ângulo do arco aparece desabilitado: as paredes são sempre retas.

**Grid:** **Tamanho** da grade e **Linhas Magnéticas** (os vértices encaixam nos cruzamentos). Os campos de **Novas paredes** valem para o lápis.

**Pé-direito:** as paredes novas nascem com o **pé-direito do projeto** (definido em **Construir** › **Paredes**). Mureta fica com 1.100 mm.

**OK:** se algum módulo, porta ou janela não couber numa parede encurtada, o editor lista os itens. Paredes com altura diferente do projeto aparecem com a caixa **Igualar ao pé-direito do projeto** (marcada; Mureta, meia-parede e parede falsa ficam de fora). Se você apagou um trecho que tinha módulos, ele lista os módulos e mostra a caixa **Remover os módulos junto?** (desmarcada: os módulos ficam soltos no lugar). Clique **OK** de novo para aplicar.
O OK é um único passo de desfazer (Ctrl+Z).
Pisos e tetos que já existem são refeitos com o contorno novo. Uma sala cujo último ponto ficou em cima do primeiro é sempre fechada no OK — nenhuma parede fica solta no canto.

**Mudar o pé-direito em Construir › Paredes** atualiza sozinho todas as paredes de altura cheia do projeto (Mureta, meia-parede e parede falsa ficam como estão). Ctrl+Z desfaz.

**"Desenhar Paredes" (3D)** tem o mesmo ímã: perto do ponto inicial o cursor gruda e aparece "Deseja fechar a parede?"; **Enter** ou clique fecha, **Esc** continua desenhando. Digitar a medida que termina no início também pergunta. A tecla **C** fecha direto.

## 1a. Portas e janelas reais

Em **Construir › Aberturas**, a porta e a janela entram como peças reais, não como uma caixa com o texto "DOOR" ou
"WINDOW":
- **Porta** (simples, 80 × 210 cm por padrão), com:
  - marco com a profundidade da parede e guarnições nos dois lados;
  - folha de nogueira de 40 mm com duas almofadas;
  - maçanetas de alavanca, fechadura e três dobradiças.
- **Porta dupla** (160 × 210): duas folhas que se encontram no meio.
- **Vão aberto**: só marco e guarnições.
- **Janela de correr**, com:
  - marco de alumínio;
  - duas folhas de vidro em trilhos;
  - puxadores e peitoril de granito.

Como funciona:
- **Medida:** a largura e a altura que você digita ao colocar a porta, ou nos prompts, são as da **folha**. O furo na
  parede fica um pouco maior, para caber o marco (com 80, o furo tem 89,8 cm).
- **Abertura:** na seção **Selecionado**, a barra de abertura gira a folha até 90° (e corre a folha da janela até o
  batente). A folha para se esbarrar numa parede ou num móvel. O lado e o sentido seguem o símbolo de giro: **Inverter
  giro** e **Inverter mão** refazem a porta.
- **Medidas e espessura:** mudar a largura, a altura ou a espessura da parede (no editor de paredes) refaz a porta e
  a janela, sem distorcer maçanetas e dobradiças.
- **Caixa de referência:** a caixa da abertura continua cortando a parede, mas aparece só em arame. "Mostrar caixas
  de portas e janelas" mostra ou esconde essa caixa.
- **Arquivo antigo:** as portas e janelas em caixa continuam como estavam. A seção **Construir** avisa quantas são e
  oferece **Atualizar portas e janelas**, que troca todas pela versão real nas mesmas posições e medidas.
- **Plano de corte:** as peças da porta ficam fora por padrão. Para uma folha entrar no corte, marque-a como peça de
  produção na seção Selecionado.

### Porta ou janela numa região marcada

Para a porta ou a janela ocupar um vão que você já conhece, marque a região na parede antes de escolher a abertura:
1. Em **Construir › Aberturas**, clique em **Marcar região**.
2. Clique num canto do vão na parede e depois no canto oposto. Os cantos andam na grade de 10 mm (com **Shift**,
   1 mm). Um clique um pouco abaixo do piso ou além da ponta da parede vale como a borda.
3. A região fica desenhada em azul na parede, com as medidas. Na barra lateral, **Esquerda**, **Direita**, **Base** e
   **Topo** acertam os cantos pelo teclado.
4. Escolha a porta (simples, dupla ou vão aberto) ou a janela. Ela já aparece na região; tecle **Enter** ou clique
   para confirmar.

O furo na parede fica **exatamente** do tamanho da região, sem nenhum milímetro a mais na largura ou na altura (sem a
região, a medida digitada é a da folha e o furo sai um pouco maior):
- a **porta** encosta no piso e vai até a borda de cima da região, mesmo que a região comece acima do piso;
- a **janela** usa a borda de baixo da região como peitoril.

Se a região passa da ponta da parede, é mais alta que ela ou encosta em outra porta ou janela, um aviso diz o motivo e
a inserção segue presa ao cursor, como sempre. **Esc** durante a inserção cancela a porta e mantém a região; **Esc** na
vista 3D ou o **X** ao lado de **Marcar região** apaga a região.

## 1b. Modo de vista

No topo da seção **Construir**:
- **Sólido · Textura:** Textura mostra as texturas dos materiais (a madeira, o granito) na vista sólida;
- **Linhas** (o botão ao lado): desenha as arestas de todos os objetos, finas e escuras, por cima da vista.

"Textura com linha" é Textura com Linhas ligado. O estado escrito embaixo mostra o modo atual. O modo vai salvo no
arquivo e volta ao abri-lo.

## 2. Remover, rebaixar e esconder paredes

No menu do botão direito da parede, ou no grupo **Parede** da janela de propriedades:
- **Remover Parede…** abre três opções:
  - **Segmento:** só o trecho; numa sala fechada, abre o contorno.
  - **Tudo:** o contorno inteiro ligado ao trecho.
  - **Manter o selecionado:** remove os outros trechos.

  Marque **Remover módulos que estão na parede** para apagar os módulos junto. Sem essa marca, eles ficam soltos no lugar. Portas e janelas sempre saem com a parede.
- **Rebaixar Parede:** a parede some da viewport e fica só uma faixa de 150 mm no piso, para ver o interior. As medidas e o pé-direito não mudam. Clique de novo (**Restaurar Altura**) para voltar.
- **Visibilidade:** vale para paredes e tetos.
  - **Invisível:** mostra só o contorno.
  - **Esconder contorno:** nem o contorno aparece. Use **Alt+H** para mostrar de novo e escolha **Visível**.

## 3. Janela de propriedades

A seção **Selecionado** muda conforme o objeto selecionado:
- **Módulo**, ou uma porta ou peça dele:
  - **Dimensões**, sempre do módulo inteiro;
  - **Cotas:** anterior e posterior até o vizinho ou o fim da parede, inferior até o piso, superior até o teto e afastamento da parede.
    Digite uma cota e o módulo se move sem mudar de tamanho. O botão **Mover na Parede** fica neste grupo;
  - **Abrir:** portas e gavetas;
  - **Ações:** os comandos da linha.
- **Parede:** comprimento, alturas e espessura, além do editor e das operações da seção 2.
- **Porta ou janela de ambiente:** largura, altura e peitoril.
  Portas com símbolo de abertura têm o grupo **Abrir** (90°, 45°, Fechar). No primeiro **Abrir**, a porta ganha uma folha 3D, que gira para o lado desenhado no símbolo. Porta dupla abre as duas folhas.
  A porta é salva fechada, como as frentes dos módulos. Janelas e vãos sem porta não têm **Abrir**.
- **Geometria:** veja a seção 5.

Com um módulo selecionado, as cotas também aparecem desenhadas no 3D.

## 4. Mover Sobre e Mover na Parede

**Mover Sobre** (funciona com o botão direito em qualquer modo da viewport, inclusive em Edição):
1. Ligue **Mover Sobre** no HUD da viewport, no menu do botão direito do módulo ou em **Selecionado** › **Posição e vínculo**.
2. Com o botão direito, arraste o módulo A até o módulo B (ou até uma parede) e solte.
3. Abre uma janela com as vistas **superior** e **frontal**, só com A e B:
   - **Vista superior:** clique perto de um lado de B para encostar A nele. Clique perto de uma profundidade (0, 30, 50, 75 ou 100%) para alinhar a frente de A.
   - **Vista frontal:** clique perto de uma altura para alinhar a base de A. Clique acima do topo de B para empilhar A sobre B.
   - Os campos aceitam medidas digitadas; **Tab** passa para o próximo.
4. **Enter** confirma e **Esc** cancela; A volta para onde estava. A janela avisa se A ficar sobreposto a outro módulo.

Na mesma janela (recursos do Reposicionar do Promob):
- **Rotação:** gira A em graus em torno do centro da base dele.
- **Passo:** as setas movem A em X e na profundidade; **Page Up** e **Page Down** movem na altura.
- **Posição relativa / absoluta:** troca o que os campos X, Y e Z mostram, a distância até B ou a posição no projeto. Nada se move ao trocar. No modo absoluto, o valor digitado vira a posição no projeto.
- **Salvar posição:** guarda a posição de A em relação a B, com a rotação. Os botões ao lado aplicam uma posição salva a outro par, por exemplo o mesmo nicho em outro quarto.
- **Substituir:** troca A por um módulo da biblioteca de módulos, no mesmo canto de referência e com a mesma rotação.

**Plano de inserção:** no menu de contexto do objeto, escolha **Usar como plano de inserção** e clique numa face.
As inserções e os movimentos que não acertam nenhum objeto passam a usar essa face no lugar do piso. Para desfazer,
use **Limpar plano de inserção**, que fica no mesmo menu e em **Selecionado** › **Posição e vínculo**.

**Mover na Parede:** use o botão no grupo **Cotas**. O módulo segue o mouse ao longo da parede, sem se afastar dela; com **Shift**, ele sobe e desce.
Com **Evitar Sobreposição** ligado, o módulo para no vizinho e nas pontas da parede. As cotas mudam ao vivo no cabeçalho e no 3D.
Clique para confirmar ou tecle **Esc** para voltar.

## 5. Geometria livre: placa e caixa

**Criar:** **Construir** › **Geometrias** › **Placa** ou **Caixa**.
1. Clique no canto da peça (com **Ctrl**, ela encaixa em vértices e arestas).
2. Mova o mouse para definir largura e profundidade. Para digitar, escreva a largura e tecle **Enter**, depois a profundidade e **Enter**.
3. Na caixa, defina também a altura.
4. **Esc** cancela e não deixa nada na cena.

**Editar:** selecione a peça. O grupo **Geometria** mostra:
- forma e posição da placa (deitada, em pé de frente ou em pé de lado);
- medidas e espessura (mudar a espessura não move a face de apoio);
- posição;
- **Duplicar**, **Espelhar** e **Excluir**, todos com Ctrl+Z.

**Peça de fabricação:** marque e escolha **Componente**, **Matéria-prima** e **Acabamento**.
- A placa entra na lista de peças como uma chapa.
- A caixa entra como seis chapas na espessura escolhida: fundo, tampo, duas laterais, frente e trás.

Elas aparecem no plano de corte e no JSON de produção com origem `FREE_GEOMETRY`.
Sem a marca, a geometria é só visual e fica fora do orçamento.
