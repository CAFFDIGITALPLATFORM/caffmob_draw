# Notas do grupo A: Construtor de Armários do Promob (construtor geral e cozinha)

Fonte: 8 vídeos do YouTube, legendas automáticas em `inputs/legendas/` e frames salvos em `inputs/prints/`.
Convenção: **[VISTO]** = lido na tela (print citado); **[DITO]** = só aparece na fala/legenda; **[INFERIDO]** = conta
ou dedução minha a partir de valores vistos (com a conta explícita). Fonte sempre como `<id> [mm:ss]`.

Versões do Promob vistas na barra de título: Promob Plus 2012 (ouZEF0fKBTI), "versão 2011" com interface antiga
(QcqJlr6WZW0, [DITO] 0:07), Promob Academic 5.38.8.7 (L6TMT6wV-xs), Promob Studio Start Solução Sob Medida 5.38.7.7
(wsdaKZtjszg, biblioteca de fábrica própria), Promob Plus 5.60.1.27 (q2aCXTWVrsA), Promob Plus 5.60.12.4
(-nGTqK7rTto, Y8vvtVJUH-0), Promob Plus Enterprise 5.60.15.46 (JCsFoDBSoME).
**O catálogo de tipos e as espessuras mudam conforme a biblioteca do fabricante carregada** (15 mm, 18 mm e 18,5 mm
aparecem em vídeos diferentes). O plugin deve tratar espessuras e lista de componentes como dados do tipo, não como
constantes.

---

## 1. Por vídeo

### -nGTqK7rTto: Construtor de armários no Promob, aulas passo a passo

Resumo: montagem de um guarda-roupa (tipo "Armário", aba Dormitórios) do zero; mostra o catálogo de abas de tipos,
a aba Estrutura com componentes e as abas Divisões (vertical, horizontal, inserção múltipla), Gavetas e Internos.
É o vídeo que melhor mostra as sub-abas de Divisões em versão recente. Resultado: armário 1300 x 2550 x 550 com
maleiro, gaveteiro interno de 4 gavetas, cabideiro e prateleiras múltiplas.

Fluxo:
1. Botão direito na parede, "Construtor de armário" (ou ícone na barra) [DITO 0:27].
2. Escolher o tipo de caixa no catálogo com abas (Dormitórios, Dormitórios - Portas Embutidas, Cozinhas, ...) [VISTO 0:50].
3. Aba Estrutura: Número de vãos, Largura total, Altura, Profundidade, Posição e cotas, Componentes [VISTO 2:02].
4. Mudar largura para 1300 e altura para 2550 [DITO 2:07-2:25; VISTO 2:32 cota 1300 e 2550].
5. Divisões > Vertical: arrastar divisória "Interna c/ Recuo" para o vão, digitar a medida do vão [DITO 3:05-4:04].
6. Divisões > Horizontal: arrastar prateleira com recuo, digitar 500 (maleiro) e 700 (vão do gaveteiro) [DITO 4:11-4:34].
7. Gavetas > Internas: selecionar o vão (dois cliques rápidos), escolher gaveta, "Inserir" [DITO 5:06-5:58].
8. Internos > Cabideiros: selecionar vão, "Cabideiro", "Inserir" [DITO 6:03-6:19].
9. Divisões > Inserção múltipla: escolher linhas na grade, inserir várias prateleiras de uma vez [DITO 4:38-5:01, 6:27-6:39].
10. "Aplicar" valida sem fechar; "OK" fecha e coloca no ambiente [DITO 6:51-7:02].

| Print | O que mostra (rótulos e valores lidos na tela) |
|---|---|
| `-nGTqK7rTto-0050-catalogo-abas-dormitorios.jpg` | Janela "Construtor de Armários", "Selecione uma estrutura de caixa para iniciar a construção:". Abas: Dormitórios, Dormitórios - Portas Embutidas, Cozinhas, Cozinhas Especiais, Cozinhas - Portas Embutidas, Cozinhas Especiais - Portas Embutidas, Cozinhas Cava, Cozinhas Especiais - Cava, Salas. Itens (aba Dormitórios - Portas Embutidas): Armário Canto Reto Esq, Armário Canto Reto Dir, Armário, Armário s/ Lat Esq, Armário s/ Lat Dir, Armário s/ Laterais, Bancada Canto Reto Esq, Bancada Canto Reto Dir, Bancada, Superior Canto Reto Esq, Superior Canto Reto Dir, Superior. Painel da parede: Comprimento 4850, Espessura 150, Pé-direito 2600. |
| `-nGTqK7rTto-0122-aba-estrutura-componentes.jpg` | Tipo: Armário. Abas no topo: Estrutura, Divisões, Gavetas (demais cobertas pela webcam). Definições: Número de vãos 1, Largura total 1000, Altura 2500, Profundidade 550. Posição: "Inferior esquerda", Cota anterior 0, Cota inferior 0, Cota posterior 3850, Cota superior 100. Componentes: [x] Lateral Esquerda 18mm, [x] Lateral Direita 18mm, [x] Divisórias, [x] Base Inferior 18mm, [x] Base Superior 18mm, [x] Rodapés, [ ] Rodízios, [ ] Vistas (auto), [ ] Vistas 150, [ ] Fechamentos 50. Cotas do desenho: vão 964 de largura, 2384 de altura interna. |
| `-nGTqK7rTto-0232-divisoes-vertical.jpg` | Aba Divisões > Vertical. Sub-abas: Divisórias Internas Móveis, Divisórias Internas Fixas, Montante, Distanciador, Sem Divisória. Itens: "Interna c/ Recuo Fron 18mm", "Interna s/ Recuo Fron 18mm". Painel inferior: Movimentação (Passo inicial, Passo). Desenho 1300 x 2550, vão 1264. |
| `-nGTqK7rTto-0418-divisoes-horizontal.jpg` | Divisões > Horizontal. Sub-abas: Prateleiras Móveis, Prateleiras Fixas, Sem Prateleira. Itens: Interna c/ Recuo Fron 18mm, Interna s/ Recuo Fron 18mm, Corrediça, Aramada. Ao arrastar a prateleira aparecem cotas editáveis acima/abaixo (500 digitado; 446 e 1970 do outro lado). Painel: Cotas (Cota Inferior, Cota Superior), Movimentação (Passo inicial, Passo). |
| `-nGTqK7rTto-0440-divisoes-insercao-multipla.jpg` | Divisões > Inserção múltipla. "Divisão Horizontal: Interna c/ Recuo Fron 18mm / Prateleira Linear de Madeira 18"; "Divisão Vertical: Interna c/ Recuo Fron 18mm / Divisória 18"; "Orientação Prioritária" (Vertical / Horizontal); grade 5 x 5 de quadradinhos; Linhas 0, Colunas 0; botão Inserir. Cotas laterais 1716/700 e 1198/700. |
| `-nGTqK7rTto-0512-gavetas-internas-afastadores.jpg` | Gavetas. Sub-abas: Internas, Sapateiras, Prateleira Corrediça, Externas. Opções de gavetas: "s/ CF Reta - Gaveta Interna s/ Contra Frente". Opções de inserção: Número de gavetas 4. Afastadores: [x] Frontal esquerdo, [x] Frontal direito, [x] Traseiro esquerdo, [x] Traseiro direito. Botão Inserir. Vãos 618 e 646, alturas 1734 e 700. |
| `-nGTqK7rTto-0618-internos-cabideiros.jpg` | Internos. Sub-abas: Cabideiros, Calceiros, Sapateiras, Porta Cintos/Gravatas, Pistões, Biblioteca. Itens: Cabideiro, Cab Extensível. Caixa "Inserir invertido" (desabilitada). Alturas 518 / 1198 / 718. |
| `-nGTqK7rTto-0730-armario-3d-propriedades.jpg` | Armário no 3D. Propriedades: Cotas (Afastamento Parede 0, Cota Anterior 1320, Cota Inferior 0, Cota Posterior 2230, Cota Superior 50), Dimensões (Largura 1300, Altura 2550, Profundidade 550, Escalar Não), Orçamento (Orçado Sim, Descrição Armário, Categoria "...trutor de Armários - I...", Grupo dormitorios). Painel com Aberturas, Arranjo, Modelos, Movimentação, Posicionamento, Propriedades. |

