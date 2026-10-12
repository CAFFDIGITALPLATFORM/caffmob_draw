# Lacunas Remanescentes — BlenderToMob (re-extração 2026-10)

> Gerado pelo Reviewer em 2026-10-10.
> Parte A: decisões do titular (todas respondidas em 2026-10-10 com "aceito"; as que exigem mudança de código viraram tarefas `DT-xx` nos `tasks.md` das units). Parte B: lacunas de código/teste que **não** dependem do titular (bugs, falta de teste, i18n). Parte C: código sem unit de spec.

## Parte A — Crítico

- **[walls2d]** Remover Vértice deve registrar o source do trecho eliminado em removed_sources (como o Delete faz)? → `questions.md#pergunta-1` ✅ decidido (aceito em 2026-10-10)
- **[selection]** Ao apagar uma parede, os agregados dos módulos filhos dela devem entrar na pergunta 'O objeto tem agregados'? → `questions.md#pergunta-2` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** O terceiro teste de can_convert deve recusar 'pai descendente do objeto' (como diz a mensagem) em vez de 'objeto descendente do pai' (como o código faz)? → `questions.md#pergunta-3` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Apagar uma parede (ou piso/teto) deve perguntar pelos agregados dos módulos filhos dela? → `questions.md#pergunta-4` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** Ao apagar uma parede, portas/janelas, geometrias e cotas filhas devem ir junto, ficar no lugar (como em wall_remove) ou o X/Delete deve delegar para caffmob.wall_remove? → `questions.md#pergunta-5` ✅ decidido (aceito em 2026-10-10)

## Parte A — Moderado

