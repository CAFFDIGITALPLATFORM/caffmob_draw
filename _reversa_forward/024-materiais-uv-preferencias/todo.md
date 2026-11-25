# Actions: Materiais, UV por face e preferências de exibição do armário

> Identificador: `024-materiais-uv-preferencias`
> Data: `2026-11-25`
> Roadmap: `_reversa_forward/024-materiais-uv-preferencias/roadmap.md`
> Nenhuma ação abaixo foi executada: este é o artefato do `/reversa-to-do`, sem código de produto.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 15 |
| Paralelizáveis (`[//]`) | 5 |
| Bloqueadas por decisão do titular | 2 (T001, T010) |
| Maior cadeia de dependência | 5 (T002 → T003 → T005 → T011 → T013) |

**Caminhos e linhas conferidos nesta árvore** (não de memória): `caffmob_draw/hb_details.py:98-99`,
`caffmob_draw/armario_v2/build.py:309` (`_material`), `:328` (`materiais`), `:390-396` (`_uv_metros`), `:608`
(`_material_da_peca`), `caffmob_draw/edgeband/build.py:18-57`, `caffmob_draw/edgeband/props.py:42-47`,
`caffmob_draw/armario_v2/props.py:197` (`BTM_PG_ArmarioV2`), `:267` (`gerado`), `caffmob_draw/__init__.py:146`
(`BTM_AddonPreferences`), `:185` (`cabinet_color`), `:304` (desenho da cor), `caffmob_draw/armario_v2/__init__.py:30`
(`_MODULES`).

## Fase 1, Confirmação e propriedades

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T001 | **Confirmar na GUI qual controle é “Cursos 3D”.** Não existe nenhuma string `Cursos 3D` em Python, `pt_BR` ou `en_US`; antes de mexer em `BTM_AddonPreferences`, abrir Edit → Preferences → Add-ons e registrar (a) o rótulo exato, (b) o `bl_idname`/prop, (c) se é opção do add-on ou da cena. Registrar o achado em `investigation.md` §4. **Nenhum código** | - | - | `_reversa_forward/024-materiais-uv-preferencias/investigation.md` | Print/nota no artefato + `grep -rn "Cursos 3D" caffmob_draw` vazio confirmando a ausência | `[ ]` **bloqueada pelo titular** |
| T002 | Acrescentar em `BTM_PG_ArmarioV2` (`props.py:197`, junto de `gerado` na linha 267) `exibicao_versao` (Int, default 0) e `exibicao` (Enum `TEXTURA_SO`/`TEXTURA_LINHAS`, default `TEXTURA_SO`) | - | `[//]` | `caffmob_draw/armario_v2/props.py` | `tests/blender_024_exibicao.py` (novo): criar raiz e ler/gravar os dois campos | `[ ]` |

## Fase 2, Núcleos puros (sem `bpy`)

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T003 | Criar `armario_v2/face_uv_core.py`: classificar cada face em `EXTERNA`, `INTERNA` ou `FITA` a partir de normal + centro da caixa + sinal do espelho, e devolver o retângulo UV em metros no referencial da peça | T002 | `[//]` | `caffmob_draw/armario_v2/face_uv_core.py` | `tests/test_face_uv_024.py` (novo): caixa 600×720×18, face frontal/normal +Y = EXTERNA, oposta = INTERNA; peça espelhada mantém o canto | `[ ]` |
| T004 | Criar `armario_v2/mdf_core.py`: gerador **puro e determinístico** dos bytes RGBA da textura MDF claro (512×512, semente fixa, grão fino), sem `bpy` e sem rede | - | `[//]` | `caffmob_draw/armario_v2/mdf_core.py` | `tests/test_mdf_core_024.py` (novo): dois chamados produzem o mesmo `bytes`; tamanho = 512×512×4; variação entre pixels dentro da faixa clara | `[ ]` |
| T005 | Levar o resultado de `mdf_core` para `bpy.data.images` **empacotada** (`pack()`), num módulo de cena `armario_v2/textura_padrao.py`, e usá-lo em `build.py:_material` (linha 309) como `ShaderNodeTexImage` + `Mapping` em 1/tamanho em metros, preservando `_material_da_peca` (linha 608) | T003, T004 | - | `caffmob_draw/armario_v2/textura_padrao.py`, `caffmob_draw/armario_v2/build.py` | `tests/blender_024_textura.py` (novo): material da chapa tem nó `TEX_IMAGE` com `image.packed_file`; peça com material do usuário continua com o material dele após `bpy.ops.caffmob.armario_v2_gerar` | `[ ]` |
| T006 | Dar UV próprio à faixa de fita em `edgeband/build.py:_write` (linha 18) e `update` (linha 57): layer `UVMap`, **U = comprimento da faixa em metros**, **V = largura da fita em metros**; `solid_material` (linha 32) continua valendo quando `use_color` (`edgeband/props.py:44`) | - | `[//]` | `caffmob_draw/edgeband/build.py` | `tests/blender_024_uv.py` (novo): faixa gerada tem `UVMap`; Umax−Umin ≈ comprimento, Vmax−Vmin ≈ largura da fita | `[ ]` |
| T007 | Fazer `build.py:_uv_metros` (linha 390) delegar o retângulo a `face_uv_core`, mantendo o layer `UVMap` e a unidade metro; nenhuma mudança de geometria | T003 | - | `caffmob_draw/armario_v2/build.py` | `tests/blender_024_uv.py`: faces externa/interna de uma chapa não compartilham o mesmo retângulo; `tests/blender_017_armario_smoke.py` continua OK | `[ ]` |