### Y8vvtVJUH-0: Como criar um balcão de cozinha pelo editor de armário

Resumo: balcão inferior único de 2700 mm (limite da chapa de MDF de 2750, [DITO 2:22]) feito com "Inferior c/
Divisória" em vez de vários módulos. Divide em vãos para cuba, gavetões, fogão, porta-temperos e portas de giro.
O 3D mostra claramente o **balcão sem tampo, com travessas (sarrafos) frontal e traseira** no topo.

Fluxo:
1. Botão direito na parede > Construtor de armário > aba Cozinhas > "Inferior c/ Divisória" > OK [DITO 1:28-2:16; VISTO 2:01].
2. Estrutura: largura 2700, profundidade 600, altura 750 [DITO 2:38-2:46; VISTO 2:42 com 2700/700/550 durante a digitação, VISTO 3:14 altura 750 e 5:54 "Inferior (2700x750x600)"].
3. Divisões > Vertical "sem recuo": arrastar e digitar larguras: 700 (cuba), 600 (gavetões), 600 (fogão), 200 (porta-temperos), sobra para porta de giro [DITO 3:19-4:05].
4. Divisões > Horizontal "com recuo" no vão da cuba [DITO 4:11-4:18].
5. Gavetas > Gavetões, 2, Inserir; Gavetas, 3, Inserir no porta-temperos [DITO 4:23-4:57; VISTO 4:26].
6. Portas > Ambas > Reta > Inserir nos vãos de porta (Ctrl + dois cliques para selecionar só o vão) [DITO 5:09-5:40; VISTO 5:22].
7. No vão do forno, "estrutura inteira" para simular fechamento [DITO 5:40-5:49].

| Print | O que mostra |
|---|---|
| `Y8vvtVJUH-0-0201-catalogo-cozinhas.jpg` | Aba Cozinhas: Inferior Canto Reto Esq, Inferior Canto Reto Dir, Inferior Canto Reto Esq c/ Rod, Inferior Canto Reto Dir c/ Rod, Inferior c/ Divisória, Inferior c/ Divisória e Rod, Inferior c/ Divisória até Piso, Inferior c/ Divisória até Piso e Rod, Inferior c/ 2 Laterais até Piso, Inferior c/ 2 Laterais até Piso e Rod, Gaveteiro, Gaveteiro c/ Rodapé, Superior Canto Reto Esq, Superior Canto Reto Dir, Superior c/ Divisória, Superior c/ 2 Laterais, Torre p/ Eletros, Torre p/ Eletros c/ Rod. |
| `Y8vvtVJUH-0-0233-inferior-c-divisoria-padrao.jpg` | Valores iniciais do tipo "Inferior c/ Divisória": Número de vãos 1, Largura total 500, Altura 700, Profundidade 550; Posição "Livre" (cotas 1908 / 1477,4 / 2375,5 / 422,6). Componentes: [x] Laterais (expansível), [ ] Laterais Engrossuradas, [x] Divisória, [x] Base Inferior 18mm, [x] Desconto Espessura Sarrafo, [ ] Tampo Linear 18mm, [ ] Pés Plásticos 150, [ ] Rodapés, [ ] Rodapés Granito, [ ] Fechamentos 50. Vão interno 464. |
| `Y8vvtVJUH-0-0242-estrutura-2700-componentes.jpg` | Largura 2700, Altura 700, Profundidade 550 (ainda editando); vão interno 2664 x 664. Mesma lista de componentes. Não há "Base Superior" na lista. |
| `Y8vvtVJUH-0-0314-divisoes-vertical-cozinha.jpg` | Divisões > Vertical. Sub-abas: Divisórias Móveis, Divisórias Fixas, Distanciador, Sem Divisória; abaixo: Com Recuo Frontal / Sem Recuo Frontal. Itens: Interna s/ Recuo Tras 18mm, Interna s/ Recuo Tras Corta Sar 18mm, Interna s/ Recuo Tras c/ Reb 18mm, Interna c/ Recuo Tras 18mm, Interna c/ Recuo Tras Corta Sar 18mm, Interna c/ Recuo Tras c/ Reb 18mm. Desenho 2700 x 750, vão 2664. |
| `Y8vvtVJUH-0-0426-gavetas-gavetoes.jpg` | Gavetas. Sub-abas: Gavetas, Gavetões, Internas, Blum. Opções de gavetas: "Gavetão c/ CF - Caixa Gavetão c/ Contra Frente". Opções de frentes: "Reta - Frente Reta". Número de gavetas 2. Vãos 718 / 600 / 1346, altura interna 714. |
| `Y8vvtVJUH-0-0522-portas-ambas-modelos.jpg` | Portas. Sub-abas: Ambas, Inteira, Esquerda, Direita, Basc Inf, Basc Sup, Frente s/Gaveta. Modelos: Reta, Lisa, Almofada, Fresada, Fresada 02, Colonial, Colonial 02, Colonial 03, Bicolor, Gola Horizontal, Gola Vertical, Borda Alumínio, Cava Horizontal, Cava Vertical, Chanfrada, Country, Country 02. Caixa "Inserir invertido". |
| `Y8vvtVJUH-0-0554-balcao-3d-propriedades.jpg` | 3D: "Inferior (2700x750x600)". Propriedades: Afastamento Parede 0, Cota Anterior 1428, Cota Inferior 87,4, Cota Posterior 655,5, Cota Superior 1762,6; Largura 2700, Altura 750, Profundidade 600, Escalar Não, Rotação Ripado Miami Tela 0. |
| `Y8vvtVJUH-0-0554-balcao-3d-topo-aberto-travessas-recorte.jpg` | Recorte ampliado do mesmo frame: topo **aberto**, sem tampo; duas travessas horizontais longitudinais (frente e fundo) ligando as laterais; divisórias aparecendo por dentro. |

### JCsFoDBSoME: Construtor de armários em cozinhas

Resumo: compara dois módulos de biblioteca lado a lado (gaveteiro + armário 2 portas, duas laterais juntas) com um
**módulo único** do construtor (1430 x 700 x 550) com divisória interna, gaveteiro de 4 gavetas, 2 portas e
prateleira. Argumento: módulo único economiza uma lateral [DITO 6:02-6:17]. Ordem importa: portas antes da
prateleira, senão as portas são divididas pela prateleira [DITO 4:44-4:58].

Fluxo:
1. Botão direito > Construtor > Cozinhas > "Inferior c/ Divisória" > OK [VISTO 2:50].
2. Abre com 500 de largura [VISTO 3:14; DITO "470 de largura" 3:15, que é a medida interna]. Muda para 1430 (vão interno 1400) [VISTO 4:09].
3. Divisões > Vertical > Divisórias Fixas: arrasta e deixa 500 para a gaveta [DITO 3:57-4:18; VISTO 4:09].
4. Gavetas > Gavetas: "já tem a opção de 4 gavetas", arrasta para o vão [DITO 4:25-4:39; VISTO 4:36].
5. Portas > Ambas > Reta, arrasta para o vão [DITO 5:02-5:23; VISTO 5:14].
6. Só então Divisões > Horizontal: prateleira no vão das portas [DITO 5:26-5:35; VISTO 5:40].

