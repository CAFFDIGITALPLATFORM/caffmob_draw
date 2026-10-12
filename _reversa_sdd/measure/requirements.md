# Cotas de Módulo (measure) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/measure/` em 2026-10-10 (3 arquivos, 220 linhas; a árvore de trabalho não tem alterações sem commit nesta pasta, último commit que a tocou: `53f594c`). Confirmação de código não implica validação visual no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que exige decisão ou teste no Blender.

## Visão Geral

🟢 A unit calcula e aplica as **cotas de um módulo** (RN-04 da feature 002, decisão D-11): afastamento da parede, cota anterior, cota posterior, cota inferior e cota superior, medidas no referencial da parede em que o módulo está. Ler uma cota não altera nada; **aplicar** uma cota move o módulo para que a medida fique igual ao valor pedido, sem mudar largura, altura nem profundidade. A unit também oferece o cálculo de deslize ao longo da parede (`slide`, RF-34 da 002) usado pelo "Mover na Parede" e o pé-direito do projeto (`ceiling_height`) usado pelo Editor de Paredes. Fontes: `cotas.py` (núcleo puro, sem `bpy`), `scene_cotas.py` (ponte com a cena), `__init__.py` (só docstring).

## Responsabilidades

- 🟢 Representar o módulo (`Placement`) e as cinco cotas (`Cotas`) em metros, no referencial da parede (`cotas.py`).
- 🟢 Achar os limites laterais do módulo pelos obstáculos da mesma faixa de altura e pelas pontas da parede (`cotas.limits`).
- 🟢 Calcular as cotas de um módulo na parede (`cotas.compute`) e de um módulo livre (`cotas.compute_free`).
- 🟢 Resolver a cota inversa: dado campo e valor, devolver a nova posição, validando o domínio (`cotas.apply`).
- 🟢 Limitar o `x0` de um módulo arrastado ao longo da parede (`cotas.slide`).
- 🟢 Ler da cena o módulo, a parede, as dimensões, os obstáculos e o pé-direito, e escrever a posição (`scene_cotas.ModuleCotas`, `for_object`, `ceiling_height`).
- 🟢 Fora da responsabilidade: classificar objetos (contrato de `selection/classify.py`), listar os filhos da parede (`hb_placement.PlacementMixin.get_wall_children_sorted`, ver `_reversa_sdd/hb_placement/requirements.md` RN-12), desenhar as cotas no 3D (`overlays/selection_cotas.py`), expor os campos no painel (`ui/object_properties.py`), o modal "Mover na Parede" (contrato em `_reversa_sdd/move_over/design.md` F-08) e formatar unidades (`data/units.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Referencial da parede, em metros: X ao longo da parede (0 = início, `wall_length` = fim), Z = altura a partir da base da parede (piso), Y = profundidade com a **face da parede em Y = 0** e os módulos do lado da frente em Y < 0. `back_y` é o Y do fundo do módulo (a origem do módulo fica no fundo). | `cotas.py` (docstring); `scene_cotas.py:ModuleCotas.__init__` |
| RN-02 | 🟢 Cotas: `afastamento = −back_y`; `anterior = x0 − left`; `posterior = right − (x0 + width)`; `inferior = z0`; `superior = ceiling − (z0 + height)`. | `cotas.py:compute` |
| RN-03 | 🟢 Limites laterais: começa em `left = 0`, `right = wall_length`. Para cada obstáculo `(ox0, ox1, oz0, oz1)` cuja faixa de altura cruza **estritamente** a do módulo (`z0 < oz1 and oz0 < z1`): se `ox1 ≤ x0 + 1e-9`, `left = max(left, ox1)`; senão, se `ox0 ≥ x1 − 1e-9`, `right = min(right, ox0)`. Obstáculos que cruzam o módulo em X são **ignorados**. | `cotas.py:_vertical_overlap/limits` |
| RN-04 | 🟢 Aplicar uma cota muda só a posição (`x0`, `z0` ou `back_y`); `width` e `height` nunca mudam. Ordem de validação: `value < 0` → `ValueError("Valor Inválido: {rótulo} não pode ser negativa.")` antes de qualquer outra regra. | `cotas.py:apply` |
| RN-05 | 🟢 Inversas: `afastamento` → `back_y = −value`; `inferior` → `z0 = value` (sem teto); `superior` → `z0 = ceiling − value − height`, e `z0 < 0` → `ValueError("Valor Inválido: {rótulo} maior que o espaço até o piso.")`; `anterior` → `x0 = left + value`; `posterior` → `x0 = right − value − width`. Para `anterior`/`posterior`, `x0 < 0` ou `x0 + width > wall_length + 1e-9` → `ValueError("Valor Inválido: {rótulo} tira o módulo da parede.")`. Os limites (`left`, `right`) são os da posição **atual**; vizinhos do outro lado não são checados. Campo desconhecido → `ValueError(f"Cota desconhecida: {field}")` não traduzido. | `cotas.py:apply` |
| RN-06 | 🟢 Módulo livre (sem parede `IS_WALL_BP` como pai, do lado de trás, ou com rotação Z própria): só `inferior` e `superior`; `afastamento`, `anterior` e `posterior` são `None`. Aplicar uma dessas três → `ValueError("Valor Inválido: módulo livre (sem parede) não tem cota anterior, posterior ou afastamento.")` sem mudar nada. | `cotas.py:compute_free`; `scene_cotas.py:ModuleCotas.apply` |
| RN-07 | 🟢 Lado da frente da parede = rotação Z própria do módulo a menos de 0,01 rad de 0 (módulo `rz % 2π`, distância a 0 ou 2π) **e** `location.y < 0,5 · espessura` da parede (`Thickness`; falha na leitura → 0,0). Só módulos assim são "na parede". | `scene_cotas.py:_on_front_side/_wall_thickness` |
| RN-08 | 🟢 Pé-direito: `home_builder.ceiling_height` da cena principal (`hb_project.get_main_scene()`, ou a cena passada se não houver) quando `> 0`; senão o input `Height` da parede (se houver parede e a leitura não falhar); senão **2,6 m**. | `scene_cotas.py:ceiling_height` |
| RN-09 | 🟢 Dimensões do módulo, em ordem de preferência: inputs `Dim X/Y/Z` do Geometry Nodes quando `home_builder.mod_name` está preenchido; senão `btm_cabinet.width/depth/height` quando `btm_cabinet.width > 0`; senão `root.dimensions` (x, y, z). Qualquer exceção do Geometry Nodes cai para o próximo. | `scene_cotas.py:_dims` |
| RN-10 | 🟢 Obstáculos de um módulo na parede = filhos da parede devolvidos por `get_wall_children_sorted(wall, exclude_obj=root, object_z_start=z0, object_height=height)` (filtro vertical estrito; helpers com `obj_x` pulados), menos os que têm `IS_2D_ANNOTATION` ou `IS_SNAP_LINE`. Cada obstáculo vira `(x_start, x_end, z0, z1)` com a **faixa de altura do próprio módulo**. | `scene_cotas.py:ModuleCotas.obstacles`; `hb_placement.py:get_wall_children_sorted` |
| RN-11 | 🟢 Escrita: na parede, `root.location = (x0, back_y, z0)` (referencial local do pai); livre, `root.location.z += (novo z0 − z0 atual)`, onde `z0` atual é a Z **mundial** da origem. | `scene_cotas.py:ModuleCotas.__init__/apply` |
| RN-12 | 🟢 Deslizar (`slide`): com "Evitar Sobreposição", `x0 = clamp(target, left, max(left, right − width))`; sem, `x0 = clamp(target, 0, max(0, wall_length − width))`. | `cotas.py:slide` |
| RN-13 | 🟢 Só módulos e suas partes/frentes têm cotas: `for_object` usa `classify.classify(obj)` e aceita `MODULE`, `PART` e `FRONT`, sempre devolvendo as cotas da **raiz** do módulo. Qualquer outro tipo (geometria, parede, abertura, anotação, outro) → `None`. | `scene_cotas.py:for_object` |

## Requisitos Funcionais

🟡 Prioridades inferidas da feature 002 (`_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RF-18, RF-25, RF-34; `roadmap.md` D-11, D-12, D-17, D-36) e dos consumidores; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Calcular as cinco cotas de um módulo na parede | Must | CA-01 |
| RF-02 | 🟢 Aplicar uma cota digitada movendo o módulo e preservando as dimensões | Must | CA-02, CA-03, CA-04 |
| RF-03 | 🟢 Módulo livre: só cotas verticais, demais rejeitadas | Must | CA-05 |
| RF-04 | 🟢 Limites laterais por vizinhos da mesma faixa de altura e pelas pontas da parede | Must | CA-01, CA-06 |
| RF-05 | 🟢 Deslizar ao longo da parede com e sem "Evitar Sobreposição" (consumido por `caffmob.move_on_wall`) | Should | CA-07 |
| RF-06 | 🟢 Pé-direito do projeto com fallback (consumido pelas cotas e pelo Editor de Paredes, D-36) | Must | CA-08 |
| RF-07 | 🟢 Obter as cotas a partir de qualquer parte ou frente do módulo (`for_object`) | Must | CA-09 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Testabilidade | `cotas.py` não importa `bpy` (só `collections` e `data.i18n`, cujo `tr` devolve o texto original fora do Blender) | `cotas.py`; `data/i18n.py:tr`; `tests/test_cotas.py` | 🟢 |
| Internacionalização | Mensagens de erro e rótulos passam por `tr`/`N_`; chaves em `data/translations/measure.json` (4 mensagens) e `geral.json` (5 rótulos) com `pt_BR` e `en_US` | `cotas.py:LABELS/apply`; `scene_cotas.py:ModuleCotas.apply` | 🟢 |
| Sem estado persistente | A unit não registra classes nem propriedades; nada é gravado no `.blend` além de `location` do módulo | `__init__.py`; `scene_cotas.py` | 🟢 |
| Desempenho | Nenhuma meta verificável. Cada leitura recria `ModuleCotas` e relista os filhos da parede (o overlay faz isso a cada redesenho, o painel uma vez por campo) | `overlays/selection_cotas.py:_specs`; `ui/object_properties.py:_cota_getter` | 🟡 decisão: medir/testar (DT-03; questions.md#pergunta-74): medir com uma parede de ~30 módulos e só otimizar (cache) se o redesenho passar de alguns ms |

## Critérios de Aceitação

🟢 CA-01 a CA-05 e CA-07 têm cálculo coberto por `tests/test_cotas.py` (CA-05 só pela parte pura `compute_free`); CA-06 **não** tem teste (ver TT-02), mas foi conferido executando `cotas.limits`; _(Revisão 2026-10-10: tests/test_cotas.py tem 6 testes, nenhum de obstáculo que encosta/cruza; limits executado: (1.0, 3.0) e (0.0, 3.0))_ CA-08 e CA-09 dependem do Blender (`tests/blender_002_smoke.py` §6, não executado nesta extração).

```gherkin
CA-01 — Calcular cotas (feliz)
Dado parede de 3,0 m, pé-direito 2,6 m, balcão Placement(x0=1.0, width=0.6, z0=0.0, height=0.72, back_y=0.0)
E obstáculos (0.2, 0.8, 0.0, 0.72), janela alta (2.0, 2.8, 1.0, 2.2) e aéreo (1.0, 1.6, 1.4, 2.1)
Quando chamo cotas.compute
Então anterior = 0.2, posterior = 1.4 (janela e aéreo em outra faixa não contam), inferior = 0.0, superior = 1.88, afastamento = 0.0

CA-02 — Aplicar cota anterior (feliz)
Dado o mesmo balcão e obstáculos
Quando aplico 'anterior' = 0.075
Então x0 = 0.875, width = 0.6 e recalcular dá anterior = 0.075

CA-03 — Aplicar as outras cotas (feliz)
Dado o mesmo balcão
Quando aplico 'posterior' 0.1, 'inferior' 0.15, 'superior' 1.0 e 'afastamento' 0.02 (cada um a partir do original)
Então x0 = 2.3, z0 = 0.15, z0 = 0.88 e back_y = −0.02, respectivamente

CA-04 — Cota inválida (falha)
Dado o mesmo balcão
Quando aplico 'anterior' = −0.01, ou 'posterior' = 2.6, ou 'superior' = 2.5
Então ValueError com mensagem iniciada por "Valor Inválido" (negativa / tira o módulo da parede / maior que o espaço até o piso)
E a Placement original não muda; via ModuleCotas, root.location não é escrito

CA-05 — Módulo livre
Dado um módulo sem parede como pai (ou do lado de trás, ou girado)
Quando leio as cotas
Então afastamento, anterior e posterior são None e inferior/superior são calculadas pela Z mundial da origem
E aplicar 'anterior', 'posterior' ou 'afastamento' levanta "Valor Inválido: módulo livre…" sem mover nada

CA-06 — Obstáculo que encosta ou cruza
Dado o balcão em x0 = 1.0
Quando um obstáculo termina exatamente em 1.0 na mesma faixa, e outro começa na altura 0.72 (topo do balcão)
Então left = 1.0 (encosta conta) e o segundo é ignorado (sobreposição de altura estrita)
E um obstáculo de 0.9 a 1.1 (cruzando o módulo em X) é ignorado: limites (0.0, 3.0)

CA-07 — Deslizar
Dado o balcão, os obstáculos de CA-01 e parede de 3,0 m
Quando chamo slide com destino 1.5, 0.0 e 9.0 (avoid=True), e 0.0 com avoid=False
Então x0 = 1.5, 0.8 (para no vizinho), 2.4 (janela alta não bloqueia) e 0.0

CA-08 — Pé-direito
Dado a cena principal com home_builder.ceiling_height = 2.7
Quando chamo ceiling_height(scene, wall)
Então devolve 2.7
E com ceiling_height = 0 devolve o input Height da parede; sem parede e sem valor, 2.6

CA-09 — Cotas a partir de uma porta (feliz) / objeto sem cotas (falha)
Dado um balcão Frameless filho de uma parede, do lado da frente
Quando chamo for_object com a porta do balcão
Então devolve ModuleCotas da raiz do balcão com on_wall = True e wall_length = Length da parede
E for_object com a própria parede, uma janela ou None devolve None
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-04, RF-06, RF-07 | 🟡 Must | RF-18 da 002 é Must; chamados por 4 consumidores (painel, overlay, Mover na Parede, Editor de Paredes) |
| RF-05 | 🟡 Should | RF-34 da 002 é Should |
| Cotas para geometrias (002 RF-18: "módulos e geometrias") | 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-73):** Won't (nesta versão) | `for_object` não aceita `GEOMETRY` |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/measure/cotas.py | `Cotas`, `Placement`, `FIELDS`, `LABELS`, `_vertical_overlap`, `limits`, `compute`, `compute_free`, `apply`, `slide` | 🟢 Código; `tests/test_cotas.py` |
| caffmob_draw/measure/scene_cotas.py | `_dims`, `_wall_of`, `_on_front_side`, `_wall_thickness`, `ceiling_height`, `ModuleCotas`, `for_object` | 🟢 Código; `tests/blender_002_smoke.py` §6 (não executado) |
| caffmob_draw/measure/__init__.py | Só docstring `"Pacote measure (feature 002)."` | 🟢 Código |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_cotas -v`: **6 testes aprovados** (cálculo, anterior 75 mm, outras cotas, inválidos, módulo livre, deslizar). Não cobrem `scene_cotas.py`. O arquivo `tests/test_measure_expr.py` testa `data/expr.py` (feature 009), não esta unit (6 testes, também aprovados).

## Lacunas e Pré-condições

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-12):** rejeitar com "Valor Inválido" a cota `anterior`/`posterior` que sobrepõe o vizinho do lado oposto e a `inferior` que passa do teto. 🟢 (código) hoje nenhuma das duas é validada (EC-01, EC-02). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-13):** medir até a lateral real de vizinhos sem Geometry Nodes, pela largura de `btm_cabinet` ou pelo bounding box, como `_dims` já faz para o próprio módulo. 🟢 (código) hoje entram como obstáculo de **largura e altura zero** em `get_wall_children_sorted` (EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-73):** cotas para geometrias ficam como Won't nesta versão; o código já não as oferece (`for_object` só aceita MODULE/PART/FRONT). A atualização do RF-18 da 002 fica para o ciclo forward (fora de `_reversa_sdd/`).
- 🟡 Sem meta de desempenho medida para o recálculo por redesenho — decisão: medir/testar (DT-03; questions.md#pergunta-74).
- 🟢 Pré-condição: `selection/classify.py` (`classify`, `MODULE`, `PART`, `FRONT`), `hb_types.GeoNodeObject/GeoNodeWall.get_input`, `hb_placement.PlacementMixin.get_wall_children_sorted`, `hb_project.get_main_scene`, `data/i18n.py` (`tr`, `N_`) disponíveis com os contratos citados em `design.md` › Dependências.
