# Roadmap: Materiais, UV por face e preferências de exibição do armário

> Identificador: `024-materiais-uv-preferencias`
> Data: `2026-11-25`
> Requirements: `_reversa_forward/024-materiais-uv-preferencias/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Delta cirúrgico sobre o construtor v2 e a biblioteca de texturas, sem tocar geometria de módulo:

1. **Textura por padrão:** o armário v2 passa a criar um material de chapa com **imagem** (textura padrão MDF claro do
   add-on) em vez de só `Base Color`; peça com material escolhido mantém o seu.
2. **Solid com textura:** o fluxo de detalhes (`hb_details.py`) deixa de forçar `color_type = 'OBJECT'` e usa
   `'TEXTURE'`; a cor dos armários (`cabinet_color`) deixa de ser o que define a leitura do móvel.
3. **UV por face:** `build.py` já grava `UVMap` planar em metros por eixo dominante; a 024 acrescenta a **classificação
   da face** (externa, interna, fita) e um segundo layer/atributo para a **fita de borda** com U no comprimento e V na
   largura.
4. **Preferências:** o enum de exibição do armário substitui “Cor por objeto” por **“Textura”**, com as variantes
   **Somente textura** e **Textura com linhas**; nenhuma outra opção existente é removida.
5. **Migração:** armários salvos com cor de objeto recebem a textura padrão **uma vez**, na abertura, com aviso e marca
   de versão.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe no repositório; valem as diretrizes de `AGENTS.md` e a arquitetura extraída.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Edição exclusiva do pacote `caffmob_draw/` | Só `armario_v2/build.py`, `edgeband/build.py`, `texture_library/`, `data/properties.py`, `__init__.py`, `hb_details.py` e testes | respeita |
| Operações não destrutivas com `UNDO` | Aplicar textura e migrar não removem material do usuário; a migração avisa e é idempotente | respeita |
| Núcleos puros testáveis fora do Blender | Classificação de face, layout de UV e decisão de exibição ficam em núcleo puro novo, sem `bpy` | respeita |
| Internacionalização `pt_BR`/`en_US` | Rótulos novos (“Textura”, “Somente textura”, “Textura com linhas”, aviso de migração) entram nos catálogos | respeita |
| Operação local, sem custo de API | A textura padrão é um arquivo do pacote; nada é baixado por padrão | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Criar em `armario_v2/build.py` um material de chapa com `ShaderNodeTexImage` apontando para a **textura padrão MDF claro**, **gerada em runtime** como `bpy.data.images` empacotada (512², grão fino determinístico, sem arquivo binário novo), com `Mapping` em 1/tamanho em metros; peça com `btm_armario_parte.material` definido continua vencendo | Decisão 1a do clarify; o UV já é métrico (`_uv_metros`), então trocar a textura não exige refazer a malha. **Não existe arquivo de textura MDF no pacote** (só ícone e refs dimensionais), e gerar em runtime evita asset binário/licença e mantém o ZIP pequeno | Depender de um PNG novo em `assets/` (licença e empacotamento); baixar do MOBI (quebra o offline) | 🟢 |
| D-02 | Trocar `space.shading.color_type` de `'OBJECT'` para `'TEXTURE'` no fluxo de detalhes e nos pontos que forçam cor de objeto, mantendo `shading.type = 'SOLID'` | Decisão 2a do clarify; é o único caminho para o Solid mostrar a textura sem material por peça | Manter `OBJECT` e pintar a cor média manualmente (não acompanha a textura) | 🟢 |
| D-03 | Núcleo puro `armario_v2/face_uv_core.py`: classifica cada face da chapa em **EXTERNA**, **INTERNA** ou **FITA** pela normal e pela posição relativa à caixa e devolve o retângulo UV em metros; `build.py` grava o layer `UVMap` a partir dele | Separa regra de cena, permite testar canto/rotação sem Blender e substitui o critério atual “eixo dominante” (que não distingue dentro/fora) | Classificar por índice de face da caixa (quebra quando a peça ganha bisel/furo) | 🟢 |
| D-04 | A fita de borda (`edgeband/build.py`, faixa fina separada) recebe UV próprio: **U = comprimento da faixa em metros**, **V = largura da fita / largura repetida da textura**; a faixa mantém a cor sólida quando `use_color` estiver ligado | Decisão 4a do clarify; a faixa é malha própria, então o mapa dela não pode herdar o da chapa | Herdar o UV da face vizinha (textura esticada na quina) | 🟢 |
| D-05 | Nas `BTM_AddonPreferences`, trocar o controle de cor do armário por um `EnumProperty exibicao_armario` com `('TEXTURA_SO', 'TEXTURA_LINHAS')`, mantendo `cabinet_color` apenas como cor de apoio/legado; `show_legacy_libraries`, `panel_mode`, `stick_magnet`, `mobi_url` e demais opções ficam intactas | Decisão 2 do pedido; nenhuma preferência existente é removida além do controle de cor, e o valor antigo é lido na migração | Renomear `cabinet_color` (perde o valor salvo); criar uma segunda tela de preferências | 🟢 |
| D-06 | “Textura com linhas” desenha **todas as arestas de cada peça** pelo contorno de malha (Freestyle/`show_object_outline` no Solid e arestas marcadas `use_edge_sharp`/atributo para render), sem material extra por peça; a variante “Somente textura” desliga esse contorno | Decisão 3a do clarify; usa o contorno que o Blender já desenha, sem sombrear a malha duas vezes | Criar objeto de wireframe por peça (custo de cena e de undo) | 🟡 |
| D-07 | Migração única em `load_post`: se o armário não tem marca `btm_armario.exibicao_versao`, aplica a textura padrão nas peças sem material, grava `exibicao_versao = 1` e emite um aviso único por cena | Decisão 5a do clarify; idempotente e não reaplica em toda abertura | Migrar em `depsgraph_update` (rodaria a cada frame) | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| “Cursos 3D” é uma opção existente da interface de preferências/recomendações; **não há string com esse nome no código** (`pt_BR`/`en_US`/Python). A feature trata a decisão como “não remover nenhuma opção existente além do controle de cor” | RN-02 | Se “Cursos 3D” for outro controle (ex.: biblioteca de cursos), o plano precisa de uma ação extra só para ele |
| A textura padrão MDF claro é gerada em runtime como imagem empacotada; não há PNG de MDF no pacote hoje | RN-01, D-01 | Se o titular exigir um arquivo de textura real do catálogo, entra o download/asset e o escopo cresce |

Nenhuma premissa vem de `[DÚVIDA]`: as cinco decisões foram fechadas em `/reversa-clarify` (2026-11-25). A premissa
“Cursos 3D” é factual, não uma dúvida de produto — a T001 a confirma na GUI antes de mexer nas preferências.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `armario_v2` | `_reversa_sdd/addenda/017-construtor-armario-v2.md#Impacto por artefato da extração` | regra-alterada | Material com imagem padrão, UV por face (`face_uv_core.py`) e marca de exibição/migração na raiz |
| `armario_v2/build.py` | `caffmob_draw/armario_v2/build.py:309` (`_material`), `:396` (`_uv_metros`) | regra-alterada | `_material` ganha textura; `_uv_metros` passa a delegar o retângulo ao núcleo de faces |
| `edgeband` | `caffmob_draw/edgeband/build.py` (`_write`, `solid_material`) | regra-alterada | Faixa ganha UV próprio (U comprimento, V largura) e material texturizado quando não for cor sólida |
| `texture_library` | `caffmob_draw/texture_library/uv_core.py` | contrato-alterado | Empresta `LAYER_UV`/projeção ao novo núcleo, sem duplicar vocabulário de veio |
| `data` | `caffmob_draw/data/properties.py` (`btm_armario`) | regra-alterada | `exibicao_versao` e `exibicao` no armário; nenhuma propriedade existente muda de tipo |
| `preferências` | `caffmob_draw/__init__.py:146` (`BTM_AddonPreferences`) | regra-alterada | `exibicao_armario` substitui o controle de cor do armário; opções existentes preservadas |
| `hb_details` | `caffmob_draw/hb_details.py:98` | regra-alterada | `color_type = 'TEXTURE'` no fluxo de detalhes |

