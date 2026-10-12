# ADR 0004 — Editores com rascunho e controle de undo

Status: retroativo, extração em 2026-10-10.

## Contexto e evidências

🟢 Histórico: `f6d9188; 00ac2f6; 98c7914`. Implementação atual: `caffmob_draw/walls2d/ops_editor.py; cabinet_editor/ops_editor.py; cabinet_editor/state.py`. O histórico confirma a introdução/evolução do mecanismo; a motivação completa dos autores não é recuperável somente pela mensagem do commit.

## Decisão observada

🟢 Paredes acumulam rascunho até OK. Armário recebe mudanças ao vivo por fila/modal, mantém snapshot e oferece Aplicar/OK/Cancelar.

## Alternativas consideradas

🟡 Editar tudo direto em callbacks; múltiplos operadores UNDO em cada botão; gerar cópia completa da cena. Alternativas inferidas.

## Consequências

🟢 Efeitos observáveis: Agrupa mudanças e viabiliza rollback lógico. Aplicar muda o ponto de restauração. Fechamento de janela, objetos removidos e falhas de rebuild exigem validação adicional.

## Limites de confiança

Não é aprovação nova de arquitetura nem promessa de comportamento testado. A análise considera a árvore de trabalho, que contém alterações sem commit.
