# Porta e Janela Reais e Região na Parede (openings) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/openings/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`; EC-xx os de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Contratos de outras units são citados, não redescritos: Editor de Paredes em `_reversa_sdd/walls2d/` (F-12 `apply_plan` re-sincroniza as aberturas), seleção e medida pela folha em `_reversa_sdd/selection/` (RN-07, RN-22, RN-23, EC-08), snap e cabeçalho do `PlacementMixin` em `_reversa_sdd/hb_placement/`, cotas em `_reversa_sdd/measure/`, "Mover Sobre" em `_reversa_sdd/move_over/` (porta e janela não são movíveis por ele).

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `door_core.py` (192) | não (`dataclasses`) | `Part`, constantes, furo ↔ folha, peças da porta | 🟢 |
| Núcleo puro | `window_core.py` (71) | não (importa `FRAME`, `LEAF`, `LEAF_HW`, `Part` de `door_core`) | Peças da janela de correr e curso | 🟢 |
| Núcleo puro | `region_core.py` (50) | não (`collections.namedtuple`, `data.i18n.N_`) | Encaixe da região | 🟢 |
| Ponte | `materials.py` (81) | sim | 8 materiais compartilhados | 🟢 |
| Ponte | `build.py` (94) | sim (`bmesh`) | Uma malha por papel | 🟢 |
| Ponte | `sync.py` (212) | sim; usa `hb_types`, `aggregates.apply/collision/group/leaf`, `inspection.room_door_leaf` | Montar/refazer na caixa | 🟢 |
| Estado | `props.py` (36), `region_props.py` (55) | sim | `Object.btm_opening_real` (salvo), `WindowManager.btm_wall_region` (sessão) | 🟢 |
| Blender | `ops.py` (98) | sim | Atualizar, tecla I | 🟢 |
| Blender | `region.py` (256) | sim (`gpu`, `blf`, `bpy_extras.view3d_utils`, `mathutils.geometry`) | Modal de marcar, limpar, desenho, `load_post` | 🟢 |
| Pacote | `__init__.py` (24) | não diretamente | Registra `props`, `ops`, `ui.view_mode`, `region_props`, `region` nessa ordem; `unregister` na inversa. É chamado por `caffmob_draw/__init__.py` (`openings.register()`), antes de `selection` | 🟢 |

## Interface

### `door_core.py` 🟢

| Símbolo | Valor / assinatura | Observação |
|---|---|---|
| Papéis | `FRAME, FRAME_HW, LEAF, LEAF_HW` (strings iguais ao nome) | Marco, ferragem do marco, folha, ferragem da folha |
| Materiais | `WOOD, METAL, RUBBER, SLOT, BRASS` | Chaves de `materials.SPECS` |
| Constantes | `LEAF_T=0.040`, `FLOOR_GAP=0.008`, `MARCO=0.046`, `GAP=0.003`, `SIDE=MARCO+GAP`, `TOP=0.059`, `CENTER_GAP=0.003`, `HANDLE_Z=1.02` | RN-01, RN-02 |
| `Part` | `@dataclass(frozen=True)`: `role`, `name`, `shape` (`'BOX'`, `'CYL_X'`, `'CYL_Y'`, `'CYL_Z'`), `center` (tupla), `size` (tupla), `material=WOOD`, `bevel=0.001`, `leaf=None`, `horizontal=False` | `size` do cilindro = (diâmetro, diâmetro, altura no eixo) |
| `Part.size_xyz` | BOX → `size`; `CYL_X` → `(h, d, d)`, `CYL_Y` → `(d, h, d)`, `CYL_Z` → `(d, d, h)` | Extensão nos eixos |
| `Part.lo` / `Part.hi` | `center ∓ size_xyz/2` | Caixa envolvente |
| `hole_size(width, height, double=False)` | `(round(leaves + 2·SIDE, 6), round(height + TOP, 6))`, `leaves = 2·width + CENTER_GAP` se dupla | `width` é **cada** folha |
| `leaf_size(hole_w, hole_h, double=False)` | `(round((hole_w − 2·SIDE − CENTER_GAP)/2 se dupla, senão hole_w − 2·SIDE, 6), round(hole_h − TOP, 6))` | Inverso |
| `_Builder` | `parts`; `box(role, name, center, size, material=WOOD, bevel=0.001, leaf=None, horizontal=False)`; `cyl(role, name, center, radius, depth, axis='Z', material=METAL, leaf=None)` (bevel 0,00035, `size = (2r, 2r, depth)`); `screw_y(role, name, x, y, z, leaf=None)` | Referencial do gerador: folha de `x0` a `x0+w`, centrada em y = 0 |
| `door_parts(width, height, wall, hinge='LEFT', side='NEG_Y', double=False, open_door=False)` | `list[Part]` no referencial da caixa | F-01 |

**`_leaf(b, x0, w, h, leaf, hinge_left, lock)`** 🟢 — `X(x) = x0 + x` se `hinge_left`, senão `x0 + w − x` (x medido do lado da dobradiça); `zc = FLOOR_GAP + h/2`. Peças (centro; tamanho; material padrão `WOOD`, bevel 0,001 salvo indicação):

