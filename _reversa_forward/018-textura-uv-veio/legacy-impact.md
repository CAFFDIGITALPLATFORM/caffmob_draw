# Legacy impact: Textura por UV, veio e conta-gotas

> Data: `2026-11-23`
> Feature: `018-textura-uv-veio`
> Rodada: parcial (T001, T002, T003, T004, T005, T006, T007, T008, T010, T012, T013, T019 e T027 concluídas; T009, T011, T014–T018 e T020–T026 pendentes)
> Política de edição: `allowLegacyEdits: true`, `allowedPaths: ["***", "caffmob_draw/*", "tests/*"]`

**Aviso de política.** O glob `***` casa com qualquer caminho, então nesta configuração a liberação é efetivamente
irrestrita. Nesta rodada só foram escritos `tests/` e as pastas próprias do Reversa (`_reversa_forward/`).

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `tests/blender_018_probe.py` (novo) | nenhum (ferramenta de verificação) | componente-novo | LOW | Probe headless das verificações 1 a 4 do T001; não é empacotado por `build.py` |
| `tests/blender_018_probe2.py` (novo) | nenhum (ferramenta de verificação) | componente-novo | LOW | Mede o UV avaliado do `GeoNodeCutpart` e o custo de `grain.sync` |
| `_reversa_forward/018-textura-uv-veio/investigation.md` | documentação | delta-de-contrato-externo | LOW | Recebe o resultado do T001 |
| `_reversa_forward/018-textura-uv-veio/roadmap.md` | documentação | delta-de-contrato-externo | LOW | D-02 validada e corrigida (UV em metros), D-03 reescrita com três fontes, D-14 acrescentada |
| `caffmob_draw/armario_v2/build.py` | código | aditivo | LOW | `_uv_metros` cria `UVMap` em metros na chapa; nenhum papel, medida ou material mudou |
| `caffmob_draw/object_library/retexture.py` | código | aditivo | MEDIUM | terceira fonte de textura e projeção na chave de cache; padrão `BOX` preserva o comportamento antigo |
| `caffmob_draw/texture_library/uv_core.py` | código | aditivo | LOW | módulo novo, sem `bpy` |
| `_reversa_forward/018-textura-uv-veio/requirements.md` | documentação | delta-de-contrato-externo | LOW | RN-08, RN-15 e RF-14 ajustados ao comportamento real do nó |
| `caffmob_draw/texture_library/catalog_core.py` | código | aditivo | LOW | T008: `nome_de_exibicao`, `nome_de_arquivo`, `eh_nome_antigo`, `nome_migrado`; nenhuma função existente mudou |
| `caffmob_draw/texture_library/catalog.py` | código | aditivo | LOW | T008: `nome_de(item_id)` com o catálogo local |
| `caffmob_draw/texture_library/uv_core.py` | código | aditivo | LOW | T019: mapa de partes do conta-gotas (`partes_para_dominios`, `dominios_do_alvo`, `alvos_unicos`) |
| `caffmob_draw/object_library/retexture.py` | código | contrato-alterado | MEDIUM | T008/T013: `material_name` usa o nome do catálogo quando houver; `migrar_nome` renomeia material antigo com o nome livre e sinaliza conflito. Nome do datablock muda; arquivo, tamanho e projeção ficam |
| `caffmob_draw/object_library/item_io.py` | código | regra-alterada | MEDIUM | `features_of` reconhece textura por `btm_texture_path`, não só pelo prefixo "Textura: ": sem isso o item salvo depois da 018 perderia a marca `TEXTURED` |
| `tests/test_018_nome.py`, `tests/test_018_partes.py`, `tests/test_018_material.py` (novos) | nenhum (ferramenta de verificação) | componente-novo | LOW | Testes puros de T004, T005 e T006 |
| `tests/blender_018_nome_smoke.py` (novo) | nenhum (ferramenta de verificação) | componente-novo | LOW | Fumaça 3/3 de T008/T013 no Blender 5.2.0 LTS |

Nenhum arquivo de `caffmob_draw/` foi tocado na rodada do T001; as rodadas seguintes tocaram `armario_v2/build.py`,
`object_library/retexture.py`, `object_library/item_io.py` e `texture_library/` (só acréscimos, exceto o nome do
material e a detecção de textura no item salvo).

## Diff conceitual por componente

