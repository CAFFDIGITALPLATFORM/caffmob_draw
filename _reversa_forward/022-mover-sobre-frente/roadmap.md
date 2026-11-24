# Roadmap: Frente do objeto no Mover Sobre

> Identificador: `022-mover-sobre-frente`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/022-mover-sobre-frente/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A correção entra em três camadas, sem tocar em geometria nem em posição salva: um **núcleo puro** decide a frente de B
por evidência (propriedade → parede → eixo → ambíguo); a **janela** passa a montar o referencial das vistas como
`b_frame @ Rz(yaw)` e traduz índices de eixo entre a base da vista e a base do objeto; e a **propriedade** `btm_front_yaw`
guarda a escolha do usuário, com um operador de pergunta que só aparece quando a decisão é ambígua. Com `yaw = 0` o
resultado é byte a byte o de hoje, o que mantém posições salvas e ensaios existentes válidos.

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Edição exclusiva no pacote `caffmob_draw/` | Deltas em `move_over/` e testes em `tests/` | respeita |
| Núcleo puro testável fora do Blender | A decisão da frente vive em `move_over/frente_core.py`, sem `bpy` | respeita |
| Não destrutivo com `UNDO` | A propriedade é um idprop no objeto; gravar a frente é um passo de desfazer | respeita |
| Desenho não escreve na cena | `draw`/vistas só leem a decisão; quem grava é o operador da pergunta | respeita |
| Internacionalização e limpeza no `unregister` | Rótulos novos nos catálogos; nenhum handler novo permanente | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Núcleo puro `caffmob_draw/move_over/frente_core.py` com `yaw_of(normal_xy)`, `wall_candidates(obj, walls)`, `decide(matrix_b, box_b, walls, stored_yaw, module_like)` → `(yaw, origem, ambíguo)` e constantes `GAP_MAX`/`DISAGREE_MAX` | Deixa a regra testável sem Blender e centraliza os limites que o clarify vai fixar | Decidir dentro de `scene.py` (regra presa ao `bpy`, sem ensaio puro) | 🟢 |
| D-02 | `scene.MoveOver` monta `view_frame = b_frame @ Rz(yaw)` e calcula `box_b`/`a_local_box` nesse referencial; helpers `to_view`/`from_view` convertem entre a base do objeto (onde `delta` continua salvo) e a base da vista | Mantém o dado salvo intacto e, com `yaw = 0`, o resultado atual | Regravar `delta` na base da vista (invalida posições salvas) | 🟢 |
| D-03 | Propriedade `obj['btm_front_yaw']` (graus, float, idprop) com leitura em `decide`; operador `caffmob.move_over_front` grava e marca `UNDO` | Decisão já tomada na 017 (`requirements.md:420`); idprop sobrevive ao `.blend` sem migração | Campo novo em `data/properties.py` (exige registro e migração de cena) | 🟢 |
| D-04 | Pergunta por `invoke_props_dialog` com os quatro lados (e "usar o eixo"), disparada na abertura quando `ambíguo`; cancelar não grava nada | Fluxo já usado em `ops_resize.py`; sem menu novo e sem bloquear o arraste | Menu rápido no canto da janela (mais código de desenho e de foco) | 🟡 |
| D-05 | Indicador de frente desenhado nas duas vistas (`_draw_view`) a partir de `view_frame` | Fecha o achado A008 e dá ao usuário a leitura da decisão | Só tooltip (não resolve a dúvida no momento do arraste) | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Limite de proximidade da parede em 100 mm e desacordo tolerado de 45° | §9 (D1, D2) | Perto/longe e conflito mudam de comportamento; o clarify fixa os dois antes do código |
| A frente gravada vale para todo o add-on | §9 (D4) / 017 `requirements.md:420` | Se valer só no Mover Sobre, outros fluxos continuam com a convenção antiga |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `move_over` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | componente-novo | `frente_core.py` (decisão pura) e o operador de frente |
| `move_over` | idem | regra-alterada | `scene.py` passa a usar `view_frame` com `yaw`; `ops_dialog.py` traduz índices de eixo e desenha o indicador |
| `move_over/encostar.py` | idem | regra-alterada | `SIDE_AXIS`/`SIDE_FACE` lidos na base da vista, sem trocar o significado de "Na frente" |
| `data/properties.py` | idem | contrato-alterado | idprop `btm_front_yaw` documentada (sem PropertyGroup novo) |

## 6. Delta no modelo de dados

- `Object['btm_front_yaw']` (float, graus, local): ausência = "sem escolha do usuário". Nenhuma propriedade existente
  muda de nome ou de tipo; arquivos antigos abrem com `yaw = 0`.

## 7. Plano de migração

1. **Arquivos já salvos:** sem `btm_front_yaw` a decisão cai nas regras 2–4 de RN-01, e `yaw = 0` reproduz o
   comportamento atual — nada a migrar.
2. **Módulos de biblioteca:** continuam sem pergunta quando não há parede (são `module_like`).
3. **Objetos importados:** passam a perguntar uma vez; a resposta fica no objeto.

## 8. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Remapear índices de eixo trocar "Na frente" por "Atrás" | alto | média | Tabela de remapeamento única em `frente_core`/`scene`, com ensaio de encostar nos quatro lados |
| Pergunta aparecer em fluxo que hoje é silencioso (módulo de biblioteca) | médio | baixa | Só perguntar quando `module_like` for falso ou quando houver conflito |
| Varredura de paredes a cada quadro do modal pesar | médio | baixa | Decidir ao abrir a janela e ao trocar B; cache da decisão no `MoveOver` |
| Indicador de frente poluir a vista | baixo | média | Marca discreta (seta + rótulo curto) apenas nas duas vistas |

## 9. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `yaw = 0` reproduz os ensaios atuais do Mover Sobre (mesmo `delta` e mesma matriz)
- [ ] Ensaios puros de `frente_core` cobrindo propriedade, parede perto/longe, eixo, conflito e cancelar
- [ ] Fumaça no Blender 5.2: pergunta, gravação, reabertura e `Ctrl+Z`
- [ ] Cobertura i18n sem chave faltante e `unregister` sem handler órfão
- [ ] `cross-check.md` sem CRITICAL nem HIGH

## 10. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-plan` | reversa |