| Peça (papel) | Centro | Tamanho / extras |
|---|---|---|
| `Folha_montante_dobradicas` (LEAF) | `(X(0.055), 0, zc)` | `(0.11, LEAF_T, h)` |
| `Folha_montante_fechadura` (LEAF) | `(X(w − 0.055), 0, zc)` | `(0.11, LEAF_T, h)` |
| `Folha_travessa_inferior/central/superior` (LEAF, `horizontal`) | `(x0 + w/2, 0, z)` com `z_low = FG + 0.07`, `z_mid = FG + h·(0.93/2.1)`, `z_top = FG + h − 0.065` | `(w − 0.22, LEAF_T, 0.14 / 0.14 / 0.13)` |
| `Almofada_0`, `Almofada_1` (LEAF) | `(x0 + w/2, 0, (b + t)/2)` com `(b, t)` = `(z_low + 0.07, z_mid − 0.07)` e `(z_mid + 0.07, z_top − 0.065)` | `(w − 0.218, 0.021, t − b + 0.002)` |
| `Friso_vertical` (LEAF; ×2 por face por almofada) | `(x0 + 0.117 e x0 + w − 0.117, ±0.014, (b + t)/2)` | `(0.014, 0.010, t − b)`, bevel 0,0025 |
| `Friso_horizontal` (LEAF, `horizontal`; ×2 por face) | `(x0 + w/2, ±0.014, b + 0.007 e t − 0.007)` | `(w − 0.248, 0.010, 0.014)`, bevel 0,0025 |
| `Vedacao_inferior` (LEAF) | `(x0 + w/2, 0, FG + 0.002)` | `(w − 0.02, 0.021, 0.004)`, `RUBBER` |
| Dobradiças, para `z` em `(0.25, FG + h/2 − 0.008, FG + h − 0.248)` | — | — |
| `Dobradica_folha` (LEAF_HW) | `(X(0.015), −0.0215, z)` | `(0.032, 0.003, 0.09)`, `METAL` |
| `Dobradica_marco` (FRAME_HW) | `(X(−0.019), −0.023, z)` | idem |
| `No_dobradica` ×5 (k par LEAF_HW, ímpar FRAME_HW), cilindro Z | `(X(−0.003), −0.025, z − 0.036 + k·0.018)` | raio 0,006, altura 0,0175 |
| `Pino_dobradica` ×2 (FRAME_HW), cilindro Z | `(X(−0.003), −0.025, z ± 0.047)` | raio 0,0064, altura 0,003 |
| `Parafuso_dobradica` (LEAF_HW) e `Parafuso_marco` (FRAME_HW), `screw_y` em `dz ∈ (−0.03, 0, 0.03)` | `(X(0.017), −0.024, z + dz)` e `(X(−0.021), −0.026, z + dz)` | cilindro Y raio 0,0034, altura 0,0015 + 2 fendas `SLOT` `(0.0045, 0.0003, 0.0008)` e `(0.0008, 0.0003, 0.0045)` em `y + sinal·0.00085`, bevel 0,0001 |
| Maçanetas, para `side ∈ (−1, 1)`; `hx = X(w − 0.064)`, `lever = X(w − 0.117)` | — | — |
| `Roseta_macaneta` (LEAF_HW, cilindro Y) | `(hx, side·0.024, HANDLE_Z)` | raio 0,026, altura 0,008 |
| `Anel_macaneta` (LEAF_HW, cilindro Y) | `(hx, side·0.029, HANDLE_Z)` | raio 0,0215, altura 0,002 |
| `Eixo_macaneta` (LEAF_HW, cilindro Y) | `(hx, side·0.048, HANDLE_Z)` | raio 0,009, altura 0,038 |
| `Alavanca_macaneta` (LEAF_HW) | `(lever, side·0.069, HANDLE_Z)` | `(0.125, 0.020, 0.017)`, `METAL`, bevel 0,007 |
| Com `lock`: `Roseta_chave`, `Cilindro_chave` (`BRASS`), `Rasgo_chave` (`SLOT`, bevel 0,0003) | `(hx, side·0.024, HZ − 0.088)`, `(hx, side·0.029, HZ − 0.084)`, `(hx, side·0.031, HZ − 0.087)` | raio 0,024/alt. 0,008; raio 0,009/alt. 0,003; `(0.002, 0.001, 0.014)` |
| Com `lock`: `Testa_fechadura` (LEAF_HW), `Lingueta` (LEAF_HW, `BRASS`, bevel 0,002), `Contratesta` (FRAME_HW) | `(X(w + 0.001), 0, HZ − 0.042)`, `(X(w + 0.005), 0, HZ)`, `(X(w + 0.002), 0, HZ)` | `(0.002, 0.026, 0.18)`, `(0.010, 0.014, 0.014)`, `(0.002, 0.034, 0.088)`, `METAL` exceto a lingueta |

🟢 As alturas das dobradiças (0,25 m) e da maçaneta (`HANDLE_Z` 1,02 m) são absolutas (não escalam com `h`).

**`_frame(b, span, h, wall, leaves)`** 🟢 — `marco_h = h + 0.016`; `face = wall/2 + 0.0085`.

| Peça (FRAME) | Centro | Tamanho / extras |
|---|---|---|
| `Marco_esquerdo` / `Marco_direito` | `(−0.026 / span + 0.026, 0, marco_h/2)` | `(MARCO, wall, marco_h)` |
| Com `leaves`: `Batente_esquerdo/direito` | `(x ± 0.020 para dentro, 0.034, marco_h/2)` | `(0.019, 0.024, marco_h)`, bevel 0,0015 |
| Com `leaves`: `Vedacao_esquerdo/direito` | `(x ± 0.023 para dentro, 0.021, h/2 + 0.006)` | `(0.010, 0.004, h)`, `RUBBER` |
| `Marco_superior` (`horizontal`) | `(span/2, 0, h + 0.036)` | `(span + 0.098, wall, MARCO)` |
| Com `leaves`: `Batente_superior` (`horizontal`), `Vedacao_superior` (`RUBBER`) | `(span/2, 0.034, h + 0.014)`, `(span/2, 0.021, h + 0.011)` | `(span + 0.006, 0.024, 0.018)`, `(span, 0.004, 0.004)` |
| `Guarnicao_vertical` ×4 | `(−0.043 e span + 0.043, ±face, (h + 0.044)/2)` | `(0.072, 0.017, h + 0.044)`, bevel 0,002 |
| `Filete_guarnicao` ×4 | `(idem, ±(face + 0.011), (h + 0.04)/2)` | `(0.043, 0.006, h + 0.04)`, bevel 0,0015 |
| `Guarnicao_superior` ×2 (`horizontal`) | `(span/2, ±face, h + 0.08)` | `(span + 0.158, 0.017, 0.072)`, bevel 0,002 |
| `Filete_superior` ×2 (`horizontal`) | `(span/2, ±(face + 0.011), h + 0.08)` | `(span + 0.154, 0.006, 0.043)`, bevel 0,0015 |

### `window_core.py` 🟢

| Símbolo | Valor / assinatura |
|---|---|
| Materiais | `ALU`, `GLASS`, `STONE` |
| Constantes | `PROFILE=0.040`, `SASH=0.035`, `SASH_DEPTH=0.030`, `GLASS_T=0.004`, `OVERLAP=0.050`, `SILL_T=0.020`, `SILL_OUT=0.030` |
| `_box(parts, role, name, lo, hi, material, leaf=None, bevel=0.0008)` | Acrescenta `Part(role, name, 'BOX', centro, hi − lo, material, bevel, leaf)` (sem `horizontal`) |
| `travel(width)` | `round(inner − (inner/2 + OVERLAP/2), 6)`, `inner = width − 2·PROFILE` |
| `window_parts(width, height, wall)` | 25 peças (`lo` → `hi`), com `P = PROFILE`, `mid = wall/2`, trilhos em `y ∈ (mid − 0.020, mid + 0.020)` |

