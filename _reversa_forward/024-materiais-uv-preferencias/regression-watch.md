# Regression watch: 024-materiais-uv-preferencias

> Identificador: `024-materiais-uv-preferencias`
> Gerado em 2026-11-25 pelo `/reversa-coding`, a partir das regras alteradas de `legacy-impact.md`.

## Itens de vigilância

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/domain.md`, material/exibição do armário | O fluxo de detalhes usa `shading.type = 'SOLID'` com `color_type = 'TEXTURE'` | presença | `hb_details` voltar a `'OBJECT'` ou a `shading.type` diferente de `SOLID` |
| W002 | `_reversa_sdd/domain.md`, opções recomendadas | “Cursos 3D” (`turn_off_3d_cursor`) e as demais opções do diálogo continuam existindo e aplicando o mesmo efeito | presença | controle removido/renomeado em `ops.py` |
| W003 | `_reversa_sdd/domain.md`, cor de armário legado | `cabinet_color` continua nas preferências e continua alimentando `obj.color` das bibliotecas herdadas (`ops_placement.py:40`) | presença | preferência removida ou `ops_placement` deixando de ler a cor |
| W004 | `_reversa_sdd/domain.md`, modo de vista | `Scene.btm_view_mode`/`btm_view_lines` continuam sendo o estado do arquivo e o controle da barra lateral | redação | variante da 024 sobrescrevendo a cena sem passar por `view_mode.apply` |
| W005 | `_reversa_sdd/domain.md`, UV da chapa | Toda malha de chapa do armário v2 tem layer `UVMap` em metros, com EXTERNA/INTERNA/FITA distintos | presença | face sem UV, UV em 0..1, ou interior igual ao exterior |
| W006 | `_reversa_sdd/domain.md`, material do usuário | Peça com material escolhido continua vencendo o acabamento do spec depois de Gerar | presença | `build._material_da_peca` deixando de priorizar `btm_armario_parte.material` |
| W007 | `_reversa_sdd/domain.md`, migração | `exibicao_versao` grava 1 na primeira abertura e a segunda não migra nem avisa de novo | presença | migração repetindo ou apagando material do usuário |
| W008 | `_reversa_sdd/architecture.md`, handlers | O `load_post` da exibição é removido no `unregister()` | ausência | handler pendurado depois de desregistrar o add-on |
| W009 | `_reversa_sdd/domain.md`, fita de borda | A faixa tem UV próprio (U no comprimento, V na espessura) e mantém a cor lisa quando `use_color` | presença | faixa herdando o UV da chapa ou perdendo o layer ao reconstruir |

## Histórico de re-extrações

(vazio — preenchido quando rodar `/reversa` de novo)

## Observações

- A suíte pura completa tem uma falha ambiente-gated conhecida nesta máquina: `test_sessao_mobi.test_permissao_e_endereco`
  (NTFS devolve 0666 em vez de 0600). Não tem relação com a 024.
- `ruff` não está instalado nesta máquina; o lint ficou sem executar nesta rodada.
