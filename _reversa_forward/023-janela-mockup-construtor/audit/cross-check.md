# Cross-check: Janela própria do Construtor de Armários igual ao mockup

> Data: `2026-11-25` (auditoria de fechamento depois da Fase 7)
> Feature: `_reversa_forward/023-janela-mockup-construtor`
> Artefatos analisados: [`requirements.md`](../requirements.md) · [`roadmap.md`](../roadmap.md) · [`actions.md`](../actions.md)
> Evidência de execução: `_reversa_bugs/plugin-caffmob-draw/inspections/2026-11-25-janela-023/`
> Bug corrigido: `BUG-20261125-K3F7` (`_reversa_bugs/plugin-caffmob-draw/bugs/`)
>
> **Este relatório é só de leitura.** Nenhum dos três artefatos foi alterado por esta auditoria.

## 1. Resumo

| Severidade | Quantidade |
|------------|-----------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 1 |
| LOW | 1 |
| **Total** | **2** |

A Fase 7 foi executada e medida: fila (T019), seleção múltipla e lote (T020), memória por cena (T021), chrome híbrido
(T022), desempenho (T023) e regressão (T024). Todos os HIGH anteriores seguem fechados; o que resta é uma limitação de
plataforma declarada e a verificação que só uma sessão gráfica fecha.

## 2. Achados e situação

| ID | Severidade | Eixo | Descrição | Situação em 2026-11-25 |
|----|------------|------|-----------|------------------------|
| A001 | HIGH | Cobertura | D-01/RF-01: "nova janela do sistema" não era cumprida | **Resolvido** — sonda: janelas 1 → 2, `IMAGE_EDITOR` em janela separada, `VIEW_3D` do usuário intacta |
| A002 | HIGH | Cobertura | Operador de abertura sem chamador | **Resolvido** — "Abrir Janela" no painel v2 |
| A003 | HIGH | Cobertura | Faltava o chrome do mockup | **Resolvido por decisão** — híbrido (1C); T022 entregou barra de abas 4+3, barras de título/seleção/lote, ícones e espaçamento |
| A004 | HIGH | Cobertura | Aba errada e abas fechadas | **Resolvido** — aba ativa é `s.aba`, Estrutura por padrão, só a aba ativa é desenhada |
| A005 | HIGH | Cobertura | Sem clique para selecionar | **Resolvido** — `selecao.aplicar_clique`, hits do preview; clique simples e Shift medidos |
| A006 | MEDIUM | Cobertura | Corte lateral sob o painel | **Resolvido** — `visible_width` |
| A007 | MEDIUM | Cobertura | GEO só no legado | **Resolvido** — `validar` + gate em OK/Aplicar |
| A008 | MEDIUM | Sanidade | Fila sem chamador | **Resolvido** — T019: botões só enfileiram; modal processa (provado no ensaio) |
| A009 | MEDIUM | Cobertura | Fechar pelo sistema sem aviso | **Resolvido** — aviso no `_end` |
| A010 | LOW | Sanidade | T001 descrevia `open_window` sem usar | **Resolvido** |
| A011 | LOW | Cosmético | Abas verticais em vez de fileira | **Resolvido por decisão** — barra de abas clicável; fileira horizontal própria está fora de escopo |
| A012 | LOW | Cosmético | mm exibidos como 1.000.000 mm | **Resolvido** — `props.py` sem subtype |
| A013 | MEDIUM | Cobertura | NFR de desempenho sem medição | **Resolvido** — abertura **127,5 ms** (sonda gráfica), preview **0,4 ms** máx. em 54 peças/30 passadas, assert de 200 ms no ensaio |
| A014 | LOW | Cobertura | Evento de mouse real e ensaios de GUI não exercitados | **Aberto por ambiente** — o núcleo do clique/Shift é provado; o caminho `modal → LEFTMOUSE` e o desenho das abas exigem sessão gráfica |
| A016 | LOW | Cobertura | O lote mexia só nos objetos: o Gerar recriava as chapas do spec e descartava mover/espelhar/apagar sem aviso | **Resolvido** — `Armário v2.ajustes` (uid + papel + nome) é gravado no lote, entra no instantâneo e o `build.gerar` reaplica; ensaio: mover 10 mm + espelhar + 2 apagadas sobrevivem ao Gerar |
| A015 | MEDIUM | Consistência | RN-07 pede restaurar **tamanho** da janela; `Window.width/height` são readonly no Blender 5.2 (`docs/rag/.../bpy.types.Window.md#bpy.types.Window.width`) e `area_dupli` não recebe tamanho | **Aberto por plataforma** — a aba é restaurada e o tamanho fica registrado na cena; reaplicar o tamanho não é possível por script. Precisa de decisão do titular: aceitar aba+registro ou desenhar a janela numa camada própria |

