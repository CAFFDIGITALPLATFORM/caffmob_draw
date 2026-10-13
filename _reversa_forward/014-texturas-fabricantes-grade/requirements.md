# Requirements: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O projetista passa a escolher o acabamento real das chapas (MDF, MDP e laminados dos fabricantes de móveis planejados)
numa área de **Texturas** da Biblioteca CAFFMob, em vez de procurar arquivo de imagem no disco a cada peça. A
biblioteca mostra seus itens (blocos e texturas) em **grade com miniatura**, pode ser **maximizada** num retângulo
maior que fica **fixo** enquanto ele trabalha, e aceita **arrastar** um bloco para a cena ou uma textura para uma
peça. O catálogo e as miniaturas vêm no plugin; as imagens em tamanho real vêm do servidor da CAF Mob, com a conta do
projetista, sob demanda ou todas de uma vez para trabalhar offline. Resolve três dores do legado: a biblioteca só
lista botões sem imagem, não existe catálogo de acabamentos de fabricante e não existe arrastar da biblioteca para a
cena.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/library_panel/requirements.md#RN-15` | O conteúdo da categoria abre num popover com "Modelos prontos" em grade de 2 colunas, com ícone fixo e **sem miniaturas** | 🟢 |
| `_reversa_sdd/library_panel/requirements.md` (MoSCoW, "Galeria com miniaturas, rolagem da coluna") | Galeria com miniaturas ficou **Won't nesta versão**; D-15 da 012 descartou a galeria desenhada na viewport | 🟡 |
| `_reversa_forward/012-biblioteca-caffmob-chapas/roadmap.md` (D-13 a D-16) | Painel flutuante sempre visível no topo esquerdo da viewport, coluna de categorias, popover nativo | 🟢 |
| `_reversa_sdd/questions.md#pergunta-88` | Coluna da biblioteca limitada à altura visível, excedente num item "Mais…", sem rolagem na viewport (decisão aceita, ainda não implementada) | 🟢 |
| `_reversa_sdd/object_library/requirements.md#RN-05` | Inserir › Objetos é a única lista com miniatura hoje: grade de 2 colunas, miniatura opcional por item | 🟢 |
| `_reversa_sdd/object_library/requirements.md#RN-17` | Imagem própria vira material "Textura: <arquivo> <tamanho> mm", projeção em caixa, escala real em mm, reaproveita material igual | 🟢 |
| `_reversa_sdd/object_library/requirements.md#RN-15` | Retexturizar vale para a cópia na cena; escopo peça ou item | 🟢 |
| `_reversa_sdd/object_library/requirements.md#RN-09` | O pacote não redistribui conteúdo de terceiros cuja licença proíbe (precedente do 3D Warehouse) | 🟢 |
| `_reversa_sdd/customize/requirements.md#RN-05` e `#RN-13` | Material por instância com precedência peça > grupo > vão; variante "ROTATED" para o veio | 🟢 |
| `_reversa_sdd/standards/requirements.md#RN-01` | O material da chapa no Padrão de Dimensões é só um rótulo de texto (MDF, MDP…), sem imagem | 🟢 |
| `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` | "Sentido da fibra/veio": orientação da textura da madeira na chapa | 🟢 |
| `_reversa_sdd/architecture.md#Integrações e distribuição` | O empacotamento leva só `caffmob_draw/` e confere os ativos de biblioteca e texturas | 🟢 |
| `_reversa_sdd/questions.md#pergunta-60` | Imagem própria é empacotada ao salvar o item na biblioteca de objetos (decisão aceita e implementada) | 🟢 |
| Pasta do titular `/home/theleoinfo/Downloads/materials/textures` (medida em 2026-10-12) | 15.281 arquivos, 3,1 GB; `fabrica/` tem 127 fabricantes. Os 12 fabricantes de chapas claros somam 1.209 texturas (~576 MB, sem as 18 imagens de relevo da pasta "Bumps" da Formica), organizadas em Fabricante › Coleção. As imagens são JPG/PNG, de 365 a 2.750 px; algumas trazem mapa de relevo à parte (`.bump`) | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de móveis planejados | Mostrar ao cliente o acabamento real que vai ser fabricado | Abre Texturas, filtra "Duratex", arrasta "Carvalho Avelã" até a frente do balcão e a frente fica com o padrão na escala certa |
| Projetista montando o ambiente | Montar a cena rápido com blocos prontos | Maximiza a biblioteca, fixa o retângulo ao lado da cena e arrasta balcões, aéreos e objetos um atrás do outro, sem reabrir a biblioteca a cada item |
| Titular (administrador do plugin) | Levar o catálogo de texturas que já tem no computador para dentro do plugin | Aponta a pasta de texturas uma vez; os fabricantes de chapas aparecem organizados por fabricante e coleção |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 Fabricantes que entram:** o catálogo de Texturas traz só os fabricantes de chapas de móveis planejados da
   pasta do titular (`fabrica/`). Estão fora: eletrodomésticos (Brastemp, Consul, Electrolux, Mabe…), vidros, pedras e
   quartzos, puxadores, ferragens, estofados, persianas e itens de decoração. Os 12 fabricantes claros são: Arauco,
   Berneck, Duratex, Eucatex, Fibraplac, Floraplac, Formica, Greenplac, Guararapes, Lopar, Placas do Brasil e Sudati,
   e só eles entram nesta versão (1.209 texturas). Ficam fora também os casos ambíguos (Max Decor, Pigmento Laqueados,
   Exclusivos Leo, Rometal, Roncali, Madelustre, Império do Marceneiro) e as pastas `cinex`, `padroes/madeiras` e
   `revest` (decisão do titular, 2026-10-12). 🟢
   - Tipo: nova
