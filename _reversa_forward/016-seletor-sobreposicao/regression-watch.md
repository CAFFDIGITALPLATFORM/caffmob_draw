# Regression Watch: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`
> Fonte: `_reversa_sdd/domain.md` (regras 🟢) e `legacy-impact.md` desta feature

## 1. Watch principal

Nenhuma regra 🟢 foi modificada ou removida, então o watch principal traz só as regras 🟢 **adjacentes ao ponto
tocado**: o mapa de teclado da seleção e o normalizador, que convivem com o operador novo. Elas precisam continuar
verdadeiras nas próximas extrações.

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `domain.md`, Seleção (RN-SELECTION-09) | `Alt + clique` e `Alt + Shift + clique` continuam chamando `caffmob.component_pick`, com a peça marcada como isenta | presença | Um dos dois atalhos abrir o painel de sobreposição, ou a peça deixar de ficar isenta |
| W002 | `domain.md`, Seleção (RN-SELECTION-07) | O normalizador continua suspenso durante modal da extensão: abrir o seletor, passar o mouse e isolar não muda seleção nem ativo | presença | A seleção ou o ativo mudar antes do `Enter` |
| W003 | `domain.md`, Seleção (RN-SELECTION-04) | A seleção aplicada no `Enter` sobe para a raiz do componente como um clique normal | redação | O seletor deixar peças soltas selecionadas depois do `Enter`, contrariando o normalizador |
| W004 | `domain.md`, Seleção (RN-SELECTION-10) | Nenhuma propriedade nova na cena: o seletor não cria `bpy.props` nem custom properties | ausência | Um arquivo salvo depois de usar o seletor ganhar campo novo no painel de objeto |

## 2. Histórico de re-extrações

## 3. Arquivadas

## 4. Observações

- As oito combinações de `LEFTMOUSE` do mapa `3D View` continuam com `view3d.select`, menos o `Ctrl + Alt + clique`,
  que agora é do seletor. Não há regra 🟢 do domínio sobre isso; a sonda de keymap da `investigation.md` é a evidência.
- Isolar com o seletor aberto e fechar o Blender à força deixa a visibilidade no arquivo (lacuna 🟡 aceita em Q3 da
  `requirements`). O caminho normal (confirmar, cancelar, `unregister`) restaura tudo; a fumaça confere a restauração.
- O menu de contexto ganhou um item e manteve os anteriores; o contrato não está em `domain.md`, então fica como
  observação, sem peso de regressão.