| Peça | `lo` → `hi` | Papel / material / bevel |
|---|---|---|
| `Marco_esquerdo`, `Marco_direito` | `(0, 0, 0)→(P, wall, h)`, `(w − P, 0, 0)→(w, wall, h)` | FRAME, `ALU` |
| `Marco_inferior`, `Marco_superior` | `(P, 0, 0)→(w − P, wall, P)`, `(P, 0, h − P)→(w − P, wall, h)` | FRAME, `ALU` |
| `Trilho_inferior` / `Trilho_superior` ×2 (um por trilho) | `(P, y − 0.0015, z0)→(w − P, y + 0.0015, z1)` com `z` `P..P + 0.008` / `h − P − 0.008..h − P` | FRAME, `ALU` |
| Por folha `i`: `x0 = P` (i = 0, trilho 0) ou `w − P − sash_w` (i = 1, trilho 1); `sash_w = (w − 2P)/2 + OVERLAP/2`; `x1 = x0 + sash_w`; `z0 = P + 0.005`, `z1 = h − P − 0.005`; `ya, yb = y ∓ SASH_DEPTH/2` | — | — |
| `Folha_montante` ×2 | `(x0, ya, z0)→(x0 + SASH, yb, z1)`, `(x1 − SASH, ya, z0)→(x1, yb, z1)` | LEAF i, `ALU` |
| `Folha_travessa` ×2 | `(x0 + SASH, ya, z0)→(x1 − SASH, yb, z0 + SASH)`, `(x0 + SASH, ya, z1 − SASH)→(x1 − SASH, yb, z1)` | LEAF i, `ALU` |
| `Vidro` | `(x0 + SASH − 0.006, y − GLASS_T/2, z0 + SASH − 0.006)→(x1 − SASH + 0.006, y + GLASS_T/2, z1 − SASH + 0.006)` | LEAF i, `GLASS`, bevel 0 |
| `Puxador_concha` | `grip_x = x0 + SASH/2` (i = 0) ou `x1 − SASH/2` (i = 1); `(grip_x − 0.008, ya − 0.006, zc − 0.06)→(grip_x + 0.008, ya, zc + 0.06)`, `zc = (z0 + z1)/2` | LEAF_HW i, `ALU`, bevel 0,003 |
| `Guarnicao_esquerda`, `_direita`, `_superior` | `(−0.05, wall, 0)→(0, wall + 0.012, h + 0.05)`, `(w, wall, 0)→(w + 0.05, wall + 0.012, h + 0.05)`, `(−0.05, wall, h)→(w + 0.05, wall + 0.012, h + 0.05)` | FRAME, `ALU` |
| `Peitoril` | `(−SILL_OUT, −SILL_OUT, −SILL_T)→(w + SILL_OUT, wall + SILL_OUT, 0)` | FRAME, `STONE`, bevel 0,002 |
| `Peitoril_pingadeira` | `(−SILL_OUT + 0.01, −SILL_OUT + 0.008, −SILL_T − 0.004)→(w + SILL_OUT − 0.01, −SILL_OUT + 0.014, −SILL_T)` | FRAME, `STONE`, bevel 0 |

### `region_core.py` 🟢

| Símbolo | Valor / assinatura |
|---|---|
| `Fit` | `namedtuple('Fit', 'ok x width height sill reason')` |
| Motivos | `EMPTY, OUTSIDE, TOO_TALL, OVERLAP` (strings iguais ao nome) |
| `MIN_SIZE`, `TOLERANCE` | `0.001`, `0.005` |
| `REASONS` | `N_`: EMPTY "A região está vazia: clique em dois cantos opostos"; OUTSIDE "A região passa da ponta da parede"; TOO_TALL "A região é mais alta que a parede"; OVERLAP "A região encosta em outra porta ou janela" |
| `_refuse(reason)` | `Fit(False, 0.0, 0.0, 0.0, 0.0, reason)` |
| `fit(x0, x1, z0, z1, wall_length, wall_height, kind, others=())` | F-02; `others` = iterável de `(x0, x1, z0, z1)` |

### `materials.py` 🟢

| Símbolo | Valor / assinatura |
|---|---|
| `TAG` | `'btm_opening_material'` (idprop no material) |
| `ASSETS` | `<pasta de openings>/assets` |
| `SPECS[key] = (nome, cor RGB, metálico, rugosidade, extras)` | `WOOD` ("Nogueira verniz acetinado", (0.32, 0.18, 0.075), 0, 0.35, Coat Weight 0.18, Coat Roughness 0.3); `METAL` ("Aço inox escovado", (0.46, 0.49, 0.51), 1, 0.27); `RUBBER` ("Borracha EPDM", (0.012, 0.016, 0.014), 0, 0.68); `SLOT` ("Cavidades das ferragens", (0.019, 0.022, 0.025), 0.6, 0.42); `BRASS` ("Latão", (0.48, 0.30, 0.10), 0.85, 0.3); `ALU` ("Alumínio anodizado", (0.78, 0.79, 0.80), 1, 0.18, Coat Weight 1.0, Coat Roughness 0.05); `GLASS` ("Vidro", (0.86, 0.92, 0.95), 0, 0.02, Transmission Weight 1.0, IOR 1.52, Alpha 0.25); `STONE` ("Granito cinza", (0.36, 0.36, 0.37), 0, 0.22, Coat Weight 0.4) |
| `_image(name)` | `None` se o arquivo não existe; senão `bpy.data.images.load(path, check_existing=True)` |
| `_wood_textures(mat, bsdf)` | Sem a imagem de cor → nada. Senão: `ShaderNodeTexImage` (cor) em `(bsdf.x − 400, bsdf.y + 120)` → `Base Color`; `ShaderNodeBump` (Strength 0,025, Distance 0,00022) em `(x − 200, y − 260)`, cor → `Height`, `Normal` → `Normal` do BSDF; com a de rugosidade: `colorspace_settings.name = 'Non-Color'`, nó em `(x − 400, y − 160)` → `Roughness` |
| `get(key)` | F-03 |

### `build.py` 🟢

| Símbolo | Valor / assinatura |
|---|---|
| `BEVEL` | `0.001` |
| `_AXIS` | `CYL_X`: `Matrix.Rotation(π/2, 4, 'Y')`; `CYL_Y`: `Matrix.Rotation(π/2, 4, 'X')`; `CYL_Z`: identidade |
| `group_key(part)` | `(role, None)` para `FRAME`/`FRAME_HW`; senão `(LEAF se role == LEAF ou material ∈ {ALU, GLASS}, senão LEAF_HW, part.leaf)` |
| `group_name(key)` | "Marco", "Ferragens do marco", "Folha {leaf+1}", "Ferragens da folha {leaf+1}" |
| `_add_part(bm, part, slot, uv_layer)` | F-04 |
| `build(parts, collection, window=False)` | `dict[(role, leaf)] → Object`; F-04. O parâmetro `window` não é usado |

### `sync.py` 🟢