2. **RN-02 Organização:** cada textura pertence a um fabricante e a uma coleção. O fabricante é a pasta de primeiro
   nível e a coleção é a subpasta; uma imagem solta na pasta do fabricante fica na coleção "Geral". O nome mostrado é o
   do arquivo sem extensão, com `_` trocado por espaço e a capitalização original. 🟢
   - Tipo: nova
3. **RN-03 O que é uma textura:** entram arquivos JPG, JPEG e PNG, em qualquer caixa de letra. Mapas de relevo
   (`.bump`, `.bump2`, pastas "Bumps"), arquivos `.resources`, `.specular`, `.txt` e legendas não aparecem como
   textura. Arquivo ilegível ou corrompido vira aviso com o caminho e não interrompe o catálogo. 🟢
   - Tipo: nova
4. **RN-04 Tamanho real:** toda textura tem um tamanho em milímetros, que o projetista pode ajustar por textura.
   Quando as dimensões da imagem em pixels coincidem com uma chapa inteira (lados entre 1.830 e 2.750 px, como
   2.750 × 1.850), vale 1 px = 1 mm 🟡. Nos demais casos, o tamanho inicial é 600 mm no maior lado, o mesmo padrão da
   imagem própria (`_reversa_sdd/object_library/requirements.md#RN-17`), confirmado pelo titular em 2026-10-12 🟢.
   - Tipo: nova
5. **RN-05 Aplicar textura:** aplicar uma textura cria (ou reaproveita) o mesmo tipo de material da imagem própria da
   biblioteca de objetos: projeção em caixa, escala real e um material só por imagem e tamanho
   (`_reversa_sdd/object_library/requirements.md#RN-17`). O alvo pode ser uma peça, uma frente, um grupo do armário ou
   um objeto, respeitando a precedência da personalização (`_reversa_sdd/customize/requirements.md#RN-05`). 🟢
   - Origem no legado: `_reversa_sdd/object_library/requirements.md#RN-17`
   - Tipo: alterada (a imagem passa a vir do catálogo, não só de um arquivo escolhido na hora)
6. **RN-06 Veio:** textura de madeira aplicada a uma peça segue o sentido do veio da peça, com a mesma convenção já
   usada para o veio na personalização (`_reversa_sdd/customize/requirements.md#RN-13`). 🟡
   - Tipo: nova
