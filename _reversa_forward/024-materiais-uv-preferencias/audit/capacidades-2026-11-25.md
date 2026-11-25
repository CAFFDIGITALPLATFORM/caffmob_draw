# Auditoria de capacidades: conversão em chapa, versão, galeria, categorias, textura e montagem por peças

> Data: 2026-11-25
> Escopo: perguntas do titular sobre o addon em `HEAD = 8e0438f8` (versão 1.27.0)
> Modo: **leitura estrita**. Nenhum arquivo de código, `requirements.md`, `roadmap.md`, `actions.md` ou `todo.md`
> foi alterado. Este relatório é o único artefato escrito.
> Leitura de código: `caffmob_draw/cutting/part_extractor.py`, `cutting/nesting.py`, `armario_v2/ops.py`,
> `armario_v2/converter.py`, `armario_v2/ponte.py`, `armario_v2/menu.py`, `ui/context_menu.py`,
> `library_panel/draw.py`, `library_panel/style.py`, `library_panel/ops_cabinet.py`, `library_panel/popover.py`,
> `library_panel/replace_core.py`, `library_panel/ops_drag.py`, `texture_library/apply.py`, `cabinet_editor/gallery_core.py`,
> `cabinet_editor/structures_core.py`, `data/cabinet_structures.json`, `data/library_models.json`, `data/layers.py`,
> `data/dimension_schema.py`, `blender_manifest.toml` e o histórico Git.

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 5 |
| MEDIUM | 2 |
| LOW | 1 |

**Veredito por pergunta do titular**

| # | Pergunta | Veredito |
|---|---|---|
| 1 | Qualquer peça vira chapa de MDF respeitando espessura/largura/tamanho máximos do Configurador | 🟡 **Parcial** |
| 2 | A versão do addon acompanha o volume de mudanças | 🔴 **Não** |
| 3 | A janela tem inferiores, altos e superiores baixos/médios/altos | 🔴 **Não** |
| 4 | Módulos pesquisáveis em fundo branco, dimensões e categoria antes de arrastar; categorias como coleção em `Marcenaria` | 🔴 **Não** |
| 5 | Trocar a textura de tudo o que está em uso na cena ativa pela janela | 🔴 **Não** |
| 6 | Montar armário peça a peça pelo botão direito, preservando a posição atual | 🟡 **Parcial** |
| 7 | Galeria totalmente compatível com o editor v2 e a janela nova | 🔴 **Não** |

