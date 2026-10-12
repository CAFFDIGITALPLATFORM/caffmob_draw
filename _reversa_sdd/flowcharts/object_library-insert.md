# Append e posicionamento modal

🟢 **CONFIRMADO** — object_library/item_io.py:124–148; ops.py:48–131. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Resolver chave U ou B] --> B[Append objetos e encontrar root]
 B --> C{Root encontrado?}
 C -->|Não| D[Remover objetos carregados e ValueError]
 C -->|Sim| E[Ligar coleção, mover ao cursor e selecionar]
 E --> F{Invoke na VIEW_3D?}
 F -->|Não| G[FINISHED]
 F -->|Sim| H[Modal em plano horizontal do Z do cursor]
 H -->|Mousemove| I[Interseção raio-plano e mover root]
 I --> H
 H -->|Clique esquerdo| J[Limpar header e FINISHED]
 H -->|Esc ou direito| K[Limpar header, remover carregados e CANCELLED]
 H -->|Middle ou wheel| L[PASS_THROUGH]
 L --> H
```

🔴 cancel externo só limpa header; sem remoção dos objetos nesse método. Referências RNA diretas durante modal exigem validação com undo.
