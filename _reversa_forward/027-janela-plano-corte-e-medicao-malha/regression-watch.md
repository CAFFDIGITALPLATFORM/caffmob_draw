# Regression watch: 027

> Feature: `027-janela-plano-corte-e-medicao-malha` (fases 1 a 8 executadas; matriz 14/14)

## 1. Watch principal

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|------------------------------|---------------------|-------------------|
| W001 | `ui/view_mode_core.py` (`settings`) | O interruptor Linhas não liga o wireframe do Blender (`show_wireframes` continua `False`) e vale para o desenho próprio (`edges = True`) | presença | Alguma vista volta a mostrar o wireframe do tema, ou `show_wireframes` volta a `True` |
| W002 | `overlays/arestas.py` (`espessura`) | A espessura da aresta vem de `BTM_AddonPreferences.espessura_aresta`, padrão 0,2 px, mínima 0,2 | presença | A linha preta some, volta a usar a cor do tema ou ignora a preferência |
| W003 | `ui/object_properties.py` (`BTM_PG_SelectionEdit`) | `multi_width/multi_height/multi_depth/multi_thickness` são `StringProperty` com `options=set()`; vazio quando os valores divergem | redação | Campo volta a ser numérico (mostra 0,0), fica animável ou mostra um valor que não é comum |
| W004 | `target/ops.py` (`caffmob.target_multi_apply`) | Com vários selecionados a medida só entra pela confirmação, num passo de Desfazer | presença | Editar o campo aplica direto, sem perguntar, ou gasta mais de um Desfazer |
| W005 | `promob/cameras.py` (`alvo_de`) | Nenhuma câmera cria Empty nem restrição Track To; o alvo é `btm_camera_alvo` e cenas antigas migram | ausência | Volta a aparecer um Empty alvo, um `TRACK_TO` ou uma câmera dessincronizada do alvo |

| W006 | `ui/panels.py` (`draw_cut_plan`) | Pedir o plano de corte abre a janela (`caffmob.cut_plan_window`) e o cálculo antigo continua alcançável como “Recalcular Plano de Corte” | presença | O botão volta a só calcular, a janela some, ou `caffmob.calculate_nesting` deixa de existir na barra lateral |
| W007 | `cutting/plan_window_core.py` (`placed`, `utilization`) | As peças vêm das faixas do otimizador em milímetros absolutos dentro da chapa, e o aproveitamento é área das peças sobre a área nominal | presença | Peça desenhada fora da chapa, coordenada relativa em vez de absoluta, ou aproveitamento diferente do `stats` do otimizador |
| W008 | `mesh_measure/scene.py` (`snapshot`) | A leitura da malha é só fotografia: nenhum modificador, camada, material ou vértice do usuário é alterado, e as partes são os componentes conexos das arestas | ausência | O objeto ganha modificador/camada/material, ou as partes deixam de corresponder aos blocos soltos |
| W009 | `mesh_measure/window.py` (`open_window`) | Sem malha selecionada a janela não abre: o painel mostra o aviso e o conta-gotas, e o operador recusa com mensagem | presença | A janela abre vazia, quebra sem seleção, ou o conta-gotas some do painel |
| W010 | `caffmob_draw/__init__.py` (`register`, `unregister`) | `mesh_measure` e `cutting.plan_window` registram e desregistram juntos; desabilitar o add-on não deixa handler nem painel | presença | Sobra handler `POST_PIXEL`, painel registrado ou operador órfão depois do `unregister` |

## 2. Observações (sem peso de regressão)

- A linha de 0,2 px rende 1 pixel na tela: abaixo disso a placa não desenha. A preferência é passada como `lineWidth`
  do `POLYLINE_UNIFORM_COLOR`; acima de 1 px a espessura cresce de verdade.
- O desenho das arestas depende de `POST_VIEW` com teste de profundidade (`LESS_EQUAL`): arestas atrás da geometria
  ficam escondidas, como no modo sólido do Blender.
- A confirmação usa `invoke_props_dialog` com `confirm_text="Sim"`; o botão de recusa é o “Cancelar” nativo do Blender
  (a API do Blender 5.2 não aceita `cancel_text`).
- Em Modo de Edição o add-on não desenha arestas (as do próprio Blender aparecem no objeto em edição); “Somente
  textura” vale para o desenho do add-on.
- A janela do plano de corte desenha só o resultado do otimizador de faixas: o motor OpCut (feature 021) continua com
  a prévia em imagem e a exportação próprias.
- Linhas Ocultas e Sólido não usam teste de profundidade (o Image Editor não garante buffer): a oclusão é por ordem de
  pintura. Aparência conferida em execução com janela real, não pixel a pixel.
- A medição não decima nem altera a malha: o custo de quadro é proporcional aos triângulos do objeto escolhido. Em
  malha muito densa a janela fica lenta (não há cópia de exibição reduzida nesta versão).
- A matriz da 027 está fechada (14/14) e a versão/tag desta rodada foram aplicadas; falta apenas o `/reversa-sync`.

## 3. Histórico de re-extrações

(vazio)

## 4. Arquivadas

(vazio)
