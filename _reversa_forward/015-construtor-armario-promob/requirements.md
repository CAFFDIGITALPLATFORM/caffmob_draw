# Requirements: Construtor de armário CAFF MOBI com a arquitetura do Promob

> Identificador: `015-construtor-armario-promob`
> Data: `2026-10-14`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular com algoritmo obrigatório. Os vídeos capturam a estrutura do Construtor de Armários do
> Promob; as legendas e os prints viram descrições técnicas, e as descrições viram elicitação para cozinha,
> dormitórios, salas, escritórios e outros ambientes, com o design CAFF MOBI.
> Evidência em `inputs/` (índice em `inputs/README.md`):
> - 24 vídeos (2 de render fora do escopo);
> - 23 legendas;
> - 192 prints;
> - 3 cadernos de notas.
>
> Citação dos vídeos: `<id> [mm:ss]`. Citação dos prints: `prints/<arquivo>`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o módulo CAFF MOBI tem três tipos (Balcão, Aéreo, Torre), mas a função que monta a caixa não recebe o tipo. Todo
tipo sai com as mesmas peças: laterais, base, tampo, fundo e prateleiras. Só as medidas mudam.

No Construtor de Armários do Promob, o projetista começa escolhendo uma **estrutura de caixa** numa galeria por
ambiente. Cada estrutura traz a sua lista de peças:
- o balcão tem sarrafos no lugar do tampo;
- o roupeiro tem base superior e rodapé;
- a torre tem laterais do piso ao topo.

Esta feature leva essa arquitetura por tipo ao CAFF MOBI, com o editor de 7 abas da 008, para cozinha, dormitórios,
salas, escritórios e outros ambientes, no visual CAFF MOBI.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#1.1 Entidades do Ambiente 3D` | Módulo = armário paramétrico de chapas MDF/MDP | 🟢 |
| `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` | Toda peça de chapa entra no plano de corte | 🟢 |
| `_reversa_sdd/domain.md#standards` (RN-STANDARDS-12, RN-STANDARDS-13) | Medidas padrão por linha e tipo (BASE, WALL, TALL); tipo inválido vira BASE; o fundo usa o mesmo papel em todos os tipos | 🟢 |
| `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-12, -15, -18, -20) | N vãos = N−1 divisórias de largura igual; pés e rodapés abaixo da caixa sem levantar o módulo; deslizantes dentro do vão com sobreposição de 30 mm; montagem LATERAL ou BASE | 🟢 |
| `_reversa_sdd/data-dictionary.md` (`cabinet_type`) | Enum do tipo do módulo | 🟢 |
| `_reversa_sdd/frameless/design.md#Tipos` e `#F3. Carcaça do inferior` | A biblioteca frameless já monta uma carcaça por tipo: o inferior com rodapé e travessas, o alto com rodapé e tampo inteiro, o aéreo sem rodapé | 🟢 |
| `_reversa_sdd/face_frame/design.md#Solver` | Rodapé e travessas decididos pelo tipo (regra FACE_FRAME-R02) | 🟢 |
| `_reversa_sdd/cabinet_editor/design.md#F-09 structure.layout` | Montagem da caixa calculada pela estrutura, sem o tipo | 🟢 |
| `_reversa_forward/008-editor-armario-construtor/requirements.md#4` | Editor com as 7 abas do Construtor; o tipo aparece só como rótulo (RN-08); extras na árvore (RN-07a) | 🟢 |
| `_reversa_forward/012-biblioteca-caffmob-chapas/` | Padrão de Dimensões com linha (COZ, DOR, BAN, SAL, ESC) e montagem do módulo CAFF MOBI | 🟢 |
| Código (levantamento de 2026-10-14): `caffmob_draw/geometry/mesh_gen.py:246` | `generate_cabinet_mesh` não recebe o tipo e monta sempre as mesmas 5 chapas e as prateleiras | 🟢 |
| Código: `caffmob_draw/cutting/part_sources.py:217` | `synthetic_records` deduz as peças do corte sem olhar o tipo | 🟢 |
| Código: `caffmob_draw/data/library_models.json` | Biblioteca CAFF MOBI: 5 modelos (balcão 1p/2p, aéreo 1p/2p, torre) | 🟢 |
| `inputs/notas-grupo-a.md#2`, `inputs/notas-grupo-b.md#2`, `inputs/notas-grupo-c.md#2` | Arquitetura por tipo no Promob (seções 4 a 7 abaixo) | 🟢 visto / 🟡 inferido |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de cozinha vindo do Promob | Montar balcão, aéreo e torre com a construção real de cada um | Abre o construtor, escolhe "Cozinhas › Inferior c/ Divisória" e vê o balcão com sarrafo frontal e traseiro, sem tampo, pronto para o tampo de pedra |
| Projetista de dormitório | Roupeiro de 3 vãos com maleiro, cabideiro, gavetas internas e portas de correr | Escolhe "Dormitórios › Armário", 3 vãos, 2600 × 2500 × 600, divide os vãos e insere as portas de correr sobre a caixa inteira |
| Projetista de sala e escritório | Rack, painel, armário baixo e gaveteiro | Escolhe "Salas › Portas Externas c/ Rod" ou "Escritórios › Gaveteiro volante" |
| Marceneiro (produção) | Plano de corte com as peças reais | O plano de corte do balcão lista "Sarrafo Frontal" e "Sarrafo Traseiro", e não "Base Superior" |

## 4. Regras de negócio novas ou alteradas

**Glossário desta feature.**
- *Estrutura de caixa* (ou *tipo de estrutura*): a receita de um tipo de armário, isto é, as peças que ele tem, como
  se encontram, quais componentes opcionais vêm marcados e as medidas padrão. Ex.: "Inferior c/ Divisória".
