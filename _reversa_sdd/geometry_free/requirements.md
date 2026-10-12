# Geometria livre: placa e caixa (geometry_free) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/geometry_free/` (5 arquivos, 458 linhas) em 2026-10-10; a pasta não tem alterações sem commit (último commit que a tocou: `53f594c`). Não existe cópia espelhada na raiz do repositório. Confirmação de código não implica validação no Blender: nada foi executado no Blender nesta extração; as funções puras `size`/`sheets` foram sondadas por extração AST (sem `bpy`). 🟡 identifica prioridade ou intenção inferida; 🔴 identifica lacuna de validação.

## Visão Geral

🟢 Peças avulsas do projeto que não pertencem a nenhum módulo: uma **placa** (uma chapa) ou uma **caixa** (sólido fechado que, na fabricação, vira seis chapas). São objetos de malha comuns marcados com `btm_plane.object_kind = 'GEOMETRY'`, com as medidas em `Object.btm_geometry`; qualquer mudança de forma ou medida refaz a malha inteira (`props.py` docstring; `mesh.py:update`).

🟢 A criação é um modal na viewport (`caffmob.geometry_create`): clique no canto, arraste a largura × profundidade no plano horizontal do canto e, na caixa, a altura; em cada passo a medida pode ser digitada (`ops_create.py` docstring). A edição posterior acontece na janela de propriedades (grupo "Geometria", `ui/object_properties.py:_draw_geometry`), e três operadores fazem duplicar, espelhar e excluir (`ops_edit.py`).

🟢 Marcada como **peça de fabricação**, a geometria entra na lista de peças, no plano de corte e no JSON global com origem `FREE_GEOMETRY` e sem módulo (`cutting/part_sources.py:geometry_records`). Sem a marca, é só visual (`props.py:BTM_PG_GeometryProps.fabrication`).

## Responsabilidades

