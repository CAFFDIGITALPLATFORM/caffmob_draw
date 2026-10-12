# Glossário e Regras de Domínio — BlenderToMob

Este documento apresenta o mapeamento do domínio de negócio e regras implícitas do sistema **BlenderToMob**, conduzido pelo agente **Detective** na fase de Interpretação.

---

## 1. Glossário de Domínio

### 1.1 Entidades do Ambiente 3D
* **Ambiente (Scene)**: O espaço tridimensional onde o layout do projeto de marcenaria é construído (cômodo).
* **Parede (Wall)**: Entidade estrutural que delimita o ambiente. Pode ser composta por um único segmento retilíneo ou por uma polilinha contínua de múltiplos segmentos.
* **Segmento de Parede (Wall Segment)**: Um trecho reto individual de parede, caracterizado por ponto inicial, ponto final, espessura e pé-direito.
* **Piso (Floor)**: O plano horizontal de referência do ambiente. Adapta-se dinamicamente ao perímetro interno definido pelas paredes.
* **Abertura (Opening)**: Vão recortado na parede para permitir a passagem de luz ou tráfego. Subdivide-se em:
  * **Porta (Door)**: Abertura que inicia no nível do piso (peitoril fixo em 0.0).
  * **Janela (Window)**: Abertura suspensa na parede com peitoril configurável.
* **Peitoril (Sill Height)**: Distância vertical do piso até a base inferior do vão de uma janela.
* **Plano de Inserção (Insertion Plane)**: Qualquer face plana de um objeto existente (piso, paredes ou faces de outros módulos) que serve como base de alinhamento e ancoragem para a inserção de novos itens. Identificado visualmente por um sombreamento amarelo.
* **Módulo (Furniture Module / Cabinet)**: Armário de marcenaria paramétrico (balcões, aéreos ou paneleiros) composto por painéis de MDF/MDP.

### 1.2 Entidades de Produção (Plano de Corte)
* **Plano de Corte (Nesting)**: Processo algorítmico de otimização de arranjo bidimensional que organiza as peças retangulares de MDF em chapas padronizadas para minimizar a sobra de material.
* **Chapa (Sheet)**: Painel de matéria-prima (MDF/MDP) nas dimensões nominais de produção (padrão $2750 \times 1830$ mm).
* **Refilo (Sheet Margins)**: Faixa de margem de segurança cortada nas quatro bordas de uma chapa de MDF para esquadrejar a placa (padrão 10mm). A área de nesting útil é reduzida por esta margem.
* **Kerf (Saw Blade Thickness)**: A espessura da lâmina da serra de corte que é consumida (virando pó) a cada divisão de peças na chapa (padrão 4mm).
* **Sentido da Fibra/Veio (Wood Grain Direction)**: Orientação das texturas ou fibras da madeira no MDF:
  * `NONE`: Peça lisa ou sem veio definido; pode ser rotacionada em 90° livremente para otimizar o encaixe.
  * `VERTICAL` / `HORIZONTAL`: Exige que as dimensões da peça permaneçam alinhadas à fibra da chapa para manter a estética visual.

---

## 2. Regras de Negócio e Domínio

### 2.1 Regras de Paredes e Piso
* **Dependência do Piso (R-01)**: O piso do ambiente é uma entidade opcional no menu de interface, que **somente** é exibido se houver ao menos um segmento de parede ativo na cena (poll: `any(WALL)`).
* **Ajuste Conformal de Piso (R-02)**: O piso deve se ajustar automaticamente ao perímetro interno delimitado pelos vértices inferiores das paredes. Isso é computado via fecho convexo Graham Scan.
* **Sentido de Orientação de Paredes (R-03)**: A construção de paredes no sentido horário (`RIGHT`) ou anti-horário (`LEFT`) determina o lado para o qual a espessura da parede será extrudada em relação à linha guia desenhada pelo cursor do mouse.

### 2.2 Regras de Snapping e Movimentação de Aberturas
* **Aderência ao Segmento (R-04)**: Uma porta ou janela está vinculada fisicamente a um segmento de parede hospedeiro. Ela herda a rotação Z e a espessura do segmento de parede. O cortador boolean possui largura igual à espessura da parede multiplicada por 3 para garantir transpasse completo e furo limpo.
* **Movimento Constrangido (R-05)**: Durante o arrasto de uma abertura no modo de inserção, a sua posição é projetada e travada no plano vertical da parede ativa. O usuário só consegue alterar a coordenada ao longo do comprimento da parede (comprimento X local) e a altura vertical (peitoril Z local).
* **Clamping de Limites (R-06)**: A abertura não pode se deslocar para fora do segmento de parede ativo. Sua posição de deslocamento local no eixo X é limitada entre $0.0$ (início do segmento) e o comprimento máximo do segmento.
* **Transição entre Segmentos (R-07)**: Caso o usuário mova o cursor em direção a um segmento de parede vizinho ou quina, o sistema recalcula a menor distância 2D e transfere a abertura para a parede adjacente, rotacionando e readequando o preview à espessura da nova parede.
* **Sill Fixo de Portas (R-08)**: Portas de ambiente possuem peitoril fixado em `0.0 mm`, impedindo deslocamento vertical. Janelas podem deslizar verticalmente entre `0.0 mm` e a altura total da parede subtraída da altura do vão.

### 2.3 Regras de Otimização de Plano de Corte
* **Precedência de Área (R-09)**: O algoritmo de nesting prioriza o encaixe de peças maiores no início das prateleiras (shelves) da chapa de MDF para evitar que o espaço útil seja fragmentado por retalhos pequenos.
* **Corte Guilhotinado (R-10)**: O arranjo das peças na prateleira da chapa respeita cortes transversais completos de ponta a ponta (guilhotina), dividindo a chapa em faixas horizontais de altura equivalente à peça mais alta contida na fileira.

---

## 3. Matriz de Certeza e Escala de Confiança

Como o projeto é executado localmente sem repositório Git inicializado para análise de commits históricos, a escala de confiança apoia-se estritamente na engenharia reversa do código-fonte Python:

* **Conexão Convexa do Piso (R-02)**: 🟢 CONFIRMADO (Lógica geométrica explícita implementada em `mesh_gen.py` via `_convex_hull_2d`).
* **Snapping de Portas/Janelas (R-04 a R-08)**: 🟢 CONFIRMADO (Máquina de estado e cálculos de distância e projeção de planos codados em `opening_builder.py`).
* **Lógica de Guilhotina e Refilo (R-09 e R-10)**: 🟢 CONFIRMADO (Algoritmo Next-Fit Decreasing e espaçamento kerf implementados em `nesting.py`).


## Re-extração 2026-10-10 — domínio atual CAFFMob Draw

Esta seção atualiza a fotografia de julho, preservada acima. Há histórico Git disponível: a afirmação antiga de ausência de Git não vale para esta re-extração. A referência atual é o pacote `caffmob_draw/` da árvore de trabalho; alterações locais podem ser posteriores ao HEAD `83a6863`.

### Glossário adicional

| Termo | Significado atual | Fonte |
|---|---|---|
| Padrão dimensional | Definição versionada de medidas em mm, componentes e linhas; origina módulos | standards/model.py; api.py |
| Padrão próprio | Módulo com overrides, montagem diferente ou espessura externa explícita | standards/apply_core.py:is_own |
| Rascunho | Estado editável antes de confirmar; paredes e armários têm estratégias distintas | walls2d/props.py; cabinet_editor/state.py |
| Subvão | Folha de árvore de divisões, endereçada por caminho estável e dimensão livre | cabinet_editor/divisions.py |
| Agregado | Item convertido/importado, vinculado a módulo ou livre, com escopo e limites | aggregates/props.py; limits.py |
| Plano de inserção | Referencial local de face usado para alinhar e mover | move_over/insertion_plane.py |
| Colisão de corpo | Checagem geométrica entre volumes e regras de escopo | collision/scan.py; rules.py |
| Interferência de abertura | Amostragem de movimento de frentes; distinta da colisão de corpo | inspection/interference.py |
| Front | Adaptador de frente móvel com estado, commit e geometria comum | inspection/fronts.py |
| Biblioteca de módulos | Geometria paramétrica com manifesto de personalização | customize/library_io.py |
| Biblioteca de objetos | Objetos/grupos salvos com manifesto próprio; acabamento aplicado na cena | object_library/item_io.py; manifest.py |
| Geometria livre | Placa/caixa opcionalmente produtiva, sem módulo proprietário | geometry_free/mesh.py; cutting/part_sources.py |
| Gate legado | Preferência de visibilidade; não autorização de segurança | legacy/gate.py |