- *Ambiente*: a categoria da galeria (Cozinhas, Dormitórios, Salas, Escritórios, Outros). Corresponde à *linha* do
  Padrão de Dimensões (COZ, DOR, SAL, ESC, BAN).
- *Sarrafo*: tira de chapa no alto do balcão que trava as laterais no lugar do tampo; há o frontal e o traseiro.
- *Rodapé*: chapa vertical sob a caixa, recuada da frente, que apoia o armário no piso.
- *Vão*: espaço interno entre duas peças verticais; o construtor divide a caixa em N vãos.
- *Conjunto deslizante*: portas de correr com trilhos, laterais batente e fechamentos, montadas sobre a caixa inteira.

**A. Arquitetura por tipo**

1. **RN-01:** O tipo de estrutura **define as peças** do armário, não só as medidas. Duas estruturas com as mesmas
   medidas geram conjuntos de peças diferentes na cena e no plano de corte. 🟢
   (`Or7qXPijqLA [0:49]`, `prints/Or7qXPijqLA-0049-construtor-tipos-de-estrutura.jpg`; Configurador com "Montagem da
   Caixa" separada para Inferior, Superior e Despenseiro: `prints/jtEjP6DrzpM-0025-configurador-dimensoes-arvore.jpg`)
   - Origem no legado: `_reversa_sdd/domain.md#standards` (RN-STANDARDS-13); `_reversa_sdd/cabinet_editor/design.md#F-09 structure.layout`
   - Tipo: alterada
2. **RN-02:** As estruturas ficam num **catálogo de dados** (nome, ambiente, miniatura, peças, componentes opcionais
   com o estado inicial, medidas padrão e regra de encontro), e não no código. O projeto pode acrescentar estruturas
   sem mudar o código. 🟡 (princípio III, "Nada pregado")
   - Tipo: nova
3. **RN-03:** Catálogo inicial de estruturas por ambiente. As peças vêm das telas do Promob; o que só apareceu como
   nome no catálogo está marcado 🟡:

   | Ambiente | Estrutura | Peças marcadas por padrão | Opcionais desmarcados | Medidas padrão (largura × altura × profundidade, mm) | Conf. |
   |---|---|---|---|---|---|
   | Cozinhas | Inferior c/ Divisória | Laterais, Divisória, Base Inferior, Sarrafo Frontal, Sarrafo Traseiro | Laterais Engrossuradas, Tampo Linear, Pés Plásticos 150, Rodapés, Rodapés Granito, Fechamentos 50, Vistas 150, Sarrafo Inteiro | 500 × 700 × 550, 1 vão | 🟢 (`prints/L6TMT6wV-xs-0040-inferior-c-divisoria-sarrafos-15mm.jpg`, `prints/JCsFoDBSoME-0314-estrutura-padrao-500x700x550-15mm.jpg`) |
   | Cozinhas | Inferior c/ Divisória e Rod | a anterior + Rodapé | idem | idem | 🟡 (só o nome) |
   | Cozinhas | Inferior c/ Divisória até Piso / até Piso e Rod | laterais descem até o piso; base entre as laterais | idem | idem | 🟡 |
   | Cozinhas | Inferior c/ 2 Laterais até Piso / e Rod | sem divisória de vão inteiro; laterais até o piso | idem | idem | 🟡 |
   | Cozinhas | Gaveteiro / Gaveteiro c/ Rodapé | Laterais, Base Inferior, Sarrafo Frontal; vão único para gavetas | idem | 400 × 700 × 560 | 🟡 (`prints/Ask6ahTwQrU-0049-catalogo-cozinha-inferiores.jpg`) |
   | Cozinhas | Superior c/ Divisória / Superior c/ 2 Laterais | Laterais, Divisória, Base Inferior, Base Superior inteiras; sem rodapé, pés e sarrafos | Fechamentos, Vistas | 800 × 950 × 320, instalado a Z 1650 | 🟡 (tela não aberta; medidas da biblioteca: `prints/KQs4HQ6f5Sg-0346*`) |
   | Cozinhas | Torre p/ Eletros / c/ Rod | Laterais do piso ao topo, Base Inferior, Base Superior; prateleira fixa "Não Divide o Fundo" | Rodapé, Pés 150, Fechamentos 50, Vista 150 | 500 × 2400 × 550 (vão de 2363 em 2400) | 🟡 (`wsdaKZtjszg [2:00]–[4:34]`) |
   | Cozinhas | Inferior / Superior Canto Reto Esq e Dir | canto em L reto | — | — | 🔴 (só o nome) |
   | Dormitórios | Armário | Lateral Esq 18, Lateral Dir 18, Divisórias, Base Inferior 18, Base Superior 18, Rodapés | Rodízios, Vistas (auto), Vistas 150, Fechamentos 50 | 1000 × 2500 × 550, 1 vão | 🟢 (`prints/-nGTqK7rTto-0122-aba-estrutura-componentes.jpg`, `prints/S_PZG9jKKrI-0612-estrutura-3vaos-3000x2600-componentes.jpg`) |
   | Dormitórios | Armário s/ Lat Esq / s/ Lat Dir / s/ Laterais | o Armário sem a(s) lateral(is), para compartilhar a lateral do vizinho | idem | idem | 🟡 (`prints/S_PZG9jKKrI-0457-tipos-estrutura-dormitorios.jpg`) |
   | Dormitórios | Armário Divisória sobre Base | Laterais, Base Superior, Rodapés; divisórias apoiadas na base; sem Base Inferior na lista | Vistas, Fechamentos | 1000 × 2500 × 600 | 🟢 (`prints/tXesiUUeDwg-0045-estrutura-divisoria-sobre-base.jpg`) |
   | Dormitórios | Superior (maleiro) e Bancada | caixa aérea de dormitório e bancada baixa | — | — | 🔴 (só o nome) |
   | Salas | Portas Externas s/ Rod / c/ Rod | Lateral Esq/Dir 18, Divisória, Base Inferior 18, Base Superior 18 | Pés 50, Rodízios 100, Rodapés | 1500 × 700 × 550 | 🟢 (`prints/q2aCXTWVrsA-0051-estrutura-componentes-base-superior.jpg`) |
   | Salas | Portas Embutidas s/ Rod / c/ Rod | igual às Externas; a porta fica dentro do vão | idem | idem | 🟡 |
   | Salas | Estrutura p/ Painel | estrutura de fixação do painel de TV | — | — | 🔴 (só o nome) |
   | Escritórios | Armário baixo, Armário alto, Gaveteiro volante, Estante | derivadas de Salas e Dormitórios: base superior inteira (o tampo faz parte do móvel), gaveteiro com Rodízios marcados, estante sem portas | — | a definir no Padrão de Dimensões da linha ESC | 🟡 (os vídeos não mostram escritório) |
   | Outros (banheiro, lavanderia, área de serviço) | Gabinete, Espelheira, Torre de serviço | reaproveitam Inferior, Superior e Torre com as medidas da linha BAN ou da linha do ambiente | — | a definir no Padrão de Dimensões | 🟡 |

   As estruturas de Salas, Escritórios e Outros ficam registradas aqui, mas são implementadas numa feature seguinte
   (clarify Q1).

   - Tipo: nova
4. **RN-04:** O **balcão de cozinha não tem tampo de chapa**: o alto da caixa é aberto, travado por Sarrafo Frontal e
   Sarrafo Traseiro, porque o tampo (pedra ou MDF) é peça à parte. "Tampo Linear" e "Sarrafo Inteiro" são opcionais
   desmarcados. A largura do sarrafo vem do Padrão de Dimensões (padrão 100 mm, editável; clarify Q5). A posição do sarrafo traseiro (horizontal ou
   vertical) também vem do padrão. 🟢 (peças e 3D: `prints/L6TMT6wV-xs-0336-balcao-3d-aberto-sarrafos.jpg`,
   `Y8vvtVJUH-0 [5:54]`; posição: `prints/jtEjP6DrzpM-0041-configurador-lista-configuracoes.jpg`); 🟡 (largura do
   sarrafo: não lida em nenhuma tela)
   - Tipo: nova
5. **RN-05:** Uma estrutura **"c/ Rod"** ou com Rodapés marcados apoia a caixa sobre o rodapé, e a **altura total
   informada inclui o rodapé**: a altura interna é a altura − base inferior − base superior (ou sarrafo) − rodapé. A
   altura do rodapé e o recuo frontal dele vêm do Padrão de Dimensões (padrão 100 mm de altura e 50 mm de recuo,
   editáveis; clarify Q5). 🟢 (armário 2500 com vão interno 2384:
   `prints/-nGTqK7rTto-0122-aba-estrutura-componentes.jpg`); 🟡 (rodapé de 80 mm calculado, não lido)
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-15: pés e rodapés ficam abaixo da
     caixa sem levantar o módulo)
   - Tipo: alterada (com rodapé da estrutura, a caixa sobe e a altura total fica igual; pés e rodízios avulsos da 008
     continuam abaixo da caixa)
