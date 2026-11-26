# Requirements: Paridade restante do Construtor e padrão completo da Biblioteca

> Identificador: `026-paridade-total-construtor-biblioteca`
> Data: `2026-11-26`
> Feature anterior: `025-criacao-posicionamento-armario` (fechada, `v1.34.0`)
> Fontes: `mockup_construtor_armarios.html`; `docs/Caff+Mob+Biblioteca+Mockup.tar.gz`;
> `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`; auditorias 023/025.

## 1. Resumo

A 023 entregou o núcleo da janela, mas deixou dez funções do mockup fora da paridade. A 025 entregou
Criar→Aplicar→Escolher/Cursor 3D e a paleta Light. A 026 fecha as dez funções restantes e aplica o padrão
documentado da Biblioteca (categorias, tema, grade de modelos e alvo de toque), preservando o fluxo 025.

## 2. Escopo

### 2.1 Construtor (dez funções que faltavam)

| ID | Função | Critério de aceite |
|----|--------|--------------------|
| RF-01 | Toolbar completa | A janela expõe montagem, limpeza, vistas, cotas, portas, abrir/fechar tudo, laterais, tema, painel, plano de corte e export; cada botão executa operador real. |
| RF-02 | Export JSON | Exporta spec, peças e cutlist agregada; o arquivo tem `schema: caffmob.armario.v1`, `armario`, `pecas`, `cutlist` e `totais`. |
| RF-03 | Titlebar | O cabeçalho mostra título, dimensões e ações de contrato/export/tema, mantendo as ações de janela do Blender. |
| RF-04 | Abas horizontais | As sete abas ficam em uma única linha horizontal, com a ativa deprimida e o nome da aba ativa visível. |
| RF-05 | Menu de contexto | Botão direito sobre a peça abre menu com Duplicar, Medida, Espelhar e Apagar; a duplicata sobrevive ao Gerar. |
| RF-06 | Popover de medida | Um diálogo altera largura/altura/profundidade em mm, regenera o armário e mantém o estado sujo para Cancelar. |
| RF-07 | Arraste de peças | Press→move→release desloca a peça no preview, grava `dx/dy/dz` no ajuste e não dispara com clique parado. |
| RF-08 | Cutlist | O painel de peças lista as medidas e exporta a cutlist no JSON; a soma das quantidades cobre todas as peças. |
| RF-09 | Apenas Laterais | A ação liga as duas laterais, desliga base/fundo e gera somente chapas `LATERAL`. |
| RF-10 | Light/Dark | O preview alterna os tokens Light/Dark e repinta as peças; a Biblioteca alterna seus tokens e persiste na sessão. |

### 2.2 Biblioteca (documento vence o código)

| ID | Função | Critério de aceite |
|----|--------|--------------------|
| RF-11 | Categorias do documento | A navegação é Armários, Portas, Janelas, Armários autorais; Armários mostra o acervo de armários, Portas/Janelas as aberturas. |
| RF-12 | Grade de modelos 2×3 | A aba Blocos usa duas colunas fixas; seis modelos ocupam três linhas. A grade de texturas continua responsiva. |
| RF-13 | Tema da Biblioteca | O botão de tema alterna Light/Dark nos tokens do painel; o padrão é Light. |
| RF-14 | Alvo de toque 44 px | Botões e abas do cabeçalho têm área de acerto mínima de 44 px, sem aumentar o desenho. |

### 2.3 Preservação

| ID | Requisito |
|----|-----------|
| RF-15 | O fluxo 025 continua: Criar armário abre a viewport; Aplicar pergunta Escolher/Cursor 3D; caixa de arame, setas, clique, Esc e Cursor 3D sem regressão. |
| RF-16 | A janela 023 continua com fila/modal, seleção múltipla, lote, memória por cena e validação GEO. |
| RF-17 | O card de detalhe da Biblioteca continua inserindo por clique e arraste, com recusa de chapa e medidas. |
| RF-18 | i18n sem chave ausente; `check_api.py` sem API desconhecida; smoke 017 OK. |

## 3. Requisitos não funcionais

- **Plataforma:** Blender 5.2; `bpy`/`gpu`/`blf` só nas funções de desenho. `check_api.py` deve passar.
- **Desfazer:** operações que mudam a cena empurram um passo de desfazer; arraste só grava no release.
- **Dados:** a duplicata é persistida em `btm_armario.ajustes.duplicada`; estado de vista/tema é de sessão.
- **Aparência:** tokens do documento; tema nativo do Blender não é repintado por add-on; as áreas desenhadas pelo
  add-on (preview e Biblioteca) seguem o alternador.
- **Compatibilidade:** nada de assinatura de API “de memória”; usar `docs/rag/`.
- **i18n:** toda string nova de UI tem `pt_BR` e `en_US`.

## 4. Cenários Gherkin

```gherkin
Cenário: Exportar o armário e a cutlist
  Dado um armário montado na janela 026
  Quando executo Exportar JSON e escolho um arquivo
  Então o JSON tem schema, spec, peças e cutlist, e a soma das quantidades é igual ao número de peças

Cenário: Arrastar uma peça
  Dado uma peça selecionada no preview frontal
  Quando pressiono, movo mais de 3 px e solto
  Então a peça desloca em X/Z e o ajuste dx/dz fica gravado para o Gerar

Cenário: Apenas Laterais
  Dado um armário com caixa completa
  Quando executo Apenas Laterais
  Então as duas laterais ficam ativas, base/fundo ficam inativos e só chapas LATERAL são geradas

Cenário: Menu de contexto e medida
  Dado uma peça selecionada
  Quando abro o menu de contexto e escolho Medida
  Então o popover aceita a nova medida, regenera e mantém o armário sujo

Cenário: Tema e biblioteca
  Dado a Biblioteca aberta
  Quando clico no botão de tema
  Então os tokens mudam para Dark e o desenho seguinte usa a paleta escura; o segundo clique volta ao Light

Cenário: Categorias do documento
  Dado a coluna da Biblioteca aberta
  Então a ordem é Armários, Portas, Janelas, Armários autorais
  E Armários mostra modelos de armário; Portas mostra aberturas de porta
```

## 5. Fora de escopo

Nada do mockup ou dos pacotes da Biblioteca foi declarado fora de escopo. As funções já entregues e auditadas em
023/025 são preservadas por regressão; os dez itens acima são os deltas desta feature.

## 6. Definição de pronto

Matriz `C01–C10`, `L01–L04` e `F01` sem linha pendente/bloqueada; provas executadas nesta rodada; i18n 3/3;
`check_api.py` OK; regressão 025/023/012/detalhe/smoke; versão/CHANGELOG; commit local sem push.
