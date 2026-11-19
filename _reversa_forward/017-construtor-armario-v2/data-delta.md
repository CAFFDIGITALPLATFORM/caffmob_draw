# Delta de dados: Construtor de armário v2

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Modelo extraído de referência: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo

Três PropertyGroups novos, todos persistidos no `.blend` pelo mecanismo normal do Blender:

1. `BTM_PG_ArmarioV2` em `Object.btm_armario` — o spec completo do armário, o estado de abertura, a aba ativa e o snapshot da abertura.
2. `BTM_PG_ArmarioParte` em `Object.btm_armario_parte` — o papel e as medidas de corte de cada chapa gerada, mais o alvo de animação.
3. `BTM_PG_ContratoChapas` em `Scene.btm_armario_contrato` — chapa máxima, espessuras por papel, montagem e orientações padrão.

Nada é migrado e nada é removido do que já está gravado. O único modelo que sai é o do editor 2D (`WindowManager.btm_cabinet_editor`), porque a interface antiga deixa de ser registrada.

## 2. `BTM_PG_ArmarioV2` — `Object.btm_armario`

Medidas em milímetros (`subtype='DISTANCE'`, `unit='LENGTH'`), como no motor anexo.

| Campo | Tipo | Faixa / valores | Observação |
|-------|------|-----------------|------------|
| `largura` | float | 100–6000 | Externa |
| `altura` | float | 100–3000 | Externa |
| `profundidade` | float | 100–1200 | Externa |
| `tipo_montagem` | enum | `LATERAL_PASSANTE`, `BASE_PASSANTE` | RN-04 |
| `orientacao_frente` | enum | `EM_PE`, `DEITADA` | Contra-frente (RN-04) |
| `orientacao_tras` | enum | `EM_PE`, `DEITADA` | Peça de trás (RN-04) |
| `espessura_lateral` | enum | 6, 15, 18, 25 | RN-05 |
| `espessura_base_inferior` | enum | 6, 15, 18, 25 | RN-05 |
| `espessura_base_superior` | enum | 6, 15, 18, 25 | RN-05 |
| `espessura_divisoria` | enum | 6, 15, 18, 25 | RN-05 |
| `espessura_prateleira` | enum | 6, 15, 18, 25 | RN-05 |
| `espessura_fundo` | enum | 6, 15, 18, 25 | Padrão 6 |
| `espessura_gaveta` | enum | 6, 15, 18, 25 | Caixa da gaveta |
| `espessura_porta` | enum | 6, 15, 18, 25 | Porta de abrir |
| `espessura_folha` | enum | 6, 15, 18, 25 | Folha deslizante |
| `bloquear_chapa` | bool | padrão `True` | RN-03 |
| `divisoes` | coleção de `BTM_PG_ArmarioDivisao` | — | RN-12 |
| `gavetas` | coleção de `BTM_PG_ArmarioGaveta` | — | RN-07 a RN-09 |
| `internos` | coleção de `BTM_PG_ArmarioInterno` | — | RN-13 |
| `porta_ativa` | bool | padrão `False` | Mutuamente exclusiva com `deslizante_ativa` (RN-14) |
| `porta_folhas` | int | 1–4 | RN-14 |
| `porta_dobradica` | enum | `ESQUERDA`, `DIREITA`, `ALTERNADA` | RN-10 |
| `deslizante_ativa` | bool | padrão `False` | RN-14 |
| `deslizante_folhas` | int | 2–4 | RN-14 |
| `deslizante_sobreposicao` | float | 10–60, padrão 30 | RN-14 |
| `deslizante_material` | enum | `MDF`, `VIDRO`, `ALUMINIO` | RN-14 |
| `deslizante_base` | enum | `DENTRO`, `FRENTE` | RN-06 |
| `trilho_profundidade` | float | 30–120, padrão 70 | RN-06 |
| `fundo_ativo` | bool | padrão `False` | RN-15 |
| `fundo_fixacao` | enum | `CANAL`, `SOBREPOSTO` | RN-15 |
| `fundo_recuo` | float | 0–40, padrão 10 | RN-15 |
| `acabamento` | enum | `MADEIRADO`, `BRANCO`, `CINZA`, `PRETO` | RN-14/RF-17 |
| `aba` | enum | `ESTRUTURA`, `DIVISOES`, `GAVETAS`, `INTERNOS`, `PORTAS`, `DESLIZANTES`, `FUNDOS` | Interface |
| `subaba_divisoes` | enum | `VERTICAL`, `HORIZONTAL`, `MULTIPLA` | Interface |
| `subaba_gavetas` | enum | `INTERNAS`, `SAPATEIRAS`, `PRAT_CORREDICA`, `EXTERNAS` | Interface |
| `aberto` | bool | `True`/`False` | Estado de abertura (RN-10) |
| `gerado` | bool | padrão `False` | `False` = móvel antigo ou armário ainda vazio |
| `origem` | string | nome do módulo de biblioteca, ou vazio | D-13 |
| `snapshot` | string (JSON) | — | Estado na abertura (RN-18) |

### 2.1 `BTM_PG_ArmarioDivisao`

| Campo | Tipo | Observação |
|-------|------|------------|
| `uid` | string | Curto, gerado na inserção |
| `eixo` | enum | `VERTICAL`, `HORIZONTAL` |
| `vao` | string | Caminho do vão, como em `cabinet_editor.bays` |
| `posicao` | float | mm a partir do início do vão |
| `tipo` | enum | `FIXA`, `MOVEL`, `ESPACADOR` |
| `espessura` | enum | 6, 15, 18, 25 |

### 2.2 `BTM_PG_ArmarioGaveta`

