# Envelope e detecção de interferência

🟢 **CONFIRMADO** — inspection/interference.py:58–219. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Frentes válidas com can_sweep] --> B[Aplicar poses e coletar caixas mundo]
 B --> C[Finally restaurar pose original]
 C --> D[Unir poses consecutivas e encolher radialmente 1 mm]
 D --> E[Targets visíveis e AABB]
 E --> F[Excluir próprio módulo; filtrar AABB]
 F --> G[Cascos convexos e BVH sob demanda]
 G --> H{Superfícies cruzam?}
 H -->|Sim| I[Centros de faces, até 32]
 H -->|Não| J[Testar vértices do alvo dentro dos cascos]
 I --> K[Registrar ponto e nomes]
 J --> K
 K --> L[Retornar resultados e nº efetivamente verificado]
```

Sem teste de choque com peças do mesmo módulo. Amostragem angular e caixas são aproximações, não simulação mecânica completa.
