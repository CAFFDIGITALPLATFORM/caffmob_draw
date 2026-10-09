# Seleção por componente

Guia rápido de como portas, janelas e itens importados são selecionados, movidos e apagados como uma coisa só. O
controle fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**, junto dos modos de seleção. Com o
HUD da viewport ligado, ele aparece também no HUD.

## 1. O que é um componente

Componente é um objeto com todas as peças que estão abaixo dele. São componentes:
- a **porta** e a **janela** da parede, com marco, folhas, ferragens e o símbolo de giro;
- um **SketchUp** importado, inteiro, mesmo com componentes dentro de componentes;
- um **OBJ, FBX ou glTF** importado com mais de uma malha: ele entra num grupo com o nome do arquivo;
- um item da **biblioteca de objetos**;
- um **armário**, quando o modo de seleção dele está em **Cabinets** (no closet, **Starters**).

Agregados (feature 003) e itens grudados num móvel (feature 004) são componentes deles mesmos: clicar num agregado
seleciona o agregado, não o móvel. Paredes, piso, teto e malhas soltas são selecionados como sempre.

## 2. Selecionar

Com **Seleção por componente** ligada (o padrão, inclusive em arquivos antigos):
- clicar em qualquer peça seleciona o componente inteiro. Clicar na maçaneta seleciona a porta;
- a seleção por caixa, por laço e pela lista de objetos também sobe para o componente, sem repetir;
- mover (**G**, ferramenta Tweak), girar e **Mover Sobre** levam o componente inteiro. A porta e a janela continuam
  presas à parede.

Armários: no modo **Cabinets**, clicar numa porta ou gaveta seleciona o armário. Nos modos **Bays**, **Openings**,
**Interiors** e **Parts**, a seleção é a de sempre.

## 3. Editar uma peça: Alt + clique

**Alt + clique** seleciona só a peça sob o cursor, sem desligar nada. Use para abrir a folha, trocar o material de uma
parte ou converter peças (**Alt + Shift + clique** soma a peça à seleção; o pai por último). Um clique sem Alt volta a
selecionar o componente.

Com a seleção por componente ligada, o Alt + clique do Blender (lista dos objetos sob o cursor) dá lugar ao da
extensão. Se você usa **Emular mouse de 3 botões** (Alt + clique gira a vista), desligue a seleção por componente para
editar peças.

## 4. Apagar

**X** ou **Delete** apaga o componente inteiro, em qualquer profundidade: apagar a porta não deixa folha, marco nem
ferragens soltos, e o furo da parede sai junto. Um **Ctrl+Z** traz tudo de volta.
- Se o objeto tem agregados, a pergunta de sempre aparece: levar os agregados junto ou deixá-los soltos no lugar.
- Itens grudados são soltos no lugar, nunca apagados.
- Uma parede, o piso e o teto são apagados sozinhos; o que está preso neles fica.

## 5. Desligar

Desligue **Seleção por componente** para voltar ao comportamento do Blender: o clique seleciona a peça, e apagar uma
peça apaga só ela (e o que estiver abaixo dela). O estado fica salvo no arquivo.

## 6. Montar esquadria de um OBJ

O OBJ de uma janela entra num grupo. Selecione o grupo e use **Montar esquadria**: as peças saem do grupo da
importação e viram a esquadria com as folhas.
