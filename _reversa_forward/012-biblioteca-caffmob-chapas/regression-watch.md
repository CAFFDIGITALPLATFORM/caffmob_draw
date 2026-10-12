# Regression watch: 012-biblioteca-caffmob-chapas

> Gerado por `/reversa-coding` em 2026-10-09. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **Só armários CAFFMob na interface** (`legacy/gate.py`): frameless, face frame, closets e a biblioteca de molduras
  só aparecem com a preferência `show_legacy_libraries`. Uma re-extração que volte a ver as galerias herdadas em
  Inserir, os modos de seleção herdados ou o submenu do armário herdado com a preferência desligada é regressão. 🟢
- **Biblioteca CAFFMob** (`library_panel/`): painel no canto superior esquerdo da parte visível da viewport, sempre
  desenhado; Criar armário, categorias fixas (Cozinha → COZ, Banheiro → BAN, Sala → SAL, Home office → ESC) e do
  usuário (`categories.json`), Criar categoria; modelos prontos de `data/library_models.json`. 🟢
- **Armário pelo padrão** (`operators/cabinet_builder.py`, `standards/cabinet_defaults.py`): medidas externas e
  chapas da linha; os 0,8/0,7/0,55 são só fallback sem padrão. 🟢
- **Montagem** (`cabinet_editor/structure.py#layout`, `carcass_lengths`): lateral passante (padrão) ou base passante,
  na malha e na lista de corte; no padrão (`assembly`), no módulo e no Promob (`CAFF_MONTAGEM`). 🟢
- **Aplicar o padrão** (`operators/ops_standards.py`, `standards/sync.py`): grava e ativa; as duas perguntas decidem;
  só módulos CAFFMob mudam; "Incluir medidas manuais" saiu da tela. O RN-23 da 001 (medidas manuais preservadas)
  vive agora como "padrão próprio" e na 2ª pergunta. 🟢
- **Duas etapas de desfazer** quando as duas perguntas são respondidas com Sim (uma por pergunta). 🟡
- **Conversão** (`legacy/convert.py`, `legacy/groups.py`): armário herdado → módulo CAFFMob na mesma caixa, com
  relatório de perdas (gavetas, frentes especiais, agregados) e uma etapa de desfazer; grupos salvos → módulos em
  Geral, um por armário. 🟢
- **Modos de seleção e `product_tab` neutralizados no `load_post`** com a porta fechada; os itens dos enums herdados
  ficam até a remoção do código (RN-14). 🟡
- **Remoção em lote** em `aggregates/ops_aggregate.delete_components` (`bpy.data.batch_remove`), usada também pela
  exclusão em profundidade da 011. 🟢
- **Gavetas** não existem no módulo CAFFMob: o balcão gaveteiro e a conversão de gavetas ficam para a feature 013. 🟡

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| — | — | nenhum watch item na tabela principal; nada a verificar |

## Arquivadas
