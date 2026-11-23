# Investigation: Textura por UV, veio e conta-gotas

> Identificador: `018-textura-uv-veio`
> Data: `2026-11-23`
> Fontes: código do pacote `caffmob_draw/` (não a cópia espelhada da raiz), extração reversa em `_reversa_sdd/` e
> `docs/rag/`.

## 1. Pergunta de investigação

Por que a textura do addon não aceita UV, não reconhece o nome do catálogo e não chega à parede? E qual é o menor
caminho para corrigir isso sem trocar o motor de material nem criar um segundo vocabulário de partes?

## 2. Achados de código

### 2.1 Material de textura ignora UV

`caffmob_draw/object_library/retexture.py:image_material` monta o grafo do zero:

- `ShaderNodeTexCoord` (saída Object) → `ShaderNodeMapping` → `ShaderNodeTexImage` com `projection = 'BOX'`;
- escala do Mapping é `1 / tamanho em metros`, tirada de `btm_texture_size_mm`;
- cache por `btm_texture_path` + tamanho (e pela variante `ROTATED`, legada).

Não há `UVMAP` no grafo em nenhum caminho. `texture_library/grain.py:projection` só classifica o grafo existente
(`BOX` se a origem for `TEX_COORD`, `UV` se for a saída UV) e `ensure_graph` aceita as duas. Ou seja: o suporte a UV
existe no serviço de veio, mas nunca é usado, porque nenhum material nasce com `UVMAP`.

Consequência: mover ilha de UV no UV Editor não tem efeito; o material projeta em caixa no espaço do objeto.

### 2.2 Nome do material vem do arquivo

`retexture.material_name` devolve `"Textura: <basename> <largura> mm"`. O catálogo, em `textures/catalog.json`, é
organizado por fabricante → coleção → item, com nomes legíveis ("Arauco" / "Colecao Realce" / "Anis"). O material
não guarda o nome do item: guarda o id em `btm_texture_id` quando vem do catálogo, mas o nome visível continua sendo o
do arquivo.

Consequência: fora do addon o usuário não reconhece a chapa; dentro do addon ele depende do id.

### 2.3 Parede não recebe material

`caffmob_draw/customize/adapters/common.py:set_cutpart_material`:

1. procura `GeoNodeCutpart`; se achar, escreve `Top Surface` e `Bottom Surface`;
2. percorre outros modificadores e escreve `Material`, `Stile Material`, `Panel Material`, `Rail Material`;
3. se não achou `GeoNodeCutpart`, cai em "outras malhas": anexa e sobrescreve todos os slots e devolve `True`.

`caffmob_draw/operators/walls.py:home_builder_walls_OT_apply_wall_material` prova o caminho correto: a parede expõe
`Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge` e `Right Edge` como inputs do nó. O
material do slot não participa do desenho.

Consequência: aplicar textura em parede devolve sucesso, não muda nada e não avisa. É o pior tipo de falha.

### 2.4 Peças do armário v2 não têm UV

`caffmob_draw/armario_v2/build.py:gerar` cria a malha, anexa o material do acabamento e preenche
`btm_armario_parte` (papel, espessura, material, veio, fitas), mas não cria layer de UV. Comparando com
`mobi/cena_v2.py` (que cria `UVMap` e usa `mesh.uv_layers.active`) e `operators/walls.py` (piso e teto com `UVMap`
planar), a omissão é só do motor v2.

### 2.5 Veio binário

`target/props.py` e `armario_v2/props.py` só têm `NONE`/`H`/`V` (o v2 com nomes `NONE`/`VERTICAL`/`HORIZONTAL`).
`grain.py:sync` grava em `obj["btm_grain_rot"]` o giro calculado por `grain_core.rotation`, que é múltiplo de 90. O
grafo de material já aceita qualquer Euler: o limite é de dado, não de shader.

### 2.6 Domínios de parte já existem

`caffmob_draw/customize/finish_core.py` define `INTERNAL`, `EXTERNAL`, `FRONTS`, `EDGE`, com `DOMAIN_PIECES` e
`DOMAIN_FACES`. A 067 já grava `btm_part.finish_role` e `btm_face_role`. Esse é o mapa pronto para
Interior/Exterior/Porta; criar um enum novo de "parte" duplicaria a regra.

## 3. Alternativas avaliadas

| Alternativa | Prós | Contras | Decisão |
|-------------|------|---------|---------|
| Manter projeção BOX e só documentar | Nenhum código novo | Não resolve o pedido; UV Editor continua inútil | descartada |
| Material em UV e BOX no mesmo grafo, escolhido por um `Mix` | Um material só por textura | Mistura duas escalas; o `Mix` precisa de máscara e não resolve malha sem UV | descartada |
| Material em UV com queda para BOX quando não há layer (D-03) | Resolve o caso normal e não quebra malha importada | Duas variantes de material na prática, com chave de cache explícita | adotada |
| Criar material por ângulo de veio | Simples de entender | Explode o número de materiais e quebra o reuso | descartada |
| Ângulo no objeto e no atributo do material (D-05) | Um material por textura; giro por peça | Exige recalcular o enum de corte | adotada |
| Enum novo de partes (Porta/Exterior/Interior) | Nome direto na UI | Duplica o vocabulário da 067 e cria tradução | descartada |
| Reusar domínios de `finish_core` (D-08) | Zero duplicação; a 067 já grava o papel | A UI precisa traduzir o rótulo para o domínio | adotada |