### Catálogo de regras extraídas

🟢 **CONFIRMADO** significa presença no código, não comprovação de execução no Blender. As linhas abaixo são transcritas do registro de escavação com sua fonte; linguagem de intenção em comentários deve ser confrontada com as limitações indicadas na análise técnica.

#### canvas2d

| ID | Regra | Evidência |
|---|---|---|
| RN-CANVAS2D-01 | 🟢 Zoom ancorado: o ponto do mundo sob o cursor não se move na tela | `caffmob_draw/canvas2d/view.py:39` |
| RN-CANVAS2D-02 | 🟢 Escala só tem piso técnico 1e-6 px/m; não há teto de zoom (013, Q1) | `caffmob_draw/canvas2d/view.py:42` |
| RN-CANVAS2D-03 | 🟢 Trava ortogonal a até 2,5° de 0/90/180/270° | `caffmob_draw/canvas2d/view.py:77` |
| RN-CANVAS2D-04 | 🟢 Grade não é desenhada quando extensão/passo > 400 em algum eixo (até ~402 linhas desenhadas, contando as bordas) _(Revisão cruzada 2026-10-10: view.py:64 testa `(x1 - x0) / step > 400`, não a contagem de linhas)_ | `caffmob_draw/canvas2d/view.py:64` |
| RN-CANVAS2D-05 | 🟢 Pinça exponencial: ida e volta devolvem a escala; delta 0 = fator 1 | `caffmob_draw/canvas2d/gestures.py:23` |
| RN-CANVAS2D-06 | 🟢 Roda obedece à preferência invert_zoom_wheel do Blender | `caffmob_draw/canvas2d/gestures.py:28` |
| RN-CANVAS2D-07 | 🟢 Zoom janela com lado < 5 px não muda a vista | `caffmob_draw/canvas2d/gestures.py:33` |
| RN-CANVAS2D-08 | 🟢 A tela 2D é um Image Editor sem imagem, sem cabeçalho, menus nem barra de ferramentas; só a região lateral | `caffmob_draw/canvas2d/window.py:51` |
| RN-CANVAS2D-09 | 🟢 Eventos sobre o painel lateral passam direto ao Blender (sobreposição de regiões) | `caffmob_draw/canvas2d/window.py:32` |
| RN-CANVAS2D-10 | 🟢 A janela do editor fecha num timer fora do modal; se o editor ocupou a área atual, devolve o tipo original | `caffmob_draw/canvas2d/window.py:101` |

#### walls2d

| ID | Regra | Evidência |
|---|---|---|
| RN-WALLS2D-01 | 🟢 Os nós são a face interna (medida real); a externa é deslocada pela espessura com esquadria t·tan(meia virada) | `caffmob_draw/walls2d/model.py:6` |
| RN-WALLS2D-02 | 🟢 Limites RN-18: comprimento 0,01–100 m, espessura 0,01–2 m, pé-direito 0,5–10 m | `caffmob_draw/walls2d/model.py:24` |
| RN-WALLS2D-03 | 🟢 Divisória tem espessura padrão 100 mm; Mureta tem altura padrão 1.100 mm | `caffmob_draw/walls2d/model.py:22` |
| RN-WALLS2D-04 | 🟢 Contorno fechado leva a espessura para fora (anti-horário → direita) | `caffmob_draw/walls2d/model.py:125` |
| RN-WALLS2D-05 | 🟢 Mudar o pé-direito inicial arrasta o final | `caffmob_draw/walls2d/model.py:234` |
| RN-WALLS2D-06 | 🟢 Com Bloquear Ângulo, o nó só anda na direção do trecho que chega nele | `caffmob_draw/walls2d/model.py:216` |
| RN-WALLS2D-07 | 🟢 Cadeia aberta de 3+ trechos com o fim a 10 mm do início fecha (no desenho e como rede de segurança no OK) | `caffmob_draw/walls2d/model.py:292` |
| RN-WALLS2D-08 | 🟢 Nada muda no 3D até o OK; Cancelar com rascunho sujo pergunta; Ctrl+Z fica no rascunho (até 100 passos) | `caffmob_draw/walls2d/history.py:14` |
| RN-WALLS2D-09 | 🟢 Mira: ímã do início (15 px) → vértice (9 px) → ortogonal 2,5° (fixa um eixo) → alinhamento X/Y só no eixo não fixado (8 px, Shift desliga) → grade (só sem trava) _(Revisão cruzada 2026-10-10: ops_editor.py:resolve_point linhas 389-404; a docstring lista alinhamento antes da ortogonal)_ | `caffmob_draw/walls2d/ops_editor.py` |
| RN-WALLS2D-10 | 🟢 A direção do lápis só muda por clique ou setas; o mouse sozinho nunca a muda | `caffmob_draw/walls2d/direction.py:3` |
| RN-WALLS2D-11 | 🟢 O Home Builder 5 põe a espessura à esquerda: Direção direita aplica a cadeia invertida | `caffmob_draw/walls2d/apply.py:116` |
| RN-WALLS2D-12 | 🟢 Parede que gira mais de 90° no OK mantém os filhos no mundo e re-hospeda as aberturas (desloca −Dim X, inverte lado e mão da porta) | `caffmob_draw/walls2d/apply.py:140` |
| RN-WALLS2D-13 | 🟢 OK avisa (e só aplica na 2ª chamada) quando itens não cabem, módulos ficam em trechos apagados ou o pé-direito difere do projeto | `caffmob_draw/walls2d/ops_editor.py#BTM_OT_WallEditorOk` |
| RN-WALLS2D-14 | 🟢 Módulos de trechos apagados ficam soltos no lugar por padrão; portas, janelas e cotas saem com a parede | `caffmob_draw/walls2d/apply.py:53` |
| RN-WALLS2D-15 | 🟢 Mureta, meia-parede e parede falsa não acompanham o pé-direito do projeto (tolerância 1 mm) | `caffmob_draw/walls2d/heights.py:12` |
| RN-WALLS2D-16 | 🟢 Pisos e tetos existentes são refeitos trocando só a malha, uma sala fechada por piso, na ordem dos nomes | `caffmob_draw/walls2d/apply.py:211` |
| RN-WALLS2D-17 | 🟢 Medidas do painel na unidade do projeto, sem arredondar; sem sufixo vale a unidade do projeto | `caffmob_draw/walls2d/props.py:243` |

#### move_over

| ID | Regra | Evidência |
|---|---|---|
| RN-MOVE_OVER-01 | 🟢 Referencial de B: X largura, Y profundidade com a frente em Y mínimo (bibliotecas e módulo rápido têm frente em −Y e fundo em Y ≈ 0), Z altura; parede como B tem a face em Y = 0 | `caffmob_draw/move_over/align.py:3-7` |
| RN-MOVE_OVER-02 | 🟢 A (arrastado) e B (referência) são as raízes do classificador: frentes e peças contam como o módulo; só B pode ser parede (RN-05) | `caffmob_draw/move_over/scene.py:41-44` |
| RN-MOVE_OVER-03 | 🟢 A assume a rotação de B antes do alinhamento (RN-08); a rotação pedida é composta por cima, pelo centro da base de A (D-21) | `caffmob_draw/move_over/scene.py:107-115` |
| RN-MOVE_OVER-04 | 🟢 Se B é parede ou está numa parede, A vira filho dessa parede (mantendo a posição no mundo) para as cotas continuarem valendo; Cancelar devolve o pai original | `caffmob_draw/move_over/scene.py:149-159` |
| RN-MOVE_OVER-05 | 🟢 Linhas de profundidade e altura a 0/30/50/75/100% de B; com parede como B só a linha da face (fundo de A na face) | `caffmob_draw/move_over/align.py:19,69-79` |
| RN-MOVE_OVER-06 | 🟢 Um clique combina no máximo um alvo por eixo (lado + profundidade/altura); clicar acima do topo de B na frontal empilha | `caffmob_draw/move_over/align.py:91-112` |
| RN-MOVE_OVER-07 | 🟢 Com o modo ligado o botão direito nunca abre o menu de contexto, mesmo sem objeto movível sob o cursor (RN-10); desligado, o evento segue ao Blender | `caffmob_draw/move_over/ops_drag.py:62-72` |
| RN-MOVE_OVER-08 | 🟢 Arraste abre a janela só com deslocamento Manhattan ≥ 5 px e referência válida ≠ A | `caffmob_draw/move_over/ops_drag.py:112-118` |
| RN-MOVE_OVER-09 | 🟢 Com Evitar Sobreposição (scene.btm_settings.collision_global) o primeiro Confirmar só avisa os módulos sobrepostos (até 4 nomes); o segundo grava (RN-11) | `caffmob_draw/move_over/ops_dialog.py:286-297` |
| RN-MOVE_OVER-10 | 🟢 Trocar Relativa/Absoluta é só exibição: nada se move | `caffmob_draw/move_over/ops_dialog.py:335-337` |
| RN-MOVE_OVER-11 | 🟢 Passo não aceita zero nem negativo; X, profundidade e altura aceitam negativos; Rotação aceita vírgula e remove ° | `caffmob_draw/move_over/ops_dialog.py:263-269` |
| RN-MOVE_OVER-12 | 🟢 Posição salva = distância do canto de A ao canto de B do mesmo lado (centro de A decide o lado) + frente + base + rotação; persiste na cena; só as 4 últimas aparecem | `caffmob_draw/move_over/reposition.py:49-70; ops_dialog.py:37,247` |
| RN-MOVE_OVER-13 | 🟢 Substituir alinha o novo módulo pelo canto de A do lado de B em que A estava, pela frente e pela base; herda rotação e pai de A; A e descendentes são apagados | `caffmob_draw/move_over/ops_substitute.py:38-63` |
| RN-MOVE_OVER-14 | 🟢 Mover na Parede só altera X local (ou Z com Shift, nunca abaixo de 0); o afastamento da parede não muda; com Evitar Sobreposição para no vizinho da mesma faixa e nas pontas (RF-34) | `caffmob_draw/move_over/ops_move_on_wall.py:81-93` |
| RN-MOVE_OVER-15 | 🟢 Plano de inserção da sessão substitui o piso Z = 0 no snap de inserção/movimento, exceto em vista ortográfica lateral (RN-17, D-24) | `caffmob_draw/move_over/insertion_plane.py:59-65; caffmob_draw/hb_snap.py:165-171` |
| RN-MOVE_OVER-16 | 🟢 Atalho do botão direito registrado também nos 19 mapas de modo da viewport, senão o menu captura o clique antes do 3D View (D-29, A001) | `caffmob_draw/move_over/ops_drag.py:128-147` |

