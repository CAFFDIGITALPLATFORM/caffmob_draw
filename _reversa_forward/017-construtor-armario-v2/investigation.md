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

## 7. Execução: T001 e T002 (2026-11-21)

### 7.1 Modelo da corrediça (`assets/slides/slide-st48-0200-0.obj`)

| Item | Valor |
|------|-------|
| Origem | `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/assets/slide-st48-0200-0.obj` |
| Destino | `caffmob_draw/assets/slides/slide-st48-0200-0.obj` (diretório criado nesta ação) |
| Tamanho | 254.513 bytes |
| SHA-256 | `209d2ba9bcccb591cdcf4569a4092df5a971c63bc5f97428b439ce79cccb17ba` (idêntico à origem) |
| Objetos | 4 — `slide-st48-0200-0_1`, `_2`, `_3`, `_4` |
| Vértices / faces | 2.572 / 5.156 |

Os quatro objetos são as quatro partes que o RN-08 nomeia: trilho externo (preso na lateral do armário), trilho interno (preso na gaveta) e as duas gaiolas de esferas a meio curso. O import na geração (T020) pode nomear as partes por índice e marcar o papel de cada uma; nada no arquivo identifica o papel por nome, então o mapeamento fica no código.

**Empacotamento:** `build.py#build_zip` percorre `caffmob_draw/` com `os.walk` e só retira `__pycache__` e o `catalog/` da raiz. `assets/slides/` não é filtrado e entra no ZIP como `assets/slides/slide-st48-0200-0.obj`; conferido simulando o mesmo `os.walk` (uma ocorrência, caminho relativo esperado). Nenhuma mudança no empacotador é necessária. `package_problems`, `texture_problems` e `pbr_problems` não olham `assets/`.

### 7.2 Catálogo `data/translations/armario_v2.json`

39 entradas novas, todas com `pt_BR` e `en_US`. Onze textos que o painel usa já existiam em outro catálogo e foram **reaproveitados em vez de duplicados**, porque o teste de cobertura exige que cada msgid pertença a um arquivo só: as sete abas (`cabinet_editor.json`), `Vertical` e `Horizontal` (`aggregates.json`), `Internas` (`cabinet_editor.json`), `Externas` (`construtor_015.json`), `Abrir` (`ui.json`) e `Gerar`, `Aplicar`, `Cancelar`, `Fechar`, `Duplicar`, `Excluir` (`cladding.json` e `geral.json`). Os dez modelos de frente seguem o `DRAWER_MODEL_ITEMS` do anexo, com rótulo curto e descrição própria para o tooltip.

## 8. Inserção pela interface e travessa de 90 mm (2026-11-23)

### 8.1 Como o painel cria peça

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| A. Operador por peça, com geração no mesmo `execute` | Um passo de desfazer por clique; reusa o núcleo já testado; o painel continua só desenhando | Repete a validação em cada operador, resolvida por uma base comum | **escolhida** (D-21) |
| B. Inserir pelo `update` de uma propriedade | Menos código | Sem passo de desfazer, gera a cada tecla e escreve na cena durante o desenho | descartada |
| C. Um operador com `EnumProperty` de peça | Um só `bl_idname` | Rótulo e ícone genéricos; testar exige percorrer o enum | descartada |

O núcleo já cobre as quatro inserções e tem teste puro: `vaos.inserir_vertical`, `vaos.inserir_horizontal` e `vaos.matriz` (T013), `gavetas.bloco` (T016) e `internos.inserir` (T018). A lacuna era só o caminho de uso: nenhum dos quatro tinha chamador no pacote.

### 8.2 Geometria da contra-frente e da peça de trás

O motor anexo gera as duas como travessa de 90 mm no topo interno, com `espessura = base superior`, e a orientação decide em qual eixo ficam os 90 mm:

```python
if p.contra_frente:
    em_pe = (p.orient_contra_frente == 'EM_PE')
    dy = mm(t_bs) if em_pe else mm(90.0)
    dz = mm(90.0) if em_pe else mm(t_bs)
    make_panel("Contra-frente", ..., internal_y_front + dy / 2.0, z_in_t - dz / 2.0, inner_w, dy, dz)
```

O mockup desenha a mesma travessa (`wMm`/`hMm` valendo 90 ou a espessura) e lista 100 mm no cutlist; o pacote adota 90 mm, o valor do motor de referência. `spec.contra_frente` e `spec.peca_de_tras` foram escritos como painel da altura total (teste de T005 espera 2000 mm em pé e 560 mm deitada), o que fecharia a frente do armário; a correção para travessa está em D-22 e a premissa no roadmap §4.