- 🟢 Declarar e registrar `BTM_PG_GeometryProps` e o ponteiro `bpy.types.Object.btm_geometry`, com callback que refaz a malha (`props.py`).
- 🟢 Calcular as medidas XYZ da peça por forma e posição da placa (`mesh.py:size`) e decompô-la em chapas de produção (`mesh.py:sheets`), em Python puro.
- 🟢 Construir a malha (cubo de 8 vértices com origem no canto mínimo) por BMesh, criar o objeto marcado e reconhecê-lo (`mesh.py:update/create_object/is_geometry`).
- 🟢 Criar por pontos de referência com encaixe (`hb_snap`), entrada numérica e cancelamento limpo (`ops_create.py:BTM_OT_GeometryCreate`).
- 🟢 Duplicar, espelhar e excluir com desfazer (`ops_edit.py`).
- 🟢 **Não** pertence a esta unit (consumidores, citados por contrato): o painel de propriedades (`ui/object_properties.py:_draw_geometry`), os botões "Placa"/"Caixa" (`ui/sidebar_build.py:121-122`, `ui/panels.py:260-261`), o adaptador de produção `cutting/part_sources.py:geometry_records` (lê `mesh.is_geometry`/`mesh.sheets`), a classificação `GEOMETRY` (`selection/classify.py:classify`, unit `selection`), o Redimensionar (`selection/resize.py:_set_width`), o realce do plano de inserção (`overlays/draw_handlers.py:184`) e o uso de `btm_geometry` pelos agregados como peça de produção (`aggregates/production.py`, `aggregates/panels.py`; unit `aggregates`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Uma geometria é um objeto `MESH` com `btm_plane.object_kind == 'GEOMETRY'` e grupo `btm_geometry`. A idprop `IS_BTM_GEOMETRY = True`, gravada na criação, **não é lida** por nenhum código do pacote (grep) | `mesh.py:is_geometry/create_object/GEOMETRY_FLAG` |
| RN-02 | 🟢 Medidas XYZ: `CAIXA` → `(width, depth, height)`. `PLACA` troca o eixo da espessura por `thickness`: `XY` (deitada) → `(width, depth, thickness)`; `XZ` (em pé, de frente) → `(width, thickness, height)`; qualquer outro valor (`YZ`, em pé de lado) → `(thickness, depth, height)`. A medida trocada continua guardada mas não aparece | `mesh.py:size` |
| RN-03 | 🟢 A malha é um cubo de 8 vértices de `bmesh.ops.create_cube(size=1)` transladado de +0,5 e escalado por `size()`: origem no canto mínimo, a peça cresce em +X, +Y e +Z. Mudar a espessura não move a face de apoio (z = 0 na placa deitada, y = 0 na de frente, x = 0 na de lado) | `mesh.py:update`; `props.py` docstring |
| RN-04 | 🟢 Mudar `kind`, `plane`, `width`, `depth`, `height` ou `thickness` refaz a malha na hora (`update=_update`); `fabrication`, `component`, `material` e `finish` não têm callback e não tocam a malha. Edições manuais de vértices se perdem na próxima mudança | `props.py:_update/BTM_PG_GeometryProps` |
| RN-05 | 🟢 O callback `_update` refaz a malha de **qualquer** objeto `MESH` dono do grupo (`self.id_data`), sem verificar `is_geometry` | `props.py:_update` |
| RN-06 | 🟢 Medidas: `FloatProperty` `subtype='DISTANCE'`, `unit='LENGTH'`, `min=0,001`, `max=10,0` m, `precision=1`; padrões largura 0,6, profundidade 0,4, altura 0,4, espessura 0,018 m. Forma padrão `PLACA`, posição `XY`, fabricação `False`, componente `ESP`, matéria-prima `"MDF"`, acabamento `""` | `props.py:_length/LIMIT_MIN/LIMIT_MAX/BTM_PG_GeometryProps` |
| RN-07 | 🟢 Criação em passos: 0 = canto (segue o cursor por `hb_snap`); 1 = largura × profundidade no plano horizontal `z = canto.z`; 2 (só `CAIXA`) = altura. Clique esquerdo avança; a placa termina no fim do passo 1, a caixa no fim do passo 2. A placa nasce sempre deitada (`plane = 'XY'`, padrão) | `ops_create.py:_advance/_move` |
| RN-08 | 🟢 O objeto existe desde o `invoke` (pré-visualização = o próprio objeto), marcado com `HB_CURRENT_DRAW_OBJ` para o raycast de `hb_snap` ignorá-lo; nasce com largura e profundidade 0,01 m (e altura 0,01 m na caixa) | `ops_create.py:invoke/DRAW_FLAG`; `hb_snap.py:best_hit` |
| RN-09 | 🟢 Passo 1 por mouse: `largura = max(0,001, |dx|)` (ou a largura digitada), `profundidade = max(0,001, |dy|)`; se o arraste vai para −X ou −Y, a origem recua a medida correspondente, de modo que o canto clicado continua sendo um canto da peça | `ops_create.py:_update_footprint` |
| RN-10 | 🟢 Passo 2 por mouse: altura = `max(0,001, p.z − origem.z)`, com `p` = interseção do raio do cursor com o plano vertical pela origem da peça cuja normal é a componente horizontal do raio de visão; com a vista vertical (componente horizontal < 1e-6) o mouse não muda a altura | `ops_create.py:_update_height` |
| RN-11 | 🟢 Entrada numérica: só os caracteres `0123456789,.` (com `PRESS`) entram no buffer; Backspace apaga o último; Enter/Enter do teclado numérico só age com buffer não vazio e passo > 0. O texto é lido por `units.parse_length(texto, unidade_da_cena, allow_zero=False)`. Ordem: 1º Enter no passo 1 fixa a **largura** (o mouse passa a mexer só na profundidade); 2º Enter fixa a **profundidade** e avança; no passo 2, Enter fixa a **altura** e conclui. Valor inválido → `report({'WARNING'}, mensagem)` e o buffer é limpo, sem avançar | `ops_create.py:modal/_typed_value` |
| RN-12 | 🟢 Concluir: limpa o texto do cabeçalho, apaga `HB_CURRENT_DRAW_OBJ`, tira a seleção dos objetos selecionados, seleciona e ativa a peça, `FINISHED`. Esc ou botão direito (`PRESS`) em qualquer passo: limpa o cabeçalho, remove o objeto e a malha (se ficou sem usuários), `CANCELLED` | `ops_create.py:_finish/_cancel` |
| RN-13 | 🟢 Navegação passa adiante: botão do meio e rodas (`MIDDLEMOUSE`, `WHEELUPMOUSE`, `WHEELDOWNMOUSE`) retornam `PASS_THROUGH`. Ctrl durante o passo 0 encaixa em vértices e arestas da face atingida (raio de 50 px) ou nos cantos da grade; sem objeto sob o cursor, o canto cai na grade do piso `z = 0` ou no plano de inserção ativo; em vista lateral ortográfica, no plano pela origem do mundo perpendicular ao raio de visão _(Revisão 2026-10-10: `hb_snap.py:snap_to_grid`, ramo `is_orthographic_side_view` → `norm = view_vector`)_ | `hb_snap.py:event_is_pass_through/main/snap_to_grid` |
| RN-14 | 🟢 Chapas (metros): `PLACA` → `[("Placa", a, b, c)]` com `a ≥ b ≥ c` = medidas de `size()` ordenadas (a espessura exportada é a **menor** medida, mesmo que não seja `thickness`). `CAIXA` com `t = thickness`, `hi = max(0,001, height − 2t)`, `wi = max(0,001, width − 2t)` → Fundo e Tampo `(width, depth, t)`; Lateral esquerda e direita `(hi, depth, t)`; Frente e Trás `(wi, hi, t)`, nessa ordem. A caixa não ordena as medidas. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-66):** na placa, exportar sempre `thickness` como espessura (as outras duas medidas como comprimento × largura) e avisar quando alguma for menor que `thickness`; na caixa, avisar quando 2t ≥ largura ou altura. Pendência de implementação: DT-03, DT-04 | `mesh.py:sheets` |
| RN-15 | 🟢 Produção (consumidor): só geometria com `is_geometry`, `fabrication = True` e visível (`not hide_viewport and not hide_get()`). Cada chapa vira `PartRecord(uid=f"{btm_uid}/{component}/{índice}", module_uid=None, module_name=nome do objeto, line="", name=<nome da chapa na caixa, nome do objeto na placa>, component, length/width/thickness em mm, finish, source="FREE_GEOMETRY", material)`. `btm_uid` é criado na primeira extração (`ensure_module_uid`, 12 hex). Medidas vêm das propriedades: a escala do objeto não entra. A mesma função também emite como `FREE_GEOMETRY` os agregados com `production_part` (uma placa com as medidas da caixa do agregado): o total `FREE_GEOMETRY` inclui esses agregados, e uma geometria livre convertida em agregado de produção sai duas vezes com o mesmo uid (aggregates EC-23) _(Revisão cruzada 2026-10-10: part_sources.py:294-306)_ | `cutting/part_sources.py:geometry_records/ensure_module_uid/_visible` |
| RN-16 | 🟢 Duplicar: `obj.copy()` com malha copiada, ligado a todas as coleções do original, com a mesma `matrix_world` e `location = matrix_world @ (size()[0], 0, 0)` (encostado no lado +X local); apaga `btm_uid` da cópia; a cópia fica selecionada e ativa, o original sai da seleção | `ops_edit.py:BTM_OT_GeometryDuplicate.execute` |
| RN-17 | 🟢 Espelhar não muda a malha nem a escala: desloca a peça de `matrix_world.to_3x3() @ (size()[0], 0, 0)` e alterna a idprop `btm_mirrored` — sem a marca, subtrai e grava `True`; com a marca, soma e apaga. A peça passa para o outro lado do ponto de origem anterior; o ponto de origem do objeto anda junto | `ops_edit.py:BTM_OT_GeometryMirror.execute` |
| RN-18 | 🟢 Excluir: `bpy.data.objects.remove(obj, do_unlink=True)` e remove a malha se ficou com 0 usuários; filhos não são removidos | `ops_edit.py:BTM_OT_GeometryDelete.execute` |
| RN-19 | 🟢 Disponibilidade: criar exige `context.area.type == 'VIEW_3D'` e modo `OBJECT`; duplicar/espelhar/excluir exigem modo `OBJECT` e objeto **ativo** que seja geometria (RN-01). Os quatro operadores têm `bl_options = {'REGISTER', 'UNDO'}` | `ops_create.py:poll`; `ops_edit.py:_GeometryAction` |