#### measure

| ID | Regra | Evidência |
|---|---|---|
| RN-MEASURE-01 | 🟢 Referencial da parede: X ao longo (0 = início), Z do piso, Y com a face da parede em 0 e módulos da frente em Y < 0 | `caffmob_draw/measure/cotas.py:3-4` |
| RN-MEASURE-02 | 🟢 Só obstáculos na mesma faixa de altura (sobreposição estrita, RN-12) limitam as cotas laterais; os que cruzam o módulo em X são ignorados | `caffmob_draw/measure/cotas.py:21-37` |
| RN-MEASURE-03 | 🟢 Aplicar uma cota move o módulo e preserva as dimensões (RN-04); negativo, abaixo do piso ou fora da parede levantam ValueError 'Valor Inválido' | `caffmob_draw/measure/cotas.py:56-82` |
| RN-MEASURE-04 | 🟢 Módulo livre (sem parede ou do lado de trás) só tem cotas inferior e superior; aplicar as outras é inválido | `caffmob_draw/measure/cotas.py:51-53; scene_cotas.py:105-108` |
| RN-MEASURE-05 | 🟢 Lado da frente = rotação Z própria < 0,01 rad e location.y < meia espessura da parede | `caffmob_draw/measure/scene_cotas.py:42-45` |
| RN-MEASURE-06 | 🟢 Pé-direito: home_builder.ceiling_height da cena principal; senão Height da parede; senão 2,6 m | `caffmob_draw/measure/scene_cotas.py:55-67` |
| RN-MEASURE-07 | 🟢 Dimensões: Dim X/Y/Z do GN quando home_builder.mod_name existe; senão btm_cabinet; senão root.dimensions | `caffmob_draw/measure/scene_cotas.py:20-32` |
| RN-MEASURE-08 | 🟢 Deslizar com Evitar Sobreposição para no vizinho da mesma faixa e nas pontas da parede; sem, só dentro da parede (RF-34) | `caffmob_draw/measure/cotas.py:85-94` |
| RN-MEASURE-09 | 🟢 Anotações 2D e snap lines não são obstáculos | `caffmob_draw/measure/scene_cotas.py:97-98` |

#### selection

| ID | Regra | Evidência |
|---|---|---|
| RN-SELECTION-01 | 🟢 Precedência do classificador (RN-01): anotação; frente/peça/módulo (frente = primeiro ancestral abaixo da raiz com marca de frente); depois porta, janela, abertura BTM, geometria, obstáculo, parede HB, parede BTM, piso, teto; senão OTHER | `caffmob_draw/selection/classify.py:94-132` |
| RN-SELECTION-02 | 🟢 btm_plane.object_kind só vale quando foi gravado de propósito (is_property_set); o padrão WALL do enum não torna um objeto parede (BUG-TBY3) | `caffmob_draw/selection/classify.py:44-56` |
| RN-SELECTION-03 | 🟢 Mover Sobre: movível = módulo (para frente e peça), geometria, obstáculo ou grupo de peças solto; referência = o mesmo mais paredes; porta, janela, piso, teto e cota nunca (RN-05) | `caffmob_draw/selection/classify.py:145-165` |
| RN-SELECTION-04 | 🟢 Raiz do componente (D-01): vão > cota solta > grudado/agregado próprio abaixo do módulo (RN-03) > módulo se modo gabinete (módulo rápido sempre) > item da biblioteca de objetos > grupo de peças mais alto > o próprio | `caffmob_draw/selection/component.py:53-74` |
| RN-SELECTION-05 | 🟢 Folha LEAF cujo parent_ref é grupo FRAME é peça da esquadria, não componente próprio | `caffmob_draw/selection/component.py:35-46` |
| RN-SELECTION-06 | 🟢 Excluir leva a subárvore inteira, filhos antes dos pais; grudados nunca saem (soltos no lugar); keep_aggregates preserva agregados próprios e peças; parede, piso e teto saem sozinhos | `caffmob_draw/selection/component.py:114-146` |
| RN-SELECTION-07 | 🟢 O normalizador não age com interruptor desligado, fora do modo objeto ou com modal da extensão/transform rodando; compara assinatura (nomes + ativo) para sair cedo; trava contra reentrada | `caffmob_draw/selection/component_select.py:136-157` |
| RN-SELECTION-08 | 🟢 Sem a interface herdada (legacy gate) todo módulo sobe; com ela, FRAMELESS sobe só em 'Cabinets', FACE_FRAME e CLOSETS sobem com o modo desligado ou em 'Cabinets'/'Starters' (D-07; 012 D-05) | `caffmob_draw/selection/component_select.py:44-64` |
| RN-SELECTION-09 | 🟢 Alt + clique seleciona só a peça e a marca isenta; Alt + Shift soma; clique sem modificador limpa isenções; isenções caem quando a peça deixa de estar selecionada e no load_post | `caffmob_draw/selection/component_pick.py:37-65; component_select.py:108-112,160-165` |
| RN-SELECTION-10 | 🟢 Interruptor Seleção por componente é salvo no arquivo e ligado por padrão; religar promove a seleção atual na próxima atualização | `caffmob_draw/selection/component_props.py:14-39` |
| RN-SELECTION-11 | 🟢 Dimensões editáveis: módulo (largura, altura, profundidade); porta e janela HB (largura, altura); o resto só leitura. Limites: largura/altura 0,01–10 m, profundidade 0,005–10, peitoril 0–5 (porta sempre 0) | `caffmob_draw/selection/editing.py:24-26,45-53,101-105` |
| RN-SELECTION-12 | 🟢 Medida manual num módulo frameless registra override (standards/sync.add_override) e roda run_calc_fix | `caffmob_draw/selection/editing.py:86-92` |
| RN-SELECTION-13 | 🟢 Parede: só HB é editável; comprimento 0,05–100, pé-direito 0,5–10, espessura 0,01–2; mudar o pé-direito inicial arrasta o final (RN-18) e refaz esquadrias | `caffmob_draw/selection/editing.py:110-125` |
| RN-SELECTION-14 | 🟢 Porta é medida e redimensionada pela folha (conversão furo ↔ folha de doors_windows), não pela caixa | `caffmob_draw/selection/element_size.py:56-59; resize.py:91-96` |
| RN-SELECTION-15 | 🟢 Redimensionar: largura 0,01–100 m; parede só HB; piso e teto nunca; elementos sem largura própria são esticados em X pela escala; agregados do pai e das peças são esticados e reposicionados na proporção, exceto folhas LEAF e agregados em face lateral (só reposicionados) | `caffmob_draw/selection/resize.py:20-33,47-66,105-129` |

