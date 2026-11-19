# Data Delta: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md`

## 1. Campos novos

n/a. A feature não cria `PropertyGroup`, `bpy.props` nem custom property. O estado do seletor vive na instância do
modal e morre com ele:

| Estado (na instância do modal) | Tipo | Uso |
|--------------------------------|------|-----|
| `hits` | lista de objetos, já ordenada | Achados do raio, da frente para trás (RN-02) |
| `staged` | conjunto de objetos | Seleção preparada, aplicada só no confirmar (RN-03, RF-10, RF-12) |
| `hover_index` | inteiro | Item em foco, que recebe o destaque (RN-04) |
| `scroll` | inteiro | Primeira linha visível da lista (RF-03, RF-09) |
| `isolated` | booleano | Se o isolamento está ligado (RN-05, RF-08) |
| `original_selected` | conjunto de objetos | Seleção viva na abertura, restaurada no cancelar (RN-03) |
| `original_active` | objeto ou `None` | Objeto ativo na abertura, restaurado no cancelar |
| `original_hidden` | dicionário objeto → `hide_get()` | Estado de visibilidade de todos os objetos do view layer (RN-05) |
| `region`, `area`, `mouse_xy`, alças de desenho | referências | Região do painel, desenho e limpeza dos dois `draw_handler` |

## 2. Campos alterados

n/a. Nenhuma marca usada pela feature muda: o raio e o destaque leem `type`, `visible_get()`, `hide_select`,
`matrix_world`, `bound_box` e `hide_get()`, que são todos nativos do Blender.

## 3. Campos removidos

n/a.

## 4. Mudanças de estrutura na cena

n/a por escrito: nenhum objeto é criado, apagado, reparentado ou convertido. A única escrita é `hide_set` durante o
isolamento, sempre restaurada em confirmar, cancelar, erro e `unregister`.

Observação de persistência: `hide_set` altera a visibilidade do view layer do arquivo, então o efeito é salvo se o
usuário salvar com o seletor aberto. É a Lacuna 🟡 aceita na decisão Q3 da `requirements` (fechar o Blender à força
com o seletor aberto). O caminho normal nunca deixa resíduo.

## 5. Migração

n/a. Nada a migrar e nenhum dado antigo lido ou reescrito.

## 6. Impacto no dicionário e no ERD

- `_reversa_sdd/data-dictionary.md`: sem entrada nova.
- `_reversa_sdd/erd-complete.md`: sem entidade nova; a feature só lê a hierarquia de objetos já modelada.
