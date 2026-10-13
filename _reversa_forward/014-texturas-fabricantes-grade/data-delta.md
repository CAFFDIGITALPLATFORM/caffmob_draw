# Data delta: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12` (revisão 2: modelo híbrido)
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/library_panel/design.md`, `_reversa_sdd/object_library/design.md`

## 1. Catálogo de texturas (novo, no pacote)

`caffmob_draw/textures/catalog.json`, gerado por `tools/texturas_importar.py` e lido por `texture_library/catalog.py`.

```json
{
  "schema-version": 1,
  "catalog-version": 1,
  "generated-at": "2026-10-12T00:00:00-03:00",
  "default-size-mm": 600,
  "full-sheet-px": [1830, 2750],
  "manufacturers": [
    {"id": "duratex", "name": "Duratex", "collections": [
      {"id": "design", "name": "Design", "items": [
        {"id": "duratex/design/carvalho-avela-design",
         "name": "Carvalho Avela Design",
         "ext": "jpg",
         "thumb": "thumbs/duratex/design/carvalho-avela-design.png",
         "px": [466, 700],
         "size-mm": [399.5, 600.0],
         "sha256": "…",
         "bytes": 182344,
         "bump": null}
      ]}
    ]}
  ]
}
```

Regras:
- `id` estável (`<fabricante>/<coleção>/<slug>`, sufixo `-2`… em colisão): é a chave do material (D-09), do cache e
  do servidor.
- `size-mm` vem de RN-04.
- `sha256` e `bytes` conferem o download (D-11).
- `catalog-version` casa com `GET /v1/textures/catalog?version=`.
- `schema-version` desconhecida, JSON inválido ou campo de tipo errado: catálogo vazio, com o aviso "Catálogo de
  texturas inválido".

## 2. Manifesto do servidor (novo, fora do pacote)

`dist/texturas-servidor/manifest.json`, formato em `interfaces/catalogo-texturas.md`. Não vai para o git nem para o
pacote.

## 3. Arquivos no pacote e no git

| Caminho | Git | ZIP |
|---------|-----|-----|
| `caffmob_draw/textures/catalog.json` | sim | sim |
| `caffmob_draw/textures/thumbs/**.png` (~25 MB) | sim | sim |
| Imagens em tamanho real | não | **não** (o `build.py` recusa, D-04) |

## 4. Arquivos na pasta do usuário da extensão (novos)

| Caminho (`bpy.utils.extension_path_user(__package__, path=…)`) | Conteúdo |
|---|---|
| `textures/<id>.<ext>` | Imagem baixada e conferida por sha256 |
| `textures/<id>.<ext>.part` | Download em andamento (retomável); nunca usado como textura |
| `auth/session.json` (permissão 0600) | `{"schema-version": 1, "refresh_token": "…", "account": {"email": "…", "name": "…"}, "server": "<url>", "saved-at": "…"}`; nunca a senha nem o token de acesso |

`session.json` com `server` diferente de `textures_server_url` é ignorado e pede login (sessão de outro servidor).

## 5. Preferências do add-on (`BTM_AddonPreferences`, estendido)

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `textures_server_url` | String | endereço do servidor da CAF Mob (definido na publicação) | Base do contrato (RN-14, RF-22) |

O modo "100% offline" não é preferência: é o estado em que todas as imagens estão no cache. A interface mostra
"Todas as texturas baixadas".

## 6. Estado de sessão do painel (`WindowManager.btm_library`, estendido)

Base: `BTM_PG_LibraryState` (`library_panel/props.py`), com `open`, `category` e `line`. Campos novos, só de sessão:

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `mode` | Enum `MIN` / `OPEN` / `MAX` | `MIN` | RN-09; `open` passa a ser derivado |
| `pinned` | Bool | False | Retângulo fixo |
| `rect` | FloatVector(4) | (0, 0, 0, 0) | x, y, largura e altura do retângulo; zero = posição inicial |
| `scroll` | Float | 0.0 | Rolagem da grade |
| `tab` | String | "" | `CAT:<nome>` ou `TEXTURAS` |
| `manufacturer`, `collection`, `search` | String | "" | Filtros |

O estado de download (fila, progresso) e o login fazem parte do estado de sessão em memória, em `texture_library/`,
e não ficam em propriedades.

## 7. Propriedades ID nos materiais de textura

| Propriedade | Tipo | Novo/alterado | Uso |
|-------------|------|---------------|-----|
| `btm_texture_id` | string | novo | Id do catálogo (D-09) |
| `btm_texture_size_mm` | float **ou** par `[largura, altura]` | alterado | Par para chapa retangular (D-08) |
| `btm_texture_rotated` | bool | novo | Veio (RN-06) |
| `btm_texture_path` | string | sem mudança | Para catálogo, aponta para o cache do usuário |

## 8. Migrações

- Nenhuma migração de projeto.
- `load_post` (D-09): materiais com `btm_texture_id` têm o caminho refeito para o cache do usuário. Imagem ainda não
  baixada fica pendente: o material é mantido, e a textura entra na fila na próxima vez que for usada.
- Id fora do catálogo do pacote gera um aviso único por arquivo ("Textura do catálogo não encontrada: <id>").
