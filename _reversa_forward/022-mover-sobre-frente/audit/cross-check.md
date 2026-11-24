# Cross-Check Audit: Frente do objeto no Mover Sobre

> Identificador: `022-mover-sobre-frente`
> Data: `2026-11-24` (rodada 2 — depois do clarify e da implementação)
> Artefatos analisados:
> - `_reversa_forward/022-mover-sobre-frente/requirements.md`
> - `_reversa_forward/022-mover-sobre-frente/roadmap.md`
> - `_reversa_forward/022-mover-sobre-frente/actions.md`
>
> **Nenhum dos três artefatos foi alterado por esta rodada.** Verificação adicional por código e execução real.

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 2 |
| LOW | 2 |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | MEDIUM | Cobertura | O RNF de desempenho ("decisão em menos de 5 ms para 200 paredes") continua sem ação e sem medição. A decisão roda uma vez por abertura (não por quadro), mas não há ensaio que prove o orçamento | `requirements.md` §6 × `actions.md` |
| A002 | MEDIUM | Cobertura | A pergunta automática de RN-05 **não dispara no caminho de arraste** (`from_drag=True`): o gesto não é interrompido e a frente vem de parede/eixo. Só o botão \"Frente do objeto\" permite corrigir nesse caminho. A decisão está registrada em `actions.md §Notas de execução`, mas o `requirements.md` não a declara como exceção de RN-05 | `requirements.md` RN-05 × `caffmob_draw/move_over/ops_dialog.py` (`if self.mo.front_ambiguo and not self.skip_front`) |
| A003 | LOW | Modelo de dados | Com `btm_front_yaw ≠ 0`, as posições salvas (`Scene.btm_saved_positions`) ficam relativas ao referencial girado. Como a frente é persistida no objeto, o referencial é estável; a limitação só aparece se o usuário trocar a frente entre salvar e aplicar | `caffmob_draw/move_over/scene.py` (`b_frame`, `saved`) |
| A004 | LOW | Consistência | `RN-01` fala em parede \"que cubra o pé de B em planta\" e o código usa a projeção do comprimento da parede com tolerância de 50 mm (`wall_candidate`); o número não está no requirements | `requirements.md` RN-01 × `caffmob_draw/move_over/frente_core.py` |

## Itens verificados e aprovados

### Eixo 1 — Cobertura
- RN-01..RN-08 têm RF correspondente, decisão no roadmap (D-01..D-05) e ação concluída (T001..T012, todas `[X]`).
- D1–D5 do clarify foram integradas em RN-01, RN-02, RN-05 e RN-06 e a seção `## Lacunas` ficou vazia.
- Cenários Gherkin cobertos por `tests/test_move_over_frente_core.py` (17 ensaios) e
  `tests/blender_022_mover_sobre_frente.py` (10 verificações no Blender 5.2, todas `PASS`).

### Eixo 2 — Consistência
- Terminologia estável (`frente`, `btm_front_yaw`, `view_frame`, `PAREDE`/`EIXO`/`PROPRIEDADE`).
- Todos os IDs citados existem (`RN-01`–`RN-08`, `RF-01`–`RF-08`, `D-01`–`D-05`, `T001`–`T012`).

### Eixo 3 — Coerência com o legado
- A decisão da 017 (`btm_front_yaw` válida para todo o add-on) é respeitada.
- `yaw = 0` mantém a matriz e as caixas anteriores (conferido na fumaça: `_target_matrix` com delta 0 devolve a
  posição original).
- Nenhum handler novo permanente: o operador é registrado e removido no `unregister` de `move_over`.

### Eixo 4 — Sanidade do actions
- Dependências só para IDs existentes; grafo acíclico.
- Nenhuma dupla `[//]` compartilha arquivo alvo; A002 da rodada anterior (T005/T007 em `ops_dialog.py`) foi resolvida
  porque T005 deixou de exigir camada de conversão.

## Execuções desta rodada

| Comando | Resultado |
|---------|-----------|
| `python tests/test_move_over_frente_core.py` | 17/17 OK |
| `"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tests/blender_022_mover_sobre_frente.py` | `{"pass": 10, "fail": 0}` |
| `python tests/test_i18n_coverage.py` | 3/3 OK |
| `python docs/rag/tools/check_api.py` | 619 arquivos, 0 símbolos desconhecidos |
| `python _reversa_bugs/tools/reversa_debugger.py --suite pure --out .../2026-11-24-coding-022` | pura **187/187**, 97,4 s |
| `python _reversa_bugs/tools/reversa_debugger.py --suite blender --blender ... --out .../2026-11-24-coding-022-blender` | Blender **199/204**, 1 315,7 s, 0 defeito — as 5 falhas são ambiente (rede/MOBI/extensão), as mesmas de sempre |

> **Nota da reconciliação (2026-11-24, fechamento da auditoria da 021):** das 5 falhas que esta rodada classificou
> como ambiente, **3 não eram** — `blender_065_cena_v2` e `blender_065_baixar_v2` falhavam por um defeito real de
> produto (abertura sem `modelo` caía no caminho de janela fixa, em `openings/window_core.py`; corrigido em
> `window_parts`) e `blender_increment1_smoke` era ensaio carregando o addon fora de `bl_ext.*`. Só
> `blender_065_ida_e_volta` e `blender_ensaio_mobi` continuam exigindo o MOBI de ensaio em `127.0.0.1` com
> `--online-mode`. Números da reexecução em `_reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-reconciliacao*`.

## Próximo passo sugerido

Sem CRITICAL nem HIGH: a feature está pronta para revisão do titular. A001 e A002 são melhorias de cobertura
(medição de desempenho e prompt no caminho de arraste) e podem virar ações de uma próxima rodada, se o titular quiser.
