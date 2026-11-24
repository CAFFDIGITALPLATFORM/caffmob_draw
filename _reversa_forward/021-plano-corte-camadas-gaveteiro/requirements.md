# Requirements: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O projetista de interiores e o marceneiro que utilizam o CAFFMob Draw enfrentam hoje lacunas críticas no fluxo diário de modelagem e produção: o plano de corte não agrupa peças por módulo nem usa o motor de otimização de referência OpCut, texturas perdidas do addon não possuem recuperação automática, não há controle global rápido de colisão na interface, camadas de cena (Arquitetura e Marcenaria) não recebem todos os elementos correspondentes, o pé-direito e os padrões de parede não ficam acessíveis rapidamente na aba Ferramentas, desgrudar um armário gera ciclo infinito de reacoplamento, "Criar Armário" abre a galeria legada verde-escura em vez do construtor atual, paredes rebaixadas perdem o reconhecimento para restauração e gaveteiros modelados manualmente não podem ser convertidos com identificação automática de peças. Esta entrega unifica essas dez melhorias e correções em um pacote coeso de produtividade, organização de cena e preparação para produção no Blender.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | Pacote `caffmob_draw/` em Blender ≥ 5.2; camadas de Produção (`cutting`), Edição de ambiente (`walls2d`), Mobiliário (`armario_v2`, `cabinet_editor`), Posicionamento (`stick`), Verificação (`collision`) e Interação (`ui`, `library_panel`). | 🟢 |
| `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` | Definição de Plano de Corte (Nesting), Chapa padrão de 2750 × 1830 mm, Refilo padrão de 10 mm, espessura de serra (Kerf) padrão de 4 mm e Sentido da Fibra/Veio (`NONE`, `VERTICAL`, `HORIZONTAL`). | 🟢 |
| `_reversa_sdd/domain.md#2.3 Regras de Otimização de Plano de Corte` | Regras `R-09` (precedência de área) e `R-10` (corte guilhotinado em prateleiras), hoje implementadas de forma simplificada em `cutting/nesting.py`. | 🟢 |
| `_reversa_sdd/addenda/017-construtor-armario-v2.md#Impacto por artefato da extração` | Construtor de armário v2 (`armario_v2`) como motor ativo de mobiliário; origem `ARMARIO_V2` no plano de corte com ferragens excluídas da lista de chapas. | 🟢 |
| `_reversa_sdd/domain.md#walls2d` | Regras `RN-WALLS2D-01` a `RN-WALLS2D-17` sobre espessura, pé-direito (0,5–10 m), mureta (1100 mm), pisos/tetos e sincronização de paredes; paredes hoje organizadas em `Arquitetura > Parede`. | 🟢 |
| `_reversa_sdd/domain.md#collision` | Regra `RN-COLLISION-08`: chave global `collision_global` desliga o motor de colisão, mas carece de botão global direto de alternância no cabeçalho da viewport 3D. | 🟢 |
| `_reversa_sdd/domain.md#stick` | Regras `RN-STICK-10` (desgrudar mantém posição no mundo), `RN-STICK-11` (assentar após 0,2 s) e `RN-STICK-12` (ímã reacopla a até 50 mm da face), cuja interação provoca o ciclo infinito de reacoplamento ao mover para frente. | 🟢 |
| `_reversa_sdd/domain.md#selection` | Regras `RN-SELECTION-01` e `RN-SELECTION-02`: classificador de objetos da cena usado pelo menu de contexto e painel de propriedades; objetos proxy sem marca de parede caem em `OTHER`. | 🟢 |
| `_reversa_sdd/code-analysis.md#17. Módulo library_panel` | Fluxo do botão "Criar Armário" (`BTM_OT_LibraryCreateCabinet`), que atualmente desvia para a galeria de estruturas de caixa legada com paleta verde escura antes do construtor. | 🟢 |
| `_reversa_sdd/code-analysis.md#11. Módulo collision` | Estrutura de verificação de colisões e dependência da chave global `collision_global` em `data/properties.py` e `hb_placement.py`. | 🟢 |
| `_reversa_forward/020-converter-em-armario/requirements.md#4. Regras de negócio novas ou alteradas` | Precedente de conversão não destrutiva via menu de botão direito e toque longo ("Converter em..."), preservando origens ocultas fora do corte com passo único de desfazer. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro projetista | Gerar lista de peças por módulo e otimizar chapas para corte | Agrupa as peças por módulo no projeto e gera o plano de corte otimizado offline baseado no OpCut, visualizando dentro do Blender e exportando em HTML/SVG/PDF. |
| Projetista de interiores | Configurar o ambiente e manter a cena organizada desde o início | Define pé-direito e espessura padrão na aba Ferramentas, gera paredes, piso (com espessura para cima ou para baixo), teto e aberturas nas subcoleções de `Arquitetura`, e cria armários diretamente pelo construtor v2 na camada `Marcenaria`. |
| Projetista de interiores | Manipular layout sem atritos de posicionamento ou visualização | Alterna colisões globalmente pelo cabeçalho da Viewport 3D, desgruda um armário e o move para frente sem ser puxado de volta, e restaura paredes rebaixadas ao clicar diretamente nelas. |
| Projetista de interiores | Recuperar projeto com texturas ausentes após mover arquivos ou limpar cache | Aciona o botão de sincronizar texturas perdidas no painel de Texturas/Materiais para baixar novamente e reconectar automaticamente os arquivos ausentes. |
| Marceneiro / Modelador 3D | Aproveitar gaveteiros modelados manualmente no fluxo paramétrico e de produção | Clica com o botão direito (ou toque longo) em um gaveteiro manual, escolhe "Converter em: Gaveteiro", decide se quer completar peças faltantes e abre o editor para editar livremente. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 (Lista de peças agrupada por módulo):** A lista de peças de produção deve permitir agrupamento hierárquico por módulo proprietário (identificando nome do módulo, quantidade de peças, dimensões em milímetros, espessura, material e sentido do veio), mantendo fora da contagem de chapas as ferragens e itens marcados com exclusão de corte. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` e `_reversa_sdd/addenda/017-construtor-armario-v2.md#Impacto por artefato da extração`
   - Tipo: alterada
