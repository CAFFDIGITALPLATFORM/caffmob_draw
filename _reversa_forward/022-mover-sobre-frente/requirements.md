# Requirements: Frente do objeto no Mover Sobre

> Identificador: `022-mover-sobre-frente`
> Data: `2026-11-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
>
> **Fila do Reversa: posição 3** (depois de 019 e 020; independente das duas).
>
> Origem: pedido do titular registrado em 2026-11-22 (`_reversa_sdd/audit/mover-sobre-frente-2026-11-22.md`),
> reaberto como `A009` na auditoria da 017 (`_reversa_forward/017-construtor-armario-v2/audit/mockup-e-frente-2026-11-23.md`)
> e reconfirmado como **A002/HIGH** na auditoria da 021 (2026-11-24).

## 1. Resumo executivo

A janela **Mover Sobre** decide sozinha qual lado do objeto de referência (B) é a frente: usa a convenção "−Y local"
para qualquer coisa, sem olhar a parede atrás e sem perguntar. Isso funciona para os módulos da biblioteca, que
nascem nessa convenção, e falha em três casos reais: parede desenhada no sentido inverso, objeto importado
(SketchUp/FBX/grupo solto) e malha autoral fora da convenção. Quando falha, a vista Frontal mostra a lateral e o
objeto arrastado (A) **é girado para a base errada** — o erro não é só de desenho.

Esta entrega faz a janela **descobrir a frente por evidência** (parede atrás primeiro, eixo do objeto depois),
**perguntar** quando houver conflito ou ausência de evidência, **guardar a resposta no objeto** para valer sempre, e
**mostrar** qual lado está sendo tratado como frente.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/audit/mover-sobre-frente-2026-11-22.md` | Achados A001–A008: vistas fixas em `VIEWS = {'front': ('FRONT',0,2), 'plan': ('PLAN',0,1)}`, parede atrás ignorada, ausência de propriedade de frente e de pergunta | 🟢 |
| `_reversa_forward/017-construtor-armario-v2/requirements.md:420` | Decisão do titular: idprop `btm_front_yaw` em graus locais, **válida para todo o add-on** e preservada ao salvar e reabrir | 🟢 |
| `_reversa_sdd/questions.md:1501-1503` | Mesma decisão, com a recomendação de alcance inicialmente restrito ao Mover Sobre | 🟢 |
| `caffmob_draw/move_over/ops_dialog.py:43` | `VIEWS` fixo: a frente é sempre XZ local | 🟢 |
| `caffmob_draw/move_over/scene.py` | `b_frame = _frame(b)`, `box_b`/`a_local_box` no referencial de B; `_target_matrix` compõe `b_rot @ orientation` (gira A) | 🟢 |
| `caffmob_draw/move_over/encostar.py:12-19,47` | `SIDE_AXIS`/`SIDE_FACE` mapeiam "Na frente"/"Atrás" para o eixo Y cru (índice 1) | 🟢 |
| `caffmob_draw/selection/classify.py` (`module_library`) | Classificador que distingue módulo de biblioteca de objeto importado/grupo solto | 🟢 |
| `caffmob_draw/walls2d/apply.py:123` | Parede gravada com a espessura à esquerda do sentido; módulos do lado −Y da face | 🟢 |
| `CLAUDE.md` / `AGENTS.md` | Operadores com `UNDO`, `unregister` desfaz tudo, texto e comentários em português, ruff 120 | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|----------------|
| Projetista de interiores | Encostar um móvel novo num módulo já posicionado | Seleciona A e B, abre o Mover Sobre; a janela mostra a frente do módulo e encosta o móvel do lado certo |
| Projetista que importa móvel | Usar um móvel de SketchUp/FBX como referência | A janela percebe que não é módulo de biblioteca, pergunta qual lado é a frente, guarda a escolha e não pergunta de novo |
| Marceneiro | Encostar um módulo na parede da sala | A frente vem da parede atrás (a face que olha para a sala), sem perguntar |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 (Precedência da frente):** a frente de B é decidida nesta ordem: (1) frente gravada no objeto pelo usuário;
   (2) parede atrás de B — **sem limite de distância**, desde que o comprimento da parede cubra o pé de B em planta —
   quando a normal da parede aponta para o lado de B; (3) eixo do objeto (comportamento atual, `yaw = 0`);
   (4) sem evidência confiável → **perguntar**. 🟢
   - Origem: auditoria de 2026-11-22 §4 (`RF-F01`, `RF-F02`, `RF-F03`).
   - Tipo: nova.