#### openings

| ID | Regra | Evidência |
|---|---|---|
| RN-OPENINGS-01 | 🟢 A medida da porta é a da folha; o furo = folha + 2 × 49 mm de largura e + 59 mm de altura (80 × 210 → 898 × 2159); dupla soma as duas folhas e 3 mm | `caffmob_draw/openings/door_core.py:56-64` |
| RN-OPENINGS-02 | 🟢 Folha de 40 mm a 8 mm do piso; marco de 46 mm com a profundidade da parede; ferragens e perfis de tamanho fixo (largura maior não distorce) | `caffmob_draw/openings/door_core.py:18-25,236-255` |
| RN-OPENINGS-03 | 🟢 Porta dupla: folha 0 com dobradiça à esquerda e fechadura, folha 1 à direita sem fechadura; vão aberto só tem marco e guarnições | `caffmob_draw/openings/door_core.py:176-185` |
| RN-OPENINGS-04 | 🟢 Dobradiças e giro ficam no lado side da parede: NEG_Y quando Swing Inside (ou símbolo ausente); Is Left do símbolo põe a dobradiça à direita (hinge RIGHT) | `caffmob_draw/openings/sync.py:74-80,189-191` |
| RN-OPENINGS-05 | 🟢 Janela de correr: 2 folhas em trilhos diferentes com sobreposição de 50 mm, vidro de 4 mm, peitoril de granito saindo 30 mm; folha 0 corre para +X e folha 1 para −X até o batente | `caffmob_draw/openings/window_core.py:27-70; sync.py:184-188` |
| RN-OPENINGS-06 | 🟢 A montagem só é refeita quando a assinatura (tipo, Dim X/Y/Z, lado, sentido, versão) muda ou com force; abertura das folhas e peças de produção são restauradas | `caffmob_draw/openings/sync.py:63-68,144-203` |
| RN-OPENINGS-07 | 🟢 A caixa continua sendo o furo que corta a parede; vira arame e o texto DOOR/WINDOW fica oculto; o símbolo 2D permanece | `caffmob_draw/openings/sync.py:131-142` |
| RN-OPENINGS-08 | 🟢 Hierarquia: caixa → grupo FRAME (marco) → grupo LEAF por folha → ferragens da folha; só os Empties são alinhados aos eixos da caixa; as malhas do marco levam OPENING_FRAME_PROP para a folha não esbarrar nele | `caffmob_draw/openings/sync.py:163-182` |
| RN-OPENINGS-09 | 🟢 Abertura máxima da folha de giro 90° | `caffmob_draw/openings/sync.py:26,192` |
| RN-OPENINGS-10 | 🟢 Atualizar portas e janelas nunca roda sozinho: a barra lateral só avisa quando há caixas sem montagem ou de versão anterior | `caffmob_draw/openings/ops.py:1-9,27-34; sync.py:209-213` |
| RN-OPENINGS-11 | 🟢 Tecla I inverte Is Left (dobradiça de lado) numa porta com símbolo e refaz a montagem mantendo o lado para onde abre; sem porta o I segue o padrão do Blender | `caffmob_draw/openings/ops.py:47-71` |
| RN-OPENINGS-12 | 🟢 Materiais criados uma vez por arquivo e reaproveitados pela marca btm_opening_material; nogueira com texturas do pacote; vidro BLENDED com alpha 0,25 | `caffmob_draw/openings/materials.py:16-26,59-81` |
| RN-OPENINGS-13 | 🟢 Região: porta encosta no piso (peitoril 0) e vai até a borda de cima; janela usa a borda de baixo como peitoril; largura e altura exatas, sem folga; recusa EMPTY (< 1 mm), OUTSIDE, TOO_TALL (tolerância 5 mm) ou OVERLAP (interseção estrita 1 mm) | `caffmob_draw/openings/region_core.py:35-50` |
| RN-OPENINGS-14 | 🟢 Marcar região: primeiro clique escolhe parede e face (BACK se y > espessura/2); cantos na grade de 10 mm (Shift 1 mm) presos à parede; região é estado de sessão por nome da parede e cai no load_post | `caffmob_draw/openings/region.py:120-136,157-197; region_props.py:1-6,26-35` |

#### aggregates

| ID | Regra | Evidência |
|---|---|---|
| RN-AGGREGATES-01 | 🟢 O agregado nunca sai do contorno da face do pai (u, v ≥ 0 e ≤ tamanho do pai − tamanho do agregado; maior que a face fica em 0) e afunda no máximo a espessura do pai (offset ≥ −espessura) (RN-08, RN-09) | `caffmob_draw/aggregates/limits.py:46-63` |
| RN-AGGREGATES-02 | 🟢 A posição é sempre recalculada de u/v/offset e o valor ajustado é gravado de volta; quando o pai muda de tamanho o handler reposiciona os agregados | `caffmob_draw/aggregates/apply.py:51-105` |
| RN-AGGREGATES-03 | 🟢 Converter exige malha ou grupo, pai ativo distinto e não descendente; objeto grudado e pai folha são recusados; desconverter devolve pai e matriz originais (RN-07, RN-12) | `caffmob_draw/aggregates/convert.py:17-84` |
| RN-AGGREGATES-04 | 🟢 Abrir a folha para no primeiro contato (varredura + bissecção); fechar é livre fora da esquadria; na esquadria fechar também testa e não passa do batente imposto pela outra folha (RN-11a, D-10) | `caffmob_draw/aggregates/sweep.py:12-47; leaf.py:245-294` |
| RN-AGGREGATES-05 | 🟢 Abrir nunca altera a malha: o pivô gira ou desliza; a pose fechada fica em btm_leaf_rest; sentido OUT abre para −Y do pai (a frente dos módulos) | `caffmob_draw/aggregates/leaf.py:1-28,100-111` |
| RN-AGGREGATES-06 | 🟢 Folha de correr na esquadria: sentido padrão para o próprio lado; curso = distância livre até a esquadria (teto do travel); pouco curso = menos de 10% da largura da folha (RN-07, RN-07a, D-08, D-09) | `caffmob_draw/aggregates/leaf.py:170-203; slide_limits.py:13-26; props.py:59-64` |
| RN-AGGREGATES-07 | 🟢 Contato: a folha é a caixa encolhida 1 mm; saem do teste a folha, pivô, descendentes, folhas irmãs e pai (esquadria) ou a raiz do módulo do pai; arame, bounds, cortadores, anotações, invisíveis e o marco da própria porta real | `caffmob_draw/aggregates/collision.py:25-95` |
| RN-AGGREGATES-08 | 🟢 Perfurar cria uma caixa cortadora do volume afundado (1 mm além da face) e um BOOLEAN DIFFERENCE EXACT no pai; a malha do pai nunca é alterada; furo real só com pai GeoNodeCutpart e face ±Z, via CPM_CUTOUT exportado em machining (RN-10, D-13, D-14) | `caffmob_draw/aggregates/perforate.py:30-38,91-161` |
| RN-AGGREGATES-09 | 🟢 Peça de produção: o agregado entra no plano de corte como placa com as medidas ordenadas da caixa (RN-13) | `caffmob_draw/aggregates/production.py:9-22` |
| RN-AGGREGATES-10 | 🟢 Grupo de peças: Empty no centro da base da caixa; peças filhas sem mover; desfazer devolve ao pai original na posição atual (RN-04); kind PLAIN/FRAME/LEAF | `caffmob_draw/aggregates/group.py:55-103; group_props.py:10-14` |
| RN-AGGREGATES-11 | 🟢 Sugestão de grupos: nomes que começam por Folha/Leaf/Sash agrupados pelos dois primeiros tokens; o resto é a Esquadria; sufixos .001 ignorados (RN-05) | `caffmob_draw/aggregates/grouping.py:10-39` |
| RN-AGGREGATES-12 | 🟢 Instalar na parede só em parede HB: jaula IS_WINDOW_BP com Dim X/Z da esquadria e Dim Y da parede, peitoril padrão 1,0 m, x preso ao comprimento; esquadria centrada por drivers Dim X/2 e Dim Y/2; vão cortado (RN-03, D-12 a D-14) | `caffmob_draw/aggregates/install.py:40-87` |
| RN-AGGREGATES-13 | 🟢 Unidade de importação automática: maior medida > 50 unidades em escala 1 = milímetros; a escala vai para a malha; glTF é métrico (RN-01, D-01) | `caffmob_draw/aggregates/import_units.py:7-18; ops_import.py:126-146` |
| RN-AGGREGATES-14 | 🟢 Arquivo importado com 2+ malhas vira um componente (grupo PLAIN com o nome do arquivo; Empty raiz vira o grupo) (011 RN-02, D-09) | `caffmob_draw/aggregates/ops_import.py:163-183` |
| RN-AGGREGATES-15 | 🟢 SketchUp: glTF Y-up → Z-up por (x, −z, y); um grupo por instância seguindo a hierarquia; figuras de escala ignoradas e contadas; instâncias repetidas recebem a primitiva mais próxima; versos duplicados descartados; contêiner com um filho colapsa; materiais com nome do SketchUp e reaproveitados por nome\|cor\|imagem (RN-07 a RN-09, RN-13, RN-14) | `caffmob_draw/aggregates/skp_core.py:59-179; skp_build.py:41-69` |
| RN-AGGREGATES-16 | 🟢 Um .skp que não abre não cria nada e o relatório diz o motivo e a alternativa (glTF, OBJ, FBX); falha na montagem desfaz o criado | `caffmob_draw/aggregates/ops_import.py:50-83; skp.py:20-36; skp_core.py:204-206` |
| RN-AGGREGATES-17 | 🟢 X/Delete com agregados: pergunta se eles vão junto só quando há agregados próprios; grudados são soltos no lugar com aviso; vãos tiram o furo da parede; remoção em lote (D-05, D-06; 012) | `caffmob_draw/aggregates/ops_aggregate.py:201-294` |