2. **RN-02 (Plano de corte offline compatível com OpCut com visualização interna e exportação):** O módulo de plano de corte deve embutir 100% offline em Python dentro do addon a lógica de otimização de corte guilhotinado bidimensional do sistema de referência OpCut (`https://github.com/bozokopic/opcut`), respeitando dimensões de chapa (padrão 2750 × 1830 mm), refilo (padrão 10 mm), espessura de serra/kerf (padrão 4 mm) e restrição de rotação por sentido do veio. O resultado deve ser exibido em visualizador/painel dentro do próprio Blender e permitir exportação para arquivo (HTML, SVG e PDF). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#2.3 Regras de Otimização de Plano de Corte` (`R-09`, `R-10`); decisão do titular em `/reversa-clarify` (2026-11-24)
   - Tipo: alterada
3. **RN-03 (Sincronização e re-download de texturas perdidas):** O painel de Texturas/Materiais deve disponibilizar ação dedicada para detectar texturas pertencentes ao catálogo do addon cujos arquivos locais estejam ausentes ou inválidos no disco, baixá-los novamente em lote e reconectar automaticamente os materiais da cena sem sobrescrever texturas íntegras já presentes. 🟢
   - Origem no legado: `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual`; decisão do titular em `/reversa-clarify` (2026-11-24)
   - Tipo: nova
4. **RN-04 (Controle global de colisões no cabeçalho da Viewport 3D):** A chave global de colisão (`collision_global`) deve ficar acessível por um botão global de ativar/desativar no cabeçalho (header) da Viewport 3D, refletindo imediatamente o estado ligado ou desligado em todos os fluxos de posicionamento e verificação de colisão. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#collision` (`RN-COLLISION-08`); decisão do titular em `/reversa-clarify` (2026-11-24)
   - Tipo: alterada
5. **RN-05 (Camada de Arquitetura em subcoleções por tipo e espessura direcional do piso):** Todo elemento arquitetural gerado pelo addon deve ser organizado dentro da coleção de topo `Arquitetura` em subcoleções por tipo: `Arquitetura > Parede`, `Arquitetura > Piso`, `Arquitetura > Teto` e `Arquitetura > Aberturas` (com demais elementos arquiteturais vinculados a `Arquitetura`), criando apenas o que faltar e sem renomear coleções existentes do usuário. O piso deve suportar definição explícita de espessura (> 0 mm) e direção de extrusão: **para baixo** (face superior no nível Z de referência, crescendo para −Z) ou **para cima** (face inferior no nível Z de referência, crescendo para +Z). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-16`) e `_reversa_sdd/domain.md#2.1 Regras de Paredes e Piso`; decisão do titular em `/reversa-clarify` (2026-11-24)
   - Tipo: alterada
