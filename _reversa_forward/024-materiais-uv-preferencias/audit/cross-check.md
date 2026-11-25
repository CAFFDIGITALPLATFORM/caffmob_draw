# Cross-check: 024-materiais-uv-preferencias

> Data: 2026-11-25 (2ª rodada — auditoria do `todo.md` revisado contra `requirements.md`, `roadmap.md` e o código real)
> Feature: `_reversa_forward/024-materiais-uv-preferencias`
> Artefatos analisados: [requirements.md](../requirements.md) · [roadmap.md](../roadmap.md) · [todo.md](../todo.md) ·
> [data-delta.md](../data-delta.md) · [investigation.md](../investigation.md)
> Leitura de código: `caffmob_draw/hb_details.py`, `armario_v2/build.py`, `armario_v2/props.py`,
> `armario_v2/__init__.py`, `armario_v2/anim.py`, `edgeband/build.py`, `edgeband/props.py`, `edgeband/core.py`,
> `__init__.py`, `ops.py`, `ui/view_mode.py`, `ui/view_mode_core.py`, `ui/sidebar_build.py`, `ui/view3d_sidebar.py`,
> `ui/menus.py`, `hb_utils.py`, `texture_library/uv_core.py`, `product_libraries/frameless/operators/ops_placement.py`,
> `tests/test_view_mode.py`, `tests/test_i18n_coverage.py`.

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 3 |
| MEDIUM | 2 |
| LOW | 4 |

**Nota sobre escrita:** o `/reversa-audit` é leitor por padrão e só gravaria este relatório. Nesta rodada o titular
pediu explicitamente que as ações inconsistentes fossem **corrigidas no artefato**; as correções foram aplicadas em
`todo.md` e estão identificadas uma a uma abaixo (coluna “Situação”). `requirements.md`, `roadmap.md` e
`data-delta.md` **não** foram alterados — o que exige decisão do titular está nas perguntas pendentes.

## Achados

