# Legacy impact: 025-criacao-posicionamento-armario

> Data: 2026-11-26
> Feature: `025-criacao-posicionamento-armario`
> Âncora: `_reversa_sdd/architecture.md` + `_reversa_sdd/domain.md` + addenda `017-construtor-armario-v2.md`
> Política de edição: só `caffmob_draw/` e `tests/`; nenhum artefato de `_reversa_sdd/` foi alterado.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/armario_v2/placement.py` | `armario_v2` (posicionamento) | `componente-novo` | LOW | Núcleo puro de orientação/caixa/raycast |
| `caffmob_draw/armario_v2/ops_placement.py` | `armario_v2` (operadores) | `componente-novo` | MEDIUM | Aviso e modal de escolha; não escreve sem confirmação |
| `caffmob_draw/armario_v2/ops.py` | `armario_v2` (Aplicar) | `regra-alterada` | MEDIUM | Gancho do aviso depois do snapshot |
| `caffmob_draw/armario_v2/ops_window.py` | `armario_v2` (janela 023) | `regra-alterada` | MEDIUM | O Aplicar da janela também pergunta |
| `caffmob_draw/armario_v2/__init__.py` | `armario_v2` (registro) | `regra-alterada` | LOW | Novo módulo em `_MODULES` |
| `caffmob_draw/library_panel/style.py` | `library_panel` (aparência) | `regra-alterada` | MEDIUM | Tokens Light do mockup |
| `caffmob_draw/library_panel/draw.py` | `library_panel` (desenho) | `regra-alterada` | MEDIUM | Consome os tokens claros |
| `caffmob_draw/library_panel/detail_core.py` | `library_panel` (card) | `regra-alterada` | LOW | Card branco/tinta café/campo creme |

## Diff conceitual por componente

- **Criar armário:** nenhuma mudança de código; `BTM_OT_ArmarioV2Abrir` já abre o painel na Vista 3D. A feature trava o
  contrato no ensaio (`len(window_manager.windows)` inalterado).
- **Aplicar:** `ops.BTM_OT_ArmarioV2Aplicar` e `ops_window.BTM_OT_ArmarioV2WindowAplicar` chamam
  `ops_placement.abrir_prompt(context)` após `undo_push`/snapshot. O gancho agenda o popup; não altera a cena.
- **Escolher:** `placement.criar_cage` cria a malha temporária; `placement.esconder/restaurar` guarda a visibilidade;
  `placement.chao` faz o raycast no piso; `placement.seta_para_yaw`/`girar` aplicam o giro; o modal confirma/cancela.
- **Cursor 3D:** `placement.no_cursor` copia `scene.cursor.location` para a raiz; as peças filhas acompanham.
- **Galeria:** `style.py` passa a expor os tokens Light; `draw.py` e `detail_core.py` usam esses tokens. Nenhuma ação,
  aba, busca, categoria, grade, seleção ou filtro foi removido.

## Preservadas

- `caffmob.cabinet_editor`/`BTM_OT_ArmarioV2Abrir` como entrada de **Criar armário** na Vista 3D.
- A janela 023 (`ops_window`, `panel_window`) e suas 7 abas; só o Aplicar ganhou o aviso.
- A hierarquia da raiz e das chapas (`build.criar_raiz`, `build.gerar`).
- Abas Biblioteca/Blocos/Texturas, busca, categorias, grade 2×3, seleção laranja, filtros Madeira/Alumínio/Blindex,
  avatar/Pin/controles da Biblioteca.
- O contrato de chapas, o plano de corte e o undo do Blender.

## Modificadas

- `ops.BTM_OT_ArmarioV2Aplicar.execute` e `ops_window.BTM_OT_ArmarioV2WindowAplicar.execute`: uma chamada a mais no
  fim, depois do snapshot.
- `armario_v2/__init__.py`: `ops_placement` após `ops_drawer_convert`.
- `library_panel/style.py`, `draw.py`, `detail_core.py`: valores de cor/claro; nenhuma assinatura pública mudou.

## Riscos de legado

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` é contrariada: o movimento é da raiz (agregado), o Aplicar continua
gravando undo, e a janela 023 continua sendo aberta só por **Abrir Janela**. A caixa de arame é temporária e não
persiste no `.blend`.