6. **RN-06 (Camada de Marcenaria para armários):** Todo armário criado, inserido ou convertido pelo addon deve ser vinculado à coleção (camada) `Marcenaria`, criando-a automaticamente caso não exista na cena, sem apagar nem renomear coleções criadas pelo usuário. 🟢
   - Origem no legado: `_reversa_sdd/addenda/017-construtor-armario-v2.md#Impacto por artefato da extração`
   - Tipo: alterada
7. **RN-07 (Parâmetros padrão rápidos de projeto na aba Ferramentas):** A aba/painel Ferramentas deve oferecer controles diretos para definir o pé-direito padrão (faixa 0,50 m a 10,00 m) e os detalhes padrão de parede do projeto (como espessura padrão na faixa 0,01 m a 2,00 m e parâmetros iniciais do editor). O Editor de Parede deve ler esses valores como padrão inicial antes de qualquer parede ser desenhada. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-02`, `RN-WALLS2D-13`) e `_reversa_sdd/domain.md#measure` (`RN-MEASURE-06`)
   - Tipo: alterada
8. **RN-08 (Quebra do ciclo infinito ao desgrudar armário):** Ao executar "Desgrudar" em um armário (ou módulo) vinculado a uma face hospedeira, o sistema deve suspender o reacoplamento automático pelo ímã (`stick/magnet`) para aquele par item–hospedeiro enquanto o usuário afasta o objeto (especialmente no movimento frontal saindo da parede), impedindo que o assentar (`settle`) puxe o armário de volta para a face anterior. O ímã só volta a atuar sobre o mesmo hospedeiro após o objeto ultrapassar a zona de afastamento ou em gesto intencional de aproximação em direção à face. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#stick` (`RN-STICK-10`, `RN-STICK-11`, `RN-STICK-12`)
   - Tipo: alterada
9. **RN-09 (Acesso direto ao Construtor de Armários v2 e biblioteca compatível com paleta CAFFMob):** A ação "Criar Armário" deve abrir diretamente o Construtor de Armários v2 (`armario_v2`), sem ser interceptada pela biblioteca/galeria legada. A biblioteca de armários permanece acessível no painel de Biblioteca, reestilizada integralmente na paleta visual oficial da CAFFMob (eliminando o visual verde escuro) e mantendo os armários dela compatíveis com o Construtor de Armários v2. 🟢
   - Origem no legado: `_reversa_sdd/code-analysis.md#17. Módulo library_panel` e `_reversa_sdd/addenda/017-construtor-armario-v2.md#Resumo da entrega`; decisão do titular em `/reversa-clarify` (2026-11-24)
   - Tipo: alterada
10. **RN-10 (Reconhecimento e restauração de parede rebaixada):** O objeto representante de uma parede rebaixada (`<parede>_Rebaixada`, altura visual de 150 mm) deve ser reconhecido pelo classificador de seleção do addon como vínculo direto à parede original rebaixada. Ao selecionar uma parede rebaixada na viewport 3D, a interface (painel contextual e menu de contexto) deve exibir explicitamente a ação "Restaurar Parede", que remove o representante rebaixado e torna a parede original visível com suas dimensões preservadas. 🟢
    - Origem no legado: `_reversa_sdd/domain.md#selection` (`RN-SELECTION-01`, `RN-SELECTION-02`) e `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-15`)
    - Tipo: alterada