| Símbolo | Assinatura | Retorno / comportamento |
|---|---|---|
| `DOOR_FLAG`, `WINDOW_FLAG`, `SWING_MAX` | `'IS_ENTRY_DOOR_BP'`, `'IS_WINDOW_BP'`, `90.0` | — |
| `is_opening(obj)` | — | Valor truthy de `obj.get(DOOR_FLAG) or obj.get(WINDOW_FLAG)` (não `bool`); `None` → falso |
| `_swing(cage)` | — | `(filho, Is Left, Swing Inside, Is Double)` do **primeiro** filho com `IS_2D_ANNOTATION` (lidos por `GeoNodeObject.get_input`, `bool`); exceção → `(filho, True, True, False)`; sem filho → `(None,)*4` |
| `kind_of(cage)` | — | RN-06 |
| `_dims(cage)` | — | `GeoNodeCage(cage).get_input('Dim X'), ('Dim Y'), ('Dim Z')` = largura, espessura, altura |
| `signature(cage)` | — | RN-09 |
| `_parts(cage, kind)` | — | Janela: `window_parts(DimX, DimZ, DimY)`. Porta: `leaf_size(DimX, DimZ, double)` e `door_parts(leaf_w, leaf_h, DimY, hinge='RIGHT' se Is Left senão 'LEFT', side='NEG_Y' se Swing Inside ou None senão 'POS_Y', double=kind == 'DOUBLE_DOOR', open_door=kind == 'OPEN_DOOR')` |
| `_remember(assembly)` | — | `(opens: dict[nome-base → open_value], production: set[nome-base])` sobre `[assembly] + children_recursive`; `None` → vazios |
| `clear(cage)` | — | F-05b |
| `_to_world(cage, objs)` | — | `obj.matrix_world = cage.matrix_world @ obj.matrix_world` |
| `_parent_keep(obj, parent)` | — | Guarda a matriz de mundo, `parent`, `matrix_parent_inverse = Identity`, restaura a matriz de mundo |
| `_align(obj, cage)` | — | Guarda as matrizes de mundo dos filhos; `obj.matrix_world = Translation(obj.translation) @ rotação de cage.matrix_world`; restaura os filhos |
| `_style_cage(context, cage)` | — | RN-13 |
| `sync(context, cage, force=False)` | — | `bool` (montou algo); F-05 |
| `openings(scene)` | — | `[o for o in scene.objects if is_opening(o)]` |
| `outdated(scene)` | — | Aberturas com `model_version < MODEL_VERSION` ou `assembly is None` |

### `props.py` 🟢

| Propriedade (`BTM_PG_Opening`, em `Object.btm_opening_real`) | Definição | Persistência |
|---|---|---|
| `kind` | `EnumProperty(items=KIND_ITEMS, default='NONE')`; `KIND_ITEMS` = `NONE` "Nenhum" ("Caixa antiga, sem a porta real"), `DOOR` "Porta", `DOUBLE_DOOR` "Porta dupla", `OPEN_DOOR` "Vão aberto", `WINDOW` "Janela" | `.blend` |
| `signature` | `StringProperty()` | `.blend` |
| `model_version` | `IntProperty(default=0)`; `MODEL_VERSION = 1` | `.blend` |
| `assembly` | `PointerProperty(type=bpy.types.Object)` → grupo `FRAME` | `.blend` |

🟢 `register`: classe e `bpy.types.Object.btm_opening_real = PointerProperty(type=BTM_PG_Opening)`; `unregister`: `del` se existir e desregistra a classe se registrada. Quem grava `kind` na criação é `doors_windows.create_placed_object` (`OPENING_KIND` da classe: `DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`, `WINDOW`) e a duplicação copia o `kind` da origem se ≠ `NONE`.

### `region_props.py` 🟢

| Propriedade (`BTM_PG_WallRegion`, em `WindowManager.btm_wall_region`) | Definição |
|---|---|
| `active` | `BoolProperty(default=False)` |
| `wall` | `StringProperty()` (nome, não ponteiro) |
| `x0`, `x1`, `z0`, `z1` | `FloatProperty(subtype='DISTANCE', unit='LENGTH')`, sem `min`/`max` |
| `side` | `EnumProperty(items=[('FRONT', "Frente", ""), ('BACK', "Fundo", "")], default='FRONT')` |

- `region_wall(context)` → `(região, parede)` se `active` e `bpy.data.objects.get(region.wall)` tem `IS_WALL_BP`; senão grava `active = False` (se a parede sumiu) e devolve `(None, None)`. 🟢
- `clear(context)` → `active = False` se a propriedade existe. 🟢

### `ops.py` 🟢

| Operador | `bl_idname` | `bl_label` | `bl_options` | `poll` | `execute` |
|---|---|---|---|---|---|
| `BTM_OT_OpeningsUpdate` | `caffmob.openings_update` | "Atualizar portas e janelas" | `{'REGISTER', 'UNDO'}` | `context.scene is not None` | `cages = outdated(scene)`; `done = soma de sync(force=True)`; sem caixas → INFO "Todas as portas e janelas já estão atualizadas"; senão INFO "{} porta(s) e janela(s) atualizada(s)"; `FINISHED` |
| `BTM_OT_DoorInvertHand` | `btm.door_invert_hand` | "Inverter giro da porta" | `{'REGISTER', 'UNDO'}` | ativo não nulo, `select_get()` e `door_of(ativo)` não nulo | F-06 |

- `door_of(obj)`: sobe de `obj` pelos pais; no **primeiro** com `IS_ENTRY_DOOR_BP` devolve ele se `_swing(...)[0]` não é `None`, senão `None` (não continua subindo). 🟢
- Keymap: `keyconfigs.addon`, mapa "Object Mode" (`space_type='EMPTY'`), `I` `PRESS` com `head=True` → `btm.door_invert_hand`. 🟢

### `region.py` 🟢

| Símbolo | Valor / assinatura |
|---|---|
| `_draw_handle`, `_addon_keymaps`, `_live` | `[None]`, `[]`, `{}` (prévia: `wall` (nome), `side`, `a`, `b` com cantos `(x, z)` locais) |
| `FILL`, `LINE`, `TEXT` | `(0.2, 0.55, 1.0, 0.18)`, `(0.25, 0.6, 1.0, 0.95)`, `(1, 1, 1, 1)` |
| `_face_y(wall, side)` | `GeoNodeWall(wall).get_input('Thickness')` se `BACK`, senão `0.0` |
| `_rect_world(wall, side, x0, x1, z0, z1)` | 4 cantos `matrix_world @ (x, y_face, z)` na ordem (x0,z0), (x1,z0), (x1,z1), (x0,z1) |
| `_draw_rect(context, wall, side, x0, x1, z0, z1)` | F-08 |
| `draw_regions()` | F-08 |
| `_tag_redraw(context)` | `tag_redraw()` em toda área `VIEW_3D` de todas as janelas |
| `on_load_post(*_args)` | `@persistent`; `_live.clear()`; `region_props.clear` se há `window_manager` |

| Operador | `bl_idname` | `bl_label` | `bl_options` | `poll` |
|---|---|---|---|---|
| `BTM_OT_WallRegion` (`Operator`, `hb_placement.PlacementMixin`) | `caffmob.wall_region` | "Marcar região" | `{'REGISTER'}` | `context.mode == 'OBJECT'` e algum objeto da cena com `IS_WALL_BP` |
| `BTM_OT_WallRegionClear` | `caffmob.wall_region_clear` | "Limpar região" | `{'REGISTER'}` | `btm_wall_region` existe e `active` |

