# Changelog do CAFFMob Draw

## 1.33.0 — 2026-11-26

### Biblioteca

- Card branco de detalhe do módulo antes de inserir: clicar num módulo da grade abre um card claro com o nome, o
  ambiente, largura, altura e profundidade pré-preenchidos pelo catálogo e pelos padrões do Padrão de Dimensões, mais o
  seletor de ambiente (Cozinha, Banheiro, Dormitório, Sala, Home office) e os botões Inserir e Cancelar
  (`library_panel/detail_core.py`, `library_panel/ops_detail.py`, `library_panel/draw.py`, `library_panel/props.py`).
- Confirmar passa as medidas e o ambiente escolhidos para `caffmob.library_insert_model`, que agora aceita
  `width_mm`/`height_mm`/`depth_mm` e os repassa ao construtor de armários; módulos de preset sem variação continuam
  usando os valores do JSON (`library_panel/popover.py`).
- Validação contra o Padrão de Dimensões: máximos do módulo, faces de chapa (largura × altura, largura × profundidade,
  altura × profundidade) contra a chapa máxima do fornecedor e espessura da lateral. Medida inválida é recusada com
  mensagem no card e nada é criado; o filtro de acervo por ambiente e a galeria do Editor de Armário V2 continuam
  intactos.

### Como a numeração foi calculada

`1.32.0 + 1 feature entregue = 1.33.0`, mantendo a convenção do repositório de uma minor por entrega.

## 1.32.0 — 2026-11-25

Primeiro incremento desde a 1.27.0 (2026-11-23). Entre uma e outra entraram cinco features com código no pacote, sem
que a versão do manifesto acompanhasse — o que este lançamento corrige.

### Entrou desde a 1.27.0

- **020 — Conversão em armário:** leitura da seleção como um móvel, papéis por peça (laterais, bases, fundo e porta),
  armário v2 no envelope das peças, origem não destrutiva e geração sob demanda (`armario_v2/ponte.py`,
  `armario_v2/converter.py`).
- **021 — Plano de corte e camadas:** plano de corte em camadas, coleções de cena organizadas e conversão em gaveteiro
  (`cutting/`, `data/layers.py`).
- **022 — Frente do Mover Sobre:** a frente do objeto passa a ser considerada no encoste e no movimento.
- **023 — Janela do Construtor de Armários:** janela própria com preview frontal e corte lateral, painel de 7 abas,
  fila de pedidos com um passo de desfazer e edição do armário v2 (`armario_v2/window.py`, `canvas2d/`).
- **024 — Materiais, UV e preferência de exibição:** textura MDF clara empacotada, UV por face com veio, preferência
  de exibição por armário e aviso de migração (`armario_v2/mdf_core.py`, `face_uv_core.py`, `exibicao.py`).

### Biblioteca

- Acervo por ambiente: o catálogo de modelos e presets declara `environments` e a grade da Biblioteca mostra só o que
  pertence à categoria aberta (`library_panel/models_core.py`, `library_panel/draw.py`,
  `data/library_models.json`).
- Categoria fixa **Dormitório** (linha `DOR`), que faltava para o acervo de dormitório ficar acessível sem criar
  categoria manual (`library_panel/categories_core.py`).
- Módulos de dormitório, banheiro, sala e escritório no catálogo: roupeiro, cômoda, gabinete e espelheira de banheiro,
  buffet e estante de sala, armário de arquivo.

### Como a numeração foi calculada

`1.27.0 + 5 features entregues (020, 021, 022, 023, 024) = 1.32.0`, mantendo a convenção do repositório de uma minor
por entrega. A 019 (`redimensionar-e-colisao`) continua pausada, com apenas `requirements.md`, e não entra na conta.

## 1.27.0 — 2026-11-23

Textura por UV, veio em graus e conta-gotas por parte (feature 018).
