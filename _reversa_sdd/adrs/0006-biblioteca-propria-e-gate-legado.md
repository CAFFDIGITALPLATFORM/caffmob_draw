# ADR 0006 — Biblioteca própria e acesso optativo ao legado

Status: retroativo, extração em 2026-10-10.

## Contexto e evidências

🟢 Histórico: `83a6863`. Implementação atual: `caffmob_draw/legacy/gate.py; library_panel/; object_library/; standards/cabinet_defaults.py`. O histórico confirma a introdução/evolução do mecanismo; a motivação completa dos autores não é recuperável somente pela mensagem do commit.

## Decisão observada

🟢 Expor painel CAFFMob com categorias/modelos próprios e manter UI de bibliotecas antigas atrás de preferência. Preservar registro de dados do legado para abrir projetos existentes.

## Alternativas consideradas

🟡 Excluir o legado; continuar com todas as bibliotecas expostas; converter automaticamente sem confirmação. Alternativas inferidas.

## Consequências

🟢 Efeitos observáveis: Reduz exposição de fluxos herdados e preserva leitura de projetos. Conversão é aproximada e pode perder frentes/agregados. Preferência não é controle de segurança.

## Limites de confiança

Não é aprovação nova de arquitetura nem promessa de comportamento testado. A análise considera a árvore de trabalho, que contém alterações sem commit.
