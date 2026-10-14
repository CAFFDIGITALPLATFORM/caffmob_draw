# Data delta: 015-construtor-armario-promob

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/data-dictionary.md` e sobre as features 006, 008, 012 e
> 014. Medidas em metros nas propriedades do Blender e em milímetros nos padrões e nos JSON, como hoje
> (RN-STANDARDS-01).
>
> **Nada é removido.** Um módulo sem `structure_id` continua com a construção antiga (RN-22, D-06).

## 1. Propriedades do Blender

### 1.1 `Object.btm_cabinet` (`caffmob_draw/data/properties.py:307`)

| Campo | Tipo | Padrão | Mudança | Observação |
|---|---|---|---|---|
| `structure_id` | `StringProperty` | `""` | **novo** | Id da estrutura no catálogo (`cabinet_structures.json`). Vazio = construção antiga (RN-22). `update=update_cabinet_geom` |
| `cabinet_type` | enum BASE/WALL/TALL | BASE | inalterado | Com `structure_id`, é preenchido pelo grupo da estrutura (INFERIOR → BASE, SUPERIOR → WALL, DESPENSEIRO → TALL) e não é mais editado à mão |
| `line` | enum COZ/DOR/BAN/SAL/ESC | COZ | inalterado | Com `structure_id`, vem do ambiente da estrutura |
| `assembly` | enum LATERAL/BASE | LATERAL | inalterado | Valor inicial = `group_assembly` do padrão para o grupo, ou o da estrutura |
| `has_top` / `thickness_top` / `mode_top` | — | — | inalterado | Continua sendo a "Base Superior". Estrutura sem Base Superior grava `has_top = False` |

### 1.2 `Object.btm_structure.extras` (`caffmob_draw/cabinet_editor/data_props.py`, `BTM_PG_StructureExtra`)

A chave é texto; não há mudança de esquema, só chaves novas da árvore (`catalog.TREE`):

| Chave nova | Rótulo | Componente (corte) | Valor | Papel em `carcass_parts` |
|---|---|---|---|---|
| `STRETCHER_FRONT` | Sarrafo Frontal | SAR | largura (m); 0 = padrão `stretcher_width` | Sarrafo no alto, rente à frente |
| `STRETCHER_BACK` | Sarrafo Traseiro | SAR | idem | Sarrafo no alto, atrás; deitado ou em pé conforme `rear_stretcher` |
| `STRETCHER_FULL` | Sarrafo Inteiro | SAR | — | Chapa de topo na profundidade toda, entre as laterais (substitui os dois sarrafos) |
| `TOP_LINEAR` | Tampo Linear | TAMP | — | Tampo sobre as laterais, profundidade + `top_overhang` |
| `TOE_KICK` | Rodapés (estrutura) | ROD | altura (m); 0 = padrão `toe_kick_height` | Rodapé que levanta a caixa dentro da altura total (D-04) |
| `REAR_RAILS` | Travessas traseiras | TRA | — | Só com o fundo TRAVESSAS (D-09) |
| `CASTERS` | Rodízios | ferragem `RODIZIO` | altura 0,100 | Abaixo da caixa, como os pés (lista de ferragens) |
| `SIDES_EXTENDED` | Laterais Engrossuradas | LAT | — | 🔴 Fora do escopo: aparece desabilitado com o motivo |

A presença padrão de cada chave vem da estrutura (`components` no catálogo). O módulo grava uma entrada só quando o
projetista muda o estado (a regra "ausente = como a biblioteca faz" da 006).

### 1.3 Enums com itens novos, sempre **acrescentados no fim** (o índice gravado não muda)

| Enum | Arquivo | Itens novos |
|---|---|---|
| `EXTRA_KIND_ITEMS` | `cabinet_editor/data_props.py` | `HANGER_ROD`, `PANTS_RACK`, `SHOE_RACK`, `BELT_RACK`, `CASTER`, `STRETCHER`, `TOE_KICK_STRUCT` |
| `DIVISION_KIND_ITEMS` | `cabinet_editor/data_props.py` | `INVISIBLE` (divide, sem peça e fora do corte), `DIVISION_ONLY` (divide para agregados, sem peça) |

`Object.btm_division` ganha `variant` (`StringProperty`, padrão `""`): a variante de catálogo da chapa (`CORTA_SAR`,
`C_REB`, `NAO_DIVIDE_FUNDO`, `CORREDICA`, `ARAMADA`, `MONTANTE`). Vazio = como hoje.

### 1.4 Vãos (`Object.btm_division.bay`, `cabinet_editor/bays.py`)

| Campo | Tipo | Mudança | Observação |
|---|---|---|---|
| `bay_width` | `FloatProperty` (m), padrão 0 | **novo** em `btm_division` | Largura digitada do vão à esquerda da divisória de vão inteiro; 0 = largura igual (RN-14, D-15) |

## 2. Padrão de Dimensões (`caffmob_draw/data/dimension_schema.py`, `standards/`)

### 2.1 Campos novos em Dimensões Externas (por linha; `_EXTERNAL_FIELDS`)

| Campo | Rótulo pt | Rótulo en | BR | EUA | Mín. | Máx. |
|---|---|---|---|---|---|---|
| `stretcher_width` | Sarrafo - Largura | Batten - Width | 100.0 | 4 in | 30.0 | 300.0 |
| `shelf_setback` | Prateleira móvel - Recuo frontal | Adjustable shelf - Front setback | 20.0 | 0,75 in | 0.0 | 100.0 |
| `hanger_rod_drop` | Cabideiro - Distância da prateleira | Hanging rod - Drop from shelf | 70.0 | 2,75 in | 20.0 | 300.0 |

Campos que já existem e passam a ser usados pelas estruturas: `toe_kick_height` (100), `toe_kick_setback` (50),
`top_overhang` (20), `base_height`, `base_depth`, `upper_*`, `install_height_upper`, `tall_*`.

### 2.2 `group_assembly` na definição (`standards/model.py`)

Fora dos valores numéricos (`raw`), como a `assembly` da 012:

```json
{
  "INFERIOR":    {"assembly": "LATERAL", "back_kind": "ENCAIXADO", "rear_stretcher": "HORIZONTAL"},
  "SUPERIOR":    {"assembly": "LATERAL", "back_kind": "ENCAIXADO", "rear_stretcher": "HORIZONTAL"},
  "DESPENSEIRO": {"assembly": "LATERAL", "back_kind": "ENCAIXADO", "rear_stretcher": "HORIZONTAL"}
}
```

- `assembly`: LATERAL | BASE.
- `back_kind`: ENCAIXADO | REBAIXADO | PREGADO | TRAVESSAS.
- `rear_stretcher`: HORIZONTAL | VERTICAL.
- Grupo ausente ou valor inválido: vale o da estrutura, com aviso (RN-STANDARDS-19 aplicada por campo).
- Entra na comparação de rascunho (RN-STANDARDS-05) como a montagem: mudar é uma alteração.
- Entra em `own` (RN-STANDARDS-06) só se o módulo tiver `group_assembly` próprio, o que não existe nesta feature.

## 3. Arquivos de dados

| Arquivo | Mudança | Contrato |
|---|---|---|
| `caffmob_draw/data/cabinet_structures.json` | **novo**: estruturas de Cozinhas e Dormitórios e a tabela `legacy_map` | `interfaces/catalogo-estruturas.md` |
| `caffmob_draw/data/library_models.json` | Cada modelo ganha `structure_id` (opcional; ausente = `legacy_map`) | `interfaces/catalogo-estruturas.md#Modelos` |