#### collision

| ID | Regra | Evidência |
|---|---|---|
| RN-COLLISION-01 | 🟢 Encostar não é colisão: sobreposição até TOLERANCE = 1 mm é ignorada (RN-11) | `caffmob_draw/collision/rules.py:18,103-107` |
| RN-COLLISION-02 | 🟢 Não contam (RN-12): dois estáticos; item com Colisão: Desativada; itens do mesmo módulo (mesmo group); pares ligados (agregado × pai, grudado × hospedeiro, porta/janela × parede) | `caffmob_draw/collision/rules.py:63-73; scan.py:68-80` |
| RN-COLLISION-03 | 🟢 Ordem das ocorrências (RN-13): penetração em parede/obstáculo, depois colisão entre itens, depois piso/teto; dentro do tipo maior profundidade primeiro; empate pelo nome | `caffmob_draw/collision/rules.py:28-32,115-116` |
| RN-COLLISION-04 | 🟢 Um par gera uma ocorrência; name_a é sempre o item móvel (estático vai para b; entre iguais, o de nome menor fica em a) e push é o deslocamento de a | `caffmob_draw/collision/rules.py:103-112` |
| RN-COLLISION-05 | 🟢 Classificação: par com parede ou obstáculo é WALL mesmo que envolva piso/teto; par com piso ou teto é FLOOR_CEILING; o resto ITEM | `caffmob_draw/collision/rules.py:76-82` |
| RN-COLLISION-06 | 🟢 Peças e frentes não entram sozinhas: a caixa da raiz do módulo cobre o módulo; cortadores, anotações, cotas, obj_x, ocultos e malhas WIRE/BOUNDS ficam de fora | `caffmob_draw/collision/scan.py:24,35-41,92-94,110` |
| RN-COLLISION-07 | 🟢 Pares com parede, obstáculo, abertura, agregado ou malha solta são confirmados pela malha real (BVHTree.overlap), respeitando o vão de uma porta na parede (D-13) | `caffmob_draw/collision/scan.py:25,83-112,165-172` |
| RN-COLLISION-08 | 🟢 Chave global btm_settings.collision_global desligada: nada roda e o painel diz 'Colisão desligada' (D-18) | `caffmob_draw/collision/scan.py:175-177; ops_collision.py:26-28; panels.py:26-29` |
| RN-COLLISION-09 | 🟢 A interface nunca diz 'sem colisões' com resultado desatualizado ou com erro; falha de cálculo vira state.error visível (RN-14, RF-25) | `caffmob_draw/collision/scan.py:219-223; panels.py:30-45` |
| RN-COLLISION-10 | 🟢 Ao soltar um movimento (assentar do grudar) o sistema refaz só os pares dos movidos e seus descendentes, avisa 'X colide com Y' e não move nada (RF-23, D-16) | `caffmob_draw/collision/scan.py:230-263` |
| RN-COLLISION-11 | 🟢 Resultado fica desatualizado quando um item vigiado (ou algo dentro dele) muda de posição ou geometria; reverificar os movidos tira-os da conta (D-15) | `caffmob_draw/collision/stale.py:19-56` |
| RN-COLLISION-12 | 🟢 'Afastar até encostar' move name_a por push; item grudado só anda no plano da face do hospedeiro e, se o empurrão é só pela normal, recusa (D-19) | `caffmob_draw/collision/ops_collision.py:105-129` |
| RN-COLLISION-13 | 🟢 RF-26 pede prévia antes de afastar; o código aplica direto com um passo de desfazer | `caffmob_draw/collision/ops_collision.py:97-129` |

#### stick

| ID | Regra | Evidência |
|---|---|---|
| RN-STICK-01 | 🟢 Face plana = todos os vértices do polígono a ≤ 0,5 mm do plano; face não plana recusa com 'A face não é plana' (RN-05) | `caffmob_draw/stick/frame.py:24,159-168; link.py:102-106` |
| RN-STICK-02 | 🟢 Dois tipos de face: BOX_SIDE quando a normal está a ≤ 1° de um lado da caixa e o ponto a ≤ 0,5 mm desse lado (acompanha medida do hospedeiro); senão PLANE (plano fixo, acompanha mover/girar) (D-02) | `caffmob_draw/stick/frame.py:171-186` |
| RN-STICK-03 | 🟢 Ao grudar, em face de pé o fundo do item (+Y local) encosta na face; em face deitada (\|n·Z\| ≥ 0,7) a base encosta; o item gira para a normal e fica a distance 0 (RF-11) | `caffmob_draw/stick/frame.py:189-192; link.py:49-75,96-128` |
| RN-STICK-04 | 🟢 Vínculo = item filho do hospedeiro com matrix_parent_inverse identidade + btm_stick; o hospedeiro é a raiz do que foi clicado (D-03) | `caffmob_draw/stick/link.py:19-26,78-85` |
| RN-STICK-05 | 🟢 Não gruda: nele mesmo, num filho dele, nem item agregado (desconverter antes) | `caffmob_draw/stick/link.py:29-39` |
| RN-STICK-06 | 🟢 Item grudado move só no plano da face: qualquer movimento livre é projetado de volta mantendo distance; u/v seguem a posição em que foi solto (RN-06, RF-13) | `caffmob_draw/stick/apply.py:128-141; ops_stick.py:198-209` |
| RN-STICK-07 | 🟢 Hospedeiro que muda de medida reposiciona os grudados a partir de u/v/distance; u/v partem da origem local, que não se move ao redimensionar (RN-07, RN-08a, RF-14) | `caffmob_draw/stick/apply.py:254-264; frame.py:6-8` |
| RN-STICK-08 | 🟢 Item que foi parar além da espessura do hospedeiro troca para a face oposta em vez de ser puxado através dele | `caffmob_draw/stick/apply.py:144-165` |
| RN-STICK-09 | 🟢 Hospedeiro apagado ou pai trocado: o item fica onde estava no mundo, sem vínculo, e a barra de status avisa 'Vínculo perdido' (RN-08, RF-15); centro da pegada fora do retângulo da face (folga 1 mm) liga out_of_face e avisa (RN-08a) | `caffmob_draw/stick/apply.py:188-213,267-270; frame.py:146-155` |
| RN-STICK-10 | 🟢 Desgrudar devolve o pai anterior (se válido) e mantém a posição no mundo (RN-09, RF-16) | `caffmob_draw/stick/link.py:143-160` |
| RN-STICK-11 | 🟢 O assentar só roda quando nenhum modal de movimento está ativo (transform.*, movimentos do plugin, PlacementMixin), 0,2 s depois; após abrir/desfazer/refazer há 0,6 s em que movimentos não contam como gesto; voltar à pose anterior não é gesto novo | `caffmob_draw/stick/apply.py:22-23,265-306,309-314; settle.py:17-36,55-58` |
| RN-STICK-12 | 🟢 Ímã (RN-10a, RF-12): módulo ou geometria solto com o fundo a até a distância das preferências (padrão 50 mm) de uma face plana de frente (n·dir ≤ −0,7), que não seja piso nem teto, gruda ao assentar com um passo de desfazer próprio 'Grudar' | `caffmob_draw/stick/magnet.py:13-57,88-101; settle.py:82-92` |
| RN-STICK-13 | 🟢 Módulo raiz posto como filho de parede sem vínculo vira elemento filho dela ao abrir o arquivo e ao ser solto: NEG_Y (frente) se rotação Z ≈ 0 e Y local < espessura/2, senão POS_Y (trás); distance guarda o recuo atual; nada se move; idempotente (RN-10, RF-19, D-08) | `caffmob_draw/stick/migrate.py:15-51; settle.py:79-81` |
| RN-STICK-14 | 🟢 Interface sempre em texto: 'Elemento filho de: <hospedeiro> — frente/trás/plano/<face>', lista 'Elementos filhos' no hospedeiro; sem a palavra 'pai' (RF-17, D-11) | `caffmob_draw/stick/link.py:163-175; panels.py:27-54` |
| RN-STICK-15 | 🟢 Mover no plano com Ctrl troca de hospedeiro ao passar sobre a face de outro objeto (só com ímã ligado); Esc restaura pai, matrizes e os 13 campos | `caffmob_draw/stick/ops_stick.py:52-68,177-216` |
| RN-STICK-16 | 🟢 Prévia do ímã durante o arraste não altera o objeto; não aparece para item já grudado nem módulo filho de parede (005, D-15) | `caffmob_draw/stick/magnet_preview.py:55-73` |

