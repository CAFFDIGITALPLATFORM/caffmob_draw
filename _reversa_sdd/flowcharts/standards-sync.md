# Propagação da definição para cena e móveis

🟢 **CONFIRMADO** — fontes: `standards/sync.py:169–176, 231–291`. Extração: 2026-10-10.

```mermaid
flowchart TD
    A[apply_definition] --> B[Incrementar profundidade de sync]
    B --> C[Completar valores com defaults]
    C --> D[Escrever destinos de cena em metros; marcar linhas de cages]
    D --> E{modules é None?}
    E -->|Sim| F[Selecionar CAFFMob sem own ou todos com include_manual]
    E -->|Não| G[Usar lista explícita, inclusive vazia]
    F --> H[Para cada CAFFMob existente]
    G --> H
    H --> I[Defaults por linha e tipo]
    I --> J[Manter largura e Z; alterar altura, profundidade, chapas e montagem]
    J --> K[Zerar espessuras próprias; limpar overrides; gravar UID e linha]
    K --> L[Reconstruir geometria]
    L --> H
    H -->|Fim| M{Modo de suporte legado?}
    M -->|Sim| N[Atualizar frameless e closets com skip de medidas manuais]
    M -->|Não| O[Invalidar plano de corte e montar relatório]
    N --> O
    O --> P[Finally: decrementar profundidade]
    B -->|Exceção em qualquer etapa| P
```

`modules=None` não compara UID anterior; a seleção do diálogo usa outra regra. Lista vazia ainda escreve destinos de cena e pode atualizar legado no suporte. Erros não desfazem as escritas anteriores; o finally restaura apenas a profundidade.