Nenhuma dessas respostas pode ser declarada positiva sem implementação: o pedido "faça todas serem positivas" é
tratado aqui como **lista de trabalho**, não como mudança de redação do relatório.

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|---|---|---|---|---|
| A001 | HIGH | Versão / release | `version = "1.27.0"` está congelada desde 2026-11-23 (`81814b5b`, feature 018). Depois dela vieram **23 commits**, incluindo as features 019, 021 (plano de corte em camadas), 022 (frente do Mover Sobre), 023 (janela do construtor) e 024 (textura MDF/UV/preferência), sem nenhum incremento. Não há tags Git | `caffmob_draw/blender_manifest.toml:4`; `git log 81814b5b..HEAD` |
| A002 | HIGH | Janela / catálogo | A galeria de estruturas de caixa (feature 015) não separa inferiores, altos e superiores baixos/médios/altos. As abas são **ambientes** (`Cozinhas`, `Dormitórios`, de `cabinet_structures.json`), e os grupos internos são só três (`INFERIOR`, `SUPERIOR`, `DESPENSEIRO`). O catálogo tem 17 estruturas, sendo **2 superiores**; "superior baixo/médio/alto" existe apenas como dimensão no Configurador | `cabinet_editor/gallery_core.py:28,53`; `data/cabinet_structures.json`; `data/dimension_schema.py` (`upper_low_height`, `upper_mid_height`, `upper_high_height`) |
| A003 | HIGH | Biblioteca / categorias | A aba Blocos mostra **os mesmos 5 modelos + 10 presets em toda categoria** (Cozinha, Banheiro, Sala, Home office). A categoria escolhida só troca a `line` usada para o tamanho padrão; não filtra o acervo. Não há hoje catálogo por ambiente: banheiro e sala recebem os mesmos balcões e torres da cozinha | `library_panel/draw.py:249,278,284`; `library_panel/categories_core.py:31-37` |
| A004 | HIGH | Texturas | Não existe ferramenta de **substituir textura em uso**. `grep -rn "Substituir textura"` em `caffmob_draw/` não devolve nada. O que existe com nome parecido é **"Substituir pelo selecionado"**, que troca o *modelo* de uma porta, janela ou móvel preservando medidas — não lê as texturas da cena nem recoloriza peças. Aplicar textura é gesto por alvo (arrastar/soltar sobre uma peça, frente, módulo ou objeto) | `library_panel/replace_core.py`; `library_panel/draw.py:57`; `texture_library/apply.py`; `library_panel/ops_drag.py` |
| A005 | HIGH | Conversão em armário | A conversão peça a peça existe (marcar papel → converter), mas **não está no botão direito**: o submenu "Converter em" do menu de contexto oferece apenas Gaveteiro e "Armário (Construtor v2)" para módulo de biblioteca. Marcar papel e converter agora ficam na caixa do painel lateral. A posição preservada é a **caixa envolvente** (a raiz nasce no envelope e as peças são regeradas pelo `spec`), não a posição de cada peça; espessuras são encaixadas em 6/15/18/25 mm e medidas inviáveis são recusadas pela validação, não corrigidas | `armario_v2/ponte.py:339,382,513`; `ui/context_menu.py:60-70`; `armario_v2/converter.py:31` (`mm_no_enum`); `armario_v2/ponte.py:396-433` |
| A006 | HIGH | Galeria ↔ v2 | A galeria insere móveis pelo construtor **015** (`caffmob.cabinet_builder`, `cabinet_editor`), não pelo `armario_v2`. A janela nova da 023 edita `btm_armario`. Existe ponte de módulo de biblioteca para v2 ("Gerar pelo motor novo"), mas ela é manual e não cobre os modelos prontos da galeria; a galeria não é, portanto, "totalmente compatível" | `library_panel/popover.py:63`; `library_panel/ops_cabinet.py`; `armario_v2/ponte.py:458` |
| A007 | MEDIUM | Corte / chapa | Toda peça da cena entra na lista de corte com material e espessura vindos do Configurador (inclusive geometria livre, escadas, gaveteiros, Promob, armário v2), o que atende "qualquer peça vira MDF". Mas peça maior que a chapa **não é dividida nem convertida**: é marcada `EXCEEDS_LENGTH/WIDTH` e sai como não posicionada, com o motivo "excede a área útil". O limite aplicado por componente é `max_length/max_width` do componente; o máximo global só semeia o contrato do armário v2 | `cutting/part_extractor.py:23,94-113`; `cutting/nesting.py:204`; `armario_v2/ops.py:149-151` |
| A008 | MEDIUM | Estrutura de cena | Categorias/ambientes **não são coleções do Blender**. `data/layers.py` cria apenas `Arquitetura` (com Parede/Piso/Teto/Aberturas) e `Marcenaria`; nenhuma subcoleção por categoria é criada, e o `btm_room_uid` aparece só como campo exportado no JSON de corte | `data/layers.py:11,56`; `cutting/part_extractor.py:126` |
| A009 | LOW | Visual | O painel da Biblioteca é **escuro** (`SURFACE #1A1B1E`), não branco. A busca existe e a categoria é escolhida antes do arraste, mas **as dimensões não são definidas antes de arrastar**: o modelo solto usa o Padrão de Dimensões; só o diálogo "Criar armário" pede tipo/largura/montagem/linha — e ele hoje é desviado para a janela do construtor v2 | `library_panel/style.py:18`; `library_panel/ops_cabinet.py:48-55`; `library_panel/draw.py` (busca e categorias) |