6. **RN-06:** Nas estruturas **"até Piso"** as laterais descem até o piso e a base inferior fica entre elas, na altura
   do rodapé. 🟡 (só o nome; `prints/Or7qXPijqLA-0049-construtor-tipos-de-estrutura.jpg`)
   - Tipo: nova
7. **RN-07:** A **regra de encontro** da estrutura (Sobrepõe Base ou Sobrepõe Lateral, com ou sem rodapé) usa as duas
   montagens que já existem: Sobrepõe Lateral é LATERAL e Sobrepõe Base é BASE. A estrutura traz a regra padrão, e o
   Padrão de Dimensões da linha pode mudá-la. 🟢 (nomes: `prints/QcqJlr6WZW0-0026-tipos-de-estrutura-2011.jpg`,
   `prints/4QEl92sAUoE-0122-tipo-estrutura-sobrepoe.jpg`); 🟡 (equivalência com LATERAL e BASE)
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-20)
   - Tipo: alterada
8. **RN-08:** O Padrão de Dimensões ganha a **montagem por grupo de estrutura**, separada para Inferior, Superior e
   Despenseiro/Torre. Cada grupo tem:
   - o tipo de fundo: encaixado, pregado, rebaixado ou com travessas;
   - a posição do sarrafo traseiro;
   - a largura do sarrafo;
   - a altura e o recuo do rodapé;
   - as espessuras.

   Mudar o padrão e reaplicá-lo atualiza os módulos que seguem o padrão (mecanismo da 012). 🟢 (Configurador:
   `prints/jtEjP6DrzpM-0025-configurador-dimensoes-arvore.jpg`, configuração nomeada "COZ - MDF 18 - Fundo encaixado -
   Sarrafo tras horizontal" em `prints/jtEjP6DrzpM-0041-configurador-lista-configuracoes.jpg`)
   - Origem no legado: `_reversa_sdd/domain.md#standards` (RN-STANDARDS-12: o fundo usa o mesmo papel em todos os tipos)
   - Tipo: alterada
9. **RN-09:** As **espessuras** (15, 18 ou 18,5 mm) são dado da estrutura e do padrão, nunca constante do código. 🟢
   (15: `L6TMT6wV-xs [0:40]`; 18: `-nGTqK7rTto [2:02]`; 18,5: `prints/hPtAAtOKeDU-0045-estrutura-2700-rodape-vista-18-5.jpg`)
   - Tipo: alterada
10. **RN-10:** O **plano de corte** lista as peças reais da estrutura, com o nome do papel da peça (Lateral, Divisória,
    Base Inferior, Base Superior, Sarrafo Frontal, Sarrafo Traseiro, Rodapé, Fundo, Prateleira). O nome define a fita
    de borda e a etiqueta. Estrutura sem base superior não gera "Base Superior" no corte. 🟢 (`Or7qXPijqLA [4:49]–[5:17]`)
    - Origem no legado: `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)`
    - Tipo: alterada

**B. Fluxo do construtor**

11. **RN-11:** **Novo armário pelo construtor**: a primeira tela pede "Selecione uma estrutura de caixa para iniciar
    a construção" numa galeria com uma aba por ambiente e uma miniatura por estrutura, com OK e Cancelar. O OK abre
    o editor de 7 abas da 008 já com a estrutura escolhida e as medidas padrão dela. 🟢
    (`prints/Or7qXPijqLA-0049-construtor-tipos-de-estrutura.jpg`, `prints/-nGTqK7rTto-0050-catalogo-abas-dormitorios.jpg`)
    - Tipo: nova
12. **RN-12:** O cabeçalho da aba Estrutura mostra **"Tipo: <nome da estrutura>"**. Os componentes da árvore são os da
    estrutura, com o estado inicial dela. Reabrir o editor num armário pronto mostra a mesma estrutura. 🟢
    (`prints/L6TMT6wV-xs-0040-inferior-c-divisoria-sarrafos-15mm.jpg`; reabrir: `QcqJlr6WZW0 [2:01]`)
    - Origem no legado: `_reversa_forward/008-editor-armario-construtor/requirements.md#4` (RN-08)
    - Tipo: alterada
13. **RN-13:** Os **modelos da biblioteca CAFF MOBI** (balcão 1p/2p, aéreo 1p/2p, torre) passam a apontar para uma
    estrutura. Inserir "Balcão 2 portas" cria um "Inferior c/ Divisória" de 800 com duas portas. 🟡
    - Tipo: alterada
14. **RN-14:** **Vãos**: largura do vão = (Largura total − (N + 1) × espessura) / N, com vãos iguais ao mudar o Número
    de vãos. A largura de um vão pode ser digitada, e os vizinhos absorvem a diferença. 🟢 (a fórmula confere em 6
    casos, ex. 3000, 3 vãos, 18 mm → 976: `S_PZG9jKKrI [06:12]`; edição: `L6TMT6wV-xs [1:03]–[1:13]`)
    - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-12)
    - Tipo: alterada (digitar a largura de um vão)

