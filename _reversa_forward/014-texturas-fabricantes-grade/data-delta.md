# Data delta: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/library_panel/design.md`, `_reversa_sdd/object_library/design.md`

## 1. Catálogo de texturas (novo, arquivo no pacote)

`caffmob_draw/textures/catalog.json`, gerado por `tools/texturas_importar.py` e lido por `texture_library/catalog.py`.

```json
{
  "schema-version": 1,
  "generated-at": "2026-10-12T00:00:00-03:00",
  "source": "materials/textures/fabrica",
  "default-size-mm": 600,
  "full-sheet-px": [1830, 2750],
  "manufacturers": [
    {"id": "duratex", "name": "Duratex", "collections": [
      {"id": "design", "name": "Design", "items": [
        {"id": "duratex/design/carvalho-avela-design",
         "name": "Carvalho Avela Design",
         "file": "duratex/Design/Carvalho_Avela_Design.jpg",
         "thumb": "thumbs/duratex/design/carvalho-avela-design.png",
         "px": [466, 700],
         "size-mm": [399.5, 600.0],
         "bump": null}
      ]}
    ]}
  ]
}
```

Regras:
- `id`: estável, em minúsculas ASCII, no formato `<fabricante>/<coleção>/<slug do arquivo>`. Colisão de slug na
  mesma coleção recebe o sufixo `-2`, `-3`… É a chave do material (D-09).
- `size-mm` vem de RN-04:
  - imagem de chapa inteira (os dois lados dentro de `full-sheet-px`): 1 px = 1 mm;
  - senão, o maior lado vale `default-size-mm` e o outro é proporcional.
- `bump`: caminho do relevo correspondente (RF-14) ou `null`.
- `schema-version` diferente de 1, JSON inválido ou campo de tipo errado: o catálogo vira vazio, com o aviso "Catálogo
  de texturas inválido" (princípio VIII).

## 2. Arquivos no pacote

| Caminho | Versionado no git | No ZIP |
|---------|-------------------|--------|
| `caffmob_draw/textures/catalog.json` | sim | sim |
| `caffmob_draw/textures/thumbs/**.png` (256 px no maior lado) | sim (~25 MB) | sim |
| `caffmob_draw/textures/<fabricante>/**` (imagens originais) | não (`.gitignore`) | sim (o `build.py` exige) |

## 3. Estado de sessão do painel (`WindowManager.btm_library`, estendido)

Base: `BTM_PG_LibraryState` (`library_panel/props.py`), com `open`, `category` e `line`. Campos novos, todos de
sessão (não vão para o arquivo):

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `mode` | Enum `MIN` / `OPEN` / `MAX` | `MIN` | Três estados de RN-09; `open` passa a ser derivado (`mode != 'MIN'`) e fica para compatibilidade |
| `pinned` | Bool | False | Retângulo fixo (RN-09) |
| `rect` | FloatVector(4) | (0, 0, 0, 0) | x, y, largura e altura do retângulo maximizado em px de região; zero = posição inicial calculada |
| `scroll` | Float | 0.0 | Rolagem da grade em px |
| `tab` | String | "" | Categoria da grade (`CAT:<nome>` ou `TEXTURAS`) |
| `manufacturer` | String | "" | Filtro de fabricante na área Texturas |
| `collection` | String | "" | Filtro de coleção |
| `search` | String | "" | Texto da busca (D-12) |

## 4. Propriedades ID nos materiais de textura

Hoje (`_reversa_sdd/object_library/design.md`): `btm_texture_path` (string) e `btm_texture_size_mm` (float).

| Propriedade | Tipo | Novo/alterado | Uso |
|-------------|------|---------------|-----|
| `btm_texture_id` | string | novo | Id do catálogo; presente só em material criado a partir do catálogo (D-09) |
| `btm_texture_size_mm` | float **ou** par `[largura, altura]` | alterado | Par para chapa retangular (D-08); float continua aceito (imagem própria) |
| `btm_texture_rotated` | bool | novo | Variante de veio (RN-06) |

Reaproveitamento (RN-05): o material é o mesmo quando caminho, tamanho e `rotated` são iguais.

## 5. Migrações

- Nenhuma migração de projeto.
- Materiais "Textura: …" antigos (float em `btm_texture_size_mm`, sem `btm_texture_id`) continuam funcionando como
  imagem própria.
- `load_post` (D-09): para cada material com `btm_texture_id`, refaz o caminho da imagem a partir do catálogo do
  pacote instalado. Id ausente do catálogo vira aviso único por arquivo ("Textura do catálogo não encontrada: <id>"),
  e o material é mantido.
