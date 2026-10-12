# Fluxograma: `structure.layout`, `extras.layout`, `slides.layout` e `appliances.layout` (cabinet_editor)

Geometria das chapas e peças geradas pelo editor (features 006, 008 e 012). Puro; caixas `(lo, hi)` no referencial da
raiz (X largura, Y profundidade com a frente no menor Y, Z altura).

```mermaid
flowchart TD
    A[structure.layout L A P thick states recuo montagem] --> B[t papel = 0 se removido em EXTEND/SHRINK, senão espessura]
    B --> C[x0 = −L/2 + t esq; x1 = L/2 − t dir; z0 = t base; z1 = A − t tampo]
    C --> D{montagem BASE?}
    D -- sim --> E[laterais começam em z = t base; base de −L/2 a L/2]
    D -- não --> F[laterais do piso ao topo; base entre x0 e x1]
    E & F --> G[tampo entre x0 e x1; fundo entre x0..x1 e z0..z1, recuado]
    G --> H[só as chapas não removidas]
    H --> I[vão interno: x0..x1, −P..fundo recuado, z0..z1]
```

```mermaid
flowchart TD
    A[extras.layout caixa t settings] --> B{Base Superior Recuada?} -- sim --> B1[BAS entre laterais, recuo 20 mm na frente]
    A --> C{Pés?} -- sim --> C1[4 cilindros r 20 mm a 50 mm dos cantos, altura pés abaixo de z0; posição desligada pula]
    A --> D{Rodapé frontal ou granito?} -- sim --> D1[faixa recuada 50 mm, altura = pés; granito com material GRANITO]
    A --> E{Rodapé esquerdo/direito?} -- sim --> E1[faixas rentes às laterais]
    A --> F{Fechamentos?} -- sim --> F1[TAMPON largura value dos dois lados, por fora, na frente]
    A --> G{Vistas / Vistas altas?} -- sim --> G1[ESP à esquerda, à direita ou em cima; altas sobem até max teto 2,70, topo]
```

```mermaid
flowchart TD
    A[slides.layout vão N estilo invertido] --> B[largura = L + N−1·30 mm / N]
    B --> C[para i: x = x0 + i·largura − 30; trilho = i ou N−1−i se invertido]
    C --> D[folha 18 mm em y0 + trilho·20 mm, entre trilhos de 10 mm]
    D --> E{estilo com rasgo?} -- sim --> F[rasgo 20 mm na borda de encontro: direita da folha 0, esquerda das demais]
    C --> G[trilhos inferior e superior na faixa y0..y0 + N·20 mm]
    H[missing_depth] --> H1{profundidade ≥ N·20 + 50 mm?} -- não --> H2[profundidade necessária]
```

```mermaid
flowchart TD
    A[appliances.layout vão item t] --> B{filtro BUILT_IN?}
    B -- sim --> C[painel em Y t..2t, recuado]
    B -- não --> D[painel em Y −t..0, para fora]
    C & D --> E{tem eletros ou é respiro?}
    E -- sim --> F[recorte centrado: largura do maior, soma das alturas, ou 440×30]
    F --> G[eletros empilhados de baixo: forno, depois micro, atrás do painel]
    E -- não --> H{item é eletro solto?} -- sim --> I[caixa do eletro no vão, sem painel]
    E -- não --> J[só o painel frontal]
```

Na cena, `scene_parts.place` põe a espessura no eixo mais fino da caixa (Z sem rotação, X com −90° em Y, Y com +90°
em X, os dois últimos com `Mirror Z`). O painel p/ eletro ganha um modificador `CPM_CUTOUT` com o recorte, que o plano
de corte leva para a usinagem.