- Métodos do modal: `_ray()` (origem e direção por `view3d_utils.region_2d_to_origin_3d/region_2d_to_vector_3d` em `self.mouse_pos` e `self.region.data`); `_wall_hit(context)` (`scene.ray_cast(evaluated_depsgraph_get(), origin, direction)`; sobe pelos pais do objeto atingido até `IS_WALL_BP`; devolve `(parede, ponto)` ou `(None, None)`); `_local(wall, side, snap_fine)` (F-07, passo 4); `_header(context)`; `_end(context)` (limpa `_live`, cabeçalho, cursor `DEFAULT`, redesenha). 🟢
- `register`: classes; `SpaceView3D.draw_handler_add(draw_regions, (), 'WINDOW', 'POST_PIXEL')` se `_draw_handle[0]` é `None`; `load_post.append(on_load_post)` se ausente; keymap "3D View" (`VIEW_3D`) `ESC` `PRESS` → `caffmob.wall_region_clear` (só com `keyconfigs.addon`). `unregister`: remove keymap (engole `ReferenceError`/`RuntimeError`), `load_post`, `draw_handler_remove`, `_live.clear()`, classes registradas em ordem inversa. 🟢

### Superfície usada pelos consumidores 🟢 (fora da unit, citada para reimplementação)

| Consumidor | Usa | Contrato |
|---|---|---|
| `operators/doors_windows.py:_sync_opening(context, obj)` | `sync.sync` | `try`/`except Exception` → `print("CAFFMob Draw: porta/janela real não montada (…)")`, `False`. Chamado ao confirmar a inserção, no `check()` dos diálogos de porta e janela e em "Flip Door Swing"/"Flip Door Hand" |
| `doors_windows._leaf_to_hole(kind, axis, value)` / `_hole_to_leaf` | `door_core.hole_size` / `leaf_size` | Só `DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`; dupla: largura digitada = soma das folhas (÷2 ou ×2 em X) |
| `doors_windows.place_in_region` / `modal_in_region` | `region_props.region_wall`, `region_core.fit`, `REASONS`, `region_props.clear` | `others` = filhos da parede com marca de abertura, `(loc.x, loc.x + Dim X, loc.z, loc.z + Dim Z)`; recusa → WARNING "{motivo}: a inserção segue presa ao cursor"; aceito → caixa filha da parede em `(fit.x, 0, fit.sill)`, rotação zero, `Dim X/Y/Z` = largura, espessura, altura; confirmar (Enter, Enter do teclado numérico, clique) limpa a região; Esc/botão direito cancela e **mantém** a região |
| `walls2d/apply.py:apply_plan` | `sync.openings`, `sync.sync` | Re-sincroniza as caixas que já têm `assembly` (sem `try`), conta em `report['openings']` |
| `selection/element_size.py`, `selection/resize.py` | `sync.kind_of`, `_sync_opening` | Medida e Redimensionar pela folha (contrato em `_reversa_sdd/selection/`) |
| `ui/sidebar_build.py` | `sync.outdated`, `caffmob.openings_update`, `caffmob.wall_region`, `caffmob.wall_region_clear`, `btm_wall_region` | Aviso "{n} porta(s) ou janela(s) em caixa" + botão; caixa "Marcar região" com dica, ou região com "Região em {parede}: L × A" e campos Esquerda/Direita/Base/Topo editáveis |
| `hb_props.py:update_show_entry_door_and_window_cages` | `btm_opening_real.assembly` | Caixa com porta real: `WIRE`, sem `show_in_front`, `hide_set(not mostrar)` |
| `inspection/room_door_leaf.py:has_real_door` | `btm_opening_real.assembly` | Porta com porta real deixa de ser "porta de ambiente" (as folhas reais abrem pelo adaptador de agregado) |
| `aggregates/collision.py` | `OPENING_FRAME_PROP = 'btm_opening_frame'` | Peças com o nome do próprio marco saem do teste da folha |

## Fluxo Principal

1. 🟢 O usuário (opcional) marca uma região (`caffmob.wall_region`, F-07); o desenho F-08 a mostra.
2. 🟢 Ele escolhe porta ou janela; `doors_windows` cria a caixa com `btm_opening_real.kind`, e com região usa `fit` (F-02); confirma, corta a parede e chama `_sync_opening` → `sync.sync` (F-05), que gera as peças (F-01), materiais (F-03) e malhas (F-04).
3. 🟢 Mudanças de medida (diálogo, Redimensionar, Editor de Paredes) chamam `sync` de novo; a assinatura decide se refaz.
4. 🟢 Tecla I (F-06) e os botões de giro mudam o símbolo e chamam `sync`. Arquivos antigos passam por `caffmob.openings_update`.

### F-01 `door_parts(width, height, wall, hinge, side, double, open_door)` 🟢 (ver `_reversa_sdd/flowcharts/openings-door_parts.md`)
1. `b = _Builder()`.
2. `open_door` → `span = width` (sem folha). `double` → `span = 2·width + CENTER_GAP`; `_leaf(b, 0, width, height, 0, True, True)`; `_leaf(b, width + CENTER_GAP, width, height, 1, False, False)`. Simples → `span = width`; `_leaf(b, 0, width, height, 0, hinge == 'LEFT', True)`.
3. `_frame(b, span, height, wall, not open_door)`.
4. `flip = −1` se `side == 'POS_Y'`, senão `1`; cada peça vira `Part(..., center=(x + SIDE, wall/2 + y·flip, z), ...)` (tamanho, material, bevel, folha e `horizontal` preservados). A ordem das peças é a de criação.

### F-02 `fit(x0, x1, z0, z1, wall_length, wall_height, kind, others=())` 🟢 (ver `flowcharts/openings-region_fit.md`)
1. Ordena `x0 ≤ x1`, `z0 ≤ z1`. Se `−TOLERANCE < z0 < 0` → `z0 = 0`.
2. `x1 − x0 < MIN_SIZE` ou `z1 − z0 < MIN_SIZE` → `EMPTY`.
3. `x0 < −TOLERANCE` ou `x1 > wall_length + TOLERANCE` ou `z0 < 0` → `OUTSIDE`.
4. `z1 > wall_height + TOLERANCE` → `TOO_TALL`.
5. `sill = z0` se `kind == 'WINDOW'`, senão `0.0`.
6. Para cada `(ox0, ox1, oz0, oz1)`: `x0 < ox1 − MIN_SIZE and ox0 < x1 − MIN_SIZE and sill < oz1 − MIN_SIZE and oz0 < z1 − MIN_SIZE` → `OVERLAP`.
7. `Fit(True, x0, x1 − x0, z1 − sill, sill, '')` (sem prender `x0` a 0 nem `x1` ao comprimento: EC-09).