**C. Divisões e internos por ambiente**

15. **RN-15:** O catálogo da aba Divisões mostra as variantes do **ambiente da estrutura**:
    - Cozinhas: divisória "Corta Sar" (corta o sarrafo) e "c/ Reb" (com rebaixo para o fundo), com ou sem recuo
      frontal e traseiro;
    - Dormitórios: Montante, prateleira Corrediça, Aramada e **Invisível**. A Invisível divide o vão, não aparece no
      3D e não entra no corte;
    - Torre: prateleira fixa "Não Divide o Fundo".

    "Somente Divisão" divide o vão sem gerar peça. Prateleiras e divisórias fixas têm a profundidade da caixa; as
    móveis têm o recuo do padrão (20 mm, editável; clarify Q5). 🟢 (nomes: `Y8vvtVJUH-0 [3:14]`, `JCsFoDBSoME [4:09]`,
    `prints/S4lHuaVA8LQ-0128-prateleiras-fixas-tipos.jpg`, `wsdaKZtjszg [2:00]`); 🟡 (comportamento de Corta Sar e
    c/ Reb)
    - Origem no legado: `_reversa_forward/008-editor-armario-construtor/requirements.md#4` (RN-10, RN-10a)
    - Tipo: alterada
16. **RN-16:** A aba Internos ganha os **internos de dormitório**, inseridos no vão alvo:
    - Cabideiros: Cabideiro 01, Cabideiro 02, Cab Extensível, Tubo, Tubo s/ Reforço. O tubo fica abaixo da prateleira
      de cima a uma distância do padrão (70 mm, editável; clarify Q5);
    - Calceiros: Madeira Esquerdo, Central e Direito; Aramado Esquerdo e Direito;
    - Sapateiras;
    - Porta Cintos/Gravatas.

    O tubo, o calceiro aramado e o porta-cintos são ferragens (lista de ferragens da 008); o calceiro de madeira e a
    sapateira de chapa entram no corte. 🟢 (itens: `S_PZG9jKKrI [09:16]`, `tXesiUUeDwg [02:20]`); 🟡 (distância do
    tubo: 25 a 70 mm nas fontes)
    - Origem no legado: `_reversa_forward/008-editor-armario-construtor/requirements.md#4` (RN-13a, RN-16)
    - Tipo: alterada
17. **RN-17:** A aba Gavetas de dormitório tem Internas, **Interna p/ trilho** (a gaveta de baixo mais alta, para
    passar o trilho da porta de correr), Sapateiras, Prateleira Corrediça e Externas, além dos afastadores Frontal e
    Traseiro, esquerdo e direito. 🟢 (`prints/tXesiUUeDwg-0245-gavetas-tipos-cf.jpg`, `hPtAAtOKeDU [03:05]`)
    - Tipo: nova