11. **RN-11 (Conversão em Gaveteiro com reconhecimento de anatomia, oferta de completar peças faltantes e abertura do editor):** O menu de contexto (botão direito do mouse ou toque longo em tela sensível) deve apresentar um submenu **"Converter em:"** contendo a opção **"Gaveteiro"** (ao lado das demais opções de conversão existentes, como Armário). A conversão deve aceitar tanto uma **malha única** (subcomponentes geométricos desconectados ou regiões reconhecíveis pelo formato) quanto **objetos separados**, classificando automaticamente as peças segundo a anatomia padrão de marcenaria:
    - **Peças estruturais da caixa** (referência MDF — Medium Density Fiberboard — 15 mm, exceto fundo): **Laterais** (2 peças, profundidade e altura útil, fixação das corrediças), **Contrafrente** (1 peça, fechamento dianteiro interno), **Posterior / Contrafundo / Traseira** (1 peça, mesma largura da contrafrente) e **Fundo** (1 peça, referência MDF 6 mm, encaixado em rasgo ou fixado por baixo);
    - **Peça de acabamento**: **Frente da gaveta** (1 peça, referência MDF 15 mm ou 18 mm, tampa externa);
    - **Ferragens e acessórios essenciais** (metadados/itens de produção não contabilizados como chapas): **Par de corrediças** (telescópicas laterais ou ocultas/invisíveis por baixo), **Puxador** (externo, embutido ou usinado/cava) e **Fixadores e acabamento** (parafusos, fita de borda nos topos superiores da caixa e nos quatro lados da frente, tapa-furos).
    - **Regra inegociável de não bloqueio e edição livre:** o sistema **nunca deve impedir a criação/conversão do gaveteiro** quando faltarem peças. Ao detectar peças faltantes, deve informar claramente quais peças foram reconhecidas e quais estão ausentes, **perguntar ao usuário se deseja completar/gerar automaticamente as peças faltantes** (opção aceitável ou recusável) e, ao concluir a conversão, **abrir o editor do gaveteiro/armário** para que o usuário tenha liberdade completa de edição. 🟢
    - Origem no legado: `_reversa_forward/020-converter-em-armario/requirements.md#4. Regras de negócio novas ou alteradas` e `_reversa_sdd/domain.md#selection` (`RN-SELECTION-01`); decisão do titular em `/reversa-clarify` (2026-11-24)
    - Tipo: nova
