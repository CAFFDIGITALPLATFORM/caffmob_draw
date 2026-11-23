# Onboarding: Construtor de armário v2

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`

Roteiro para quem vai testar a feature pela primeira vez, do zero até o plano de corte. Cada passo diz o que fazer e o que deve acontecer.

## 1. Preparar o ambiente

1. `ruff check caffmob_draw/` — sem avisos.
2. `python3 docs/rag/tools/check_api.py` — sem `[UNKNOWN in 5.2]`.
3. `tests/test_i18n_coverage.py` com as chaves novas:

   ```bash
   python3 -m pytest tests/test_i18n_coverage.py -q
   ```

4. Fumaças que não podem regredir:

   ```bash
   blender --background --factory-startup --python-exit-code 1 --python tests/blender_017_armario_smoke.py
   blender --background --factory-startup --python-exit-code 1 --python tests/blender_008_construtor_smoke.py
   ```

5. `python3 build.py` e instale o ZIP em **Edit → Preferences → Get Extensions → Install from Disk**.

## 2. Abrir o construtor

1. Abra o Blender com um arquivo novo.
2. Pressione `N` na vista 3D e procure a aba **CAFFMob Draw**.
3. Sem nada selecionado, o painel **Construtor de armário** deve aparecer com a mensagem de janela vazia e o botão **Montar Caixa**.
4. Confirme que **não existe** nenhuma peça na cena e que não há janela 2D.

## 3. Contrato de chapas

1. Abra a aba **Estrutura**.
2. Confira a chapa: 2750 × 1830 mm, espessuras 6/15/18/25, montagem e orientações preenchidas a partir do Padrão de Dimensões.
3. Se o padrão não estiver configurado, o contrato deve vir com os valores do `dimension_schema` BR e a aba deve avisar que é o padrão de fábrica.
4. Num arquivo sem contrato (`configurado = False`), **Gerar** deve recusar com mensagem e não criar geometria.
5. Ainda na aba **Estrutura**, marque **Contra-frente** e **Peça de trás** e gere: as duas travessas aparecem entre as laterais, no topo interno, uma na frente e outra no fundo.
6. Troque a orientação da contra-frente para **deitada** e gere de novo: a travessa passa a deitar no plano do topo, com a espessura na vertical.
7. Desmarque a peça de trás e gere: só ela sai da cena e do plano de corte.

## 4. Montar a caixa

1. Use **Montar Caixa** — laterais, base inferior, base superior e fundo aparecem.
2. Confira as medidas na lista de peças: lateral com a altura total (lateral passante) e base entre as laterais.
3. Troque para **base passante** e gere de novo: a base passa a cobrir a largura total e as laterais ficam entre as bases.

## 5. Chapa máxima

1. Peça um armário de 3000 mm de largura com lateral inteira.
2. Com **bloquear se extrapolar** ligado, nada é gerado e a mensagem lista a peça e a medida.
3. Desligue o bloqueio e gere: o armário aparece e a lista marca a peça fora da chapa.

## 6. Divisões

1. Na aba **Divisões**, use **Inserir divisória** e **Inserir prateleira**: cada clique cria a peça no vão ativo e gera o armário no mesmo passo de desfazer.
2. Duplique: a peça nova nasce no maior vão livre.
3. Tente duplicar num vão com menos de 80 mm livres: comando recusado com aviso.
4. Na sub-aba **Múltipla**, use **Inserir matriz** com 2 linhas e 1 coluna: uma divisória e duas prateleiras por vão resultante.
5. Confira que cada inserção volta com um único `Ctrl+Z` e que o vão do cabeçalho é o mesmo onde a peça nasceu.

## 7. Gavetas e corrediça

1. Na aba **Gavetas**, preencha quantidade 4 e altura do bloco 760 mm e use **Criar bloco de gavetas**.
2. Confira quatro alturas iguais com 3 mm de folga entre elas.
3. Ligue **corrediça 3D**: cada gaveta recebe trilho externo, trilho interno e gaiolas.
4. Renomeie temporariamente `caffmob_draw/assets/slides/slide-st48-0200-0.obj` e gere de novo: o conjunto geométrico equivalente aparece e a gaveta ainda abre.

## 8. Internos

1. Na aba **Internos**, use os botões **Cabideiro**, **Calceiro**, **Sapateira** e **Maleiro**: cada um insere o interno no vão ativo.
2. Confira as posições iniciais: calceiro e sapateira a 480 mm do piso do vão, maleiro a 420 mm abaixo do topo.
3. Edite a altura de cada um e confirme que só aquele interno se move.

## 9. Portas e deslizantes

1. Na aba **Portas**, duas folhas num armário de 1000 mm, com dobradiça alternada.
2. Na aba **Deslizantes**, ative a porta deslizante: as portas de abrir desligam sozinhas.
3. Escolha **base por dentro** e trilho de 70 mm: divisórias, prateleiras, gavetas e internos recuam 70 mm; laterais e bases mantêm a profundidade.
4. Troque para **base na frente**: nenhuma peça interna muda de profundidade.

## 10. Abrir e fechar

1. Clique com o botão direito numa gaveta: o menu oferece **Abrir/Fechar**, **Duplicar** (só em divisória e prateleira) e **Excluir**.
2. Abra a gaveta: ela sai 72% da profundidade e as gaiolas andam 50%.
3. Abra de novo: a gaveta volta e o rótulo do menu era o da ação oposta.
4. Confirme `Ctrl+Z`: cada operação de abrir/fechar volta em um passo, sem sobrar timer.

## 11. Fundo e acabamento

1. Ligue o fundo, escolha **encaixado** com recuo de 10 mm: o painel de 6 mm fica a 10 mm da face de trás.
2. Troque o acabamento entre madeirado, branco, cinza e preto: chapas e frentes mudam; vidro e alumínio continuam distintos.

## 12. Plano de corte

1. Abra o plano de corte do armário.
2. Confira nome, largura, altura e espessura de cada chapa, incluindo as peças das gavetas e as folhas.
3. Confirme que a corrediça **não** aparece como peça de chapa e que nenhuma peça aparece duas vezes.
4. Com a contra-frente e a peça de trás marcadas, as duas aparecem no corte com 90 mm de altura de peça; desmarcadas, não aparecem.

## 13. Módulo de biblioteca

1. Insira um módulo frameless e um face frame pela biblioteca.
2. Os dois devem abrir no painel novo, com as medidas do módulo preenchidas.
3. Use **Gerar**: o armário v2 aparece, o módulo antigo fica oculto e o plano de corte não duplica peças.

## 14. Móvel antigo

1. Abra um arquivo com um armário feito pelo editor antigo.
2. Abra o construtor nele: o painel avisa que o móvel é da construção antiga e que a edição exige recriar.
3. Confirme que nenhuma peça e nenhum parâmetro foram alterados e que o plano de corte continua listando as peças antigas.

## 15. Desfazer e desregistrar

1. Gere, altere e confirme: um único `Ctrl+Z` volta ao estado anterior.
2. Abra, mude a largura e use **Cancelar**: o armário volta à largura anterior e não fica passo de desfazer.
3. Desative o addon em **Preferences → Add-ons**: nenhum operador, propriedade, item de menu, timer ou `draw_handler` pode sobrar; reative e confirme que o painel volta.

## 16. Interface em inglês

1. Troque o idioma do Blender para inglês e reabra o painel.
2. As sete abas, os modelos de frente e as mensagens devem aparecer em inglês.

## Se algo falhar

- Anote o passo, o texto exato da mensagem e o que a cena mostrava.
- Rode a fumaça com `--python-exit-code 1` e guarde a saída completa.
- Verifique `btm_armario` e `btm_armario_parte` no armário pelo **Object Properties → Custom Properties**.
