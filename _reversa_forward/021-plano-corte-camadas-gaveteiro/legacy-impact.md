# Legacy Impact: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Cenário: `legado` (âncora: `_reversa_sdd/architecture.md` + `_reversa_sdd/domain.md`)
> Política de edição do legado: `allowLegacyEdits: true`; `allowedPaths` incluindo `caffmob_draw/**`, `tests/**` e `"***"` (`.reversa/reversa-config.json`).

## Tabela de arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|-----------------|---------------------------------------------|------|------------|---------------|
| `caffmob_draw/cutting/opcut_core.py` | `cutting` | `componente-novo` | HIGH | Novo motor guilhotinado 2D offline compatível com OpCut (`greedy` e `forward_greedy`) |
| `caffmob_draw/cutting/module_list_core.py` | `cutting` | `componente-novo` | MEDIUM | Agrupamento hierárquico de peças por módulo, excluindo ferragens e itens fora do corte |
| `caffmob_draw/cutting/plan_export.py` | `cutting` | `delta-de-contrato-externo` | MEDIUM | Exportação atômica offline em SVG, HTML autocontido e PDF 1.4 puro |
| `caffmob_draw/cutting/plan_render.py` | `cutting` | `componente-novo` | LOW | Renderização RGBA interna para prévia de chapas no Blender |
| `caffmob_draw/cutting/ops_opcut.py`, `__init__.py` | `cutting` | `regra-nova` | MEDIUM | Operadores e painel UI do Plano de Corte OpCut + lista por módulo |
| `caffmob_draw/data/properties.py` | `data` | `delta-de-dados` | MEDIUM | Novas propriedades de piso (`floor_thickness`, `floor_thickness_direction`), parede (`default_wall_thickness`) e corte (`cutting_engine`, `cutting_group_by_module`, `cutting_preview_sheet_index`) |
| `caffmob_draw/data/layers.py` | `walls2d` / `data` | `componente-novo` | HIGH | Roteamento unificado de camadas `Arquitetura > Parede\|Piso\|Teto\|Aberturas` e `Marcenaria`, mais cálculo de faixa Z do piso (`DOWN`/`UP`) |
| `caffmob_draw/armario_v2/build.py` | `armario_v2` | `regra-alterada` | HIGH | Desacopla `e_raiz()` do nome da coleção via `btm_armario_v2_root` (com fallback legado) e direciona armários para `Marcenaria` |
| `caffmob_draw/armario_v2/drawer_detect_core.py`, `ops_drawer_convert.py`, `__init__.py` | `armario_v2` | `componente-novo` | HIGH | Analisador geométrico puro e operador não destrutivo "Converter em: Gaveteiro" sem bloqueio por peças faltantes |
| `caffmob_draw/stick/props.py`, `release_guard_core.py`, `link.py`, `magnet.py` | `stick` | `regra-alterada` | HIGH | Corrige ciclo infinito ao desgrudar armário e movê-lo para frente via `released_host_name` e guarda de histerese |
| `caffmob_draw/operators/floor_builder.py`, `walls.py`, `walls2d/apply.py`, `openings/sync.py` | `walls2d` / `openings` | `regra-alterada` | MEDIUM | Espessura direcional do piso (`DOWN`/`UP`) e vínculo automático às subcoleções de `Arquitetura` |
| `caffmob_draw/walls2d/ops_editor.py`, `ui/sidebar_build.py` | `walls2d` / `ui` | `regra-alterada` | MEDIUM | Controles rápidos de pé-direito, espessura padrão de parede e espessura/direção do piso na aba Construir/Ferramentas |
| `caffmob_draw/operators/ops_wall_extras.py`, `selection/lowered_wall_core.py`, `selection/classify.py` | `selection` / `operators` | `regra-alterada` | MEDIUM | Reconhecimento de proxy de parede rebaixada (`btm_is_lowered_wall` + `btm_lowered_wall_ref` + fallback legado) |
| `caffmob_draw/ui/context_menu.py` | `ui` | `regra-alterada` | MEDIUM | Exibe "Restaurar Parede" em paredes rebaixadas e submenu "Converter em:" (Gaveteiro / Armário) |
| `caffmob_draw/ui/header_collision.py`, `ui/__init__.py` | `collision` / `ui` | `regra-nova` | MEDIUM | Botão global de colisões no cabeçalho `VIEW3D_HT_header` sincronizado com `collision_global` e `block_penetration` |
| `caffmob_draw/texture_library/sync_missing.py`, `ops_sync_missing.py`, `__init__.py` | `texture_library` | `delta-de-contrato-externo` | MEDIUM | Detecção e re-download assíncrono de texturas perdidas com timeout 15 s, 2 retentativas e escrita atômica |
| `caffmob_draw/library_panel/style.py`, `ops_cabinet.py` | `library_panel` | `regra-alterada` | MEDIUM | "Criar Armário" abre diretamente o Construtor v2; `style.py` adota paleta oficial CAFFMob sem verde escuro legado |
| `caffmob_draw/data/translations/feature_021.json` | `data` | `regra-nova` | LOW | Catálogo bilíngue `pt_BR` e `en_US` com 90 strings novas cobrindo 100% da interface adicionada |

