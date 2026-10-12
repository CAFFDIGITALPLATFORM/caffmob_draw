# Canvas 2D — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/canvas2d/` em 2026-10-10, incluindo a árvore de trabalho ainda sem commit da feature 013. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-70):** commitar a 013 antes de congelar as specs; enquanto não houver commit, os itens da 013 (`gestures.py`, `compat.trackpad_delta`/`pinch_delta`) ficam **pendentes de commit** (DT-04). Confirmação de código não implica validação visual no Blender. 🟡 identifica prioridade inferida; 🔴 identifica lacuna de validação.

## Visão Geral

🟢 O módulo oferece coordenadas, navegação e desenho comuns às telas 2D dos editores de paredes e armários. Converte metros em pixels, fornece enquadramento e utilitários de encaixe e prepara uma área Image Editor como tela própria. Fontes: `view.py`, `gestures.py`, `draw.py`, `window.py`.

## Responsabilidades

- 🟢 Converter pontos entre mundo 2D e tela, deslocar/enquadrar a vista e aplicar zoom com âncora (`view.py:View2D`).
- 🟢 Converter pinça e roda em fatores de zoom e retângulo de seleção em bounds mundiais (`gestures.py`).
- 🟢 Calcular grade, encaixe ortogonal e distâncias geométricas (`view.py`).
- 🟢 Disponibilizar primitivas de desenho, textos traduzidos e cotas na unidade do usuário (`draw.py`).
- 🟢 Abrir/localizar a área do editor, identificar sobreposição do painel lateral e adiar seu fechamento (`window.py`).
- 🟢 A captura dos eventos e as alterações de paredes/armários pertencem aos consumidores; este módulo não implementa essas sessões de edição (`walls2d/ops_editor.py`, `cabinet_editor/ops_editor.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Mundo em metros; tela em pixels com origem inferior esquerda. `rect=(x,y,w,h)`, centro mundial padrão (0,0), escala padrão 100 px/m. | view.py:View2D |
| RN-02 | 🟢 Conversões usam o centro do retângulo; `contains` inclui suas quatro bordas. | view.py:to_screen/to_world/contains |
| RN-03 | 🟢 Pan subtrai delta em pixels dividido pela escala do centro mundial; zoom ancorado preserva o ponto mundial sob o cursor. | view.py:pan/zoom |
| RN-04 | 🟢 `zoom` limita escala ao mínimo 1e−6 px/m, sem teto. O construtor e `fit` não aplicam esse mesmo clamp geral. | view.py:__init__/zoom/fit |
| RN-05 | 🟢 Enquadrar centraliza bounds e escolhe a menor escala que atende largura/altura com margem relativa padrão 0,1; extensão degenerada usa mínimo 1e−6 m antes da margem. | view.py:fit |
| RN-06 | 🟢 Pinça usa exp(delta/150); delta positivo aproxima, negativo afasta, zero não muda. | gestures.py:pinch_factor |
| RN-07 | 🟢 Roda usa fator 1,15 ou seu inverso; `inverted` troca o sentido. Leitura da preferência e do evento é responsabilidade do consumidor. | gestures.py:wheel_factor; walls2d/ops_editor.py |
| RN-08 | 🟢 Zoom janela aceita qualquer sentido de arraste; se qualquer lado tiver menos de 5 px, retorna None sem alterar a vista. O helper só produz bounds; o consumidor decide chamar fit. | gestures.py:zoom_window_bounds |
| RN-09 | 🟢 Grade com passo ≤0 ou densidade de extensão/passo >400 em qualquer eixo retorna duas listas vazias. Caso contrário, usa índices de floor a ceil inclusivos, podendo incluir linhas além das bordas. | view.py:grid_lines |
| RN-10 | 🟢 Snap de grade arredonda cada coordenada ao múltiplo do passo; passo ≤0 devolve o ponto sem encaixe. | view.py:snap_to_grid |
| RN-11 | 🟢 Snap ortogonal considera 0/90/180/270°, tolerância inclusiva 2,5°, conserva comprimento radial e informa se travou. Vetor com comprimento <1e−12 não trava. | view.py:ortho_snap |
| RN-12 | 🟢 Distância a segmento limita projeção a [0,1]; segmento de comprimento ao quadrado <1e−18 usa distância à ponta. | view.py:distance_point_segment |
| RN-13 | 🟢 Desenho usa cores RGBA, primitivas em pixels e transformação View2D para primitivas mundiais. Textos passam por tradução; cotas usam units.format_value. | draw.py |
| RN-14 | 🟢 Janela duplicada é preferida; se não for criada, a área atual é reutilizada e seu tipo original é guardado. Ausência de área/janela no fallback gera RuntimeError com mensagem recebida. | window.py:open_window |
| RN-15 | 🟢 Área preparada é IMAGE_EDITOR sem imagem, com painel lateral e sem cabeçalho, menus ou barras de ferramentas de imagem. | window.py:prepare |
| RN-16 | 🟢 Painel lateral só conta quando largura/altura >1; hit usa coordenadas da janela, limite superior exclusivo. visible_width exclui sobreposição à direita quando ui.x está dentro da região. | window.py:side_panel/over_side_panel/visible_width |
| RN-17 | 🟢 Fechamento é agendado em timer com intervalo inicial 0,05 s; restaura o tipo no fallback ou tenta fechar a janela duplicada quando há outra janela. Falha RuntimeError ao fechar transforma a área em VIEW_3D. | window.py:close_later/_close |

## Requisitos Funcionais

🟡 Prioridades inferidas da reutilização pelos editores, alternativas explícitas e testes existentes; não constituem um roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Conversões inversas e teste de pertencimento ao retângulo | Must | CA-01 e CA-02 |
| RF-02 | 🟢 Pan, zoom ancorado e enquadramento | Must | CA-03 e CA-04 |
| RF-03 | 🟢 Fatores de pinça/roda e bounds do zoom janela | Must | CA-05 e CA-06 |
| RF-04 | 🟢 Grade, snap ortogonal e distâncias | Must | CA-07 e CA-08 |
| RF-05 | 🟢 Primitivas/texto/cotas comuns aos editores | Must | CA-09 e CA-10 |
| RF-06 | 🟢 Área própria com fallback, acesso ao painel e fechamento diferido | Should | CA-11 e CA-12; fallback mantém acesso quando duplicação falha |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Custo de desenho | Suprimir grade quando extensão/passo excede 400 em algum eixo; não assumir limite exato de 400 elementos na lista | view.py:grid_lines | 🟢 |
| Separação do cálculo | Coordenadas e fatores de gestos executam sem importar bpy; desenho/janela dependem do host | view.py; gestures.py; draw.py; window.py | 🟢 |
| Ciclo de vida da UI | Adiar fechamento em 0,05 s, fora da chamada modal que usa a área | window.py:close_later | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados diretamente das funções atuais. CA-09 a CA-12 descrevem contratos estáticos cujo resultado visual/contextual ainda não foi executado nesta re-extração.

```gherkin
CA-01 — Conversão reversível
Dado rect (10,20,400,300), escala 250 e centro mundial (1,-0.5)
Quando converto o centro para tela e depois para mundo
Então obtenho pixel (210,170) e recupero (1,-0.5) dentro da precisão numérica

CA-02 — Ponto fora da área
Dado um retângulo (0,0,400,300)
Quando consulto contains para (401,150)
Então recebo false, enquanto (400,150) pertence à área

CA-03 — Navegação ancorada
Dado uma vista válida e um ponto mundial sob um pixel de âncora
Quando aplico zoom de fator 2 nessa âncora
Então o ponto continua no mesmo pixel, e pan de dx desloca o centro mundial por −dx/scale

CA-04 — Limite inferior do zoom
Dado escala positiva de 100 px/m
Quando aplico zoom com fator zero
Então a escala fica em 1e−6 px/m; a função não rejeita o fator

CA-05 — Gestos e enquadramento
Dado uma vista com escala positiva e pinças de deltas +33 e −33
Quando aplico sete pinças em cada sentido e enquadro um retângulo válido em qualquer direção
Então a escala retorna com erro relativo ≤0,1%, os bounds são ordenados e fit centraliza a seleção

CA-06 — Retângulo insuficiente
Dado pixels de início e fim cuja largura ou altura seja inferior a 5 px
Quando solicito zoom_window_bounds
Então recebo None e o helper não modifica centro nem escala

CA-07 — Encaixe e distância
Dado ponto (1.26,0.74), passo 0.5 e vetor de aproximadamente 2 graus em relação a X
Quando aplico snap de grade e ortogonal e meço (13,4) ao segmento (0,0)–(10,0)
Então obtenho (1.5,0.5), trava ortogonal preservando comprimento e distância 5

CA-08 — Grade inválida ou densa
Dado passo não positivo ou extensão/passo superior a 400 em qualquer eixo
Quando solicito grid_lines
Então recebo listas vazias; snap_to_grid com passo não positivo mantém o ponto original

CA-09 — Desenho e rótulos
Dado um handler de desenho do consumidor, uma View2D e coordenadas mundiais válidas
Quando solicito box ou segment, texto e length_label
Então pontos são convertidos em pixels, textos passam por tr e a cota usa a unidade ativa via units.format_value

CA-10 — Desenho vazio
Dado lista vazia de pontos ou linha tracejada com comprimento inferior a 1e−6 px
Quando solicito lines ou dashed respectivamente
Então lines não chama draw_lines e dashed devolve lista vazia

CA-11 — Abertura com fallback
Dado uma área/janela válida e duplicação que não produz nova janela
Quando open_window é executado
Então reutiliza a área atual, guarda restore_area_type e window_ptr/area_ptr e prepara IMAGE_EDITOR

CA-12 — Contexto sem área
Dado contexto sem área ou janela e nenhuma nova área duplicada
Quando open_window é executado
Então levanta RuntimeError com a mensagem fornecida, sem registrar ponteiros da sessão como sucesso
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-05 | 🟡 Must | Base comum de apresentação e cálculo dos editores; RF-01 a RF-04 têm testes puros |
| RF-06 | 🟡 Should | Janela dedicada tem fallback na própria área; o cálculo da vista independe dela |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/canvas2d/view.py | View2D, snap_to_grid, ortho_snap, distance_point_point/segment | 🟢 Código; test_canvas2d_view |
| caffmob_draw/canvas2d/gestures.py | pinch_factor, wheel_factor, zoom_window_bounds | 🟢 Código; test_canvas2d_gestures |
| caffmob_draw/canvas2d/draw.py | begin/end, primitivas, text, length_label, box/segment | 🟢 Código; validação visual pendente |
| caffmob_draw/canvas2d/window.py | open_window, prepare, focus_tab, close_later, identificação de área/painel | 🟢 Código; runtime de janela pendente |
| caffmob_draw/canvas2d/__init__.py | Marcador do pacote | 🟢 Sem lógica de negócio |
| caffmob_draw/walls2d/ops_editor.py | Consumo de gestos/preferência da roda e eventos | 🟢 Integração por leitura; fora da responsabilidade da unit |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_canvas2d_view test_canvas2d_gestures -v`: **15 testes aprovados**. Cobertura: conversões, pan/zoom, fit, snap/distâncias/grade, pinça, inversão da roda e zoom janela. Esses testes não cobrem todos os cenários acima, GPU ou criação/fechamento real de janelas.

## Lacunas e Pré-condições

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-71):** guardar um snapshot mínimo (`show_menus`, `show_region_header`, `show_region_ui`) em `open_window` e restaurá-lo no fechamento do fallback; a janela duplicada não muda. 🟢 (código) hoje o fechamento restaura tipo e liga menus/cabeçalho incondicionalmente, sem snapshot. Pendência de implementação: snapshot em `open_window` e restauração em `_close` (DT-02).
- 🟡 Eventos reais de touchpad, foco do painel e comportamento multi-janela exigem teste do host; os testes puros cobrem apenas os cálculos. Decisão do titular (2026-10-10, questions.md#pergunta-7): rodar `tests/blender_013_touchpad_smoke.py` e a prova manual em cada plataforma suportada e registrar em `investigation.md` §6 — decisão: medir/testar (DT-03).
- 🟢 Chamadores devem fornecer escala/retângulo adequados e números finitos. Construtor, fit e exp não têm validação geral: escala zero pode causar divisão por zero; expoente extremo pode causar OverflowError. Não atribuir tratamento inexistente ao contrato.
- 🟢 draw.end desativa blend para NONE; não restaura automaticamente o estado gráfico anterior. O consumidor deve considerar esse efeito na composição de handlers.