- **[canvas2d]** Quando o editor foi aberto numa janela duplicada e, no fechamento, só resta uma janela (ou window_ptr não bate), _close não faz nada e a área fica como Image Editor sem cabeçalho nem menus. Isso é intencional ou a área deveria voltar a VIEW_3D com menus/cabeçalho? → `questions.md#pergunta-6` ✅ decidido (aceito em 2026-10-10)
- **[canvas2d]** O sinal de pinch_delta (-(dx+dy)) e a sensibilidade 1/150 foram validados em quais plataformas (macOS, Wayland, Windows)? → `questions.md#pergunta-7` ✅ decidido (aceito em 2026-10-10)
- **[walls2d]** O "Não" da pergunta de fechamento por arraste (close_existing) deve sobreviver ao OK? → `questions.md#pergunta-8` ✅ decidido (aceito em 2026-10-10)
- **[walls2d]** Soltar o botão sobre a barra superior deve concluir o arraste de vértice e o retângulo da lupa? → `questions.md#pergunta-9` ✅ decidido (aceito em 2026-10-10)
- **[walls2d]** confirm_pending deve ser zerado quando o rascunho muda depois do 1º aviso? → `questions.md#pergunta-10` ✅ decidido (aceito em 2026-10-10)
- **[walls2d]** Com Bloquear Ângulo ligado, os campos de ângulo devem ficar desabilitados (ou ignorar a trava)? → `questions.md#pergunta-11` ✅ decidido (aceito em 2026-10-10)
- **[measure]** Aplicar a cota anterior/posterior pode sobrepor o vizinho do lado oposto, e a inferior pode passar do teto (cota superior negativa). Isso deve ser rejeitado com 'Valor Inválido'? → `questions.md#pergunta-12` ✅ decidido (aceito em 2026-10-10)
- **[measure]** Vizinhos sem Geometry Nodes (módulo rápido btm_cabinet, objeto importado) viram obstáculo de largura e altura zero. As cotas devem medir até a lateral real desses vizinhos? → `questions.md#pergunta-13` ✅ decidido (aceito em 2026-10-10)
- **[measure]** Módulos filhos de paredes da camada nova (BTM, sem IS_WALL_BP) são tratados como livres (só cotas verticais). É intencional? → `questions.md#pergunta-14` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** Com um campo em edição e um valor válido, Tab grava e volta ao campo X (índice 0) em vez de ir ao próximo campo; com um valor inválido, vai ao próximo campo levando o texto inválido. Qual é o comportamento esperado? → `questions.md#pergunta-15` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** As caixas de A e B usadas no alinhamento e na verificação de sobreposição devem incluir a árvore de malhas visíveis (frentes, puxadores), como o Substituir já faz, ou só a geometria da raiz? → `questions.md#pergunta-16` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** Se o Blender interromper Mover na Parede ou Plano de inserção (abrir arquivo, fechar janela), a posição original e o cabeçalho/cursor devem ser restaurados? → `questions.md#pergunta-17` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** Depois do aviso de sobreposição, mover A com setas ou Page Up/Down deve zerar o aviso (para o próximo Confirmar verificar de novo)? → `questions.md#pergunta-18` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** No Substituir, o novo módulo deve herdar a escala de A (hoje recebe a.matrix_world inteira)? → `questions.md#pergunta-19` ✅ decidido (aceito em 2026-10-10)
- **[selection]** Editar a largura ou a altura de uma porta/janela HB pelo painel deve refazer a porta real (_sync_opening) e mostrar a medida da folha, como o Redimensionar já faz? → `questions.md#pergunta-20` ✅ decidido (aceito em 2026-10-10)
- **[selection]** Janelas BTM (btm_plane OPENING) devem ser redimensionáveis? Se sim, por qual caminho (btm_opening.width e a malha de corte)? → `questions.md#pergunta-21` ✅ decidido (aceito em 2026-10-10)
- **[openings]** A porta ou janela inserida numa região marcada na face de fundo deve abrir para o lado dessa face, como pede 011 RN-11? → `questions.md#pergunta-22` ✅ decidido (aceito em 2026-10-10)
- **[openings]** Cotas e textos 2D podem ficar como filhos da caixa da porta na prática? Se sim, _swing deve exigir o input 'Swing Inside', como room_door_leaf.swing_of? → `questions.md#pergunta-23` ✅ decidido (aceito em 2026-10-10)
- **[openings]** Trocar porta simples ↔ dupla pelo 'Toggle Double Door' deve refazer a porta real? → `questions.md#pergunta-24` ✅ decidido (aceito em 2026-10-10)
- **[openings]** Aceita mover a invalidação da região (active = False) para fora do callback de desenho? → `questions.md#pergunta-25` ✅ decidido (aceito em 2026-10-10)
- **[openings]** Objetos do usuário postos como filhos do marco ou da folha devem sobreviver quando a porta real é refeita? → `questions.md#pergunta-26` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Desconverter (e o Delete com 'Apagar também os agregados' desligado) deve deixar o objeto onde está agora, em vez de voltar à matriz da época da conversão? → `questions.md#pergunta-27` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Agregado com pai Empty (grupo, esquadria, raiz de FBX) deve usar a caixa da união das peças (group.object_corners)? → `questions.md#pergunta-28` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Folha cujo pai não pertence a módulo (ex.: parede) deve excluir do contato só o pai, e não toda a subárvore dele? → `questions.md#pergunta-29` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Mudar sentido/ângulo/curso com a folha aberta deve passar pela varredura, e a varredura deve refinar obstáculos finos (passo menor ou teste de volume varrido)? → `questions.md#pergunta-30` ✅ decidido (aceito em 2026-10-10)
- **[collision]** Encostar com sobreposição de exatamente 1 mm deve contar como colisão? Se não, a comparação deve ter folga numérica (depth <= TOLERANCE + 1e-9)? → `questions.md#pergunta-31` ✅ decidido (aceito em 2026-10-10)
- **[collision]** 'Afastar até encostar' deve ter prévia e mover o item selecionado (004 RF-26), ou manter o movimento direto de name_a? → `questions.md#pergunta-32` ✅ decidido (aceito em 2026-10-10)
- **[collision]** A confirmação pela malha deve tratar item totalmente contido num objeto fino (teste de ponto dentro da malha)? → `questions.md#pergunta-33` ✅ decidido (aceito em 2026-10-10)
- **[collision]** Objetos novos, apagados ou renomeados após a verificação devem deixar o resultado desatualizado, e check_moved sem verificação prévia deve marcar checked? → `questions.md#pergunta-34` ✅ decidido (aceito em 2026-10-10)
- **[collision]** Grupos soltos (SketchUp, biblioteca de objetos) devem entrar na colisão, e o painel do item deve editar o override do agregado em vez do da raiz do módulo? → `questions.md#pergunta-35` ✅ decidido (aceito em 2026-10-10)
- **[stick]** Trocar o pai de um item grudado fora do plugin (Ctrl+P/Alt+P) deve desfazer o vínculo com aviso "Vínculo perdido", como promete a docstring de apply.py? Hoje o vínculo fica órfão: o painel continua dizendo "Elemento filho de", os campos não movem nada e o hospedeiro antigo ainda lista o item. → `questions.md#pergunta-36` ✅ decidido (aceito em 2026-10-10)
- **[stick]** Quando o hospedeiro é apagado pelo Outliner ou renomeado, o vínculo deve ser atualizado na hora? Hoje o índice por nome só é refeito depois de grudar, desgrudar, abrir ou desfazer, então o item fica com is_stuck sem hospedeiro, ou deixa de acompanhar a medida do hospedeiro renomeado. → `questions.md#pergunta-37` ✅ decidido (aceito em 2026-10-10)
- **[stick]** "Desgrudar" um módulo que está na parede deve ser durável? Hoje ele volta a ser vinculado no próximo assentar com pose nova ou na próxima abertura do arquivo (stick_migrated é gravado e nunca lido). → `questions.md#pergunta-38` ✅ decidido (aceito em 2026-10-10)
- **[stick]** O comando Grudar deve aceitar parede, piso, teto, cota e objetos não-item como item? O poll e o painel aceitam qualquer objeto ativo (uma parede pode virar filha de outro objeto); só o menu de contexto restringe aos tipos de item. → `questions.md#pergunta-39` ✅ decidido (aceito em 2026-10-10)
- **[customize]** O que a posição de puxador "Lateral" (SIDE) deve fazer? Nenhum adaptador a trata (no btm cai no meio da altura), mas ela aparece no menu. → `questions.md#pergunta-40` ✅ decidido (aceito em 2026-10-10)
- **[customize]** Ao trocar um vão para 2 a 4 gavetas no frameless, a personalização do vão antigo (material das frentes, estilo, puxador, interior) deve passar para os vãos novos? Hoje ela se perde (confirmado no Blender 5.2). → `questions.md#pergunta-41` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** A Montagem (LATERAL/BASE) mudada no painel do editor deve entrar no rascunho (Ctrl+Z, Cancelar e Aplicar) como as outras edições? Hoje ela é gravada direto em btm_cabinet.assembly, fora da fila, não faz parte do EditorState e Cancelar não a desfaz; SET_ASSEMBLY existe na ponte mas ninguém o enfileira. → `questions.md#pergunta-42` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** Com pedidos na fila, OK e Cancelar devem executar a fila antes de encerrar? Hoje `request` é testado antes de `process` e os pedidos pendentes são descartados (EC-02). → `questions.md#pergunta-43` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** Mudar o Número de vãos quando já existe uma divisória comum em s0 deve ser recusado com aviso, reorganizar as divisões ou continuar gerando DIV-003 (EC-07)? → `questions.md#pergunta-44` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** Os deslizantes devem ocupar sempre o primeiro vão-raiz inteiro (hoje) ou o subvão escolhido / todos os vãos (EC-08)? → `questions.md#pergunta-45` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** Os itens 'Interna s/ Recuo — Tras 15mm' e 'c/ Recuo — Tras 15mm' devem aplicar o recuo de trás de 15 mm do catálogo? Hoje só o recuo da frente vem do item; o de trás vem do campo 'Recuo atrás' (desligado por padrão). → `questions.md#pergunta-46` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** No painel Forno/Micro o forno deve ficar embaixo (comentário do código) ou o micro embaixo (o que o código faz hoje)? → `questions.md#pergunta-47` ✅ decidido (aceito em 2026-10-10)
- **[standards]** A Montagem (LATERAL/BASE) deve ser gravada e lida no .btmdim.json? Hoje não é: uma definição 'Base passante' exportada volta como LATERAL, enquanto o XML do Promob a preserva em CAFF_MONTAGEM. → `questions.md#pergunta-48` ✅ decidido (aceito em 2026-10-10)
- **[standards]** Valores não finitos (NaN, inf) devem ser recusados como 'Valor Inválido'? Hoje NaN passa e inf só falha pela faixa. → `questions.md#pergunta-49` ✅ decidido (aceito em 2026-10-10)
- **[standards]** Depois de 'Definir ativa' com Sim na 1ª pergunta, os módulos que acabaram de ser atualizados podem reaparecer na lista 'difere' da 2ª pergunta (EC-01)? Isso é aceito ou a 2ª pergunta deve excluí-los? → `questions.md#pergunta-50` ✅ decidido (aceito em 2026-10-10)
- **[standards]** No Configurador aberto numa embutida, depois de 'Duplicar para editar', o botão rotulado 'Fechar' deve aplicar as edições na cópia (hoje aplica) ou só fechar (EC-07)? → `questions.md#pergunta-51` ✅ decidido (aceito em 2026-10-10)
- **[standards]** M-02 deve ativar 'Padrão EUA (HB5)' também em projetos herdados só com gabinetes face frame? Hoje só frameless/closets contam (EC-13). → `questions.md#pergunta-52` ✅ decidido (aceito em 2026-10-10)
- **[standards]** O XML exportado com o atributo extra CAFF_MONTAGEM abre sem erro no Promob? A docstring afirma que o Promob ignora IDs desconhecidos, mas não houve teste. → `questions.md#pergunta-53` ✅ decidido (aceito em 2026-10-10)
- **[legacy]** Quando a construção de um armário falha no meio do lote, o lote deve ter rollback (apagar os módulos já criados e avisar), ou basta o comportamento atual (traceback, módulo parcial 'BTM_Cabinet' ao lado dos originais, que o Ctrl+Z remove)? → `questions.md#pergunta-54` ✅ decidido (aceito em 2026-10-10)
- **[legacy]** Duas regras de contagem divergem do plano da 012: (a) portas somam entre aberturas (2 portas em vãos diferentes = DOUBLE sem perda), quando o D-24 dizia 'a maior abertura manda, as outras são perda'; (b) no face frame, PULLOUT/TILT_OUT/INSET_PANEL em gaiola folha são contados duas vezes (Gavetas/Painéis + Frentes especiais). Qual é a regra pretendida? → `questions.md#pergunta-55` ✅ decidido (aceito em 2026-10-10)
- **[legacy]** O relatório deve declarar como perda a troca de chapas, espessuras e montagem pelas do padrão ativo, a redistribuição das prateleiras e as frentes não lidas quando o adaptador falha (hoje sai 'sem perdas')? → `questions.md#pergunta-56` ✅ decidido (aceito em 2026-10-10)
- **[library_panel]** Uma categoria com caractere que o nome de arquivo troca (ex. 'Pia: Lavabo') grava os módulos em 'Pia_ Lavabo/', eles não aparecem na categoria e surge uma categoria nova 'Pia_ Lavabo' (COZ). A validação do nome deve recusar esses caracteres, ou a pasta da categoria deve usar o mesmo nome saneado? → `questions.md#pergunta-57` ✅ decidido (aceito em 2026-10-10)
- **[library_panel]** Com categories.json corrompido, criar categoria ou trocar linha sobrescreve o arquivo e as categorias do usuário perdem a linha (as sem pasta somem). Os avisos de leitura também não aparecem em lugar nenhum. Devemos guardar uma cópia do arquivo corrompido antes de regravar e mostrar o aviso no painel? → `questions.md#pergunta-58` ✅ decidido (aceito em 2026-10-10)
- **[object_library]** Inserir pelo botão da barra lateral (o caminho normal da UI) não faz o objeto acompanhar o mouse: o modal recebe a região UI sem RegionView3D. Corrigimos fazendo _follow usar a região WINDOW da área sob o mouse? → `questions.md#pergunta-59` ✅ decidido (aceito em 2026-10-10)
- **[object_library]** A textura de imagem própria usa coordenadas de objeto (a escala do objeto muda o tamanho aparente) e a imagem não é empacotada no .blend do item (caminho relativo). Deve-se empacotar a imagem ao salvar o item e compensar a escala? → `questions.md#pergunta-60` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** Folha convertida de correr (SLIDE) ativa: o gizmo chama front.travel(), que não existe em AggregateLeafFront (AttributeError a cada redesenho). A seta deve aparecer com o curso real da folha ou ficar escondida para folhas de correr? → `questions.md#pergunta-61` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** Folhas convertidas com max_angle > 90° (ex. 110°): clique, 'Abrir 90°' e o dial param em 90°; só a varredura de interferência vai até 110°. O dial (e o clique) devem chegar ao max_angle da folha? → `questions.md#pergunta-62` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** Salvar (Ctrl+S) no meio de uma animação ou com pending do gizmo grava a pose intermediária (delta_*) porque get() ainda lê btm_open antigo; e um objeto compartilhado entre cenas com save_fronts_open diferente é salvo fechado. O salvar fechado deve concluir/zerar animações pendentes antes de fechar e respeitar a opção por objeto? → `questions.md#pergunta-63` ✅ decidido (aceito em 2026-10-10)
- **[molding]** Validação visual no Blender 5.2: o perfil embutido (X negativo = para dentro) aparece do lado certo do bevel, os retornos nas pontas acabadas e as meias-esquadrias saem corretos? Inclui corridas só de cantos (EC-07, sentido não normalizado) e pai com escala/inclinação (EC-08). → `questions.md#pergunta-64` ✅ decidido (aceito em 2026-10-10)
- **[geometry_free]** Com parent, duplicar e espelhar mandam a peça para outro lugar (EC-09) e excluir faz os filhos (agregados, cotas) saltarem para a origem do mundo (EC-14). Qual o comportamento desejado: duplicar/espelhar no X local relativo ao pai e, ao excluir, apagar os filhos ou mantê-los na posição mundial? → `questions.md#pergunta-65` ✅ decidido (aceito em 2026-10-10)
- **[geometry_free]** Placa com uma medida do plano menor que a espessura (ex. 600 × 10 mm com espessura 18 mm) é exportada com 10 mm de espessura e 18 mm de largura, sem aviso (EC-02); caixa com espessura ≥ metade gera chapas de 1 mm (EC-03). Deve haver aviso ou recusa na produção? → `questions.md#pergunta-66` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** Geometria livre convertida em agregado deve sair na produção como geometria (chapas) ou como agregado (uma placa)? → `questions.md#pergunta-67` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** Folhas devem ser ligadas à caixa (IS_WINDOW_BP/IS_ENTRY_DOOR_BP) e à parede hospedeira em _links? → `questions.md#pergunta-68` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** set_dimension de porta/janela deve chamar _sync_opening como o Redimensionar? → `questions.md#pergunta-69` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** A 013 será commitada ou descartada? → `questions.md#pergunta-70` ✅ decidido (aceito em 2026-10-10)

