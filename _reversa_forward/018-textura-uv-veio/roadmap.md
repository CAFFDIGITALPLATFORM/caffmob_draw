# Roadmap: Textura por UV, veio e conta-gotas

> Identificador: `018-textura-uv-veio`
> Data: `2026-11-23`
> Requirements: `_reversa_forward/018-textura-uv-veio/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A textura do addon continua sendo um material de imagem por (arquivo, tamanho), mas deixa de ser caixa-preta: o
material passa a nascer com **UV Map** como fonte de coordenada, a escala em milímetros vem do `texture_size_mm` do
catálogo e o nome do material passa a ser o nome do item no catálogo. O giro do veio vira um número em graus gravado
na peça, que o serviço de veio já existente (`texture_library/grain.py`) transforma em rotação do atributo
`btm_grain_rot`; nenhum material novo é criado para girar.

O UV é gerado onde a peça nasce: `armario_v2/build.py` grava um layer `UVMap` por chapa com a escala do catálogo, do
mesmo jeito que `mobi/cena_v2.py` e `geometry/obra_v2.py` já projetam. A parede é corrigida no funil de material
(`customize/adapters/common.set_cutpart_material`), que passa a escrever os seis sockets do nó de parede em vez de
gravar no slot — o mesmo funil que o arrastar-textura e o retexturizar já usam.

Por cima disso entra o conta-gotas: um operador modal lê o material sob o cursor, guarda a assinatura na sessão e um
segundo operador aplica por domínio de acabamento (`FRONTS`, `EXTERNAL`, `INTERNAL`), que é o vocabulário que a 067 já
usa para Porta, Exterior e Interior. Nada de um segundo vocabulário de partes.

**Fatiamento.** Esta é a primeira de três entregas. Ordem escolhida: 018 (materiais confiáveis, defeitos de parede e
UV), 019 (redimensionar, veio do armário e colisão no HUD), 020 (conversão em armário). A 018 vem primeiro porque
conserta dois defeitos silenciosos que hoje atingem todo projeto, não cria geometria e é pré-requisito de confiança
para a 020 herdar material na conversão.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto. Valem as regras de engenharia de `CLAUDE.md`/`AGENTS.md`, tratadas
como restrição:

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Alvo Blender 5.2, diferença de versão só em `compat.py` | Toda escrita de input GN passa por `compat.try_set_gn_input`; nenhuma leitura por nome de socket cru | respeita |
| Propriedade `bpy.props` por atributo, nunca por `obj["..."]` | Campos novos são PropertyGroup; idprops só em material, onde não há PropertyGroup | respeita |
| Núcleo puro separado de `bpy` | Escala de UV, rotação, nome de material e mapa de domínios vão para `texture_library/uv_core.py` | respeita |
| Operador que muda a cena com `UNDO`; handler removido no `unregister` | Conta-gotas e veio com `UNDO`; modal e desenho de destaque com remoção explícita | respeita |
| Texto novo em português, catálogo `pt_BR`/`en_US` | Catálogo `textura_018.json` nos dois contextos | respeita |
| Não editar a cópia espelhada da raiz | Só `caffmob_draw/` e `tests/` | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Núcleo puro novo `caffmob_draw/texture_library/uv_core.py`: `escala_uv(size_mm)`, `girar_uv(angulo)`, `nome_de_material(entry)`, `partes_para_dominios(parte)` | Testável sem Blender e concentra a regra que hoje está espalhada entre `obra_v2`, `retexture` e `finish_core` | (a) deixar a conta dentro de `retexture`; (b) usar o UV de `obra_v2` direto, que é do gerador de obra | 🟢 |
| D-02 | `armario_v2/build.py:_malha` cria `UVMap` em cada chapa com **UV em metros** (1 unidade = 1 m), planar pelo eixo dominante da face; a repetição real fica no `Mapping` do material (`1/tamanho_mm`), então trocar a textura não refaz o UV. **Validada no T001** (caixa de `bmesh` sem modificador, layer sobrevive) e **corrigida no T010**: gravar `comprimento/tamanho_mm` no UV dobraria a escala que o material já aplica. **Fumaça**: chapa 600 × 400 → u 0–0,6 e v 0–0,4 | É o único ponto que emite chapa; sem UV ali, nenhuma chapa da 017 terá UV | (a) emitir UV depois, num operador à parte; (b) deixar o material projetar em caixa | 🟢 |
| D-03 | `retexture.image_material` ganha `projection` com **três fontes**, escolhidas por objeto: `'UV'` (`ShaderNodeUVMap`, layer `UVMap`), `'ATTRIBUTE_UV'` (`ShaderNodeAttribute` GEOMETRY, atributo `uv_map`, para peça com `GeoNodeCutpart`) e `'BOX'` (`TexCoord.Object`); a chave de cache inclui a projeção. **Executada no T012**: o padrão do parâmetro é `'BOX'` por compatibilidade e `projection_for(obj)` decide pelo alvo. Revisada pelo T001: o cutpart **não tem** layer de UV, tem o atributo `uv_map` (FLOAT_VECTOR, CORNER) | O T001 provou que `ShaderNodeUVMap` funciona e respeita o layer, mas peça de biblioteca só expõe `uv_map`; o plano original de um `UV` único não atenderia essas peças | (a) só UV e recusar cutpart; (b) converter `uv_map` em layer aplicando o modificador, o que mataria o construtor paramétrico | 🟢 |
| D-04 | Material é nomeado por `Fabricante Item` ("Arauco Anis"); quando dois fabricantes tiverem o mesmo item, entra a coleção ("Arauco Colecao Realce Anis"); o nome fica também em `mat['btm_texture_nome']` | É o nome que o usuário vê no catálogo e reconhece fora do addon | (a) nome do arquivo (atual); (b) só o nome do item, que colide | 🟢 |
| D-05 | Veio em graus: `grain_angle` (FloatProperty, graus, −180..180) novo em `BTM_PG_ArmarioParte` e em `BTM_PG_Part`; `grain.sync` grava `btm_grain_rot` = `grain_angle` + 90 quando o enum for vertical | Reaproveita o grafo de veio que já existe e mantém o giro por objeto, sem material por ângulo | (a) enum com 4/8 direções; (b) material por ângulo | 🟢 |
| D-06 | O veio de corte continua vindo do enum (`H`/`V`/`NONE`); ao gravar ângulo, o enum é recalculado pelo múltiplo de 90 mais próximo (0/180 → H, 90/270 → V) e o painel avisa quando o ângulo não é múltiplo de 90 | O plano de corte só entende H/V/NONE (`cutting/part_roles.py`) | (a) ângulo no corte; (b) bloquear ângulo intermediário | 🟡 |
| D-07 | Conta-gotas em dois operadores: `caffmob.texture_pick` (modal, lê o material sob o cursor por `view3d` e guarda a origem) e `caffmob.texture_apply_parts` (aplica nos alvos com as partes marcadas) | Separa escolher de aplicar e deixa a aplicação repetível sem novo clique | (a) um operador só, que copia na hora; (b) copiar por área de transferência | 🟢 |
| D-08 | Partes do conta-gotas = domínios de `customize/finish_core.py`: Porta → `FRONTS`, Exterior → `EXTERNAL`, Interior → `INTERNAL`; a marcação por clique usa o mesmo gesto do apontar-papel da 020 | Um vocabulário só para acabamento, sem tradução entre "parte" e "domínio" | (a) enum novo de partes; (b) grupo de material (`CAIXA`/`FRENTES`) | 🟢 |
| D-09 | A assinatura do conta-gotas vive em `WindowManager.btm_texture_pick` (sessão, não salva), com `path`, `size_mm`, `texture_id`, `angle` e `nome` | Copiar textura é gesto de sessão; não precisa poluir o arquivo | (a) guardar em `Scene`; (b) guardar no objeto de origem | 🟢 |
| D-10 | Parede/piso/teto: `set_surface_material(obj, mat)` escreve os seis sockets de parede (`Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge`) e os equivalentes de piso/teto; `set_cutpart_material` delega e devolve `False` quando nenhum socket existe | Hoje a função devolve `True` sem efeito na parede, o que esconde o defeito | (a) adaptador novo por tipo; (b) só slot, com aviso | 🟢 |
| D-11 | Textura em armário v2: `build.gerar` aplica o material da peça quando `btm_armario_parte.material` for nome de material existente, e o acabamento do spec fica como padrão; o UV é refeito a cada geração | Mantém a escolha do usuário depois de gerar de novo e é onde a 020 vai herdar material | (a) só acabamento do spec; (b) material por grupo | 🟢 |
| D-12 | Migração de material antigo no momento do uso: se já existe material com o mesmo `btm_texture_path` e tamanho e o nome é o formato antigo, ele é renomeado para o nome novo; se o nome novo já existe, mantém e avisa | Evita dois materiais iguais com nomes diferentes e não quebra projeto salvo | (a) renomear tudo na carga do arquivo; (b) criar material novo sempre | 🟡 |
| D-13 | Catálogo novo `caffmob_draw/data/translations/textura_018.json`; testes puros `tests/test_018_uv.py`, `test_018_nome.py`, `test_018_partes.py` | Regra do repo para i18n e para núcleo testável | (a) reusar `texturas_014.json`; (b) sem teste puro | 🟢 |
| D-14 | O UV Editor fica garantido nas malhas com layer próprio (armário v2 e malha importada com UV); em geometria gerada por GN (cutpart e parede) o UV é do grafo e o addon **avisa** em vez de prometer edição. A correção do grafo fica fora desta feature | T001: o `GeoNodeCutpart` devolve `uv_layers` vazio e grava `uv_map` a cada avaliação; o `GeoNodeWall` grava `UVMap` (FLOAT2, CORNER) a cada avaliação, então edição na malha base é sobrescrita | (a) editar os `.blend` de nós da 018; (b) aplicar modificador nas peças, perdendo o paramétrico | 🟢 |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou aberta na 018. As premissas abaixo são técnicas e vêm de pontos que só o Blender resolve:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| ~~O UV do layer `UVMap` gravado na malha base chega ao shader nas peças com `GeoNodeCutpart`~~ **Resolvida pelo T001**: não chega. O cutpart entrega o atributo `uv_map` e nenhum layer; a parede entrega `UVMap` gerado pelo grafo | §10, lacuna do UV em Geometry Nodes | Deixou de ser premissa: virou D-03 (três fontes) e D-14 (limite do UV Editor) |
| Ângulo de veio não múltiplo de 90 é visual; o corte usa o múltiplo mais próximo | RN-10, D-06 | Baixo: o corte fica H/V coerente, mas o desenho pode divergir do corte em 45° |
| Renomear material antigo no uso não conflita com material compartilhado entre armários | §10, migração | Médio: nome repetido mantém o antigo e avisa em vez de trocar |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Serviço de veio | `caffmob_draw/texture_library/grain.py` | contrato-alterado | `sync` soma `grain_angle` ao girar e passa a aceitar ângulo livre; enum continua mandando no corte |
| Material de textura | `caffmob_draw/object_library/retexture.py` | contrato-alterado | Nova fonte de coordenada (UV), novo nome de material e projeção na chave de cache |
| Catálogo de texturas | `caffmob_draw/texture_library/catalog_core.py` / `catalog.py` | contrato-alterado | Passa a expor o nome de exibição composto para o material |
| Núcleo de UV | `caffmob_draw/texture_library/uv_core.py` (novo) | componente-novo | Escala, rotação, nome e mapa de domínios, sem `bpy` |
| Geração do armário | `caffmob_draw/armario_v2/build.py` | regra-alterada | Cria `UVMap` por chapa e aplica material da peça |
| Propriedade da peça | `caffmob_draw/armario_v2/props.py` e `caffmob_draw/target/props.py` | contrato-alterado | `grain_angle` novo nos dois grupos |
| Funil de material | `caffmob_draw/customize/adapters/common.py` | regra-alterada | `set_surface_material` para parede/piso/teto e falha visível sem socket |
| Aplicação de textura | `caffmob_draw/texture_library/apply.py` | contrato-alterado | Aceita domínio de parte e devolve o que não pôde aplicar |
| Conta-gotas | `caffmob_draw/texture_library/ops_pick.py` (novo) | componente-novo | Operadores de captura e de aplicação por parte |
| Estado de sessão | `WindowManager.btm_texture_pick` (novo) | contrato-novo | Assinatura da textura copiada |
| HUD/viewport | `caffmob_draw/operators/viewport_hud.py` (consumo) | contrato-alterado | Desenha o destaque da parte sob o cursor durante o conta-gotas |

## 6. Delta no modelo de dados

- Resumo: dois campos `grain_angle` em PropertyGroups existentes, uma assinatura de sessão para o conta-gotas e
  três idprops novos em material de textura (nome, projeção e ângulo de calibração quando houver). Nenhum campo novo
  em `Scene`.
- Detalhe completo em: `_reversa_forward/018-textura-uv-veio/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| n/a | n/a | A feature não toca HTTP, fila, gRPC nem GraphQL; o catálogo é arquivo local já existente |