18. **RN-18:** A **caixa da gaveta** é calculada pelas folgas do Padrão de Dimensões:
    - Folga Corrediça: 13 mm; 5 mm com corrediça invisível;
    - Folga até Fundo da Caixa: 30 mm;
    - folgas superior e inferior da contra-frente, da lateral e da posterior: 20 mm cada.

    A caixa tem Lateral, Contra Frente, Posterior e Fundo de 6 mm. O fundo pode ser encaixado em canal (avanço de 5)
    ou pregado por baixo (avanço de 18 na frente e na traseira). As peças da caixa entram no corte. 🟢
    (`prints/jtEjP6DrzpM-0107-gavetas-folgas-padrao.jpg`, `jtEjP6DrzpM [3:38]`, `[5:46]`)
    - Tipo: nova

**D. Portas de correr como conjunto**

19. **RN-19:** A aba Deslizantes passa a ter dois modos: **No vão** (as folhas da 008, que continuam como estão) e
    **Sobre a caixa**, o conjunto deslizante sobre a caixa inteira (clarify Q4). Este segundo modo é implementado numa
    feature seguinte (clarify Q1). São três sistemas:
    - **Interna (piso-teto)**: peso no trilho de baixo, laterais batente mais fundas que a caixa (padrão 650);
    - **Externa (flutuante)**: peso no trilho de cima, laterais de 580;
    - **Embutida**: trilhos na própria caixa, sem laterais batente; as divisórias internas recuam para dar passagem às
      folhas.

    Parâmetros: Número de portas (padrão = número de vãos), Transpasse (padrão 10; 0 com trilho simples), Folga, Folga
    altura porta (padrão 48), Trilho superior e inferior (Simples, Duplo, Triplo, Quádruplo) e Fechamentos Linear Sup e
    Linear Inf. A largura da folha é (Comprimento + (n − 1) × Transpasse) / n. 🟢 (`prints/S_PZG9jKKrI-1120-editor-portas-configuracao.jpg`,
    `prints/4QEl92sAUoE-0748-editor-portas-trilhos.jpg`, `prints/JfwIZVEnvJA-0255-editor-portas-laterais-lat-arm-650.jpg`;
    a fórmula confere em 5 casos); 🟡 (trilhos triplo e quádruplo: só ditos)
    - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-18)
    - Tipo: alterada
20. **RN-20:** Com conjunto deslizante Interno ou Externo, a caixa pede **profundidade mínima de 580**, as
    prateleiras usam a variante com recuo frontal e o editor avisa quando uma gaveta externa ou uma porta de abrir
    bate nas folhas. 🟡 (`S_PZG9jKKrI [06:05]–[06:23]`, `hPtAAtOKeDU [01:18]–[03:13]`: só dito)
    - Tipo: nova

**E. Design CAFF MOBI**

21. **RN-21:** A galeria de estruturas e a vista do editor seguem a identidade **CAFF MOBI** do canvas de marca:
    - família teal `#0B8582` (escura `#1BB3AD` sobre Noite `#10302F`), creme `#FFF4EA`, laranja `#F07A2A` só para
      seleção e ação principal, e azul `#5BC0FF` para informação;
    - Sora nos títulos;
    - miniaturas das estruturas desenhadas no mesmo traço (chapas em contorno, vão em teal);
    - estado sempre também em texto.

    🟢 (paleta: `inputs/README.md#Design de referência`; tokens da 014:
    `_reversa_forward/014-texturas-fabricantes-grade/design-direction.md#2`). A identidade se aplica à galeria de
    estruturas e à vista do editor, desenhadas na GPU com a família Noite da 014; os painéis nativos do Blender
    continuam nativos (clarify Q3)
    - Tipo: nova

**F. Projetos existentes e padrões editáveis**

22. **RN-22:** Os módulos CAFF MOBI criados antes desta feature **mantêm a construção antiga** (com tampo inteiro)
    até o projetista reaplicar o Padrão de Dimensões ou abrir o módulo no editor. Nesse momento o módulo passa para a
    estrutura equivalente ao tipo dele: Balcão → Inferior c/ Divisória, Aéreo → Superior c/ Divisória, Torre → Torre
    p/ Eletros. Abrir um projeto não muda o plano de corte de nenhum módulo. 🟢 (clarify Q2)
    - Origem no legado: `_reversa_sdd/domain.md#standards` (RN-STANDARDS-11: aplicar o padrão a um módulo CAFFMob)
    - Tipo: nova
