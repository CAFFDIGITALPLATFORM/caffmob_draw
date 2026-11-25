# Investigation: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/023-janela-mockup-construtor/requirements.md`

## Pesquisa de fundo

O construtor de armário do addon já existe como **armário v2** (`caffmob_draw/armario_v2/`), entregue na feature 017 e documentado no adendo vigente `_reversa_sdd/addenda/017-construtor-armario-v2.md` (desde 2026-11-23). O v2 calcula e emite peças em milímetros a partir de um contrato de chapas, com sete abas (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos), catálogo em pt_BR/en_US, modo de abertura animado e um único passo de desfazer por confirmação. A interface do v2 hoje é um **painel na Vista 3D** (`CAFFMob Draw`, sidebar), não uma janela própria.

O editor 2D antigo (`caffmob_draw/cabinet_editor/`) saíra do registro por decisão de design da feature 017/T027 (`cabinet_editor/__init__.py` registra apenas `data_props, gallery, previews, reflow_handler`). Sua máquina de estado (fila de pedidos + modal UNDO, instantâneo `EditorState`, OK/Aplicar/Cancelar) está documentada em `state-machines.md` (Editor de armário) e `cabinet_editor/design.md` (fluxos F-01 a F-03).

A tela 2D própria já é um padrão do legado: `domain.md#canvas2d` (RN-CANVAS2D-08) define a "tela 2D é um Image Editor sem imagem, sem cabeçalho, menus nem barra de ferramentas; só a região lateral", aberta por `canvas2d.window.open_window`.

O mockup de referência (`novo_arm_building/.../mockup_construtor_armarios.html`) especifica: titlebar, toolbar, preview dividido (frontal + corte lateral), empty-overlay "Janela de Armário Vazia", painel lateral de 7 abas, Movimentação, footer OK/Cancelar/Aplicar.

## Alternativas avaliadas

| Alternativa | Avaliação | Decisão |
|-------------|-----------|---------|
| A) Nova janela do sistema (Image Editor, restaura área ao fechar) | Alinha RN-CANVAS2D-08 e requisito Q1 (nova janela do sistema). | **Escolhida** |
| B) Ocupar a área da Vista 3D atual com fallback ao fechar | Descarta o requisito Q1 (pedido explícito de nova janela). | Descartada |
| C) Editar o módulo legado `cabinet_editor`/`btm_cabinet` | Descarta o requisito Q2 e o adendo 017 vigente (armário v2 é o motor atual). | Descartada |
| D) Comportamento equivalente sem pixel-perfeito | Descarta o requisito Q3 (pedido explícito de pixel-perfeito). | Descartada |

## Padrões aplicáveis

- Blender Python API (`bpy`, `bmesh`, `gpu`, `mathutils`) — dependências.md §2.1.
- Operador modal com `UNDO` (`bpy.types.Operator`, `bl_options = {'REGISTER', 'UNDO'}`) — máquina de estado do editor de armário (`state-machines.md`).
- `canvas2d.window.open_window` — abrir janela própria com Image Editor sem imagem (`domain.md#canvas2d` RN-CANVAS2D-08).
- Arquivos locais (blend/JSON/PNG) — sem servidor REST, sem banco, sem fila externa (`architecture.md#Limites e organização`).

## Links para fontes externas

Nenhuma fonte externa (API remota, documentação de terceiros) é necessária; todos os padrões são internos ao pacote `caffmob_draw/`.

## Fontes consultadas

- `_reversa_sdd/architecture.md` (Limites e organização, camada Mobiliário)
- `_reversa_sdd/domain.md` (canvas2d, cabinet_editor)
- `_reversa_sdd/state-machines.md` (Editor de armário)
- `_reversa_sdd/cabinet_editor/design.md` (Visão de Camadas, Estruturas de Dados, Operadores, Fluxos F-01 a F-16)
- `_reversa_sdd/addenda/017-construtor-armario-v2.md` (vigente)
- `novo_arm_building/.../mockup_construtor_armarios.html` (mockup de referência)
