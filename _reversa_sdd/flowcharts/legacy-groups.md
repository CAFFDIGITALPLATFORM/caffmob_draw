# Conversão de grupos salvos e marcador

🟢 **CONFIRMADO** — legacy/groups.py:91–154; ops.py:85–103. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Invoke conversão de grupos] --> B[Ler pendentes e marcar offered antes da confirmação]
 B --> C{Confirmar?}
 C -->|Cancelar| D[Oferta segue dispensada]
 C -->|Sim| E[Para cada caminho pendente]
 E --> F[Snapshot e carregar objetos em coleção temporária]
 F --> G[Converter raízes e salvar módulos em Geral]
 G --> H[Finally limpar novos data-blocks e holder]
 H --> I{Erro de processamento?}
 I -->|Não| J[Adicionar caminho aos concluídos]
 I -->|Sim| K[Registrar erro sem marcar convertido]
 J --> E
 K --> E
 E -->|Fim| L[Escrever marcador e invalidar cache]
```

Erros retornados pelo save só entram no relatório e não impedem marcação do grupo. Arquivos de origem são preservados; reexecução usa caminho, sem verificar conteúdo alterado.