## Parte A — Cosmético

- **[canvas2d]** No fallback (editor ocupando a área atual), a área deve voltar exatamente ao estado anterior (menus, cabeçalho, região N, barras, imagem) ou basta restaurar o tipo e ligar menus/cabeçalho como hoje? → `questions.md#pergunta-71` ✅ decidido (aceito em 2026-10-10)
- **[walls2d]** O sinal da pinça foi validado em todas as plataformas-alvo (macOS, Wayland, X11/Windows)? → `questions.md#pergunta-72` ✅ decidido (aceito em 2026-10-10)
- **[measure]** A feature 002 RF-18 pede cotas para 'módulos e geometrias'; for_object só aceita MODULE/PART/FRONT. Geometrias devem ter cotas? → `questions.md#pergunta-73` ✅ decidido (aceito em 2026-10-10)
- **[measure]** Há meta de desempenho para o recálculo das cotas (ModuleCotas recriado e filhos da parede relistados a cada redesenho e por campo do painel)? → `questions.md#pergunta-74` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** Esc deve desligar o modo Mover Sobre, e o objeto sob o cursor deve ser realçado no 3D durante o arraste, como a feature 002 pedia? → `questions.md#pergunta-75` ✅ decidido (aceito em 2026-10-10)
- **[move_over]** Vale manter a meta da feature 002 (prévia em até 200 ms e redesenho em até 100 ms) e medi-la? → `questions.md#pergunta-76` ✅ decidido (aceito em 2026-10-10)
- **[selection]** Há meta de desempenho para o normalizador com seleções grandes (centenas de peças)? → `questions.md#pergunta-77` ✅ decidido (aceito em 2026-10-10)
- **[openings]** Há meta de tempo para sync (bmesh + várias view_layer.update) em projetos com muitas portas? → `questions.md#pergunta-78` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Desinstalar deve usar frame_matrix e o pai anterior para devolver a esquadria ao lugar de antes, como diz a docstring de window_props? → `questions.md#pergunta-79` ✅ decidido (aceito em 2026-10-10)
- **[aggregates]** Há meta de desempenho para varredura, measure_free_travel e recorte durante o arraste (a 003 pedia recorte só ao soltar)? → `questions.md#pergunta-80` ✅ decidido (aceito em 2026-10-10)
- **[collision]** check_moved deve reordenar a lista inteira pela ordem RN-06 e limpar error após sucesso? → `questions.md#pergunta-81` ✅ decidido (aceito em 2026-10-10)
- **[stick]** Depois de um giro livre (R) num item grudado, o assentar deve restaurar a orientação em relação à face (004 D-04b)? E num hospedeiro com escala de objeto diferente de 1, os campos u/v/Distância devem ser em metros do mundo? → `questions.md#pergunta-82` ✅ decidido (aceito em 2026-10-10)
- **[customize]** Material por peça num módulo btm (malha única) ou em malha sem GeoNodeCutpart deve ser aplicado, ou o botão "Peça …" deve sumir nesses casos? Hoje grava, reporta sucesso e nada muda. → `questions.md#pergunta-83` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** A Região da aba Portas (Inferior, Superior, Alta) deve mudar algo além de Basculante? Hoje só FLIP tem efeito (EC-13). → `questions.md#pergunta-84` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** A mensagem 'Selecione uma divisória na vista para mover com as setas' deve aparecer? Hoje process limpa s.error logo depois (EC-01). → `questions.md#pergunta-85` ✅ decidido (aceito em 2026-10-10)
- **[cabinet_editor]** É aceitável que cada Ctrl+Z/Ctrl+Y do editor apague e recrie internos, extras e deslizantes (nomes .001 e custo) mesmo sem mudança neles (EC-12)? Há meta de tempo para o desfazer no editor? → `questions.md#pergunta-86` ✅ decidido (aceito em 2026-10-10)
- **[standards]** Qual o comportamento esperado de Ctrl+Z depois da sequência Configurador → 1ª pergunta → 2ª pergunta: um passo para tudo ou um por operador? Não foi verificado no Blender. → `questions.md#pergunta-87` ✅ decidido (aceito em 2026-10-10)
- **[library_panel]** A coluna não tem rolagem nem limite: com muitas categorias, as últimas (inclusive 'Criar categoria') saem da área visível. Há um número máximo de categorias esperado, ou a coluna deve rolar/quebrar? → `questions.md#pergunta-88` ✅ decidido (aceito em 2026-10-10)
- **[library_panel]** Com duas viewports ou duas janelas, o estado aberto é único (abre em todas) e o hover guarda uma região só; e a ordem efetiva do keymap frente ao HUD e à seleção por componente não foi testada com o HUD ligado. Esse comportamento é aceitável? → `questions.md#pergunta-89` ✅ decidido (aceito em 2026-10-10)
- **[object_library]** A inserção de objetos não tem encaixe (snapping) nem colisão, e a raiz Empty e as malhas filhas dos itens ficam fora da verificação de colisão. Isso é intencional? → `questions.md#pergunta-90` ✅ decidido (aceito em 2026-10-10)
- **[object_library]** Quando o modal é cancelado de fora (fechar a janela, abrir outro arquivo), os objetos carregados ficam na cena. Devem ser removidos como no Esc? → `questions.md#pergunta-91` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** Ao desativar a extensão com o modo de inspeção rodando, o unregister só zera _active: timers, modal handler e o registro no HUD ficam vivos. Deve encerrar a sessão (chamar _finish)? → `questions.md#pergunta-92` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** Os resultados de interferência ficam no WindowManager sem invalidação: mover ou apagar objetos mantém a cruz e o rótulo no ponto antigo. Devem ser invalidados ao editar, como na colisão de corpo? → `questions.md#pergunta-93` ✅ decidido (aceito em 2026-10-10)
- **[inspection]** A primeira abertura de uma porta de ambiente cria pivô e folha por um operador sem UNDO; o Ctrl+Z seguinte pode ou não removê-los. É aceitável, ou a criação da folha deve entrar no histórico? → `questions.md#pergunta-94` ✅ decidido (aceito em 2026-10-10)
- **[molding]** Arrastar Reveal/Stack Offset/Cap Offset apaga e recria todas as molduras a cada passo do arraste. Isso é aceitável ou a reconstrução deve ser adiada (debounce) para o fim do arraste? → `questions.md#pergunta-95` ✅ decidido (aceito em 2026-10-10)
- **[geometry_free]** A feature 002 pedia digitar a espessura durante a criação (RF-11) e material/acabamento por face (RF-12); o código não faz nenhum dos dois (espessura vem de 0,018 m; um único material em texto). Isso continua sendo requisito ou o comportamento atual foi aceito? → `questions.md#pergunta-96` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** Atualizar esses artefatos (stick wall_side com espessura 0 ⇒ POS_Y; manifesto 1.1.0 real; collision.check_item inexistente)? → `questions.md#pergunta-97` ✅ decidido (aceito em 2026-10-10)
- **[revisão cruzada]** catalog/ é código morto a remover ou será religado? → `questions.md#pergunta-98` ✅ decidido (aceito em 2026-10-10)

