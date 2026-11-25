# Onboarding: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/023-janela-mockup-construtor/requirements.md`

Passo a passo executável para um humano testar a feature pela primeira vez.

## Pré-requisitos

- Blender 5.2.0 com o addon CAFFMob Draw carregado e registrado.
- Modo objeto ativo.
- Um armário v2 (`armario_v2`, `Object.btm_armario`) existente na cena (ou criado via "Criar Armário" → Construtor v2).

## Passos de teste

1. **Abrir a janela.** Com o armário v2 selecionado (ou sem armário, para criar do zero), clicar em **Abrir Janela** no cabeçalho do painel CAFFMob Draw. A contagem de janelas do Blender deve aumentar em 1 e a Vista 3D do usuário deve continuar VIEW_3D. A janela nova deve abrir com a aba **Construtor Armário** ativa, preview dividido (frontal + corte lateral), Estrutura aberta, barra "Selecionado: …" e o empty state "Janela de Armário Vazia". (Critério RF-01)
2. **Montar a caixa.** Na aba Estrutura, ativar Laterais, Base Inferior, Base Superior e Fundo (ou clicar "Montar Caixa"). As chapas devem aparecer ao vivo no preview; clicar numa peça a seleciona (barra "Selecionado: …"). (Critério RF-02)
3. **Validar medida inválida.** Definir a largura para um valor fora da faixa da biblioteca. Deve aparecer `DIM-003` (ERRO) no campo e o botão OK ficar desabilitado. Peça fora do módulo ou prateleiras sobrepostas em mais de 1 mm mostram `GEO-001`/`GEO-002` e também bloqueiam OK/Aplicar. (Critério RF-03)
4. **Confirmar (OK).** Clicar em OK. Deve gravar um passo de desfazer do Blender, fechar a janela e manter as peças geradas na cena. Apertar Ctrl+Z na cena deve desfazer todo o conjunto gerado. (Critério RF-04)
5. **Aplicar sem fechar.** Reabrir a janela, fazer uma alteração, clicar em Aplicar. A janela permanece aberta e a alteração vira o novo ponto de retorno do Cancelar. (Critério RF-05)
6. **Cancelar descarta.** Com alterações não confirmadas, clicar em Cancelar e confirmar "Descartar". O armário deve voltar ao estado da abertura e a janela fechar. Ao fechar a janela pelo sistema com alterações, deve aparecer o aviso "Editor fechado: alterações descartadas". (Critério RF-06)
7. **Empty state.** Sem nenhuma estrutura ativa, o preview deve exibir o empty card "Janela de Armário Vazia" com o botão de montagem rápida "Montar Caixa". (Critério RF-07)

8. **Seleção múltipla (RF-08).** Clicar numa peça (barra mostra o nome), Shift+clique noutra (barra mostra "2 peças selecionadas"); usar as setas da barra para mover as duas, "Espelhar" para inverter no eixo X e "Apagar" para removê-las. Um Ctrl+Z desfaz o lote. Clicar no vazio limpa a seleção. (Critério RF-08)
9. **Memória por cena (RF-09).** Ir para a aba Gavetas, fechar a janela e reabrir: ela volta em Gavetas. Numa cena sem histórico, abre em Estrutura. O tamanho atual fica registrado na cena, mas o Blender 5.2 não permite reaplicá-lo por script (`Window.width` é readonly). (Critério RF-09)
10. **Desempenho (NFR).** Abrir a janela com o armário montado: abaixo de 2 s; arrastar/clicar no preview responde abaixo de 200 ms. Medido por `tests/blender_023_desempenho.py` (modelo do preview) e pela sonda gráfica de abertura.
11. **Conferir o que não é pixel-perfeito.** A janela usa o chrome do Blender: barra de ferramentas, lista de peças e botões em painéis da região lateral; não há titlebar própria, abas horizontais nem barra "Movimentação & Precisão". Essa diferença é a decisão aberta (T018) e deve ser conferida com o titular antes de declarar paridade visual.

## Resultado esperado

A janela se comporta como o Construtor do Promob (preview ao vivo, painel lateral, confirmação explícita), edição em milímetros, erro bloqueia OK/Aplicar, OK grava passo de desfazer e fecha, Aplicar grava sem fechar, Cancelar restaura o estado inicial.
