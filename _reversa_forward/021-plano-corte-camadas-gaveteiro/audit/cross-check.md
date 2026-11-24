# Cross-Check Audit: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Artefatos analisados:
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/requirements.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md`
> - `_reversa_forward/021-plano-corte-camadas-gaveteiro/actions.md`
> Verificação adicional solicitada pelo titular: comparação visual de `caffmob_draw/armario_v2/panel.py` contra `mockup_construtor_armarios.html` e validação E2E ao vivo no Blender 5.2 via MCP (`127.0.0.1:9877`).

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 2 |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | LOW | Cobertura / Contrato | A rodada anterior registou o servidor na porta `9876`, mas `.blender-mcp/settings.md` (regra do projeto) aponta `9877`. Revalidado em 2026-11-24 com o servidor em `9877`: a porta do settings é a correta e a validação E2E passou nela. | `.blender-mcp/settings.md` |
| A002 | LOW | Consistência | Em `actions.md` (T021 e T022), os arquivos alvo listados inicialmente eram `caffmob_draw/ui/panels.py` e `caffmob_draw/texture_library/ops_apply.py`, mas a implementação isolou de forma mais limpa em módulos dedicados `caffmob_draw/cutting/ops_opcut.py` e `caffmob_draw/texture_library/ops_sync_missing.py` (registrado corretamente em `progress.jsonl` e `legacy-impact.md`). | `_reversa_forward/021-plano-corte-camadas-gaveteiro/actions.md` |

## Itens verificados e aprovados

### Eixo 1 — Cobertura
- Todos os 14 Requisitos Funcionais (`RF-01` a `RF-14`) possuem decisão técnica correspondente (`D-01` a `D-09`) em `roadmap.md`.
- Todas as 9 decisões técnicas (`D-01` a `D-09`) possuem ações concretas (`T001` a `T032`) em `actions.md`, todas concluídas (`[X]`).
- Todos os cenários Gherkin (casos felizes e negativos) estão cobertos por testes puros e validação ao vivo no Blender 5.2 via MCP.

### Eixo 2 — Consistência
- Terminologia uniforme (`Arquitetura`, `Marcenaria`, `Gaveteiro`, `Construtor de Armários v2`, `OpCut`, `collision_global`) nos três documentos.
- Todos os IDs citados (`RF-01`..`RF-14`, `RN-01`..`RN-12`, `D-01`..`D-09`, `T001`..`T032`) existem nas seções que os definem.
- Os 2 contratos em `interfaces/` (`texture-sync-http.md` e `opcut-export-files.md`) estão referenciados na seção 7 do `roadmap.md`.

### Eixo 3 — Coerência com o legado
- Nenhuma decisão contradiz regras 🟢 do `_reversa_sdd/domain.md` sem registro explícito em `legacy-impact.md` e `regression-watch.md`.
- Todos os componentes citados existem em `_reversa_sdd/architecture.md` e `_reversa_sdd/addenda/017-construtor-armario-v2.md`.

### Eixo 4 — Sanidade do actions
- Todas as dependências em `actions.md` apontam para IDs válidos (`T001`–`T032`).
- Nenhuma ação marcada `[//]` compartilha arquivo alvo com outra `[//]` na mesma fase.
- Grafo de dependências acíclico (maior cadeia = 6).

### Auditoria Extra — Aparência vs Mockup & Validação Ao Vivo via Blender MCP (5.2.0 LTS)
- **Aparência do Construtor de Armários (`armario_v2/panel.py` vs `mockup_construtor_armarios.html`):** ajustado para exibir barra de título com badge de status de chapa (`Chapa OK` / `Fora da chapa`) + botão rápido `Plano de Corte`, barra de ferramentas superior (`Montar Caixa`, `Limpar`, `Abrir/Fechar`), grade de 7 abas em 2 linhas com ícones (`4 + 3`, sem truncamento no N-panel) e subcabeçalho com dimensões `L × A × P mm`, montagem e vão ativo.
- **Bugs reais detectados e corrigidos durante a validação ao vivo via Blender MCP:**
  1. `caffmob_draw/data/layers.py`: `_get_or_create_child` agora reaproveita `bpy.data.collections.get(name)` antes de criar nova coleção, evitando duplicatas como `Marcenaria.001`.
  2. `caffmob_draw/cutting/ops_opcut.py`: corrigida a chamada `part_extractor.extract_production_parts(context)` com desempacotamento da tupla `(parts, _incompatible)`.
- **Resultado final no Blender 5.2.0 LTS via MCP:** 9/9 blocos E2E (`RF-01` a `RF-13` + painel mockup) aprovados (`PASS`), `test_i18n_coverage.py` 100% verde e `caffmob_draw.zip` empacotado.

### Revalidação de 2026-11-24 — MCP como única regra de verdade

Servidor: `/opt/blender/blender --background --online-mode -c blender_mcp --host localhost --port 9877` (Blender 5.2.0 LTS), add-on registrado por `tests/_blender_env.py` dentro da própria sessão.

| Bloco | Superfície exercitada pela API real | Resultado |
|-------|--------------------------------------|-----------|
| Testes puros no Blender | `test_opcut_core`, `test_cutting_module_export`, `test_drawer_detect_core`, `test_stick_release_guard`, `test_floor_direction_and_layers`, `test_lowered_wall_classify`, `test_smoke_021` | 24/24 |
| i18n | `test_i18n_coverage` | 3/3 |
| E2E (`tests/blender_021_mcp_e2e.py`) | camadas `Arquitetura > Parede\|Piso\|Teto\|Aberturas` e `Marcenaria`; piso `DOWN`/`UP`; OpCut (plano, lista por módulo, sem ferragens, prévia RGBA, exportação HTML/SVG/PDF atómica); conversão em gaveteiro na `Marcenaria`; parede rebaixada + `Restaurar Parede` + submenu `Converter em`; colisão global no header; detector/cancelamento de texturas perdidas; grudar/desgrudar com `released_host_name`; `Criar Armário` → construtor v2; painéis OpCut/Texturas; painel do construtor vs mockup | 50/50 |

**Aparência:** o `BTM_PT_ArmarioV2` reproduz a metade direita do mockup — barra de título com badge de chapa, barra de ferramentas (Montar Caixa/Limpar/Abrir-Fechar), 7 abas em 2 linhas, subcabeçalho com dimensões/montagem/vão e rodapé Gerar/Aplicar/Cancelar. O que o mockup tem e o N-panel não pode ter é a área de desenho (vista frontal/corte lateral, HUD flutuante e inspetor): essa superfície é a própria Viewport 3D do Blender. Não há ajuste de código pendente para a aparência dentro dessa limitação.