7. **RN-07 Onde as texturas ficam (híbrido):** o pacote da extensão leva só o **catálogo** e as **miniaturas** dos 12
   fabricantes (cerca de 25 MB). Assim, a grade de Texturas aparece completa logo depois de instalar, mesmo sem
   internet. As **imagens em tamanho real** (cerca de 576 MB) ficam no **servidor da CAF Mob** e são baixadas para a
   pasta do usuário da extensão (RN-12). O plugin só pode ser publicado na plataforma de extensões do Blender se não
   levar as imagens dos fabricantes, que não são conteúdo GPL. O titular declara ter o direito de distribuir essas
   imagens pelo servidor da CAF Mob (decisões de 2026-10-12). 🟢
   - Tipo: nova
11. **RN-11 Conta CAF Mob:** baixar imagens exige entrar com uma conta CAF Mob no plugin. O projetista entra uma vez;
    a sessão fica guardada na pasta do usuário da extensão e é renovada sem pedir a senha de novo, até ele sair ou a
    sessão expirar. A senha nunca é gravada em disco. Sem conta, o projetista vê a grade e as miniaturas, e o plugin
    pede o login quando ele tenta usar uma textura ainda não baixada. 🟢 (decisão do titular, 2026-10-12)
    - Tipo: nova
12. **RN-12 Quando as imagens são baixadas:** há dois modos.
    - **Sob demanda (padrão):** ao aplicar ou soltar uma textura cuja imagem ainda não está no computador, o plugin
      baixa só essa imagem, mostra o progresso e aplica a textura quando o download termina. A imagem fica guardada e
      não é baixada de novo.
    - **100% offline:** o projetista pode escolher baixar **todas** as imagens de uma vez (cerca de 576 MB), se a conta
      dele tiver permissão para isso. Depois disso, as texturas funcionam sem internet.
    O download continua de onde parou depois de uma queda, nunca deixa imagem pela metade no lugar da definitiva e
    pode ser cancelado. 🟢 (decisão do titular, 2026-10-12)
    - Tipo: nova
13. **RN-13 Sem internet:** quando o acesso à internet do Blender está desligado ou o servidor não responde, a grade
    continua mostrando o catálogo e as miniaturas. Texturas já baixadas funcionam normalmente; as outras aparecem
    marcadas como "não baixada" e, ao tentar usá-las, o plugin mostra um aviso claro, sem erro Python e sem travar a
    interface. 🟢
    - Tipo: nova
14. **RN-14 Contrato com o servidor:** esta feature define o contrato que o servidor da CAF Mob vai atender: login e
    renovação de sessão, catálogo com versão, endereço de cada imagem, permissão de "baixar tudo" e os erros. O
    endereço do servidor fica nas preferências do plugin. Enquanto o site não publica o serviço, o contrato pode ser
    atendido por um servidor provisório com o mesmo formato. 🟡 (decisão do titular, 2026-10-12)
    - Tipo: nova
8. **RN-08 Grade:** a Biblioteca CAFFMob mostra os itens de cada categoria em grade, cada célula com miniatura e nome:
   modelos prontos, módulos salvos, objetos e texturas. A miniatura da textura é a própria imagem reduzida; a do bloco
   é a miniatura que já é gerada ao salvar. 🟢
   - Origem no legado: `_reversa_sdd/library_panel/requirements.md#RN-15` (grade sem miniatura) e o Won't "Galeria com
     miniaturas" da 012
   - Tipo: alterada (pedido explícito do titular em 2026-10-12, que reabre a decisão D-15 da 012)
9. **RN-09 Minimizar, maximizar e fixar:** a biblioteca tem três estados:
   - **minimizada**: mostra só o rótulo "BIBLIOTECA CAFFMOB", como hoje;
   - **aberta**: a coluna de categorias atual;
   - **maximizada**: um retângulo maior, com a grade, as categorias (incluindo Texturas) e uma busca.
   O retângulo maximizado **flutua sobre a cena**, sem encolher a área da vista, e o projetista pode movê-lo e
   redimensioná-lo. Ele pode ser **fixado**: fixo, continua aberto enquanto o projetista mexe na cena; solto, fecha com
   Esc ou com um clique fora, como hoje (`_reversa_sdd/library_panel/requirements.md#RN-13`). Em nenhum estado o
   retângulo cobre informações importantes do plugin (HUD, botões de navegação, avisos e cotas de tela): ele se
   posiciona e se limita para não sobrepor essas áreas. O estado (minimizada, aberta, maximizada; fixo ou solto) vale
   para a sessão. 🟢 (decisão do titular, 2026-10-12)
   - Tipo: nova
