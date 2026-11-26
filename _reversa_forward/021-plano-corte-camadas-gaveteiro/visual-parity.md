# Paridade visual — painel do Construtor de Armário v2 (T033/A004)

**Data:** 2026-11-26
**Alvo:** `caffmob_draw/armario_v2/panel.py` — `BTM_PT_ArmarioV2`, categoria **CAFFMob Draw**
**Referência:** `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html`
**Ambiente:** Blender 5.2, Windows, janela 1560×1009, `--factory-startup --enable-event-simulate`

## Como foi executado

- O mockup foi aberto no navegador e capturado em `audit/mockup-021.png`.
- `tests/blender_021_panel_visual.py` abre uma janela real, cria o armário vazio (`caffmob.cabinet_editor`), monta a
  caixa, seleciona a raiz, abre a barra lateral, escolhe a categoria CAFFMob Draw por clique simulado, rola até o
  painel e salva `audit/painel-021.png`.
- Comando:
  `blender.exe --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_021_panel_visual.py`
- Resultado: `ABRIR {'FINISHED'}`, `MONTAR {'FINISHED'}`, `PRINT ... True`, saída **0**, sem traceback.

O painel do armário v2 fica no fim da categoria CAFFMob Draw, depois dos painéis já existentes (Opções, Cena,
Construir, Padrões Rápidos do Projeto, Ambiente); a barra lateral precisa ser rolada até ele. Isso é a organização
atual da categoria, não uma mudança desta rodada.

## O que o painel mostra

Com um armário 1000×2400×510 mm e o contrato 2730×1810, a aba ESTRUTURA mostra: título "Construtor de Armários",
atalhos "Plano de Corte" e "Abrir Janela", "Chapa OK (2730×1810)", "Montar Caixa"/"Limpar", as sete abas em duas
colunas (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos), "Armário: 1000 × 2400 × 510 mm",
"Montagem: Lateral passante" e o contrato de chapas abaixo.

## Divergências e destino

| # | Divergência | Evidência | Severidade | Destino |
|---|---|---|---|---|
| 1 | `icon='MOD_LENGTHWISE'` não existe no enum do Blender 5.2: desenhar a caixa "Travessas" (aba Estrutura) levantava `TypeError` e o painel não terminava de desenhar | traceback da primeira execução | Alta (quebra o painel) | **Corrigido** para `MOD_LENGTH` |
| 2 | As sete abas em 4 + 3 numa linha truncavam "Estr...", "Divi...", "Gav..." e "Inte..." na barra de 280 px | `audit/painel-021.png` | Média (rótulos) | **Corrigido**: grade de 2 colunas × 4 linhas; rótulos completos |
| 3 | Título e atalhos na mesma linha truncavam "Const...", "Plano..." e "Abrir J..." | idem | Média | **Corrigido**: título em linha própria; atalhos na linha seguinte |
| 4 | "Montagem: Latera..." e "Vão ativo" dividiam a linha | idem | Baixa | **Corrigido**: "Montagem" e "Vão ativo" em linhas separadas; "Lateral passante" completo |
| 5 | Paleta: mockup claro (#eceef2/#fff, azul #2563eb); painel segue o tema do Blender (escuro no factory) | capturas | Aceita por design | Painel nativo usa o tema do usuário; a paleta CAFF exigiria desenho próprio (a janela do construtor) |
| 6 | Tipografia/espaçamento: mockup Segoe UI 12 px, gaps 4–12 px, raios 4 px e sombras; painel usa layout nativo (`box`, separadores), sem raio/sombra | capturas | Aceita por design | idem |
| 7 | Estrutura: o mockup é uma janela inteira (titlebar, toolbar, canvas 2D, inspector, status); o painel é uma barra lateral sem canvas/controles de vista | capturas | Aceita por escopo | A janela inteira é `caffmob.armario_v2_window_open` (`window.py`); a T033 compara o painel (`panel.py`) |
| 8 | Rótulo da classe: "Construtor de Armário v2" (singular) vs. mockup "Construtor de Armários" (o cabeçalho interno já usa o plural) | capturas | Cosmética | Registrado; sem mudança (rótulo do addon/i18n) |
| 9 | Ações: painel "Gerar/Aplicar/Cancelar"; mockup "Cancelar/Aplicar/OK (Gerar Blender)" | capturas | Cosmética | Sem mudança; a ação primária do painel é Gerar (altura 1.4) |
| 10 | Badge: painel "Chapa OK (2730×1810)" vs. mockup "Chapa OK (2750×1830)" | capturas | Dado, não UI | Reflete o contrato ativo (2730×1810); sem mudança |
| 11 | Ícones: o mockup usa glifos; o painel usa ícones nativos do Blender | capturas | Aceita por design | Semântica equivalente (CUBE, GRID, MOD_ARRAY, MOD_BEVEL, MESH_PLANE, ARROW_LEFTRIGHT, MOD_SOLIDIFY, TRASH, MOD_ARRAY, FULLSCREEN_ENTER); o inválido foi corrigido (#1) |

## Conclusão

O painel entrega a mesma arquitetura de informação do mockup (título, status de chapa, sete abas, medidas, montagem e
ações) e os mesmos caminhos de operação. A paridade pixel a pixel não é possível numa barra lateral nativa: paleta,
tipografia, espaçamento e a ausência de canvas são decisões do Blender — a janela do construtor é a superfície de
janela inteira. As quatro divergências corrigíveis (ícone inválido e três truncamentos) foram corrigidas e verificadas
na captura final.

**T033:** fechada.

**A004:** a paridade T033 foi executada. Dos três ensaios de GUI citados pela auditoria, `blender_012_convert_undo`
passou (OK); `blender_004_cabinet_editor_smoke` e `blender_012_library_ui` falharam por expectativas anteriores às
mudanças atuais (a guarda de "construção antiga" no editor e o card de detalhe da Biblioteca), não pelo painel.
A004 permanece LOW para esses dois ensaios desatualizados; nenhum código de produto foi alterado por eles.
