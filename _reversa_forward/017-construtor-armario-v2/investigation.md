# Investigação: Construtor de armário v2

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Pergunta de fundo

Como trocar o construtor de armário do pacote por um motor que calcula as peças sozinho, sem perder o que o resto do addon já consome — malha, personalização, padrão de dimensões e plano de corte — e sem deixar dois construtores registrados.

## 2. O que o legado já resolve

| Necessidade | Onde já existe | Estado |
|-------------|----------------|--------|
| Regra de montagem lateral/base passante | `caffmob_draw/cabinet_editor/structure.py#carcass_lengths`, testada em `tests/test_cabinet_editor_structure.py` | 🟢 reutilizável |
| Limite de chapa (lado maior × maior limite) | `caffmob_draw/cutting/part_extractor.py#limit_status` | 🟢 reutilizável |
| Espessura e material por papel | `caffmob_draw/data/dimension_schema.py#PARAMS`, `standards/api.py` | 🟢 reutilizável |
| Peças da cena para o corte | `caffmob_draw/cutting/part_sources.py` (6 adaptadores) e `PartRecord` | 🟢 ponto de extensão |
| Propriedades persistidas no objeto | `data_props.py`, `structure_inputs.py`, `btm_cabinet` | 🟢 padrão a seguir |
| Texto traduzido | `data/i18n.py`, `data/translations/pt_BR.json`, `en_US.json` | 🟢 padrão a seguir |
| Menu de botão direito na vista | `ui/context_menu.py`, `ui/sidebar_selected.py` | 🟢 mesmo gancho |
| Import de OBJ | `assets/` já distribui arquivos; `build.py` empacota o pacote inteiro | 🟡 conferir a assinatura em `docs/rag/project/02_padroes_blender_5_2.md` |

## 3. Alternativas avaliadas

### 3.1 Onde o motor novo vive

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| A. Pacote novo `armario_v2/` | Núcleo puro isolado; não mexe nos 38 arquivos do `cabinet_editor`; testável fora do Blender | Dois nomes no pacote durante a transição | **escolhida** (D-01) |
| B. Reescrever dentro de `cabinet_editor/` | Um pacote só | Mistura o motor novo com a UI antiga que sai; importações circulares com `structure` | descartada |
| C. Adaptar as bibliotecas paramétricas | Reaproveita tudo que existe | É exatamente o acoplamento que o anexo elimina: cada biblioteca reconstrói as próprias chapas | descartada |

### 3.2 Superfície da interface

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| A. Painel na vista 3D com sete abas | Decisão do titular; o móvel é visto enquanto se edita; sem modal nem janela a gerenciar | Precisa de `EnumProperty` por aba e de desenho de estado | **escolhida** (D-05) |
| B. Janela 2D própria (como hoje) | Vista frontal desenhada em GPU já pronta | Repete o modal, o rollback e os handlers que a feature quer aposentar; decisão do titular foi a A | descartada |
| C. Híbrido (janela 2D + painel) | Atende os dois gostos | Duas superfícies para manter e duas fontes de estado | descartada |

### 3.3 Leitura das peças pelo plano de corte

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| A. Adaptador lê malha com papel gravado | As peças são a geometria gerada, sem intermediário; papel e medidas exatos | Exige PropertyGroup por peça e registro no extrator | **escolhida** (D-02, RN-24) |
| B. Emitir `GeoNodeCutpart` falso para reusar o adaptador atual | Zero adaptador novo | O motor não usa Geometry Nodes; criar o modificador só para o corte é peso morto na cena | descartada |
| C. Recalcular as peças na hora do corte a partir do spec | Sempre coerente com o spec | Pode divergir da cena depois de mover ou excluir peça; duas fontes de verdade | descartada |

### 3.4 Corrediça 3D

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| A. Importar o OBJ do anexo, uma vez por armário | Modelo real, como o anexo faz | Arquivo binário no pacote; import a cada geração | **escolhida** (D-12) |
| B. Geometria procedural sempre | Nada a empacotar | Menos fiel; o anexo já tem o modelo | descartada como padrão, mantida como alternativa quando o arquivo falta |

## 4. Padrões aplicáveis do repositório

- `docs/rag/project/02_padroes_blender_5_2.md` — receita de operador com `bl_options = {'REGISTER', 'UNDO'}`, PropertyGroup com `# type: ignore`, `draw_handler_add` com remoção em todos os caminhos.
- `docs/rag/project/03_compatibilidade_5x.md` — inputs de Geometry Nodes via `compat`; `bpy.props` lidos por atributo desde 5.0.
- `docs/rag/project/04_armadilhas.md` — timer e `draw_handler` órfãos após desregistrar; dados desatualizados depois de reconstruir a cena.
- `caffmob_draw/cabinet_editor/gallery.py` — precedente de sessão em dicionário de módulo com `_stop()` chamado em todos os caminhos de saída e no `unregister`.
- `caffmob_draw/cabinet_editor/ops_editor.py#BTM_OT_CabinetEditorModal` — precedente de timer de 16 ms e de limpeza no `_end`.

## 5. O que ainda precisa ser conferido no código, antes de escrever

1. `bpy.ops.wm.obj_import` na 5.2 (nome, `forward_axis`, `up_axis`) — `rag_search.py --symbol`.
2. Como `previews.py` registra a coleção de miniaturas e se algo fora do editor a usa.
3. Quais fumaças existentes abrem o editor 2D (004, 006, 008) e passam a falhar quando a UI sair do registro.
4. Se `collision/guard.py` e `stick/settle.py` só comparam o `bl_idname` do modal antigo.

## 6. Fontes

- `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/__init__.py` — motor de referência (props, contrato, geração, corrediça, abrir/fechar, duplicar).
- `.../mockup_construtor_armarios.html` — as sete abas, HUD, inspetor, menu de contexto e modal de corte.
- `_reversa_sdd/cabinet_editor/requirements.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/cutting/requirements.md` — regras do construtor atual e da extração de peças.
- `_reversa_forward/015-construtor-armario-promob/roadmap.md` — precedente de estrutura de caixa como dado e de módulo antigo seguindo a construção antiga.
- Nenhuma pesquisa externa foi necessária: a especificação que prevalece está no repositório.