- **Material de textura (`object_library/retexture.py`)**: alterado no T012 — `image_material` ganhou `projection` e o `btm_texture_projection` entrou na chave de cache; `apply_image` escolhe a fonte por alvo. Chamadas sem projeção continuam em `BOX`, então material antigo não muda. O T001 mostrou que a decisão D-03
  precisa de três fontes de coordenada, não duas: layer `UVMap` (armário v2 e malha importada), atributo `uv_map`
  (peça com `GeoNodeCutpart`) e projeção de caixa.
- **Geração do armário (`armario_v2/build.py`)**: não alterado ainda. O T001 confirmou que a chapa é caixa de `bmesh`
  sem modificador, então criar `UVMap` ali é viável e o layer é editável.
- **Parede (`operators/walls.py` e `GeoNodeWall`)**: não alterado e não precisa de alteração para receber material —
  os seis sockets existem. O UV da parede é gerado pelo grafo (`UV_Store`, FLOAT2, CORNER, nome `UVMap`) a cada
  avaliação, então edição no UV Editor na malha base é sobrescrita.
- **Serviço de veio (`texture_library/grain.py`)**: não alterado. Custo medido dentro do orçamento.

## Preservadas

- `_reversa_sdd/customize/requirements.md#RN-05`: precedência de material (peça > vão > grupo) continua sendo o
  caminho de gravação da textura aplicada.
- `_reversa_sdd/customize/requirements.md#RN-13`: grupos `CAIXA`, `FRENTES`, `FUNDO`, `INTERNO` continuam válidos.
- `_reversa_sdd/collision/requirements.md#RN-10` e `#RN-11`: a colisão não é tocada nesta feature (é a 019).
- `_reversa_sdd/cutting/requirements.md#Origem das peças`: o plano de corte continua lendo `btm_part.grain`; o ângulo
  visual é convertido para H/V antes de chegar nele (D-06).

## Modificadas

- Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada por código nesta rodada.
- No plano, duas decisões técnicas mudaram em função do T001: **D-03** (três fontes de coordenada) e **D-14** (limite
  do UV Editor em geometria de Geometry Nodes). Ambas estão registradas com data no `roadmap.md`.

## Observações de risco

- O T001 invalidou a promessa ampla de "UV Editor funciona em toda peça". O requisito foi corrigido para o que é
  verdade: UV Editor nas malhas com layer editável, aviso nas geradas por grafo.
- A correção definitiva para o UV de peça de biblioteca exigiria editar os `.blend` de nós do pacote ou aplicar o
  modificador nas peças — os dois caminhos foram descartados por decisão de escopo (D-14).

## Rodada 2026-11-23: T019, T014 e T011

- `customize/adapters/common.set_cutpart_material` deixou de devolver `True` em parede: agora grava os seis sockets do
  `GeoNodeWall` por `set_surface_material` e devolve `False` quando a parede marcada não tem o nó. Quem chamava e
  ignorava o retorno (`apply`, `retexture.apply_finish`) passa a contar só o que mudou de verdade.
- `armario_v2/build.gerar` passou a resolver o material da peça por `btm_armario_parte.material` antes do acabamento
  do spec. O plano de corte continua igual: sem escolha, o campo guarda a mesma chave de antes.
- `texture_library` ganhou `pick.py` e `ops_pick.py`, e `operators/viewport_hud.py` ganhou um segundo draw handler
  (`POST_PIXEL`) com remoção no `unregister` — nada muda para quem já estava registrado.

## Rodada 2026-11-23: T009, T020, T021 e T022 (veio em graus)

- `grain_core.rotation` ganhou `angle=0.0` como último argumento: chamadas antigas (T065, `grain.sync`, testes) ficam
  idênticas, e o ângulo só muda o eixo da normal.
- `uv_core.angulo_para_veio` passou a delegar em `grain_core.direction`: mesma tabela 0/180 → H e 90/270 → V, e
  `None` continua devolvendo H.
- `cutting/part_roles.part_grain` e `part_sources.armario_v2_records` derivam o veio do ângulo **quando o campo
  existe**. Arquivo antigo lê o campo com o padrão 0 (o RNA cria em todo objeto e em toda peça), e ângulo 0 devolve
  o mesmo `HORIZONTAL`/`VERTICAL`/`NONE` de antes: o plano de corte não muda.
- `armario_v2/props.py` e `target/props.py` ganharam `grain_angle` com `update` que chama `grain.sync`: mexer no
  ângulo gira a textura da peça, sem refazer o móvel e sem tocar nas irmãs do mesmo material.