| ID | Severidade | Eixo | Descrição | Situação |
|---|---|---|---|---|
| A001 | HIGH | Cobertura / duplicação | A variante “Textura com linhas” e o Solid com `color_type = 'TEXTURE'` **já existem** como recurso entregue da feature 010: `Scene.btm_view_mode` (`'SOLID'`/`'TEXTURE'`), `Scene.btm_view_lines`, `ui/view_mode.apply` (`:26`) com `load_post`, `ui/view_mode_core.settings` (`:24`) e o controle na barra lateral (`ui/sidebar_build.py:23-33`), testado por `tests/test_view_mode.py`. O to-do anterior criava um mecanismo paralelo (`armario_v2/exibicao.py` com contorno próprio), duplicando o que já funciona | **Corrigido** — T010 passa a mapear `exibicao_armario` para `view_mode_core.settings` + `view_mode.apply`; nenhum contorno novo |
| A002 | HIGH | Consistência | O to-do anterior mandava remover `layout.prop(self, "cabinet_color")` (`__init__.py:304`) como se fosse a opção “Cor por objeto”. Não é: `cabinet_color` é a **cor de objeto dos armários das bibliotecas herdadas**, lida em `ops_placement.py:40` (`obj.color = add_on_prefs.cabinet_color`). A opção que a RN-01 manda trocar por textura está no **diálogo de preferências recomendadas**, `caffmob.set_recommended_settings` (`ops.py:30-110`, `turn_on_object_color_type`, texto “- REQUIRED” em `:110`) | **Corrigido** — T009 preserva `cabinet_color` e a linha `:304`; criada **T016** para o diálogo de `ops.py` |
| A003 | HIGH | Cobertura | Com o Solid em `TEXTURE`, `ui/view3d_sidebar.py:38-46` passaria a exibir sempre “Object Color Type is not enabled!” e um botão de “Open Recommended Settings” — regressão visível que nenhuma ação cobria | **Corrigido** — criada **T017** |
| A004 | MEDIUM | Consistência | “Cursos 3D” não existe em string alguma de `caffmob_draw/` (nem `pt_BR`, nem `en_US`). A única ocorrência no repositório é o pedido do titular registrado na auditoria da 023. O candidato real com nome quase idêntico é **“Turn Off 3D Cursor”** (`ops.py:54`), no mesmo diálogo que oferece a opção de cor de objeto | **Endereçado** — T001 ficou com alvo concreto (diálogo + `turn_off_3d_cursor`), segue bloqueante e sem código; pergunta 1 em `todo.md#Lacunas` |
| A005 | MEDIUM | Consistência | O to-do anterior listava “asset PNG vs. textura em runtime” como lacuna aberta, mas a decisão 1 do clarify já fechou isso (textura gerada em runtime e empacotada). Manter a pergunta reabria decisão fechada | **Corrigido** — lacuna removida do `todo.md` |
| A006 | LOW | Sanidade | `roadmap.md` §6 e `data-delta.md` dizem que `btm_armario.exibicao` tem “padrão herdado da preferência”; `bpy.props` não herda default de preferência do add-on | **Corrigido no to-do** — T002 fixa `TEXTURA_SO` como default da prop e delega a preferência à aplicação na geração/migração; pergunta 4 registrada |
| A007 | LOW | Cobertura | T012 mandava traduzir só em `armario_v2.json`, mas os rótulos alterados por T016/T017 moram em `ops.json` (`:218-224`) e `ui.json` (`:778`) | **Corrigido** — T012 cobre os três catálogos, `pt_BR` e `en_US` |
| A008 | LOW | Consistência | `roadmap.md` D-05 cita `__init__.py:195` para `cabinet_color`; a linha real é **185** (a 195 é `door_window_color`). `hb_details.py` aparece como 98 na prosa e 99 no código (`color_type`) | **Corrigido no to-do** — tabela de linhas conferidas usa 185, 304, 98/99 |
| A009 | LOW | Sanidade | O to-do anterior pedia “nenhum operador novo declare UNDO”, mas não verificava a remoção do `load_post` no `unregister` — o ponto real de vazamento de handler | **Corrigido** — T011 e T014 exigem `append` **e** `remove`, com prova por `grep` |

## Fechamento dos achados HIGH

### A001 — a variante “com linhas” já existe

`ui/view_mode_core.settings(mode, lines, previous_color)` devolve exatamente
`{'shading_type': 'SOLID', 'color_type': 'TEXTURE'|..., 'show_wireframes': bool(lines), ...}`; `ui/view_mode.apply`
escreve isso em todas as vistas 3D e o `load_post` reaplica ao abrir o arquivo. `ui/sidebar_build.draw_view_mode` já
desenha “Sólido · Textura” + o interruptor Linhas, e `view_mode_core.label` já rotula “Textura com linha”. Criar um
segundo mecanismo em `armario_v2/exibicao.py` produziria dois interruptores com o mesmo efeito e um deles sem teste.
A T010 corrigida reaproveita o núcleo; o que continua sendo trabalho novo é só a **preferência** (`exibicao_armario`) e
a **decoração do armário** (`btm_armario.exibicao`), não o desenho das linhas.

Resta uma diferença real de comportamento a decidir com o titular (pergunta 3): `show_wireframes` é global e mostra
arestas de todos os objetos, não só das chapas do armário.

### A002 — “Cor por objeto” está no diálogo, não na paleta

O requisito fala em “preferências recomendadas do add-on”. `BTM_AddonPreferences` (`__init__.py:146`) desenha uma
**paleta** (parede, armário, porta/janela, textos, destaque, obstáculo) e `cabinet_color` (`:185`) é consumida por
`toggle_cabinet_color` (`ops_placement.py:40`) para pintar armários das bibliotecas herdadas. Já
`home_builder_OT_set_recommended_settings` (`ops.py:30`) é o diálogo que instala as “configurações recomendadas” e
oferece `turn_on_object_color_type` com o texto **“Turn On Object Color Type - REQUIRED”** (`:110`), aplicando
`shading.color_type = 'OBJECT'` (`:90`). É esse o controle que a RN-01/D-02 mandam substituir por textura — e é também
o diálogo onde vive a única opção com nome parecido com “Cursos 3D”.