10. **RN-10 Arrastar para a cena:** arrastar uma célula da grade para a cena e soltar:
    - um bloco (modelo pronto, módulo, objeto) é inserido no ponto sob o mouse, com as mesmas regras de encaixe e
      posicionamento da inserção atual;
    - uma textura é aplicada ao alvo sob o mouse (RN-05);
    - soltar fora de qualquer alvo válido não muda nada e mostra um aviso curto;
    - Esc durante o arraste cancela.
    Cada soltura é uma etapa só de desfazer. 🟡
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Gerar, a partir da pasta do titular, o catálogo e as miniaturas que vão no pacote e o conjunto de imagens que vai para o servidor (RN-01, RN-07) | Must | Numa instalação nova, sem internet, Texturas mostra os 12 fabricantes com as 1.209 miniaturas, e nenhum fabricante de fora de RN-01 aparece; o pacote não contém nenhuma imagem em tamanho real | 🟢 |
| RF-02 | Organizar as texturas por fabricante e coleção, com o nome legível (RN-02) | Must | "fabrica/duratex/Design/Carvalho_Avela_Design.jpg" aparece como "Carvalho Avela Design" em Duratex › Design | 🟢 |
| RF-03 | Filtrar o que não é textura e avisar arquivo ruim sem parar (RN-03) | Must | Nenhum `.bump` vira célula; um JPG corrompido gera um aviso com o caminho e os demais carregam | 🟢 |
| RF-04 | Mostrar a área Texturas em grade com miniatura, filtro por fabricante e coleção e busca por nome (RN-08) | Must | Buscar "carvalho" mostra só as texturas com "carvalho" no nome, de todos os fabricantes | 🟡 |
| RF-05 | Aplicar a textura escolhida à peça, à frente, ao grupo ou ao objeto selecionado, na escala real (RN-04, RN-05) | Must | Uma textura de chapa inteira (2.750 × 1.850 px) numa porta de 700 mm mostra o padrão na proporção da chapa real; trocar o tamanho para 1.200 mm muda a escala aparente | 🟡 |
| RF-06 | Ajustar o tamanho real de uma textura (RN-04) | Should | Mudar o tamanho de 600 para 300 mm dobra a repetição aparente na peça | 🟡 |
| RF-07 | Respeitar o sentido do veio da peça (RN-06) | Should | Uma lateral e um tampo do mesmo armário mostram o veio no sentido do comprimento de cada peça | 🟡 |
| RF-08 | Mostrar todas as categorias da biblioteca em grade com miniatura (RN-08) | Must | A categoria Cozinha mostra os modelos prontos e os módulos salvos como células com imagem e nome | 🟡 |
| RF-09 | Maximizar a biblioteca num retângulo maior (RN-09) | Must | Maximizada, a grade mostra pelo menos 4 colunas numa tela de 1.920 px de largura | 🟡 |
| RF-10 | Fixar e soltar o retângulo maximizado (RN-09) | Must | Fixo, ele continua aberto depois de clicar na cena e girar a vista; solto, fecha com Esc ou clique fora | 🟢 |
| RF-15 | Minimizar a biblioteca ao rótulo "BIBLIOTECA CAFFMOB" e mover ou redimensionar o retângulo maximizado (RN-09) | Must | Minimizada, só o rótulo aparece; maximizada, arrastar a borda muda o tamanho e arrastar o topo muda o lugar | 🟢 |
| RF-16 | Não sobrepor o HUD, os botões de navegação, os avisos e as cotas de tela do plugin (RN-09) | Must | Com o HUD ligado, nenhum botão do HUD fica coberto pelo retângulo em nenhum estado nem posição | 🟡 |
| RF-17 | Entrar e sair com a conta CAF Mob no plugin (RN-11) | Must | Depois de entrar, fechar e abrir o Blender não pede a senha de novo; nenhum arquivo da pasta do usuário contém a senha | 🟢 |
| RF-18 | Baixar sob demanda a imagem da textura usada, com progresso e cancelamento (RN-12) | Must | Soltar uma textura não baixada numa peça mostra o progresso e aplica a textura ao terminar; a segunda vez não baixa de novo | 🟢 |
| RF-19 | Baixar todas as imagens para uso 100% offline, quando a conta tiver permissão (RN-12) | Must | Com permissão, "Baixar tudo" deixa as 1.209 imagens no computador e, com a internet desligada, qualquer textura é aplicada; sem permissão, a opção aparece indisponível com o motivo | 🟢 |
| RF-20 | Funcionar sem internet com o que já foi baixado e avisar o resto (RN-13) | Must | Com o acesso à internet do Blender desligado, a grade abre, as baixadas funcionam e uma não baixada mostra o aviso, sem erro | 🟢 |
| RF-21 | Retomar um download interrompido sem deixar imagem pela metade (RN-12) | Should | Cortar a rede no meio de um download e religar: o download continua e o arquivo final confere com o tamanho do servidor | 🟡 |
| RF-22 | Endereço do servidor configurável nas preferências (RN-14) | Must | Trocar o endereço nas preferências faz o catálogo e os downloads seguirem o novo servidor | 🟡 |
| RF-11 | Arrastar um bloco da grade para a cena (RN-10) | Must | Arrastar "Balcão 2 portas" e soltar no piso insere o armário naquele ponto; Ctrl+Z remove de uma vez | 🟡 |
| RF-12 | Arrastar uma textura da grade até uma peça (RN-10, RN-05) | Must | Soltar "Carvalho Avela Design" sobre a frente do balcão aplica a textura só naquela frente | 🟡 |
| RF-13 | Soltar no vazio ou cancelar o arraste sem efeito (RN-10) | Must | Soltar uma textura no céu da vista não muda nenhum material e mostra o aviso; Esc durante o arraste não insere nada | 🟡 |
| RF-14 | Associar o mapa de relevo da textura, quando existir, ao material (RN-03) | Could | Uma textura da Formica com `.bump` correspondente ganha relevo no modo de vista com textura | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Depois da primeira indexação, abrir Texturas com as 1.209 texturas leva menos de 1 s; as miniaturas carregam sob demanda e a listagem não relê o disco a cada redesenho | O legado relê pastas e manifestos a cada redesenho (`_reversa_sdd/object_library/requirements.md`, RNF de desempenho); princípio IX (`.reversa/principles.md`) | 🟡 |
| Desempenho | Miniaturas de no máximo 256 px, geradas uma vez e reaproveitadas (no pacote ou em cache na pasta do usuário), para não carregar imagens de até 2.750 px na grade | Imagens medidas na pasta do titular (365 a 2.750 px) | 🟡 |
| Tamanho do pacote | O pacote cresce no máximo cerca de 25 MB (catálogo e miniaturas) e continua dentro do limite da plataforma de extensões do Blender (cerca de 200 MB, número levantado em 2026-10-12, sem documento oficial) | RN-07; levantamento de 2026-10-12 | 🟡 |
| Segurança | Comunicação com o servidor só por HTTPS; a senha nunca é gravada; a sessão fica na pasta do usuário da extensão com acesso restrito ao usuário; nenhum segredo vai para o arquivo do projeto nem para os logs | RN-11 | 🟢 |
| Rede | O plugin declara a permissão de rede no manifesto e não faz nenhum acesso quando o acesso à internet do Blender está desligado (`bpy.app.online_access`); downloads nunca travam a interface | RN-13; `docs/rag/blender-api/corpus/bpy.app.md#bpy.app.online_access` | 🟢 |
| Usabilidade | Telas limpas: a grade mostra imagem e nome; termos internos não aparecem. A direção visual da grade e do retângulo maximizado é definida com o fluxo `/impeccable` antes do plano | Princípio I (`.reversa/principles.md`); pedido do titular | 🟢 |
| Usabilidade | Textos de tela em português, traduzíveis | Regra do repositório (`CLAUDE.md`, "Textos de UI") | 🟢 |
| Robustez | Pasta ausente, fabricante vazio ou imagem ilegível viram aviso claro, nunca erro Python | Princípio VIII (`.reversa/principles.md`) | 🟢 |
| Portabilidade | O projeto salvo continua mostrando as texturas em outro computador que tenha o plugin instalado, e a regra de empacotar a imagem ao salvar item segue valendo | `_reversa_sdd/questions.md#pergunta-60` | 🟡 |
| Licença | Nenhuma imagem em tamanho real dos fabricantes entra no pacote; elas são servidas pelo servidor da CAF Mob, sob a declaração de direito de distribuição do titular (RN-07) | Decisão do titular, 2026-10-12; plataforma de extensões só aceita conteúdo GPL | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Catálogo e miniaturas já vêm no plugin
  Dado uma instalação nova do plugin, sem internet
  Quando o projetista abre a área Texturas da biblioteca
  Então aparecem os 12 fabricantes de chapas de RN-01 organizados por coleção, com miniaturas
  E nenhum fabricante de eletrodoméstico, vidro ou puxador aparece

