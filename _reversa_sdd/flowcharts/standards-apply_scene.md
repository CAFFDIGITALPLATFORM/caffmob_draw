# Seleção dos módulos nas duas perguntas

🟢 **CONFIRMADO** — fontes: `standards/apply_core.py:24–42; sync.py:206–228; operators/ops_standards.py:491–590`. Extração: 2026-10-10.

```mermaid
flowchart TD
    A[Plano com UID global anterior] --> B{Tipo do componente}
    B -->|LEGACY ou OTHER| C[Não aplicável; legado sugere conversão]
    B -->|CAFFMob| D{Own ou UID não vazio diferente?}
    D -->|Sim| E[differ]
    D -->|Não| F[follow]
    E --> G{Primeira pergunta: aplicar?}
    F --> G
    G -->|Cancelar| H[Módulos ficam como estão]
    G -->|Sim| I[Aplicar follow]
    I --> J{Há differ?}
    J -->|Não| K[Encerrar]
    J -->|Sim, interativo| L[Segunda pergunta]
    J -->|Sim, EXEC| M{apply_differ?}
    L -->|Cancelar| K
    L -->|Sim| N[Recalcular plano e aplicar differ]
    M -->|False| K
    M -->|True| N
    N --> K
```

A definição e os destinos de cena já foram gravados antes das perguntas. Cancelar a segunda não reverte follow. `targets` é puro e testado; operadores usam diretamente as listas do plano.
