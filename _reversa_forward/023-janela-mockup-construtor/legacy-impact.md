# Legacy Impact: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Gerado por: `/reversa-coding` (T012)

## Arquivos criados (novos)

| Arquivo | Responsabilidade |
|---------|------------------|
| `caffmob_draw/armario_v2/window.py` | Sessão da janela própria, open/close, draw handler do preview, fila de pedidos |
| `caffmob_draw/armario_v2/ops_window.py` | Operadores Abrir/Aplicar/Cancelar/OK, modal com timer |
| `caffmob_draw/armario_v2/panel_window.py` | Painel de 7 abas na região UI do Image Editor, empty state, rodapé OK/Aplicar/Cancelar |
| `caffmob_draw/armario_v2/preview.py` | Desenho do preview dividido (frontal + corte lateral) com paleta pixel-perfeito do mockup |
| `tests/test_janela_023_open.py` | Teste puro de sessão e janela_existe |

## Arquivos modificados

| Arquivo | Alteração |
|---------|-----------|
| `caffmob_draw/armario_v2/__init__.py` | Acrescentado `window`, `ops_window`, `panel_window` a `_MODULES` e documentado no docstring |

## Arquivos do legado NÃO modificados (reutilizados inalterados)

| Arquivo | Uso na feature 023 |
|---------|-------------------|
| `caffmob_draw/armario_v2/ops.py` | Operadores de construção (Montar Caixa, Inserir Divisoria, etc.), `snapshot_de`, `aplicar_snapshot`, `gerar_armario`, `semear_contrato` |
| `caffmob_draw/armario_v2/props.py` | PropertyGroups `BTM_PG_ArmarioV2` (spec, chapas, aba, enums) |
| `caffmob_draw/armario_v2/build.py` | `criar_raiz`, `raiz_de`, `e_raiz`, `limpar` |
| `caffmob_draw/canvas2d/window.py` | `open_window`, `close_later`, `window_alive` (abrir/restaurar janela Image Editor) |
| `caffmob_draw/armario_v2/spec.py`, `vaos.py`, `chapas.py`, `conferencia.py`, `gavetas.py`, `internos.py`, `portas.py`, `corredica.py` | Núcleos puros de cálculo e validação |

## Impacto sobre componentes existentes

- **Nenhum componente existente foi alterado.** A feature apenas acrescenta novos módulos à cascata de registro do `armario_v2` (`_MODULES`).
- O painel da Vista 3D (`armario_v2/panel.py`) continua inalterado; a janela própria é uma interface alternativa sobre os mesmos dados (`Object.btm_armario`).
- Não há mudança de modelo de dados (`data-delta.md`: nenhum campo novo, nenhum removido, nenhuma migração).
- Não há contrato externo afetado (tudo é local: API Python do Blender, arquivos blend/JSON).

## Arquivos de auditoria gerados

| Arquivo | Conteúdo |
|---------|----------|
| `progress.jsonl` | Log de progresso das 12 ações executadas |
| `regression-watch.md` | Pontos de atenção para regressão e testes sugeridos |