## 3. Impacto e direção (o que segue aberto)

**A015 — tamanho da janela.** O requisito 4B foi cumprido na aba e no registro, não na reaplicação do tamanho. O
Blender não expõe setter: `Window.width`/`height` são somente leitura e `bpy.ops.screen.area_dupli` não tem parâmetros
de tamanho. Direção: decisão do titular no próximo ciclo — (a) aceitar o comportamento atual e reescrever a RN-07 para
"aba por cena + tamanho registrado", ou (b) abrir uma feature de janela desenhada em GPU, onde o tamanho é do próprio
desenho. Não implementar (b) sem essa decisão.

**A014 — GUI.** Uma sessão gráfica humana deve clicar com o mouse (sem passar pelo operador de seleção), abrir cada
uma das 7 abas e conferir o chrome. O que dá para provar headless já está provado.

## 4. Verificados que passaram

**Cobertura**
- RF-01 a RF-09 têm decisão e ação; T001–T024 `[X]`, T021 com a limitação declarada.
- Fila: botão enfileira sem escrever (PEÇAS intactas), modal processa, erro vira aviso e a próxima ação roda.
- Seleção: clique simples, vazio limpa, Shift acumula e alterna; lote move 10 mm, espelha o eixo X, apaga as duas peças.
- Memória: cena sem histórico abre em Estrutura; aba gravada volta ao reabrir.
- Desempenho: abertura 127,5 ms (< 2 s) e preview 0,4 ms (< 200 ms) com 54 peças.
- Lote persistente: mover/espelhar/apagar sobrevivem ao Gerar (28/28 no ensaio de fase 7); o instantâneo guarda e restaura a coleção de ajustes.

**Consistência**
- `actions.md` (24 ações) bate com as linhas da tabela; T019–T024 têm ensaio correspondente.
- Nenhum identificador fantasma; a única pendência de produto é A015.

**Coerência com o legado**
- D-01 usa o caminho do Editor de Paredes; D-06 reutiliza a máquina fila + modal UNDO (RN-CABINET_EDITOR-01).
- GEO-001/GEO-002 reutilizam as regras do editor antigo; a janela edita `Object.btm_armario` (D-02).

## 5. Limitações desta auditoria

- O clique real (modal → LEFTMOUSE) e o desenho das 7 abas não foram exercitados por um humano nesta rodada.
- O tamanho da janela não é reaplicável por script (A015).
- `ruff` não está instalado nesta máquina; `check_api.py` passou (629 arquivos, nenhuma API desconhecida).
- `blender_065_ida_e_volta.py:34` (`Somente o MOBI de ensaio em 127.0.0.1`) e `blender_ensaio_mobi.py:19` + `assert
  bpy.app.online_access, 'Use --online-mode'` continuam ambiente-gated (`CAFFMOB_BASE` vazio).
- A cena do usuário foi restaurada: duas raízes originais vazias, uma janela, `VIEW_3D` na área; as raízes `.002` e
  `.003` criadas pelas sondas foram apagadas e as peças geradas, limpas.

## 6. Aviso

Esta auditoria não alterou `requirements.md`, `roadmap.md` nem `actions.md`. A única escrita deste relatório é ele mesmo.
