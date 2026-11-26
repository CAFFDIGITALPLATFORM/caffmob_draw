# Requirements: Janela do plano de corte, medição de malha e controle de arestas

> Identificador: `027-janela-plano-corte-e-medicao-malha`
> Data: `2026-11-26`
> Feature anterior: `026-paridade-total-construtor-biblioteca` (fechada, `v1.35.0`)
> Fontes: pedido direto do titular nesta rodada (três blocos `/reversa-requirements` e um `/reversa-debugger`).

## 1. Resumo

A 026 fechou a paridade do Construtor e da Biblioteca. Esta feature trata o próximo lote pedido pelo titular:
o plano de corte deixa de ser o sistema antigo e passa a abrir uma janela própria; nasce a janela
**V-Ray Mesh Measure**; o viewport ganha controle de arestas (linha preta espessura variável e modo
“só textura, zero aresta”); e as propriedades de item passam a aplicar em todos os selecionados quando a
preferência está ligada. O defeito da coleção de câmeras foi corrigido e provado nesta rodada (RF-05).

## 2. Escopo

### 2.1 Entregue e provado nesta rodada

| ID | Função | Critério de aceite | Estado |
|----|--------|--------------------|--------|
| RF-05 | Coleção de câmeras | O gerenciador cria **uma** coleção `CAMERAS`, dá a ela uma cor de etiqueta aleatória, adota as câmeras já existentes que ainda não foram organizadas, reaproveita a coleção antiga `Câmeras do Promob` em vez de duplicá-la, e põe a nova câmera dentro dela. | ✅ provado (`tests/blender_cameras_colecao.py`, 27/27) |
| RF-05b | Câmera sem rastreador | Nenhuma câmera cria Empty nem restrição Track To: o alvo é um ponto guardado na própria câmera (`btm_camera_alvo`), e a câmera é orientada por código. Cenas antigas com Empty alvo são migradas na primeira leitura: o Empty vira ponto e é removido. Altura do alvo, Atualizar pela vista e Percorrer continuam funcionando pelo ponto. | ✅ provado (`tests/blender_cameras_colecao.py`, 27/27) |

### 2.2 Especificado, não implementado

| ID | Função | Critério de aceite |
|----|--------|--------------------|
| RF-01 | Plano de corte em janela | O sistema antigo de plano de corte não é mais o caminho de entrada; a ação abre uma janela no estilo do editor de parede, com as peças, chapas e aproveitamento desenhados nela. |
| RF-02 | Janela V-Ray Mesh Measure | Janela própria que: detecta a malha selecionada ou mostra conta-gotas + aviso quando não há seleção; alterna opaco/raio-X; lista as partes soltas como camadas e mostra as medidas de cada uma; câmera 3D orbitando o objeto com perspectiva e ortográfica; snap configurável nas extremidades do objeto e de cada parte; cor sólida por parte; representações Aramado, Linhas Ocultas, Sólido, Raio-X e Material; medidas manuais por arraste entre extremidades; unidade absoluta ou arredondada em cm/mm/m; visualização de impressão com tipos de folha; criação de views com badge e controle de tamanho/proporção na área de impressão. |
| RF-03 | Arestas no viewport | A visualização com linha mostra aresta preta forte de 0,2 px com espessura ajustável pelo usuário; a visualização “somente textura” esconde aresta **e** vértice, deixando a cena limpa. |
| RF-04 | Aplicar em todos os selecionados | Preferência (padrão ligada): com vários objetos selecionados, as propriedades de item mostram o valor comum, ficam vazias com `?` quando divergem (dica no hover), e ao definir um valor o sistema pergunta “Você está prestes a aplicar transformação em todos os objetos ativos: Confirma? Sim/Não”, aplica em todos e registra um passo de desfazer. |

### 2.3 Preservação

| ID | Requisito |
|----|-----------|
| RF-06 | O fluxo 025 continua: criar armário abre a viewport; Aplicar pergunta Escolher/Cursor 3D; caixa de arame, setas, clique, Esc e Cursor 3D sem regressão. |
| RF-07 | A paridade da 026 continua (toolbar, export, titlebar, abas, menu, medida, arraste, cutlist, Apenas Laterais, Light/Dark, Biblioteca). |
| RF-08 | i18n sem chave ausente; `check_api.py` sem API desconhecida; smoke 017 OK. |

## 3. Requisitos não funcionais

- **Plataforma:** Blender 5.2; `bpy`/`gpu`/`blf` só em funções de desenho; `check_api.py` obrigatório.
- **Desfazer:** RF-01, RF-02 e RF-04 empurram passo de desfazer; RF-03 é só desenho.
- **Custo:** RF-02 é 3D interativo na GPU, não LLM; nenhuma chamada de token. O risco é de quadro, não de API.
- **Aparência:** tokens do documento; o add-on não repinta o chrome nativo do Blender.
- **i18n:** toda string nova tem `pt_BR` e `en_US`.

## 4. Cenários Gherkin

```gherkin
Cenário: Coleção de câmeras
  Dado uma cena com câmeras soltas na coleção mestre
  Quando crio uma câmera pelo Gerenciar câmeras
  Então existe uma única coleção CAMERAS com cor de etiqueta
  E todas as câmeras estão dentro dela
  E nenhuma coleção "Câmeras do Promob" sobra
  E nenhum Empty nem restrição Track To foi criado

Cenário: Plano de corte em janela
  Dado um projeto com peças
  Quando peço o plano de corte
  Então abre uma janela própria, sem o sistema antigo
  E as peças aparecem desenhadas com o aproveitamento

Cenário: Medir uma malha
  Dado que selecionei uma malha com partes soltas
  Quando abro o V-Ray Mesh Measure
  Então vejo as partes como camadas e as medidas de cada uma
  E posso orbitar em perspectiva e em ortográfica, com snap configurável

Cenário: Aplicar em todos os selecionados
  Dado três armários selecionados com larguras diferentes
  Quando abro as propriedades de item
  Então a largura aparece vazia com "?"
  E ao definir 800 mm o sistema pede confirmação e aplica nos três, com desfazer
```

## 5. Fora de escopo

Nada foi declarado fora de escopo pelo titular. RF-01 a RF-04 estão **pendentes**, não fora de escopo:
a matriz desta feature tem linhas abertas e por isso a auditoria dela **não** é 0/0/0/0.

## 6. Definição de pronto

Matriz `RF-01..RF-08` sem linha pendente ou bloqueada; provas executadas na rodada; i18n 3/3; `check_api.py` OK;
regressão 025/023/012/detalhe/smoke; versão/CHANGELOG; commit local sem push.
