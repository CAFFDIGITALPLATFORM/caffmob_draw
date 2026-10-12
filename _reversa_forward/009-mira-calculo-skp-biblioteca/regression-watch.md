# Regression watch: 009-mira-calculo-skp-biblioteca

> Gerado por `/reversa-coding` em 2026-10-09. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **Lápis do editor de paredes (002):** o Enter segue a direção travada, que só muda por clique ou pelas setas
  (`walls2d/ops_editor.py`, `walls2d/direction.py`). Uma re-extração não deve voltar a descrever "o Enter usa a
  direção do cursor". 🟢
- **Mira com alinhamento X/Y:** trava a 8 px na tela, Shift desliga, e a cadeia de travas é ímã → vértice →
  alinhamento → ortogonal → grade (`resolve_point`). 🟢
- **Medida com conta** (`data/expr.py`): `+ - * /`, parênteses e unidade por número, sem `eval`. A PL-03 da 001
  mudou: `3/4` é conta (0,75 mm); pés e polegadas continuam recusados. 🟢
- **SketchUp pelo OpenSKP** em todas as plataformas, com as wheels da extensão. `.skp` deixou de ser formato recusado
  pelo "Importar modelo" da 003. 🟢
- **Biblioteca de objetos:** os itens embutidos nunca têm a origem "3D Warehouse" (`build.py`, `store.check_bundled`);
  os do usuário ficam em `extension_path_user(..., "object_library")`. 🟢
- **`.gitignore`:** `caffmob_draw/wheels/` é versionada (exceção à regra `wheels/`). 🟡
- **Arquivos de 2013 a 2020** que o OpenSKP não abre (cerca de 1 em 4) mostram o motivo e a alternativa. 🟡

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| — | — | nenhum watch item na tabela principal; nada a verificar |

| Data | Resultado | Observação |
|------|-----------|------------|

## Arquivadas

| ID | Arquivada em | Motivo |
|----|--------------|--------|