## Parte B — Crítico

- **[customize]** EC-01: library_io.load usa `missing` sem defini-lo quando não há .json; inserir grupo antigo (e Substituir em move_over/ops_substitute) quebra com UnboundLocalError deixando os objetos ligados à cena. Correção: `missing = []` antes do `if data is not None`. Reproduzido no Blender 5.2.

## Parte B — Moderado

- **[canvas2d]** open_window fallback, CA-12 e _close sem teste automatizado; abertura só coberta indiretamente por smoke tests do Blender
- **[canvas2d]** View2D sem guarda contra escala zero (rect com lado 0 em fit) -> ZeroDivisionError em to_world/pan; visible_width não tem piso
- **[walls2d]** EC-10: _side_set não passa por _guard; a troca de Direção pelo painel se perde num Ctrl+Z imediato (props.py:188-197)
- **[walls2d]** EC-02: Delete em cadeia fechada não limpa s.selected; o painel passa a mostrar outro trecho e um 2º Delete remove outra parede (ops_editor.py:remove_segment 442-447)
- **[measure]** scene_cotas.py sem teste puro ou Blender para ceiling_height (fallbacks), ModuleCotas.apply livre/na parede e vizinho sem mod_name (TT-04)
- **[measure]** ui/object_properties.py:_cota_getter não trata ValueError de GeoNodeWall.get_input('Length') (EC-08): erro no getter da propriedade durante o desenho do painel
- **[move_over]** Sem teste do aviso de sobreposição em duas confirmações nem do modal Mover na Parede (TT-07, TT-08); testes Blender existentes não foram executados nesta revisão
- **[selection]** Sem teste de editing.py (limites, overrides, set_wall) nem de EC-08/EC-10 (TT-07)
- **[selection]** Testes Blender (blender_011_component_smoke.py, blender_toast_resize_invert.py, blender_bug_TBY3_walls.py, blender_012_legacy_gate_smoke.py) não foram executados nesta revisão
- **[openings]** caffmob.openings_update e walls2d/apply.apply_plan chamam sync sem try: uma exceção numa caixa interrompe o operador e as caixas seguintes não são processadas (EC-11)
- **[openings]** Sem teste de materials.py, build.py (contagem de malhas, chanfro único), EC-02, EC-04, EC-07, EC-10 (TT-07)
- **[openings]** Testes Blender (blender_010_openings_smoke.py, blender_011_region_smoke.py, blender_bug_YIMY_openings.py, blender_bug_porta_real_abre.py, blender_toast_resize_invert.py) não executados nesta revisão
- **[aggregates]** Sem teste para can_convert (ordem dos motivos e o teste de descendência), desconverter após mover o pai (EC-02), folha com pai parede (EC-07), renomear perfurado (EC-09), desinstalar (EC-14), Delete de parede com agregado em módulo (EC-16)
- **[aggregates]** Renomear agregado com furo real deixa o CPM_CUTOUT antigo no pai e na usinagem (furo fantasma exportado); vínculo por nome em perforate.py
- **[aggregates]** Testes Blender da unit (blender_003_aggregates_smoke, blender_004_collision_smoke, blender_007_window_smoke, blender_009/010 skp, blender_011_component_smoke, blender_012_apply_smoke) não executados nesta revisão (sem Blender no ambiente); 35 testes puros aprovados
- **[collision]** Sem teste para check_moved sem verificação prévia (EC-04), ordem após check_moved (EC-05), erro persistente (EC-10), escopo SELECTED com abertura/agregado (EC-09), push de item grudado (CA-22)
- **[collision]** tests/blender_004_collision_smoke.py (inclui 200 itens ≤ 2 s) não executado nesta revisão (sem Blender no ambiente)
- **[stick]** EC-09: link.release compara parent.name (string) com objetos em children_recursive (sempre verdadeiro); se orig_parent virou descendente do item, cria ciclo de parentesco. Trocar por `parent not in item.children_recursive`.
- **[customize]** EC-02: _missing_styles não conhece fronts_closets.FRONT_STYLES (existing = set()) e o filtro por prefixo "Estilo '" apaga o aviso real "Estilo '{}' não existe no closets". Reproduzido no Blender 5.2.
- **[customize]** EC-06: panels.draw_customize não passa kind ao menu Estilo, então drawer_style não é editável pelo painel (RF-03 promete estilo de gaveta).
- **[customize]** EC-09: interior_from_json converte tipos fora do try; um btm_custom.interior com valor não numérico quebra read, reapply e o painel do módulo.
- **[cabinet_editor]** EC-05: insert_reason não confere a aba do item de catálogo; Internos com SLIDE_* cria painel sem recorte e Deslizantes com OVEN cria folhas com esse 'estilo'.
- **[cabinet_editor]** EC-15: eletro mais profundo que o vão não gera aviso (too_small ignora profundidade e GEO-001 não olha Y).
- **[standards]** EC-05: document_to_values não valida a forma interna (lines com lista, edges inteiro) e levanta AttributeError/TypeError que o operador não captura.
- **[standards]** EC-14: migration.run só captura StandardsError; outra exceção interrompe o resto do load_file_post (stick.migrate.run, HUD) em caffmob_draw/__init__.py:99.
- **[legacy]** Sem teste de integração de convert_group/convert_pending com um .blend de grupo real (TT-05): nomes 'Nome 1/2', sufixo ' (2)', limpeza e marcador
- **[library_panel]** Sem teste puro de categories.load/create com pasta temporária (TT-04: EC-01 e não-cache de OSError, EC-03)
- **[library_panel]** Sem teste de models_core.parse com valor não numérico (TT-05): ValueError não capturado quebra o popover inteiro (EC-07)
- **[object_library]** EC-01: manifesto com tipo inesperado (features 5, materials 5, size_mm [null,...]) levanta TypeError não capturado em store._scan e quebra a seção Inserir › Objetos, find_item e existing_names enquanto o arquivo existir; basta capturar TypeError junto com ValueError
- **[object_library]** Sem teste automatizado do modal (TT-03), inclusive invocado pela barra lateral
- **[inspection]** Sem teste do modal com eventos simulados (TT-03), do gizmo em folha convertida (TT-04) e de salvar durante animação (TT-05).
- **[molding]** Nenhum teste automatizado da unit (puro ou smoke); as sondas desta revisão (CA-03/06/09/13/14/15/16) podem virar tests/blender_molding_smoke.py e um teste puro dos offsets.
- **[molding]** EC-04/EC-11: TypeError não capturado em _profile_metrics/clear_scene_molding (bpy.data.curves.remove com dado que não é Curve) aborta a reconstrução depois de apagar todas as molduras; testar isinstance(data, bpy.types.Curve) antes de remover.
- **[geometry_free]** EC-01: BTM_OT_GeometryCreate não tem cancel(); interrupção externa do modal deixa o objeto provisório com HB_CURRENT_DRAW_OBJ e o cabeçalho preso — implementar cancel() chamando a limpeza de _cancel.
- **[geometry_free]** EC-06/EC-07: _typed_value não recalcula obj.location após medida digitada com arraste negativo; typed_width guarda o valor sem limite e desloca a origem por ele.
- **[geometry_free]** EC-12: Shift+D nativo copia btm_uid; o JSON global passa a falhar a validação por uid duplicado. Regenerar o uid quando dois objetos o compartilham na extração.

