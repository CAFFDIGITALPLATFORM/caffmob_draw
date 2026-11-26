# Roadmap: Criação direta, posicionamento e galeria clara do armário v2

> Identificador: `025-criacao-posicionamento-armario`
> Data: `2026-11-26`
> Requirements: `_reversa_forward/025-criacao-posicionamento-armario/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Delta cirúrgico sobre o construtor v2, sem reabrir a 023:

1. **Criar armário** continua entrando por `caffmob.cabinet_editor`/`BTM_OT_ArmarioV2Abrir`, que já abre o painel
   na Vista 3D; a feature **verifica e trava** esse contrato (sem janela nova) no ensaio de janela.
2. **Aplicar** ganha um gancho único (`ops_placement.abrir_prompt`) chamado depois do snapshot nos dois caminhos
   (painel e janela 023). O aviso é um popup com dois operadores; o gancho é **adiado por um timer** para o popup
   sobreviver ao `execute` do Aplicar e abrir com a janela/área/região da Vista 3D.
3. **Escolher** usa `placement.py` para criar uma caixa de arame temporária (8 vértices/12 arestas/0 faces), ocultar
   o armário real, acompanhar o mouse no piso por raycast e aplicar o giro das setas; o clique confirma, Esc/botão
   direito restauram.
4. **Cursor 3D** move só a raiz para o cursor; as peças filhas acompanham pela hierarquia existente.
5. **Galeria** troca os tokens de `library_panel/style.py`, `draw.py` e `detail_core.py` pela paleta Light do mockup,
   sem tocar em abas, busca, grade, seleção, filtros ou categorias.

Não há migração de dados nem contrato externo: tudo é transformação de objetos e desenho de UI.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste repositório; valem as diretrizes do projeto e a arquitetura extraída.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Edição exclusiva de `caffmob_draw/` e `tests/` | Novos módulos em `armario_v2/`, paleta em `library_panel/`, ensaios em `tests/` | respeita |
| Operações não destrutivas com `UNDO` | Confirmação grava um passo; cancelamento restaura loc/rot/hide | respeita |
| Núcleos puros testáveis fora do Blender | `placement.py` (setas/caixa) e tokens de `style.py` têm testes puros | respeita |
| Hierarquia v2 como fonte de movimento | Move-se a raiz; as peças filhas não são reposicionadas uma a uma | respeita |
| UI do Blender sem camada GPU nova | Popup, caixa `WIRE` e painel existente; nada de titlebar própria | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência | Cobre |
|----|---------|----------------|--------------------------|-------------|-------|
| D-01 | Manter **Criar armário** em `caffmob.cabinet_editor` (`BTM_OT_ArmarioV2Abrir`) e provar que ele abre na Vista 3D sem aumentar a contagem de janelas; a janela 023 fica em **Abrir Janela**. | O caminho já existe e é o que o titular pediu (“abrir a viewport direto”); mudar para a janela 023 contradiria o pedido. | Abrir a janela 023 no botão Criar armário; criar uma nova viewport temporária. | 🟢 | RF-01 |
| D-02 | Chamar `ops_placement.abrir_prompt(context)` **depois** do snapshot em `ops.BTM_OT_ArmarioV2Aplicar` e em `ops_window.BTM_OT_ArmarioV2WindowAplicar`; o aviso só encaminha e não escreve. | Um gancho único cobre os dois Aplicares; a pergunta é o pedido central. | Duplicar a pergunta em cada painel; perguntar antes do snapshot (perderia o ponto de retorno). | 🟢 | RF-02 |
| D-03 | O aviso é um `invoke_popup` de 300 px com **Escolher na viewport** e **Cursor 3D**; `abrir_prompt` acha a `VIEW_3D` em qualquer janela e usa `temp_override`, mas **agenda** a abertura num timer de 0,05 s. | O popup precisa de janela/área/região válidas; abri-lo dentro do `execute` do Aplicar fazia o popup nascer e morrer com o operador. O timer preserva o contexto e não prende o Aplicar. | Abrir direto no `execute` (morria); abrir numa janela nova (não é o pedido). | 🟢 | RF-02, RF-06 |
| D-04 | Mover/rotacionar apenas a **raiz** do armário; as peças filhas acompanham por `matrix_parent_inverse = Identity`. | A raiz é o agregado; reposicionar cada chapa quebraria a hierarquia e o undo. | Mover cada filho; criar um empty pai novo. | 🟢 | RF-03, RF-04, RF-06 |
| D-05 | No modo Escolher, criar uma malha temporária de **8 vértices, 12 arestas e nenhuma face**, `display_type='WIRE'`, nas medidas do spec; ocultar o armário real e restaurar no fim. | É a leitura de “armário em forma de linhas” sem material/sombreamento e sem duplicar as chapas. | Contorno das chapas reais; wireframe do armário inteiro; material transparente. | 🟢 | RF-03, RF-05 |
| D-06 | Raycast do mouse no plano `z = 0` a partir da região da Vista 3D; a caixa acompanha o ponto; o clique confirma. | O piso é o plano de trabalho do construtor; o raycast usa a câmera real e não depende de objetos. | Mover no plano da câmera; usar o cursor 3D a cada movimento. | 🟢 | RF-03, RF-05 |
| D-07 | Setas cardeais: `UP_ARROW=0°`, `RIGHT_ARROW=90°`, `DOWN_ARROW=180°`, `LEFT_ARROW=270°`; `R` soma 90°. O giro é em Z, no centro da raiz. | Atende o pedido e usa os nomes reais dos eventos do Blender 5.2. | Girar em incrementos arbitrários; usar `UP`/`RIGHT` (não existem). | 🟢 | RF-04 |
| D-08 | Clique esquerdo confirma; **Esc** e **botão direito** cancelam; ambos removem a caixa; o cancelamento restaura `location`, `rotation_euler` e `hide_get` anteriores. | Fecho seguro e previsível, com o mesmo estado de antes. | Só Esc; cancelar deixando a caixa; confirmar sem undo. | 🟢 | RF-05 |
| D-09 | Sem `VIEW_3D` (ou `--background`), `place_choose.execute` chama `place_cursor`; `abrir_prompt` devolve `False`. | Caminho determinístico para scripts e testes, sem exceção. | Falhar com aviso; abrir uma viewport temporária. | 🟢 | RF-07 |
| D-10 | Aplicar a paleta Light do mockup nos tokens de `library_panel/style.py`; `draw.py` e `detail_core.py` só consomem os tokens. | Uma fonte de verdade para a aparência; não muda a estrutura funcional da galeria. | Reescrever a galeria; trocar categorias; adicionar tema escuro. | 🟢 | RF-08 |
| D-11 | Provar o núcleo em Python puro (`test_placement_025`, `test_library_style_025`) e o fluxo completo em janela real (`blender_025_place`), com asserts de janelas, caixa, setas, clique e Esc. | O projeto usa ensaios puros + Blender para UI; o popup em si não é capturável por `screen.screenshot`. | Só teste headless; só inspeção manual. | 🟢 | RF-09 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| As cinco chapas são filhas da raiz e a raiz é o agregado; mover/rotacionar a raiz move o conjunto | §2, `build.py` | Se alguma peça não for filha, ela ficaria para trás; o ensaio verifica o deslocamento de uma peça junto com a raiz |
| Os eventos das setas no Blender 5.2 são `UP_ARROW`, `DOWN_ARROW`, `LEFT_ARROW`, `RIGHT_ARROW` | §4, RN-04 | O mapa falharia silenciosamente; o ensaio envia `RIGHT_ARROW` e mede 90° |
| O print do Blender não captura popups; o retorno `{'RUNNING_MODAL'}` e o gancho chamado são a prova disponível | §11 | A aparência do popup fica sem print; a auditoria declara a limitação e o teste de janela prova o encaminhamento |
| A paridade integral do mockup é escopo da 023 (D-05) | §10, RN-09 | Se o titular quiser reabrir, é feature nova, não uma correção da 025 |

Nenhuma premissa vem de `[DÚVIDA]`: as decisões de escopo desta rodada estão em §9 dos requirements.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `armario_v2` posicionamento | `caffmob_draw/armario_v2/build.py` | componente-novo | `placement.py`: orientações, caixa, raycast no piso, ocultar/restaurar |
| `armario_v2` operadores de posicionamento | `caffmob_draw/armario_v2/ops.py` | componente-novo | `ops_placement.py`: aviso, Cursor 3D, Escolher modal, `abrir_prompt` |
| `armario_v2` Aplicar | `caffmob_draw/armario_v2/ops.py` | regra-alterada | Chama o aviso depois do snapshot |
| `armario_v2` janela 023 | `caffmob_draw/armario_v2/ops_window.py` | regra-alterada | O Aplicar da janela também chama o aviso |
| `armario_v2` registro | `caffmob_draw/armario_v2/__init__.py` | regra-alterada | `ops_placement` entra em `_MODULES` |
| `library_panel` aparência | `caffmob_draw/library_panel/style.py` | regra-alterada | Tokens Light do mockup |
| `library_panel` desenho | `caffmob_draw/library_panel/draw.py`, `detail_core.py` | regra-alterada | Consomem os tokens claros; scrollbar/progresso com alpha escuro |

## 6. Delta no modelo de dados

Nenhum campo persistente novo. O posicionamento é a transformação da raiz (`location`, `rotation_euler`) e o modo
Escolher guarda estado **transitório** no operador (`_ocultos`, `_area`, `_region`, `_rv3d`, `_inicio`). Detalhe em
`data-delta.md`.

## 7. Delta de contratos externos

Nenhum: sem HTTP, fila, formato de arquivo ou API de terceiros. `abrir_prompt` é uma função Python local.

## 8. Plano de migração

n/a — não há dados antigos a migrar. O armário v2 já existe; a única mudança de estado é a transformação da raiz,
gravada no `.blend` como qualquer outra transformação e coberta pelo undo.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| O popup morrer junto com o `execute` do Aplicar | alto | média | `abrir_prompt` agenda a abertura em timer de 0,05 s com `temp_override`; o ensaio prova que o gancho é chamado |
| A janela 023 não ter uma `VIEW_3D` válida no contexto | médio | média | `_area_3d` procura em todas as janelas; se não achar, devolve `False` sem quebrar o Aplicar |
| Raycast do mouse errar o piso ou a região | médio | média | O ensaio usa o centro da região, `z = 0`, e mede o giro; o modo sem viewport cai no cursor |
| Esc deixar a caixa ou o armário oculto | alto | baixa | `_limpar` remove a caixa e restaura `hide_set`; ensaio mede loc/rot/hide |
| Setas com nomes errados | médio | baixa | Mapa usa os nomes reais; ensaio envia `RIGHT_ARROW` e mede 90° |
| Paleta clara reduzir contraste de texto/ícone | médio | média | Tokens de tinta `#2B1A0E` sobre fundos claros; o card e o painel foram olhados na captura `biblioteca_detalhe.png` |
| A mudança de estilo regredir abas/busca/grade | médio | baixa | Nenhuma mudança de layout; só tokens; card 38/38 e UI 9/9 reexecutados |

## 10. Critério de pronto

- [x] Criar armário abre a viewport sem janela nova (ensaio)
- [x] Aplicar pergunta nos dois caminhos (painel e janela 023)
- [x] Escolher: caixa de arame, mouse, setas, clique, Esc
- [x] Cursor 3D: raiz no cursor, peças junto
- [x] Fallback sem viewport
- [x] Galeria Light do mockup
- [x] Testes puros + ensaio de janela + `check_api.py`
- [x] `requirements.md`, `roadmap.md`, `actions.md` e `cross-check.md` da 025
- [x] Versão 1.34.0, CHANGELOG e tag local (sem push)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial gerada para o ciclo `/reversa-audit` | reversa |
