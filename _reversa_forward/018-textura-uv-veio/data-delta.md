# Data delta: Textura por UV, veio e conta-gotas

> Identificador: `018-textura-uv-veio`
> Data: `2026-11-23`
> Base extraída: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/customize/requirements.md`,
> `_reversa_sdd/collision/requirements.md` (para o padrão de estado de sessão)

## 1. Campos novos

### 1.1 `BTM_PG_ArmarioParte` (peça do armário v2)

| Campo | Tipo | Faixa | Padrão | Onde é lido |
|-------|------|-------|--------|-------------|
| `grain_angle` | Float, graus | −180 a 180 | 0.0 | `texture_library/grain.sync` (giro do atributo `btm_grain_rot`), painel da peça |

- Justificativa: o veio do armário v2 é enum (`veio`), insuficiente para casar textura com chapa vizinha (RN-10).
- Regra de convivência: `veio` continua guardando a intenção (`NONE`/`VERTICAL`/`HORIZONTAL`) e `grain_angle` é o
  giro extra em graus; o **corte** é o múltiplo de 90 mais próximo do total (`veio` + ângulo), derivado por
  `cutting/part_roles.grain_direction` — o enum não é reescrito (ver desvio do T020 em `actions.md`).

### 1.2 `BTM_PG_Part` (`Object.btm_part.grain` já existe)

| Campo | Tipo | Faixa | Padrão | Onde é lido |
|-------|------|-------|--------|-------------|
| `grain_angle` | Float, graus | −180 a 180 | 0.0 | `grain.sync`, `cutting/part_roles.part_grain` (só para aviso) |

- Mesma convivência da 1.1; o corte usa o total de `grain` (`NONE`/`H`/`V`) com `grain_angle`, e arquivo sem o
  campo lê 0 (mesmo corte de antes).

### 1.3 Material de textura (idprops, sem PropertyGroup)

| Idprop | Tipo | Exemplo | Uso |
|--------|------|---------|-----|
| `btm_texture_nome` | str | `"Arauco Anis"` | Nome legível do item do catálogo, independente de renomear o material |
| `btm_texture_nome_conflito` | bool | `True` | Migração de D-12: o nome do catálogo já estava ocupado por outro material, então o antigo ficou e a interface avisa |
| `btm_texture_projection` | str | `"UV"` / `"BOX"` | Fonte de coordenada usada pelo material; entra na chave de cache |
| `btm_texture_size_mm` | float ou par de floats | `600.0` / `[1830.0, 2750.0]` | Já existe: tamanho real da textura |
| `btm_texture_path` | str | caminho absoluto | Já existe: identificação do arquivo |
| `btm_texture_id` | str | `"arauco/anis"` | Já existe: id no catálogo |
| `btm_image_grain_axis` | str | `"H"` / `"V"` | Já existe: calibração do veio na imagem |

- Nenhum idprop existente é removido; `btm_texture_rotated` continua aceito para arquivo antigo (M-05).

### 1.4 Estado de sessão do conta-gotas

`WindowManager.btm_texture_pick` — `PointerProperty` para um PropertyGroup novo, **não salvo** no `.blend` (mesmo
padrão de `WindowManager.btm_collision`).

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `ativo` | Bool | False | Modal em andamento |
| `path` | String | `""` | Arquivo da textura copiada |
| `nome` | String | `""` | Nome do catálogo |
| `texture_id` | String | `""` | Id no catálogo |
| `size_mm` | Float | 0.0 | Largura em mm |
| `height_mm` | Float | 0.0 | Altura em mm (0 = igual à largura) |
| `angle` | Float | 0.0 | Giro de veio copiado |
| `origem` | String | `""` | Nome do objeto de onde veio |
| `alvos` | String | `""` | Nomes dos alvos separados por `\n`, congelados ao abrir o modal |

- `angle` lê `grain_angle` da peça (`btm_armario_parte` ou `btm_part`); a aplicação por parte devolve o ângulo à
  origem antes de sincronizar, e o `btm_grain_rot` das peças fica igual ao da origem (fumaça J).

## 2. Campos removidos ou renomeados

Nenhum campo é removido. O que muda é o **nome do material** (idprop e nome do datablock), não o modelo.

## 3. Migrações

| Item | Regra | Quando roda | Reversível |
|------|-------|-------------|------------|
| Nome de material antigo | Material com `btm_texture_path` + `btm_texture_size_mm` e nome no formato `"Textura: <arquivo> <n> mm"` é renomeado para `btm_texture_nome`/nome do catálogo, se o nome novo não existir | No primeiro uso da textura (aplicar, copiar ou girar veio) | Sim: o nome antigo está no histórico de undo da operação |
| Projeção ausente | Material sem `btm_texture_projection` recebe `"UV"`; se o alvo não tiver layer de UV, a aplicação usa `"BOX"` naquele objeto e avisa | No primeiro uso | Sim: o idprop é regravado na próxima aplicação |
| Peça sem UV | `build.gerar` cria o layer ao regerar | Na próxima geração do armário | Sim: regerar de novo recria |
| Material da peça v2 | `BTM_PG_ArmarioParte.material` passa a aceitar o nome de um material do arquivo; sem nome, continua com a chave do acabamento (`CHAPA`/`VIDRO`/`ALUMINIO`). `build.gerar` lê o campo antes de refazer as peças e o regrava resolvido | Em cada Gerar | Sim: o campo volta à chave do spec se o material sumir |

## 4. Índices e consultas

Não há banco nem índice. As consultas novas são em memória:

- `materiais_por_textura(path, size, projection)` — varre `bpy.data.materials` uma vez por aplicação.
- `partes_do_dominio(objs, dominio)` — uma passada por objeto, usando `finish_core` e `btm_armario_parte.papel`.

## 5. Compatibilidade com o modelo extraído

| Fonte | O que muda |
|-------|-----------|
| `_reversa_sdd/customize/requirements.md#RN-05` | Precedência de material continua; a textura aplicada por domínio grava na peça (`btm_custom.material`) ou no grupo, como hoje |
| `_reversa_sdd/customize/requirements.md#RN-13` | Grupos `CAIXA`/`FRENTES`/`FUNDO`/`INTERNO` continuam aceitos; domínio novo é por cima, sem substituir |
| `_reversa_sdd/data-dictionary.md` | Acrescenta os campos da seção 1; nada é removido |
| `_reversa_sdd/collision/requirements.md#RN-16` | Nenhum impacto: colisão é feature 019 |
| `_reversa_sdd/data-dictionary.md` (`BTM_PG_ArmarioParte.material`) | Mesmo campo, dois valores aceitos: a chave do acabamento (contrato do plano de corte, `cutting/part_sources.ARMARIO_V2_MATERIALS`) ou o nome de um material do arquivo (escolha da peça, T011/D-11) |