## 6. Delta no modelo de dados

- `Object.btm_armario` (raiz): `exibicao_versao` (Int, padrão 0; 1 = migrado) e `exibicao` (Enum `TEXTURA_SO` |
  `TEXTURA_LINHAS`, padrão herdado da preferência).
- `Object.btm_edgeband`: nada novo; o UV é geometria, não dado.
- `Scene.btm_settings`: nada novo; a escolha é de preferência do add-on, não da cena.
- Migração: nenhum campo removido. `cabinet_color` continua existindo como legado lido pela migração.
- Detalhe completo em `_reversa_forward/024-materiais-uv-preferencias/data-delta.md`.

## 7. Delta de contratos externos

Nenhum: a feature não abre HTTP, fila ou formato de arquivo. Por isso não há diretório `interfaces/`.

## 8. Plano de migração

1. **Cena antiga:** `load_post` percorre só raízes `btm_armario` de `Marcenaria` com `exibicao_versao == 0`, aplica a
   textura padrão nas peças sem material, grava `exibicao_versao = 1` e mostra **um** aviso por cena.
2. **Preferência antiga:** se `exibicao_armario` estiver no padrão e `cabinet_color` tiver sido alterado, a migração
   mantém a textura (decisão 5a) e registra no relatório que a cor antiga virou cor de apoio.