Cenário: Baixar sob demanda ao usar a textura
  Dado o projetista com a conta CAF Mob conectada e uma textura ainda não baixada
  Quando ele solta a textura sobre uma frente de balcão
  Então o plugin mostra o progresso do download
  E aplica a textura na frente quando o download termina

Cenário: Usar uma textura sem estar conectado
  Dado o projetista sem a conta CAF Mob conectada
  Quando ele tenta aplicar uma textura ainda não baixada
  Então o plugin pede para entrar com a conta
  E nenhum material muda

Cenário: Baixar tudo para uso offline
  Dado uma conta CAF Mob com permissão para baixar tudo
  Quando o projetista escolhe usar as texturas 100% offline
  Então as 1.209 imagens ficam no computador
  E, com a internet desligada, qualquer textura é aplicada

Cenário: Sem internet
  Dado o acesso à internet do Blender desligado
  Quando o projetista aplica uma textura não baixada
  Então aparece um aviso claro
  E a interface continua respondendo

Cenário: Arquivo de textura corrompido
  Dado um fabricante com um JPG ilegível
  Quando o catálogo é carregado
  Então aparece um aviso com o caminho do arquivo
  E as demais texturas do fabricante aparecem normalmente

Cenário: Buscar e aplicar uma textura
  Dado a biblioteca aberta em Texturas e uma frente de balcão selecionada
  Quando o projetista busca "carvalho" e escolhe "Carvalho Avela Design"
  Então a frente mostra a textura em escala real
  E as outras peças do balcão não mudam