## Parte B — Cosmético

- **[canvas2d]** Sem teste para contains na borda exata, zoom com fator <= 0, ortho_snap perto de 360° e tolerância exata 2,5°
- **[canvas2d]** draw.dashed sem teste (exige stub de gpu/blf para importar draw.py)
- **[walls2d]** EC-13: project_height não passa por validate antes de ser gravado nas paredes com Igualar (apply.py:248-251)
- **[walls2d]** CA-04 (remove_node com trecho único) e CA-02 com o valor exato não têm teste puro
- **[walls2d]** EC-01, EC-03, EC-05, EC-06, EC-07 sem teste identificado
- **[walls2d]** Docstring de resolve_point (ops_editor.py:378) diz alinhamento → ortogonal, mas o código aplica ortogonal antes do alinhamento
- **[measure]** Sem teste para obstáculo que cruza/encosta em X/Z, campo desconhecido, módulo mais largo que a parede (TT-02, CA-06)
- **[measure]** cotas.apply com campo desconhecido e valor negativo levanta KeyError em vez de ValueError (EC-07); consumidores só passam FIELDS
- **[move_over]** Sem teste puro para combine com dois alvos no mesmo eixo, gaps negativo (sobreposição em X), empate de side_of e delta_for com tipo desconhecido (TT-03)
- **[move_over]** Rotação digitada inválida mostra a mensagem crua do float() em inglês no painel (EC-08)
- **[selection]** Sem teste puro dedicado para cota filha de vão (EC-01), agregado em grupo SketchUp (EC-02), own_aggregates(parede) (EC-07) e btm_kind sem is_property_set; comportamento confirmado por execução manual nesta revisão
- **[selection]** Mensagens em inglês do hb_types vazam para o usuário em set_dimension do frameless sem GN (EC-09) e no Redimensionar da janela BTM (EC-10)
- **[openings]** Sem teste puro dedicado para tolerâncias de fit em x0/x1/z1, porta sobre janela e kind desconhecido (comportamento confirmado por execução nesta revisão)
- **[openings]** Docstring de build.py e code-analysis §9.5 ainda dizem '5 a 6 objetos por porta'; são 4 malhas + 3 Empties na porta simples
- **[aggregates]** install.install quebra com TypeError se group_box(frame) for None (esquadria sem membros, ex. raiz de FBX marcada como grupo sem members, EC-10); can_install não testa isso
- **[aggregates]** rebuild_pivot reaproveita o pivô sem atualizar empty_display_type quando motion muda (SINGLE_ARROW fica numa folha de correr)
- **[aggregates]** apply.py declara _last_parent_box duas vezes (a segunda depois do handler); inofensivo, já registrado em code-analysis §10.1
- **[collision]** tests/test_collision_rules.py não cobre tolerância no limite (1,0 mm instável), concêntricos (EC-12), ponto do rótulo (EC-02) nem eixo cruzado (EC-13); comportamento conferido por execução manual
- **[collision]** Painel: as linhas de ocorrência são criadas em layout.row, fora da coluna com alert; só o cabeçalho fica vermelho (panels.py:143-148)
- **[stick]** Os 6 rótulos de aggregates/limits.FACE_LABELS passam por tr() mas não têm entrada em nenhum catálogo: em en_US o painel mostra "Direita (+X)" etc. em português.
- **[stick]** TT-05: sem teste para pai trocado, hospedeiro renomeado, desgrudar módulo de parede, wall_side sem espessura, face interna → PLANE, escala ≠ 1, giro livre, stick_move com Ctrl, spin pelo painel, face não plana pelo operador e apagar hospedeiro sem invalidate().
- **[stick]** TT-02: limites exatos de choose_face/contact_axis/out_of_face e normal nula só foram verificados à mão; vale virar testes em tests/test_stick_frame.py.
- **[stick]** EC-15: exceção que não seja ReferenceError dentro de settle.run descarta o lote de _pending (já limpo) e encerra o temporizador sem log.
- **[stick]** Validação visual da prévia do ímã (contorno, caixa e texto) segue pendente; as fumaças só verificam magnet_preview.compute.
- **[customize]** library_io.save: falha entre os dois os.replace deixa .blend novo com .json antigo (não é totalmente atômico).
- **[customize]** EC-12: R na inserção gira só a raiz; os outros objetos soltos não giram nem têm o offset girado.
- **[customize]** EC-20: set_interior inválido pelo operador devolve FINISHED (passo de desfazer vazio).
- **[customize]** 6 self.report com texto literal (sem tr) em ops_customize/ops_library e o rótulo da frente em btm.set_front sem tr: ficam em português no en_US.
- **[customize]** TT-04: sem teste automatizado para EC-01, EC-02, EC-09 e EC-13 (EC-01/02/04 só foram reproduzidos por sonda manual).
- **[cabinet_editor]** EC-09: aviso 'sem vão interno' vira 'Os trilhos precisam de mais profundidade (sem vão interno)', mensagem enganosa e com metros não traduzidos.
- **[cabinet_editor]** EC-20: 'Sem Divisória' num subvão de bay remove a bay sem o aviso de SET_BAYS.
- **[cabinet_editor]** TT-03 (teste puro de EC-07) e TT-04 (smoke de EC-01/EC-02) não existem.
- **[standards]** EC-06: import_definition(on_conflict='replace') com a homônima antes da ativa desloca a definição ativa sem aviso (só scripts).
- **[standards]** ops_standards.py:_definition_items guarda em cache a lista vazia, mas devolve a lista literal [('NONE', ...)] sem cache quando não há definições (strings de enum dinâmico sem referência).
- **[standards]** Não há teste puro de io_json (TT-02) nem de validate com NaN/inf (TT-03).
- **[standards]** RN-13/RN-15: para módulos CAFFMob, 'Padrão próprio por overrides' e o `clear_overrides` de apply_to_module não têm escritor correspondente no pacote (sem efeito prático hoje).
- **[legacy]** Sem teste automatizado de falha no meio do lote (TT-06); comportamento só conhecido por sonda
- **[legacy]** CA-03 (armário herdado aninhado) e CA-05 (aviso por timer no load_post) sem teste; a fumaça chama neutralize_product_tab direto, não via load_post
- **[legacy]** write_marker não remove o .tmp quando a escrita ou o os.replace falham (EC-09)
- **[library_panel]** Fumaça de UI não exercita clique fora/Esc (CA-03) nem Criar armário fora do modo objeto (CA-13)
- **[library_panel]** categories_core.parse aceita "name": null como categoria "None" e models_core aceita label null como "None"
- **[library_panel]** layout_core.bounds sem consumidor (código morto)
- **[object_library]** item_io.save deixa o .json temporário quando json.dump falha (entra na lista de limpeza só depois)
- **[object_library]** catalog._ID com $ aceita item_id com \n final; usar fullmatch
- **[object_library]** Listagem sem cache: cada redesenho da seção relê as duas pastas e todos os manifestos (EC-13); sem meta de desempenho
- **[inspection]** overlay._draw_3d deixa gpu.state.depth_test_set('NONE') sem restaurar ao fim do desenho (EC-17); restaurar o estado anterior evita afetar outros draw handlers.
- **[inspection]** O smoke não cobre portas de ambiente (room_doors) nem folhas convertidas (aggregate_leaf) em iter_fronts/abrir/interferência.
- **[inspection]** props.py:default_angle tem descrição 'usado pelo clique ... e por "Abrir tudo"', mas BTM_OT_FrontsSetOpen ignora default_angle (usa o próprio mode).
- **[inspection]** EC-14: a mensagem de fronts_set_open conta len(targets), inclusive frentes puladas por ReferenceError.
- **[molding]** EC-03: _spawn_sweep remove objetos sweep/perfil sem spline mas deixa os dados de curva órfãos até salvar/recarregar.
- **[molding]** EC-12: perfil filho de um sweep apagado à mão não é encontrado por clear_scene_molding (só procura via bevel_object) e acumula oculto na cena.
- **[molding]** Sem rollback: falha no meio de apply_scene_packages deixa a cena parcialmente limpa/reconstruída.
- **[geometry_free]** Sem teste puro de size/sheets (TT-01) nem smoke do modal com eventos simulados (TT-03), parent/escala (TT-04) e Shift+D nativo (TT-05).
- **[geometry_free]** Rótulos Forma/Posição da Placa/Peça de Fabricação/Componente/Matéria-prima/Acabamento e nomes das chapas (Fundo, Tampo…) não passam por N_/tr.
- **[revisão cruzada]** aggregates/ops_aggregate._release_stuck_children grava btm_stick.orig_parent direto, fora de stick.apply.write (sem efeito hoje: orig_parent não tem update)
- **[revisão cruzada]** aggregates/limits.box_for: docstring diz que o grudar usa clamp_to_face=False, mas o ramo não tem chamador
- **[revisão cruzada]** walls2d/ops_editor.resolve_point: docstring lista alinhamento antes da trava ortogonal; o código faz o contrário
- **[revisão cruzada]** aggregates/ops_aggregate.BTM_OT_DeleteWithAggregates.poll: comentário 'parede, piso e teto seguem no Delete do Blender' é impreciso
- **[revisão cruzada]** collision/scan._Meshes: docstring 'mesmo cálculo de inspection/interference._Targets' — é cópia divergente (CURVE, display_type)
- **[revisão cruzada]** Raiz do repositório: molding/ops.py espelhado ainda usa home_builder.refresh_room_molding (cópia não empacotada)

