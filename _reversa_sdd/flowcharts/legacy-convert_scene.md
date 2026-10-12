# Conversão em lote da cena

🟢 **CONFIRMADO** — legacy/convert.py:77–145. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Raízes explícitas ou gate.legacy_roots] --> B[Filtrar objetos vivos e legados]
 B --> C[Ler todas caixas, specs, matrizes, pais e agregados]
 C --> D[Construir todos CAFFMob com padrão ativo]
 D --> E[Excluir raízes e agregados próprios em lote; soltar grudados]
 E --> F[Restaurar nomes originais]
 F --> G[Retornar Result por armário]
 D -->|Falha| H[Propagar exceção sem rollback explícito]
```

🟢 A estrutura evita exclusão um a um. Falha durante construção pode deixar módulos novos parciais; o operador declara UNDO, mas runtime não verificado.