Cenário: Biblioteca em grade com miniaturas
  Dado a categoria Cozinha com modelos prontos e módulos salvos
  Quando o projetista abre a categoria
  Então cada item aparece como célula com miniatura e nome

Cenário: Maximizar e fixar a biblioteca
  Dado a biblioteca maximizada e fixada
  Quando o projetista clica na cena e gira a vista
  Então o retângulo da biblioteca continua aberto

Cenário: Minimizar sem cobrir o plugin
  Dado a biblioteca maximizada e o HUD ligado
  Quando o projetista minimiza a biblioteca
  Então só o rótulo "BIBLIOTECA CAFFMOB" aparece
  E nenhum botão do HUD fica coberto

Cenário: Arrastar um bloco para a cena
  Dado a biblioteca maximizada em Cozinha
  Quando o projetista arrasta "Balcão 2 portas" e solta sobre o piso
  Então o balcão é inserido no ponto sob o mouse
  E um Ctrl+Z remove o balcão de uma vez

Cenário: Arrastar uma textura até uma peça
  Dado a biblioteca maximizada em Texturas
  Quando o projetista arrasta uma textura e solta sobre a lateral de um armário
  Então só a lateral recebe a textura, com o veio no sentido do comprimento

Cenário: Soltar a textura no vazio
  Dado uma textura sendo arrastada
  Quando o projetista solta sobre uma área sem objeto
  Então nenhum material muda
  E aparece um aviso curto