Por isso T009 não remove mais a linha `:304` (removê-la tiraria do usuário o controle da cor real dos armários
herdados, sem relação com a feature) e a troca de comportamento ficou em T016.

### A003 — o aviso da barra lateral

`ui/view3d_sidebar.py:39` testa `context.space_data.shading.color_type != 'OBJECT'` e, quando verdadeiro, desenha um
bloco em alerta com o botão que abre o diálogo recomendado. Com o Solid em `TEXTURE` (RN-01) o teste fica verdadeiro em
todo armário novo, transformando um diagnóstico em ruído permanente. T017 corrige a condição junto com T008; sem isso a
feature entrega o próprio erro na cara do usuário.

## Escopo de escrita: nenhuma ação fora de `caffmob_draw/`

Esta auditoria conferiu, ação por ação, o caminho que cada uma escreve. **Nenhuma das 17 ações exige mudança de código
de produto fora de `caffmob_draw/`**, e por isso nenhuma precisou ser corrigida por esse motivo. As três exceções são
superfícies que não são produto:

| Ação | Caminho escrito | Por que não é código de produto |
|---|---|---|
| T001 | `_reversa_forward/024-materiais-uv-preferencias/audit/cross-check.md` | Nota de confirmação na pasta do próprio Reversa; não altera arquivo do add-on |
| T013 | `_reversa_forward/024-materiais-uv-preferencias/onboarding.md` | Documento de onboarding, pasta do Reversa |
| T014 | `tests/` (leitura e execução) | Harness de ensaio, liberado por `allowedPaths: tests/*`; não altera `caffmob_draw/` |

As demais 14 ações escrevem exclusivamente em `caffmob_draw/` (`armario_v2/props.py`, `armario_v2/build.py`,
`armario_v2/textura_padrao.py`, `armario_v2/face_uv_core.py`, `armario_v2/mdf_core.py`, `armario_v2/exibicao.py`,
`armario_v2/__init__.py`, `edgeband/build.py`, `hb_details.py`, `ops.py`, `ui/view3d_sidebar.py`, `__init__.py`,
`data/translations/*.json`). Nenhuma delas toca o gerador de geometria de módulo (fora de escopo, §5 do requirements),
o plano de corte, as bibliotecas herdadas nem os fluxos 2D que dependem de `color_type = 'OBJECT'`
(`hb_utils.set_layout_shading`, `hb_layouts`, `catalog/render_thumbnails`).

## Critério de pronto vs. o que o to-do realmente cobre

| Critério (`roadmap.md` §10) | Ações | Situação |
|---|---|---|
| Armário novo nasce texturizado; material do usuário vence | T004, T005 | coberto (prova em `blender_024_textura`) |
| Solid com `color_type = 'TEXTURE'`; mesmo material em Preview/render | T008, T016, T017 | coberto, com o aviso e o diálogo corrigidos (A002/A003) |
| UV EXTERNA/INTERNA/FITA + fita com U/V próprios | T003, T006, T007 | coberto |
| “Somente textura” e “Textura com linhas” sem remover opções | T001, T009, T010, T016 | coberto **reusando** `ui/view_mode` (A001); T010 ainda depende da pergunta 3 |
| Migração única com aviso e `exibicao_versao` | T002, T011 | coberto, incluindo remoção do handler |
| i18n `pt_BR`/`en_US` e `check_api` | T012, T013 | coberto nos três catálogos; `test_i18n_coverage` conferido nesta árvore (3 testes OK) |
| Suítes verdes exceto ambiente-gated | T013, T014 | coberto; offline e UNDO explícitos |
| Aparência e contorno julgados na GUI | T015 | coberto, requer sessão gráfica |