## O que já está correto (verificado)

- **Peça de qualquer origem no corte**: `extract_production_parts` cobre módulos CAFFMob, bibliotecas herdadas, geometria
  livre, escadas, gaveteiros, armário v2 e Promob (`cutting/part_extractor.py:94-113`).
- **Material MDF como padrão** e espessura por componente vindos do Configurador (`part_extractor.DEFAULT_MATERIAL`,
  `thickness_lookup`); limite de chapa por componente é aplicado (`limit_status`).
- **Máximo global do Configurador alimenta o contrato de chapas do armário v2** (maior com maior, `armario_v2/ops.py:149`).
- **Busca e categorias na Biblioteca**: campo de busca com filtro por nome (`draw.block_entries`), coluna de categorias
  fixas e do usuário (`sidebar_categories`) e aba Texturas/Blocos.
- **Substituição preservando medidas** de portas, janelas e móveis (`replace_core.plan_replacement`), com validação de
  família e de faixa dimensional.
- **Conversão não destrutiva**: as peças de origem ficam na cena; a raiz do armário nasce no envelope das peças e o
  resultado é um armário v2 editável (abas, Gerar, ajustes), com `UNDO` nos operadores.
- **Disciplina de versão até 1.27.0**: o histórico mostra incremento por entrega (1.1.1 → 1.27.0), então a numeração
  não é arbitrária — ela só parou de ser atualizada nas últimas seis features.

## O que falta para cada resposta virar "sim"

1. **Chapa (A007)**: decidir e implementar a política de peça maior que a chapa — dividir com junta/veio declarado,
   ou recusar na origem com ação de correção. Hoje o sistema só informa.
2. **Versão (A001)**: bump coerente com 019–024 (minor, pelo padrão do repositório), tag e nota de release; criar a
   etapa "versão" no fecho de feature para não repetir o atraso.
3. **Galeria por classe (A002)**: abas ou filtros Inferior / Alto / Superior baixo / médio / alto, com estruturas
   faltantes no catálogo (hoje 2 superiores), mantendo ambiente como segundo eixo.
4. **Acervo por categoria (A003)**: campo de ambiente/linha no catálogo de modelos e presets + filtro na grade; sem
   isso, Cozinha e Banheiro continuam idênticos.
5. **Tema e dimensões antes do arraste (A009)**: tema claro opcional (ou decidir manter o escuro e registrar a
   decisão) e diálogo de dimensões no clique/arraste do bloco.
6. **Substituir textura (A004)**: inventário das texturas em uso na cena ativa, lista com a atual marcada e ação de
   troca em lote por escopo de cena, com um passo de desfazer.
7. **Conversão por botão direito (A005)**: levar "Marcar peça como…" e "Converter agora" ao menu de contexto, decidir
   preservação de posição peça a peça (hoje só o envelope) e o que fazer com espessura fora do enum.
8. **Galeria no v2 (A006)**: inserir modelos prontos já como `btm_armario` (ou abrir a janela da 023 a partir da
   galeria), aposentando o caminho `cabinet_builder` para o fluxo novo.
9. **Categorias como coleções (A008)**: subcoleções de `Marcenaria` por categoria/ambiente, com migração dos objetos
   existentes e regra de não renomear coleção do usuário.

## Encerramento

- `requirements.md`, `roadmap.md`, `actions.md`, `todo.md` e o código **não foram alterados**.
- Correção de qualquer item acima é trabalho de `/reversa-forward` (ou `/reversa-clarify` para as decisões abertas:
  política de peça grande, preservação de posição peça a peça, tema claro/escuro).
- Nada aqui autoriza declarar as sete perguntas como positivas: cinco são lacunas de capacidade e duas são parciais.