## 8. Plano de migração

1. Primeiro uso de uma textura já aplicada: reconhecer o material pelo `btm_texture_path` + `btm_texture_size_mm` e
   renomear para o nome do catálogo, gravando `btm_texture_nome` (D-12).
2. Material sem `btm_texture_projection` passa a valer `'UV'`; se o objeto não tiver layer de UV, a aplicação cai em
   `'BOX'` e avisa, sem alterar o material de outros objetos.
3. Peça de armário v2 gerada antes desta feature não tem `UVMap`: a próxima geração recria as peças e o layer; nada
   é migrado em lote.
4. Nenhum arquivo do usuário é reescrito na abertura; a migração acontece no uso, sob o operador com `UNDO`.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Geometry Nodes de chapa/parede gerar UV próprio e ignorar o layer base | alto | **confirmado** (T001) | D-03 com três fontes por objeto e D-14: o addon avisa que o UV de peça com GN é do grafo; o material lê `uv_map` nas peças de biblioteca e `UVMap` na parede |
| Renomear material quebrar projeto salvo que referencia o nome antigo | alto | baixo | Renomear só quando o nome novo não existe; senão manter e avisar; teste com dois armários no mesmo arquivo |
| Ângulo livre divergir do veio de corte | médio | alto | Enum do corte recalculado pelo múltiplo de 90 e aviso em texto no painel |
| Textura em parede de versão antiga sem os sockets esperados | médio | médio | `set_surface_material` devolve `False` e o chamador reporta aviso; nenhuma escrita parcial |
| Conta-gotas aplicar em objeto errado quando a seleção muda durante o modal | médio | médio | Guardar os nomes dos alvos ao iniciar e revalidar antes de aplicar; cancelar sem mudança quando um sumiu |
| Custo de material por textura × projeção criar material duplicado | baixo | médio | Chave de cache explícita e teste puro de reaproveitamento |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Testes puros de UV, nome e partes passando
- [ ] Fumaça no Blender: parede texturizada muda a vista; UV Editor move a textura; veio 90° por parte; conta-gotas em três armários
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-23 | Versão inicial gerada por `/reversa-plan` sobre o escopo fatiado da 018 | reversa |
| 2026-11-23 | T015–T018 executados e revisão de olhos frescos: `texture_library/props.py` (`BTM_PG_TexturePick` em `WindowManager`, D-09), captura da assinatura no `caffmob.texture_pick` e `caffmob.texture_apply_parts` por domínio com `{'REGISTER','UNDO'}`, revalidação dos alvos e recusa sem origem. Simplificações: estado de sessão só nas props (`pick.py` ficou com o cursor), `uv_core.parte_de_dominios`, `common._set_slots` e `apply.material_for` (reusado pelo conta-gotas). **Achado**: `finish.piece_role` não lê `btm_armario_parte`, então a aplicação por parte usa `common.set_cutpart_material` + `finish.remember` + `btm_armario_parte.material`. Fumaça 8/8 (G: só Porta em três armários; H: três recusas) | reversa |
| 2026-11-23 | T019 reaberto e fechado com o desenho: `texture_library/pick.py` (estado, peça sob o cursor por `ray_cast`, papel de acabamento do armário v2), `uv_core.parte_do_alvo` (Porta > Exterior > Interior) e `caffmob.texture_pick` (hover, Esc, sem Undo) pintando a caixa da peça e o nome da parte em `operators/viewport_hud.py`, com remoção no `unregister`. T014: `set_surface_material` grava os seis sockets da parede (nó achado pelos sockets) e os slots de piso/teto; parede sem nó devolve `False`. T011: `build.gerar` aplica o material de `btm_armario_parte.material` e o mantém entre gerações. Fumaça `tests/blender_018_parede_smoke.py` 6/6, incluindo render da parede antes (cinza) e depois (vermelho da textura); 017 e 009 sem regressão, `check_api.py` limpo | reversa |
| 2026-11-23 | T008, T013, T019 e T004–T006 executados: `catalog_core.nome_de_exibicao` (+ `nome_de_arquivo`, `eh_nome_antigo`, `nome_migrado`), `catalog.nome_de`, `retexture.material_name` pelo catálogo e `retexture.migrar_nome` no reaproveitamento; mapa de partes do conta-gotas em `uv_core` (`partes_para_dominios`, `dominios_do_alvo`, `alvos_unicos`). Testes puros: 8 nome, 8 partes, 13 material, verdes; fumaça `blender_018_nome_smoke.py` 3/3. T019 foi entregue como mapa de partes: o desenho no HUD depende do conta-gotas (T015–T018) | reversa |
| 2026-11-23 | Escala com textura retangular medida no Blender: `BOX` dá célula 50 × 200 mm no topo e 200 × 100 mm na lateral; `UV` dá 100 × 100 mm nas duas. Conclusão: a conta do UV está correta e o defeito era o armário ainda aplicar por `BOX`; `apply_cached` e `ops_apply` passaram a escolher a projeção por alvo. T003 escrito (9 testes verdes) | reversa |
| 2026-11-23 | T002, T007, T010 e T012 executados: catálogo `textura_018.json` (chaves sem colisão), `uv_core` puro, `UVMap` em metros na chapa e as três fontes de textura no material. Fumaça no Blender 5.2.0 LTS: 4/4 verificações | reversa |
| 2026-11-23 | T001 executado no Blender 5.2.0 LTS: cutpart sem layer de UV (atributo `uv_map`), parede com os seis sockets e `UVMap` gerado, `ShaderNodeUVMap` validado por render, `grain.sync` a 0,18–0,38 ms por peça. D-02 validada, D-03 reescrita com três fontes, D-14 acrescentada | reversa |
| 2026-11-23 | T009 e T020–T022: veio em graus. `grain_core` ganhou `normalize`/`total_angle`/`direction` e `rotation(angle=)`, `grain_angle` entrou na chapa do v2 e em `btm_part` (update → `grain.sync`), o `sync` lê a intenção de `btm_armario_parte` ou `btm_part` e o corte deriva do total pelo múltiplo de 90. **Desvio**: o enum não é reescrito no update — reescrever fazia o giro saltar 90° entre edições para ângulos entre 45° e 90°. **T017 fechado**: o conta-gotas leva o ângulo da origem. Fumaça 10/10 (I e J) | reversa |