2. **RN-02 (Frente gravada vence sempre):** a escolha do usuário é gravada em `obj['btm_front_yaw']` (graus, local ao
   objeto, salvo no `.blend` como idprop) e tem precedência sobre parede e eixo em todas as sessões, inclusive depois
   de salvar e reabrir. Vale para **todo o add-on** (esclarecimento de 2026-11-24). 🟢
   - Origem: decisão da 017 (`requirements.md:420`) e `_reversa_sdd/questions.md:1501`.
   - Tipo: nova.
3. **RN-03 (Referencial das vistas pela frente decidida):** as vistas Frontal e Planta passam a ser calculadas no
   referencial `b_frame @ Rz(yaw)`. Com `yaw = 0` o resultado é **idêntico** ao de hoje, preservando posições salvas,
   campos absolutos e ensaios existentes. 🟢
   - Origem: auditoria de 2026-11-22 §5.2.
   - Tipo: alterada.
4. **RN-04 (Semântica dos lados preservada):** "Na frente" e "Atrás" continuam significando o lado da frente e o lado
   de trás **do objeto**, com o remapeamento dos índices de eixo aplicado na base da vista (arraste, ímã, cota, alças
   e giro por vista usam a mesma base). 🟢
   - Origem: auditoria de 2026-11-22 A005/A007.
   - Tipo: alterada.
5. **RN-05 (Perguntar só quando necessário, sem bloquear):** a pergunta aparece quando (a) não há parede atrás e B não
   é módulo de biblioteca, ou (b) parede e eixo discordam acima de **45°** (esclarecimento de 2026-11-24). A pergunta
   é um **diálogo com os quatro lados e a opção "Usar o eixo"**. Cancelar a pergunta não altera a cena e não grava
   propriedade. 🟢
   - Origem: auditoria de 2026-11-22 `RF-F03`/`RF-F07`.
   - Tipo: nova.
6. **RN-06 (B é parede):** quando a referência é a parede e a janela veio de um **arraste**, a frente é o lado de onde
   A chegou; **sem arraste** (janela aberta pelo menu) ou com A sobre a espessura da parede, **perguntar**
   (esclarecimento de 2026-11-24). 🟢
   - Origem: auditoria de 2026-11-22 §5.1 regra 6.
   - Tipo: nova.
7. **RN-07 (Indicador de frente):** as duas vistas exibem um sinal explícito do lado tratado como frente (seta/linha
   "frente"), para que o usuário veja a decisão sem abrir campo nenhum. 🟢
   - Origem: auditoria de 2026-11-22 A008/`RF-F05`.
   - Tipo: nova.
8. **RN-08 (Padrões transversais):** textos novos em `pt_BR` com tradução `en_US`; operadores que alteram a cena com
   `UNDO`; desenho sem escrever na cena; handlers removidos no `unregister`. 🟢
   - Origem: `CLAUDE.md`/`AGENTS.md` e padrão das features 017/021.
   - Tipo: mantida.

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Decidir a frente de B por precedência: propriedade gravada → parede atrás dentro do limite → eixo do objeto → perguntar (RN-01) | Must | Módulo de biblioteca sem propriedade e sem parede abre com a frente no eixo (−Y) e sem pergunta; o mesmo módulo com `btm_front_yaw = 90°` abre com a frente no lado correspondente | 🟢 |
| RF-02 | Gravar a escolha do usuário em `obj['btm_front_yaw']` e reutilizá-la em todas as sessões (RN-02) | Must | Escolher a frente, fechar o arquivo e reabrir: a janela abre com a mesma frente e não pergunta de novo | 🟢 |
| RF-03 | Calcular as vistas Frontal e Planta no referencial da frente decidida, idêntico ao atual quando `yaw = 0` (RN-03) | Must | Um ensaio de posicionamento existente (módulo, parede, canto) produz o mesmo `delta` e a mesma matriz com a mudança aplicada, `yaw = 0` | 🟢 |
| RF-04 | Manter o significado de "Na frente"/"Atrás" do objeto e o ímã, a cota, as alças e o giro por vista coerentes com a base decidida (RN-04) | Must | Com a frente a 90°, "Na frente" encosta A no lado que a janela mostra como frente, e o ímã puxa para esse lado | 🟢 |
| RF-05 | Perguntar a frente quando não houver evidência confiável ou houver conflito parede × eixo, sem alterar a cena ao cancelar (RN-05) | Must | Objeto importado sem parede atrás abre a pergunta; cancelar mantém a posição de A, não grava `btm_front_yaw` e não muda a cena | 🟢 |
| RF-06 | Tratar B = parede pela direção de onde A chegou; perguntar quando A estiver sobre a parede (RN-06) | Must | Mover A contra a face frontal de uma parede e abrir a janela: a frente é essa face; com A centrado na parede, a janela pergunta | 🟡 |
| RF-07 | Exibir indicador de frente nas duas vistas (RN-07) | Should | As vistas mostram a marca de frente coerente com o lado usado no posicionamento | 🟢 |
| RF-08 | Internacionalização e `UNDO` nos fluxos novos (RN-08) | Must | Em `en_US` os rótulos da pergunta e do indicador aparecem traduzidos; `Ctrl+Z` depois de gravar a frente devolve o estado anterior | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | A decisão da frente (varredura de paredes + classificação) deve custar menos de 5 ms para 200 paredes e não rodar a cada quadro do modal | A janela redesenha durante o arraste; a decisão é tomada ao abrir e só é recalculada quando B muda | 🟡 |
| Compatibilidade | `yaw = 0` não pode alterar nenhuma posição salva, campo absoluto ou ensaio existente do Mover Sobre | Auditoria de 2026-11-22 §5.2 | 🟢 |
| Integridade | Perguntar e cancelar nunca deixa a cena meio alterada nem grava propriedade parcial | Padrão não destrutivo das features 017/021 | 🟢 |
| Observabilidade | A decisão deve dizer de onde veio a frente (propriedade, parede ou eixo) num tooltip/status da janela | Facilita diagnosticar caso o usuário discorde do resultado | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Módulo de biblioteca sem parede mantém o comportamento atual (RF-01, RF-03)
  Dado um módulo de biblioteca sem btm_front_yaw e sem parede atrás
  Quando o projetista abre o Mover Sobre com esse módulo como referência
  Então a frente é o eixo do objeto (yaw = 0), sem pergunta
  E a posição final de A é a mesma que a versão atual produziria

