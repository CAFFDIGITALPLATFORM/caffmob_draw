# Onboarding: testar o seletor de objetos sobrepostos

> Identificador: `016-seletor-sobreposicao`
> Para quem vai testar a feature pela primeira vez no Blender 5.2.

## Preparar

1. Gere e instale o pacote: `py -3 build.py`, depois Edit → Preferences → Get Extensions → Install from Disk →
   `caffmob_draw.zip` (ou desligue e religue a extensão, se ela já estiver instalada a partir da pasta).
2. Abra um arquivo novo e monte uma cena de teste: três cubos empilhados no mesmo ponto, uma curva, um texto, um
   vazio e um cubo com **Desabilitar seleção** ligado (Object Properties → Visibility → Selectable, desmarcado).
3. Deixe a viewport em **Object Mode**. O seletor não abre em Edit Mode, Sculpt nem nos demais modos.

## Abrir e conferir a lista

1. Passe o mouse sobre o ponto onde os três cubos coincidem e use **Ctrl + Alt + botão esquerdo**.
   Esperado: o painel abre ao lado do cursor, com o nome dos três cubos, do mais próximo ao mais distante, o total
   no cabeçalho e os atalhos no rodapé.
2. Confira que a curva, o texto, o vazio e o cubo não selecionável **não** aparecem.
3. Confira na barra lateral que a seleção que existia antes continua igual e que o objeto ativo não mudou.
4. Aponte para o vazio do céu e repita o atalho. Esperado: nenhum painel abre, aparece o aviso de que não há objeto
   elegível e a seleção continua igual.

## Inspecionar, marcar e confirmar

1. Abra de novo e passe o mouse pelas linhas. Esperado: a caixa envolvente do objeto em foco aparece destacada na
   viewport, e a seleção continua intocada.
2. Clique na linha 2 e depois na 3. Esperado: as duas ficam marcadas e o item sob o mouse fica realçado.
3. Use `Ctrl+A` e depois `Ctrl+/`. Esperado: primeiro tudo marcado, depois só o que estava desmarcado antes.
4. Use `+` e `-` no item em foco, e `Ctrl+/` de novo. Esperado: `+` marca, `-` desmarca, e a inversão só troca as
   marcações.
5. Tecle `Enter`. Esperado: a seleção anterior continua e só os marcados entram ou saem (RF-12), o item em foco
   entre eles vira o ativo, e o painel fecha. **Ctrl+Z** não deve trazer o painel de volta.

## Isolar, cancelar e conferir o retorno

1. Abra o seletor, tecle `I`. Esperado: só o objeto em foco continua visível e o cabeçalho mostra que o isolamento
   está ligado.
2. Com o isolamento ligado, passe para outra linha. Esperado: o isolamento acompanha o foco.
3. Tecle `I` de novo. Esperado: a visibilidade de todos volta ao que era. Saia com `Esc`.
4. Abra o seletor, marque outros dois objetos e tecle `Esc` (ou clique com o botão direito). Esperado: a seleção, o
   ativo e a visibilidade são exatamente as de antes de abrir.
5. Salve e reabra o arquivo. Esperado: nenhum objeto escondido, nenhuma propriedade nova no painel de objeto.

## Lista cheia e menu de contexto

1. Monte 20 cubos sobrepostos. Abra o seletor e role com a roda até o fim. Esperado: a última linha aparece, todas
   foram visíveis uma vez, e a rolagem não mudou marcação nem foco.
2. Use as setas para baixo até a linha 13. Esperado: a linha em foco continua visível na lista rolada.
3. Clique com o **botão direito** num objeto e escolha o item do seletor no menu. Esperado: o painel abre no ponto do
   cursor da viewport, com a mesma lista do atalho.

## Testes automáticos

```bash
cd tests && PYTHONUTF8=1 py -3 -m unittest test_overlap_core test_i18n_coverage test_identity
cd .. && py -3 docs/rag/tools/check_api.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_016_overlap_smoke.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --factory-startup --enable-event-simulate \n  --python tests/blender_016_overlap_window.py
```

A fumaça no Blender cobre: abrir com três cubos alinhados, recusar curva, texto, vazio, objeto oculto e objeto com
`hide_select`, marcar por linha, `Ctrl+A`, `Ctrl+/`, isolar e restaurar, confirmar, cancelar e conferir que a pilha de
desfazer não cresceu e que `hide_get()` voltou ao estado inicial.
