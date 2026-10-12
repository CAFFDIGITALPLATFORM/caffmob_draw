# Mapeamento e reexportação do DIMENSIONEXPORT

🟢 **CONFIRMADO** — fontes: `standards/io_promob.py:32–190`. Extração: 2026-10-10.

```mermaid
flowchart TD
    A[Ler XML] --> B{Raiz correta e atributos com ID?}
    B -->|Não| C[PromobFormatError]
    B -->|Sim| D[Normalizar nome e guardar pares na ordem]
    D --> E[Separar CAFF_MONTAGEM; default LATERAL]
    E --> F[Registrar duplicados e último valor por ID]
    F --> G[Para cada ocorrência original]
    G --> H{ID mapeado e último valor válido?}
    H -->|Sim| I[Gravar chave e valor; contar mapped]
    H -->|Não| J[Chave vazia; registrar desconhecido ou inválido]
    I --> K[Guardar ID, string original e chave]
    J --> K
    K --> G
    G -->|Fim| L[Devolver values, raw, assembly e report]
    L --> M[Exportação: percorrer raw na ordem]
    M --> N{Chave com valor atual?}
    N -->|Não| O[Preservar string original]
    N -->|Sim| P[Preservar formato numérico se igual; senão formatar]
    O --> Q[Acrescentar montagem válida no final]
    P --> Q
    Q --> R[Temporário no destino e os.replace]
```

Mapped conta ocorrências, não chaves distintas. A reexportação com raw não acrescenta campos ausentes do arquivo original. A raiz/DEFINITION é regenerada; só ordem e strings de atributos são preservadas. 🔴 Integração no aplicativo Promob não verificada.
