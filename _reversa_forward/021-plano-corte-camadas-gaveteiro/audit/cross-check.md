# Cross-Check Audit: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24` (rodada 3 — reconciliação; a rodada 2 é a segunda passada com olhos frescos)
> Artefatos analisados:
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/requirements.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/actions.md`
>
> Verificação adicional pedida pelo titular: conferência de código (arquivo:linha), execução real do E2E da 021
> no Blender 5.2.0 LTS e placar da suíte. A rodada 2 não alterou os três artefatos; a **rodada 3 corrigiu
> `roadmap.md` §10 e `actions.md` T021/T022** e retratou A001 e A002 com evidência — ver §Rodada 3.

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 1 |

**Situação depois da rodada 3:** nenhum achado aberto. A001 e A002 foram **retratados com evidência** (o ponteiro
estava obsoleto por outro motivo; a frente do Mover Sobre foi entregue na feature 022); A003, A004 e A005 foram
**corrigidos nos documentos**; A006 foi **rotulado**. Ver §Rodada 3 — veredito e evidência.

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Estado do ciclo | `.reversa/active-requirements.json` aponta a feature **018** (`current-stage: to-do`) enquanto a 021 está concluída (32/32 ações `[X]`, `progress.jsonl` com 32 registros e validação verde). Qualquer `/reversa-coding`, `/reversa-audit` ou `/reversa-clarify` executado sem correção deste ponteiro trabalha na feature errada | `.reversa/active-requirements.json` |
| A002 | HIGH | Cobertura (pedido do titular, fora dos três artefatos) | **A frente do objeto no Mover Sobre continua não implementada.** O pedido registrado em 2026-11-22 (achados A001–A008) e reaberto como A009 na auditoria da 017 segue aberto: as vistas são fixas em `front=(X,Z)` / `plan=(X,Y)`, a parede atrás de B não é consultada, não existe pergunta ao usuário e não existe propriedade de frente | `caffmob_draw/move_over/ops_dialog.py:43`; `caffmob_draw/move_over/scene.py`; `caffmob_draw/move_over/props.py` |
| A003 | MEDIUM | Consistência | `roadmap.md §10 Critério de pronto` está com **todos os itens `[ ]`** (inclusive "todas as ações marcadas `[X]`" e "testes puros passando"), enquanto `actions.md` tem 32/32 `[X]` e a validação está verde. O documento se contradiz sobre o próprio estado | `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md` §10 |
| A004 | MEDIUM | Consistência | `actions.md` lista como alvo de T021 `caffmob_draw/ui/panels.py` e de T022 `caffmob_draw/texture_library/ops_apply.py`, mas a implementação ficou em `caffmob_draw/cutting/ops_opcut.py` e `caffmob_draw/texture_library/ops_sync_missing.py` (registrado em `progress.jsonl`). A rodada anterior classificou como LOW; segue sem correção no artefato e induz quem for retomar a feature a procurar no arquivo errado | `actions.md` T021/T022 |
| A005 | MEDIUM | Rastreabilidade | `2026-11-24-suite-completa.md` afirma que os cinco defeitos (#156–#160) foram "todos fechados com `DONE.md`", mas `_reversa_bugs/plugin-caffmob-draw/bugs/` contém apenas `BUG-20261124-7K2M` (#156). Os cartões `3Q9X` (#157), `8W4D` (#158), `5N6R` (#159) e `2C8T` (#160) não existem no repositório | `_reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-suite-completa.md` × `_reversa_bugs/plugin-caffmob-draw/bugs/` |
| A006 | LOW | Terminologia | O relatório da suíte usa duas linhas de base sem rótulo único: a primeira passada (`Pura 156/30`) e a medição inicial no Windows (`pura 181/186`). Lido fora de contexto, o "30" parece um placar atual | `2026-11-24-suite-completa.md` §Resultado da primeira passada × §Segunda passada |

## Impacto e direção (HIGH)

### A001 — o estado do Reversa aponta para a 018, não para a 021

**Impacto:** o ponteiro é a porta de entrada de todos os skills forward. Com ele em 018 (`to-do`), um
`/reversa-coding` marcaria ações da 018 e um `/reversa-audit` auditaria a 018 — inclusive quando o pedido do titular
é sobre a 021. É também o que explica a fila `019`/`020` aparecer como "próximas" enquanto a 021 já está entregue.

**Direção:** o titular (ou `/reversa-requirements` de uma nova entrega) deve atualizar `feature-dir`, `feature-id`,
`current-stage` e `stages-completed`. Este skill não altera o arquivo. Se a intenção for abrir a 019, ela ainda não
tem `roadmap.md` nem `actions.md` (só `requirements.md`), então o próximo passo real é `/reversa-plan` dela.

**Veredito da rodada 3 — corrigido, com a causa trocada.** O ponteiro estava errado, mas não pelo motivo escrito
acima: estar na 018 não era o problema — a 018 é de fato a primeira feature aberta na ordem do projeto, e é
normal que o ponteiro fique nela enquanto ela não é fechada. O problema real é que a **018 já está concluída**
(`actions.md` com 28 `[X]` e 0 `[ ]`, entrega em `81814b5b`/`60895236`, `progress.jsonl` completo) e o ponteiro
ainda diz `current-stage: to-do`. Estado corrigido em `.reversa/active-requirements.json` (e no espelho
`.reversa/queued-features.json`): ativa = **019** em `requirements` (único artefato que ela tem), fila = **020**.
Queda a decisão do titular sobre abrir a 019 (`/reversa-plan`) — a 019 continua sem `roadmap.md`/`actions.md`.

### A002 — a frente do objeto no Mover Sobre nunca foi implementada

**Reprodução (código):** `ops_dialog.VIEWS = {'front': ('FRONT', 0, 2), 'plan': ('PLAN', 0, 1)}`
(`ops_dialog.py:43`) — a vista frontal é sempre XZ local e a planta XY local. `move_over/scene.py` monta
`b_frame = _frame(b)` e nunca varre paredes atrás de B; `move_over/props.py` não tem campo de frente e
`btm_front_yaw` só aparece em documentação (`_reversa_sdd/audit/mover-sobre-frente-2026-11-22.md`,
`_reversa_sdd/questions.md:1501`, `_reversa_forward/017-construtor-armario-v2/requirements.md:420`).

**Impacto:** em objeto importado (SketchUp/FBX/grupo solto), parede desenhada no sentido inverso ou módulo com malha
fora da convenção −Y, a janela mostra a lateral como frente e `_target_matrix` **gira A na base errada** — o erro não
é só de desenho, é de posição final.

**Direção:** é uma feature nova, fora do escopo da 021. Decisão de produto já registrada na 017 (idprop
`btm_front_yaw`, válida para todo o add-on) e proposta técnica na auditoria de 2026-11-22 §5. **Via:** uma nova
feature forward (`/reversa-requirements` → `/reversa-clarify`), porque há parâmetros abertos (raio de "perto",
tolerância de desacordo, forma da pergunta).

**Veredito da rodada 3 — retratado: a frente foi entregue na feature 022.** O caminho indicado acima foi cumprido:
`/reversa-requirements` → `/reversa-clarify` (D1–D5 respondidas) → `/reversa-plan` → `/reversa-to-do` → auditoria →
`/reversa-coding`, commits `3cfd5422` e `1d520b88`. Evidência no código de hoje: `move_over/frente_core.py`
(`decide`, `decide_for_wall`, `face_of`, `DISAGREE_MAX = 45`), `move_over/ops_front.py`
(`caffmob.move_over_front`), `scene.MoveOver(..., from_drag)` compondo `b_frame @ Rz(yaw)`, botão
"Frente do objeto" e indicador na planta. Provas: `tests/test_move_over_frente_core.py` 17/17 e
`tests/blender_022_mover_sobre_frente.py` 10/10 (PASS). O que **não** está coberto, registrado no cross-check da
022 como A001/A002: o prompt de frente não dispara no caminho de arraste direto (só no operador) e a meta de
desempenho não tem medição própria. Nada disso reabre a lacuna original (a parede atrás de B é consultada e a
frente é decidível/ajustável).

## Respostas ao titular (verificação extra)

| Pergunta | Veredito | Evidência |
|----------|----------|-----------|
| Os ~30 erros de quando a 021 foi implementada estão todos corrigidos? | **Sim.** A primeira passada registrava **pura 156/30**; 29 dos 30 vinham do mesmo defeito (`NotRequired` só existe no Python 3.11, import quebrando 29 ensaios) e o restante dos cartões #157–#160 | `2026-11-24-suite-completa.md` §Resultado da primeira passada; placar final **pura 186/186**, Blender 198/203 (5 ambiente, 0 defeito, 0 performance) |
| O Editor de armário pode ser aberto e tem a aparência e as funções do mockup? | **Sim, com uma limitação declarada.** `caffmob.cabinet_editor` abre o construtor e cria a raiz vazia num projeto limpo (`armario_v2/ops.py:336-370`); o painel `BTM_PT_ArmarioV2` (View3D → CAFFMob Draw) repete as 7 abas do mockup (`Estrutura`, `Divisões`, `Gavetas`, `Internos`, `Portas`, `Deslizantes`, `Fundos`), o badge de chapa, a barra `Montar Caixa`/`Limpar`, o subcabeçalho de dimensões e o rodapé `Gerar`/`Aplicar`/`Cancelar`. **Não é idêntico**: a área de desenho do mockup (frontal, planta, HUD e inspetor) é a própria Viewport 3D no Blender — decisão registrada na 017 (RN-22/D-05) | `armario_v2/props.py:35-43`, `armario_v2/panel.py:169-200,385-404`; E2E 50/50 |
| O botão geral de colisão do viewport está corrigido? | **Sim.** `caffmob.toggle_global_collision` alterna `collision_global` **e** `block_penetration` (o guarda lê o segundo desde a 066), o header desenha o rótulo `Colisão: ON/OFF` e o `unregister` remove o append | Execução real nesta rodada: `tests/blender_021_mcp_e2e.py` → `{"pass": 50, "fail": 0}`, exit 0, com os avisos "Colisões ativadas"/"Colisões desativadas" |
| É possível criar um armário do zero, rápido e fácil? | **Sim.** Abrir o construtor sem armário na cena cria a raiz; `Montar Caixa` liga laterais, bases e fundo e gera num passo; as abas inserem divisórias, prateleiras, matriz, bloco de gavetas e internos | `armario_v2/ops.py:336-370,450-610`; `panel.py` (janela vazia com Montar Caixa) |
| É possível redimensionar um armário sem perder ou deformar peças? | **Hoje: por elemento, não o armário inteiro.** O `Redimensionar` do menu muda a largura do pai e estica os agregados na proporção (o defeito #160, que pulava a adaptação, foi corrigido). Redimensionar **o armário como conjunto** é a feature **019**, que tem só `requirements.md` — não está implementada | `ui/ops_resize.py`, `selection/resize.py:1-45`; `_reversa_forward/019-redimensionar-e-colisao/` |
| É possível editar todas as peças de dentro do armário pelo editor? | **Sim.** Abas `Divisões`, `Gavetas`, `Internos`, `Portas`, `Deslizantes`, `Fundos` editam campo a campo o que existe, e os operadores `Inserir divisória/prateleira/matriz`, `Criar bloco de gavetas` e `Inserir interno` gravam e regeram em um único `UNDO`; a seleção por componente (011) permite pegar a peça na vista | `armario_v2/panel.py:1-40,169-200`; `armario_v2/ops.py:490-610` |
| O menu Mover Sobre está corrigido conforme o histórico? | **Sim, desde a feature 022** (a linha desta tabela descrevia o estado antes dela; ver A002 e §Rodada 3) | `move_over/frente_core.py`, `move_over/ops_front.py`, `scene.MoveOver(..., from_drag)`; 17/17 + 10/10 |

## Itens verificados e aprovados

### Eixo 1 — Cobertura
- `RF-01` a `RF-14` têm decisão (`D-01`–`D-09`) e implementação rastreável: `cutting/module_list_core.py` +
  `cutting/ops_opcut.py`; `cutting/opcut_core.py` + `plan_render.py` + `plan_export.py`;
  `texture_library/sync_missing.py` + `ops_sync_missing.py`; `ui/header_collision.py`; `data/layers.py` +
  `operators/floor_builder.py` + `openings/sync.py`; `armario_v2/build.py`; `walls2d/ops_editor.py` +
  `ui/sidebar_build.py`; `stick/release_guard_core.py` + `link.py` + `magnet.py`;
  `library_panel/ops_cabinet.py` + `style.py`; `selection/lowered_wall_core.py` + `classify.py`;
  `armario_v2/drawer_detect_core.py` + `ops_drawer_convert.py`; `data/translations/feature_021.json`.
- Cenários Gherkin cobertos: 24 ensaios puros da 021 + E2E real **50/50** (camadas, piso `DOWN`/`UP`, OpCut com
  exportação HTML/SVG/PDF, gaveteiro com peças faltantes, parede rebaixada, colisão no header, texturas perdidas,
  desgrudar sem ciclo, `Criar Armário` → construtor v2, painel do construtor).

### Eixo 2 — Consistência
- Terminologia uniforme (`Arquitetura`, `Marcenaria`, `Gaveteiro`, `OpCut`, `collision_global`) nos três documentos.
- Todos os IDs citados (`RF-01`–`RF-14`, `RN-01`–`RN-12`, `D-01`–`D-09`, `T001`–`T032`) existem onde são definidos.
- Os dois contratos de `interfaces/` (`texture-sync-http.md`, `opcut-export-files.md`) estão na seção 7 do roadmap.

### Eixo 3 — Coerência com o legado
- Nenhuma decisão contraria regra 🟢 de `_reversa_sdd/domain.md`; os desvios (coleção `Marcenaria`, `e_raiz()`
  desacoplado do nome) estão registrados em `legacy-impact.md` e vigiados em `regression-watch.md`.
- Componentes citados existem em `_reversa_sdd/architecture.md` e no addenda da 017.

### Eixo 4 — Sanidade do actions
- Dependências apontam só para IDs existentes (`T001`–`T032`); grafo acíclico (maior cadeia 6).
- Nenhuma ação `[//]` compartilha arquivo alvo com outra da mesma fase.

## Execuções desta rodada

| Comando | Resultado |
|---------|-----------|
| `python _reversa_bugs/tools/reversa_debugger.py --suite pure --pure-timeout 45 --out _reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-audit` | **pura 186/186**, 0 falhas, 99,5 s, exit 0 (`2026-11-24-audit/report.md`) |
| `"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python tests/blender_021_mcp_e2e.py` | `{"pass": 50, "fail": 0}`, exit 0 |

## Rodada 3 — veredito e evidência (reconciliação 2026-11-24)

Pedido do titular: nenhum achado pode continuar "registrado mas não resolvido".

| ID | Severidade | Veredito | Evidência |
|----|------------|----------|-----------|
| A001 | HIGH | **Corrigido** — o ponteiro estava obsoleto, mas a causa escrita na rodada 2 estava errada | A 018 é a próxima feature aberta na ordem e está **concluída** (28 `[X]`, 0 `[ ]`; commits `81814b5b`/`60895236`). `.reversa/active-requirements.json` (e o espelho `queued-features.json`) agora aponta **019** em `requirements`, fila só com **020** |
| A002 | HIGH | **Retratado com evidência** — a frente do objeto foi entregue na feature 022 | `move_over/frente_core.py` (17/17 em `tests/test_move_over_frente_core.py`), `move_over/ops_front.py`, `scene.MoveOver(..., from_drag)`, 10/10 no `tests/blender_022_mover_sobre_frente.py`; commits `3cfd5422`/`1d520b88`. Pendências declaradas no cross-check da 022 (prompt só no operador; RNF sem medição) não reabrem a lacuna |
| A003 | MEDIUM | **Corrigido** — `roadmap.md` §10 marcado com a evidência de cada critério | 32/32 ações, 24 ensaios puros, `test_smoke_021` + E2E 50/50, i18n 3/3, `regression-watch.md` no diretório da feature |
| A004 | MEDIUM | **Corrigido** — alvos de T021/T022 alinhados ao que foi implementado | T021 → `cutting/ops_opcut.py` (+ `plan_render.py`, `plan_export.py`); T022 → `texture_library/ops_sync_missing.py` |
| A005 | MEDIUM | **Corrigido** — o relatório da suíte não afirma mais `DONE.md` para cartões que não existem | `2026-11-24-suite-completa.md` registra que só o #156 tem cartão (`BUG-20261124-7K2M`); #157–#160 foram corrigidos direto no código (commit `f2f35215`), sem cartão |
| A006 | LOW | **Rotulado** — as duas linhas de base têm nome e contexto | O relatório da suíte abre a seção Linux como "fotografia de antes" e a de Windows como "placar depois" |

### As 5 falhas da suíte Blender — causa concreta

A rodada 2 aceitou as cinco como "ambiente" porque o runner classifica por menção a `online_access`/MOBI/extensão.
Olhado o log de cada uma, **três não eram ambiente**: duas eram defeito real de produto e uma era ensaio
carregando o addon do jeito errado.

| Ensaio | O que o log dizia | Causa concreta | Situação |
|--------|-------------------|----------------|----------|
| `blender_065_cena_v2` | `AssertionError: Referência rica original: 14 objetos` (print com 13) | **Defeito real.** `_montar_pecas_abertura` passou `model=None` para `openings/window_core.window_parts` desde a 078; `None` não aciona o padrão do parâmetro e cai no ramo de janela **fixa**, gerando 2 peças (Marco, Folha 1) em vez de 3 (Marco, Folha 1, Folha 2). O ensaio de 159dbfc1 (worktree temporária) dava `abertura_peca: 3` e 14 objetos; hoje dava 2 e 13 | **Corrigido** em `window_parts` (`model = model or 'janela_correr_2f'`, `material = material or 'aluminio'`). Ensaio passa com a asserção original: 14 objetos, `abertura_peca: 3` |
| `blender_065_baixar_v2` | `AssertionError: Referência rica monta 17 objetos` (linha 137) | Mesma causa da linha acima (a montagem incremental conta as mesmas 17 entidades) | **Corrigido** pela mesma mudança; passa com `len(root.all_objects) == 17` |
| `blender_increment1_smoke` | `ValueError: The "package" does not name an extension` em `addon.load_file_post(None)` | **Ensaio desatualizado** (não é defeito do produto): carregava `caffmob_draw` como módulo solto. Além disso, o banco do Padrão de Dimensões é por `extension_path_user` e o ensaio deixava a cópia "Padrão Brasil - cópia" gravada, então a execução seguinte já começava com ela ativa | **Corrigido**: carga como `bl_ext.ensaio_increment1.caffmob_draw` (padrão dos ensaios 065) e banco em diretório temporário (`store.override_path`), fechado no fim. Roda duas vezes seguidas com `BLENDER_INCREMENT1_SMOKE_OK` e não deixa arquivo de banco |
| `blender_065_ida_e_volta` | `assert urlsplit(BASE).scheme == 'http' and urlsplit(BASE).hostname == '127.0.0.1'` | **Ambiente, de verdade.** Exige `CAFFMOB_BASE=http://127.0.0.1:<porta>` de um MOBI descartável, `T121_PREPARO` (JSON do ensaio web), `BLENDER_USER_RESOURCES` dentro da pasta de entrega e `--online-mode`; sem isso aborta antes de registrar o addon | **Bloqueado por recurso externo** — nada a corrigir sem o servidor de ensaio |
| `blender_ensaio_mobi` | `assert urlsplit(base).hostname == '127.0.0.1' and urlsplit(base).scheme == 'http'` | **Ambiente, de verdade.** Mesmo requisito (`CAFFMOB_BASE` em loopback + `--online-mode`) para o ensaio HTTP real da 063 | **Bloqueado por recurso externo** |

Nenhuma asserção foi afrouxada: as duas falhas de contagem voltaram a passar com os números originais (14 e 17), e a
fumaça continua exigindo `Padrão Brasil` de 15 mm, 24 peças, plano de 6 chapas e exportações.

### Execuções da reconciliação (depois das mudanças)

| Comando | Resultado |
|---------|-----------|
| `python _reversa_bugs/tools/reversa_debugger.py --suite pure --pure-timeout 45 --out .../2026-11-24-reconciliacao-2` | **pura 187/187**, 98,4 s, exit 0 (0 defeito) |
| `python _reversa_bugs/tools/reversa_debugger.py --suite blender --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --blender-timeout 360 --out .../2026-11-24-reconciliacao-blender-2` | **Blender 202/204**, 980,9 s, exit 0; 2 falhas, ambas **ambiente** (`065_ida_e_volta`, `ensaio_mobi` — MOBI em `127.0.0.1` + `--online-mode`) |
| `python docs/rag/tools/check_api.py` | 619 arquivos, `OK: no unknown API references found` |

Comparação com os números da rodada anterior: pura **187/187 → 187/187** (sem regressão) e Blender
**199/204 → 202/204** (três ensaios a mais passando, nenhum a menos).

## Próximo passo sugerido

A 021 está coberta e verde (0 CRITICAL) e, depois desta rodada, sem nenhum HIGH/MEDIUM em aberto. O ponteiro do
Reversa aponta para a **019** (`requirements`), a próxima feature aberta na ordem — o passo real é `/reversa-plan`
dela quando o titular quiser. A frente do Mover Sobre (A002) está entregue na 022.