## Parte C — Código sem unit de spec

- `cutting/ (csv_exporter, drilling, hardware, json_exporter, machining, part_roles, part_sources, stale, part_extractor) + operators/ops_cutting.py + operators/export.py` → unit 'production' (lista de peças, furação, ferragens, JSON/CSV, plano desatualizado); substitui _reversa_sdd/cutting/ de 2026-07, que só cobre nesting.py. Necessária para fechar as notas 27 e 31
- `ui/ (context_menu, object_properties, ops_resize, save_feedback, sidebar*, view_mode*, layout_probe, my_modules) e ui/panels.py, ui/menus.py, ui/view3d_sidebar.py, ui/menu_apend.py (cobertos só por spec 2026-07 ou citação)` → unit 'sidebar_ui' (barra lateral única, menu de contexto, propriedades do objeto, vocabulário de ações, aviso ao salvar, modos de vista)
- `data/expr.py, data/i18n.py, data/units.py, data/dimensions_preset.py, data/properties.py (cresceu desde 2026-07), compat.py, compat_identity.py, library_common.py` → unit 'core_data' (expressões, tradução, unidades, presets, compat de versão e identidade, utilitários de biblioteca); compat.py hoje é só transversal
- `operators/ops_wall_extras.py, operators/ops_dimensions.py, geometry/floor_outline.py` → unit 'wall_extras' (remover/rebaixar/visibilidade de parede, cotas, contorno de piso) ou anexar a walls2d; KEEP_WITH_WALL e remove_wall são contrato de exclusão (selection EC-18)
- `overlays/element_toast.py, overlays/selection_cotas.py` → anexar a 'sidebar_ui' ou a measure/selection como consumidores com contrato
- `operators/rooms.py, operators/ops_stairs.py, operators/cabinet_builder.py, geometry/door_controller.py, operators/doors_windows.py, operators/walls.py (cobertos por specs 2026-07/legadas só por citação)` → re-extrair: cabinet_builder e doors_windows são contrato de standards/openings/selection; rooms/stairs podem ir para uma unit legada 'hb_rooms'
- `catalog/ (7 arquivos)` → coberto só por catalog_molding e não importado pelo add-on: confirmar com o titular se é código morto