#### customize

| ID | Regra | Evidência |
|---|---|---|
| RN-CUSTOMIZE-01 | 🟢 Um Spec descreve só o que o usuário mudou na instância; campo vazio = segue a biblioteca (RN-01) | `caffmob_draw/customize/spec.py:1-5; props.py:1-5` |
| RN-CUSTOMIZE-02 | 🟢 Estilos, materiais e puxadores são guardados por nome e resolvidos ao aplicar; ausente no arquivo → aviso, nunca índice gravado (RN-06) | `caffmob_draw/customize/spec.py:4; caffmob_draw/customize/adapters/common.py:19-26; caffmob_draw/customize/adapters/frameless.py:246-257` |
| RN-CUSTOMIZE-03 | 🟢 Vãos endereçados por caminho estável pela ordem dos filhos (X crescente, Z decrescente, nome), não pelo nome do objeto: bay<i>/opening<j>, opening<i>, module | `caffmob_draw/customize/adapters/common.py:13-16; caffmob_draw/customize/adapters/frameless.py:57-62` |
| RN-CUSTOMIZE-04 | 🟢 A personalização mora no vão (sobrevive à reconstrução das frentes), o material na peça e os grupos/puxador-geral na raiz; material da peça vence o do grupo (D-03, RF-05) | `caffmob_draw/customize/props.py:1-5; caffmob_draw/customize/adapters/common.py:86-93` |
| RN-CUSTOMIZE-05 | 🟢 Depois de cada reconstrução a biblioteca chama after_rebuild; módulo sem personalização sai sem custo; trava de reentrância por nome da raiz (D-04) | `caffmob_draw/customize/reapply.py:46-80` |
| RN-CUSTOMIZE-06 | 🟢 Frentes aceitas variam por biblioteca: frameless 7 tipos; face frame 7; closets sem basculante nem painel; btm sem gavetas e sem estilos (seção desabilitada com o motivo, RF-01) | `caffmob_draw/customize/adapters/frameless.py:39-40; caffmob_draw/customize/adapters/closets.py:32-33; caffmob_draw/customize/adapters/btm.py:23-28; caffmob_draw/customize/panels.py:12-22` |
| RN-CUSTOMIZE-07 | 🟢 Frameless: mais de uma gaveta só em vão que ocupa o compartimento inteiro; pilha máxima de 4 gavetas (aviso acima disso) | `caffmob_draw/customize/adapters/frameless.py:136-148` |
| RN-CUSTOMIZE-08 | 🟢 Interior: 0–20 prateleiras, 0–10 divisórias, 0–8 gavetas; alturas digitadas em quantidade igual às prateleiras, crescentes, dentro do vão; sem alturas, vãos livres iguais gap = (H − n·t)/(n+1) | `caffmob_draw/customize/spec.py:20-22,132-159` |
| RN-CUSTOMIZE-09 | 🟢 Face frame, closets e btm distribuem prateleiras por igual (alturas ignoradas com aviso); closets não tem divisória vertical nem gaveta interna; btm só prateleiras; face frame cria uma divisória por vez | `caffmob_draw/customize/adapters/face_frame.py:138-166; caffmob_draw/customize/adapters/closets.py:110-115; caffmob_draw/customize/adapters/btm.py:58-68` |
| RN-CUSTOMIZE-10 | 🟢 Grupos de material pela função da peça: POR → FRENTES; BACK/FUN_* → FUNDO; PRAT/DIV → INTERNO; resto CAIXA; veio preservado pela variante '<nome> ROTATED' no Rail Material (D-08) | `caffmob_draw/customize/spec.py:164-172; caffmob_draw/customize/adapters/common.py:29-33,66-69` |
| RN-CUSTOMIZE-11 | 🟢 Módulo salvo = .blend (RELATIVE_ALL, fake_user) + .json (manifesto) + .png 256 px, em extension_path_user/modules/<categoria>; nome de arquivo sanitizado, nome original no manifesto; gravação atômica e sem parciais em erro (D-10, RF-07) | `caffmob_draw/customize/library_io.py:22-37,140-168; caffmob_draw/customize/manifest.py:24-27` |
| RN-CUSTOMIZE-12 | 🟢 Nome repetido na mesma categoria exige marcar 'Substituir'; sem isso nada é escrito (RN-05, RF-08, D-11) | `caffmob_draw/customize/ops_library.py:54-67` |
| RN-CUSTOMIZE-13 | 🟢 Inserir: manifesto inválido ou major > 1 → aviso e nada inserido; estilos ausentes → geometria salva mantida e um aviso geral. 🔴 .blend sem .json: a intenção (003) é entrar como 'sem personalização' sem reaplicar spec, mas o código levanta `UnboundLocalError` (`missing` nunca atribuído) depois de ligar os objetos à cena (customize EC-01; herdado por `move_over/ops_substitute`) _(Revisão cruzada 2026-10-10: library_io.py:load reproduzido no Blender 5.2 pela revisão de customize)_ | `caffmob_draw/customize/manifest.py:115-133; caffmob_draw/customize/library_io.py:206-239; caffmob_draw/customize/panels.py:106` |
| RN-CUSTOMIZE-14 | 🟢 Módulo inserido continua paramétrico: a personalização é reaplicada pelo adaptador e as divisões ganham uids novos e são refluídas (RF-09) | `caffmob_draw/customize/library_io.py:131-137,229-232` |
| RN-CUSTOMIZE-15 | 🟢 Remoção de chapa (006) esconde por driver somado ao da biblioteca ((expr) or btm_rm); restaurar remove só o driver nosso; espessura sobrescrita no frameless tira o driver Material Thickness e voltar ao padrão o recria | `caffmob_draw/customize/adapters/common.py:243-269,281-292; caffmob_draw/customize/adapters/frameless.py:381-390` |
| RN-CUSTOMIZE-16 | 🟢 Fundo recuado (008) move a peça do fundo por delta_location (−Y da raiz), que drivers e recálculos não sobrescrevem; um fundo removido pelo projetista continua removido | `caffmob_draw/customize/adapters/common.py:362-374; caffmob_draw/customize/reapply.py:10-12` |
| RN-CUSTOMIZE-17 | 🟢 Limpar personalização do vão zera estilo, puxador, posição e material mas não reaplica: a interface pede trocar o estilo do projeto para refazer as frentes | `caffmob_draw/customize/ops_customize.py:235-248` |
| RN-CUSTOMIZE-18 | 🟢 Contrato prevê inserir .blend sem manifesto 'sem personalização' e sem reaplicar spec; o código atual falha nesse caminho (ver notas) | `caffmob_draw/customize/library_io.py:206-239` |

#### cabinet_editor

