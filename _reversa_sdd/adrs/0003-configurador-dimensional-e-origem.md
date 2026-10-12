# ADR 0003 — Padrão dimensional versionado e origem dos módulos

Status: retroativo, extração em 2026-10-10.

## Contexto e evidências

🟢 Histórico: `d03c0af`. Implementação atual: `caffmob_draw/standards/model.py; standards/apply_core.py; standards/sync.py`. O histórico confirma a introdução/evolução do mecanismo; a motivação completa dos autores não é recuperável somente pela mensagem do commit.

## Decisão observada

🟢 Representar valores por definição/linha/componente, manter padrões embutidos protegidos e atribuir UID de origem ao módulo. Separar módulos que seguem o padrão daqueles com parâmetros próprios.

## Alternativas consideradas

🟡 Defaults soltos por biblioteca; aplicar silenciosamente tudo; armazenar apenas valores sem origem. Essas alternativas são reconstruções analíticas, não deliberações comprovadas.

## Consequências

🟢 Efeitos observáveis: Permite distinguir seguir/diferir e conservar largura/posição Z ao aplicar. Impõe conversão mm↔m e migração; montagem não faz round-trip no JSON atual.

## Limites de confiança

Não é aprovação nova de arquitetura nem promessa de comportamento testado. A análise considera a árvore de trabalho, que contém alterações sem commit.
