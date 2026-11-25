# Legacy impact: 024-materiais-uv-preferencias

> Data: 2026-11-25
> Feature: `024-materiais-uv-preferencias`
> Âncora: `_reversa_sdd/architecture.md` + `_reversa_sdd/domain.md` (cenário legado)
> Política de edição no momento da execução: `allowLegacyEdits: true`, `allowedPaths: ["***", "caffmob_draw/*", "tests/*"]`
> — o glob `"***"` libera o projeto inteiro na prática; os caminhos usados foram só `caffmob_draw/` e `tests/`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/armario_v2/props.py` | `armario_v2` (spec) | `delta-de-dados` | MEDIUM | `exibicao_versao` e `exibicao` na raiz; nenhum campo existente muda de tipo |
| `caffmob_draw/armario_v2/face_uv_core.py` | `armario_v2` (UV) | `componente-novo` | LOW | Núcleo puro que classifica EXTERNA/INTERNA/FITA |
| `caffmob_draw/armario_v2/mdf_core.py` | `armario_v2` (material) | `componente-novo` | LOW | Bytes determinísticos da textura MDF |
| `caffmob_draw/armario_v2/textura_padrao.py` | `armario_v2` (material) | `componente-novo` | MEDIUM | Imagem empacotada e nós do material da chapa |
| `caffmob_draw/armario_v2/build.py` | `armario_v2` (geração) | `regra-alterada` | HIGH | Chapa nasce com textura; `_uv_metros` delega ao núcleo de faces |
| `caffmob_draw/edgeband/build.py` | `edgeband` | `regra-alterada` | MEDIUM | Faixa ganha UV próprio (U comprimento, V espessura) |
| `caffmob_draw/hb_details.py` | `hb_details` | `regra-alterada` | HIGH | Fluxo de detalhes força `color_type = 'TEXTURE'` em vez de `'OBJECT'` |
| `caffmob_draw/ops.py` | preferências recomendadas | `regra-alterada` | HIGH | O controle de cor passa a aplicar `TEXTURE`; “Cursos 3D” intacto |
| `caffmob_draw/ui/view3d_sidebar.py` | barra lateral | `regra-alterada` | MEDIUM | Aviso de cor de objeto aceita `TEXTURE` |
| `caffmob_draw/__init__.py` | preferências | `regra-alterada` | MEDIUM | `exibicao_armario` acrescentado; `cabinet_color` preservado |
| `caffmob_draw/armario_v2/exibicao.py` | `armario_v2` (exibição) | `componente-novo` | HIGH | Variante pelo modo de vista existente + migração idempotente |
| `caffmob_draw/armario_v2/__init__.py` | `armario_v2` | `regra-alterada` | LOW | Módulo `exibicao` entra em `_MODULES` |
| `caffmob_draw/data/translations/*.json` | i18n | `delta-de-dados` | LOW | 10 chaves novas em pt_BR/en_US |

## Diff conceitual por componente

- **Material/UV**: `build.materiais` cria a chapa com `ShaderNodeTexImage` apontando para uma imagem 512² gerada em
  runtime e empacotada, com `Mapping` em `1/0,6 m` (o UV já é métrico). `build._uv_metros` deixa de usar “eixo
  dominante” e passa a consultar `face_uv_core`: as duas faces grandes viram EXTERNA/INTERNA (a interna espelha o U e
  avança uma espessura) e as quatro estreitas viram FITA. A faixa da fita recebe layer `UVMap` próprio.
- **Exibição**: `hb_details` e o diálogo recomendado aplicam `color_type = 'TEXTURE'`; o aviso da barra lateral só
  acusa quando a cor não é `OBJECT` nem `TEXTURE`. A preferência `exibicao_armario` escolhe “Somente textura” ou
  “Textura com linhas” e a variante é aplicada pelo modo de vista existente (`Scene.btm_view_mode` +
  `btm_view_lines` → `overlay.show_wireframes`).
- **Dados/migração**: `btm_armario.exibicao_versao` (0→1) e `exibicao`; um `load_post` `@persistent` migra cada raiz
  uma vez, garante a chapa padrão nas peças sem material e avisa uma vez por cena. Nada é apagado.

## Preservadas

- “Cursos 3D” (`turn_off_3d_cursor`, `ops.py:54`) e as demais opções do diálogo recomendado.
- `cabinet_color` e o `layout.prop` dele (`__init__.py:304`), lidos por `ops_placement.py:40` como `obj.color`.
- `show_legacy_libraries`, `panel_mode`, `stick_magnet`, `mobi_url`, cores de parede/porta/anotação/obstáculo.
- `Scene.btm_view_mode`, `btm_view_lines` e o controle “Sólido·Textura” da barra lateral.
- `hb_utils.set_layout_shading`, `hb_layouts` e `catalog/render_thumbnails.py` (fora do fluxo de detalhes).
- Material do usuário por peça (`btm_armario_parte.material`) e o contrato de chapas/corte.

## Modificadas

- `hb_details._setup_2d_view`: `color_type` `OBJECT` → `TEXTURE`.
- `ops.home_builder_OT_set_recommended_settings`: `turn_on_object_color_type` → `turn_on_texture_color_type`, com
  `'TEXTURE'`; rótulo “Turn On Texture Color Type - REQUIRED”.
- `view3d_sidebar`: aviso de cor de objeto agora aceita `TEXTURE`.
- `build.materiais`/`build._material`: chapa com imagem; `build._uv_metros`: UV por face.
- `edgeband.build._write`: layer `UVMap` na faixa.
