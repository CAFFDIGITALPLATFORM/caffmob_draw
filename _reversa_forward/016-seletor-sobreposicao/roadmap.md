# Roadmap: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`
> Requirements: `_reversa_forward/016-seletor-sobreposicao/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature é um par de módulos novos dentro de `caffmob_draw/selection/`, o mesmo pacote de
`component_pick.py`, porque ela é interação de seleção na viewport e não desenho permanente de overlay.

Um núcleo puro, `selection/overlap_core.py`, guarda o que não precisa do Blender: ordenação e recorte dos achados,
o estado do seletor (marcados, foco, rolagem), a resposta de cada tecla e a geometria do painel em pixels. Ele roda
nos testes puros com objetos simulados, como `selection/classify.py` e `selection/component.py`.

O operador modal `caffmob.overlap_select` (`selection/overlap_select.py`, `{'INTERNAL'}`) faz o resto: um raio por
objeto `MESH` elegível na abertura, dois `draw_handler_add` (caixa do objeto em foco em `POST_VIEW`, painel em
`POST_PIXEL`), isolamento por `hide_set` com o estado guardado, e a seleção só aplicada no `Enter`. Cancelar devolve
seleção, ativo e visibilidade. O atalho `Ctrl + Alt + botão esquerdo` entra no mapa `3D View` com `head=True`, e a
mesma ação aparece em `ui/context_menu.py#draw_context_menu`, ao lado das demais ações da viewport.

Desenho e leitura de mouse reaproveitam `canvas2d/draw.py` e `hb_gpu_draw.point_in_rect`; os textos vão para
`data/translations/sobreposicao.json`, em `pt_BR` e `en_US`. Nada é gravado na cena, então não há migração.

## 2. Princípios aplicados

