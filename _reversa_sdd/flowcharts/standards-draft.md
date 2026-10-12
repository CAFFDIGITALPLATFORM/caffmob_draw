# Rascunho e aplicação pelo Configurador

🟢 **CONFIRMADO** — fontes: `standards/api.py:241–319, 418–478`. Extração: 2026-10-10.

```mermaid
flowchart TD
    A[begin_draft] --> B[Garantir definição e copiar valores e montagem]
    B --> C[Completar faltantes e reconstruir árvore]
    C --> D[Selecionar parâmetro com guard de callback]
    D --> E{FLOAT ou ENUM?}
    E -->|FLOAT| F[Interpretar unidade; converter m para mm e arredondar]
    E -->|ENUM| G[Receber opção do enum]
    F --> H{Validação aceita?}
    G --> H
    H -->|Não| I[Mostrar erro e preservar valor anterior]
    H -->|Sim| J[Gravar rascunho e limpar erro]
    J --> K[Comparar valores e montagem com definição]
    K --> L{Aplicar?}
    L -->|Não| C
    L -->|Sim| M{Definição existe e não é embutida?}
    M -->|Não| N[StandardsError]
    M -->|Sim| O[Renomear se necessário e copiar rascunho]
    O --> P{Há alterações de valores ou montagem?}
    P -->|Sim| Q[Incrementar versão e timestamp]
    P -->|Não| R[Sincronizar; acrescentar changes ao relatório]
    Q --> R
```

A cópia no apply não revalida a coleção inteira. Renomeação isolada não incrementa versão. A validação numérica atual aceita NaN; não inferir proteção de finitude.