## 4. Plano de corte (registros)

Com `structure_id`, `synthetic_records` gera um registro por `Part` de `carcass_parts`, com o nome de papel:

| Papel | Nome no corte | Componente | Fitas (padrão BR) |
|---|---|---|---|
| LEFT / RIGHT | Lateral esquerda / Lateral direita | LAT | frente |
| BOTTOM | Base inferior | BAS | frente |
| TOP | Base superior | BAS | frente |
| STRETCHER_FRONT / STRETCHER_BACK | Sarrafo frontal / Sarrafo traseiro | SAR | frente (só o frontal) |
| STRETCHER_FULL | Sarrafo inteiro | SAR | frente |
| TOP_LINEAR | Tampo linear | TAMP | frente e laterais |
| TOE_KICK | Rodapé frontal | ROD | frente |
| BACK | Fundo | FUN_INF / FUN_SUP / FUN_ALT pelo grupo | — |
| REAR_RAILS | Travessa traseira (×2) | TRA | — |

- **Fundo por grupo:** o fundo passa a usar FUN_SUP no grupo SUPERIOR e FUN_ALT no DESPENSEIRO. Isso altera a
  RN-STANDARDS-12 só para módulos com `structure_id`.
- **Chave do registro:** continua `synthetic:<nome>`. Os nomes novos não colidem com os antigos. Os módulos sem
  `structure_id` mantêm os mesmos nomes e uids.

## 5. Migrações

| Quando | O que muda | Reversível |
|---|---|---|
| Abrir o editor num módulo sem `structure_id` | `structure_id` = `legacy_map[(line, cabinet_type)]`; `has_top` conforme a estrutura; malha regenerada | Sim: Cancelar devolve o instantâneo tirado antes da conversão; desfazer depois do OK |
| Reaplicar o padrão (`sync.apply_to_module`) | Mesma conversão nos módulos do plano | Sim: desfazer |
| Abrir um `.blend` antigo | Nada | — |
| Importar padrão JSON/XML sem os campos novos | Campos assumem os valores de fábrica; `group_assembly` vazio | — |