`.reversa/principles.md` não existe. Valem as regras de `AGENTS.md` e de `docs/rag/project/02_padroes_blender_5_2.md`,
que a feature respeita:

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Diferenças de versão só em `compat.py` | Nenhuma API dependente de versão é nova; o shader vem de `compat.get_builtin_shader` por `canvas2d.draw` | respeita |
| Handlers com remoção em todos os caminhos e no `unregister` | Os dois `draw_handler_add` saem no confirmar, no cancelar, no erro e no `unregister`; o keymap sai no `unregister` | respeita |
| `bpy.props` lidas por atributo; `# type: ignore` | Nenhuma propriedade nova; o estado vive na instância do modal, não na cena | respeita |
| Operadores que alteram dados com `UNDO` | O seletor não altera dado do projeto (RN-10): `{'INTERNAL'}`, sem passo de desfazer | respeita |
| Textos em português, com tradução | Catálogo novo `sobreposicao.json`; `tests/test_i18n_coverage.py` cobre a área nova assim que ela existe | respeita |
| Só malha nos cálculos geométricos (addendo `BUG-20261118-PLNT`) | O raio e o destaque só olham `obj.type == 'MESH'`, como o desenho da planta baixa | respeita |
| Núcleo puro testável sem `bpy` | `overlap_core.py` não importa `bpy`, só `N_` para os textos | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Núcleo puro `selection/overlap_core.py`: `rank(hits)` (ordena por distância e devolve a lista sem repetir), `Picker` (marcados, foco, rolagem, visível), `toggle`, `mark_all`, `invert`, `add`, `remove`, `move`, `scroll_by`, `panel_rect`, `row_at` e `action_at` | Ordenação, recorte e resposta a tecla viram teste puro, sem Blender, como `classify` e `component`; a geometria do painel em pixels já é padrão do projeto (`canvas2d/view.py`, `library_panel/layout_core.py`) | Tudo dentro do operador (não testável sem abrir o Blender); geometria do painel no `_draw` (erro de clique vs. desenho) | 🟢 |
| D-02 | Operador `caffmob.overlap_select` em `selection/overlap_select.py`, `bl_options = {'INTERNAL'}`, `poll` com `area.type == 'VIEW_3D'`, `region.type == 'WINDOW'` e `context.mode == 'OBJECT'` | Prefixo `caffmob.` exigido por `tests/test_identity.py`; `INTERNAL` porque não há dado do projeto alterado (RN-10) e nenhum passo de desfazer é criado | `view3d.overlap_selector` do anexo (namespace errado para o add-on); `{'REGISTER','UNDO'}` (empilharia desfazer sem dado alterado) | 🟢 |
| D-03 | Achados: uma passada em `context.view_layer.objects`, só `obj.type == 'MESH'`, `obj.visible_get()` e `not obj.hide_select`; para cada um, `evaluated_get(depsgraph)` e `evaluated.ray_cast` no espaço local do objeto, com origem e direção convertidas por `view3d_utils.region_2d_to_origin_3d` e `region_2d_to_vector_3d` | É o algoritmo de `_objects_under_cursor` do anexo; cada objeto é testado individualmente porque `scene.ray_cast` devolve só o primeiro impacto (RN-02). O filtro por `MESH` vem antes do cast, o que evita o caso de curva que derrubou o Blender na sonda (Lacuna 🟡) | `scene.ray_cast` (perde os de trás); varrer `depsgraph.object_instances` (fora de escopo por Q2) | 🟢 |
| D-04 | Destaque do foco (RN-04) por caixa envolvente do objeto, desenhada em `POST_VIEW` a partir de `obj.bound_box` transformado por `matrix_world`, com `line_width_set` e cor de destaque | Não converte geometria (nenhum `to_mesh`), não toca na seleção e é independente do tempo do depsgraph. A malha branca por `gpu` exigiria montar o batch da malha avaliada a cada troca de foco | Selecionar o objeto para pré-visualizar (contraria RN-03 e dispara o normalizador de RN-SELECTION-07); destaque permanente em `overlays/draw_handlers.py` (desenho de fundo, não de sessão) | 🟡 |
| D-05 | Painel em `POST_PIXEL`, com `canvas2d.draw.begin/rect/outline/text/end` e `hb_gpu_draw.point_in_rect`, posicionado ao lado do cursor e preso à região; rolagem de uma linha por toque da roda, com `MAX_VISIBLE = 12`; rodapé com o atalho de abertura | Reaproveita o desenho 2D já usado em `move_over/ops_dialog.py`; o painel do anexo já tem essas medidas (390 × linhas de 25 px) e o rodapé é onde o RNF manda lembrar o atalho | Popup do Blender (`invoke_popup`): não desenha sobre a viewport com posição própria, como o `ops_dialog` já registrou | 🟢 |
| D-06 | Isolamento por `hide_set`: na abertura, guarda `obj.hide_get()` de todos os objetos do view layer; isolar esconde tudo menos o foco, restaurar devolve o mapa; toda saída (confirmar, cancelar, erro, `unregister`) chama a restauração | RN-05 e Q3. A Local View nativa isola o que está selecionado, contrariando RN-03/RN-04, e reenquadra a vista | `view3d.localview` (mexe na seleção e na câmera); `hide_viewport` (outro interruptor, não reversível pelo usuário) | 🟢 |
| D-07 | Atalho: item `LEFTMOUSE` / `CLICK` com `ctrl=True`, `alt=True`, `head=True` no mapa `3D View` (`keyconfigs.addon`), guardado para remoção; a mesma ação em `ui/context_menu.py`, com `layout.operator_context = 'INVOKE_DEFAULT'` | RN-08 e RF-14. `Alt` e `Alt + Shift` ficam com `caffmob.component_pick` (D-04 da 011); os oito combos de `LEFTMOUSE` já são `view3d.select`, então o item entra em `head=True`, como o do componente | `Alt + Shift + clique` do anexo (colide com o `component_pick`); tecla isolada fora do mouse (menos descoberta) | 🟢 |
| D-08 | Abertura pelo menu de contexto com o cursor da viewport: quando o evento não traz coordenada de região válida, a posição sai de `window.mouse_x/mouse_y` menos `region.x/region.y`; se cair fora da região, usa o centro dela | O item de menu é obrigatório por RN-08 e o raio precisa de um ponto; o anexo só tinha o atalho, onde `mouse_region_x/y` sempre vale | Exigir o atalho também no menu (contradiz o RF-14); usar o objeto ativo (não é o que está sob o cursor) | 🟡 |
| D-09 | Registro: entrada na lista `_submodule_names` de `caffmob_draw/__init__.py` (`"selection.overlap_core"` antes de `"selection.overlap_select"`), import explícito junto de `component_props/component_select/component_pick` e registro nas duas cascatas, na mesma posição | RN-11: o módulo segue o contrato dos módulos de seleção (hot-reload, `register`, `unregister`) e o `unregister` do add-on remove o keymap e qualquer seletor aberto | Registrar dentro de `selection/__init__.py` (o pacote hoje é só docstring); entrar em `ui.register` (não é interface de painel) | 🟢 |
| D-10 | Cancelamento externo: referência de módulo ao seletor aberto, e uma função `cancel_active()` chamada no `unregister` e antes de abrir outro | Débito 🔴 conhecido de `_reversa_sdd/architecture.md#Débitos`: modal com limpeza incompleta no cancelamento externo | Confiar no `ESC` do usuário (deixa `hide_set` no arquivo ao desinstalar) | 🟡 |
| D-11 | Traduções em `caffmob_draw/data/translations/sobreposicao.json`, com textos-chave em português e as duas línguas preenchidas, um arquivo só para os textos novos | `tests/test_i18n_coverage.py` exige as duas línguas e um dono por texto; área nova entra traduzida (`PENDING_AREAS` vazio) | Reaproveitar `selection.json` (mistura duas áreas no mesmo dono e o teste proíbe texto repetido) | 🟢 |

