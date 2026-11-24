# Inspeção da suíte completa · 2026-11-24

## Escopo

- 186 arquivos `tests/test_*.py` (Python puro, um processo por arquivo, limite de 45 s).
- 203 arquivos `tests/blender_*.py` (Blender 5.2 LTS, `--background --factory-startup`, limite de 90 s na primeira passada).
- Ruff não faz parte da suíte; os 149 avisos existentes são prévios a esta inspeção.

## Resultado da primeira passada

| Suíte | Passou | Falhou | Timeout |
|---|---:|---:|---:|
| Pura | 156 | 30 | 0 |
| Blender | 177 | 25 | 1 (`066_cladding_bench`, performance) |

## Defeitos de produto corrigidos

| Bug | Sintoma | Causa | Correção |
|---|---|---|---|
| #156 `BUG-20261124-7K2M` | 29 testes puros não importavam | `NotRequired` só existe no Python 3.11 | fallback para `typing_extensions` |
| #157 `BUG-20261124-3Q9X` | `test_017_corte` sem `grain_angle` | acesso direto a campo opcional | `getattr(..., 0.0)` |
| #158 `BUG-20261124-8W4D` | janela sem modelo virava de giro | `None` tratado como modelo | padrão `janela_correr_2f` |
| #159 `BUG-20261124-5N6R` | plano vazio criava `Arquitetura` vazia | coleções Piso/Teto criadas antes de usar | criação preguiçosa |
| #160 `BUG-20261124-2C8T` | Redimensionar não adaptava agregados | caminho direto da 080 pulava a adaptação | estado + adaptação após a transação |

Todos fechados com `DONE.md`; as views foram regeneradas por `regenerate.py`.

## Ensaios desatualizados ajustados

| Arquivo | Ajuste |
|---|---|
| `blender_005_sidebar_inventory.py` | `caffmob_stairs.place_stairs` entrou na lista de aposentados: a 071 o substituiu pelo editor novo de escadas |
| `blender_bug_5R7U_cabinet_editor.py` | sai com aviso de obsoleto quando o editor 2D (removido pela 017) não está registrado |
| `blender_bug_6JIM_cabinet_queue.py` | idem |
| `blender_identity_smoke.py` | ignora os arquivos da interface antiga do editor 2D ao procurar operadores citados |
| `blender_bug_A2G7_floor.py` | mede só a face superior; o piso virou laje com laterais (26,1 m² era 12 m² + 12 m² + 2,1 m²) |
| `blender_bug_YAVM_wall_editor.py` | acompanha o terceiro retângulo de `_toolbar_rects` |

## Falhas de ambiente

| Arquivo | Motivo |
|---|---|
| `blender_065_baixar_v2.py`, `blender_065_cena_v2.py` | `online_access: false`; referência remota não baixada |
| `blender_065_ida_e_volta.py`, `blender_ensaio_mobi.py` | exigem o MOBI de ensaio em `127.0.0.1` |
| `blender_increment1_smoke.py` | `ValueError: The "package" does not name an extension` sem a extensão instalada |
| `blender_066_cladding_bench.py` | passa com limite maior; o teste de performance leva mais de 90 s |
| `blender_067_proto_snapshot.py` | `refresh` p95 2,89–3,02 ms contra alvo de 2,0 ms; medição de máquina, não reproduzida como defeito funcional |

## Ajustes de ensaio feitos junto das correções

- `009`, `013`, `065_walls2d_selecao`: fake do modal ganhou `_handle_menu`; `013` acompanha o terceiro retângulo da barra.
- `002`: inventário ignora os arquivos da interface antiga do editor 2D.
- `014_apply` e `014_image_material`: nome do material aceita o nome do catálogo (feature 018/073).
- `071_promob`: metal PBR aceita `Metallic` ligado a mapa, não só valor 1.0.
- `texture_grid`: itens PBR do catálogo (073) não entram na contagem das 1209 texturas comuns.
- `7YO4`: contexto falso ganhou `view_layer` e `window_manager`.
- `test_packaging`: `novo_arm_building/` é pasta de referência versionada, não extensão.

## Reversa Debugger executado

O runner executável está em `_reversa_bugs/tools/reversa_debugger.py` (documentação em `_reversa_bugs/tools/README.md`).

```bash
python3 _reversa_bugs/tools/reversa_debugger.py --suite all --blender /opt/blender/blender \
  --pure-timeout 45 --blender-timeout 360 \
  --out _reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-debugger
```

- Exit code: **0** (nenhum defeito candidato).
- Saída real: `2026-11-24-debugger/report.md`, `results.json` e um log por ensaio em `pure/` e `blender/`.
- Placar do runner: **pura 186/186**; **Blender 197/203**; 5 ambiente, 1 performance, 0 defeitos.
- Tempo total: 991,7 s.

## Resultado final

- Pura: **186/186 passam** (0 falhas, 0 timeouts).
- Blender: **197/203 passam, 6 falham, 0 timeouts**.
- Falhas restantes, todas classificadas pelo runner:
  - ambiente: `065_baixar_v2`, `065_cena_v2`, `065_ida_e_volta`, `ensaio_mobi`, `increment1_smoke`;
  - performance: `067_proto_snapshot` (p95 de refresh 3,15 ms > alvo 2,0 ms).

## Limitações restantes

- Testes com janela/GUI e os de rede não foram executados neste ambiente headless.
- `066_cladding_bench` passa com limite de 300 s; o teste de performance não cabe nos 90 s da primeira passada.
- `067_proto_snapshot` mede tempo de máquina; não foi reproduzido como defeito funcional.
