# Data delta: câmeras sem objeto alvo

> Identificador: `027-janela-plano-corte-e-medicao-malha`
> Data: `2026-11-26`

## 1. O que mudou

| Antes | Depois |
|-------|--------|
| Coleção `Câmeras do Promob` | Coleção `CAMERAS`, com `color_tag` aleatória entre `COLOR_01` e `COLOR_08` |
| Cada câmera tinha um Empty `<nome> · alvo` e uma restrição `TRACK_TO` | Nenhum objeto novo na cena; a orientação é calculada em `_apontar` |
| `obj['btm_camera_alvo']` guardava o **nome** do Empty | `obj['btm_camera_alvo']` guarda a **posição** `(x, y, z)` do alvo |

## 2. Preferências e alvo da seleção (fases 2 e 3)

| Antes | Depois |
|-------|--------|
| O interruptor Linhas ligava `View3DOverlay.show_wireframes` (wireframe do tema) | `show_wireframes` fica desligado; as arestas pretas vêm de `overlays/arestas.py`, com `BTM_AddonPreferences.espessura_aresta` (padrão 0,2 px) |
| Nenhuma preferência de aplicação em lote | `BTM_AddonPreferences.aplicar_em_todos` (padrão ligado) |
| `Target` só tinha `multi_thickness` | `Target.multi_sizes`: (largura, altura, profundidade, espessura) editáveis de cada selecionado; `multi_thickness` continua, derivado dele |
| `Scene.btm_selection.multi_thickness` era `FloatProperty` e aplicava direto | `multi_width`, `multi_height`, `multi_depth` e `multi_thickness` são `StringProperty` com `options=set()`: vazio com `?` quando diverge, e a escrita passa por `caffmob.target_multi_apply` |

Nada é gravado no `.blend`: as preferências são do add-on (fora da cena e do Desfazer), e o alvo da seleção é
recalculado pelo snapshot a cada mudança de seleção ou de cena.

## 3. Migração

Ler o alvo (`alvo_de`) já migra:

- valor é texto (nome de Empty): copia a posição do Empty, grava a lista de três números, aponta a câmera e remove o
  Empty;
- Empty já apagado: o alvo vira a posição atual da câmera;
- valor ausente: alvo na posição da câmera;
- valor é lista: já migrado.

A posição do Empty é lida de `matrix_basis` quando ele não tem pai (vale na hora, ao contrário de `matrix_world`, que
só depois da avaliação do grafo — e esta leitura pode acontecer durante o desenho).

## 4. Compatibilidade

- `alvo_de` devolve **ponto (`Vector`)**, não objeto. Quem lia `.location` ou `.matrix_world` mudou junto:
  `_get`/`_set` de Altura do alvo, Atualizar pela vista, Remover câmera e Percorrer (que agora anima
  `location` + `rotation_quaternion` da câmera, sem animar um Empty).
- Projetos antigos continuam abrindo: a migração acontece na primeira leitura, sem passo manual.
