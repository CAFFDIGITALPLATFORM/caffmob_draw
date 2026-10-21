# Adendo: 066-reparo-do-addon-caffmob

- **Feature:** 066, reparo do addon CAFFMob Draw (colisão, portas, armário autoral e revestimentos)
- **Data:** 2026-10-21
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)
- **Entrega:** PRs #12 (onda 1, 1.3.0), #13 (onda 2, 1.4.0), #14 e #15 (onda 3, 1.5.0) e #16 (onda 4, 1.6.0),
  empilhadas nessa ordem

## Vigência

Vigente desde 2026-10-21.

## Resumo da entrega

A feature 066 converte em reparos as 92 ações da análise "CAFFMob: portas e revestimentos" (RF-001 a RF-092).

- **Colisão:** deixa de ser relatório e passa a ser guarda. O movimento para no primeiro contato, em silêncio, e
  "Impedir atravessamento" vem ligado também em arquivos antigos.
- **Medidas:** ganham as cotas laterais.
- **Portas de ambiente:** passam a ter vínculo por uid, limite de giro por modelo e transferência para outra parede.
- **Armário montado à mão:** pode ser adotado como componente, com portas próprias, biblioteca (manifesto 1.2.0) e
  regras dimensionais sem escala.
- **Revestimentos:** pacote novo para parede e teto, que contorna os vãos e sincroniza de forma incremental.
- **MOBI:** nada vai a ele; o contrato fica intocado (RN-16).

Ações concluídas: **91 de 95**. As 4 abertas (T088, T090, T092, T094) são os aceites do titular no Blender, uma por
onda.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|---|---|---|---|
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Limites e organização | componente-novo | Três pacotes novos: `cladding/` (revestimentos), `collision/guard.py` (guarda ao vivo) e `stable_id.py` (uid estável). |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Fluxos entre componentes | regra-alterada | Todo caminho de movimento passa pelo guarda (handler de depsgraph, `load_post`, `undo_post`, `redo_post`). |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Limites e organização | componente-extinto | `collision/overlay.py` e `collision/stale.py` foram removidos; nada é desenhado por contato. |
| `_reversa_sdd/collision/requirements.md` | Visão Geral | regra-alterada | Impedir sobreposição durante o arraste entrou no escopo; a lista de colisões virou diagnóstico técnico calculado sob pedido. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-COLLISION-08 | regra-alterada | Leia `block_penetration` (ligado por padrão) no lugar de `collision_global`, que fica oculta. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-COLLISION-09 | regra-removida | Não existe mais o estado "desatualizado" do painel. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-MOVE_OVER-09 | regra-removida | O segundo Confirmar não grava sobreposto: a pose é limitada. |
| `_reversa_sdd/move_over/design.md` | F-05 `overlapping()` | regra-alterada | Todo corpo físico é obstáculo, não só módulos reconhecidos. |
| `_reversa_sdd/measure/` | (componente) | componente-novo | Até duas cotas laterais pela vista (`measure/side.py`, `overlays/side_cotas.py`), que suprimem anterior e posterior. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-OPENINGS-09 | regra-alterada | O limite de giro é `swing_limit` por porta, 90° por padrão e até 180°. |
| `_reversa_sdd/domain.md` | Regras de Snapping e Movimentação de Aberturas (2.2), R-07; RN-OPENINGS-11 | regra-alterada | A porta troca de parede depois da inserção, por "Mover para outra parede", com um Desfazer. |
| `_reversa_sdd/openings/design.md` | `sync.py` (`_remember`) | regra-alterada | A abertura é guardada por `leaf_index` em graus, e o recorte é achado por `m.object == cage`, nunca pelo nome. |
| `_reversa_sdd/data-dictionary.md` | `btm_opening_real` | delta-de-dados | Campos novos: `uid`, `host_wall`, `swing_limit`, `corner_ref` e `corner_dist_mm`; migração idempotente no `load_post`. |
| `_reversa_sdd/data-dictionary.md` | Cena (`btm_settings`) | delta-de-dados | Campos novos: `block_penetration` e `show_side_dimensions`. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-AGGREGATES-03 | regra-alterada | O converter e o grupo aceitam `MEMBER_TYPES` (malha, curva, texto, superfície, empty e luz); só `BODY_TYPES` contam na caixa e na colisão. |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas, RN-SELECTION-04 | regra-alterada | A peça de armário autoral sobe até a raiz `AUTHORED` antes da regra do grudado ou agregado. |
| `_reversa_sdd/aggregates/design.md` | `leaf.py` (pivô) | regra-alterada | O pivô da folha é achado pela hierarquia, e a migração converte o pivô gravado por nome. |
| `_reversa_sdd/aggregates/` | (componente) | componente-novo | Armário autoral: `btm_authored` e `btm_member`; operadores para adotar, para os membros e para a porta do armário; `front_kind`. |
| `_reversa_sdd/inspection/` | Tipos de frente | regra-nova | `SLIDING` entra no enum, e a frente é chaveada por uid. |
| `_reversa_sdd/customize/design.md` | Manifesto | delta-de-contrato-externo | `caffmob_draw.user-module` 1.2.0 só para AUTHORED; nativos continuam em 1.1.0. |
| `_reversa_sdd/customize/design.md` | `library_io` | regra-nova | Salvar o autoral fecha as folhas num `try/finally` e mantém a cena igual; inserir renova uids e refs e entra com as folhas fechadas. |
| `_reversa_sdd/customize/` | Adaptadores | componente-novo | `adapters/authored.py`: a personalização paramétrica é recusada com motivo (RN-10). |
| `_reversa_sdd/selection/` | Dimensões (`resize.py`, `editing.py`) | regra-alterada | O AUTHORED redimensiona por regras (`aggregates/rules.py`, `stretch.py`), por translação de vértices, sem escala. |
| `_reversa_sdd/selection/` | Dimensões | regra-alterada | A medida que faria penetrar volta ao valor anterior, em silêncio. |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Limites e organização | componente-novo | `cladding/` com núcleo puro, presets, controlador `btm_cladding`, região, gerador, sincronização, material e adoção. |
| `_reversa_sdd/openings/` | Transferência | regra-alterada | Mover a porta sincroniza o revestimento das duas paredes no mesmo Desfazer. |
| `_reversa_sdd/deployment.md` | Versão | delta-de-contrato-externo | Versões 1.3.0, 1.4.0, 1.5.0 e 1.6.0, uma por onda. |

## Regras sob vigilância

W001 a W018, em `caff_systems:_reversa_forward/066-reparo-do-addon-caffmob/regression-watch.md`, na worktree
`.claude/worktrees/065-studio-mobi-e-blender`.

## Fontes

Os artefatos ficam em `caff_systems`, na worktree `.claude/worktrees/065-studio-mobi-e-blender`:

- `_reversa_forward/066-reparo-do-addon-caffmob/legacy-impact.md`
- `_reversa_forward/066-reparo-do-addon-caffmob/regression-watch.md`
- `_reversa_forward/066-reparo-do-addon-caffmob/requirements.md`
- `_reversa_forward/066-reparo-do-addon-caffmob/progress.jsonl`
- `_reversa_forward/066-reparo-do-addon-caffmob/interfaces/user-module-file-1.2.0.md`
