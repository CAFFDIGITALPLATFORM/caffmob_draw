# Roadmap: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/023-janela-mockup-construtor/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Entregar uma **nova janela do sistema** (Image Editor sem imagem, restaura a área ao fechar) que hospeda o Construtor de Armários v2, com preview dividido (frontal + corte lateral), painel lateral de 7 abas (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos), empty state "Janela de Armário Vazia" e botões OK/Aplicar/Cancelar, replicando pixel-perfeito o mockup em `novo_arm_building/.../mockup_construtor_armarios.html`. A janela edita o **armário v2** (`armario_v2`, `Object.btm_armario`) e não o módulo legado `cabinet_editor`/`btm_cabinet`.

O caminho é delta sobre o existente: reaproveitar os núcleos puros do armário v2 (`caffmob_draw/armario_v2/`) — divisões, extras, gavetas, internos, deslizantes, fundo, montagem — e adicionar uma camada de interface própria em janela separada, aberta via `canvas2d.window.open_window` (conforme `architecture.md#canvas2d` e `domain.md#canvas2d` RN-CANVAS2D-08), com a máquina de estado de fila + modal UNDO já documentada em `state-machines.md` (Editor de armário) e `cabinet_editor/design.md` (F-01 a F-03).

## 2. Princípios aplicados

Não existe `.reversa/principles.md` neste projeto. Não há princípios obrigatórios a verificar nem conflitos a registrar.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| n/a | Não há `principles.md` definido | n/a |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|---------------|--------------------------|-------------|
| D-01 | Abrir uma **nova janela do sistema** com Image Editor sem imagem (via `canvas2d.window.open_window`) em vez de ocupar a área da Vista 3D atual. | Requisito Q1 (nova janela do sistema) e RN-CANVAS2D-08 (`domain.md#canvas2d`). | Ocupar a Vista 3D com fallback ao fechar. | 🟢 (implementado e medido em 2026-11-25: janelas 1 → 2) |
| D-02 | Editar o **armário v2** (`armario_v2`, `Object.btm_armario`) em vez do módulo legado `cabinet_editor`/`btm_cabinet`. | Requisito Q2 e adendo `017-construtor-armario-v2.md` vigente (armário v2 é o motor atual; editor 2D saiu do registro). | Módulo legado `cabinet_editor`. | 🟢 (adendo vigente) |
| D-03 | Replicar **pixel-perfeito** (paleta, espaçamento, ícones iguais ao HTML do mockup). | Requisito Q3. | Comportamento equivalente com visual livre. | 🟡 (premissa Q3 aceita no clarify) |
| D-04 | Reaproveitar a máquina de estado fila + modal UNDO do editor antigo (`cabinet_editor/ops_editor.py`, F-01 a F-03) para o novo construtor em janela. | `state-machines.md` Editor de armário e `cabinet_editor/design.md` descrevem pedidos, instantâneo EditorState, OK/Aplicar/Cancelar. | Inventar nova máquina de estado. | 🟢 |
| D-05 | Paridade **híbrida**: chrome funcional do Blender (barra de ferramentas, lista de peças, seleção, abas em painéis) + paleta, espaçamento e ícones do mockup onde a UI permitir; sem titlebar própria nem abas horizontais. | Decisão de 2026-11-25 (opção 1C); o Image Editor não permite titlebar/fileira horizontal sem uma camada de desenho própria. | Réplica pixel a pixel. | 🟢 (decidido; execução em T022) |
| D-06 | Integrar a fila + modal UNDO (RN-02): todo botão do painel enfileira e um único modal processa, em vez de chamar o operador direto. | Decisão de 2026-11-25 (opção 2A); `state-machines.md` e RN-CABINET_EDITOR-01. | Manter chamadas diretas e só documentar. | 🟢 (decidido; execução em T019) |
| D-07 | Seleção múltipla com Shift/Ctrl+clique e ações em lote (mover, apagar, espelhar) num único passo de desfazer. | Decisão de 2026-11-25 (opção 3B); RN-06. | Seleção única apenas. | 🟢 (decidido; execução em T020) |
| D-08 | Persistir por cena a última aba ativa e o último tamanho da janela; cena sem histórico abre em Estrutura no tamanho padrão. | Decisão de 2026-11-25 (opção 4B); RN-07. | Persistir globalmente ou não persistir. | 🟢 (decidido; execução em T021) |

## 4. Premissas