## Requisitos Funcionais

🟡 Prioridades inferidas da feature 002 (RF-11 Must, RF-12 Must, RF-14/RF-15 Should em `_reversa_forward/002-editor-parede-mover-sobre/requirements.md:169-172,455-456`) e dos consumidores; não constituem roadmap novo.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Criar placa por pontos (canto + largura × profundidade), com encaixe e medidas digitadas | Must | CA-01, CA-02, CA-03, CA-05 |
| RF-02 | 🟢 Criar caixa por pontos (canto + base + altura) | Must | CA-04, CA-06 |
| RF-03 | 🟢 Cancelar a criação sem deixar objeto nem malha | Must | CA-07 |
| RF-04 | 🟢 Editar forma, posição da placa e medidas com a malha atualizada na hora, sem mover a face de apoio | Must | CA-08, CA-09 |
| RF-05 | 🟢 Marcar como peça de fabricação com componente, matéria-prima e acabamento, gerando 1 (placa) ou 6 (caixa) chapas | Should | CA-10, CA-11, CA-12 |
| RF-06 | 🟢 Duplicar ao lado (+X local) com identidade de produção nova | Should | CA-13 |
| RF-07 | 🟢 Espelhar para o outro lado da origem e desfazer o espelho com um segundo clique | Should | CA-14 |
| RF-08 | 🟢 Excluir a geometria com desfazer | Should | CA-15 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desfazer | Os 4 operadores com `{'REGISTER', 'UNDO'}`; a criação vira um único passo de desfazer ao terminar o modal; edição pelo painel entra no desfazer de propriedade do Blender | `ops_create.py:BTM_OT_GeometryCreate.bl_options`; `ops_edit.py:_GeometryAction` | 🟢 (código) / 🟡 (comportamento do undo no Blender não verificado nesta extração) |
| Custo | Cada atribuição de medida refaz a malha (8 vértices): `invoke` faz 4 a 5 reconstruções; cada `MOUSEMOVE` do passo 1 faz 2 (largura e profundidade) | `ops_create.py:invoke/_update_footprint`; `props.py:_update` | 🟢 |
| Robustez | Sem método `cancel()`: se o modal for interrompido de fora (troca de arquivo, desregistro), o objeto provisório fica na cena com `HB_CURRENT_DRAW_OBJ` | `ops_create.py` (ausência) | 🟢 (código) / 🔴 (efeito no Blender) |
| Testabilidade | `size`/`sheets` são puras mas o módulo importa `bmesh`/`bpy` no topo (não importa fora do Blender); nenhum teste unitário da unit. Smoke Blender existente: `tests/blender_002_smoke.py:194-224` | `mesh.py:1-9`; `tests/` | 🟢 _(Revisão 2026-10-10: smoke executado no Blender 5.2.0 LTS, `blender_002_smoke: OK`, código 0)_ / 🔴 (sem teste puro) |
| Internacionalização | Textos do cabeçalho via `tr()` e catálogo `data/translations/geometry_free.json` (15 chaves); nomes de medidas marcados com `N_`; os rótulos `Forma`, `Posição da Placa`, `Peça de Fabricação`, `Componente`, `Matéria-prima`, `Acabamento` e os nomes de chapa (`Fundo`, `Tampo`…) não passam por `N_`/`tr` | `ops_create.py:_header`; `props.py`; `mesh.py:sheets` | 🟢 |
| Unidades | Internas em metros; produção em mm (`× 1000`); cabeçalho formatado na unidade da cena por `units.format_length` | `cutting/part_sources.py:geometry_records`; `ops_create.py:_header` | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual. CA-10 a CA-12 e CA-16 conferidos por sonda AST de `size`/`sheets`; CA-08, CA-11 (contagem 7), CA-13 a CA-15 correspondem a asserções de `tests/blender_002_smoke.py:194-224`. _(Revisão 2026-10-10: o smoke passou no Blender 5.2.0 LTS; sonda adicional confirmou CA-09 (dimensões (0,6, 0,018, 0,4) e (0,018, 0,4, 0,4), 8 vértices), CA-10, CA-13 (sem `btm_uid`, malha própria), CA-14 completo (x 0,0 com `btm_mirrored`, depois x 0,8 sem a idprop) e CA-16; CA-01 a CA-07 (modal) seguem sem teste)_

