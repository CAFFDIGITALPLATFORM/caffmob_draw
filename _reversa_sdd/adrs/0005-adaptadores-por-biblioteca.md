# ADR 0005 — Contratos comuns com adaptadores por biblioteca

Status: retroativo, extração em 2026-10-10.

## Contexto e evidências

🟢 Histórico: `f6d9188; adcd52f; 00ac2f6`. Implementação atual: `caffmob_draw/inspection/fronts.py; inspection/adapters/; customize/adapters/; cabinet_editor/bridge.py`. O histórico confirma a introdução/evolução do mecanismo; a motivação completa dos autores não é recuperável somente pela mensagem do commit.

## Decisão observada

🟢 Usar contratos comuns de frente, personalização e editor, delegando leitura/reconstrução à biblioteca de origem e explicitando capacidades ausentes.

## Alternativas consideradas

🟡 Supor propriedades uniformes; duplicar toda a UI por biblioteca; converter previamente todo item legado. Alternativas inferidas.

## Consequências

🟢 Efeitos observáveis: Reduz dependência de UI sobre estruturas heterogêneas, mas não uniformiza capacidades. Molding possui adaptadores próprios restritos; não reutiliza automaticamente suporte moderno.

## Limites de confiança

Não é aprovação nova de arquitetura nem promessa de comportamento testado. A análise considera a árvore de trabalho, que contém alterações sem commit.
