# Regression watch: Textura por UV, veio e conta-gotas

> Feature: `018-textura-uv-veio`
> Data: `2026-11-23`
> Base: fatos confirmados no T001 (Blender 5.2.0 LTS) e decisões D-02, D-03, D-14

## Itens de vigilância

| ID | Origem (arquivo, seção) | Regra esperada após a mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|-------------------------------|---------------------|-------------------|
| W001 | `caffmob_draw/geometry_nodes/GeoNodeCutpart.blend` (Store Named Attribute `UV_Store`, atributo `uv_map`) | A chapa gerada pelo `GeoNodeCutpart` continua sem layer de UV e com o atributo `uv_map` (CORNER, FLOAT_VECTOR) | presença | Um `uv_layers` não vazio no avaliado, ou `uv_map` ausente/em outro domínio: o material deixa de achar a textura |
| W002 | `caffmob_draw/geometry_nodes/GeoNodeWall.blend` (interface) | O grupo de parede mantém os seis sockets de material: `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge` | presença | Qualquer um dos seis sumir da interface: `set_surface_material` volta a não ter onde escrever |
| W003 | `caffmob_draw/geometry_nodes/GeoNodeWall.blend` (`UV_Store`) | A parede continua gravando `UVMap` (FLOAT2, CORNER) a partir de posição e normal | presença | UV da parede sumir ou mudar de nome: material em UV e o aviso de UV do grafo ficam errados |
| W004 | `caffmob_draw/armario_v2/build.py` (`_malha`) | A chapa do armário v2 continua sendo malha de `bmesh` sem modificador | ausência | Surgir modificador de nós na chapa: o `UVMap` criado em T010 deixa de sobreviver |
| W005 | `caffmob_draw/texture_library/grain.py` (`sync`) | `sync` continua abaixo de 1 ms por peça em material de imagem já montado | confidência | Custo por peça acima de 5 ms: a geração de armário grande passa a travar |
| W006 | `caffmob_draw/object_library/retexture.py` (`image_material`) | A projeção do material continua gravada e entra na chave de cache | redação | Dois materiais iguais com projeções diferentes, ou material reaproveitado com projeção errada |

## Observações

- W001, W002 e W003 nasceram de fatos medidos, não de regra 🟢 do `domain.md`: entram como vigilância de contrato do
  pacote porque uma atualização dos `.blend` de nós pode quebrá-los sem que nenhum teste puro perceba.
- W005 é limite de desempenho observado (0,18–0,38 ms por peça em 40 peças), não regra de negócio.
- O T001 não alterou nenhuma regra de `_reversa_sdd/domain.md`; por isso não há item de tipo `ausência` nesta rodada.

## Histórico de re-extrações

| Data | Extração | Resultado |
|------|----------|-----------|
| - | - | - |

## Arquivadas

| ID | Motivo | Data |
|----|--------|------|
| - | - | - |