12. **RN-12 (Padrões transversais da extensão):** Todo texto novo da interface deve ser redigido em português brasileiro (`pt_BR`) e traduzido para inglês (`en_US`) no catálogo de internacionalização; todo operador que altera a cena deve declarar passo de desfazer (`UNDO`) e todo manipulador (handler) registrado deve ser removido no `unregister`. 🟢
    - Origem no legado: `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual`
    - Tipo: mantida

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Gerar lista de peças agrupadas por módulo, exibindo por módulo suas peças de chapa (nome, papel, largura × comprimento em mm, espessura, material, veio e quantidade), excluindo ferragens e itens marcados fora do corte (RN-01) | Must | Em uma cena com 2 armários distintos, a lista exibe 2 grupos nomeados conforme os módulos, com a soma exata das chapas de cada um e 0 ferragens misturadas às chapas | 🟢 |
| RF-02 | Gerar plano de corte bidimensional offline em Python utilizando o algoritmo de otimização compatível com OpCut dentro do Blender, com visualização interna em painel/imagem e exportação para arquivo HTML, SVG e PDF, respeitando dimensões de chapa, refilo, kerf e restrição de veio (RN-02) | Must | Ao acionar a geração de plano de corte com peças válidas e sem acesso à internet, o sistema produz o arranjo otimizado em chapas sem sobreposição, exibe a prévia das chapas dentro do Blender e exporta arquivos HTML, SVG e PDF válidos respeitando refilo de 10 mm, kerf de 4 mm e veio travado | 🟢 |
| RF-03 | Exibir botão "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais que identifica texturas do addon ausentes no disco, baixa novamente os arquivos faltantes e reconecta automaticamente os materiais afetados na cena (RN-03) | Must | Ao apagar 1 arquivo de textura baixado do cache local e acionar o botão no painel de Texturas/Materiais, o addon detecta o arquivo ausente, baixa-o novamente, restaura a aparência do material na cena e informa quantas texturas foram recuperadas (ou quais falharam) | 🟢 |
| RF-04 | Disponibilizar botão global de Ativar / Desativar Colisões diretamente no cabeçalho (header) da Viewport 3D, sincronizado com `collision_global` (RN-04) | Must | Um clique no botão no cabeçalho da Viewport 3D alterna `collision_global` entre ligado e desligado com indicação visual clara do estado; quando desligado, nenhum bloqueio ou varredura de colisão é executado | 🟢 |
| RF-05 | Vincular automaticamente Teto, Piso, Paredes, Aberturas e demais objetos arquiteturais gerados pelo addon às subcoleções da camada `Arquitetura` (`Arquitetura > Parede`, `Arquitetura > Piso`, `Arquitetura > Teto`, `Arquitetura > Aberturas`) (RN-05) | Must | Ao gerar paredes, aberturas, piso e teto pelo addon, 100% desses objetos aparecem nas respectivas subcoleções dentro de `Arquitetura`, nunca soltos na raiz da cena | 🟢 |
| RF-06 | Permitir configurar a espessura do piso e escolher a direção da espessura: para baixo (−Z a partir do plano de referência) ou para cima (+Z a partir do plano de referência) (RN-05) | Must | Com espessura de 150 mm definida "para baixo", o topo do piso fica em Z = 0,000 m e a base em Z = −0,150 m; alterando para "para cima", a base fica em Z = 0,000 m e o topo em Z = +0,150 m | 🟢 |
| RF-07 | Vincular automaticamente todos os armários criados, inseridos ou convertidos pelo addon à camada (coleção) `Marcenaria` (RN-06) | Must | Ao criar um armário pelo construtor, inserir da biblioteca ou converter um móvel, a raiz e suas peças ficam organizadas dentro da coleção `Marcenaria` na cena | 🟢 |
| RF-08 | Exibir na aba Ferramentas controles rápidos para definir o pé-direito padrão e detalhes padrão de parede do projeto, consumidos automaticamente pelo Editor de Parede antes de desenhar qualquer trecho (RN-07) | Must | Ao alterar o pé-direito para 2,80 m e a espessura padrão para 150 mm na aba Ferramentas antes de abrir o Editor de Parede, qualquer nova parede desenhada já nasce com 2,80 m de altura e 150 mm de espessura | 🟢 |
| RF-09 | Eliminar o ciclo infinito de reacoplamento ao desgrudar um armário e movê-lo para frente (RN-08) | Must | Após clicar em "Desgrudar" num armário grudado em uma parede e movê-lo 30 mm ou 100 mm para frente, o armário permanece na nova posição após o tempo de assentamento (0,2 s+) sem voltar para a parede nem reacoplar automaticamente | 🟢 |
| RF-10 | Fazer o botão "Criar Armário" abrir diretamente o Construtor de Armários v2, mantendo a biblioteca acessível no painel de Biblioteca com a paleta visual oficial da CAFFMob (sem o verde escuro legado) e com armários compatíveis com o Construtor v2 (RN-09) | Must | Clicar em "Criar Armário" abre imediatamente o Construtor de Armários v2; acessar a Biblioteca de Armários pelo painel de Biblioteca exibe o visual na paleta CAFFMob e qualquer armário inserido dela abre e edita normalmente no Construtor v2 | 🟢 |
| RF-11 | Reconhecer paredes rebaixadas ao serem clicadas na viewport e exibir a opção "Restaurar Parede" para desfazer o rebaixamento (RN-10) | Must | Após rebaixar uma parede fora do editor e clicar no objeto rebaixado de 150 mm, o addon o reconhece como parede rebaixada e exibe o botão "Restaurar Parede"; ao acioná-lo, a parede volta à altura original e o representante rebaixado é removido | 🟢 |
| RF-12 | Adicionar submenu "Converter em:" no menu de botão direito e toque longo contendo a opção "Gaveteiro", aceitando malha única ou objetos separados (RN-11) | Must | Ao clicar com botão direito (ou toque longo) em uma malha única de gaveta ou em um conjunto de objetos separados de um gaveteiro manual, o submenu "Converter em:" exibe "Gaveteiro" | 🟢 |
| RF-13 | Analisar geometricamente a malha ou os objetos selecionados na conversão em Gaveteiro para classificar peças estruturais (2 laterais, contrafrente, traseira, fundo), acabamento (frente) e registrar ferragens/acessórios (corrediças, puxador, fixadores/fita de borda); quando faltarem peças, perguntar ao usuário se deseja completá-las automaticamente sem nunca bloquear a criação, e abrir o editor ao final para edição livre (RN-11) | Must | Converter uma malha com 6 peças classifica as 6 e abre o editor; converter uma malha sem contrafrente e sem fundo exibe aviso com as 2 peças ausentes, pergunta se o usuário deseja gerá-las automaticamente, respeita a escolha (gerando ou mantendo parcial) e abre o editor do gaveteiro para edição livre | 🟢 |
| RF-14 | Disponibilizar todos os textos novos da interface em português (`pt_BR`) e inglês (`en_US`) e garantir suporte a `UNDO` nos operadores de cena (RN-12) | Must | Com o idioma do Blender alternado para inglês, todos os novos botões, rótulos e avisos aparecem traduzidos; executar `Ctrl+Z` após qualquer conversão, criação ou restauração devolve a cena ao estado anterior | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Otimização de plano de corte para até 150 peças deve concluir em até 3 segundos sem travar permanentemente a interface do Blender; análise geométrica de conversão de gaveteiro com até 20 submalhas deve concluir em até 1 segundo. | Referência de interatividade em viewport 3D e metas adotadas nas features 017 e 020 (`_reversa_forward/020-converter-em-armario/requirements.md#6`). | 🟡 |
| Confiabilidade e Rede | A sincronização de texturas perdidas deve aplicar timeout máximo de 15 segundos por arquivo, tolerar até 2 tentativas por textura em falha transitória de rede, permitir cancelamento pelo usuário e nunca deixar arquivos parcialmente gravados no cache (escrita atômica). | Evita congelamento do Blender e corrupção do cache local quando a conexão cai durante o download. | 🟢 |
| Integridade de Dados | Ações destrutivas não são permitidas sem passo de desfazer (`UNDO`): conversão em gaveteiro, restauração de parede e reorganização em camadas devem preservar propriedades existentes e permitir reversão limpa por `Ctrl+Z`. | Princípio não destrutivo e requisitos da extensão (`_reversa_sdd/architecture.md#Persistência e unidades`). | 🟢 |
| Usabilidade e Identidade Visual | Toda interface exibida no fluxo de "Criar Armário", Biblioteca de Armários, Ferramentas, Cabeçalho de Colisão e Menu de Contexto deve seguir a paleta visual oficial da CAFFMob, eliminando desvios visuais legados (verde escuro) e reduzindo cliques em tarefas frequentes. | Solicitação direta do titular sobre desalinhamento visual e agilidade no fluxo de trabalho. | 🟢 |
| Observabilidade | Falhas em sincronização de texturas, peças ausentes detectadas na conversão em gaveteiro e peças que não cabem na chapa durante o plano de corte devem exibir mensagens objetivas ao usuário (aviso/relatório), nunca falhar silenciosamente. | Padrão de transparência de estado já adotado em `_reversa_sdd/domain.md#collision` (`RN-COLLISION-09`). | 🟢 |
| Custo e Operação Local | Nenhuma funcionalidade desta entrega deve consumir APIs pagas de modelos de Inteligência Artificial (IA); o motor de plano de corte compatível com OpCut e toda a análise geométrica executam 100% localmente e offline. | Diretriz de controle de custo e decisão 1a do titular em `/reversa-clarify` (2026-11-24). | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Gerar lista de peças agrupadas por módulo (RF-01)
  Dado uma cena contendo um armário "Balcão Pia" com 6 chapas e 1 par de corrediças e um armário "Aéreo" com 5 chapas
  Quando o projetista gera a lista de peças agrupadas por módulo
  Então a lista exibe o grupo "Balcão Pia" com 6 chapas e o grupo "Aéreo" com 5 chapas
  E o par de corrediças não aparece como chapa de MDF na listagem

