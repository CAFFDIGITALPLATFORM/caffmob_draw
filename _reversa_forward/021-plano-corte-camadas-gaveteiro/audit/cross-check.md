# Cross-check: 021-plano-corte-camadas-gaveteiro

> Data: 2026-11-24, revisado em 2026-11-25 (re-verificação de interface executada, não presumida)
> Feature: `_reversa_forward/021-plano-corte-camadas-gaveteiro`
> Artefatos analisados: [requirements.md](../requirements.md) · [roadmap.md](../roadmap.md) · [actions.md](../actions.md)
> Evidência de execução: `_reversa_bugs/cabinet_editor/inspections/2026-11-24-debugger/`

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 1 |

Este relatório fecha os achados da auditoria anterior em vez de apenas repeti-los. Placar medido nesta máquina:
suíte pura **1582/1582**, OK com 5 pulados (fontes do MOBI só disponíveis na pasta de entrega),
`blender_021_mcp_e2e.py` **52/52** (inclui a nova prova do RF-08), `blender_022_mover_sobre_frente.py` **10/10**,
`blender_017_armario_smoke.py` OK e a sonda de interface **22/22**.

Revisão de 2026-11-25: suíte pura **1600 ensaios** com uma única falha ambiente-gated (`test_sessao_mobi.py:19`),
harness novo de interface `tests/blender_021_ciclo_debug.py` **12/12**, `blender_023_fase7.py` **36/36**,
`blender_021_mcp_e2e.py` **52/52**, `blender_017`/`blender_066`/`blender_067` OK e `blender_022` **10/10**. O placar de
severidade não mudou: A006 entrou já **Resolvido**.

## Achados e situação

| ID | Severidade | Eixo | Descrição | Situação |
|---|---|---|---|---|
| A001 | MEDIUM | Consistência | `T032` estava `[X]` ("zero regressões") sem que a suíte tivesse sido executada; a execução real achou cinco falhas puras e duas no Blender | **Resolvido** — suíte executada e registrada em `actions.md`/`roadmap.md` §10.1 |
| A002 | MEDIUM | Cobertura | `RF-08` (pé-direito e espessura padrão na aba Ferramentas) não tinha verificação automatizada | **Resolvido** — seção 12 de `tests/blender_021_mcp_e2e.py` prova painel e valores de abertura do editor; 52/52 |
| A003 | MEDIUM | Consistência | `RF-10` não registrava que, com um móvel legado ativo, "Criar Armário" cai no diálogo antigo e cria um `BTM_Cabinet` | **Resolvido** — `requirements.md` §5 e o cenário Gherkin passam a declarar a condição e a RN-23 |
| A004 | LOW | Cobertura | Os ensaios que provam aparência/janela (`blender_004_cabinet_editor_smoke.py`, `blender_012_convert_undo.py`, `blender_012_library_ui.py`) exigem GUI e não rodaram nesta rodada | **Aberto por ambiente** — só uma sessão gráfica fecha |
| A005 | LOW | Sanidade | Os números "187/187" e "186/186" das rodadas anteriores contavam arquivos de ensaio, não ensaios | **Resolvido** — `roadmap.md` §10 usa a contagem medida de ensaios |
| A006 | LOW | Cobertura | As perguntas de interface (editor abre, botão de colisão, criar/redimensionar/editar peças) tinham sido respondidas por memória, sem comando | **Resolvido** — `tests/blender_021_ciclo_debug.py` 12/12 e `blender_023_fase7` 36/36; falhas restantes reproduzidas na asserção exata e classificadas como ambiente-gated |

## Fechamento

### A001 — done sem execução

A suíte pura foi executada de verdade (`unittest discover`, 1582 ensaios) e as falhas de ensaio no Windows
viraram cartões corrigidos: `BUG-20261124-7H3K` (ordenação case-insensitive de `Path`) e `BUG-20261124-Q2MF`
(`select` em pipe). A reexecução final fechou **1582/1582, OK**, com 5 pulados por fontes do MOBI que só existem na
pasta de entrega. Na suíte Blender, as duas falhas restantes foram reproduzidas na asserção exata e são
ambiente-gated: `blender_065_ida_e_volta.py:34` ("Somente o MOBI de ensaio em 127.0.0.1") e
`blender_ensaio_mobi.py:19`.

