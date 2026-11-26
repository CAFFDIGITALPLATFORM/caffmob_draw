# Actions: Janela do plano de corte, medição de malha e controle de arestas

> Identificador: `027-janela-plano-corte-e-medicao-malha`
> Data: `2026-11-26`
> Roadmap: `_reversa_forward/027-janela-plano-corte-e-medicao-malha/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 14 |
| Concluídas | 3 |
| Abertas | 11 |
| Paralelizáveis (`[//]`) | 4 |

## Fase 1, Coleção de câmeras (concluída)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T001 | Coleção `CAMERAS`, cor de etiqueta aleatória, adoção das câmeras existentes e reaproveitamento da coleção antiga | - | `[//]` | `caffmob_draw/promob/cameras.py` | `[X]` |
| T001b | Câmera sem Empty e sem Track To: alvo vira ponto na câmera, orientação por código, migração das cenas antigas, Altura do alvo / Atualizar / Percorrer pelo ponto | T001 | - | `caffmob_draw/promob/cameras.py` | `[X]` |
| T002 | Ensaio no Blender: nome único, cor estável, adoção, não mover câmera já organizada, sem Empty/Track To, migração e importação de vistas | T001, T001b | - | `tests/blender_cameras_colecao.py` | `[X]` |
| T003 | Revisão de API e lint do arquivo tocado | T001 | - | `docs/rag/tools/check_api.py`, ruff | `[X]` |

## Fase 2, Arestas

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T004 | Preferência de espessura da aresta (padrão 0,2 px) e desenho da linha preta no viewport | - | `[//]` | `caffmob_draw/**/preferences`, `overlay` | `[ ]` |
| T005 | Modo “somente textura” sem nenhuma aresta nem vértice visível | T004 | - | idem | `[ ]` |

## Fase 3, Aplicar em todos os selecionados

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T006 | Preferência “aplicar transformações em todos os selecionados” (padrão ligada) | - | `[//]` | preferências do add-on | `[ ]` |
| T007 | Leitura multi-objeto com valor comum, vazio e `?` quando diverge, e dica no hover | T006 | - | painel de item | `[ ]` |
| T008 | Diálogo de confirmação ao definir valor e aplicação em todos com um passo de desfazer | T007 | - | painel de item | `[ ]` |

## Fase 4, Plano de corte em janela

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T009 | Janela própria do plano de corte no padrão do editor de parede; sistema antigo sai do caminho de entrada | T008 | - | novo módulo de janela + `cutting/` | `[ ]` |

## Fase 5, V-Ray Mesh Measure

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T010 | Janela, detecção da malha selecionada, conta-gotas e aviso sem seleção | T009 | - | módulo novo | `[ ]` |
| T011 | Partes soltas como camadas, medidas por parte e raio-X | T010 | - | módulo novo | `[ ]` |
| T012 | Câmera orbital 3D, perspectiva/ortográfica e snap configurável | T011 | - | módulo novo | `[ ]` |
| T013 | Representações (Aramado, Linhas Ocultas, Sólido, Raio-X, Material) e cor sólida por parte | T012 | - | módulo novo | `[ ]` |
| T014 | Medidas manuais, unidades (absoluta/arredondada em cm/mm/m) e impressão com views e badges | T013 | - | módulo novo | `[ ]` |

## Provas da rodada

| Comando | Resultado |
|---------|-----------|
| `tests/blender_cameras_colecao.py` (Blender 5.2.0, `--background`) | **27/27 OK**, saída 0 |
| `tests/blender_025_place.py` (Blender 5.2 do Windows, janela real) | **16/16 OK**, saída 0 |
| `tests/blender_012_library_ui.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_biblioteca_detalhe.py` (Blender 5.2 do Windows, janela real) | OK, saída 0 |
| `tests/blender_026_parity.py` (Blender 5.2.0, xvfb) | **23/23 OK**, saída 0 |
| `tests/blender_023_fase7.py` (Blender 5.2.0, `--background`) | OK, saída 0 |
| `tests/test_armario_026_parity` + `test_i18n_coverage` | **9/9 OK** |
| `tests/blender_smoke.py` | `BLENDER_SMOKE_OK`, saída 0 |
| `docs/rag/tools/check_api.py` | nenhuma API desconhecida |
| `ruff check` nos arquivos tocados | limpo |

## Limites desta rodada

- Os três ensaios de GUI exigem janela com GPU: no Blender do Linux/WSL o EGL/Zink não cria superfície e o processo
  aborta. Passaram a ser executados no **Blender 5.2 do Windows**, chamado do WSL por `powershell.exe` com
  `Start-Process -Wait -RedirectStandardOutput`, e aí sim rodaram com janela real.
- A matriz tem 11 linhas abertas. **A auditoria da 027 não é 0/0/0/0.**

## Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial; T001–T003 executados e provados | reversa |