## 4. Premissas

Nenhuma dúvida em aberto: a `clarify` de 2026-11-19 fechou as três perguntas e o `requirements.md` não tem
marcador pendente.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| A caixa envolvente basta como destaque de foco (D-04) | §4 RN-04, RF-04 | Baixo: o destaque é estético; trocar por contorno de arestas não muda contrato |
| O cursor da viewport é recuperável quando a ação vem do menu (D-08) | §4 RN-08, RF-14 | Médio: o item de menu abriria no centro da vista e escolheria outra pilha de objetos |
| O tempo de abertura na cena real fica abaixo de 1 s (D-03) | §6 RNF de desempenho, §10 Lacuna 🟡 | Médio: a tarefa T001 mede antes de fechar; se estourar, entra poda por `obj.visible_camera` ou cache por evento |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Núcleo do seletor | `selection/overlap_core.py` (novo) | componente-novo | Ordenação, estado, teclas e geometria do painel, puro |
| Seletor da viewport | `selection/overlap_select.py` (novo) | componente-novo | Operador modal, raio por objeto, dois desenhos, isolamento, keymap |
| Menu de contexto | `ui/context_menu.py#draw_context_menu` | contrato-alterado | Ganha o item do seletor, com `INVOKE_DEFAULT` |
| Registro da extensão | `caffmob_draw/__init__.py#_submodule_names, register, unregister` | regra-alterada | Hot-reload, import e as duas cascatas |
| Desenho 2D | `canvas2d/draw.py#begin, rect, outline, text, end` | n/a (reuso) | Sem mudança; base do painel (D-05) |
| Seleção por componente | `selection/component_pick.py#register` | n/a (reuso) | Sem mudança; referencia o keymap que continua com `Alt` e `Alt + Shift` |
| Overlays | `overlays/draw_handlers.py` | n/a | Sem mudança: o desenho do seletor é de sessão, não permanente |
| Traduções | `data/translations/sobreposicao.json` (novo) | contrato-novo | Textos do painel, avisos e rodapé nas duas línguas |
| Testes | `tests/test_overlap_core.py`, `tests/blender_016_overlap_smoke.py` (novos) | componente-novo | Núcleo puro e fumaça no Blender 5.2 |