### F-03 `materials.get(key)` 🟢
1. Primeiro material de `bpy.data.materials` com `mat.get(TAG) == key` → devolve.
2. Senão `bpy.data.materials.new(nome)`; `mat[TAG] = key`; `diffuse_color = (*cor, extras.get('Alpha', 1.0))`; `metallic`, `roughness`.
3. Primeiro nó `BSDF_PRINCIPLED` de `mat.node_tree.nodes`: `Base Color = (*cor, 1)`, `Metallic`, `Roughness`, cada extra cujo socket existe (inclusive `Alpha` no vidro); `WOOD` → `_wood_textures`.
4. `GLASS` → `surface_render_method = 'BLENDED'`. Devolve o material.

### F-04 `build(parts, collection)` 🟢
1. Agrupa as peças por `group_key`, na ordem de primeira aparição.
2. Por grupo: `keys = sorted({materiais})`; `bm = bmesh.new()`; camada UV "UVMap"; `_add_part` com `slot = keys.index(material)`.
3. `_add_part`: BOX → `create_cube(size=1)` + `scale(vec=size)`; cilindro → `create_cone(cap_ends=True, segments=32, radius1=radius2=d/2, depth=h)` + `transform(_AXIS[shape])`; depois `translate(center)`. Para as faces ligadas aos vértices criados: `material_index = slot`, `smooth = shape != 'BOX'`; UV por laço com a normal da face `n`: `|n.y| > 0.5` → `(a, b) = (z, x)` se `horizontal`, senão `(x, z)`; `|n.x| > 0.5` → `(y, z)`; senão `(x, y)`; `uv = (a/0.45 + off, b/2.3 + 0.3·off)`, `off = (Σ ord(c) do nome mod 97)/97`.
4. `mesh = bpy.data.meshes.new(group_name)`, `bm.to_mesh`, `bm.free`; materiais anexados na ordem de `keys`; `obj = bpy.data.objects.new(group_name, mesh)`; `collection.objects.link(obj)`.
5. Se alguma peça tem `bevel` truthy: modificador "Chanfro" (`BEVEL`, `width = BEVEL` 0,001, `segments = 2`, `limit_method = 'ANGLE'`) e "Normais ponderadas" (`WEIGHTED_NORMAL`, `keep_sharp = True`). O valor de `bevel` de cada peça não é usado além disso (EC-12).

### F-05 `sync(context, cage, force=False)` 🟢 (ver `flowcharts/openings.md` §1)
1. `not is_opening(cage)` → `False`.
2. `sig = signature(cage)`; sem `force`, `data.signature == sig` e `data.assembly` vivo em `bpy.data.objects` → `False`.
3. `kind = kind_of(cage)`; `opens, production = _remember(data.assembly)`; `clear(cage)`; `room_door_leaf.remove_leaves(cage)` (pivôs e folhas cinzas da feature 005 e `btm_open`).
4. `collection` = primeira coleção da caixa ou `scene.collection`; `view_layer.update()`; `built = build.build(_parts(cage, kind), collection)`; cada objeto renomeado "`<caixa sem sufixo .NNN>` `<nome do grupo>`"; `_to_world`; `view_layer.update()`.
5. `frame_objs` = objetos de chave `FRAME`/`FRAME_HW`; `frame = group.create_group(frame_objs, 'FRAME', "<caixa> - montagem")`; cada malha recebe `obj[OPENING_FRAME_PROP] = frame.name`; `_align(frame, cage)`; `_parent_keep(frame, cage)`; `view_layer.update()`.
6. Para cada índice de folha (ordenado): `sash = group.create_group([malha Folha], 'LEAF', "<caixa> - folha {i+1}")`; a malha de ferragens da folha, se houver, vira filha da **malha** da folha (`_parent_keep`); `_align(sash, cage)`; `_parent_keep(sash, frame)`. `view_layer.update()`. (No passo 7, `make_leaf` insere o pivô entre o FRAME e o grupo LEAF.)
7. Para cada folha: janela → `travel = window_core.travel(DimX)`; `leaf.make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X' se i == 0 senão 'NEG_X', travel=travel)`; `apply._write(sash, 'travel', travel)`. Porta → `leaf.make_leaf(sash, frame, 'SWING', hinge=RN-12, swing_sign='OUT' se Swing Inside ou None senão 'IN', max_angle=90.0)`. Nome-base em `opens` com valor > 0 → `sash.btm_aggregate.open_value = valor` (atribuição direta, dispara o `update` do agregado); em `production` → `production_part = True`.
8. `data.kind = kind`, `data.assembly = frame`, `data.signature = sig`, `data.model_version = MODEL_VERSION`; `_style_cage(context, cage)`; `True`.

F-05b `clear(cage)`: `assembly` nulo ou fora de `bpy.data.objects` → nada. Senão, para `children_recursive + [assembly]` ainda existentes: guarda a malha (se `MESH`), `bpy.data.objects.remove(obj, do_unlink=True)`, remove a malha se ficou com 0 usuários; `assembly = None`. Apaga também qualquer objeto do usuário que tenha sido posto como filho da montagem (EC-05). 🟢 (código) 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-26):** apagar só objetos criados pela montagem (marcados) e reparentar os demais para a caixa. Pendência de implementação: DT-05.

### F-06 `btm.door_invert_hand.execute` 🟢 (ver `flowcharts/openings.md` §2)
1. `door = door_of(ativo)`; `swing = GeoNodeObject(_swing(door)[0])`; `set_input('Is Left', not bool(get_input('Is Left')))`.
2. `sync.sync(context, door)` (sem `force`: a assinatura mudou).
3. Se `view_layer.objects.active is None` (o ativo era uma peça apagada): alvo = primeira `MESH` de `assembly.children_recursive` (na prática a malha do marco, 🟡) ou a caixa; `select_set(True)` e vira o ativo.
4. INFO "Giro da porta invertido"; `FINISHED`.

### F-07 `caffmob.wall_region` 🟢 (ver `flowcharts/openings.md` §3)
1. `invoke`: `init_placement`; `_live.clear()`; `region_props.clear` (a região anterior é descartada já aqui); `modal_handler_add`; cabeçalho "Clique no primeiro canto da região numa parede | Esc: cancelar"; `RUNNING_MODAL`.
2. `modal`, a cada evento: cursor `CROSSHAIR`; `MIDDLEMOUSE`, `WHEELUPMOUSE`, `WHEELDOWNMOUSE` → `PASS_THROUGH`; `RIGHTMOUSE`/`ESC` `PRESS` → `_end`, `CANCELLED`; `INBETWEEN_MOUSEMOVE` → `RUNNING_MODAL`; senão `update_snap(context, event)` (atualiza `self.region` e `self.mouse_pos`).
3. Sem canto `a`: `_wall_hit`; com `LEFTMOUSE PRESS` e parede: `side = 'BACK'` se `(parede.matrix_world⁻¹ @ ponto).y > Thickness/2`, senão `FRONT`; `corner = _local(parede, side, event.shift)`; se não nulo, `_live = {wall: nome, side, a: corner, b: corner}` e cabeçalho "Clique no canto oposto | Shift: grade de 1 mm | Esc: cancelar".
4. `_local`: interseção do raio com o plano da face (`ponto = matrix_world @ (0, y_face, 0)`, normal = eixo Y local normalizado; `intersect_line_plane`); `None` se paralelo; ponto local; `x`, `z` por `hb_snap.snap_value_to_grid(valor, scene.unit_settings, fine=shift)`; preso a `[0, Length]` e `[0, Height]`.
5. Com canto `a`: parede sumiu → `_end`, `CANCELLED`; `b = _local(...)` se não nulo; `LEFTMOUSE PRESS` → grava `btm_wall_region` (`wall`, `side`, `x0 = min`, `x1 = max`, `z0 = min`, `z1 = max`, `active = True`), `_end`, INFO "Região marcada: {L} × {A}. Escolha a porta ou a janela" (`units.unit_to_string`), `FINISHED`.
6. Demais eventos (inclusive teclado) → `_tag_redraw`, `RUNNING_MODAL` (consumidos).

