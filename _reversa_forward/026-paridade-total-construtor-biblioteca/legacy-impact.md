# Legacy impact: 026

## 1. Código tocado

| Área | Mudança | Risco controlado |
|------|---------|------------------|
| `armario_v2/window.py` | Estado de vista/tema/laterais, escalas, `registrar_movimento`, `registrar_duplicata` | Campos de sessão; não muda o snapshot nem a fila. |
| `armario_v2/preview.py` | Tema, cor do papel em tempo de desenho, filtro laterais, vista única | Default `SPLIT/LIGHT`; desenho antigo preservado. |
| `armario_v2/props.py` / `build.py` | `ajustes.duplicada` e recriação da cópia no Gerar | Default falso; sem duplicata o fluxo é idêntico. |
| `armario_v2/ops_window.py` | Novos operadores, menu, arraste | O modal 023 mantém seleção, ESC e fila; arraste só começa com peça. |
| `armario_v2/panel_window.py` | Titlebar, abas em linha, toolbar, medida/duplicar, export | Painéis existentes e validação GEO intactos. |
| `library_panel/*` | Categorias, tema, grade 2×3, alvo 44 px | Linhas/ambientes continuam no card; texturas seguem responsivas. |
| i18n | 36 chaves novas em `armario_v2.json` | Cobertura 3/3; pt_BR/en_US preenchidos. |

## 2. Features anteriores

- **023:** fila/modal, seleção múltipla, lote, memória por cena e GEO passam em `blender_023_fase7` 36/36.
  A alteração de abas não removeu nenhum painel; os ids das abas continuam os mesmos.
- **025:** Criar→Aplicar→Escolher/Cursor 3D, caixa de arame, setas, clique e Esc passam em
  `blender_025_place` 16/16. Nenhuma linha do fluxo de placement foi alterada.
- **012/014:** a UI da Biblioteca continua abrindo, criando categoria e criando armário (9/9); o card continua
  inserindo por clique/arraste e recusando chapa (38/38). As categorias mudaram por requisito do documento.

## 3. Contratos

- `caffmob.armario_v2_window_*`: novos operadores aditivos; `_WindowOperator.poll` exige sessão.
- `parity_core.payload`: contrato do JSON versionado; não lê `bpy`.
- `btm_armario.ajustes.duplicada`: campo persistido, default falso.
- `btm_library.theme`: estado de `WindowManager`, não persistido no `.blend`.

## 4. Riscos residuais

- O tema do chrome nativo do Blender não é repintado por add-on; as áreas desenhadas pelo add-on são.
- O arraste é provado por eventos sintéticos no modal; não foi feito clique manual humano nesta rodada.
- A grade 2×3 é da aba Blocos; texturas preservam a grade responsiva.
