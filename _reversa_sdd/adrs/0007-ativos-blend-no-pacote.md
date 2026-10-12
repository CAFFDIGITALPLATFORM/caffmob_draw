# ADR 0007 — Ativos blend versionados como dependência do pacote

Status: retroativo, extração em 2026-10-10.

## Contexto e evidências

🟢 Histórico: `eb39aa9`. Implementação atual: `caffmob_draw/build.py; caffmob_draw/assets/; caffmob_draw/hb_geo_nodes/`. O histórico confirma a introdução/evolução do mecanismo; a motivação completa dos autores não é recuperável somente pela mensagem do commit.

## Decisão observada

🟢 Versionar os ativos necessários ao pacote e recusar build quando faltarem ativos obrigatórios.

## Alternativas consideradas

🟡 Gerar todos os ativos no clone; depender de arquivos locais não versionados. Alternativas inferidas.

## Consequências

🟢 Efeitos observáveis: Um clone pode gerar pacote funcional com nós e recursos necessários. Projetos blend do usuário continuam fora do versionamento; binários do pacote aumentam tamanho do repositório.

## Limites de confiança

Não é aprovação nova de arquitetura nem promessa de comportamento testado. A análise considera a árvore de trabalho, que contém alterações sem commit.