## Contradições novas entre units (revisão cruzada)

- {"contact": "selection ↔ aggregates ↔ walls2d (exclusão de parede)", "detail": "Três caminhos apagam parede com resultados diferentes: X/Delete pelo plugin (quando há agregado/grudado abaixo) ou Delete nativo apagam só a parede e os filhos não grudados (caixas de porta/janela, geometrias, cotas, obj_x, proxy rebaixado) perdem o pai e saltam para a posição local (sonda Blender 5.2: (5,1,0) → (1,0,0)); caffmob.wall_remove/walls2d.apply (ops_wall_extras.remove_wall) solta mantendo a matriz de mundo e apaga aberturas/cotas/proxy junto.", "files_fixed": ["_reversa_sdd/selection/edge-cases.md (EC-18)"], "severity": "moderado"}
- {"contact": "geometry_free ↔ aggregates ↔ cutting", "detail": "Geometria livre convertida em agregado com production_part sai duas vezes em geometry_records com o mesmo uid <btm_uid>/<component>/0; validate_global_json acusa uid duplicado.", "files_fixed": ["_reversa_sdd/aggregates/edge-cases.md (EC-23)", "_reversa_sdd/geometry_free/requirements.md (RN-15)", "_reversa_sdd/aggregates/design.md"], "severity": "moderado"}
- {"contact": "openings ↔ walls2d ↔ collision", "detail": "Folha de porta/janela real é ITEM fino ligada só ao FRAME: o par folha × parede hospedeira (não só folha × caixa) não é excluído; folha aberta cruzando a face no batente pode gerar 'Penetração em parede' falsa.", "files_fixed": ["_reversa_sdd/collision/edge-cases.md (EC-22)"], "severity": "moderado"}
- {"contact": "openings ↔ selection", "detail": "Editar Dim X/Z da porta pelo painel não refaz a porta real e não há handler que o faça; só 'Atualizar portas e janelas' recupera.", "files_fixed": ["_reversa_sdd/openings/edge-cases.md (EC-21)", "_reversa_sdd/selection/edge-cases.md (EC-08)"], "severity": "moderado"}
- {"contact": "move_over ↔ collision ↔ object_library", "detail": "Aviso de sobreposição do Mover Sobre só compara com módulos; colisão ignora grupos soltos; módulo sobre grupo solto não é avisado por nenhum dos dois.", "files_fixed": ["_reversa_sdd/move_over/edge-cases.md (EC-22)"], "severity": "cosmetico"}
- {"contact": "walls2d ↔ openings", "detail": "walls2d.apply_plan chama openings.sync sem try (exceção sobe depois de gravar paredes), ao contrário de _sync_opening que engole.", "files_fixed": ["_reversa_sdd/walls2d/design.md"], "severity": "cosmetico"}
- {"contact": "collision ↔ data-dictionary", "detail": "data-dictionary dizia que collision_override liga/desliga ignorando o global; só OFF age e o global desligado vence (divergência registrada por collision e ainda não corrigida no global).", "files_fixed": ["_reversa_sdd/data-dictionary.md"], "severity": "cosmetico"}
- {"contact": "geometry_free ↔ standards (impacto)", "detail": "geometry_free/props.py importa data/dimension_schema.py, arquivo da unit standards; a spec-impact-matrix mostrava só geometry_free → data.", "files_fixed": ["_reversa_sdd/traceability/spec-impact-matrix.md"], "severity": "cosmetico"}
