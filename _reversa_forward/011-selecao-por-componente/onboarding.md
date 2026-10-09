# Onboarding: testar a seleção por componente e a região na parede

> Identificador: `011-selecao-por-componente`
> Para quem vai testar a feature pela primeira vez no Blender 5.2.

## Preparar

1. Gere e instale o pacote: `python3 build.py`, depois Edit → Preferences → Get Extensions → Install from Disk →
   `caffmob_draw.zip`.
2. Abra um arquivo novo, crie um cômodo com paredes de 150 mm (Construir › Paredes).
3. Confira na barra lateral (N), no bloco do topo, o interruptor **Seleção por componente**: ele vem ligado.

## Seleção por componente

1. Insira uma porta simples (Construir › Aberturas) e clique na maçaneta. Esperado: o vão da porta fica selecionado,
   e só ele.
2. Arraste a porta clicando na folha. Esperado: a porta desliza presa à parede, inteira.
3. Dê **Alt + clique** na almofada. Esperado: só a almofada fica selecionada. Troque o material e confira que só ela
   muda. Um clique sem Alt volta a selecionar a porta.
4. Importe um OBJ com várias malhas (Inserir › Objetos › Importar). Esperado: entra um grupo; clicar num pedaço
   seleciona o grupo, e arrastar move tudo.
5. Faça uma seleção por caixa que pegue peças da porta e do OBJ. Esperado: ficam 2 objetos selecionados.
6. Coloque um armário. Com o modo de seleção **Cabinets**, clique na porta do armário: o armário inteiro fica
   selecionado. Com o modo **Parts**, o mesmo clique seleciona só a peça.
7. Desligue o interruptor e clique na maçaneta: só a maçaneta fica selecionada. Salve, reabra e confira que o
   interruptor continua desligado.

## Exclusão

1. Ligue o interruptor, selecione a porta e tecle X. Esperado: nenhuma peça da porta fica na cena (confira na lista
   de objetos), e a parede fica sem o furo.
2. Ctrl+Z. Esperado: a porta inteira e o furo voltam.
3. Num móvel com agregado, tecle X: a pergunta "O objeto tem agregados" continua aparecendo.

## Porta e janela na região

1. Construir › Aberturas › **Marcar região**. Clique num canto e depois no canto oposto da parede, a partir do piso,
   e digite ou meça 820 × 2120 mm.
2. Escolha a porta simples. Esperado: ela aparece já na região; tecle Enter. Confira no painel da porta: largura
   820 mm, altura 2120 mm, sem diferença.
3. Marque outra região de 1200 × 1000 mm com a borda de baixo a 1100 mm do piso e escolha a janela. Esperado: janela
   de 1200 × 1000 com peitoril de 1100.
4. Marque uma região mais larga que o trecho livre da parede e escolha a porta. Esperado: aviso de que não cabe, e a
   inserção segue presa ao cursor, como hoje.
5. Marque uma região e tecle Esc: ela some.

## Testes automáticos

```bash
python3 -m pytest tests/test_component_core.py tests/test_wall_region_core.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_011_component_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_011_region_smoke.py
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
```
