# Adendo: Materiais, UV por face e preferências de exibição do armário

> Identificador: `024-materiais-uv-preferencias`
> Data: `2026-11-26`
> Cenário: `legado`
> Extração de referência: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md`

## Vigência

Vigente desde 2026-11-26.

## Resumo da entrega

O armário v2 deixou de nascer com cor de objeto e passou a nascer com a textura padrão de MDF claro: a chapa recebe
uma imagem 512² gerada em runtime e empacotada, o UV é métrico e classificado por face (EXTERNA, INTERNA e FITA), e a
fita de borda ganhou UV próprio (U no comprimento, V na espessura). O fluxo de detalhes e as opções recomendadas
passaram a forçar `color_type = 'TEXTURE'` sobre `shading.type = 'SOLID'`, a opção "Cor por objeto" virou "Textura" com
as variantes "Somente textura" e "Textura com linhas" (via `overlay.show_wireframes`), e "Cursos 3D" foi preservado.
Cenas e armários antigos migram uma única vez por `exibicao_versao`, sem apagar material do usuário.

Ações concluídas: **17 de 17** (`[X]` em `todo.md`), sem nenhuma aberta.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Persistência e unidades | delta-de-dados | `armario_v2/props.py` grava `exibicao_versao` e `exibicao` na raiz do armário; nenhum campo existente muda de tipo |
| `_reversa_sdd/architecture.md` | Limites e organização | componente-novo | Nascem `armario_v2/face_uv_core.py`, `armario_v2/mdf_core.py`, `armario_v2/textura_padrao.py` e `armario_v2/exibicao.py` |
| `_reversa_sdd/architecture.md` | Fluxos entre componentes | regra-alterada | `exibicao` entra em `_MODULES` do armário v2; o `load_post` `@persistent` migra a cena e é removido no `unregister()` |
| `_reversa_sdd/architecture.md` | Integrações e distribuição | delta-de-dados | A imagem do MDF é gerada em runtime e empacotada; o manifesto da extensão vai a `1.32.0` (a 024 viaja no pacote) |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | `build.materiais` dá textura à chapa e `build._uv_metros` deixa o "eixo dominante" e classifica EXTERNA/INTERNA/FITA por `face_uv_core` |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | A faixa da fita de borda ganha layer `UVMap` próprio: U no comprimento da aresta, V na espessura |
| `_reversa_sdd/domain.md` | Glossário adicional | regra-nova | `btm_armario.exibicao` escolhe "Somente textura" ou "Textura com linhas"; a variante passa por `btm_view_mode`/`btm_view_lines` até `overlay.show_wireframes` |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | `hb_details` força `SOLID` + `TEXTURE`; as opções recomendadas trocam "Cor por objeto" por "Textura" e preservam "Cursos 3D" |
| `_reversa_sdd/domain.md` | Glossário adicional | regra-nova | A migração idempotente por `exibicao_versao` (0→1) garante a chapa padrão nas peças sem material e avisa uma vez por cena |
| `_reversa_sdd/architecture.md` | Limites e organização | regra-alterada | `armario_v2/__init__.py` inclui `exibicao` em `_MODULES`; o módulo novo `exibicao.py` já está contado nos componentes novos |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | O aviso da barra lateral só acusa cor de objeto quando o `color_type` não é `OBJECT` nem `TEXTURE` |
| `_reversa_sdd/domain.md` | Glossário adicional | delta-de-dados | Dez chaves novas de tradução em pt_BR/en_US para as variantes e os avisos da exibição |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | Material do usuário (`btm_armario_parte.material`) continua vencendo o acabamento padrão depois de Gerar |

## Regras sob vigilância

`W001`, `W002`, `W003`, `W004`, `W005`, `W006`, `W007`, `W008`, `W009` e `W010`, em
`_reversa_forward/024-materiais-uv-preferencias/regression-watch.md`.

## Fontes

- `_reversa_forward/024-materiais-uv-preferencias/legacy-impact.md`
- `_reversa_forward/024-materiais-uv-preferencias/regression-watch.md`
- `_reversa_forward/024-materiais-uv-preferencias/requirements.md`
- `_reversa_forward/024-materiais-uv-preferencias/progress.jsonl`
- `_reversa_forward/024-materiais-uv-preferencias/todo.md`