| ID | Regra | Evidência |
|---|---|---|
| RN-CABINET_EDITOR-01 | 🟢 Toda mudança do editor passa pela fila e é executada pelo modal com UNDO: um passo de desfazer só no OK (ou um por Aplicar); Cancelar reaplica o instantâneo inicial (D-21, D-22, D-04) | `caffmob_draw/cabinet_editor/ops_editor.py:1-20, 182-230; props.py:1-10` |
| RN-CABINET_EDITOR-02 | 🟢 Erro (severity ERROR) impede OK e Aplicar; aviso não (RN-03, D-24) | `caffmob_draw/cabinet_editor/validate.py:1-14; ops_editor.py:465-473; ops_actions.py:483-494` |
| RN-CABINET_EDITOR-03 | 🟢 Medidas limitadas à faixa geral estreitada pela faixa da biblioteca | `caffmob_draw/cabinet_editor/validate.py:23-45; bridge.py:71-80` |
| RN-CABINET_EDITOR-04 | 🟢 Peça fora da largura/altura do módulo com mais de 1 mm é GEO-001 (erro em prateleira/divisória); a profundidade é livre por causa do puxador | `caffmob_draw/cabinet_editor/validate.py:69-81` |
| RN-CABINET_EDITOR-05 | 🟢 Ajustes automáticos = o que o recálculo mudou sozinho, sem as peças que o usuário editou (RF-07, RN-02) | `caffmob_draw/cabinet_editor/elevation.py:80-100; ops_editor.py:165` |
| RN-CABINET_EDITOR-06 | 🟢 Remover componente externo: KEEP só tira a chapa; EXTEND estende as vizinhas e o vão cresce; SHRINK reduz a medida externa e o vão fica igual; modo que a biblioteca não faz cai em KEEP com aviso STR-001 (RN-06) | `caffmob_draw/cabinet_editor/structure.py:1-60; bridge.py:369-383` |
| RN-CABINET_EDITOR-07 | 🟢 Espessura de componente externo entre 3 e 60 mm; 0 = segue o Configurador (STR-002) | `caffmob_draw/cabinet_editor/structure.py:28, 69-75` |
| RN-CABINET_EDITOR-08 | 🟢 Divisão sempre corta um subvão-folha inteiro; offset medido da face esquerda/de baixo e mantido quando o vão-raiz muda (RN-09, RN-11, RN-16) | `caffmob_draw/cabinet_editor/divisions.py:1-25, 94-118` |
| RN-CABINET_EDITOR-09 | 🟢 Subvão mínimo 50 mm de cada lado da chapa e profundidade mínima 50 mm depois dos recuos (RN-14; DIV-001, DIV-002) | `caffmob_draw/cabinet_editor/divisions.py:38-40, 204-229` |
| RN-CABINET_EDITOR-10 | 🟢 Divisão herda material e espessura do componente Divisória do Configurador na linha do módulo, salvo sobrescrita (RN-10, RN-12) | `caffmob_draw/cabinet_editor/scene_divisions.py:7-8, 35-46` |
| RN-CABINET_EDITOR-11 | 🟢 Divisões, extras, internos e deslizantes são filhos diretos da raiz, fora do que as bibliotecas reconstroem (D-03, D-12) | `caffmob_draw/cabinet_editor/scene_divisions.py:1-5; scene_parts.py:1-8` |
| RN-CABINET_EDITOR-12 | 🟢 N vãos = N-1 divisórias verticais bay em cadeia s0, s0.b…, largura igual; mudar N mantém as existentes e acrescenta/tira só as do fim (RN-07b, D-15) | `caffmob_draw/cabinet_editor/bays.py:1-54` |
| RN-CABINET_EDITOR-13 | 🟢 Distanciador ocupa a faixa sem dividir o vão; 'p/ Divisão' exige o vão logo à direita/acima de uma divisória e a segue | `caffmob_draw/cabinet_editor/divisions.py:15-20; bridge.py:457-462` |
| RN-CABINET_EDITOR-14 | 🟢 Base Superior Recuada remove o tampo (KEEP) e o restaura ao desligar | `caffmob_draw/cabinet_editor/bridge.py:488-501` |
| RN-CABINET_EDITOR-15 | 🟢 Pés e rodapés ficam abaixo da caixa: o módulo não é levantado; valores padrão das capturas do Promob (pés 150, fechamento 50, vistas 150 mm) | `caffmob_draw/cabinet_editor/extras.py:1-30` |
| RN-CABINET_EDITOR-16 | 🟢 Gavetas e Portas inserem no vão da biblioteca que contém o centro do subvão alvo (D-05, D-23); gaveta interna só no frameless; gavetão 2 a 4 | `caffmob_draw/cabinet_editor/bridge.py:562-624` |
| RN-CABINET_EDITOR-17 | 🟢 Painel p/ eletro: externo para fora do plano da frente, embutido recuado uma espessura; recorte centrado com a medida dos eletros empilhados; item que não cabe (medida + 10 mm de folga por lado) fica apagado e é recusado (RN-13a) | `caffmob_draw/cabinet_editor/appliances.py:1-60; catalog.py:34-43; bridge.py:627-640` |
| RN-CABINET_EDITOR-18 | 🟢 Deslizantes: folhas dentro do vão, uma por trilho (20 mm), sobreposição 30 mm, abrem para o centro; profundidade mínima N·20 + 50 mm; folha que não corre gera aviso (RN-13b) | `caffmob_draw/cabinet_editor/slides.py; scene_slides.py:198-240` |
| RN-CABINET_EDITOR-19 | 🟢 Fundo Inteiro Recuado anda o fundo para dentro e o vão termina nele; 'Inserir automaticamente' reaplica depois de cada reconstrução (D-11, RN-14, RN-15) | `caffmob_draw/cabinet_editor/structure.py:84-111; bridge.py:520-535` |
| RN-CABINET_EDITOR-20 | 🟢 Montagem LATERAL (laterais do piso ao topo) ou BASE (base na largura toda, laterais em cima) muda chapas, vão e comprimentos de corte do módulo CAFFMob (012, D-09) | `caffmob_draw/cabinet_editor/structure.py:84-128` |
| RN-CABINET_EDITOR-21 | 🟢 Clique escolhe a chapa sob o cursor, menos frentes, vãos e chapas que cobrem o subvão inteiro; sem chapa, escolhe o subvão (D-06) | `caffmob_draw/cabinet_editor/ops_editor.py:263-272, 439-450` |

#### standards

| ID | Regra | Evidência |
|---|---|---|
| RN-STANDARDS-01 | 🟢 Valores de comprimentos nas definições em mm; escrita de geometria em m com divisão por 1000. | `caffmob_draw/standards/api.py:171-181` |
| RN-STANDARDS-02 | 🟢 Embutidas BR/US são somente leitura na API de valores e não podem ser excluídas. | `caffmob_draw/standards/api.py:132-141,203-206` |
| RN-STANDARDS-03 | 🟢 Duplicação cria UUID, nome único, USER e ativa a cópia; preserva montagem e raw. | `caffmob_draw/standards/api.py:109-129` |
| RN-STANDARDS-04 | 🟢 set_values valida todos pares antes de qualquer gravação. | `caffmob_draw/standards/api.py:209-223` |
| RN-STANDARDS-05 | 🟢 Rascunho compara números com tolerância 1e-6 mm; montagem é uma alteração; nome sozinho não muda versão. | `caffmob_draw/standards/api.py:264-319` |
| RN-STANDARDS-06 | 🟢 Own se overrides, montagem diferente da origem ou espessura explícita de componente maior que zero. | `caffmob_draw/standards/apply_core.py:19-21` |
| RN-STANDARDS-07 | 🟢 Plano: CAFFMob de origem anterior ou sem UID e sem own segue; outros CAFFMob diferem; legado/outros não aplicáveis. | `caffmob_draw/standards/apply_core.py:24-35` |
| RN-STANDARDS-08 | 🟢 Cancelar primeira pergunta preserva módulos CAFFMob; segunda só decide differ após follow aplicado. | `caffmob_draw/standards/../operators/ops_standards.py:531-590` |
| RN-STANDARDS-09 | 🟢 modules=None seleciona CAFFMob sem own, independente de UID anterior; include_manual inclui todos. | `caffmob_draw/standards/sync.py:266-268` |
| RN-STANDARDS-10 | 🟢 modules=[] ainda grava destinos de cena e pode propagar legado no modo suporte. | `caffmob_draw/standards/sync.py:253-281` |
| RN-STANDARDS-11 | 🟢 Aplicar CAFFMob mantém largura e posição Z; reseta espessuras próprias e todos overrides; escreve UID. | `caffmob_draw/standards/sync.py:231-250` |
| RN-STANDARDS-12 | 🟢 Defaults usam papel BACK -> FUN_INF inclusive em WALL/TALL; caixa usa espessura LEFT. | `caffmob_draw/standards/cabinet_defaults.py:57-64; ../cabinet_editor/structure.py:34` |
| RN-STANDARDS-13 | 🟢 Sem padrão ou linha disponível, medidas fallback retornam aviso; tipo inválido vira BASE. | `caffmob_draw/standards/cabinet_defaults.py:42-64` |
| RN-STANDARDS-14 | 🟢 Skip por campo manual atua na propagação de suporte legado; lista explícita CAFFMob prevalece. | `caffmob_draw/standards/sync.py:72-82,269-275` |
| RN-STANDARDS-15 | 🟢 Profundidade de sincronização restaura em finally; não há rollback de dados em falha. | `caffmob_draw/standards/sync.py:169-176` |
| RN-STANDARDS-16 | 🟢 JSON aceita identidade atual e anterior; unidade mm e versões futuras recusadas; montagem não serializada. | `caffmob_draw/standards/io_json.py:16-17,35-115` |
| RN-STANDARDS-17 | 🟢 Importação JSON cria UID novo, USER, não ativa e renomeia conflito ou substitui somente usuário. | `caffmob_draw/standards/io_json.py:161-186` |
| RN-STANDARDS-18 | 🟢 XML preserva atributos na ordem; duplicados usam último valor para mapear cada ocorrência. | `caffmob_draw/standards/io_promob.py:69-121` |
| RN-STANDARDS-19 | 🟢 CAFF_MONTAGEM fora dos raw; ausente/ inválido -> LATERAL, inválido com aviso. | `caffmob_draw/standards/io_promob.py:61-94` |
| RN-STANDARDS-20 | 🟢 XML reexporta raw existente; sintetiza todos códigos só se raw vazio; metadados da raiz são regenerados. | `caffmob_draw/standards/io_promob.py:129-190; ../operators/ops_standards.py:433-458` |
| RN-STANDARDS-21 | 🟢 Escrita JSON/XML atômica por temporário no diretório de destino e os.replace. | `caffmob_draw/standards/io_json.py:122-134; io_promob.py:152-179` |
| RN-STANDARDS-22 | 🟢 M-02 escolhe US se cages frameless/closet; M-01 sobrepõe com Migrada se valores explícitos válidos. | `caffmob_draw/standards/migration.py:54-108` |
| RN-STANDARDS-23 | 🟢 M-03 carimba raízes sem UID a cada run, sem reconstruir. | `caffmob_draw/standards/migration.py:111-137` |
| RN-STANDARDS-24 | 🟢 Finitude numérica e forma profunda do JSON não são integralmente validadas. | `caffmob_draw/standards/../data/dimension_schema.py:validate; io_json.py:73-115` |