Nenhuma premissa decorrente de `[DÚVIDA]` não resolvida: as 3 dúvidas foram esclarecidas na sessão de `/reversa-clarify` (Q1 → nova janela do sistema; Q2 → armário v2; Q3 → pixel-perfeito).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| n/a | n/a | n/a |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `armario_v2` UI (painel Vista 3D) | `_reversa_sdd/architecture.md#Limites e organização` (Mobiliário) | componente-extenso | Adicionar nova janela própria (Image Editor) que espelha o construtor v2; o painel da Vista 3D permanece inalterado |
| `canvas2d.window` | `_reversa_sdd/domain.md#canvas2d` (RN-CANVAS2D-08) | contrato-reutilizado | Abrir janela própria com Image Editor sem imagem |
| `armario_v2/panel.py` | `caffmob_draw/armario_v2/panel.py` (inferido do addenda 017) | componente-extenso | Espelhar as 7 abas e o preview dividido na nova janela, com botão "Abrir Janela" no painel da Vista 3D |
| `armario_v2/window.py` + `ops_window.py` | `caffmob_draw/armario_v2/window.py` | componente-extenso | Janela nova via `canvas2d.window.open_window`, modal na janela nova, seleção por clique e fechamento avisado |
| `armario_v2/preview.py` + `selecao.py` + `validar.py` | `caffmob_draw/armario_v2/preview.py` | componente-novo | Preview com largura visível, ordem de pintura, hits de clique e GEO-001/GEO-002 |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhuma mudança de modelo de dados; a janela edita o mesmo `Object.btm_armario` e `Scene.btm_armario_contrato` do armário v2 (adendo 017-construtor-armario-v2.md).
- Detalhe completo em: `_reversa_forward/023-janela-mockup-construtor/data-delta.md`

## 7. Delta de contratos externos

Nenhum contrato externo (HTTP / fila / gRPC / GraphQL) é afetado — tudo é local (API Python do Blender, arquivos blend/JSON locais). Diretório `interfaces/` omitido.

## 8. Plano de migração

n/a — não há migração de dados; o modelo de dados do armário v2 já existe e é reutilizado inalterado.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Duplicação de UI (painel Vista 3D + nova janela) editando o mesmo armário v2 simultaneamente | médio | médio | Travar sessão: se uma janela do construtor estiver aberta, bloquear a outra (poll/reflow_handler já rejeita sessão aberta) |
| Pixel-perfeito dependendo de recursos CSS/HTML não disponíveis no Blender Image Editor | médio | alto | Mapear apenas o que é renderizável em UI Blender (panels/operators); a decisão (réplica em GPU x paridade funcional) está na §10 do requirements, pendente do clarify |
| Regressão no armário v2 existente | baixo | baixo | Apenas adicionar janela; não alterar núcleos puros nem painel existente |

## 10. Critério de pronto

- [x] Todas as ações do `actions.md` marcadas `[X]` — T019–T024 fechadas (T021 com a limitação readonly no tamanho)
- [x] `cross-check.md` executado sem CRITICAL nem HIGH (2026-11-25, depois da correção)
- [x] `regression-watch.md` gerado e atualizado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

### 10.1 Placar medido em 2026-11-25

| Prova | Resultado |
|-------|-----------|
| Suíte pura (`unittest discover`) | 1593 ensaios, 1 falha ambiente-gated (`test_sessao_mobi`, permissão POSIX no NTFS), 5 pulados |
| `tests/test_janela_023_core.py` | 11/11 |
| Sonda MCP da janela | janelas 1 → 2, `aba_ativa = "Construtor Armário"`, `hits = 10`, seleção "Lateral esquerda" |
| `probe_editor_021.py` | 22/22 (colisão, criar do zero, resizing 5 → 5 sem peça achatada, edições 5 → 33) |
| `blender_017_armario_smoke.py` | OK |
| `blender_021_mcp_e2e.py` | 52/52 |
| `blender_023_janela_open.py` | OK |
| `blender_065_ida_e_volta.py` / `blender_ensaio_mobi.py` | falham na asserção de ambiente (MOBI 127.0.0.1 / `--online-mode`), não em código do produto |
| Meta de desempenho (NFR) | **medida**: abertura 127,5 ms na sessão gráfica; preview 0,4 ms máx. (54 peças, 30 passadas) — `probe_janela_023_desempenho.py` e `tests/blender_023_desempenho.py` |
| Fase 7 | T019–T024 executadas; `blender_023_fase7.py` 22/22; ensaio de desempenho com assert da meta |

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-11-25 | D-01 marcada como implementada; D-05 (chrome funcional x pixel) registrada; placar de execução em §10.1 | reversa |
| 2026-11-25 | Esclarecimentos: D-05 vira híbrida e entram D-06 (fila/modal), D-07 (seleção múltipla) e D-08 (memória por cena) | reversa |