### F-08 `draw_regions()` (POST_PIXEL) 🟢
1. `context = bpy.context`. Com `_live`: parede viva e `b` definido → `_draw_rect` da prévia; volta (a região gravada não é desenhada durante o modal).
2. Sem `_live`: `region_wall(context)` (pode gravar `active = False`, EC-10); com região → `_draw_rect`.
3. `_draw_rect`: sai sem `region`/`region_data`; projeta os 4 cantos (`location_3d_to_region_2d`), sai se algum é `None` (atrás da câmera); `gpu.shader.from_builtin('UNIFORM_COLOR')`, `blend_set('ALPHA')`, 2 triângulos com `FILL`, `line_width_set(2.0)`, 4 arestas `LINES` com `LINE`, volta a largura 1 e `blend_set('NONE')`; texto "{L} × {A}" (`unit_to_string`), `blf.size(0, 14 · ui_scale)`, branco, centrado na média dos 4 cantos.

## Fluxos Alternativos

- **Vão aberto**: sem símbolo → `OPEN_DOOR`, 1 malha (Marco) e nenhum grupo `LEAF`; `door_of` devolve `None` (tecla I não age). 🟢
- **Símbolo ausente numa porta com `kind` gravado**: `Is Left`/`Swing Inside` `None` → `hinge LEFT`, `side NEG_Y`, `swing_sign OUT`. 🟢
- **Falha durante a montagem**: `_sync_opening` imprime e devolve `False`; o estado parcial (montagem apagada, malhas criadas) fica como estiver; no Editor de Paredes e em "Atualizar" a exceção sobe ao operador (EC-11). 🟢 (código) / 🟡 (efeito)
- **Região recusada**: `place_in_region` avisa e devolve `False`; a inserção continua presa ao cursor e a região continua marcada. 🟢
- **Sem janela (modo fundo)**: sem `keyconfigs.addon` não há keymaps; o desenho e o modal não rodam; `fit` e `sync` funcionam (fumaças). 🟢
- **Texturas ausentes**: `WOOD` fica só com cor e Principled, sem bump. 🟢

## Máquinas de Estado

### Caixa de porta/janela 🟢

| Estado | Condição | Transição |
|---|---|---|
| Antiga | `kind == 'NONE'` e `assembly is None` (arquivo anterior à 010) | `caffmob.openings_update` → Montada |
| Sem montagem | `kind ≠ 'NONE'` e `assembly is None` (montagem apagada ou falhou) | `sync` (inserção, diálogo, `openings_update`); o Editor de Paredes **não** a refaz (exige `assembly`) |
| Montada | `assembly` vivo, `signature` = atual | Mudança de `Dim X/Y/Z`, `Is Left`, `Swing Inside`, `kind` ou `MODEL_VERSION` + `sync` → Refazendo |
| Desatualizada | `model_version < MODEL_VERSION` | `caffmob.openings_update` (força) → Montada |
| Refazendo | dentro de `sync` | Grava `signature`/`model_version` → Montada |

### Região na parede 🟢