| Print | O que mostra |
|---|---|
| `JCsFoDBSoME-0250-catalogo-cozinhas-inferior-c-divisoria.jpg` | Catálogo aba Cozinhas (Promob Plus Enterprise 5.60.15.46): mesmos tipos do Y8vvtVJUH-0, "Inferior c/ Divisória" selecionado. Parede 4850x150x2600. |
| `JCsFoDBSoME-0314-estrutura-padrao-500x700x550-15mm.jpg` | Abas: Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos. Tipo Inferior c/ Divisória: vãos 1, Largura 500, Altura 700, Profundidade 550; Posição "Inferior esquerda" (Cota anterior 0, inferior 0, posterior 4350, superior 1900). Componentes: [x] Laterais, [ ] Laterais Engrossuradas, [x] Divisória, [x] Base Inferior 15mm, [ ] Tampo Linear 18mm, [ ] Pés Plásticos 150, [ ] Rodapés, [ ] Rodapés Granito, [ ] Fechamentos 50. Movimentação: Passo inicial 0, Passo 10. Vão interno 470. Botões OK, Cancelar, Aplicar. |
| `JCsFoDBSoME-0409-divisorias-fixas-vertical.jpg` | Divisões > Vertical > Divisórias Fixas > Com Recuo Frontal: Fixa s/ Recuo Tras 15mm, Fixa s/ Recuo Tras Corta Sar 15mm, Fixa s/ Recuo Tras c/ Reb 15mm, Fixa c/ Recuo Tras 15mm, Fixa c/ Recuo Tras Corta Sar 15mm, Fixa c/ Recuo Tras c/ Reb 15mm. Largura 1430, vão 1400, altura 700. |
| `JCsFoDBSoME-0436-gavetas-4-gavetas.jpg` | Gavetas > Gavetas: "Gaveta c/ CF - Caixa Gaveta c/ Contra Frente"; frente "Reta - Frente Reta"; Número de gavetas 4. Vãos 500 / 900, altura interna 670. |
| `JCsFoDBSoME-0514-portas-ambas.jpg` | Portas: sub-abas Inteira, Ambas, Esquerda, Direita, Basc Inf, Basc Sup; modelos Reta, Lisa, Almofada, Fresada, Fresada 02, Colonial, Colonial 02, Colonial 03, Bicolor, Gola Horizontal, Gola Vertical, Borda Alumínio, Cava, Cava Vertical, Chanfrada. Vãos 515 / 885 depois da gaveta inserida. "Não há propriedades disponíveis!". |
| `JCsFoDBSoME-0540-prateleiras-moveis-vidro.jpg` | Divisões > Horizontal > Prateleiras Móveis > Com Recuo Frontal: Interna s/ Recuo Tras 15mm, Vidro s/ Recuo Tras 10mm, Interna c/ Recuo Tras 15mm, Vidro c/ Recuo Tras 10mm. |
| `JCsFoDBSoME-0610-balcao-3d-travessas-topo-aberto.jpg` | 3D aproximado: "Inferior (1430x700x550)". Topo aberto, travessa horizontal na frente e outra no fundo, caixas de gaveta visíveis por cima, divisória entre gaveteiro e portas. |

### q2aCXTWVrsA: Curso Promob LB Design, Construtor de Armários, Cozinha

