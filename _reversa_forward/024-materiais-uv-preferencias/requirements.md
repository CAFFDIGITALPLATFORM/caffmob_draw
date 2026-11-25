# Requirements: Materiais, UV por face e preferências de exibição do armário

> Identificador: `024-materiais-uv-preferencias`
> Data: `2026-11-25`
> Origem: pedido do titular na rodada de auditoria de 2026-11-25 (feature 021), separado porque é pipeline de
> material/UV e tela de preferências, não correção da 021.
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o armário v2 nasce com **cor de objeto** e o modo Solid não mostra a textura; no Preview a textura depende de o
material já existir, e não há garantia de que a caixa externa, a caixa interna e a fita de borda recebam o mapa no
canto certo. As preferências recomendadas do add-on ainda oferecem "Cor por objeto" em vez de textura, e a opção
"Textura com linhas" não existe. Esta feature fecha essa lacuna: escolher a fonte de exibição (textura ou sólida),
gerar **UV por face** por tipo de peça (externa, interna, fita de borda) com o mesmo mapa em todos os modos, e
substituir a opção de cor por objeto por **Textura**, com as variantes **Somente textura** e **Textura com linhas**,
mantendo a opção "Cursos 3D" intacta.

> **Estado desta rodada:** requisitos escritos e **esclarecidos** (sessão de 2026-11-25, cinco decisões fechadas).
> **Nenhuma implementação começou**; o próximo ciclo é o `/reversa-plan`.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/addenda/017-construtor-armario-v2.md` | Peças do `armario_v2` são geradas por caixa (mesh própria por peça) e hoje não recebem UV por face. | 🟢 |
| `_reversa_forward/018-textura-uv-veio/requirements.md` | Precedente de UV/veio por componente e de material por peça; a 024 estende a regra para as faces do armário. | 🟢 |
| `caffmob_draw/hb_details.py:98` | O add-on já força `space.shading.type = 'SOLID'` e `color_type = 'OBJECT'` em fluxo de detalhes — a 024 precisa decidir se mexe nesse fluxo. | 🟢 |
| `caffmob_draw/data/properties.py` | `btm_settings` concentra as preferências de cena; as opções de exibição novas entram aqui, não em propriedades por objeto. | 🟢 |
| `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html` | Mockup de referência do construtor; a exibição do armário deve conversar com a paleta dele. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro projetista | Apresentar o móvel com o material real | Aplica a textura do MDF e vê a mesma chapa no Solid e no Preview, com a fita de borda no canto certo. |
| Projetista de interiores | Escolher a leitura visual do projeto | Alterna "Somente textura" e "Textura com linhas" para mostrar o desenho técnico sem perder o material. |
| Modelador | Não perder o fluxo já conhecido | Continua usando "Cursos 3D" e as opções existentes; nada é removido além da troca de "Cor por objeto" por "Textura". |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 (Fonte de exibição: textura em vez de cor de objeto):** o armário v2 nasce com a **textura padrão do
   add-on (MDF claro)** aplicada a todas as peças sem material; peças com material definido mantêm o seu. No Preview
   vale o material; no **Solid** o `color_type` passa a `'TEXTURE'` (cor média da textura) em todas as peças — não
   uma cor de objeto arbitrária, nem `OBJECT` forçado pelo fluxo de detalhes. A opção de preferências "Cor por
   objeto" deixa de existir e passa a se chamar **"Textura"**. 🟢
   - Origem no legado: `caffmob_draw/hb_details.py:98`; mockup do construtor.
   - Tipo: alterada
2. **RN-02 (Variantes "Somente textura" e "Textura com linhas"):** a opção "Textura" deve oferecer exatamente duas
   variantes: **Somente textura** (material puro, sem linhas de aresta) e **Textura com linhas** (material + **todas as arestas visíveis na viewport**, pelo interruptor **Linhas** que já existe — `overlay.show_wireframes`; não é contorno exclusivo das chapas). A opção **"Cursos 3D"** — confirmada pelo titular, em 2026-11-25, como o checkbox **"Turn Off 3D Cursor"** (`turn_off_3d_cursor`, `ops.py:54`) — permanece e não pode ser escondida nem removida por essa mudança. 🟢
   - Origem no legado: mockup do construtor; preferências recomendadas do add-on.
   - Tipo: nova
3. **RN-03 (UV por face com o mesmo mapa em todos os modos):** ao aplicar textura, cada face deve receber o mapa do
   canto devido conforme o tipo de peça — **caixa externa**, **caixa interna** e **fita de borda** — e o mesmo UV deve
   valer para Solid, Preview e render, sem costura deslocada nem textura esticada. A **fita de borda tem UV próprio**:
   o comprimento da fita corre no eixo **U** ao longo da aresta e a largura da fita ocupa o eixo **V**. 🟢
   - Origem no legado: `_reversa_forward/018-textura-uv-veio/requirements.md`; geração de caixa do `armario_v2`.
   - Tipo: nova
4. **RN-04 (Cenas e armários já existentes):** armários salvos com "Cor por objeto" são migrados **uma única vez**, na
   abertura da cena, para a textura padrão do add-on, com aviso ao usuário; a migração é marcada para não repetir a
   cada abertura. Nada quebra nem apaga material do usuário. 🟢
   - Origem no legado: `btm_settings` e preferências já gravadas em cenas.
   - Tipo: nova

## 5. Fora de escopo (nesta feature)

- Alterar o gerador de geometria do armário (a 023/017 já o fazem); aqui só material, UV e exibição.
- Importar catálogo novo de texturas de fabricante (feature 014).
- Redesenhar o painel do construtor ou a janela (feature 023).

## 6. Esclarecimentos

### Sessão 2026-11-25

- **Q:** Qual é a fonte da textura quando o armário ainda não tem material?
  **R:** Textura padrão do add-on (MDF claro) aplicada automaticamente em todas as peças; peças com material definido
  mantêm o seu.
- **Q:** No modo Solid, a textura deve aparecer de que forma?
  **R:** Cor média da textura (`color_type = 'TEXTURE'`) em todas as peças — o `hb_details.py` deixa de forçar `OBJECT`
  nesse fluxo.
- **Q:** "Textura com linhas": quais arestas são desenhadas?
  **R:** Todas as arestas de cada peça (o contorno de cada chapa), no estilo do mockup.
- **Q:** Como mapear a fita de borda?
  **R:** UV próprio da fita: comprimento corre no eixo U ao longo da aresta e a largura da fita ocupa o eixo V.
- **Q:** O que acontece com armários já salvos com "Cor por objeto"?
  **R:** Migram uma única vez, na abertura da cena, para a textura padrão, com aviso e marca de migração.

### Sessão 2026-11-25 — segunda rodada

> Três das quatro perguntas abertas pelo `/reversa-audit` foram respondidas pelo titular; a quarta segue em §7.
> Nenhum código foi tocado nesta rodada.

- **Q:** "Cursos 3D" — qual controle é, para não removê-lo por engano?
  **R:** É o checkbox **"Turn Off 3D Cursor"** (`turn_off_3d_cursor`, `caffmob_draw/ops.py:54`), do diálogo
  `caffmob.set_recommended_settings`. **Preservar intacto**: só o controle de cor (`turn_on_object_color_type`,
  `ops.py:39`) muda.
- **Q:** O `color_type` vale para a viewport inteira — qual o escopo aceito?
  **R:** **Global**, como no clarify: paredes, portas e armários das bibliotecas herdadas (que usam `obj.color`,
  inclusive `cabinet_color`) passam a mostrar a cor média do material no Solid.
- **Q:** "Textura com linhas" — quais arestas desenhar?
  **R:** Reusar o **interruptor Linhas já existente** (`Scene.btm_view_lines` → `overlay.show_wireframes`): arestas de
  todos os objetos, sem contorno exclusivo das chapas e sem objeto de wireframe novo.

## 7. Lacunas

Resta **uma** dúvida, aberta pelo `/reversa-audit` e ainda não respondida pelo titular (as outras três foram fechadas
na segunda rodada de 2026-11-25, em §6):

1. **`exibicao_armario` vs. `Scene.btm_view_mode` (T009/T010):** manter os dois níveis — a preferência do add-on como
   padrão de fábrica e `Scene.btm_view_mode` como estado gravado no arquivo — ou um só? A preferência não consegue
   herdar default em `bpy.props` (ver T002), e o controle "Sólido·Textura" da barra lateral já grava o estado na cena.
   *Decide a forma final de T009 e o destino de T010.*

Nenhuma implementação começou; o próximo ciclo é `/reversa-clarify` (uma pergunta) e depois `/reversa-coding`.

## 8. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-25 | Versão inicial gerada na auditoria da feature 021 (lacuna de material/UV/preferências separada como candidata) | reversa |
| 2026-11-25 | `/reversa-clarify`: cinco decisões integradas (textura padrão MDF, Solid `TEXTURE`, linhas em todas as arestas, UV próprio da fita, migração única com aviso); 0 dúvidas restantes | reversa |
| 2026-11-25 | `/reversa-clarify` (2ª sessão): três respostas do titular integradas ("Cursos 3D" = `turn_off_3d_cursor`; `color_type` global; linhas pelo interruptor existente); resta 1 dúvida (`exibicao_armario` vs. `Scene.btm_view_mode`) | reversa |