**O que o to-do não fecha sozinho:** as perguntas 1–4 de `todo.md#Lacunas`. Sem a resposta da 3, “Textura com linhas”
fica com o comportamento global de `show_wireframes`; sem a 2, o `color_type` global muda também paredes e armários
herdados. Nenhuma delas se resolve por código — são decisões do titular, e é exatamente onde a missão para.

## Itens verificados que passaram

### Cobertura
- RN-01 → T004/T005/T008/T016/T017; RN-02 → T001/T009/T010; RN-03 → T003/T006/T007; RN-04 → T002/T011.
- As 7 decisões do roadmap têm ação: D-01→T004/T005; D-02→T008/T016; D-03→T003/T007; D-04→T006; D-05→T001/T009;
  D-06→T010/T017; D-07→T002/T011.
- As cinco decisões do clarify aparecem sem contradição: textura em runtime (T004/T005), Solid `TEXTURE`
  (T008/T016), três classes de face (T003), fita com U/V (T006), `cabinet_color` legado + `exibicao_armario`
  (T009), migração idempotente (T002/T011).

### Consistência
- Citações de linha conferidas por `grep -n` e registradas em `todo.md` (tabela de caminhos): `hb_details.py:98/99`,
  `build.py:309/328/390/412/431/608/649`, `edgeband/build.py:18/32/47/57`, `edgeband/props.py:41/44`,
  `armario_v2/props.py:197/267`, `armario_v2/__init__.py:30`, `__init__.py:146/185/304`, `ops.py:30/39/54/110`,
  `view3d_sidebar.py:38-46`, `view_mode.py:26/51/54`, `view_mode_core.py:24`, `sidebar_build.py:23-33`,
  `uv_core.py:24`, `ops_placement.py:40`, `anim.py:362/400-407`, `edgeband/core.py:193`.
- Nenhum arquivo citado como alvo está ausente; os testes da 024 (`tests/*_024.py`) são entregas declaradas, não
  caminhos reaproveitados por engano. Os testes existentes aparecem só como regressão (`blender_017_armario_smoke`,
  `blender_023_fase7`, `blender_023_desempenho`, `test_view_mode`, `test_i18n_coverage`, `check_api.py`).

### Coerência com o legado
- `armario_v2` continua dono da geração; a fita continua objeto separado com malha própria; o plano de corte não é
  tocado (textura é exibição).
- Fluxos 2D que **precisam** de `color_type = 'OBJECT'` foram explicitamente deixados fora de escopo em T008:
  `hb_utils.set_layout_shading` (`:384`), `hb_layouts` (render de layout, `:1207`) e `catalog/render_thumbnails.py:154`.

### Sanidade do actions
- Dependências apontam só para IDs existentes; sem ciclo. Cadeia mais longa: T004 → T005 → T008 → T016 → T012 → T013 →
  T014 (7).
- T002, T003, T004 e T006 são `[//]` e não compartilham arquivo alvo (props do armário, dois núcleos puros e a fita).
- T005 e T007 tocam o mesmo `build.py`, mas são sequenciais (T005 depende de T003/T004; T007 depende de T003) e não
  estão marcadas `[//]`.
- T009/T010/T016/T017 dividem superfícies distintas (`__init__.py`, `exibicao.py`, `ops.py`, `view3d_sidebar.py`).

### Política de escrita
- Detalhe por ação na seção “Escopo de escrita”: 14 ações escrevem em `caffmob_draw/`, três em documentação/ensaio
  (`_reversa_forward/` e `tests/`) e nenhuma em código de produto fora do pacote.
- Observação de configuração: `.reversa/reversa-config.json` traz `allowedPaths` com `"***"` além de `caffmob_draw/*`
  e `tests/*`, o que na prática libera o projeto inteiro — quem depende da trava deve remover o curinga.

## Aviso

`requirements.md`, `roadmap.md`, `data-delta.md` e `investigation.md` não foram alterados por esta auditoria. As
correções descritas acima foram aplicadas apenas em `todo.md`, a pedido explícito do titular. As decisões que faltam
são as quatro perguntas listadas em `todo.md#Lacunas` — próximo ciclo: `/reversa-clarify`.
