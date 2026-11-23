# Auditoria: fidelidade ao mockup e frente no Mover Sobre

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-23`
> Artefatos analisados: `requirements.md`, `roadmap.md` e `actions.md` da 017
> Referências externas: `mockup_construtor_armarios.html` (anexo do titular) e `_reversa_sdd/audit/mover-sobre-frente-2026-11-22.md`
> Este relatório é datado e não substitui o `cross-check.md`, que fica como retrato da segunda passada.

## 1. Resumo

| Severidade | Qtd | Assunto |
|------------|-----|---------|
| CRITICAL | 0 | Nenhum conflito com regra 🟢 do legado, contrato externo ou ciclo |
| HIGH | 5 | Quatro requisitos `Must` sem caminho de uso ou sem peça gerada; frente do Mover Sobre não implementada |
| MEDIUM | 3 | Conteúdo do mockup sem equivalente, lista de peças sem consumidor, simulação por gaveta ausente |
| LOW | 1 | Docstring do painel atribui ao HUD uma inserção que não existe |

As duas perguntas do titular têm resposta objetiva:

1. O Mover Sobre **não** ganhou a definição de frente. Continua na convenção de −Y local e não pergunta nada ao usuário.
2. O construtor novo **não** reproduz o design do mockup. Usa a sidebar nativa do Blender, decisão registrada na RN-22,
   e perdeu quatro blocos funcionais do mockup (inserção, matriz, simulação por gaveta e lista de peças).

## 2. Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Cobertura | RF-07 é `Must` e exige inserir divisória e prateleira, inclusive matriz. `vaos.matriz`, `vaos.inserir_vertical` e `vaos.inserir_horizontal` existem no núcleo, mas **nenhum** consumidor no produto: só testes e fumaças os chamam. O Duplicar do menu copia uma divisória que já existe, então nem a primeira divisória pode ser criada pela interface | `caffmob_draw/armario_v2/vaos.py:173,189,204`; `caffmob_draw/armario_v2/menu.py:98`; nenhuma chamada em `ops.py`, `panel.py` ou `hud.py` |
| A002 | HIGH | Cobertura | RF-09 é `Must` e pede quantidade, altura do bloco e modelo por gaveta. `gavetas.bloco` não tem consumidor no add-on; o painel só lista as gavetas já gravadas e nada no produto cria um bloco. A fumaça cria as gavetas por Python | `caffmob_draw/armario_v2/gavetas.py:67`; `panel.py:_gavetas`; nenhuma chamada a `.bloco(` em `caffmob_draw/` |
| A003 | HIGH | Cobertura | RF-12 é `Must` e manda inserir cabideiro, calceiro, sapateira e maleiro. `internos.inserir` não tem consumidor; o painel apenas edita internos que já existam, e nenhum caminho os cria | `caffmob_draw/armario_v2/internos.py:48`; `panel.py:_internos` |
| A004 | HIGH | Cobertura | RF-05 pede dimensões, montagem e orientações de contra-frente e peça de trás. O `spec` calcula as duas, mas `build.pecas` **nunca emite** contra-frente nem peça de trás, e `props.py` não tem flag de presença para elas. A ação T020 também não as prevê: requisito sem ação correspondente | `spec.py:217,222`; `build.py:pecas`; `props.py:BTM_PG_ArmarioV2`; `actions.md` T020 |
| A005 | MEDIUM | Consistência | A aba Estrutura do mockup tem componentes com presença e espessura por peça (contra-frente, travessa traseira e rodapé). O painel traz espessura por papel e as duas orientações, mas não as presenças. Rodapé não existe em requisito nenhum: é lacuna de escopo, não defeito de implementação | `mockup_construtor_armarios.html#renderPanel`; `panel.py:_estrutura`; `requirements.md` §5 |
| A006 | MEDIUM | Cobertura | `resumo.lista_de_pecas` não tem consumidor: a lista de peças do mockup (modal de cutlist com nome, medidas e marca de fora-da-chapa) não existe no add-on. O RF-19 é cumprido pelo adaptador de corte, então o requisito passa, mas a função fica sem uso e o usuário não vê a lista | `resumo.py:30`; `panel.py` só usa `linha_estado`; `hud.py` mostra uma peça por vez |
| A007 | LOW | Consistência | A docstring de `panel.py` diz que a inserção múltipla é do HUD (T025), mas o HUD só alterna a estrutura, inspeciona a peça e realça a seleção. A afirmação não corresponde ao código nem a `actions.md` | `panel.py` (docstring, fim); `hud.py` (docstring) |
| A008 | MEDIUM | Consistência | As sub-abas de Divisões existem, mas `Múltipla` não tem a matriz do mockup (grade 5 × 5, linhas × colunas, prioridade por eixo). Em Gavetas não há simulação por linha (modelo mais Abrir/Fechar) nem ação de atualizar ou excluir o bloco. A aba Portas também perdeu o Abrir/Fechar que o mockup tem ali | `panel.py:_divisoes`; `panel.py:_gavetas`; `panel.py:_portas`; mockup `renderPanel` |
| A009 | HIGH | Coerência | A frente do objeto no Mover Sobre **não foi implementada**. Não existe `move_over/frente.py`, `ops_front.py` nem propriedade de frente; `VIEWS` continua fixo em `(X, Z)` e `(X, Y)`, a parede atrás de B não é consultada e não há pergunta ao usuário. Os achados A001 a A008 da auditoria de 2026-11-22 continuam abertos. Fica fora da 017, mas responde à pergunta do titular | `_reversa_sdd/audit/mover-sobre-frente-2026-11-22.md`; `move_over/ops_dialog.py:43`; `move_over/scene.py:73`; `move_over/props.py` (sem campo de frente) |

## 3. Impacto e direção de correção

### A001, A002 e A003 (inserção)

Os três requisitos são `Must` e a interface do construtor não tem como criar divisória, prateleira, gaveta nem interno:
o painel edita o que já está gravado e o menu duplica o que já existe. Na prática, um armário criado do zero só chega à
caixa e ao fundo; os demais blocos só aparecem quando vêm de um módulo de biblioteca pela ponte. O teste de fumaça não
pega porque cria as coleções por Python.

Direção: `/reversa-plan` para abrir ações de inserção (cards e matriz do mockup na aba Divisões, bloco de gavetas na aba
Gavetas, botões de interno na aba Internos), reutilizando `vaos.matriz`, `gavetas.bloco` e `internos.inserir`, que já
estão testados. Se a decisão for deixar a inserção fora do escopo, `/reversa-clarify` para rebaixar RF-07, RF-09 e RF-12.

### A004 (contra-frente e peça de trás)

O `spec` calcula comprimento e altura das duas peças, mas elas nunca viram malha e não há presença no modelo de dados.
Quem olhar a cena não encontra a contra-frente nem a travessa traseira prometidas na aba Estrutura do mockup.

Direção: `/reversa-plan` para flag de presença em `props.py` mais a emissão em `build.pecas` (com teste em
`tests/test_017_build.py`), ou `/reversa-clarify` para reduzir o RF-05 a cálculo.

### A009 (frente no Mover Sobre)

A pergunta "está funcionando conforme ajustado?" tem resposta objetiva: **não**. O pedido foi auditado em 2026-11-22 e
nada foi implementado desde então; a janela continua chamando de frente o −Y local de qualquer objeto, ignora a parede
atrás e não pergunta nada ao usuário. O bloqueio não é técnico: falta decisão sobre as perguntas 99 (precedência e
limite de "perto") e 100 (onde guardar a escolha). O impacto é maior que o desenho: como A herda a rotação de B, uma
frente errada gira o objeto, não só a vista.

Direção: `/reversa-clarify` para fechar as perguntas 99 e 100; depois `/reversa-plan` para as ações da proposta da
auditoria (núcleo `frente.py`, operador, propriedade e a seta de frente nas duas vistas).

## 4. Verificados e corretos

- **Cobertura de decisões:** as 20 decisões do `roadmap.md` têm ação no `actions.md`; as 40 ações apontam para
  dependências existentes, sem ciclo, e os 27 `[//]` não compartilham arquivo alvo.
- **Identificadores:** todos os RN e RF citados nos três documentos existem no `requirements.md`.
- **Requisitos com caminho de uso:** RF-01, RF-03, RF-04, RF-06, RF-10, RF-11 (pelo campo do separador), RF-13 a RF-26
  têm operador, painel, menu, HUD ou adaptador que os exercita; RF-20 tem a fumaça de reabertura.
- **Mockup, paridade de informação:** as sete abas, as sub-abas de Divisões e Gavetas, os dez modelos de frente, os
  quatro afastadores independentes, o separador por colunas e linhas, as opções de deslizante e de fundo e o aviso de
  chapa estão no painel, com os mesmos nomes do mockup.
- **Decisão de superfície:** a RN-22 e a D-05 mandam a superfície ser a própria vista 3D, sem janela 2D. O painel nativo
  do Blender é consequência dessa decisão, não um desvio acidental.
- **Corrediça e reabertura:** RN-08, RN-10, RN-17 e RF-10, RF-20 fechados por T036 a T040, com fumaças verdes.

## 5. O que esta auditoria não fez

- Não alterou `requirements.md`, `roadmap.md`, `actions.md`, `data-delta.md`, `onboarding.md` nem nenhum arquivo de
  `caffmob_draw/` ou `tests/`.
- Não executou o Blender nem abriu o mockup num navegador: a comparação de design é de marcação e de código de desenho,
  não visual. Nenhuma captura foi feita.
- Não substituiu o `cross-check.md` da segunda passada, para não apagar o registro de A012 e A013.