#### legacy

| ID | Regra | Evidência |
|---|---|---|
| RN-LEGACY-01 | 🟢 UI herdada exige show_legacy_libraries; dados permanecem registrados. | `caffmob_draw/legacy/gate.py:22–25` |
| RN-LEGACY-02 | 🟢 Conversão conserva dimensões/matriz/pai, usa chapas e montagem do padrão ativo e exclui agregados próprios. | `caffmob_draw/legacy/convert.py:108–145` |
| RN-LEGACY-03 | 🟢 Oferta de grupos é marcada antes da confirmação; grupo sem error é concluído mesmo com erros individuais de save. | `caffmob_draw/legacy/groups.py:133–154; ops.py:85–95` |

#### library_panel

| ID | Regra | Evidência |
|---|---|---|
| RN-LIBRARY_PANEL-01 | 🟢 Fixas primeiro; categorias de usuário depois; pastas soltas viram COZ. | `caffmob_draw/library_panel/categories_core.py:35–100` |
| RN-LIBRARY_PANEL-02 | 🟢 Painel sempre desenhado sem modal permanente; clique fora fecha e passa para seleção. | `caffmob_draw/library_panel/draw.py:85–119; ops_click.py:65–77` |
| RN-LIBRARY_PANEL-03 | 🟢 Modelos usam medidas do padrão, largura explícita mm quando não zero; popover usa botões sem miniaturas. | `caffmob_draw/library_panel/popover.py:20–80` |

#### object_library

| ID | Regra | Evidência |
|---|---|---|
| RN-OBJECT_LIBRARY-01 | 🟢 Biblioteca tem raiz embutida só leitura e raiz do usuário; ID diferencia de nome. | `caffmob_draw/object_library/store.py:30–85` |
| RN-OBJECT_LIBRARY-02 | 🟢 Posicionamento interativo usa plano horizontal do cursor; Esc/direito remove objetos, cancel externo só header. | `caffmob_draw/object_library/ops.py:90–131` |
| RN-OBJECT_LIBRARY-03 | 🟢 Save faz replace sequencial, sem transação entre arquivos; retextura afeta cena, não biblioteca. | `caffmob_draw/object_library/item_io.py:102–121; retexture.py:70–99` |

#### inspection

| ID | Regra | Evidência |
|---|---|---|
| RN-INSPECTION-01 | 🟢 Valores comuns articulados em graus até 90, gavetas em fração; folhas convertidas admitem máximo próprio. | `caffmob_draw/inspection/fronts.py:39–60; adapters/aggregate_leaf.py:36–50` |
| RN-INSPECTION-02 | 🟢 Salvar fecha frentes salvo opt-out e restaura por cena/key em save_post ou save_post_fail. | `caffmob_draw/inspection/save_guard.py:21–78` |
| RN-INSPECTION-03 | 🟢 Interferência exclui próprio módulo, amostra poses, encolhe pontos radialmente e usa AABB/BVH/contenção. | `caffmob_draw/inspection/interference.py:37–204` |

#### molding

| ID | Regra | Evidência |
|---|---|---|
| RN-MOLDING-01 | 🟢 Somente face frame e frameless recebem molduras automáticas. | `caffmob_draw/molding/adapters.py:collect_targets` |
| RN-MOLDING-02 | 🟢 Rodapés podem omitir recessos e atravessam eletrodomésticos como vãos SKIP. | `caffmob_draw/molding/engine.py:kick_sweep_segments` |
| RN-MOLDING-03 | 🟢 Toda aplicação apaga sweeps anteriores antes de gerar os novos. | `caffmob_draw/molding/ops.py:apply_scene_packages` |
| RN-MOLDING-04 | 🟢 Capa nunca monta abaixo do topo do armário antes do offset configurado. | `caffmob_draw/molding/ops.py:_sweep_z` |

#### geometry_free

| ID | Regra | Evidência |
|---|---|---|
| RN-GEOMETRY_FREE-01 | 🟢 Fabricação de geometria livre é optativa e exige visibilidade. | `caffmob_draw/cutting/part_sources.py:geometry_records` |
| RN-GEOMETRY_FREE-02 | 🟢 Placa é uma chapa; caixa decompõe-se em seis chapas na produção. | `caffmob_draw/geometry_free/mesh.py:sheets` |
| RN-GEOMETRY_FREE-03 | 🟢 Espessura produtiva da placa é a menor dimensão ordenada. | `caffmob_draw/geometry_free/mesh.py:sheets` |
| RN-GEOMETRY_FREE-04 | 🟢 Espelhar alterna flag e desloca, sem transformar os vértices. | `caffmob_draw/geometry_free/ops_edit.py` |

### Conflitos entre intenção e implementação

- 🔴 Biblioteca de módulos: a regra declarada de aceitar `.blend` sem manifesto encontra um caminho de falha descrito em `code-analysis.md`, módulo customize. Não promover intenção a comportamento executado.
- 🟢 Escrita atômica de um arquivo JSON/XML usa temporário e replace; isso não equivale a transação do conjunto `.blend`/JSON/thumbnail. Biblioteca de objetos e reconstruções de cena podem deixar resultados parciais.
- 🟢 Paredes do editor 2D são rascunho até OK; o armário é atualizado ao vivo e Cancelar reaplica o snapshot vigente. Após Aplicar, snapshot vigente deixa de ser o inicial da sessão.
- 🟢 `molding` atende somente face frame/frameless, embora o painel moderno ofereça outros módulos. Não generalizar suporte por semelhança de UI.
- 🔴 Fabricação e malha de geometria livre divergem se espessura exceder medida do plano ou se houver escala no objeto; exportação deriva das propriedades.
- 🔴 Interferência é aproximada; ausência de conflito não constitui certificação física de folga ou fabricação.

### Lacunas que exigem decisão ou verificação humana

Contratos atuais foram documentados sem correção de código. Permanecem: recuperação após gravação/reconstrução parcial; cancelamento externo e desregistro de modais; referências RNA removidas durante interação; famílias sem capacidades equivalentes; validação profunda de manifestos e finitude numérica; transformações parentadas; gatilho de rechecagem da interferência; equivalência produtiva dos itens convertidos do legado. Essas lacunas são candidatas a testes/decisões, não funcionalidades implicitamente autorizadas.