23. **RN-23:** Todo valor que nenhum vídeo mostrou na tela entra como **padrão editável** no Padrão de Dimensões ou no
    catálogo de estruturas, nunca fixo no código. Os padrões iniciais são:
    - largura do sarrafo: 100 mm;
    - rodapé: 100 mm de altura, recuo frontal de 50 mm;
    - recuo das prateleiras móveis: 20 mm;
    - tubo do cabideiro: 70 mm abaixo da prateleira de cima.
    
    O mesmo vale para as medidas, as espessuras, as peças marcadas e os componentes opcionais de cada estrutura da
    RN-03. 🟢 (clarify Q5: "tudo poderá ser editado"; princípio III)
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O tipo de estrutura muda as peças geradas (RN-01) | Must | Um "Inferior c/ Divisória" e um "Superior c/ Divisória", ambos de 800 × 700 × 550, saem com listas de peças diferentes: o primeiro com Sarrafo Frontal e Traseiro e sem Base Superior, o segundo com Base Superior | 🟢 |
| RF-02 | Catálogo de estruturas em dados, editável sem código (RN-02) | Must | Acrescentar uma estrutura ao catálogo de dados a faz aparecer na galeria depois de recarregar, sem mudar código | 🟡 |
| RF-03 | Estruturas de Cozinhas: Inferior c/ Divisória e variantes, Gaveteiro, Superior, Torre p/ Eletros (RN-03, RN-04, RN-06) | Must | Cada estrutura de Cozinhas da tabela RN-03 com 🟢/🟡 gera as peças da tabela; o balcão sai sem tampo e com os dois sarrafos | 🟢/🟡 |
| RF-04 | Estruturas de Dormitórios: Armário, s/ Lat, Divisória sobre Base (RN-03) | Must | "Armário" de 1000 × 2500 × 550 com chapa 18 e rodapé do padrão sai com Base Inferior, Base Superior e Rodapé; "Divisória sobre Base" sai sem Base Inferior | 🟢 |
| RF-05 | Estruturas de Salas (RN-03) | Should | "Portas Externas s/ Rod" de 1500 × 700 × 550 sai com Base Inferior e Base Superior inteiras, sem rodapé; marcar Pés 50 põe 4 pés de 50 | 🟢 |
| RF-06 | Estruturas de Escritórios e Outros (RN-03) | Should | "Gaveteiro volante" sai com Rodízios marcados e uma coluna de gavetas; "Gabinete" de banheiro usa as medidas da linha BAN | 🟡 |
| RF-07 | Rodapé da estrutura levanta a caixa e a altura total fica igual (RN-05) | Must | "Armário" de 2500 com chapa 18 e rodapé de 80 tem altura interna 2384 e altura total 2500 | 🟢 |
| RF-08 | Regra de encontro por estrutura (RN-07) | Should | "Sobrepõe Base" cria a base passante; "Sobrepõe Lateral" cria a lateral passante; o comprimento de corte de cada peça muda conforme a regra | 🟡 |
| RF-09 | Montagem por grupo no Padrão de Dimensões: tipo de fundo, sarrafo, rodapé, espessuras (RN-08, RN-09) | Must | Mudar a largura do sarrafo no grupo Inferior do padrão COZ e reaplicar muda os sarrafos de todos os balcões que seguem o padrão, e só deles | 🟢 |
| RF-10 | Plano de corte com as peças reais e os nomes de papel (RN-10) | Must | O corte de um "Inferior c/ Divisória" lista Sarrafo Frontal e Sarrafo Traseiro e não lista Base Superior | 🟢 |
| RF-11 | Galeria "Selecione uma estrutura de caixa" com abas por ambiente (RN-11) | Must | O comando Novo armário abre a galeria com as abas dos ambientes implementados (nesta feature, Cozinhas e Dormitórios); OK numa estrutura abre o editor com "Tipo: <nome>" e as medidas padrão dela; Cancelar não cria nada | 🟢 |
| RF-12 | Árvore de componentes e cabeçalho da estrutura (RN-12) | Must | Num "Inferior c/ Divisória", a árvore traz Sarrafo Frontal e Sarrafo Traseiro marcados e Tampo Linear desmarcado; marcar "Tampo Linear" acrescenta o tampo | 🟢 |
| RF-13 | Modelos da biblioteca CAFF MOBI ligados a estruturas (RN-13) | Must | "Balcão 2 portas" da biblioteca cria um "Inferior c/ Divisória" de 800 com duas portas e sarrafos | 🟡 |
| RF-14 | Largura de vão por fórmula e digitável (RN-14) | Should | 3000, 3 vãos, 18 mm: três vãos de 976; digitar 900 no vão do meio redistribui a diferença nos vizinhos | 🟢 |
| RF-15 | Catálogo de divisões filtrado pelo ambiente, com Invisível e Somente Divisão (RN-15) | Should | Num "Armário" de dormitório aparecem Montante e Invisível; a prateleira Invisível divide o vão e não entra no corte | 🟢 |
| RF-16 | Internos de dormitório: cabideiros, calceiros, sapateiras, porta-cintos (RN-16) | Must | "Cabideiro 01" num vão de 976 cria o tubo abaixo da prateleira de cima e o lança na lista de ferragens | 🟢 |
| RF-17 | Gavetas de dormitório com Interna p/ trilho e afastadores (RN-17) | Should | 3 gavetas "Interna p/ trilho" num vão: a de baixo sai mais alta que as outras duas | 🟢 |
| RF-18 | Caixa de gaveta pelas folgas do padrão, com as peças no corte (RN-18) | Should | Gaveteiro de 200 com laterais de 15 e Folga Corrediça 13: caixa de 144 de largura; o corte lista Lateral, Contra Frente, Posterior e Fundo 6 | 🟢 |
| RF-19 | Conjunto deslizante sobre a caixa: Interna, Externa, Embutida (RN-19) | Should | Caixa de 2400, 2 portas, transpasse 10: folhas de 1205; Interna cria laterais batente de 650; Embutida não cria laterais batente | 🟢 |
| RF-20 | Avisos de compatibilidade com correr (RN-20) | Could | Conjunto Interno numa caixa de 550: aviso "profundidade mínima 580" nos Ajustes automáticos | 🟡 |
| RF-21 | Visual CAFF MOBI na galeria e na vista (RN-21) | Must | A galeria e a vista do editor usam os tokens da família Noite da 014 e o título em Sora; os painéis nativos não mudam; cada estado (selecionado, desabilitado) vem também em texto | 🟢 |
| RF-23 | Módulos antigos mantêm a construção até reaplicar o padrão ou abrir o editor (RN-22) | Must | Abrir um projeto com um balcão antigo não muda o plano de corte; abrir o balcão no editor o passa a "Inferior c/ Divisória", com sarrafos | 🟢 |
| RF-24 | Valores padrão editáveis (RN-23) | Must | Mudar a largura do sarrafo de 100 para 80 no Padrão de Dimensões e reaplicar gera sarrafos de 80 | 🟢 |
| RF-22 | Textos novos em pt-BR e en-US | Must | Em inglês, a galeria aparece como "Select a carcass structure to start building" e as estruturas têm nome traduzido | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Gerar ou regerar um armário de até 4 vãos e 20 divisões em até 0,5 s; a galeria abre em até 1 s com 40 miniaturas | Mesma meta da 006 e da 008; princípio IX | 🟡 |
| Manutenibilidade | A receita de cada estrutura e as regras de montagem ficam em núcleo puro testável fora do Blender, separado do desenho | Princípio IV ("cada camada na espessura certa") | 🟢 |
| Confiabilidade | Para cada estrutura do catálogo há um teste que confere a lista de peças e as medidas de corte de um caso de referência da seção 7 | Princípio VII ("caixote no esquadro") | 🟢 |
| Compatibilidade | As bibliotecas frameless, face frame e closets mantêm os próprios tipos; esta feature muda só o módulo CAFF MOBI | `_reversa_sdd/frameless/design.md#Tipos` | 🟢 |
| Robustez | Estrutura do catálogo com dado inválido (peça desconhecida, medida não numérica) não aparece na galeria e gera aviso claro, sem traceback | Princípio VIII ("fita de borda") | 🟢 |
| Acessibilidade | Contraste de texto de pelo menos 4,5:1 nos tokens CAFF MOBI; estado nunca só por cor | `PRODUCT.md`; 014 `design-direction.md#3` | 🟢 |
| Custo | Nenhuma chamada a modelo de IA nem serviço externo no fluxo: o construtor é regra determinística local | Diretriz do projeto (controle de custo) | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Balcão de cozinha com a construção do Promob
  Dado a galeria de estruturas aberta na aba Cozinhas
  Quando o projetista escolhe "Inferior c/ Divisória" e clica OK
  Então o editor abre com "Tipo: Inferior c/ Divisória", largura 500 e altura e profundidade do Padrão de Dimensões
    da linha Cozinha (no Promob, 700 × 550)
  E a caixa tem Laterais, Base Inferior, Sarrafo Frontal e Sarrafo Traseiro, sem Base Superior
  E o plano de corte lista os dois sarrafos e não lista Base Superior

