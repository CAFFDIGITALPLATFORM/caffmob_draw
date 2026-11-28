# Adendo: 080-edicao-medidas-reais

- **Feature:** 080, medidas reais, edição segura de módulos e confirmação de cota
- **Data:** 2026-11-27 (replanejamento; a onda A é de 2026-10-31)
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)
- **Base:** `master` `92b13674` (1.36.1)
- **Entrega desta rodada:** A2 (faixa de entrada do master) + onda B (token de cota), manifesto **1.37.0**. A onda A
  (medida física, assar escala, transação, substituição) já estava mergeada em `ed367a8a` (PR #42, 1.25.0). A onda B
  foi recuperada do commit `03ca710a`, cujo pai é exatamente `92b13674`.
- **Artefatos da feature:** `caff_systems/.claude/worktrees/065-studio-mobi-e-blender/_reversa_forward/080-edicao-medidas-reais/`

## Vigência

Vigente desde 2026-11-27. Onde este adendo divergir do `domain.md`, vale este texto até a próxima extração.

## 1. RN-SELECTION-11 — faixa de entrada é só a do master (A2, D-15)

Antes da A2, a entrada dimensional cruzava os limites gerais com o `hard_min/hard_max` da propriedade do gerador
convertido pela escala dos ancestrais; na prática, o BTM ficava restrito a 0,1–3,0 m de largura/altura e 0,1–2,0 m de
profundidade. Isso contradizia a faixa documentada no master.

Agora:

- A faixa aceita na entrada é `selection/editing.py:LIMITS`: largura e altura de **0,01 a 10 m**, profundidade de
  **0,005 a 10 m**, inclusive. Não existe faixa local mais estreita.
- `module_resize.physical_ranges` (o que o painel e o editor exibem em “faixa: min – max”) e `module_resize._validate`
  chamam `module_geometry.physical_range`/`check_value` com `param_range=None`.
- `module_geometry` mantém o parâmetro `param_range` apenas como capacidade de cálculo: quem o usa é o diagnóstico da
  recusa, não a validação de entrada.
- O que o gerador não representa continua recusado pela **pós-condição** (D-07, diferença > 0,1 mm por eixo), com
  rollback completo. Nunca há arredondamento, clamp ou sucesso aparente.

Mensagem da recusa da pós-condição (`module_resize._not_represented`): nomeia o campo, o valor pedido, o produzido, a
faixa aceita do master e, quando a propriedade declara limite finito, a faixa do gerador convertida pela escala dos
ancestrais. Exemplo real do ensaio: “pedido 3500 mm, produzido 3000 mm. A faixa aceita é 10 mm a 10000 mm; o gerador
declara 100 mm a 3000 mm.”

Nenhuma propriedade mudou de `min`/`max`: a alternativa de alargar o `hard_min/hard_max` do BTM foi descartada para não
fazer o gerador produzir geometria degenerada.

## 2. HYCE-v002 — confirmação de cota pelo registro mostrado (onda B, D-13)

`overlays/cota_token.py` (puro, sem `bpy`) guarda a identidade e a pose completas do que foi **mostrado**:

- alvo móvel: `session_uid`, `matrix_world` 4x4, escopo (`btm_target.cota_scope`), `session_uid` do pai (0 sem pai) e
  `scene.as_pointer()`;
- referência por lado: objeto (`session_uid`, `matrix_world`, caixa mínima/máxima no mundo), Piso ou Teto
  (`ceiling_height`).

Tolerâncias (RNF-02): translação 1e-6 m (0,001 mm); componentes da 3x3 e da caixa 1e-6. Renomear não invalida (o nome
não entra no token); apagar e recriar com o mesmo nome invalida (uid muda).

- `side_cotas._compute` devolve também `token`; `check_unchanged` aceita o registro mostrado e o lado, e compara com um
  cálculo novo feito fora do desenho e dos getters.
- `side_cotas.shown(context)` expõe o último cálculo sem recalcular; `apply_fixed` tira a diferença **do registro
  mostrado**, confere o token antes de mover e refaz o cálculo depois de mover (a próxima confirmação compara contra a
  pose que a tela vai mostrar).
- O popup guarda o registro em `_popup[0]` no `invoke` e o passa ao `execute`; o campo do painel
  (`ui/object_properties._fixed_setter`) passa `side_cotas.shown(context)`. Popup e campo recusam o mesmo conjunto de
  mudanças, com mensagens traduzidas em `data/translations/cotas_080.json`.

Guardrails inalterados: nada é avaliado em getter nem em draw; os campos virtuais continuam sem `ANIMATABLE`; a
quarentena de drivers no load segue; `guard.reconfigure` continua sem veto geral por colisão (RN-07/RN-10 da feature).

## 3. Dados e compatibilidade

Nenhuma propriedade nova é persistida; o token de cota vive só em memória e some no reload. Não há migração: abrir um
`.blend` antigo não regrava nada. A2 muda apenas a faixa aceita na próxima edição confirmada. Contrato
`caffmob.ambiente/v2`, envio ao MOBI, importador `.promob` e pacote do addon: sem mudança de formato.

## 4. Verificação

- Puros: `test_080_module_geometry`, `test_080_bake_plan` (inclui `MasterRangeEntryTest`, com guarda estática de que a
  transação não volta a usar a faixa do gerador na entrada) e `test_080_cota_token` (11 testes).
- Headless: `tests/blender_080_medidas_reais.py` (163 verificações, inclui `case_master_range`) e
  `tests/blender_080_cotas.py` (23 verificações). `blender_080_cotas.py` entrou na lista padrão `BLENDER_SCRIPTS` de
  `tools/portao.sh`.
- `python3 docs/rag/tools/check_api.py`: sem referências desconhecidas na API 5.2.
- Traduções novas da A2 em `data/translations/medidas_reais_080.json` (pt_BR, en_US, es_ES); `test_i18n_coverage` verde.
- QA visual do titular: `onboarding.md` §2.7 (A2) e §3 (cotas).