```gherkin
CA-01 — Placa por mouse (feliz)
Dado a viewport 3D em modo OBJECT e a unidade da cena em mm
Quando o usuário aciona "Placa", clica no piso em (1, 2, 0) e clica de novo em (1,6, 2,4, 0)
Então existe uma malha "Placa" com btm_plane.object_kind = 'GEOMETRY', btm_geometry.kind = 'PLACA', plane 'XY', width 0,6, depth 0,4, thickness 0,018, location (1, 2, 0), sem a idprop HB_CURRENT_DRAW_OBJ, selecionada e ativa, e o cabeçalho da área volta ao normal

CA-02 — Arraste para o lado negativo
Dado o canto clicado em (1, 2, 0)
Quando o cursor vai a (0,5, 1,7, 0) e o usuário clica
Então width 0,5, depth 0,3 e location (0,5, 1,7, 0): o canto clicado é o canto (+X, +Y) da peça

CA-03 — Medidas digitadas
Dado a placa no passo 1 e a unidade da cena em mm
Quando o usuário digita "600" Enter e depois "400" Enter
Então width 0,6 (o mouse passa a mexer só na profundidade), depth 0,4 e a placa é concluída

CA-04 — Caixa com altura digitada
Dado o operador com kind 'CAIXA' depois do canto e da base confirmados por clique
Quando o usuário digita "720" Enter
Então height 0,72 e a caixa é concluída (FINISHED)

CA-05 — Medida inválida (falha)
Dado o passo 1 com buffer vazio
Quando o usuário digita "0" Enter (ou "1,2,3" Enter)
Então aparece o aviso "Valor Inválido: a medida não pode ser zero." (ou "… não é um número válido."), o buffer é limpo, o passo não muda e nenhuma medida é alterada

CA-06 — Altura em vista de topo (falha suave)
Dado a caixa no passo 2 com a vista exatamente de cima
Quando o cursor se move
Então a altura não muda (componente horizontal do raio < 1e-6); digitar a altura e Enter ainda conclui

CA-07 — Cancelar (falha)
Dado a criação de placa em qualquer passo
Quando o usuário pressiona Esc ou o botão direito
Então o objeto e a malha "Placa" deixam de existir em bpy.data, o cabeçalho é limpo e o operador retorna CANCELLED

CA-08 — Espessura sem mover a face de apoio
Dado uma placa XY com width 0,8, depth 0,5, thickness 0,018
Quando thickness muda para 0,025
Então dimensions.z = 0,025 e o menor z dos vértices continua 0,0

CA-09 — Posição da placa
Dado uma placa 0,6 × 0,4 × 0,4 com espessura 0,018
Quando plane muda de 'XY' para 'XZ' e depois para 'YZ'
Então as dimensões da malha passam a (0,6, 0,018, 0,4) e depois (0,018, 0,4, 0,4)

CA-10 — Chapa da placa
Dado PLACA, plane 'XZ', 0,6 / 0,4 / 0,4 / 0,018
Quando sheets é calculado
Então devolve [("Placa", 0,6, 0,4, 0,018)]

CA-11 — Seis chapas da caixa
Dado CAIXA 0,6 × 0,5 × 0,7 com espessura 0,018 e fabrication True, visível
Quando a lista de peças é extraída
Então saem 6 PartRecord FREE_GEOMETRY sem module_uid: Fundo e Tampo 600 × 500 × 18, Laterais 664 × 500 × 18, Frente e Trás 564 × 664 × 18 (mm), uids "<btm_uid>/ESP/0" a "/5"; com uma placa marcada na mesma cena, o total FREE_GEOMETRY é 7

CA-12 — Geometria não fabricada ou oculta (falha)
Dado uma placa com fabrication False, e outra com fabrication True oculta na viewport
Quando a lista de peças é extraída
Então nenhuma das duas gera PartRecord

CA-13 — Duplicar
Dado uma placa XY de largura 0,8 na origem, sem parent
Quando caffmob.geometry_duplicate executa
Então a cópia ativa tem location.x = 0,8, malha própria, a mesma espessura e nenhuma idprop btm_uid

CA-14 — Espelhar e voltar
Dado a cópia do CA-13 em x = 0,8
Quando caffmob.geometry_mirror executa
Então location.x = 0,0 e btm_mirrored = True; executado de novo, location.x = 0,8 e a idprop some

CA-15 — Excluir e desfazer
Dado uma geometria ativa
Quando caffmob.geometry_delete executa
Então o objeto sai de bpy.data.objects e a malha sem usuários é removida; Ctrl+Z devolve a peça com o mesmo material (🟡 não verificado)

CA-16 — Caixa com espessura maior que a metade (borda)
Dado CAIXA 0,03 × 0,5 × 0,03 com espessura 0,018
Quando sheets é calculado
Então Laterais (0,001, 0,5, 0,018) e Frente/Trás (0,001, 0,001, 0,018): o mínimo de 1 mm entra e nenhuma validação recusa a peça

CA-17 — Ações sem geometria ativa (falha)
Dado o objeto ativo é uma parede (ou o modo é EDIT)
Quando caffmob.geometry_duplicate, geometry_mirror ou geometry_delete é chamado (busca F3 ou script)
Então o poll é falso e nada muda (o painel "Geometria" nem é desenhado: só aparece para elementos GEOMETRY)
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-04 | Must | 🟡 Feature 002 RF-11/RF-12 (Must); botões na barra lateral principal e no Construtor |
| RF-05 | Should | 🟡 Feature 002 RF-14; caminho de produção compartilhado com agregados (`aggregates/production.py`) |
| RF-06, RF-07, RF-08 | Should | 🟡 Feature 002 RF-15; há alternativas nativas do Blender (Shift+D, Ctrl+M, X) |
| Digitar a espessura durante a criação | Won't (no código atual) | 🟢 O modal só aceita largura, profundidade e altura; a espessura vem do padrão 0,018 m (cenário da 002 citava "digita a espessura de 18 mm"). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-96):** aceito o comportamento atual como Won't: a espessura é editável no painel logo depois e material por face não entra na produção (só uma matéria-prima por peça); o registro correspondente na feature 002 fica para o ciclo forward (fora de `_reversa_sdd/`) |
| Material e acabamento por face | Won't (no código atual) | 🟢 Um único `material`/`finish` em texto; nenhum material do Blender é atribuído (002 RF-12 pedia "por face"). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-96):** aceito o comportamento atual como Won't: a espessura é editável no painel logo depois e material por face não entra na produção (só uma matéria-prima por peça); o registro correspondente na feature 002 fica para o ciclo forward (fora de `_reversa_sdd/`) |
| Placa em pé criada direto por pontos | Won't (no código atual) | 🟢 A placa nasce deitada; a posição muda depois no painel |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---|---|---|
| `caffmob_draw/geometry_free/__init__.py` | `_modules`, `register`, `unregister` | 🟢 |
| `caffmob_draw/geometry_free/props.py` | `KINDS`, `PLANES`, `COMPONENT_ITEMS`, `LIMIT_MIN`, `LIMIT_MAX`, `_update`, `_length`, `BTM_PG_GeometryProps`, `register`, `unregister` | 🟢 |
| `caffmob_draw/geometry_free/mesh.py` | `GEOMETRY_FLAG`, `size`, `sheets`, `_props`, `update`, `create_object`, `is_geometry` | 🟢 (`size`/`sheets` sondadas) |
| `caffmob_draw/geometry_free/ops_create.py` | `DRAW_FLAG`, `MIN_SIZE`, `BTM_OT_GeometryCreate` (`poll`, `invoke`, `_ray`, `_hit`, `_on_plane`, `_update_footprint`, `_update_height`, `modal`, `_move`, `_advance`, `_typed_value`, `_header`, `_finish`, `_cancel`), `register`, `unregister` | 🟢 |
| `caffmob_draw/geometry_free/ops_edit.py` | `_active_geometry`, `_GeometryAction`, `BTM_OT_GeometryDuplicate`, `BTM_OT_GeometryMirror`, `BTM_OT_GeometryDelete`, `register`, `unregister` | 🟢 |
| `caffmob_draw/cutting/part_sources.py` (consumidor) | `geometry_records`, `ensure_module_uid`, `_visible` | 🟢 |
| `caffmob_draw/ui/object_properties.py` (consumidor) | `_draw_geometry` | 🟢 |
| `caffmob_draw/ui/sidebar_build.py`, `ui/panels.py` (consumidores) | botões `caffmob.geometry_create` com `kind` | 🟢 |
| `caffmob_draw/selection/classify.py`, `resize.py`, `element_size.py`, `editing.py` (consumidores) | `GEOMETRY`, `_set_width`, `size`, `get_dimension` | 🟢 |
| `caffmob_draw/hb_snap.py` (dependência) | `main`, `best_hit`, `snap_to_grid`, `event_is_pass_through`, `RADIUS = 50`, `STEPS = 6` | 🟢 |