Cenário: Tampo linear opcional no balcão
  Dado um "Inferior c/ Divisória" aberto no editor
  Quando o projetista marca "Tampo Linear" na árvore de componentes
  Então o balcão ganha o tampo de chapa e ele entra no plano de corte
  Quando desmarca
  Então o tampo sai e os sarrafos continuam

Cenário: Largura de vão digitada
  Dado um "Armário" de 3000 com 3 vãos de 976 e chapa 18
  Quando o projetista digita 900 no vão do meio
  Então os vãos das pontas ficam com 1014 cada

Cenário: Mesmas medidas, tipos diferentes
  Dado um "Inferior c/ Divisória" e um "Superior c/ Divisória", ambos de 800 × 700 × 550
  Quando o projetista gera o plano de corte
  Então o inferior tem sarrafos e o superior tem Base Superior inteira

Cenário: Roupeiro com rodapé
  Dado a aba Dormitórios
  Quando o projetista escolhe "Armário", 3 vãos, 3000 × 2500 × 550, chapa 18, rodapé 80
  Então cada vão tem 976 de largura e 2384 de altura interna
  E a altura total continua 2500

Cenário: Divisória sobre base
  Dado a estrutura "Armário Divisória sobre Base"
  Quando o editor abre
  Então a árvore de componentes não traz Base Inferior

Cenário: Padrão de Dimensões por grupo
  Dado três balcões e dois aéreos que seguem o padrão COZ
  Quando o projetista muda a largura do sarrafo no grupo Inferior e reaplica o padrão
  Então os três balcões mudam e os dois aéreos ficam iguais

Cenário: Biblioteca ligada à estrutura
  Dado a biblioteca CAFF MOBI
  Quando o projetista insere "Balcão 2 portas"
  Então surge um "Inferior c/ Divisória" de 800 com duas portas e sarrafos

Cenário: Cabideiro no roupeiro
  Dado um vão de dormitório selecionado
  Quando o projetista insere "Cabideiro 01" na aba Internos
  Então o tubo aparece abaixo da prateleira de cima
  E a lista de ferragens ganha o tubo

Cenário: Prateleira invisível
  Dado um vão de dormitório selecionado
  Quando o projetista insere a prateleira "Invisível"
  Então o vão fica dividido em dois
  E nenhuma peça nova aparece no 3D nem no plano de corte

Cenário: Conjunto deslizante interno
  Dado um "Armário" de 2400 × 2500 × 600 com 2 vãos
  Quando o projetista insere o conjunto deslizante Interna, 2 portas, transpasse 10
  Então surgem duas folhas de 1205 em trilhos diferentes e laterais batente de 650

Cenário: Caixa rasa para correr
  Dado um "Armário" de 550 de profundidade
  Quando o projetista insere o conjunto deslizante Interna
  Então os Ajustes automáticos avisam "profundidade mínima 580"

Cenário: Estrutura inválida no catálogo
  Dado uma estrutura de catálogo com uma peça desconhecida
  Quando a galeria abre
  Então a estrutura não aparece
  E uma mensagem diz qual estrutura foi ignorada e por quê

Cenário: Cancelar a galeria
  Dado a galeria de estruturas aberta
  Quando o projetista clica Cancelar
  Então nenhum armário é criado e não há passo de desfazer

Cenário: Sala com bases inteiras
  Dado a aba Salas
  Quando o projetista escolhe "Portas Externas s/ Rod" e marca "Pés 50"
  Então a caixa de 1500 × 700 × 550 tem Base Inferior e Base Superior inteiras
  E quatro pés de 50 aparecem fora do plano de corte

Cenário: Gaveteiro volante de escritório
  Dado a aba Escritórios
  Quando o projetista escolhe "Gaveteiro volante"
  Então a caixa vem com Rodízios marcados e uma coluna de gavetas

Cenário: Regra de encontro
  Dado um "Armário" com a regra "Sobrepõe Base"
  Quando o projetista gera o plano de corte
  Então a Base Inferior tem a largura total e as laterais ficam sobre ela