Cenário: Gerar plano de corte otimizado offline compatível com OpCut com visualização e exportação (RF-02)
  Dado uma lista válida de 12 peças de MDF 15 mm com chapa padrão 2750 × 1830 mm, refilo 10 mm e kerf 4 mm, sem acesso à internet
  Quando o projetista aciona a geração do plano de corte
  Então o sistema distribui todas as peças em chapas respeitando o refilo, o kerf e o sentido do veio
  E exibe a visualização das chapas dentro do Blender e permite exportar o plano em HTML, SVG e PDF

Cenário: Plano de corte com peça maior que a área útil da chapa (RF-02 — caso negativo)
  Dado uma peça com 2900 mm de comprimento para uma chapa de 2750 × 1830 mm
  Quando o projetista aciona a geração do plano de corte
  Então o sistema não trava e exibe aviso explícito indicando que a peça excede a área útil da chapa

Cenário: Sincronizar texturas perdidas pelo painel de Texturas/Materiais com sucesso (RF-03)
  Dado um projeto que utiliza 2 texturas do catálogo do addon, sendo que 1 arquivo foi removido do disco local
  Quando o projetista clica em "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais
  Então o addon baixa novamente apenas a textura ausente, reconecta o material na cena e informa "1 textura sincronizada"

Cenário: Sincronizar texturas perdidas sem conexão com a internet (RF-03 — caso negativo)
  Dado um projeto com 1 textura ausente do disco e máquina sem acesso à rede
  Quando o projetista clica em "Sincronizar Texturas Perdidas"
  Então o addon respeita o timeout configurado, não grava arquivo corrompido e exibe mensagem informando a falha de conexão

Cenário: Alternar colisões globalmente pelo cabeçalho da Viewport 3D (RF-04)
  Dado a cena aberta com colisões globais ativadas
  Quando o projetista clica no botão global de colisões no cabeçalho da Viewport 3D
  Então o botão indica estado desativado, `collision_global` passa para falso e movimentos de armários deixam de disparar bloqueio de colisão