Arquivos que a mudança toca (rascunho do `legacy-impact.md` do `/reversa-coding`):
`caffmob_draw/selection/overlap_core.py`, `caffmob_draw/selection/overlap_select.py`, `caffmob_draw/ui/context_menu.py`,
`caffmob_draw/__init__.py`, `caffmob_draw/data/translations/sobreposicao.json`, `tests/test_overlap_core.py`,
`tests/blender_016_overlap_smoke.py`.

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhum campo novo, nenhuma marca nova nos objetos, nenhuma propriedade de cena. O estado do
  seletor (achados, marcados, foco, rolagem, isolado, seleção e ativo originais, `hide_get()` por objeto) vive na
  instância do modal e desaparece ao fechar. A única escrita externa é `hide_set` durante o isolamento, restaurada
  em toda saída.
- Detalhe completo em: `_reversa_forward/016-seletor-sobreposicao/data-delta.md`

## 7. Delta de contratos externos

n/a: a feature não toca contrato externo (HTTP, fila, gRPC, GraphQL, arquivo de troca). O único contrato que ela
acrescenta é interno à viewport: o item de keymap e o item de menu levam ao mesmo operador.

## 8. Plano de migração

n/a. Nada é gravado na cena e nenhum dado antigo muda de forma. Arquivo salvo com o isolamento ligado mantém a
visibilidade que estiver no arquivo ao fechar o Blender à força, caso já registrado como Lacuna 🟡 na `requirements`;
o caminho normal (confirmar, cancelar, `unregister`) restaura tudo.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| O `ray_cast` por objeto custa caro na cena real (mais de 2.000 objetos) | médio | médio | T001 mede antes de tudo; se passar de 1 s, podar candidatos antes do cast (por exemplo `visible_camera` e caixa envolvente contra o raio) e medir de novo |
| O `ray_cast` numa curva derruba o Blender (sonda de 2026-11-19, exit 11) | alto | baixo | O filtro `obj.type == 'MESH'` precede qualquer avaliação, e o cast fica em `try/except`; o smoke abre numa cena com curva, texto, vazio e instâncias de Geometry Nodes junto da malha |
| O isolamento deixa objetos escondidos ao fechar o Blender à força | médio | baixo | Restauração em toda saída e no `unregister`; aviso no `onboarding.md`; decisão de Q3 já aceitou o risco |
| O `Ctrl + Alt + clique` tira do usuário a variante de `view3d.select` | baixo | certo (é o desenho) | Mesma ação no menu de contexto e atalho no rodapé do painel (RNF de compatibilidade) |
| Abrir o seletor e cancelar cria passo de desfazer | baixo | baixo | `{'INTERNAL'}` e nenhuma escrita de dado; o smoke confere que a pilha de desfazer não cresce |
| O modal interfere no HUD da viewport (`LEFTMOUSE` `PRESS`, `head=True`) | médio | baixo | O HUD só consome cliques nos widgets dele e devolve `PASS_THROUGH`; o smoke abre o seletor com o HUD ligado |
| Objeto apagado ou renomeado durante a inspeção | baixo | baixo | Toda chamada em objeto guardado vai em `try/except (ReferenceError, RuntimeError)`; a linha sai da lista sem fechar o seletor |
| Texto novo sem tradução quebra `test_i18n_coverage` | baixo | médio | Catálogo `sobreposicao.json` criado junto do código (D-11) |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `tests/test_overlap_core.py` verde, junto de `test_i18n_coverage` e `test_identity`
- [ ] `tests/blender_016_overlap_smoke.py` verde no Blender 5.2 (`--factory-startup`), com `EXIT=0`
- [ ] Tempo de abertura medido na cena real do titular (mais de 2.000 objetos), abaixo de 1 s
- [ ] `py -3 docs/rag/tools/check_api.py` limpo e `py_compile` nos arquivos novos
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-plan`, já com os esclarecimentos de 2026-11-19 | reversa |
