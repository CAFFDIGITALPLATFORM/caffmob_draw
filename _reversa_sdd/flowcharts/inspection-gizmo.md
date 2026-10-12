# Arraste do gizmo e commit diferido

🟢 **CONFIRMADO** — inspection/gizmo.py:23–166. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Ativo selecionado] --> B[Resolver Front e frame mundo]
 B --> C{Articulada?}
 C -->|Sim| D[Dial radians para graus; snap opcional]
 C -->|Não| E[Arrow metros para fração por travel]
 D --> F[Apply e pending]
 E --> F
 F --> G{Dial e arrow fora de modal?}
 G -->|Não| F
 G -->|Sim| H[Timer zero agenda commit]
 H --> I[Commit valor e limpar pending]
```

AggregateLeafFront deslizante não implementa travel, embora arrow o invoque; confirmar efeito em runtime. Pending é global, não por janela.