Cenário: Organizar Teto, Piso, Paredes e Aberturas em subcoleções de Arquitetura com direção de espessura do piso (RF-05, RF-06)
  Dado um projeto novo sem coleções personalizadas
  Quando o projetista gera paredes, aberturas, piso com espessura de 120 mm na direção "para baixo" e teto
  Então as paredes ficam em "Arquitetura > Parede", o piso em "Arquitetura > Piso", o teto em "Arquitetura > Teto" e as aberturas em "Arquitetura > Aberturas"
  E o piso ocupa a faixa vertical de Z = 0,000 m até Z = −0,120 m
  Quando o projetista altera a direção da espessura do piso para "para cima"
  Então o piso passa a ocupar a faixa vertical de Z = 0,000 m até Z = +0,120 m

Cenário: Direcionar armários para a camada Marcenaria (RF-07)
  Dado uma cena aberta no Blender
  Quando o projetista cria um novo armário pelo addon
  Então o armário e suas peças são vinculados à coleção "Marcenaria"

Cenário: Definir pé-direito e detalhes padrão na aba Ferramentas antes do Editor de Parede (RF-08)
  Dado uma cena sem paredes criadas
  Quando o projetista define pé-direito de 2,85 m e espessura padrão de 180 mm na aba Ferramentas e abre o Editor de Parede
  Então o Editor de Parede inicia com pé-direito padrão de 2,85 m e espessura padrão de 180 mm aplicados aos novos trechos

Cenário: Desgrudar armário e movê-lo para frente sem reacoplamento infinito (RF-09)
  Dado um armário grudado na face frontal de uma parede com o ímã ativo (tolerância de 50 mm)
  Quando o projetista clica em "Desgrudar" e move o armário 30 mm para frente (afastando-o da parede)
  Então após o período de assentamento o armário permanece 30 mm à frente da parede e não volta a grudar na parede

Cenário: Abrir Construtor v2 diretamente no Criar Armário e manter Biblioteca compatível com paleta CAFFMob (RF-10)
  Dado a barra lateral do CAFFMob Draw aberta no modo Objeto
  Quando o projetista clica em "Criar Armário"
  Então o Construtor de Armários v2 abre diretamente sem exibir a biblioteca antes
  Quando o projetista acessa a biblioteca de armários pelo painel de Biblioteca
  Então a biblioteca exibe a paleta visual oficial da CAFFMob (sem o verde escuro legado) e os armários inseridos dela são compatíveis com o Construtor de Armários v2

Cenário: Reconhecer e restaurar parede rebaixada (RF-11)
  Dado uma parede com pé-direito de 2,60 m que foi rebaixada fora do editor para o representante visual de 150 mm
  Quando o projetista seleciona o objeto da parede rebaixada na viewport 3D
  Então o addon reconhece o objeto como parede rebaixada e exibe a opção "Restaurar Parede"
  Quando o projetista aciona "Restaurar Parede"
  Então a parede original volta a ficar visível com 2,60 m de altura e o representante de 150 mm é removido

Cenário: Converter malha única completa em Gaveteiro e abrir editor (RF-12, RF-13)
  Dado uma malha única modelada manualmente contendo 2 laterais, 1 contrafrente, 1 traseira, 1 fundo e 1 frente de gaveta
  Quando o projetista abre o menu de contexto (botão direito ou toque longo) e seleciona "Converter em:" -> "Gaveteiro"
  Então o addon identifica as 6 peças da gaveta por papel, permite associar ferragens (corrediças, puxador e acabamentos), cria o gaveteiro na camada "Marcenaria" e abre o editor para edição livre

Cenário: Converter gaveteiro manual com peças faltantes oferecendo completar sem bloqueio (RF-12, RF-13 — caso parcial/negativo)
  Dado objetos separados representando apenas 2 laterais, 1 traseira e 1 frente (sem contrafrente e sem fundo)
  Quando o projetista seleciona os objetos e aciona "Converter em:" -> "Gaveteiro"
  Então o addon sinaliza explicitamente que "Contrafrente" e "Fundo" estão ausentes e pergunta se o usuário deseja completar as peças faltantes
  E caso o usuário recuse completar, o gaveteiro é criado normalmente com as 4 peças disponíveis e o editor é aberto para edição livre
  E caso o usuário aceite completar, o gaveteiro é criado com as peças faltantes geradas e o editor é aberto para edição livre

