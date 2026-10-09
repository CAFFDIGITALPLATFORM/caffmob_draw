# Data Delta: Seleção por componente e região na parede

> Identificador: `011-selecao-por-componente`
> Data: `2026-10-09`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md`

## 1. Campos novos

| Dono | Campo | Tipo | Padrão | Salvo no arquivo | Uso |
|------|-------|------|--------|------------------|-----|
| `Scene` | `btm_component_select` | `BoolProperty` | `True` | sim | Interruptor "Seleção por componente" (RN-09, D-08) |
| `WindowManager` | `btm_component_exempt` | `StringProperty` (nomes separados por `\n`) | `""` | não (sessão) | Peças escolhidas por Alt + clique, que o normalizador não promove (D-04) |
| `WindowManager` | `btm_wall_region` | `PointerProperty(BTM_PG_WallRegion)` | vazio | não (sessão) | Região marcada na parede (D-10) |

### `BTM_PG_WallRegion` (novo)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `active` | `BoolProperty` | Há uma região marcada |
| `wall` | `StringProperty` | Nome do objeto da parede (`IS_WALL_BP`) |
| `x0`, `x1` | `FloatProperty` (`unit='LENGTH'`) | Borda esquerda e direita, no X local da parede, com `x0 < x1` |
| `z0`, `z1` | `FloatProperty` (`unit='LENGTH'`) | Borda de baixo e de cima, no Z local, com `z0 < z1` |
| `side` | `EnumProperty` (`FRONT`, `BACK`) | Face da parede onde a região foi desenhada |

A região guarda o nome da parede, e não um ponteiro. Se a parede for apagada ou renomeada, a região é descartada sem
erro.

## 2. Campos alterados

n/a. As marcas usadas para achar a raiz já existem e não mudam:
- `IS_ENTRY_DOOR_BP` e `IS_WINDOW_BP`;
- `btm_plane.object_kind`;
- `btm_group.is_group`;
- `btm_object_item.is_item`;
- `btm_aggregate.is_aggregate`;
- `btm_stick`;
- as tags de módulo de `classify.MODULE_TAGS`.

## 3. Campos removidos

n/a.

## 4. Mudanças de estrutura na cena

- A importação de OBJ, FBX ou glTF com mais de uma malha cria um Empty com `btm_group` (`kind='PLAIN'`), pai das
  malhas importadas (D-09). Os objetos importados antes da feature não mudam.
- A exclusão remove a subárvore inteira da raiz (D-05, D-06). Nenhuma marca muda.

## 5. Migração

n/a. Arquivo antigo lê `btm_component_select` com o padrão `True`. O estado de sessão na `WindowManager` nasce vazio.
