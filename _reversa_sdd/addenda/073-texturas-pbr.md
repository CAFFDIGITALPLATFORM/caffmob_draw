# Adendo: 073-texturas-pbr

- **Feature:** 073, texturas PBR dentro do CAFFMob Draw para parede, piso e metais
- **Data:** 2026-10-27
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)
- **Entrega:** PR #38, mesclada em `565e9789` e publicada como 1.23.0 nas 5 plataformas. O lado do MOBI está em
  `caff_systems` (#361, `bb3a115aa`).
- **Artefatos da feature:** `caff_systems/.claude/worktrees/065-studio-mobi-e-blender/_reversa_forward/073-texturas-pbr/`

## Vigência

Vigente desde 2026-10-27.

## Resumo da entrega

O addon passa a levar no pacote 26 texturas PBR 1K, CC0 do ambientCG, em `caffmob_draw/pbr/` (59 MB), com
`manifest.json`. Cada textura tem slug, UUID v5, tom, palavras do nome, tamanho real em mm, origem e sha256 de cada
mapa. Elas aparecem na biblioteca, na seção "Revestimentos e metais", como já baixadas, e funcionam sem rede.

Os dois construtores de material ligam relevo, rugosidade e metálico no mesmo vetor da cor. O importador do Promob
casa o nome do material com o manifesto e grava `tipo='textura'` no documento v2, com `escala_mm` real. O relatório
de importação traz a contagem e os avisos de aproximação. O pacote por plataforma passou de ~107 para ~168 MB.

**Estado: sincronização parcial, 37 de 38 ações concluídas.** A aberta é a T035, o QA do titular. Em 2026-10-27 ele
confirmou que as texturas de piso e parede aparecem na biblioteca. Ainda faltam a importação de um `.promob` sem
internet e o envio ao MOBI.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | [Integrações e distribuição](../architecture.md#integrações-e-distribuição) | regra-alterada | O empacotamento verifica também `pbr/` (`build.py` `pbr_problems`): todo arquivo registrado no manifesto, CC0, sha256 conferido e `LICENSES/CC0-1.0.txt` no pacote; o manifesto declara `SPDX:CC0-1.0`; a regra da 014 (`texture_problems`) continua |
| `_reversa_sdd/architecture.md` | [Fluxos entre componentes](../architecture.md#fluxos-entre-componentes) | regra-alterada | O catálogo de texturas tem uma segunda origem, o pacote (fabricante `caffmob-pbr`); `catalog.item(uuid)` prefere a textura do pacote à do MOBI, e `downloads.cached` devolve o arquivo local sem rede |
| `_reversa_sdd/architecture.md` | [Fluxos entre componentes](../architecture.md#fluxos-entre-componentes) | regra-alterada | Importador do Promob (`promob/para_v2.py`): chapa de fabricante → textura do pacote (exata pela palavra, senão pelo tom, senão a `padrao`) → cor pelo nome → cor da classe; parede, piso e laje casados viram `tipo='textura'` |
| `_reversa_sdd/architecture.md` | [Persistência e unidades](../architecture.md#persistência-e-unidades) | delta-de-dados | Documento v2 vindo do Promob passa a ter materiais `textura` (`textura_id` UUID v5, `escala_mm`, nome original); o relatório ganha `texturas {com_textura, aproximadas, em_cor}`; material do complemento guarda `btm_promob_origem` |
| `_reversa_sdd/object_library/requirements.md` | retextura | regra-alterada | `retexture.image_material` liga os mapas PBR quando o `texture_id` é do pacote, no reuso e no material novo; a retextura continua afetando a cena e não a biblioteca (RN-OBJECT_LIBRARY-03) |
| `_reversa_sdd/library_panel/requirements.md` | árvore de texturas | regra-alterada | "Revestimentos e metais" na árvore, com tradução; a textura do pacote aparece no estado de baixada |
| `_reversa_sdd/architecture.md` | [Limites e organização](../architecture.md#limites-e-organização) | componente-novo | `texture_library/pbr_core.py` (manifesto, UUID, validação, casamento), `texture_library/pbr.py` (`attach`), `tools/baixar_pbr.py` (download, sha256, folha de aprovação), `caffmob_draw/pbr/` e `LICENSES/CC0-1.0.txt` |
| n/a | `mobi/materiais_v2.py` (cena v2) | regra-alterada | `_aplicar_imagem` liga os mapas PBR no vetor do UV em mm; antes ligava só a cor |

A extração não tem pasta própria para `texture_library/` nem para `promob/`. A 071 ainda não foi sincronizada. Por
isso as linhas desses componentes apontam para a arquitetura geral. O `legacy-impact.md` da feature cita
"`texture_library/` RN-13", mas essa seção não existe na extração. A regra que ela descreve, textura baixada que
funciona sem internet, está registrada aqui, na segunda linha da tabela.

## Regras sob vigilância

W001 a W006, em `caff_systems/.claude/worktrees/065-studio-mobi-e-blender/_reversa_forward/073-texturas-pbr/regression-watch.md`.
W001 a W004 e W006 cobrem o addon.

## Fontes

- `_reversa_forward/073-texturas-pbr/legacy-impact.md` (na worktree 065 de `caff_systems`)
- `_reversa_forward/073-texturas-pbr/regression-watch.md`
- `_reversa_forward/073-texturas-pbr/requirements.md`
- `_reversa_forward/073-texturas-pbr/progress.jsonl`
- `_reversa_forward/073-texturas-pbr/onboarding.md` (as 26 texturas escolhidas)
- `caff_systems:_reversa_sdd/addenda/073-texturas-pbr.md` (adendo da plataforma)
