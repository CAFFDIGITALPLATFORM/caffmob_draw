# Actions: Janela do plano de corte, medição de malha e controle de arestas

> Identificador: `027-janela-plano-corte-e-medicao-malha`
> Data: `2026-11-26`
> Roadmap: `_reversa_forward/027-janela-plano-corte-e-medicao-malha/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 14 |
| Concluídas | 14 |
| Abertas | 0 |
| Paralelizáveis (`[//]`) | 4 |

## Fase 1, Coleção de câmeras (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T001 | Coleção `CAMERAS`, cor de etiqueta aleatória, adoção das câmeras existentes e reaproveitamento da coleção antiga | - | `[//]` | `caffmob_draw/promob/cameras.py` | `[X]` |
| T001b | Câmera sem Empty e sem Track To: alvo vira ponto na câmera, orientação por código, migração das cenas antigas, Altura do alvo / Atualizar / Percorrer pelo ponto | T001 | - | `caffmob_draw/promob/cameras.py` | `[X]` |
| T002 | Ensaio no Blender: nome único, cor estável, adoção, não mover câmera já organizada, sem Empty/Track To, migração e importação de vistas | T001, T001b | - | `tests/blender_cameras_colecao.py` | `[X]` |
| T003 | Revisão de API e lint do arquivo tocado | T001 | - | `docs/rag/tools/check_api.py`, ruff | `[X]` |

## Fase 2, Arestas (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T004 | Preferência de espessura da aresta (padrão 0,2 px) e desenho da linha preta no viewport | - | `[//]` | `caffmob_draw/__init__.py`, `caffmob_draw/overlays/arestas.py` | `[X]` |
| T005 | Modo “somente textura” sem nenhuma aresta nem vértice visível | T004 | - | `ui/view_mode.py`, `ui/view_mode_core.py`, `armario_v2/exibicao.py` | `[X]` |

## Fase 3, Aplicar em todos os selecionados (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T006 | Preferência “aplicar transformações em todos os selecionados” (padrão ligada) | - | `[//]` | `caffmob_draw/__init__.py` | `[X]` |
| T007 | Leitura multi-objeto com valor comum, vazio e `?` quando diverge, e dica no hover | T006 | - | `target/multi_apply.py`, `target/snapshot.py`, `target/resolver.py`, `ui/object_properties.py` | `[X]` |
| T008 | Diálogo de confirmação ao definir valor e aplicação em todos com um passo de desfazer | T007 | - | `target/ops.py`, `ui/object_properties.py` | `[X]` |

## Fase 4, Plano de corte em janela (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T009 | Janela própria do plano de corte no padrão do editor de parede; sistema antigo sai do caminho de entrada | T008 | - | `cutting/plan_window.py`, `cutting/plan_window_core.py` | `[X]` |

## Fase 5, V-Ray Mesh Measure (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T010 | Janela, detecção da malha selecionada, conta-gotas e aviso sem seleção | T009 | - | `mesh_measure/core.py`, `mesh_measure/scene.py`, `mesh_measure/window.py` | `[X]` |
| T011 | Partes soltas como camadas, medidas por parte e raio-X | T010 | - | `mesh_measure/scene.py`, `mesh_measure/draw.py` | `[X]` |
| T012 | Câmera orbital 3D, perspectiva/ortográfica e snap configurável | T011 | - | `mesh_measure/camera.py`, `mesh_measure/core.py` | `[X]` |
| T013 | Representações (Aramado, Linhas Ocultas, Sólido, Raio-X, Material) e cor sólida por parte | T012 | - | `mesh_measure/draw.py`, `mesh_measure/scene.py` | `[X]` |
| T014 | Medidas manuais, unidades (absoluta/arredondada em cm/mm/m) e impressão com views e badges | T013 | - | `mesh_measure/core.py`, `mesh_measure/draw.py`, `mesh_measure/window.py` | `[X]` |

## Provas da rodada

| Comando | Resultado |
|---------|-----------|
| `tests/blender_cameras_colecao.py` (Blender 5.2.0, `--background`) | **27/27 OK**, saída 0 |
| `tests/blender_027_arestas_multiplos.py` (Blender 5.2.0, `--background`) | **22/22 OK**, saída 0 |
| `tests/blender_027_plano_corte.py` (Blender 5.2.0, `--background`) | **29/29 OK**, saída 0 |
| `tests/blender_027_medicao_malha.py` (Blender 5.2.0, `--background`) | **81/81 OK**, saída 0 |
| `tests/blender_027_janelas.py` (Blender 5.2 do Windows, janela real) | **18/18 OK** — as duas janelas abrem, desenham nas cinco representações, montam a folha e fecham limpando a sessão |
| `tests/blender_010_view_mode_smoke.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_024_exibicao.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_024_visual.py` (Blender 5.2 do Windows, janela real + render) | OK, saída 0 |
| `tests/blender_067_onda1_tipos.py` (Blender 5.2 do Windows, janela real) | OK, inclui 18 em três chapas e **um** Desfazer |
| `tests/blender_025_place.py` (Blender 5.2 do Windows, janela real) | **16/16 OK**, saída 0 |
| `tests/blender_012_library_ui.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_biblioteca_detalhe.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_026_parity.py` (Blender 5.2.0, xvfb) | **23/23 OK**, saída 0 |
| `tests/blender_023_fase7.py` (Blender 5.2.0, `--background`) | OK, saída 0 |
| `tests/blender_021_mcp_e2e.py` (Blender 5.2.0, `--background`) | **52/52 OK** — inclui o painel do plano de corte e a prévia OpCut |
| `tests/blender_005_sidebar_inventory.py` (Blender 5.2.0, `--background`) | OK — o operador novo não duplica seção e nenhum caminho antigo se perdeu |
| `tests/blender_024_prefs.py` e `tests/blender_smoke.py` | 0 falhas / `BLENDER_SMOKE_OK` |
| Suíte pura (`unittest discover -p "test_*.py"`) | 1648 testes, **5 falhas pré-existentes** em `library_categories`, `bug_EI4W` e `smoke_021` (arquivos não tocados) |
| `tests/test_i18n_coverage.py` | 3/3 OK (13 + 38 + 84 chaves novas nas três áreas) |
| `docs/rag/tools/check_api.py` | nenhuma API desconhecida (648 arquivos) |
| `ruff check` nos arquivos tocados | limpo |

## Limites desta rodada

- Os ensaios com janela exigem GPU: no Blender do Linux/WSL o EGL/Zink não cria superfície. Foram executados no
  **Blender 5.2 do Windows**, chamado do WSL por `powershell.exe` com `Start-Process -Wait`.
- A linha de 0,2 px é a mais fina que a placa desenha (a GPU não desenha abaixo de 1 pixel); o valor da preferência é
  passado como `lineWidth` do `POLYLINE_UNIFORM_COLOR`, então acima de 1 a espessura cresce de verdade.
- **Linhas Ocultas** e **Sólido** são desenhados sem teste de profundidade (o Image Editor não garante buffer de
  profundidade): a oclusão vem da ordem de pintura (longe → perto) e, no caso das linhas ocultas, das faces pintadas
  na cor do papel antes do contorno das faces da frente. A aparência foi conferida na execução do
  `tests/blender_027_janelas.py`, não pixel a pixel.
- A matriz tem **0 linha aberta**. O cross-check formal (`/reversa-audit`) fica para o fecho da feature.

## Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial; T001–T003 executados e provados | reversa |
| 2026-11-26 | T004–T008 (RF-03, RF-04) executados e provados; linha preta própria com espessura e medidas da seleção múltipla com confirmação | reversa |
| 2026-11-26 | T009–T014 executados e provados: janela do plano de corte e janela V-Ray Mesh Measure; matriz fechada | reversa |
