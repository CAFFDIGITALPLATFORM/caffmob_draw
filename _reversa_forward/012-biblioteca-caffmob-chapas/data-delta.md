# Data Delta: Biblioteca CAFFMob e armários por chapas no padrão global

> Identificador: `012-biblioteca-caffmob-chapas`
> Data: `2026-10-09`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md`, `caffmob_draw/standards/model.py`,
> `caffmob_draw/data/properties.py`

## 1. Campos novos

| Dono | Campo | Tipo | Padrão | Salvo | Uso |
|------|-------|------|--------|-------|-----|
| `BTM_PG_StandardDefinition` (`standards/model.py`) | `assembly` | `EnumProperty` (`LATERAL`, `BASE`) | `LATERAL` | sim | Montagem do padrão global (RN-08, D-08) |
| `BTM_PG_CabinetProperties` (`Object.btm_cabinet`) | `assembly` | `EnumProperty` (`LATERAL`, `BASE`) | `LATERAL` | sim | Montagem do armário (RN-08, D-07) |
| `BTM_PG_CabinetProperties` | `line` | `EnumProperty` (`COZ`, `DOR`, `BAN`, `SAL`, `ESC`) | `COZ` | sim | Linha do padrão do armário (RN-03, D-13) |
| `Object` (raiz de módulo paramétrico: CAFFMob, frameless, closets) | `btm_standard_uid` | idprop `str` | `""` | sim | Padrão global com que o módulo foi criado ou atualizado (RN-09, D-09) |
| `BTM_AddonPreferences` (`__init__.py`) | `show_legacy_libraries` | `BoolProperty` | `False` | preferências | Mostra a interface das bibliotecas herdadas, só para suporte (RN-12, D-01) |
| `WindowManager` | `btm_library` | `PointerProperty(BTM_PG_LibraryState)` | — | não (sessão) | Painel aberto ou fechado, última categoria (D-02, D-06) |

### `BTM_PG_LibraryState` (novo)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `open` | `BoolProperty` | Painel aberto |
| `category` | `StringProperty` | Última categoria aberta (linha padrão do Criar armário) |

## 2. Campos alterados

| Campo | Antes | Depois |
|-------|-------|--------|
| `btm_line` (idprop em raiz de módulo) | Gravado só por `sync._tag_lines` (COZ ou DOR) | Gravado também ao inserir pela categoria, com a linha dela (BAN, SAL, ESC…) |
| `WindowManager.btm_standards_draft.include_manual` | Interruptor no Configurador | Fora da interface: o valor vem da 2ª pergunta (D-11); o campo continua para scripts |
| `operators/cabinet_builder.py` (propriedades do operador) | 0,8 / 0,7 / 0,55 / 0,018 como padrão | Fallback nomeado, usado só sem padrão ativo; `invoke` preenche tudo pelo padrão e pela linha |
| `btm_cabinet.cabinet_type` (BASE, WALL, TALL) | Escolhido no módulo rápido | Usado também para as medidas externas do padrão (D-08); WALL = aéreo |
| `Scene.home_builder.product_tab` | Trocado pela interface | Some da interface; o `load_post` põe FRAMELESS com a porta fechada (D-04) |

## 3. Arquivo novo do usuário

`extension_path_user(pkg, "modules")/categories.json`, UTF-8:

```json
{
  "schema-version": 1,
  "categories": [
    {"name": "Lavanderia", "line": "DOR"},
    {"name": "Geral", "line": "COZ"}
  ]
}
```

- As quatro categorias fixas (Cozinha, Banheiro, Sala, Home office) não ficam no arquivo: vêm do catálogo do pacote.
- Nome: não vazio, sem `/` nem `\`, único sem diferenciar maiúsculas, e diferente das fixas.
- Linha desconhecida ou arquivo inválido: lê o que der, avisa e usa COZ; o arquivo não é sobrescrito até a próxima
  gravação válida.
- Cada categoria é também uma pasta `modules/<nome>/` (a mesma de `customize/library_io.py`).

## 3. (cont.) Marcador dos grupos antigos

`extension_path_user(pkg, "modules")/legacy_groups.json`, gravado quando o usuário aceita ou dispensa a oferta de
converter os grupos salvos (roadmap D-30):

```json
{"schema-version": 1, "offered": true, "converted": ["Cozinha L.blend", "Ilha.blend"]}
```

Os grupos convertidos viram módulos em `modules/Geral/` (mesma estrutura de `customize/library_io`); os `.blend`
originais em `cabinet_groups/` não são apagados.

## 3a. Catálogo de modelos prontos (dados do pacote)

`caffmob_draw/data/library_models.json`:

```json
{
  "schema-version": 1,
  "models": [
    {"id": "balcao_1p", "label": "Balcão 1 porta", "cabinet_type": "BASE", "width_mm": 450, "door_swing": "LEFT", "shelves": 1},
    {"id": "balcao_2p", "label": "Balcão 2 portas", "cabinet_type": "BASE", "width_mm": 800, "door_swing": "DOUBLE", "shelves": 1},
    {"id": "aereo_1p", "label": "Aéreo 1 porta", "cabinet_type": "WALL", "width_mm": 450, "door_swing": "LEFT", "shelves": 1},
    {"id": "aereo_2p", "label": "Aéreo 2 portas", "cabinet_type": "WALL", "width_mm": 800, "door_swing": "DOUBLE", "shelves": 1},
    {"id": "torre", "label": "Torre", "cabinet_type": "TALL", "width_mm": 600, "door_swing": "DOUBLE", "shelves": 4}
  ]
}
```

Altura, profundidade, chapas e montagem não ficam no modelo: vêm do padrão, na linha da categoria. Sem gaveteiro: gavetas
no módulo CAFFMob são da feature 013 (sessão 4).

## 3b. Relatório da conversão (sessão, não salvo)

Por armário: nome do herdado, biblioteca, nome do módulo CAFFMob criado e a lista de perdas (texto traduzível e
quantidade).

## 4. Campos removidos

n/a.

## 5. Migração (`standards/migration.py`, M-03, no `load_post`)

1. Padrão sem `assembly`: lê `LATERAL` (padrão da propriedade).
2. Raiz de módulo paramétrico sem `btm_standard_uid`: recebe o uid do padrão ativo, sem refazer nada.
3. Módulo CAFFMob sem `line` ou `assembly`: COZ e LATERAL (o tipo já existe em `cabinet_type`).
5. Com a porta herdada fechada, `product_tab` = FRAMELESS (D-04).
4. Pastas em `modules/` sem entrada em `categories.json`: entram com linha COZ.
