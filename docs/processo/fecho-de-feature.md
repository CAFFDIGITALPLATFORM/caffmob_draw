# Fecho de feature: versão e nota de release

Etapa obrigatória do ciclo forward, criada em 2026-11-25 porque a `1.27.0` ficou congelada por cinco features
(020 a 024) enquanto o código mudava.

## Quando roda

Ao fechar uma feature do `_reversa_forward/` — junto com `legacy-impact.md`, `regression-watch.md` e a última linha do
`progress.jsonl`, antes de considerar a entrega concluída.

## Passos

1. **Versão:** `caffmob_draw/blender_manifest.toml` recebe **uma minor por feature entregue** (`1.32.0` → `1.33.0`).
   Patch só em correção que não entrega recurso novo.
   ```bash
   grep '^version' caffmob_draw/blender_manifest.toml
   ```
2. **Nota de release:** seção da versão no `CHANGELOG.md`, com o que entrou, os arquivos de referência e quais
   features ela cobre. O cálculo da numeração fica escrito ali para a próxima rodada conferir.
3. **Tag:** `git tag -a vX.Y.Z -m "<resumo>"`, criada localmente. Publicar (`git push --tags`) só com autorização do
   titular.
4. **Registro:** linha no `progress.jsonl` da feature com `"action": "VERSION"`, versão anterior, nova e arquivos
   tocados.
5. **Pendências:** feature pausada (só `requirements.md`) não conta como entrega e não entra no cálculo; registre isso
   na nota de release.

Se o manifesto já estiver à frente do `CHANGELOG.md`, corrija a nota antes de criar a tag.

## Histórico

| Versão | Data | Features cobertas |
|---|---|---|
| 1.32.0 | 2026-11-25 | 020, 021, 022, 023, 024 (a 019 segue pausada) |
| 1.27.0 | 2026-11-23 | 018 |
