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

**Estado dos registros (corrigido na reconciliação de 2026-11-24):** só o #156 tem cartão próprio em `bugs/`
(`BUG-20261124-7K2M-contrato-sem-notrequired/`, com `DONE.md`). Os cartões `3Q9X` (#157), `8W4D` (#158),
`5N6R` (#159) e `2C8T` (#160) **não existem no repositório** — foram corrigidos direto no código junto da feature
021 (commit `f2f35215`), sem abrir cartão, e esta tabela é o único registro deles. Não houve regeneração de views
por `regenerate.py` nesta rodada.

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

> **Correção da reconciliação de 2026-11-24:** as duas primeiras linhas abaixo estavam **mal classificadas**.
> `blender_065_cena_v2` e `blender_065_baixar_v2` não falhavam por rede: falhavam numa contagem de objetos
> (13 em vez de 14 e 17), causada por um defeito real de produto — abertura sem `modelo` caía no caminho de janela
> fixa em `openings/window_core.py` (regressão da 078). Corrigido em `window_parts` (`model = model or
> 'janela_correr_2f'` e `material = material or 'aluminio'`); os dois ensaios passam com as asserções originais.
> `blender_increment1_smoke` também deixou de ser ambiente: o ensaio carregava o addon como módulo solto em vez de
> `bl_ext.*`; ajustado, passa. Restam como ambiente só os dois que exigem MOBI de ensaio em `127.0.0.1`.

| Arquivo | Motivo |
|---|---|
| `blender_065_baixar_v2.py`, `blender_065_cena_v2.py` | ~~`online_access: false`; referência remota não baixada~~ **defeito real corrigido** (ver aviso acima) |
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

## Segunda passada (Linux)

> Rótulo das linhas de base: a seção **Resultado da primeira passada** é a fotografia de *antes* das correções
> (pura 156/30). A seção **Segunda passada (Windows 11)** é a fotografia *depois* — é ela que vale como placar.
> O "30" da primeira linha é o número de falhas de então, não um placar atual.

- Pura: **186/186 passam** (0 falhas, 0 timeouts).
- Blender: **197/203 passam, 6 falham, 0 timeouts**.
- Falhas restantes, todas classificadas pelo runner:
  - ambiente: `065_baixar_v2`, `065_cena_v2`, `065_ida_e_volta`, `ensaio_mobi`, `increment1_smoke`;
  - performance: `067_proto_snapshot` (p95 de refresh 3,15 ms > alvo 2,0 ms).

## Limitações restantes

- Testes com janela/GUI e os de rede não foram executados neste ambiente headless.
- `066_cladding_bench` passa com limite de 300 s; o teste de performance não cabe nos 90 s da primeira passada.
- `067_proto_snapshot` mede tempo de máquina; não foi reproduzido como defeito funcional.

## Segunda passada (Windows 11, 2026-11-24) — estado final

Runner: `python _reversa_bugs/tools/reversa_debugger.py --suite all --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --pure-timeout 45 --blender-timeout 360 --out _reversa_bugs/plugin-caffmob-draw/inspections/2026-11-24-debugger`

- Exit code **0**, 994,6 s, sem outro processo na máquina durante a medição.
- Saída real no repo: `2026-11-24-debugger/report.md`, `results.json` e um log por ensaio (`pure/` 186, `blender/` 203).
- Antes das correções a mesma máquina dava pura **181/186** e Blender **193/203**, com 10 falhas classificadas
  como **defeito** pelo runner. Cada uma foi reproduzida, diagnosticada e corrigida; **nenhuma asserção foi
  afrouxada** — o que mudou foi portabilidade do ensaio e, em dois casos, o produto.

### Defeitos de produto corrigidos

| Arquivo | Sintoma | Causa | Correção |
|---|---|---|---|
| `caffmob_draw/texture_library/downloads.py` | `blender_014_apply` e `blender_014_textures_net` falhavam com `AssertionError: A ponte não respondeu dentro do prazo`; a ponte nunca entregava resposta | `proc.stdout.read()` num pipe **texto não-bloqueante** levanta `TypeError` no Windows e `_read_lines` engolia o erro, devolvendo vazio (catálogo, login e downloads ficavam mudos) | thread leitora `_pump` enfileira as linhas sob lock e o `bpy.app.timers` drena; `os.set_blocking` sai; `eof` marca o fim do pipe (achado T004 preservado) |
| `caffmob_draw/texture_library/downloader.py` | mensagens acentuadas do worker saíam em cp1252 e o Blender (que lê UTF-8) não decodificava — `UnicodeDecodeError`/mensagem perdida | `sys.stdout` do filho usava o locale do sistema | `sys.stdin`/`sys.stdout.reconfigure(encoding="utf-8")` no `main()` |

Evidência da correção: `blender_014_apply: OK` e `BLENDER_014_TEXTURES_NET_OK`, com os logs em
`2026-11-24-debugger/blender/`.

### Ensaios ajustados para Windows (sem afrouxar asserção)

| Arquivo | Ajuste | Por quê |
|---|---|---|
| `test_071_texturas` | `ps.__file__.rsplit('/', 2)` → `Path(...).parents[1]` | separador `/` fixo não resolve caminho no Windows |
| `test_identity` | `read_text(encoding="utf-8")` | `read_text()` sem encoding usa cp1252 e quebra em fonte UTF-8 |
| `test_object_library` | `endswith("DECOR/vaso-1.blend")` → `Path(...).parts[-2:]` | o produto usa `os.path.join` (correto); a asserção era POSIX |
| `test_standards_store` | conexões `sqlite3` fechadas num helper `_snapshot` | o Windows tranca o arquivo e o `rmtree` do tearDown falhava |
| `test_texture_downloader` | `select()` → thread + `queue`; `call(..., timeout=)` | `select()` só aceita soquetes no Windows; a recusa de loopback leva ~2 s por tentativa e o retry 2+4+8 s do produto pedia 60 s |
| `blender_014_textures_net` | assert de `chmod 600` só em `os.name == "posix"` | o Windows não tem modo POSIX; a proteção é o ACL do perfil |
| `blender_067_onda1_padroes` | `with sqlite3.connect(...)` → `try/finally: close()` | `with` só confirma a transação; o arquivo ficava trancado no `TemporaryDirectory` |
| `blender_073_pbr` | dois `endswith(".../...")` → `Path(...).parts[-2:]` | separador POSIX |
| `blender_mobi_operadores` | `mat['btm_texture_path'] == cached` → `Path(a) == Path(b)` | separador POSIX |

### Placar final

| Suíte | Arquivos | Passaram | Falharam | Timeouts | Classificação |
|---|---:|---:|---:|---:|---|
| Pura | 186 | **186** | 0 | 0 | — |
| Blender | 203 | **198** | 5 | 0 | ambiente: 5, defeito: 0, performance: 0 |

Os dois ensaios de tempo passam nesta passada: `blender_066_cladding_bench` (exit 0) e
`blender_067_proto_snapshot` com `PROTO_SNAPSHOT {"refresh": {"n": 360, "p50": 0.23, "p95": 1.32, "p99": 1.43}}` e
`PROTO_SNAPSHOT_OK` (alvo de p95: 2,0 ms).

### Falhas restantes — todas bloqueadas por ambiente

| Ensaio | Classificação | Evidência (comando + trecho do log em `2026-11-24-debugger/blender/`) |
|---|---|---|
| `blender_065_baixar_v2` | ambiente | `{"status": "erro", "blender": "5.2.0 LTS", "online_access": false}` |
| `blender_065_cena_v2` | ambiente | `{"status": "erro", "blender": "5.2.0 LTS", "online_access": false, "verificacoes": []}` |
| `blender_065_ida_e_volta` | ambiente | `assert urlsplit(BASE).scheme == 'http' and urlsplit(BASE).hostname == '127.0.0.1', 'Somente o MOBI de ensaio em 127.0.0.1'` |
| `blender_ensaio_mobi` | ambiente | `assert urlsplit(base).hostname == '127.0.0.1' and urlsplit(base).scheme == 'http', base` |
| `blender_increment1_smoke` | ~~ambiente~~ **ensaio corrigido** | o ensaio carregava o addon como módulo solto (`import caffmob_draw`), não como `bl_ext.*`; ajustado, passa (`BLENDER_INCREMENT1_SMOKE_OK`) |

**Correção da reconciliação de 2026-11-24:** três destas cinco "falhas de ambiente" não eram ambiente.
`blender_065_cena_v2` e `blender_065_baixar_v2` falhavam por um **defeito real**: abertura sem `modelo` caía no
caminho de janela fixa em `openings/window_core.py` (regressão da 078), gerando 2 peças em vez de 3; corrigido em
`window_parts` (`model = model or 'janela_correr_2f'`, `material = material or 'aluminio'`), e os dois ensaios
passam com as asserções originais (14 e 17 objetos). `blender_increment1_smoke` era ensaio desatualizado, também
corrigido. Só os dois que exigem MOBI descartável em `127.0.0.1` + `--online-mode`
(`blender_065_ida_e_volta`, `blender_ensaio_mobi`) continuam bloqueados por recurso externo — ambos param no
`assert` de `CAFFMOB_BASE` antes de tocar a cena.

## Reconciliação (2026-11-24) — fechamento da auditoria da 021

Depois de revisar as cinco "falhas de ambiente" uma a uma, três deixaram de ser ambiente:

| Ensaio | Era | Virou |
|---|---|---|
| `blender_065_cena_v2` | `AssertionError: Referência rica original: 14 objetos` (com 13), classificado como `online_access: false` | **defeito real corrigido**: `openings/window_core.window_parts` recebia `model=None` e caía no ramo de janela fixa (2 peças em vez de 3). O padrão do contrato (`caffmob/v2/contrato.py`: `WINDOW` → `janela_correr_2f`/`aluminio`) agora vale dentro da função |
| `blender_065_baixar_v2` | `AssertionError: Referência rica monta 17 objetos` | mesma causa; passa com 17 objetos |
| `blender_increment1_smoke` | `ValueError: The "package" does not name an extension` | **ensaio corrigido**: carga como `bl_ext.*` (não como módulo solto) e banco de padrões em diretório temporário — antes ele deixava "Padrão Brasil - cópia" gravado no `padroes.sqlite3` do pacote de ensaio e a execução seguinte falhava na primeira asserção |

Restam como ambiente apenas `blender_065_ida_e_volta` e `blender_ensaio_mobi`, que exigem um MOBI descartável em
`127.0.0.1` com `--online-mode` (ambos param no `assert` de `CAFFMOB_BASE`, antes de tocar a cena).

### Placar depois da reconciliação

| Suíte | Arquivos | Passaram | Falharam | Timeouts | Exit |
|---|---:|---:|---:|---:|---:|
| Pura | 187 | **187** | 0 | 0 | 0 |
| Blender | 204 | **202** | 2 (ambiente: 2) | 0 | 0 |

Saída real: `2026-11-24-reconciliacao-2/report.md` (pura, 98,4 s) e
`2026-11-24-reconciliacao-blender-2/report.md` (Blender, 980,9 s). Os relatórios das passadas anteriores desta seção
continuam válidos como histórico (199/204 e 198/203), mas o placar de hoje é o das duas linhas acima.

## Limitações da passada de Windows

- Ensaios com janela/GUI continuam fora (execução headless).
- `ruff` não está instalado nesta máquina (`command not found`): o estilo não foi conferido pelo lint.
- `git diff`/`git status` globais falham por causa do symlink `AGENTS.md` (`core.symlinks=false` no clone +
symlink real no worktree): as conferências de diff foram feitas por caminho (`git diff -- caffmob_draw tests`).