### A002 — RF-08 sem prova

Fechado com execução, não com inspeção de código. A seção 12 do `blender_021_mcp_e2e.py`:

1. desenha a aba Ferramentas com um layout falso e confirma que `ceiling_height` e `default_wall_thickness` são
   expostos;
2. grava 2,85 m e 180 mm na cena, abre o `caffmob.wall_editor` sem GUI (o `poll` é relaxado só no ensaio e
   `window.open_editor` levanta o erro esperado) e confirma que `window_manager.btm_wall_editor.new_height` e
   `new_thickness` nascem com esses valores.

Resultado medido: **52/52, exit 0**.

### A003 — RF-10 incompleto

O requisito e o cenário Gherkin agora dizem o comportamento real: sem móvel legado ativo, "Criar Armário" abre o
Construtor v2; com móvel legado ativo, mantém de propósito o diálogo antigo da RN-23
(`caffmob_draw/library_panel/ops_cabinet.py:40-46`). A redação absoluta anterior não descrevia o código.

### A006 — interface afirmada por memória

A rodada de 2026-11-25 executou o que faltava: operador de colisão sem erro e alternando as duas chaves, desenho do
cabeçalho emitindo o botão com o rótulo do estado, montar caixa do zero (5 chapas, Gerar idempotente), redimensionar
para 900 mm sem perder peça nem degenerar, lote movendo e devolvendo cada peça e as sete abas registradas. O item de
menu "Abrir janela do construtor" é emitido em `menu.py:149`; no `--background` o operador de abrir recusa por `poll`
(contexto), o que é a fronteira da GUI e não um defeito. As três falhas restantes foram reproduzidas:
`blender_065_ida_e_volta.py:34` (MOBI em 127.0.0.1), `blender_ensaio_mobi.py:19` (`CAFFMOB_BASE` + `--online-mode`) e
`test_sessao_mobi.py:19` (438 ≠ 384, permissão NTFS). Relatório em
`_reversa_bugs/cabinet_editor/inspections/2026-11-25-debugger-f021/report.md`.

### A004 — ensaios de GUI

Permanece aberto e é o único item LOW. Os três ensaios de janela e a paridade pixel a pixel com
`mockup_construtor_armarios.html` (T033) exigem sessão gráfica; esta rodada não os executou e não afirma paridade
visual. O que está provado sem GUI: as sete abas, o título "Construtor de Armários" e o acesso ao Plano de Corte.

### A005 — contagem de arquivos

Os números antigos contavam arquivos de ensaio. O placar atual conta ensaios executados e está repetido em
`roadmap.md` §10/§10.1.

## Itens verificados que passaram

### Cobertura
- RF-01 a RF-14 têm decisão no roadmap e pelo menos uma ação no actions.
- Todo cenário Gherkin de `requirements.md#7` mapeia para um RF com ação correspondente.
- Nenhum identificador citado no roadmap (`D-01` a `D-09`, `RN-01` a `RN-12`) está ausente do requirements.

### Consistência
- Termos estáveis entre os três documentos ("plano de corte", "Marcenaria", "Arquitetura", "gaveteiro").
- Os alvos de arquivo de `T021`/`T022` existem: `caffmob_draw/cutting/ops_opcut.py`,
  `caffmob_draw/texture_library/ops_sync_missing.py`.

### Coerência com o legado
- `RN-COLLISION-08` atendida e verificada em execução (operador, desenho do cabeçalho e tradução).
- `RN-STICK-10/11/12` cobertas por `stick/release_guard_core.py` e pela fumaça da 021.
- Armários em `Marcenaria` e `e_raiz()` desacoplado do nome da coleção — verificado na sonda.

### Sanidade do actions
- Dependências apontam para IDs existentes; nenhum ciclo.
- As 32 ações de implementação estão `[X]` e todas têm arquivo alvo; resta **T033**, aberta de propósito.

## Aviso

Esta auditoria não alterou `requirements.md`, `roadmap.md`, `actions.md`, `data-delta.md`, `interfaces/` nem
`investigation.md`. As correções de conteúdo acima foram feitas pelos ciclos anteriores desta mesma rodada
(`/reversa-debugger`, `/reversa-requirements`, `/reversa-plan`, `/reversa-to-do`), não por este relatório.
