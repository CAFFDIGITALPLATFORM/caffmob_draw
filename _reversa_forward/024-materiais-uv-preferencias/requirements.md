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

> **Estado desta rodada:** requisitos escritos; **nenhuma implementação começou**. As decisões abaixo marcam
> `[DÚVIDA]` e estão listadas em `## Esclarecimentos pendentes` — o ciclo para aqui, antes do `/reversa-clarify`.

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

1. **RN-01 (Fonte de exibição: textura em vez de cor de objeto):** o armário v2 deve exibir a **textura** do material
   no modo Preview e uma cor derivada da textura no Solid — não uma cor de objeto arbitrária. A opção de preferências
   "Cor por objeto" deixa de existir e passa a se chamar **"Textura"**. 🟡 🔴 `[DÚVIDA]`
   - Origem no legado: `caffmob_draw/hb_details.py:98`; mockup do construtor.
   - Tipo: alterada
2. **RN-02 (Variantes "Somente textura" e "Textura com linhas"):** a opção "Textura" deve oferecer exatamente duas
   variantes: **Somente textura** (material puro, sem linhas de aresta) e **Textura com linhas** (material + contorno
   de aresta do componente, como no mockup). A opção **"Cursos 3D"** permanece e não pode ser escondida nem removida
   por essa mudança. 🟡 🔴 `[DÚVIDA]`
   - Origem no legado: mockup do construtor; preferências recomendadas do add-on.
   - Tipo: nova
3. **RN-03 (UV por face com o mesmo mapa em todos os modos):** ao aplicar textura, cada face deve receber o mapa do
   canto devido conforme o tipo de peça — **caixa externa**, **caixa interna** e **fita de borda** — e o mesmo UV deve
   valer para Solid, Preview e render, sem costura deslocada nem textura esticada. 🟡 🔴 `[DÚVIDA]`
   - Origem no legado: `_reversa_forward/018-textura-uv-veio/requirements.md`; geração de caixa do `armario_v2`.
   - Tipo: nova
4. **RN-04 (Cenas e armários já existentes):** armários salvos com "Cor por objeto" não podem quebrar ao abrir; é
   preciso definir se a migração aplica textura padrão, mantém a cor anterior ou pergunta ao usuário. 🟡 🔴 `[DÚVIDA]`
   - Origem no legado: `btm_settings` e preferências já gravadas em cenas.
   - Tipo: nova

## 5. Fora de escopo (nesta feature)

- Alterar o gerador de geometria do armário (a 023/017 já o fazem); aqui só material, UV e exibição.
- Importar catálogo novo de texturas de fabricante (feature 014).
- Redesenhar o painel do construtor ou a janela (feature 023).

## 6. Esclarecimentos pendentes

> Nenhuma pergunta abaixo foi respondida. O ciclo **para aqui**; `/reversa-clarify` deve ser executado pelo titular.

1. **Qual é a fonte da textura quando o armário ainda não tem material?**
   a) textura padrão do add-on (MDF claro) aplicada automaticamente em todas as peças
   b) mantém o material do contrato de chapas, e só quem não tiver material cai na textura padrão
   c) pergunta por peça, sem padrão
   d) Resposta livre
   *Bloqueia:* RN-01 e o critério de aceite de "armário novo já sai texturizado".

2. **No Solid, a textura deve aparecer de que forma?**
   a) cor média da textura (`color_type = 'TEXTURE'`) em todas as peças
   b) cor do material (`MATERIAL`) com a iluminação do Solid
   c) continua cor por objeto até o usuário trocar
   d) Resposta livre
   *Bloqueia:* RN-01 e a decisão sobre `hb_details.py` forçar `OBJECT`.

3. **"Textura com linhas": quais arestas são desenhadas?**
   a) todas as arestas da peça (contorno de cada chapa)
   b) só as arestas de silhueta e as divisas entre peças
   c) as arestas no estilo do mockup, mesmo que custe um material/linha extra por peça
   d) Resposta livre
   *Bloqueia:* RN-02 e o custo de desenho no viewport.

4. **Como mapear a fita de borda?**
   a) UV próprio da fita, com o comprimento ao longo da aresta e a largura da fita no eixo V
   b) herda o UV da face vizinha, sem mapa próprio
   c) textura sólida (uma cor por fita), sem mapa
   d) Resposta livre
   *Bloqueia:* RN-03 e o teste de canto/rotação da textura.

5. **O que acontece com armários já salvos com "Cor por objeto"?**
   a) migra para textura padrão na abertura, uma vez, com aviso
   b) mantém a cor até o usuário aplicar textura manualmente
   c) pergunta na primeira abertura da cena
   d) Resposta livre
   *Bloqueia:* RN-04 e a estratégia de compatibilidade.

## 7. Lacunas

- `[DÚVIDA]` RN-01: fonte da textura padrão e comportamento no Solid.
- `[DÚVIDA]` RN-02: definição exata de "linhas" e custo no viewport.
- `[DÚVIDA]` RN-03: UV da fita de borda e das faces internas.
- `[DÚVIDA]` RN-04: migração de cenas existentes.
- Sem decisão sobre essas quatro, `/reversa-plan` não pode dimensionar esforço nem `/reversa-to-do` abrir ações.