## 4. O que precisa ser verificado no Blender (antes de codificar D-02 e D-03)

1. Abrir o `.blend` do pacote com o nó `GeoNodeCutpart` e verificar se a saída tem atributo UV gerado pelo grafo. Se
   tiver, o layer da malha base não chega ao shader e a decisão D-03 precisa de `btm_uv_source` por objeto.
2. Verificar no nó de parede se os seis sockets de material existem em todas as versões do grupo e se
   `compat.try_set_gn_input` os encontra por nome.
3. Verificar se `ShaderNodeUVMap` com layer explícito `'UVMap'` funciona quando a malha tem mais de um layer (o caso
   de malha importada que já traz UV).
4. Medir o custo de `grain.sync` num armário de 40 peças com material de imagem em cada uma.

Nenhuma dessas verificações foi executada nesta sessão: não há Blender no ambiente de análise. Ficam como primeiro
bloco de ações do `actions.md`.

## 5. Padrões aplicáveis do projeto

- `docs/rag/project/02_padroes_blender_5_2.md`: propriedade por atributo, operador com `UNDO`, modal + `POST_PIXEL`,
  remoção de handler no `unregister`.
- `docs/rag/project/03_compatibilidade_5x.md`: entrada de Geometry Nodes só por `compat`.
- `docs/rag/project/04_armadilhas.md`: não manter referência a dado avaliado entre quadros; recalcular no uso.
- Precedente de migração de material: `texture_library/grain.py:_restore_legacy` (M-05), que converte a variante
  `"<nome> ROTATED"` de volta ao material de origem.

## 6. Referências internas

- `_reversa_sdd/customize/requirements.md#RN-05` (precedência de material) e `#RN-13` (grupos).
- `_reversa_sdd/selection/requirements.md#RN-01` (classificação usada pelo arrastar-textura).
- `_reversa_sdd/cutting/requirements.md#Origem das peças` (o que o corte lê de veio).
- `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-19` (peça gerada com papel gravado).

## 7. Resultado do T001 (2026-11-23, Blender 5.2.0 LTS)

Executado em instância headless (`--background --factory-startup`), sem tocar na sessão aberta do titular. Scripts:
`tests/blender_018_probe.py` e `tests/blender_018_probe2.py`.

| # | Verificação | Resultado | Consequência para o plano |
|---|-------------|-----------|---------------------------|
| 1 | `GeoNodeCutpart` gera UV próprio? | **Não gera layer de UV.** O grupo tem 13 entradas e não expõe socket de UV. O grafo grava `Store Named Attribute` com `data_type=FLOAT_VECTOR`, `domain=CORNER`, nome `uv_map`. Malha base com layer `UVMap` avaliada pelo modificador devolve `uv_layers = []`, e o atributo `uv_map` está presente no avaliado | D-03 precisa da terceira fonte (`ShaderNodeAttribute` em `uv_map`) para peça de biblioteca; o layer da malha base não sobrevive |
| 2 | Os seis sockets de material existem na parede? | **Sim.** `GeoNodeWall` tem 13 entradas e os seis nomes existem: `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge`; saída única `Geometry`. O grafo tem `UV_Store` (FLOAT2, CORNER) gravando `UVMap` a partir de posição e normal | D-10 validada: escrever nos sockets é o caminho certo. A parede tem UV real, mas gerado a cada avaliação |
| 3 | `ShaderNodeUVMap` com layer explícito funciona e muda com a edição? | **Sim.** Cena com duas camadas (`UVMap` e `Outra` invertida), material lendo `UVMap`, render 8×8 em Cycles CPU: antes, esquerda `(0.85, 0.22, 0.13)` e direita `(0.08, 0.34, 0.82)`; depois de espelhar `UVMap`, os lados trocam. A camada `Outra` não interferiu | A fonte `'UV'` da D-03 é viável e o UV Editor funciona onde há layer editável |
| 4 | Custo de `grain.sync` em 40 peças | **0,18 ms por peça** (7,4 ms no total; 0,38 ms/peça na primeira medição com cache frio). `ensure_graph` devolveu `True`, projeção detectada `BOX`, `btm_grain_rot` gravado. O addon registrou sem erro em background | Sem risco de desempenho: o orçamento de 100 ms por armário é folgado |

**Conclusões registradas**

- A premissa de que o layer `UVMap` da malha base chegaria ao shader está **refutada**; ela saiu de §4 do roadmap.
- O armário v2 é caixa de `bmesh` sem modificador (`armario_v2/build.py:_malha`), então criar `UVMap` ali é válido e
  editável — D-02 confirmada.
- O UV Editor fica garantido nas malhas com layer próprio. Em geometria de Geometry Nodes o UV é do grafo e o addon
  deve avisar (D-14), não prometer edição.
- Arquivos de medição (`probe_*.png`) foram gerados na raiz e removidos após a leitura dos pixels.