Resumo: o instrutor usa o tipo "Portas Externas s/ Rod" da aba **Salas** para o balcão (diz "módulo sala mesmo,
não tem problema", [DITO 0:37]), ajusta largura ao vão da parede menos tamponamentos, 2 vãos, portas de giro e
prateleira. O tampo é posto **depois, pelo Editor de Tamponamentos** (profundidade 570 para 550 do móvel, espessura
25 lida na tela). O aéreo com portas de correr **não** é feito no construtor: é montado peça a peça com
tamponamentos e geometria retangular.

Fluxo:
1. Botão direito na parede > "Construir Armário" [VISTO 0:33] > aba Salas > "Portas Externas s/ Rod" [VISTO 0:35].
2. Largura = vão da parede menos 30 (15 de tamponamento de cada lado) [DITO 0:51-1:00; VISTO 0:51 "1579,3" sendo editado, depois 1549,3].
3. Altura 800 e altura do chão 110 [DITO 1:18-1:25; VISTO cota inferior 110 a partir de 0:51].
4. Mais um vão (2 vãos), Portas > porta gola horizontal nos dois vãos, Divisões > prateleira interna com duplo clique [DITO 1:28-1:51; VISTO 1:54].
5. OK. Tampo pelo Editor de Tamponamentos: profundidade 57 cm para móvel de 55 cm, 2 cm de sobra na frente, "espessura de 15" [DITO 2:01-2:18] (na tela a espessura lida é 25) [VISTO 2:04].
6. Parte superior (aéreo) construída manualmente com tamponamentos, profundidade 38 cm, e portas deslizantes da biblioteca "Portas e Frentes > Deslizante de madeira" [DITO 2:31-5:40].

| Print | O que mostra |
|---|---|
| `q2aCXTWVrsA-0035-catalogo-salas.jpg` | Abas visíveis: Cozinhas Especiais - Portas Embutidas, Cozinhas Cava, Cozinhas Especiais - Cava, Salas. Aba Salas: Portas Embutidas s/ Rod, Portas Embutidas c/ Rod, Portas Externas s/ Rod (selecionado), Portas Externas c/ Rod, Estrutura p/ Painel. |
| `q2aCXTWVrsA-0043-portas-externas-s-rod-padrao.jpg` | Valores iniciais: vãos 1, Largura total 1500, Altura 700, Profundidade 550, Posição Livre. Componentes: [x] Lateral Esquerda 18mm, [x] Lateral Direita 18mm, [x] Divisória, [x] Base Inferior 18mm, [x] Base Superior 18mm, [ ] Pés 50, [ ] Rodízios 100, [ ] Rodapés. Vão interno 1464. |
| `q2aCXTWVrsA-0051-estrutura-componentes-base-superior.jpg` | Largura 1579,3 sendo digitada, Cota inferior 110, vão 1543,3. Mesmos componentes; Movimentação Passo inicial 0, Passo 10. |
| `q2aCXTWVrsA-0154-divisoes-horizontal-2-vaos.jpg` | 2 vãos 765,7 e 747,7, altura interna 764; prateleira dividindo um vão em 391 / 373. Divisões > Horizontal > Prateleiras Móveis: Interna c/ Recuo Fron 18mm, Interna s/ Recuo Fron 18mm, Vidro c/ Recuo Fron 10mm, Vidro s/ Recuo Fron 10mm. Sub-abas Prateleiras Fixas, Sem Prateleira. |
| `q2aCXTWVrsA-0204-editor-tamponamentos-tampo.jpg` | Janela "Editor de Tamponamentos": Vista Frontal e Planta Baixa; Selecionar Tampos "Inferior - Tamponamento Inferior $H$", Cores / Branco; Alinhamento: Planta Baixa "Acima", Vista Frontal "Traseiro"; Dimensão: Profundidade 570, Espessura 25; Posição: Deslocamento 0; [x] Agrupar itens após inserção. Rodapé: "Rack (1549,3x800x550)". |
| `q2aCXTWVrsA-0746-resultado-balcao-e-aereo-manual.jpg` | Resultado: balcão com portas e tampo; aéreo de 2 portas de correr montado à mão acima. |

### L6TMT6wV-xs: PROMOB Aula 5, Construtor de Armários

Resumo: balcão de cozinha 1400 x 700 x 600 com 3 vãos (gavetas, 2 portas, porta-latas) e depois um armário de
dormitório "Armário Divisória sobre Base" 2600 x 2600 x 600. **É o vídeo que mostra explicitamente "Sarrafo Frontal
15mm" e "Sarrafo Traseiro 15mm" como componentes do balcão inferior.** Mostra também prateleira centralizada por
duplo clique, "Sem Prateleira > Somente Divisão" (linha imaginária) e nichos por inserção múltipla.

Fluxo (cozinha):
1. Selecionar parede ou piso; ícone na barra superior ou botão direito > Construtor de armário [DITO 0:20-0:27].
2. Cozinhas > "Inferior c/ Divisória" [VISTO 0:31].
3. Estrutura: largura 1400, altura 700, profundidade 600, 3 vãos [DITO 0:45-1:01; VISTO 1:06].
4. Clicar no vão e digitar a largura: 400 (gavetas) e 200 (porta-latas) [DITO 1:03-1:13].
5. Prateleira horizontal com recuo: arrastar não centraliza; apagar e dar dois cliques no vão e dois na prateleira, "entra centralizada" [DITO 1:29-1:51; VISTO 2:11 com 327,5 / 327,5].
6. Gavetas: frente (Reta, Lisa, Frisada, Gola), número 4, arrastar [DITO 1:53-2:23].
7. Portas: Ambas, Inteira, Esquerda, Direita, Basculante inferior, Basculante superior; dois cliques no modelo com o vão selecionado; "Inserir invertido" muda o lado [DITO 2:29-3:13].
8. Internos > Biblioteca > Acessórios > Cozinhas > Aramados > Porta Latas [DITO 3:13-3:23; VISTO 3:16].
9. OK; Aberturas abre portas e gavetas no 3D [DITO 3:32-3:38; VISTO 3:36].

Fluxo (dormitório, resumido): "Armário divisória sobre base", largura 2600, altura 2600, profundidade 600, 3 vãos
divididos "por igual" [DITO 4:02-4:26]; prateleiras com recuo 550 e 720; gavetas com contra frente de vidro;
sapateiras; cabideiro a 70 mm da prateleira de cima [DITO 5:35-5:41]; "Sem prateleira" como linha imaginária
para dividir o vão entre 2 gavetas e 2 sapateiras sem cortar o montante [DITO 5:53-7:06]; nichos por inserção
múltipla [DITO 7:28-7:49]; portas "Ambas" no maleiro e no corpo [DITO 8:06-8:25].

| Print | O que mostra |
|---|---|
| `L6TMT6wV-xs-0031-catalogo-cozinhas.jpg` | Promob Academic 5.38.8.7. Abas: Cozinhas, Cozinhas Cava, Cozinhas - Portas Embutidas, Dormitórios, Dormitórios - Portas Embutidas. Itens Cozinhas: Inferior c/ Divisória, Inferior c/ Divisória e Rod, Inferior c/ Divisória até Piso, Inferior c/ Divisória até Piso e Rod, Inferior c/ 2 Laterais até Piso, Inferior c/ 2 Laterais até Piso e Rod, Gaveteiro, Gaveteiro c/ Rodapé, Superior c/ Divisória, Superior c/ 2 Laterais, Torre p/ Eletros, Torre p/ Eletros c/ Rod. |
| `L6TMT6wV-xs-0040-inferior-c-divisoria-sarrafos-15mm.jpg` | Valores iniciais: vãos 1, Largura 500, Altura 700, Profundidade 550; Posição "Inferior esquerda" (anterior 0, inferior 0, posterior 4400, superior 1900). Componentes: [x] Laterais, [ ] Laterais Engrossuradas, [x] Divisória, [x] Base Inferior 15mm, **[x] Sarrafo Frontal 15mm, [x] Sarrafo Traseiro 15mm**, [ ] Tampo Linear 15mm, [ ] Pés Plásticos 150 (lista continua abaixo, cortada). Vão interno 470. |
| `L6TMT6wV-xs-0106-estrutura-3-vaos-1400x700x600.jpg` | Número de vãos 3, Largura 1400, Altura 700, Profundidade 600. Primeiro vão editado para 400, cota ao lado 923,3; altura interna 670. |
| `L6TMT6wV-xs-0211-gavetas-frente-gola-prateleira-centralizada.jpg` | Gavetas > Gavetas: "Gaveta c/ CF - Caixa Gaveta c/ Contra Frente"; frente "Gola - Frente Gola"; Número de gavetas 4. Prateleira centralizada no vão do meio: 327,5 acima e 327,5 abaixo; painel Cotas: Cota Inferior 327,5, Cota Superior 327,5. Status "Selecionado: Interna c/ Recuo Fron 15mm". |
| `L6TMT6wV-xs-0316-internos-biblioteca-aramados.jpg` | Internos > Biblioteca: combos Acessórios / Cozinhas / Aramados; itens (página 1/12): Fruteira, 2 Cestos, Cesto Meia Lua, Cesto 3/4, Gaveta, Gaveta Pia, Gaveteiro, Porta Latas 01. Vãos 1170 + 200, altura 670. |
| `L6TMT6wV-xs-0336-balcao-3d-aberto-sarrafos.jpg` | 3D "Inferior (1400x700x600)" com portas abertas: topo aberto, travessa frontal e travessa traseira no alto, 4 gavetas, prateleira, porta-latas aramado. |
| `L6TMT6wV-xs-0408-dormitorio-armario-divisoria-sobre-base.jpg` | Tipo "Armário Divisória sobre Base": vãos 1, Largura 1000 (2600 sendo digitado), Altura 2500, Profundidade 600, Posição Livre (Cota inferior 100). Componentes: [x] Lateral Esquerda 15mm, [x] Lateral Direita 15mm, [x] Base Superior 15mm, [x] Rodapés, [ ] Vistas, [ ] Fechamentos 50. Não há "Base Inferior" na lista. Vão interno 970. |
| `L6TMT6wV-xs-0615-sem-prateleira-somente-divisao.jpg` | Divisões > Horizontal > Sem Prateleira: item "Somente Divisão". Painel Movimentação e Posicionamento (X 0, Y -295, Z 1142). Alturas 2037 / 450 / 270. |

### QcqJlr6WZW0: Project, Ferramentas, Construtor de armários (Cyncly)

Resumo: vídeo oficial curto da versão 2011, interface antiga com painel "Propriedades / Agregados / Estrutura".
Mostra os 4 tipos de estrutura por **regra de sobreposição** (Sobrepõe Base, Sobrepõe Base c/Rodapé, Sobrepõe
Lateral, Sobrepõe Lateral c/Rodapé), divisórias e prateleiras fixas x móveis, nichos e agregados.

Fluxo:
1. Ícone na barra ou botão direito na parede [DITO 0:17-0:26]; escolher a estrutura [VISTO 0:26].
2. Definir quantidade de vãos, dimensões totais e posição na parede (Esquerda / Central / Direita) [DITO 0:38-0:47; VISTO 0:42].
3. Inserir prateleiras e divisórias pela barra (menus "Prateleiras Fixas" / "Prateleiras Móveis"); fixas têm a profundidade do armário, móveis têm recuo configurável na inserção; aparecem cotas de posição [DITO 0:47-1:20; VISTO 1:00].
4. Nichos: quantidade de divisões horizontais e verticais [DITO 1:23-1:33; VISTO 1:30].
5. Agregados: selecionar o vão, clicar no agregado, "Inserir"; tipos cabideiro, calceiro, fundos, gavetas, frentes; gavetas com quantidade [DITO 1:36-1:58; VISTO 1:46, 1:54].
6. OK; para ajustar depois, botão direito no armário e abrir de novo o Construtor [DITO 2:01-2:10].

| Print | O que mostra |
|---|---|
| `QcqJlr6WZW0-0026-tipos-de-estrutura-2011.jpg` | "Selecione uma estrutura para iniciar a construção do armário": Sobrepõe Base, Sobrepõe Base c/Rodapé (selecionado), Sobrepõe Lateral, Sobrepõe Lateral c/Rodapé. |
| `QcqJlr6WZW0-0042-estrutura-3-vaos-componentes.jpg` | Tipo: Sobrepõe Base c/Rodapé. Definições: Número de vãos 3, Largura total 2500, Altura (editando; 2600 no desenho), Profundidade 550, botão Aplicar. Posição: Esquerda / Central / Direita. Componentes: [x] Lateral Esquerda 18mm, [x] Divisória 18mm, [x] Lateral Direita 18mm, [x] Base Inferior 18mm, [x] Base Superior 18mm, [x] Rodapé 18mm. |
| `QcqJlr6WZW0-0100-menu-prateleiras-fixas-moveis.jpg` | Menu da barra: Prateleiras Fixas > "Interna mm"; Prateleiras Móveis. Altura 2300. |
| `QcqJlr6WZW0-0130-nichos-e-cotas-dos-vaos.jpg` | Vãos 827,3 / 809,3 / 827,3; prateleiras com cotas 1024 / 472 / 688; nicho em grade no vão central. |
| `QcqJlr6WZW0-0146-agregados-outros-calceiros.jpg` | Agregados: abas Frentes, Fundos, Gavetas, Outros; Outros > Cabideiros / Calceiros; calceiros Esquerdo, Central, Direito. |
| `QcqJlr6WZW0-0154-agregados-gavetas-afastadores.jpg` | Agregados > Gavetas > Interna: "Gaveta - Gaveta Interna"; Número de gavetas 5; Afastadores [x] Esquerdo [x] Direito. Alturas 1514 / 670. |
| `QcqJlr6WZW0-0202-armario-3d-resultado.jpg` | Armário de 3 vãos no ambiente, com prateleiras, nicho, cabideiro e 5 gavetas internas. |

### ouZEF0fKBTI: Promob 1, Construtor de armário

Resumo: vídeo curto (1:32) em Promob Plus de 2012. Mostra o menu de contexto da parede, os 4 tipos por sobreposição
e a aba Estrutura com Posição Esquerda/Central/Direita. O armário nasce com a largura e a altura da parede
(4,85 x 2,6 m) e o instrutor reduz para 3 x 1 m centralizado.

Fluxo:
1. Selecionar a parede, botão direito, "Construir Armários" [VISTO 0:17].
2. Escolher "Sobrepõe Base c/Rodapé" [DITO 0:31; VISTO 0:22].
3. A tela já traz largura e altura da parede, com rodapé e uma divisão (2 vãos) [DITO 0:43-0:55; VISTO 0:44].
4. Mudar para largura 3, altura 1 e posição Central [DITO 1:04-1:27; VISTO 1:28].

| Print | O que mostra |
|---|---|
| `ouZEF0fKBTI-0017-menu-construir-armario.jpg` | Menu de contexto da parede: Recortar, Copiar, Colar, Remover, Duplicar, Ferramentas, Editar Paredes..., Editar Geometria..., Editar Faixas..., Editar Regiões..., Réguas, **Construir Armários**, Converter para, Camadas, Segmentar, Rebaixar, Transparente, Visível / Invisível, Editar Tamponamentos... Faixas da parede marcadas em 0,16 / 0,87 / 2,15. Parede 4,85 x 0,15 x 2,6. |
| `ouZEF0fKBTI-0022-tipos-de-estrutura.jpg` | Sobrepõe Base, Sobrepõe Base c/Rodapé, Sobrepõe Lateral, Sobrepõe Lateral c/Rodapé. |
| `ouZEF0fKBTI-0044-aba-estrutura-componentes.jpg` | Tipo: Sobrepõe Base c/Rodapé. Painel: Propriedades, Agregados, Estrutura. Número de vãos 2, Largura total 4,85, Altura 2,6, Profundidade 0,55 (unidade em metros nesta instalação), Posição Esquerda. Componentes: [x] Lateral Esquerda 18mm, [x] Lateral Direita 18mm, [x] Divisória 18mm, [x] Base Inferior 18mm, [x] Base Superior 18mm, [x] Rodapé 18mm. |
| `ouZEF0fKBTI-0128-estrutura-3000x1000-central.jpg` | Largura 3, Altura 1, Profundidade 0,55, Posição Central; desenho com 2 vãos e faixa de rodapé embaixo. |

### wsdaKZtjszg: Torre de Fornos no Construtor de Armários

Resumo: vídeo de um fabricante (biblioteca "Solução Sob Medida", Promob Studio Start 5.38.7.7) mostrando a torre
de fornos feita no tipo "Armário Despenseiros". Recomenda **não** usar prateleira inteira entre forno e micro: usar
"Gaveta s/ Corpo" (só a frente) como painel fixo de fechamento e uma prateleira solta dimensionada para o vão.
Ganhou porta basculante superior. Fundo deixou de ser emendado aos 800 mm (veio da chapa corrigido) [DITO 0:53-1:16].

Fluxo:
1. Construtor > aba Cozinhas > "Armário Despenseiros" [VISTO 0:21].
2. Estrutura: 700 x 2400 x 550 [VISTO 1:14].
3. Divisões > Horizontal > Prateleiras Fixas "Não Divide o Fundo" [VISTO 2:00; DITO 2:01 "prateleira fixa"].
4. Gavetas > Gaveta, 2, no vão de baixo [DITO 2:12-2:16; VISTO 2:50].
5. Gavetas > "Gaveta s/ Corpo", 1, no vão do forno e micro [DITO 2:52-3:15; VISTO 3:22].
6. Portas > Basculante > "Superior (7152)" no vão de cima [DITO 3:25-3:35; VISTO 3:38].
7. No 3D trocar a frente de gola para porta reta e "sem puxador" pela aba Modelos [DITO 3:51-4:07].

| Print | O que mostra |
|---|---|
| `wsdaKZtjszg-0021-catalogo-cozinhas-despenseiro.jpg` | Abas Cozinhas, Dormitórios, Escritórios. Cozinhas: Armário Despenseiros, Balcões Inferiores, Armários Superiores. |
| `wsdaKZtjszg-0026-despenseiro-padrao-500x1350x550.jpg` | Abas Estrutura, Divisões, Gavetas, Portas (só 4). Tipo: Armário Despenseiros. Valores iniciais: vãos 1, Largura 500, Altura 1350, Profundidade 550; Posição Inferior esquerda (0 / 0 / 4350 / 1250). Componentes: [ ] Rodapé, [ ] Pés Plásticos 150, [ ] Fechamentos 50, [ ] Vista 150. Vão interno 463. |
| `wsdaKZtjszg-0114-estrutura-700x2400-componentes.jpg` | Largura 700, Altura 2400, Profundidade 550; vão interno 663 x 2363. |
| `wsdaKZtjszg-0200-prateleiras-fixas-nao-divide-fundo.jpg` | Divisões: Vertical, Horizontal, Inserção múltipla; Horizontal: Prateleiras Móveis, Prateleiras Fixas, Prateleiras Vidro. Fixas: "Não Divide o Fundo c/ Recuo Front", "Não Divide o Fundo s/ Recuo Front", "Não Divide o Fundo - s/ Recuo Front p/ Basc...". |
| `wsdaKZtjszg-0250-gavetas-2-gavetas-vaos.jpg` | Gavetas: sub-abas Gaveta, Gaveta s/ Corpo, Gaveta Tandem Parcial c/ Blumotion (mais abas por setas). "Gaveta"; Número de gavetas 2. Vãos (alturas) 513 / 1151,5 / 698,5. |
| `wsdaKZtjszg-0322-gaveta-sem-corpo-nicho-forno.jpg` | "Gaveta s/ Corpo" (miniatura "Montagem"); Número de gavetas 1; vão do meio 1151,5. |
| `wsdaKZtjszg-0338-portas-basculante-superior.jpg` | Portas: Ambas, Esquerda, Direita, Inteira, Basculante; item "Superior (7152)". Vãos 494,5 / 1868,5. |
| `wsdaKZtjszg-0434-torre-3d-resultado.jpg` | Torre no 3D: laterais do piso ao topo, topo fechado, basculante em cima, frente fixa no meio, 2 gavetas embaixo. |

---

## 2. Arquitetura por tipo de armário (consolidado)

Regra geral observada: **cada tipo do catálogo é uma "estrutura de caixa" com sua própria lista de componentes
marcados por padrão**. O construtor não usa uma caixa genérica com medidas trocadas; o que muda entre balcão, aéreo,
torre e dormitório é quais peças vêm marcadas (base superior x sarrafos, rodapé, pés, laterais até o piso).

### 2.1 Balcão / inferior de cozinha ("Inferior c/ Divisória" e variantes)

- **Peças vistas por padrão**: Laterais, Divisória, Base Inferior, **Sarrafo Frontal** e **Sarrafo Traseiro**
  (L6TMT6wV-xs [0:40]) ou, em outra biblioteca, "Desconto Espessura Sarrafo" (Y8vvtVJUH-0 [2:33]).
  **Não existe "Base Superior" na lista** do inferior (Y8vvtVJUH-0 [2:33], JCsFoDBSoME [3:14], L6TMT6wV-xs [0:40]).
- **Topo**: aberto, fechado por **duas travessas** (frente e fundo) no alto. VISTO no 3D: Y8vvtVJUH-0 [5:54] (recorte),
  JCsFoDBSoME [6:10], L6TMT6wV-xs [3:36]. Pela imagem as travessas parecem deitadas (face larga na horizontal), mas
  a largura delas não foi lida em lugar nenhum.
- **Tampo**: componente opcional **"Tampo Linear 18mm"/"Tampo Linear 15mm" desmarcado por padrão**. Na prática o tampo
  (pedra ou MDF) é colocado à parte; em q2aCXTWVrsA [2:04] pelo Editor de Tamponamentos (profundidade 570 para
  caixa de 550; espessura 25 lida).
- **Apoio no piso**: Pés Plásticos (valor 150 ao lado) e Rodapés / Rodapés Granito, **todos desmarcados por padrão**
  no tipo "Inferior c/ Divisória". As variantes "... e Rod" do catálogo trazem rodapé (só o nome foi visto, a tela
  dessas variantes não foi aberta em nenhum vídeo do grupo A).
- **Laterais até o piso**: variantes "Inferior c/ Divisória até Piso", "Inferior c/ 2 Laterais até Piso" (nome visto,
  estrutura interna não mostrada). [INFERIDO] no tipo padrão as laterais assentam sobre a base ou a base passa por
  baixo: a altura interna é altura menos 2 espessuras (700 - 670 = 30 com 15 mm; 750 - 714 = 36 com 18 mm), isto é,
  base inferior + espessura da travessa.
- **Divisórias de balcão** têm variantes próprias: "Corta Sar" (corta o sarrafo) e "c/ Reb" (com rebaixo para fundo),
  com ou sem recuo traseiro, com ou sem recuo frontal (Y8vvtVJUH-0 [3:14], JCsFoDBSoME [4:09]).
- **Medidas padrão vistas**: largura 500, altura 700, profundidade 550, 1 vão (Y8vvtVJUH-0 [2:33], JCsFoDBSoME [3:14],
  L6TMT6wV-xs [0:40]). Medidas usadas nos exemplos: 2700 x 750 x 600; 1430 x 700 x 550; 1400 x 700 x 600.
- **Limite**: peça única até o comprimento da chapa (2750 mm) [DITO Y8vvtVJUH-0 2:22].

### 2.2 Aéreo / superior ("Superior c/ Divisória", "Superior c/ 2 Laterais", "Superior Canto Reto Esq/Dir", "Armários Superiores")

- Tipos **vistos só no catálogo** (Y8vvtVJUH-0 [2:01], L6TMT6wV-xs [0:31], wsdaKZtjszg [0:21]). Nenhum vídeo do grupo A
  abriu a aba Estrutura de um superior: **componentes, espessuras e medidas padrão do aéreo NÃO foram lidos**.
- q2aCXTWVrsA monta o aéreo **fora do construtor**, com tamponamentos, profundidade 38 cm [DITO 2:52] e altura 60 cm
  [DITO 3:22], fundo por geometria retangular de 15 mm [DITO 4:03].
- Para comparação, o tipo de sala "Portas Externas s/ Rod" (que q2aCXTWVrsA usou como balcão) traz **Base Inferior e
  Base Superior inteiras** + laterais + Pés 50 + Rodízios 100 + Rodapés (q2aCXTWVrsA [0:43]). Isso mostra que caixa
  com base e "tampo" inteiros é outro tipo, não o inferior de cozinha.

### 2.3 Alto / torre de fornos / despenseiro ("Torre p/ Eletros", "Torre p/ Eletros c/ Rod", "Armário Despenseiros")

- "Torre p/ Eletros" e "Torre p/ Eletros c/ Rod" vistos só no catálogo (Y8vvtVJUH-0 [2:01], L6TMT6wV-xs [0:31]).
- "Armário Despenseiros" (biblioteca de fábrica, wsdaKZtjszg): padrão 500 x 1350 x 550, componentes opcionais Rodapé,
  Pés Plásticos 150, Fechamentos 50, Vista 150 (todos desmarcados) [0:26]. Laterais, bases e fundo **não aparecem
  como itens desmarcáveis** nessa biblioteca. [INFERIDO] espessura 18,5: vão 663 em 700 de largura e 2363 em 2400 de
  altura (37 = 2 x 18,5); o rodapé de seleção do 3D confirma "Frente de Gaveta Gola (694x1167x18,5)" [3:54].
- 3D da torre: laterais inteiras do piso ao topo, topo fechado [VISTO 4:34].
- Divisão típica: vão de baixo com 2 gavetas (698,5), vão do meio para forno + micro (1151,5) fechado por
  "Gaveta s/ Corpo" e prateleira solta, vão de cima com basculante (513 / 494,5) [VISTO 2:50, 3:22, 3:38].
- Prateleira fixa da torre: "Não Divide o Fundo" (o fundo continua inteiro atrás da prateleira) [VISTO 2:00].

### 2.4 Gaveteiro ("Gaveteiro", "Gaveteiro c/ Rodapé")

- Visto só no catálogo (Y8vvtVJUH-0 [2:01], JCsFoDBSoME [2:50], L6TMT6wV-xs [0:31]). Estrutura não aberta.
- Na prática os vídeos fazem o gaveteiro **como vão dentro do balcão**, com Gavetas > N gavetas (JCsFoDBSoME, L6TMT6wV-xs).

### 2.5 Canto ("Inferior Canto Reto Esq/Dir", "... c/ Rod", "Superior Canto Reto Esq/Dir", "Armário Canto Reto Esq/Dir", "Bancada Canto Reto Esq/Dir")

- Só nomes no catálogo (Y8vvtVJUH-0 [2:01], -nGTqK7rTto [0:50]). Nenhum vídeo do grupo A abriu um tipo de canto.
  Só existe "canto reto"; canto em L ou 45 graus não aparece no construtor destes vídeos.

### 2.6 Dormitório / armário alto genérico ("Armário", "Armário Divisória sobre Base", "Sobrepõe ...")

- "Armário" (5.60): Lateral Esquerda 18, Lateral Direita 18, Divisórias, Base Inferior 18, Base Superior 18, Rodapés
  marcados; Rodízios, Vistas (auto), Vistas 150, Fechamentos 50 desmarcados; padrão visto 1000 x 2500 x 550
  (-nGTqK7rTto [2:02]). [INFERIDO] rodapé de 80: 2500 - 2384 = 116 = 18 + 18 + 80.
- "Armário Divisória sobre Base" (5.38): Lateral Esq 15, Lateral Dir 15, Base Superior 15, Rodapés marcados; Vistas e
  Fechamentos 50 desmarcados; **sem Base Inferior na lista**; padrão 1000 x 2500 x 600, cota inferior 100
  (L6TMT6wV-xs [4:08]).
- Versão 2011/2012: os tipos se chamam pela **regra de sobreposição**: Sobrepõe Base, Sobrepõe Base c/Rodapé,
  Sobrepõe Lateral, Sobrepõe Lateral c/Rodapé (QcqJlr6WZW0 [0:26], ouZEF0fKBTI [0:22]). Componentes: Lateral Esq,
  Lateral Dir, Divisória, Base Inferior, Base Superior, Rodapé, todos 18 mm (QcqJlr6WZW0 [0:42]). Os vídeos não
  explicam o que cada sobreposição faz; pelo nome, define se a base passa por cima/por baixo das laterais ou o contrário.

### 2.7 Salas ("Portas Embutidas s/ Rod", "Portas Embutidas c/ Rod", "Portas Externas s/ Rod", "Portas Externas c/ Rod", "Estrutura p/ Painel")

- "Portas Externas s/ Rod": 1500 x 700 x 550, Lateral Esq/Dir 18, Divisória, Base Inferior 18, Base Superior 18,
  Pés 50, Rodízios 100, Rodapés (q2aCXTWVrsA [0:43]). Pés, rodízios e rodapé desmarcados.
- "Portas Embutidas" x "Portas Externas" também existe em Dormitórios e Cozinhas ("- Portas Embutidas"): é a família
  do tipo que decide se a porta fica sobreposta ou dentro do vão. Só nomes vistos.

---

## 3. Abas e catálogos do construtor

Versões recentes (5.38 a 5.60): abas no topo direito **Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes,
Fundos** (JCsFoDBSoME [3:14], L6TMT6wV-xs [0:40], q2aCXTWVrsA [0:43]). Biblioteca de fábrica pode ter só Estrutura,
Divisões, Gavetas, Portas (wsdaKZtjszg [0:26]). Versão 2011: painel "Propriedades / Agregados / Estrutura", com
Agregados > Frentes, Fundos, Gavetas, Outros (QcqJlr6WZW0 [0:42], [1:46]).

Catálogo de tipos (abas): Dormitórios, Dormitórios - Portas Embutidas, Cozinhas, Cozinhas Especiais, Cozinhas -
Portas Embutidas, Cozinhas Especiais - Portas Embutidas, Cozinhas Cava, Cozinhas Especiais - Cava, Salas
(-nGTqK7rTto [0:50]). Itens por aba: ver tabelas da seção 1.

| Aba | Sub-abas e itens vistos |
|---|---|
| **Estrutura** | Definições (Número de vãos, Largura total, Altura, Profundidade); Posição (combo: Inferior esquerda / Livre; na 2011: Esquerda / Central / Direita) com Cota anterior, Cota inferior, Cota posterior, Cota superior; Componentes (lista com caixas e valores); Movimentação (Passo inicial, Passo). |
| **Divisões > Vertical** | Cozinha: Divisórias Móveis, Divisórias Fixas, Distanciador, Sem Divisória; Com Recuo Frontal / Sem Recuo Frontal; itens "Interna/Fixa s/ ou c/ Recuo Tras [Corta Sar] [c/ Reb] 15/18mm" (Y8vvtVJUH-0 [3:14], JCsFoDBSoME [4:09]). Dormitório: Divisórias Internas Móveis, Divisórias Internas Fixas, Montante, Distanciador, Sem Divisória; "Interna c/ / s/ Recuo Fron 18mm" (-nGTqK7rTto [2:32]). Despenseiro: "Não Divide o Fundo c/ / s/ Recuo Front" (wsdaKZtjszg [2:00] e folha 1). |
| **Divisões > Horizontal** | Prateleiras Móveis, Prateleiras Fixas, Sem Prateleira (ou Prateleiras Vidro na biblioteca de fábrica). Itens: Interna c/ / s/ Recuo Fron 18mm, Corrediça, Aramada (-nGTqK7rTto [4:18]); Interna s/ / c/ Recuo Tras 15mm, Vidro s/ / c/ Recuo Tras 10mm (JCsFoDBSoME [5:40]); Vidro c/ / s/ Recuo Fron 10mm (q2aCXTWVrsA [1:54]); "Somente Divisão" (L6TMT6wV-xs [6:15]). |
| **Divisões > Inserção múltipla** | Divisão Horizontal (modelo), Divisão Vertical (modelo), Orientação Prioritária Vertical/Horizontal, grade de quadradinhos, Linhas, Colunas, Inserir (-nGTqK7rTto [4:40]). |
| **Gavetas** | Dormitório: Internas, Sapateiras, Prateleira Corrediça, Externas; "s/ CF Reta - Gaveta Interna s/ Contra Frente"; Número de gavetas; Afastadores Frontal esq/dir, Traseiro esq/dir (-nGTqK7rTto [5:12]). Cozinha: Gavetas, Gavetões, Internas, Blum; "Gaveta c/ CF - Caixa Gaveta c/ Contra Frente", "Gavetão c/ CF - Caixa Gavetão c/ Contra Frente"; Opções de frentes (Reta, Gola; menu com Reta, Lisa, Fresada, Almofada, Colonial, Bicolor, Gola, Borda Alumínio, Cava, Chanfrada, Country no frame de L6TMT6wV-xs [2:10]); Número de gavetas (Y8vvtVJUH-0 [4:26], JCsFoDBSoME [4:36], L6TMT6wV-xs [2:11]). Fábrica: Gaveta, Gaveta s/ Corpo, Gaveta Tandem Parcial c/ Blumotion (wsdaKZtjszg [2:50]). |
| **Internos** | Cabideiros (Cabideiro, Cab Extensível), Calceiros, Sapateiras, Porta Cintos/Gravatas, Pistões, Biblioteca (-nGTqK7rTto [6:18]); Biblioteca com combos Acessórios / Cozinhas / Aramados (Fruteira, 2 Cestos, Cesto Meia Lua, Cesto 3/4, Gaveta, Gaveta Pia, Gaveteiro, Porta Latas 01) (L6TMT6wV-xs [3:16]); "Inserir invertido". |
| **Portas** | Ambas, Inteira, Esquerda, Direita, Basc Inf, Basc Sup, Frente s/Gaveta (Y8vvtVJUH-0 [5:22]); modelos listados na seção 1; "Inserir invertido". Fábrica: Basculante > "Superior (7152)" (wsdaKZtjszg [3:38]). |
| **Deslizantes** | Aba visível no cabeçalho; **conteúdo não aberto** em nenhum vídeo do grupo A. |
| **Fundos** | Aba visível; conteúdo não aberto nas versões recentes. Na 2011, Agregados > Fundos existe (não lido); os itens Esquerdo/Central/Direito vistos ao lado são de **Calceiros** (QcqJlr6WZW0 [1:46]). |

---

## 4. Parâmetros (nome exato na tela, valor visto, unidade)

| Campo | Valor visto | Unidade | Fonte |
|---|---|---|---|
| Número de vãos | 1 (padrão nos tipos recentes); 2 ao abrir na 2012; 3 nos exemplos | inteiro, com setas | Y8vvtVJUH-0 [2:33], ouZEF0fKBTI [0:44] |
| Largura total | 500 (Inferior c/ Divisória, Despenseiros); 1000 (Armário, Armário Divisória sobre Base); 1500 (Portas Externas s/ Rod); largura da parede (2012) | mm (m na instalação de ouZEF0fKBTI) | Y8vvtVJUH-0 [2:33], wsdaKZtjszg [0:26], -nGTqK7rTto [2:02], q2aCXTWVrsA [0:43], ouZEF0fKBTI [0:44] |
| Altura | 700 (inferior, salas); 1350 (Despenseiros); 2500 (Armário); altura da parede (2012) | mm | idem |
| Profundidade | 550 (quase todos); 600 (Armário Divisória sobre Base) | mm | idem, L6TMT6wV-xs [4:08] |
| Posição | "Inferior esquerda" ou "Livre" (combo); Esquerda / Central / Direita (2011) | - | JCsFoDBSoME [3:14], Y8vvtVJUH-0 [2:33], QcqJlr6WZW0 [0:42] |
| Cota anterior / inferior / posterior / superior | distâncias às paredes; ex. 0 / 0 / 4350 / 1900; com Livre ficam calculadas e cinzas | mm | JCsFoDBSoME [3:14] |
| Lateral Esquerda / Lateral Direita | 15mm, 18mm (18,5 inferido na biblioteca de fábrica) | mm | L6TMT6wV-xs [4:08], q2aCXTWVrsA [0:43] |
| Laterais / Laterais Engrossuradas | marcado / desmarcado | - | Y8vvtVJUH-0 [2:33] |
| Divisória / Divisórias | marcado | - | idem |
| Base Inferior | 15mm ou 18mm, marcado | mm | JCsFoDBSoME [3:14], Y8vvtVJUH-0 [2:33] |
| Base Superior | 15mm ou 18mm; só em armário, salas e 2011, não no inferior de cozinha | mm | -nGTqK7rTto [2:02], q2aCXTWVrsA [0:43] |
| Sarrafo Frontal / Sarrafo Traseiro | 15mm, marcados (inferior de cozinha) | mm | L6TMT6wV-xs [0:40] |
| Desconto Espessura Sarrafo | marcado (inferior de cozinha, outra biblioteca) | - | Y8vvtVJUH-0 [2:33] |
| Tampo Linear | 15mm ou 18mm, desmarcado | mm | L6TMT6wV-xs [0:40], Y8vvtVJUH-0 [2:33] |
| Pés Plásticos | 150, desmarcado | mm (altura, inferido) | Y8vvtVJUH-0 [2:33] |
| Pés | 50, desmarcado (salas) | mm | q2aCXTWVrsA [0:43] |
| Rodízios | 100, desmarcado | mm | q2aCXTWVrsA [0:43] |
| Rodapés / Rodapé | marcado em armário; desmarcado no inferior; 18mm na 2011 | mm | -nGTqK7rTto [2:02], QcqJlr6WZW0 [0:42] |
| Rodapés Granito | desmarcado | - | Y8vvtVJUH-0 [2:33] |
| Fechamentos | 50, desmarcado | mm | Y8vvtVJUH-0 [2:33] |
| Vistas / Vista / Vistas (auto) | 150, desmarcado | mm | -nGTqK7rTto [2:02], wsdaKZtjszg [0:26] |
| Passo inicial / Passo (Movimentação) | 0 / 10 | mm | JCsFoDBSoME [3:14] |
| Número de gavetas | 4 (dormitório e cozinha), 2 (gavetões), 5 (2011) | inteiro | -nGTqK7rTto [5:12], Y8vvtVJUH-0 [4:26], QcqJlr6WZW0 [1:54] |
| Afastadores | 4 caixas marcadas (Frontal/Traseiro x esq/dir); 2 na 2011 (Esquerdo, Direito) | - | -nGTqK7rTto [5:12], QcqJlr6WZW0 [1:54] |
| Cota Inferior / Cota Superior (prateleira selecionada) | 327,5 / 327,5 no exemplo | mm | L6TMT6wV-xs [2:11] |
| Linhas / Colunas (inserção múltipla) | 0 / 0 | inteiro | -nGTqK7rTto [4:40] |
| Distância do cabideiro à prateleira de cima | 70 | mm | [DITO] L6TMT6wV-xs [5:38] |

Faixas (mínimo e máximo) **não foram vistas** em nenhum campo.

---

## 5. Regras observadas

1. **Divisão inicial igual**: ao mudar o número de vãos, os vãos livres ficam iguais. VISTO: 3 vãos em 2500 com 18 mm
   dão 809,3 livres cada ((2500 - 4 x 18) / 3 = 809,3) (QcqJlr6WZW0 [1:30]); 3 vãos em 2600 com 15 mm dão 846,7
   (L6TMT6wV-xs, mosaico [4:22]); DITO "fez a medida exata por igual" (L6TMT6wV-xs [4:22]).
2. **Cota do vão é editável**: clicar no vão e digitar a largura; os vizinhos absorvem a diferença
   (L6TMT6wV-xs [1:03-1:13]; VISTO 400 e 923,3 em [1:06]).
3. **Convenção das cotas dos vãos** [INFERIDO]: os rótulos acima do desenho somam a largura interna total e um deles
   inclui a espessura da divisória (QcqJlr6WZW0: 827,3 + 809,3 + 827,3 = 2464 = 2500 - 36; -nGTqK7rTto: 618 + 646 =
   1264 = 1300 - 36). A regra exata de qual cota absorve a divisória não foi explicada.
4. **Altura interna** = altura - base inferior - (base superior ou sarrafo) [e - rodapé quando há]. VISTO: 700 → 670
   (15 mm), 750 → 714 e 700 → 664 (18 mm), 800 → 764 (base inferior + superior 18 mm), 2500 → 2384 (armário com rodapé).
5. **Prateleira centralizada**: arrastar não centraliza; dois cliques no vão e dois cliques no modelo inserem no meio
   (L6TMT6wV-xs [1:29-1:51]; VISTO 327,5 / 327,5 em [2:11]).
6. **Seleção do vão**: dois cliques rápidos seleciona só o vão; Ctrl + dois cliques também usado
   (-nGTqK7rTto [5:01], Y8vvtVJUH-0 [5:12]). Status no rodapé: "Selecionado: Vão".
7. **Gavetas dividem o vão inteiro**: o número digitado reparte a altura do vão selecionado em N frentes iguais
   (VISTO 4 gavetas ocupando o vão inteiro em JCsFoDBSoME [4:36] e L6TMT6wV-xs [2:11]). Afastadores existem para a
   gaveta interna não bater na porta/dobradiça [DITO -nGTqK7rTto 5:35-5:51].
8. **Ordem portas → prateleira**: inserir a prateleira antes divide as portas em duas alturas; inserir as portas
   primeiro mantém a porta inteira [DITO JCsFoDBSoME 4:44-4:58].
9. **"Sem prateleira" / "Somente Divisão"**: divide o vão para agregados sem gerar peça, sem cortar o montante
   [DITO L6TMT6wV-xs 5:59-7:06; VISTO 6:15].
10. **Fixas x móveis**: divisórias e prateleiras fixas têm a profundidade do armário; móveis têm recuo configurável
    [DITO QcqJlr6WZW0 0:56-1:06].
11. **Recuo frontal / traseiro, Corta Sar, c/ Reb**: as divisórias de cozinha escolhem se cortam o sarrafo e se têm
    rebaixo para o fundo (nomes vistos em Y8vvtVJUH-0 [3:14] e JCsFoDBSoME [4:09]; comportamento não demonstrado).
12. **Reabrir para editar**: botão direito no armário pronto > abrir de novo o Construtor/"Editar armário"
    [DITO QcqJlr6WZW0 2:01-2:10, L6TMT6wV-xs 7:13].
13. **Aplicar x OK**: Aplicar valida sem fechar; OK fecha e insere [DITO -nGTqK7rTto 6:55-7:02].
14. **Nasce com a parede** (2012): a primeira tela vem com largura e altura da parede selecionada (ouZEF0fKBTI [0:44]);
    nas versões recentes nasce 500 x 700 x 550 ou 1000 x 2500 x 550 conforme o tipo.
15. **Torre de fornos**: não dividir com prateleira inteira; usar "Gaveta s/ Corpo" como frente fixa e prateleira solta
    dimensionada para o vão [DITO wsdaKZtjszg 2:16-3:15].
16. **Módulo único x módulos separados**: módulo único economiza uma lateral; separados são mais fáceis de montar
    [DITO JCsFoDBSoME 6:02-6:17, Y8vvtVJUH-0 0:28-0:35].

---

## 6. Lacunas (o que os vídeos do grupo A não mostram)

- **Aba Estrutura de aéreo, torre p/ eletros, gaveteiro e cantos**: só nomes no catálogo. Não li espessuras,
  componentes nem medidas padrão desses tipos (exceto o "Armário Despenseiros" da biblioteca de fábrica).
- **Largura/altura das travessas (sarrafos)** do balcão: componentes vistos (Sarrafo Frontal/Traseiro 15mm), mas a
  largura da peça não aparece em nenhum campo.
- **Recuos numéricos**: recuo de prateleira/divisória móvel, recuo do fundo, rebaixo; nenhum valor lido.
- **Fundo**: abas Fundos (recentes) e Agregados > Fundos (2011) nunca foram abertas; espessura e encaixe do fundo
  (rebaixo, sobreposto, canal) não vistos.
- **Deslizantes**: aba nunca aberta.
- **Expansão dos itens com "+"** (Laterais, Rodapés, Pés Plásticos, Fechamentos, Vistas): ninguém expandiu.
- **Altura e recuo do rodapé**: só inferido (80 mm no "Armário" de -nGTqK7rTto pela conta 2500 - 2384 - 36).
- **Comportamento das sobreposições** (Sobrepõe Base x Sobrepõe Lateral): nomes vistos, efeito não explicado.
- **Folgas de porta e de gaveta**, espessura das frentes (só 18,5 inferido em wsdaKZtjszg pela barra de status).
- **Faixas e validações** dos campos (mínimos, máximos, mensagens de erro): nada visto.
- **Aba Propriedades** da versão 2011 não foi aberta.
