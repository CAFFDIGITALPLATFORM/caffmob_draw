# Preparação e gravação de item

🟢 **CONFIRMADO** — object_library/item_io.py:57–121; ops.py:211–239. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Seleção ou objetos importados] --> B[Reusar grupo ou agrupar malhas de topo]
 B --> C[Resolver ID novo ou substituição]
 C --> D[Marcar root como item e calcular manifesto]
 D --> E[Escrever blend e JSON temporários]
 E --> F[Replace blend; depois replace JSON]
 F --> G[Gerar PNG opcional]
 G --> H[Retornar Item]
 E -->|OSError ou RuntimeError| I[Limpar temporários conhecidos e retornar erros]
```

🟢 Não há transação conjunta dos arquivos; falha do segundo replace pode deixar par parcialmente atualizado. Marcas na raiz não são revertidas pela rotina.