## Diff conceitual por componente

- **Produção (`cutting`):** passa a oferecer o otimizador guilhotinado 2D offline compatível com OpCut, agrupamento de peças por módulo, prévia RGBA interna e exportação atômica em HTML/SVG/PDF, preservando `nesting.py` como opção clássica.
- **Organização de cena (`walls2d`, `operators`, `openings`, `armario_v2`):** todos os elementos arquiteturais vão para `Arquitetura > Parede|Piso|Teto|Aberturas` e armários/gaveteiros vão para `Marcenaria`; o piso suporta espessura para baixo (−Z) ou para cima (+Z).
- **Posicionamento (`stick`):** `release()` agora registra `released_host_name` e marca `opt_out` ao desgrudar manualmente de uma parede, enquanto `magnet.find()` respeita a banda de histerese para impedir o reacoplamento infinito.
- **Seleção e paredes (`selection`, `ops_wall_extras`, `ui/context_menu`):** o proxy `<parede>_Rebaixada` é resolvido de volta para a parede original, habilitando "Restaurar Parede" diretamente ao clicar nele.
- **Mobiliário e Biblioteca (`library_panel`, `armario_v2`):** "Criar Armário" abre direto o Construtor v2, a biblioteca adota a paleta CAFFMob (sem o verde escuro legado) e o menu de contexto ganha "Converter em: Gaveteiro" com detecção geométrica tolerante a peças faltantes.
- **Colisão e Texturas (`ui/header_collision`, `texture_library`):** controle global de colisão no header da Viewport 3D e sincronização assíncrona de texturas perdidas no painel de Texturas/Materiais.

## Preservadas

- `_reversa_sdd/domain.md#2.3` (`R-09`, `R-10`): algoritmo clássico `cutting/nesting.py` preservado como opção `LEGACY_SHELF`.
- `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-01` a `RN-WALLS2D-15`): matemática de face interna, esquadria, limites de pé-direito (0,5–10 m) e mureta (1100 mm) intactas.
- `_reversa_sdd/domain.md#collision` (`RN-COLLISION-01` a `RN-COLLISION-12`): regras de tolerância 1 mm, classificação e escopo de colisão preservadas.
- `_reversa_sdd/domain.md#stick` (`RN-STICK-01` a `RN-STICK-09`, `RN-STICK-13` a `RN-STICK-16`): vínculo de face, projeção no plano e prévia preservados.
- `_reversa_sdd/addenda/017-construtor-armario-v2.md`: motor de chapas v2, contrato de chapas, exclusão de ferragens do corte e compatibilidade com arquivos `.blend` anteriores preservados.

## Modificadas

- `_reversa_sdd/domain.md#2.3` (`R-09`, `R-10`): plano de corte padrão passa a usar o otimizador guilhotinado compatível com OpCut (`opcut_core.py`) com lista agrupada por módulo e exportação HTML/SVG/PDF.
- `_reversa_sdd/domain.md#collision` (`RN-COLLISION-08`): `collision_global` ganha botão global direto no cabeçalho `VIEW3D_HT_header` sincronizado com `block_penetration`.
- `_reversa_sdd/domain.md#stick` (`RN-STICK-10`, `RN-STICK-12`): desgrudar registra `released_host_name` e suprime reacoplamento imediato pelo ímã ao mover para frente.
- `_reversa_sdd/domain.md#selection` (`RN-SELECTION-01`): classificador passa a reconhecer proxies de parede rebaixada (`btm_is_lowered_wall` / `<parede>_Rebaixada`) como `WALL`.
- `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-16`): pisos e tetos passam a ser roteados para `Arquitetura > Piso` e `Arquitetura > Teto`, com espessura direcional (`DOWN`/`UP`) no piso.
- `_reversa_sdd/addenda/017-construtor-armario-v2.md`: coleção padrão do armário v2 muda de `CAFFMob Armário v2` para `Marcenaria`, com identificação da raiz por `btm_armario_v2_root` (+ fallback legado).
- `_reversa_sdd/code-analysis.md#17. Módulo library_panel`: "Criar Armário" abre diretamente o Construtor v2 e `library_panel/style.py` migra para a paleta oficial CAFFMob.