| Estado | Entrada | Saída |
|---|---|---|
| Nenhuma | `active = False` | `caffmob.wall_region` → Marcando |
| Marcando (sem canto) | `_live` vazio, modal ativo | 1º clique numa parede → Marcando (1 canto); Esc/botão direito → Nenhuma |
| Marcando (1 canto) | `_live` com `a`, `b` | 2º clique → Marcada; Esc/botão direito ou parede apagada → Nenhuma |
| Marcada | `active = True` | Confirmar porta/janela na região, Limpar, Esc na vista 3D, `load_post`, novo `caffmob.wall_region` ou parede ausente → Nenhuma; cancelar a inserção → Marcada |

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `hb_types.GeoNodeObject` | `get_input`/`set_input` de `Is Left`, `Swing Inside`, `Is Double` no símbolo | 🟢 |
| `hb_types.GeoNodeCage`, `GeoNodeWall` | `Dim X/Y/Z` da caixa; `Length`, `Height`, `Thickness` da parede | 🟢 |
| `aggregates/group.create_group(objs, kind, name)` | Empty novo no centro em XY e no `z` mínimo da caixa envolvente das malhas, ligado às coleções da primeira malha, com `btm_group.is_group = True`, `kind` e membros; `None` sem malhas | 🟢 |
| `aggregates/leaf.make_leaf(obj, parent, motion, hinge, swing_sign, max_angle, slide_dir, travel)` | Converte o grupo em folha `LEAF`: grava o repouso, `open_value = 0` e cria um pivô (Empty "<folha>" + sufixo, filho do `parent`) que passa a ser o pai do grupo; na janela mede o curso livre (`measure_free_travel`), depois sobrescrito por `apply._write('travel')` | 🟢 |
| `aggregates/apply._write(obj, name, value)` | Grava `travel` sem disparar o `update` | 🟢 |
| `aggregates/collision.OPENING_FRAME_PROP` | `'btm_opening_frame'` | 🟢 |
| `inspection/room_door_leaf.remove_leaves(door)` | Apaga pivôs `btm_room_door_pivot` e folhas cinzas; `door.pop('btm_open')` | 🟢 |
| `hb_placement.PlacementMixin` | `init_placement` (`self.region`, `self.mouse_pos`), `update_snap(context, event)`; `draw_header_text`, `clear_header_text` (contrato em `_reversa_sdd/hb_placement/`) | 🟢 |
| `hb_snap.snap_value_to_grid(value, unit_settings, fine)` | Métrico 10 mm / 1 mm; imperial 1" / 1/16" | 🟢 |
| `units.unit_to_string(unit_settings, value)` (definida em `data/units.py`; `region.py` a importa pela reexportação `caffmob_draw/units.py` _(Revisão 2026-10-10: region.py:24; units.py:20)_) | Texto das medidas (unidade do BlenderToMob, vírgula decimal; imperial em pés ou polegadas a 1/16") | 🟢 |
| `data/i18n.py` | `tr`, `N_` | 🟢 |
| `ui/view_mode` | Registrado por este pacote: `Scene.btm_view_mode`, `btm_view_lines`, `btm_view_prev_color` e `load_post` próprio (contrato na unit `ui`) | 🟢 |
| PropertyGroups/idprops | `btm_aggregate` (`is_aggregate`, `kind`, `open_value`, `production_part`, `travel`), `scene.home_builder.show_entry_door_and_window_cages`, `IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `IS_2D_ANNOTATION`, `IS_WALL_BP` | 🟢 |
| Ativos | `assets/nogueira_cor.jpg`, `assets/nogueira_rugosidade.jpg` | 🟢 |
| API Blender | `bmesh.ops.create_cube/create_cone/scale/transform/translate`, `bpy.data.meshes/objects/materials/images`, `Scene.ray_cast`, `bpy_extras.view3d_utils`, `mathutils.geometry.intersect_line_plane`, `gpu`, `blf`, `SpaceView3D.draw_handler_add` | 🟢 |

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| A caixa do Home Builder continua sendo o furo; a porta real é montada **dentro** dela (corte, vão livre, recuos e símbolo 2D intocados) | `sync.py` docstring (010 RN-04, RF-05) | 🟢 |
| Medida da porta = folha; furo derivado (padrão brasileiro "porta de 80") | `door_core.py` docstring (010 RN-02) | 🟢 |
| Geradores puros, sem `bpy`, testados fora do Blender | docstrings; `tests/test_*_core.py` | 🟢 |
| Poucas malhas por papel em vez de 157 peças (D-08) | `build.py` docstring | 🟢 |
| Refazer só por assinatura; restaurar abertura e produção | `sync.py:signature/_remember` (010 D-10 a D-12) | 🟢 |
| Folhas como agregados `LEAF` do sistema 003/007 (giro e correr com colisão) | `sync.py:sync` → `leaf.make_leaf` | 🟢 |
| Atualização de arquivos antigos só sob comando | `ops.py` docstring (010 RN-04, D-16) | 🟢 |
| Região como estado de sessão no `WindowManager`, por nome de parede | `region_props.py` docstring (011 D-10) | 🟢 |
| Região medida no plano da face clicada (sem paralaxe) | `region.py` docstring | 🟢 |
| Um único desenho `POST_PIXEL` registrado no `register` (prévia e região) | `region.py` docstring | 🟢 |

## Estado Interno

- 🟢 Global de módulo: `region._live`, `region._draw_handle[0]`, `region._addon_keymaps`, `ops._addon_keymaps`.
- 🟢 Persistente (`.blend`): `Object.btm_opening_real` na caixa; `btm_opening_material` nos materiais; `btm_opening_frame` nas malhas do marco; os objetos montados; propriedades `btm_aggregate` das folhas.
- 🟢 Sessão: `WindowManager.btm_wall_region`.
- 🟢 Escritas na cena: objetos, malhas, materiais e imagens novos; remoção da montagem anterior; `display_type`, `show_in_front`, `hide_set` da caixa e `hide_viewport` dos textos; `Is Left` do símbolo (tecla I); seleção e ativo (tecla I).

## Observabilidade

- 🟢 Nenhum log próprio. Relatórios `INFO` em "Atualizar", tecla I e marcação; o consumidor `_sync_opening` imprime falhas no console; `place_in_region` reporta `WARNING` com o motivo da recusa. Cabeçalho da área durante a marcação.

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-22):** com `side = BACK`, a inserção grava `Swing Inside` = falso (ou gira 180°). 🟢 (código) hoje o lado é ignorado (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-23):** `_swing` exige `has_input('Swing Inside')`. 🟢 (código) hoje o primeiro filho `IS_2D_ANNOTATION` é tratado como símbolo (EC-02). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-24):** simples ↔ dupla atualiza `kind` e refaz a porta real. 🟢 (código) hoje não refaz (EC-04). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-25):** sem escrita em `WindowManager` no desenho; invalidação em operadores ou `depsgraph_update_post`. 🟢 (código) hoje escreve dentro do desenho (EC-10). Pendência de implementação: DT-04.
- 🟢 _(Revisão 2026-10-10: sync.py:90-92, 160, 192)_ `_remember` e a restauração usam o nome-base antes do primeiro "."; caixas cujo nome tem ponto (ex.: "Porta 0.80") geram nomes cortados, sem perder a correspondência (EC-06).
- 🟢 `_to_world` aplica também a escala da caixa às malhas; caixas com escala ≠ 1 deformariam a porta _(Revisão 2026-10-10: sync.py:111 usa `cage.matrix_world` inteira)_; 🟡 o fluxo normal mantém escala 1 (inferido).
- 🟡 As normais das faces dos cilindros girados não são recalculadas antes da UV (`bmesh.ops.transform` não atualiza `face.normal`); afeta só a UV das ferragens.

## Divergências entre artefatos e código

- 🟢 `_reversa_forward/011…/requirements.md` RN-11 diz que "a abertura segue o lado da parede onde a região foi marcada"; o código guarda `side` só para o desenho e `place_in_region` usa `y = 0`, rotação zero.
- 🟢 `_reversa_forward/011…/roadmap.md` D-10 nomeia `btm.wall_region`, com `UNDO` na confirmação e desenho `POST_VIEW`; o código usa `caffmob.wall_region`, `bl_options = {'REGISTER'}` (sem undo) e `POST_PIXEL`.
- 🟢 `domain.md` RN-OPENINGS-02 cita `door_core.py:236-255`, mas o arquivo tem 192 linhas (as regras estão em `door_core.py:18-25` e `_leaf`/`_frame`, l. 87-170).
- 🟢 `code-analysis.md` §9.5 e a docstring de `build.py` dizem "cerca de 5 a 6 objetos por porta"; o código gera, por porta simples, 4 malhas + 3 Empties (grupo FRAME, grupo LEAF e o pivô criado por `leaf.make_leaf`); na dupla 6 malhas + 5 Empties; na janela 3 malhas + 5 Empties.
- 🟢 `code-analysis.md` §9.3 e `flowcharts/openings-region_fit.md` não registram que `x0` entre −5 mm e 0 e `x1`/`z1` até 5 mm além da parede são **aceitos sem prender** (EC-09).
- 🟢 `code-analysis.md` §9.7 e `flowcharts/openings.md` §3 não registram que `invoke` de `caffmob.wall_region` apaga a região anterior antes da nova marcação, nem que a região é invalidada dentro do desenho.
- 🟢 `state-machines.md`, `permissions.md`, `c4-components.md` e `architecture.md` não descrevem a unit: falam da camada `btm_opening`/`BTM_OT_InsertOpening` (`operators/opening_builder.py`, outra unit). As máquinas de estado acima são novas. `data-dictionary.md` §8 e `erd-complete.md` estão alinhados com o código.
