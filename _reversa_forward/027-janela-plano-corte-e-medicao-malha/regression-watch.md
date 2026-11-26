# Regression watch: 027

> Feature: `027-janela-plano-corte-e-medicao-malha` (fases 1 a 3 executadas)

## 1. Watch principal

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|------------------------------|---------------------|-------------------|
| W001 | `ui/view_mode_core.py` (`settings`) | O interruptor Linhas não liga o wireframe do Blender (`show_wireframes` continua `False`) e vale para o desenho próprio (`edges = True`) | presença | Alguma vista volta a mostrar o wireframe do tema, ou `show_wireframes` volta a `True` |
| W002 | `overlays/arestas.py` (`espessura`) | A espessura da aresta vem de `BTM_AddonPreferences.espessura_aresta`, padrão 0,2 px, mínima 0,2 | presença | A linha preta some, volta a usar a cor do tema ou ignora a preferência |
| W003 | `ui/object_properties.py` (`BTM_PG_SelectionEdit`) | `multi_width/multi_height/multi_depth/multi_thickness` são `StringProperty` com `options=set()`; vazio quando os valores divergem | redação | Campo volta a ser numérico (mostra 0,0), fica animável ou mostra um valor que não é comum |
| W004 | `target/ops.py` (`caffmob.target_multi_apply`) | Com vários selecionados a medida só entra pela confirmação, num passo de Desfazer | presença | Editar o campo aplica direto, sem perguntar, ou gasta mais de um Desfazer |
| W005 | `promob/cameras.py` (`alvo_de`) | Nenhuma câmera cria Empty nem restrição Track To; o alvo é `btm_camera_alvo` e cenas antigas migram | ausência | Volta a aparecer um Empty alvo, um `TRACK_TO` ou uma câmera dessincronizada do alvo |

## 2. Observações (sem peso de regressão)

- A linha de 0,2 px rende 1 pixel na tela: abaixo disso a placa não desenha. A preferência é passada como `lineWidth`
  do `POLYLINE_UNIFORM_COLOR`; acima de 1 px a espessura cresce de verdade.
- O desenho das arestas depende de `POST_VIEW` com teste de profundidade (`LESS_EQUAL`): arestas atrás da geometria
  ficam escondidas, como no modo sólido do Blender.
- A confirmação usa `invoke_props_dialog` com `confirm_text="Sim"`; o botão de recusa é o “Cancelar” nativo do Blender
  (a API do Blender 5.2 não aceita `cancel_text`).
- Em Modo de Edição o add-on não desenha arestas (as do próprio Blender aparecem no objeto em edição); “Somente
  textura” vale para o desenho do add-on.
- A matriz da 027 ainda tem T009–T014 abertas (plano de corte em janela e V-Ray Mesh Measure): a feature não está
  fechada e não houve versão nem tag nesta rodada.

## 3. Histórico de re-extrações

(vazio)

## 4. Arquivadas

(vazio)