Cenário: Cancelar o arraste
  Dado um bloco sendo arrastado sobre a cena
  Quando o projetista aperta Esc
  Então nada é inserido
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | Sem o catálogo importado e organizado não existe a área Texturas |
| RF-04, RF-05 | Must | Escolher e aplicar o acabamento real é o objetivo da primeira parte do pedido |
| RF-08, RF-09, RF-10, RF-15, RF-16 | Must | Grade, minimizar, maximizar, fixar e não cobrir o plugin são pedidos explícitos do titular |
| RF-11, RF-12, RF-13 | Must | Arrastar para a cena é pedido explícito; o caso negativo protege a cena |
| RF-17, RF-18, RF-19, RF-20, RF-22 | Must | Sem conta, download e modo offline as texturas híbridas não funcionam |
| RF-21 | Should | Retomar o download protege conexões instáveis, mas o download do zero ainda atende |
| RF-06, RF-07 | Should | Escala ajustável e veio elevam o realismo, mas a textura já serve com o padrão |
| RF-14 | Could | Só parte das texturas tem relevo (Eucatex 19, Formica 24) |
| RNF de desempenho | Should | Com 1.209 texturas, ler tudo a cada redesenho trava a viewport (princípio IX) |
| Galeria das texturas de `padroes/` (diversos, tapetes, pessoas…) | Won't (nesta versão) | Fora do pedido: só fabricantes de móveis planejados |

## 9. Esclarecimentos

### Sessão 2026-10-12

- **Q:** Além dos 12 fabricantes de chapas claros, o que mais entra em Texturas?
  **R:** Só os 12 (Arauco, Berneck, Duratex, Eucatex, Fibraplac, Floraplac, Formica, Greenplac, Guararapes, Lopar,
  Placas do Brasil e Sudati). Atualizado em RN-01.
- **Q:** As texturas vão dentro do pacote da extensão ou só para a biblioteca local do usuário?
  **R:** Dentro do pacote. Atualizado em RN-07, RF-01, no cenário de instalação e nos RNF de tamanho do pacote e
  licença.
- **Q:** Fixada, a biblioteca maximizada ocupa uma faixa própria da tela ou flutua sobre a cena?
  **R:** Flutua sobre a cena, com a opção de deixar minimizada mostrando só o nome "BIBLIOTECA CAFFMOB", como a atual,
  e com a ressalva de não sobrepor informações importantes do plugin. Atualizado em RN-09, RF-15, RF-16 e num cenário
  novo.
- **Q:** Qual o tamanho real padrão de uma textura que não tem tamanho de chapa inteira?
  **R:** 600 mm no maior lado, ajustável por textura. Confirmado em RN-04.

### Sessão 2026-10-12 (2): armazenamento online

- **Q:** Onde ficam as texturas, sabendo que a plataforma de extensões do Blender não aceita o pacote de ~600 MB nem
  conteúdo não GPL?
  **R:** Híbrido: catálogo e miniaturas no pacote; imagens em tamanho real no servidor da CAF Mob, baixadas quando
  usadas. Substitui a resposta anterior ("dentro do pacote"). Atualizado em RN-07, RF-01, no cenário de instalação e
  nos RNF de tamanho do pacote e licença.
- **Q:** Em que estado está o site da CAF Mob para servir as texturas?
  **R:** Esta feature define o contrato; o endereço do servidor fica configurável. Nova RN-14 e RF-22.
- **Q:** Quem pode baixar as texturas?
  **R:** Quem entra com uma conta CAF Mob. Nova RN-11, RF-17 e RNF de segurança.
- **Q:** Quando as imagens grandes são baixadas?
  **R:** Ao usar a textura, com a opção de usar as texturas 100% offline baixando tudo do servidor, quando a conta
  tiver permissão. Novas RN-12 e RN-13, RF-18 a RF-21 e RNF de rede.

## 10. Lacunas

- Nenhuma lacuna aberta. Pontos de atenção para o plano (não são dúvidas):
  - o formato do login da conta CAF Mob (por exemplo, código de autorização aberto no navegador ou usuário e senha
    no plugin) é decisão técnica do contrato de RN-14;
  - onde as imagens originais ficam no repositório e como chegam ao servidor (o pacote leva só catálogo e
    miniaturas).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-12 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-12 | Sessão de esclarecimentos: 4 respostas integradas (RN-01, RN-04, RN-07, RN-09; RF-15 e RF-16 novos) | reversa-clarify |
| 2026-10-12 | Segunda sessão: armazenamento híbrido com servidor CAF Mob (RN-07 reescrita; RN-11 a RN-14 e RF-17 a RF-22 novos) | reversa-clarify |