Cenário: Internacionalização e desfazer nos novos fluxos (RF-14)
  Dado o Blender configurado no idioma inglês (`en_US`)
  Quando o usuário executa qualquer uma das novas ações (converter em gaveteiro, restaurar parede, sincronizar texturas) e pressiona Ctrl+Z
  Então os rótulos aparecem traduzidos corretamente e o desfazer restaura a cena ao estado anterior em um único passo
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Agrupar peças por módulo é base essencial para conferência e orçamento de marcenaria. |
| RF-02 | Must | Plano de corte offline integrado baseado no OpCut elimina dependência de retrabalho manual externo. |
| RF-03 | Must | Recuperar texturas perdidas evita projetos quebrados com materiais cor-de-rosa/ausentes. |
| RF-04 | Must | Controle global de colisão no cabeçalho da viewport reduz atrito constante na movimentação livre de móveis. |
| RF-05 | Must | Organização consistente da camada Arquitetura em subcoleções evita poluição da árvore de cena. |
| RF-06 | Must | Direção da espessura do piso (para cima/baixo) evita erros de cota de pé-direito e rodapé. |
| RF-07 | Must | Separação de armários na camada Marcenaria viabiliza ocultar/isolar marcenaria da obra rapidamente. |
| RF-08 | Must | Definir pé-direito e padrões na aba Ferramentas acelera o início de qualquer projeto. |
| RF-09 | Must | Corrige bug de alto impacto na experiência (ciclo infinito ao desgrudar armário). |
| RF-10 | Must | Corrige regressão de fluxo, alinha identidade visual da marca e garante compatibilidade da biblioteca com o Construtor v2. |
| RF-11 | Must | Corrige bug que deixava paredes rebaixadas presas/irreconhecíveis sem caminho de restauração. |
| RF-12 | Must | Entrada unificada "Converter em: Gaveteiro" no menu de botão direito e toque longo. |
| RF-13 | Must | Reconhecimento geométrico tolerante a peças faltantes com opção de completar e edição livre viabiliza reaproveitar modelos manuais reais. |
| RF-14 | Must | Mantém padrão de qualidade, tradução bilíngue e segurança de `UNDO` da extensão. |
| RNF de Desempenho | Should | Garante fluidez interativa na viewport mesmo em projetos médios/grandes. |
| RNF de Confiabilidade e Rede | Must | Previne congelamento e arquivos corrompidos ao sincronizar texturas. |
| RNF de Integridade de Dados | Must | Protege o trabalho do projetista contra perda de dados em conversões e edições. |
| RNF de Custo e Operação Local | Must | Garante operação 100% local sem custos recorrentes de tokens ou serviços externos. |

## 9. Esclarecimentos

### Sessão 2026-11-24

- **Q:** Plano de Corte (OpCut): como o motor de otimização baseado no OpCut deve rodar e apresentar o resultado no Blender?
  **R:** Embutido 100% offline em Python no addon, com visualização dentro do Blender (painel/imagem gerada) e exportação em arquivo (HTML/SVG/PDF) (opção 1a).
- **Q:** Biblioteca/Galeria legada de armários (visual verde escuro): o que deve acontecer com a galeria antiga quando "Criar Armário" abrir diretamente o Construtor v2?
  **R:** Manter acessível no painel de Biblioteca, sem interceptar "Criar Armário", reestilizada na paleta visual oficial da CAFFMob e mantendo os armários compatíveis com o Construtor v2 (opção 2d + compatibilidade v2).
- **Q:** Conversão em Gaveteiro quando faltarem peças: qual comportamento esperado além de nunca bloquear a criação?
  **R:** Perguntar ao usuário se deseja completar/gerar automaticamente as peças faltantes e abrir o editor para que o usuário tenha liberdade completa de edição (opção 3d + 3c).
- **Q:** Organização da camada `Arquitetura`: como organizar Paredes, Piso, Teto e Aberturas dentro de `Arquitetura`?
  **R:** Subcoleções organizadas por tipo: `Arquitetura > Parede`, `Arquitetura > Piso`, `Arquitetura > Teto`, `Arquitetura > Aberturas` e demais itens arquiteturais em `Arquitetura` (opção 4a).
- **Q:** Posição na interface do Botão Global de Colisões e do Botão de Sincronizar Texturas Perdidas?
  **R:** Botão global de Colisões no cabeçalho (header) da Viewport 3D e "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais (opção 5c).

## 10. Lacunas

Nenhuma lacuna ou dúvida pendente após a sessão de esclarecimentos de 2026-11-24.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-11-24 | Esclarecimentos integrados por `/reversa-clarify` (5 decisões fechadas, 0 dúvidas restantes) | reversa |