3. **Peça com material do usuário:** nunca é sobrescrita; a textura só entra onde `material` está vazio.
4. **Fita de borda com cor sólida (`use_color`):** continua sólida; o UV novo só vale quando há material texturizado.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| UV por face inverter dentro/fora em peça com espelho (`scale.x = -1`) | alto | média | O núcleo recebe a matriz/determinante e normaliza o sinal; ensaio cobre peça espelhada (023) |
| Textura gerada em runtime ficar com aparência fraca | médio | média | Grão determinístico com semente fixa e teste de que a imagem é empacotada (`pack()`) e sobrevive ao salvar/reabrir |
| `color_type = 'TEXTURE'` deixar peças sem material cinza no Solid | baixo | alta | Toda peça sem material recebe o material padrão com imagem antes de desenhar |
| Migração rodar em cena grande e travar a abertura | médio | baixa | Só raízes de `Marcenaria`, uma passada, sem regenerar geometria |
| “Textura com linhas” pesar o viewport em armário grande | médio | média | Contorno de objeto, sem objeto extra; medir com o ensaio de 54 peças da 023 |

## 10. Critério de pronto

- [ ] Armário novo nasce com a textura padrão em todas as peças sem material; peça com material do usuário não muda
- [ ] Solid usa `color_type = 'TEXTURE'` e mostra a textura; Preview e render usam o mesmo material
- [ ] UV por face classifica EXTERNA/INTERNA/FITA e a fita tem U no comprimento e V na largura (ensaio puro + Blender)
- [ ] Preferências oferecem “Textura” com “Somente textura” e “Textura com linhas”; demais opções intactas
- [ ] Cena antiga migra uma vez, com aviso e `exibicao_versao = 1`; segunda abertura não repete
- [ ] `pt_BR`/`en_US` completos (`test_i18n_coverage`) e `check_api.py` sem API desconhecida
- [ ] Suítes pura e Blender verdes, exceto os casos ambiente-gated já enumerados (MOBI/permissão NTFS)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-25 | Versão inicial gerada por `/reversa-plan` a partir das cinco decisões do `/reversa-clarify` | reversa |
