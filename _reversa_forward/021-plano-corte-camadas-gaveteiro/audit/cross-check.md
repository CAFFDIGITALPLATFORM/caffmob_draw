# Cross-Check Audit: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24` (rodada 2 — segunda passada, olhos frescos)
> Artefatos analisados:
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/requirements.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/actions.md`
>
> Verificação adicional pedida pelo titular: conferência de código (arquivo:linha), execução real do E2E da 021
> no Blender 5.2.0 LTS e placar da suíte. **Nenhum dos três artefatos foi alterado por esta rodada.**

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 1 |

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

## Respostas ao titular (verificação extra)

| Pergunta | Veredito | Evidência |
|----------|----------|-----------|
| Os ~30 erros de quando a 021 foi implementada estão todos corrigidos? | **Sim.** A primeira passada registrava **pura 156/30**; 29 dos 30 vinham do mesmo defeito (`NotRequired` só existe no Python 3.11, import quebrando 29 ensaios) e o restante dos cartões #157–#160 | `2026-11-24-suite-completa.md` §Resultado da primeira passada; placar final **pura 186/186**, Blender 198/203 (5 ambiente, 0 defeito, 0 performance) |
| O Editor de armário pode ser aberto e tem a aparência e as funções do mockup? | **Sim, com uma limitação declarada.** `caffmob.cabinet_editor` abre o construtor e cria a raiz vazia num projeto limpo (`armario_v2/ops.py:336-370`); o painel `BTM_PT_ArmarioV2` (View3D → CAFFMob Draw) repete as 7 abas do mockup (`Estrutura`, `Divisões`, `Gavetas`, `Internos`, `Portas`, `Deslizantes`, `Fundos`), o badge de chapa, a barra `Montar Caixa`/`Limpar`, o subcabeçalho de dimensões e o rodapé `Gerar`/`Aplicar`/`Cancelar`. **Não é idêntico**: a área de desenho do mockup (frontal, planta, HUD e inspetor) é a própria Viewport 3D no Blender — decisão registrada na 017 (RN-22/D-05) | `armario_v2/props.py:35-43`, `armario_v2/panel.py:169-200,385-404`; E2E 50/50 |
| O botão geral de colisão do viewport está corrigido? | **Sim.** `caffmob.toggle_global_collision` alterna `collision_global` **e** `block_penetration` (o guarda lê o segundo desde a 066), o header desenha o rótulo `Colisão: ON/OFF` e o `unregister` remove o append | Execução real nesta rodada: `tests/blender_021_mcp_e2e.py` → `{"pass": 50, "fail": 0}`, exit 0, com os avisos "Colisões ativadas"/"Colisões desativadas" |
| É possível criar um armário do zero, rápido e fácil? | **Sim.** Abrir o construtor sem armário na cena cria a raiz; `Montar Caixa` liga laterais, bases e fundo e gera num passo; as abas inserem divisórias, prateleiras, matriz, bloco de gavetas e internos | `armario_v2/ops.py:336-370,450-610`; `panel.py` (janela vazia com Montar Caixa) |
| É possível redimensionar um armário sem perder ou deformar peças? | **Hoje: por elemento, não o armário inteiro.** O `Redimensionar` do menu muda a largura do pai e estica os agregados na proporção (o defeito #160, que pulava a adaptação, foi corrigido). Redimensionar **o armário como conjunto** é a feature **019**, que tem só `requirements.md` — não está implementada | `ui/ops_resize.py`, `selection/resize.py:1-45`; `_reversa_forward/019-redimensionar-e-colisao/` |
| É possível editar todas as peças de dentro do armário pelo editor? | **Sim.** Abas `Divisões`, `Gavetas`, `Internos`, `Portas`, `Deslizantes`, `Fundos` editam campo a campo o que existe, e os operadores `Inserir divisória/prateleira/matriz`, `Criar bloco de gavetas` e `Inserir interno` gravam e regeram em um único `UNDO`; a seleção por componente (011) permite pegar a peça na vista | `armario_v2/panel.py:1-40,169-200`; `armario_v2/ops.py:490-610` |
| O menu Mover Sobre está corrigido conforme o histórico? | **Não** — ver A002 | `move_over/ops_dialog.py:43`; ausência de `move_over/frente*.py` e de `btm_front_yaw` no pacote |

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

## Próximo passo sugerido

A 021 está coberta e verde (0 CRITICAL). Os dois HIGH não são regressões da 021: A001 é estado do ciclo e A002 é uma
feature nova. Antes de seguir, o titular precisa decidir qual feature fica ativa e abrir a frente do objeto no Mover
Sobre numa entrega própria (`/reversa-requirements` → `/reversa-clarify`).