## Fase 3, Exibição e preferências

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T008 | Trocar `space.shading.color_type = 'OBJECT'` por `'TEXTURE'` em `hb_details.py:99`, mantendo `shading.type = 'SOLID'`; nenhum outro fluxo é tocado | T005 | - | `caffmob_draw/hb_details.py` | `tests/blender_024_exibicao.py`: após o fluxo de detalhes, `space.shading.color_type == 'TEXTURE'` num `VIEW_3D` de teste | `[ ]` |
| T009 | Trocar o controle “Cor dos Armários” por **“Textura”** em `BTM_AddonPreferences`: novo `exibicao_armario` (`TEXTURA_SO`/`TEXTURA_LINHAS`), remover a linha `layout.prop(self, "cabinet_color")` (`__init__.py:304`) e **manter a propriedade** `cabinet_color` (`:185`) como legado/migração; nenhuma outra opção é removida | T001 | - | `caffmob_draw/__init__.py` | `tests/blender_024_prefs.py` (novo): enum tem exatamente 2 itens; `cabinet_color` continua existindo; `show_legacy_libraries`, `panel_mode`, `stick_magnet`, `mobi_url` intactos | `[ ]` **bloqueada por T001** |
| T010 | Implementar “Textura com linhas” (todas as arestas de cada chapa) para a variante `TEXTURA_LINHAS` e desligar em `TEXTURA_SO` | T005, T009 | - | `caffmob_draw/armario_v2/exibicao.py` (novo) | `tests/blender_024_exibicao.py`: alternar a variante liga/desliga o contorno sem trocar material | `[ ]` **mecanismo pendente de decisão (ver Lacunas)** |
| T011 | Migração idempotente: handler `load_post` (padrão de `armario_v2/anim.py:400`) que percorre raízes de `Marcenaria` com `exibicao_versao == 0`, aplica a textura padrão nas peças sem material, grava `1` e avisa **uma vez**; registrar o módulo em `armario_v2/__init__.py:30` (`_MODULES`) | T002, T005 | - | `caffmob_draw/armario_v2/exibicao.py`, `caffmob_draw/armario_v2/__init__.py` | `tests/blender_024_migracao.py` (novo): primeira passada migra e conta 1 aviso; segunda passada não altera nada | `[ ]` |

## Fase 4, Fechamento

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T012 | Registrar `pt_BR`/`en_US` de “Textura”, “Somente textura”, “Textura com linhas”, descrições e aviso de migração | T008, T009, T010, T011 | - | `caffmob_draw/data/translations/armario_v2.json` | `cd tests && python -m unittest test_i18n_coverage` | `[ ]` |
| T013 | Atualizar `onboarding.md` com o resultado real dos passos 1–4 e rodar a bateria | T005, T006, T007, T008, T009, T010, T011, T012 | - | `_reversa_forward/024-materiais-uv-preferencias/onboarding.md` | `tests/test_face_uv_024`, `test_mdf_core_024`, `blender_024_*`, `blender_017`, `blender_023_fase7`, `blender_023_desempenho`, suíte pura, `docs/rag/tools/check_api.py` | `[ ]` |
| T014 | Provar **offline** e **UNDO**: rodar os ensaios da 024 com `CAFFMOB_BASE` vazio e sem `--online-mode`, e garantir que nenhum operador novo (se houver) declare `UNDO` sem remoção de handler no `unregister` | T013 | - | `tests/` | `CAFFMOB_BASE= blender --background ... --python tests/blender_024_*.py` sem chamada de rede; `grep -n "bl_options" ` nos operadores novos | `[ ]` |
| T015 | Verificação visual em sessão gráfica: grão do MDF, Solid/Preview/render iguais, contorno da variante “com linhas”, aviso de migração | T013 | - | `_reversa_forward/024-materiais-uv-preferencias/onboarding.md` §5 | Checklist preenchido na GUI | `[ ]` **requer GUI** |

## Ordem recomendada

1. **T001 e T002** em paralelo (uma é GUI, outra é propriedade).
2. **T003 e T004** em paralelo (núcleos puros, sem cena).
3. **T006** em paralelo com **T005** (fita não depende da textura).
4. **T007 → T008** (UV antes de o Solid passar a mostrá-lo).
5. **T009** depois de T001; **T010** depois de T005 + T009 (ou fica bloqueada).
6. **T011** fecha a migração; **T012** traduz; **T013/T014** medem; **T015** valida na GUI.

## Lacunas e perguntas pendentes para o `/reversa-clarify`

1. **“Cursos 3D” (T001):** não existe string com esse nome no código. É uma opção da tela de preferências do add-on,
   uma biblioteca/categoria, ou um controle da cena? *Bloqueia T009.*
2. **Mecanismo de “Textura com linhas” (T010):** no Solid, “todas as arestas de cada chapa” pode ser (a) contorno de
   objeto global (`shading.show_object_outline`, afeta a cena toda), (b) wireframe por peça (mostra arestas e
   triangulação), ou (c) contorno geométrico por peça (mais caro, mas exato). *Bloqueia T010 e o critério de pronto de
   RN-02.*
3. **Asset vs. runtime (T005):** a decisão do clarify pediu “textura padrão do add-on”, mas **não há PNG de MDF no
   pacote**; o plano gerou a textura em runtime e empacotada. Confirmar que isso satisfaz, ou exigir um arquivo de
   textura real do catálogo. *Não bloqueia T004/T005, mas muda licença e peso.*

## Notas de execução

> Reservado para `/reversa-coding`. Nada executado nesta rodada: só documentação de reversa foi escrita.
