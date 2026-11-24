# Adendo: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Cenário: `legado`
> Extração de referência: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md`

## Vigência

Vigente desde 2026-11-24.

## Resumo da entrega

Esta entrega consolida dez melhorias de produtividade, organização de cena e produção no CAFFMob Draw: lista de peças agrupadas por módulo e motor de plano de corte guilhotinado 2D offline compatível com OpCut (com visualização interna no Blender e exportação atômica em HTML, SVG e PDF), botão "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais, botão global de colisões no cabeçalho da Viewport 3D, organização unificada nas camadas `Arquitetura > Parede|Piso|Teto|Aberturas` e `Marcenaria`, direção de espessura do piso (`Para baixo` / `Para cima`), padrões rápidos de pé-direito e parede na aba Construir/Ferramentas consumidos pelo Editor de Parede, correção do ciclo infinito ao desgrudar armário, acesso direto ao Construtor de Armários v2 em "Criar Armário" com migração da biblioteca para a paleta oficial CAFFMob, reconhecimento de paredes rebaixadas com ação "Restaurar Parede" e submenu "Converter em: Gaveteiro" com detecção geométrica tolerante a peças faltantes e abertura do editor.

Ações concluídas: **32 de 32** (`[X]`), sem nenhuma aberta.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Limites e organização | `componente-novo` | Nascem os núcleos puros `cutting/opcut_core.py`, `cutting/module_list_core.py`, `cutting/plan_render.py`, `data/layers.py`, `armario_v2/drawer_detect_core.py`, `stick/release_guard_core.py`, `selection/lowered_wall_core.py` e os operadores `cutting/ops_opcut.py`, `armario_v2/ops_drawer_convert.py`, `ui/header_collision.py` e `texture_library/ops_sync_missing.py` |
| `_reversa_sdd/architecture.md` | Persistência e unidades | `delta-de-dados` | `Scene.btm_settings` recebe `floor_thickness`, `floor_thickness_direction`, `default_wall_thickness`, `cutting_engine`, `cutting_group_by_module` e `cutting_preview_sheet_index`; `Object.btm_stick` ganha `released_host_name`; objetos recebem `btm_armario_v2_root`, `btm_is_lowered_wall`, `btm_lowered_wall_ref`, `btm_floor_thickness`, `btm_floor_direction` e `btm_gaveteiro_meta` |
| `_reversa_sdd/architecture.md` | Integrações e distribuição | `delta-de-contrato-externo` | Exportação local atômica em HTML, SVG e PDF vetorial puro (`cutting/plan_export.py`) e re-download HTTP assíncrono de texturas perdidas com timeout de 15 s e até 2 retentativas (`texture_library/sync_missing.py`) |
| `_reversa_sdd/domain.md` | 2.3 Regras de Otimização de Plano de Corte | `regra-alterada` | O motor padrão de plano de corte passa a ser o guilhotinado 2D offline compatível com OpCut (`forward_greedy`/`greedy`), mantendo `nesting.py` como opção legada; lista de peças passa a suportar agrupamento hierárquico por módulo sem ferragens |
| `_reversa_sdd/domain.md` | collision (`RN-COLLISION-08`) | `regra-alterada` | A chave global `collision_global` ganha botão global direto no cabeçalho `VIEW3D_HT_header` sincronizado com `block_penetration` e com remoção limpa no `unregister` |
| `_reversa_sdd/domain.md` | stick (`RN-STICK-10`, `RN-STICK-12`) | `regra-alterada` | `stick/link.py:release()` grava `released_host_name` (e `opt_out` quando hospedeiro for parede) e `stick/magnet.py` suprime o reacoplamento imediato na zona de histerese, eliminando o ciclo infinito ao mover para frente |
| `_reversa_sdd/domain.md` | selection (`RN-SELECTION-01`) | `regra-alterada` | O classificador reconhece proxies de parede rebaixada (`btm_is_lowered_wall` / `<parede>_Rebaixada`) como `WALL` resolvendo para a parede original, exibindo "Restaurar Parede" no menu de contexto |
| `_reversa_sdd/domain.md` | walls2d (`RN-WALLS2D-16`) | `regra-alterada` | Paredes, pisos, tetos e aberturas passam a ser roteados para `Arquitetura > Parede\|Piso\|Teto\|Aberturas`; pisos suportam espessura configurável `DOWN` (−Z) ou `UP` (+Z), e a aba Construir/Ferramentas expõe padrões rápidos consumidos pelo Editor de Parede |
| `_reversa_sdd/addenda/017-construtor-armario-v2.md` | Impacto por artefato da extração | `regra-alterada` | Armários v2 e gaveteiros convertidos passam a ser vinculados à coleção `Marcenaria`, e `e_raiz()` passa a usar a flag explícita `btm_armario_v2_root` com fallback para a coleção legada `CAFFMob Armário v2` |
| `_reversa_sdd/code-analysis.md` | 17. Módulo `library_panel` | `regra-alterada` | "Criar Armário" abre diretamente o Construtor de Armários v2 sem desvio pela galeria legada, e `library_panel/style.py` adota a paleta oficial CAFFMob sem os tons verde-escuros legados |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | `regra-nova` | Menu de contexto (botão direito e toque longo) ganha submenu "Converter em:" com "Gaveteiro", detectando as 6 peças da gaveta + ferragens em malha única ou objetos separados, sem nunca bloquear por peças faltantes, perguntando se deseja completá-las e abrindo o editor |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | `regra-nova` | Catálogo bilíngue `caffmob_draw/data/translations/feature_021.json` com 90 chaves em `pt_BR` e `en_US` cobrindo 100% da nova superfície de interface |

## Regras sob vigilância

`W001`, `W002`, `W003`, `W004`, `W005`, `W006` e `W007`, em `_reversa_forward/021-plano-corte-camadas-gaveteiro/regression-watch.md`.

## Fontes

- `_reversa_forward/021-plano-corte-camadas-gaveteiro/legacy-impact.md`
- `_reversa_forward/021-plano-corte-camadas-gaveteiro/regression-watch.md`
- `_reversa_forward/021-plano-corte-camadas-gaveteiro/requirements.md`
- `_reversa_forward/021-plano-corte-camadas-gaveteiro/progress.jsonl`
- `_reversa_forward/021-plano-corte-camadas-gaveteiro/actions.md`