Cenário: Objeto importado sem evidência pergunta a frente e guarda a resposta (RF-01, RF-02, RF-05)
  Dado um objeto importado que não é módulo de biblioteca e não tem parede atrás
  Quando o projetista abre o Mover Sobre
  Então a janela pergunta qual lado é a frente
  Quando o projetista escolhe um lado
  Então a escolha é gravada em btm_front_yaw e a janela passa a usar esse lado
  E ao reabrir o arquivo a janela mantém a escolha sem perguntar de novo

Cenário: Parede atrás define a frente sem pergunta (RF-01, RF-06)
  Dado um armário encostado numa parede, a até o limite de proximidade do fundo
  Quando o projetista abre o Mover Sobre com o armário como referência
  Então a frente é a face da parede que olha para o lado do armário
  E nenhuma pergunta é exibida

Cenário: Conflito entre parede e eixo pergunta antes de posicionar (RF-05)
  Dado um objeto cuja convenção de eixo aponta para o lado oposto da parede atrás (desacordo acima da tolerância)
  Quando o projetista abre o Mover Sobre
  Então a janela pergunta qual lado é a frente
  E cancelar não altera a posição de A nem grava propriedade

Cenário: "Na frente" continua sendo a frente do objeto com a base girada (RF-04)
  Dado um objeto com btm_front_yaw de 90 graus
  Quando o projetista arrasta A para "Na frente" na vista Frontal
  Então A encosta no lado que a janela mostra como frente
  E o ímã, a cota e as alças usam esse mesmo lado
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Sem a precedência, os outros requisitos não têm regra única |
| RF-02 | Must | Sem persistir, o usuário responde a mesma pergunta em toda sessão |
| RF-03 | Must | É a correção do defeito: a vista e a matriz de A na base certa |
| RF-04 | Must | Corrigir só o desenho gira A errado (auditoria A006) |
| RF-05 | Must | Perguntar é o caminho para os casos sem evidência, sem bloquear |
| RF-06 | Should | Caso real de parede usada como referência; pode entrar depois da base |
| RF-07 | Should | Sem indicador o usuário não vê a decisão |
| RF-08 | Must | Padrão de qualidade do add-on |

## 9. Esclarecimentos

### Sessão 2026-11-24

- **Q:** D1 — A que distância a parede atrás de B ainda define a frente?
  **R:** Qualquer distância: a parede atrás sempre vence (sem limite), desde que ela corra atrás do pé de B.
- **Q:** D2 — Quando parede e eixo discordam, a partir de quanto o add-on pergunta?
  **R:** Acima de 45°.
- **Q:** D3 — Como a janela pergunta qual lado é a frente?
  **R:** Diálogo com os quatro lados e a opção "Usar o eixo".
- **Q:** D4 — A frente gravada vale onde?
  **R:** Em todo o add-on.
- **Q:** D5 — Quando B é parede e A não veio de arraste, qual lado vale?
  **R:** Perguntar.

## 10. Lacunas

Nenhuma lacuna ou dúvida pendente após a sessão de esclarecimentos de 2026-11-24.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-requirements` a partir da auditoria de 2026-11-22 e do achado A002 da auditoria da 021 | reversa |
| 2026-11-24 | Esclarecimentos de `/reversa-clarify` integrados (D1–D5 fechadas, 0 dúvidas restantes) | reversa |