| Campo | Tipo | Observação |
|-------|------|------------|
| `uid` | string | — |
| `vao` | string | Vão do bloco |
| `indice` | int | 0-based dentro do bloco |
| `altura` | float | mm; o núcleo distribui as folgas de 3 mm |
| `modelo` | enum | os dez modelos `s_cf_*` / `c_cf_*` |
| `separador_colunas` | int | 1 = sem separador |
| `separador_linhas` | int | 1 = sem separador |
| `afastador_frente` / `afastador_tras` / `afastador_esq` / `afastador_dir` | bool | Independentes (RN-09) |
| `corredica_3d` | bool | Usa o OBJ (RN-08) |

### 2.3 `BTM_PG_ArmarioInterno`

| Campo | Tipo | Observação |
|-------|------|------------|
| `uid` | string | — |
| `vao` | string | — |
| `tipo` | enum | `CABIDEIRO`, `CALCEIRO`, `SAPATEIRA`, `MALEIRO` |
| `altura` | float | mm do piso do vão; padrão 480 (calceiro, sapateira) e `altura_vao − 420` (maleiro) |

## 3. `BTM_PG_ArmarioParte` — `Object.btm_armario_parte`

Uma instância por chapa gerada. É a fonte do adaptador de corte (RN-24) e do alvo de animação (RN-10).

| Campo | Tipo | Observação |
|-------|------|------------|
| `papel` | string | `LATERAL`, `BASE_INF`, `BASE_SUP`, `DIVISORIA`, `PRATELEIRA`, `FUNDO`, `FRENTE_GAVETA`, `LATERAL_GAVETA`, `TRASEIRA_GAVETA`, `FUNDO_GAVETA`, `PORTA`, `FOLHA`, `SEPARADOR`, `AFASTADOR` |
| `componente` | string | Código do Padrão de Dimensões (`LAT`, `BAS`, `DIV`, `PRAT`, `FUN_INF`, `POR`, …) para casar com `part_extractor.record_to_part` |
| `comprimento_mm` | float | Medida de corte no comprimento |
| `largura_mm` | float | Medida de corte na largura |
| `espessura_mm` | float | Espessura real da chapa |
| `material` | string | Vazio = vale o padrão do componente |
| `veio` | enum | `NONE`, `HORIZONTAL`, `VERTICAL` (mesma grafia de `part_roles.part_grain`) |
| `fita_l1` / `fita_l2` / `fita_w1` / `fita_w2` | bool | Mesmos lados de `part_roles.EDGE_INPUTS` |
| `uid` | string | `<uid do armário>/<papel>/<índice>` |
| `movel` | bool | `True` em gaveta, porta e folha |
| `curso_mm` | float | Quanto o alvo anda ao abrir |
| `eixo` | enum | `Y`, `X`, `GIRO` |

Peças de ferragem (trilho externo, trilho interno, gaiola) recebem `papel = ""` e ficam fora do corte.

## 4. `BTM_PG_ContratoChapas` — `Scene.btm_armario_contrato`

| Campo | Tipo | Observação |
|-------|------|------------|
| `comprimento_max` | float | Padrão 2750 |
| `largura_max` | float | Padrão 1830 |
| `espessura_lateral` … `espessura_porta` | enum | Mesmos oito papéis do armário |
| `montagem_padrao` | enum | `LATERAL_PASSANTE`, `BASE_PASSANTE` |
| `orientacao_frente_padrao` | enum | `EM_PE`, `DEITADA` |
| `orientacao_tras_padrao` | enum | `EM_PE`, `DEITADA` |
| `configurado` | bool | Falso = nenhum contrato fornecido (RN-02) |

`apply_host_contract(comprimento_max, largura_max, espessuras: dict, montagem, orientacao_frente, orientacao_tras)` é a função pública de injeção (RF-03). O painel semeia o contrato a partir de `standards.api.active_definition` quando `configurado` é falso.

## 5. Campos removidos

| Campo | Onde | Efeito |
|-------|------|--------|
| `WindowManager.btm_cabinet_editor` | `caffmob_draw/cabinet_editor/props.py` | Bloco deixa de ser registrado; arquivo antigo o perde na próxima gravação, sem erro |
| `BTM_PG_CabinetEditorState`, `…Component`, `…Message`, `…Adjustment`, `…StructureRow`, `…DivisionRow` | mesma origem | Classes não registradas pelo pacote; nada indexa esses dados |

Os PropertyGroups de dados dos módulos (`btm_cabinet`, `btm_structure`, `btm_division`, `btm_part`, `btm_geometry`) continuam registrados por `data_props` e pelos módulos donos — nenhum móvel antigo perde dado.

## 6. Migrações

Nenhuma. `btm_armario` ausente significa móvel da construção antiga: `gerado = False`, painel em modo aviso, `Gerar` e `Aplicar` desabilitados (RN-23, D-14).

## 7. Índices e consultas

Não há banco. As leituras são varreduras de `scene.objects`:

- corte: `part_sources.armario_v2_records(scene)` percorre as malhas com `btm_armario_parte` e ignora `btm_cut_exclude` e objetos ocultos, como os outros adaptadores;
- menu de contexto e Abrir/Fechar: sobem a hierarquia a partir do objeto ativo até a raiz com `btm_armario`;
- reabrir o painel: lê `btm_armario` da raiz e repovoa as coleções.

## 8. Unidades e precisão

Milímetros no spec e na peça; metros na geometria do Blender, com a conversão num único ponto de `build.py` (divisão por 1000). Arredondamento de corte em 0,1 mm, como `part_sources` já faz no uid e nos furos.
