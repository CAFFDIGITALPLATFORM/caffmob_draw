# Fluxograma: `divisions.resolve`, `add`, `add_many`, `remove` e `bays.apply` (cabinet_editor)

Subvãos do armário (feature 006, D‑04, D‑05; 008, D‑10, D‑15, D‑22). Puro, no referencial da raiz.

```mermaid
flowchart TD
    A[resolve roots divisions] --> B[spaces = cópia de roots s0, s1…]
    B --> C[divisões ordenadas por profundidade do caminho e caminho]
    C --> D{spaces tem division.space?}
    D -- não --> E[órfã: DIV-003] --> C
    D -- sim --> F[_split: corte em lo eixo + offset; chapa de espessura t; metades a e b]
    F --> G{kind SPACER?}
    G -- sim --> H[subvão continua com o mesmo caminho, lado maior]
    G -- não --> I[remove o caminho; cria caminho.a e caminho.b]
    H & I --> J[cuts uid = subvão, chapa sem recuo] --> C
    C -- fim --> K[return folhas, cortes, órfãs]
```

```mermaid
flowchart TD
    A[add roots divs space orientação t opções] --> B[folhas = resolve]
    B --> C{space é folha?} -- não --> E[ValueError 'Escolha um vão livre']
    C -- sim --> D{offset dado?}
    D -- não --> F{SPACER?} -- sim --> G[offset 0]
    F -- não --> H[offset = max 0, tamanho − t / 2]
    D -- sim --> I
    G & H --> I[Division uid novo] --> J[lista + divisão]
    M[add_many count] --> N[gap = tamanho − count·t / count + 1]
    N --> O[repete count vezes: add no alvo com offset gap; alvo = alvo.b]
    R[remove uid] --> S[metades = space.a, space.b]
    S --> T[sai a divisão e toda divisão cujo space é uma metade ou está dentro dela]
    RS[remove_in_space folha] --> RS1{folha tem pai?} -- não --> RS0[nada]
    RS1 -- sim --> RS2[divisória não distanciador cortando o pai] --> R
```

```mermaid
flowchart TD
    A[bays.apply roots divs N t] --> B{s0 existe?} -- não --> Z[sem mudança]
    B -- sim --> C[plan: largura = L − N−1·t / N; caminhos s0, s0.b, s0.b.b… com offset = largura]
    C --> D[divisórias bay atuais por profundidade]
    D --> E[as excedentes: remove com o que está dentro]
    E --> F[as que ficam: novo caminho, offset e espessura]
    F --> G[faltantes: Division VERTICAL bay=True]
    G --> H[return divisões]
```

`validate` aplica `offset_range` (mínimo 50 mm de cada lado; distanciador pode encostar) e a profundidade mínima de
50 mm depois dos recuos (`place`). O `offset` é medido a partir da face esquerda/de baixo do subvão, então quando o
vão‑raiz muda de tamanho a chapa mantém a distância e o resto se ajusta (RN‑16).