Cenário: Gaveta interna para trilho
  Dado um vão de dormitório selecionado
  Quando o projetista insere 3 gavetas "Interna p/ trilho"
  Então a gaveta de baixo sai mais alta que as outras duas

Cenário: Caixa da gaveta pelas folgas
  Dado um gaveteiro de 200 com laterais de 15 e Folga Corrediça 13
  Quando o projetista insere uma gaveta
  Então a caixa tem 144 de largura
  E o plano de corte lista Lateral, Contra Frente, Posterior e Fundo de 6

Cenário: Visual CAFF MOBI
  Dado a galeria de estruturas aberta
  Quando o projetista passa o mouse numa estrutura e a seleciona
  Então a seleção aparece no destaque CAFF MOBI e o nome da estrutura aparece em texto no rodapé
  E uma estrutura indisponível mostra o motivo em texto

Cenário: Galeria em inglês
  Dado o Blender em inglês
  Quando o projetista abre a galeria
  Então o título é "Select a carcass structure to start building"

Cenário: Projeto antigo não muda sozinho
  Dado um projeto salvo antes desta feature, com um balcão de tampo inteiro
  Quando o projetista abre o projeto
  Então o balcão e o plano de corte ficam iguais
  Quando ele abre o balcão no editor
  Então o balcão passa a "Inferior c/ Divisória", com sarrafo frontal e traseiro

Cenário: Padrão editável
  Dado o Padrão de Dimensões com sarrafo de 100
  Quando o projetista muda o sarrafo para 80 e reaplica o padrão
  Então os balcões que seguem o padrão saem com sarrafos de 80

Cenário: Trilho simples força transpasse zero
  Dado o conjunto deslizante com trilho superior Simples
  Quando o projetista digita transpasse 10
  Então o transpasse volta a 0 com o aviso de que trilho simples não sobrepõe folhas
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 a RF-04, RF-07, RF-09 a RF-13, RF-23, RF-24 | Must | É o problema relatado: cada tipo com a sua construção, a partir da galeria e da biblioteca, com o corte certo, sem mudar projetos antigos sozinho (clarify Q1, Q2, Q5) |
| RF-15, RF-16, RF-17, RF-21, RF-22 | Must | Cozinhas e Dormitórios completos, design CAFF MOBI e regra de idioma do projeto (clarify Q1, Q3) |
| RF-08, RF-14 | Should | Regra de encontro e largura de vão digitada: completam Cozinhas e Dormitórios sem bloquear |
| RF-05, RF-06 | Won't (feature seguinte) | Salas, Escritórios e Outros (clarify Q1) |
| RF-18, RF-19, RF-20 | Won't (feature seguinte) | Caixa de gaveta pelas folgas e conjunto deslizante "Sobre a caixa" (clarify Q1; Q4 já define os dois modos) |
| Cantos (Inferior/Superior Canto Reto), Estrutura p/ Painel, Superior de dormitório, Bancada | Won't (nesta feature) | Só o nome aparece nos vídeos (🔴): falta a estrutura para especificar |
| Bancada, tampo de pedra e base de alvenaria | Won't | No Promob são geometria livre, não armário (`notas-grupo-c.md#2`, "Bancada") |
| Mesa de escritório | Won't | Não é armário; fica para uma feature de móveis soltos |

## 9. Esclarecimentos

### Sessão 2026-10-14

- **Q:** Escopo desta feature? **R:** (b) Arquitetura por tipo (RF-01 a RF-13), Cozinhas e Dormitórios completos e o
  design CAFF MOBI. Salas, Escritórios, Outros, caixa de gaveta e conjunto deslizante ficam para features seguintes.
  → seção 8
- **Q:** O que acontece com os módulos que já estão nos projetos? **R:** (a) Mantêm a construção antiga até o
  projetista reaplicar o padrão ou abrir o editor; o plano de corte não muda sozinho. → RN-22, RF-23
- **Q:** Onde aplicar o design CAFF MOBI? **R:** (a) Galeria de estruturas e vista do editor desenhadas na GPU, com a
  família Noite da 014. → RN-21, RF-21
- **Q:** O conjunto deslizante sobre a caixa inteira substitui as folhas no vão da 008? **R:** (a) Convive: dois modos
  na aba Deslizantes, "No vão" e "Sobre a caixa". → RN-19
- **Q:** Confirma os padrões não vistos nos vídeos (sarrafo 100, rodapé 100 com recuo 50, recuo de prateleira móvel 20,
  tubo 70 abaixo da prateleira)? **R:** Sim, porém tudo poderá ser editado. → RN-04, RN-05, RN-15, RN-16, RN-23, RF-24

## 10. Lacunas

- 🟡 Os vídeos não abrem a aba Estrutura do aéreo, do gaveteiro, da torre p/ eletros nem dos cantos. As peças desses
  tipos na RN-03 são inferidas do nome, da biblioteca e do Configurador; vale conferir num Promob instalado.
- 🟡 A distribuição de alturas das gavetas não fecha com os dados vistos (170,3 em 700 com 4 gavetas). A regra da
  008 (alturas iguais) continua até alguém conferir num Promob instalado.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-14 | Versão inicial gerada por `/reversa-requirements`, a partir de 24 vídeos, 23 legendas e 192 prints | reversa |
| 2026-10-14 | `/reversa-clarify`: 5 respostas (escopo, módulos antigos, design, deslizantes, padrões editáveis); RN-22, RN-23, RF-23, RF-24 | reversa |
| 2026-10-14 | `/reversa-plan`: cenário do balcão e RF-11 alinhados ao escopo e à D-19 (medidas do Padrão de Dimensões) | reversa |
