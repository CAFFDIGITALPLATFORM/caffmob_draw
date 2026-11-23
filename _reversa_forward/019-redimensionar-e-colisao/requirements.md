# Requirements: Redimensionar armário, veio do armário e colisão à mão

> Identificador: `019-redimensionar-e-colisao`
> Data: `2026-11-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
>
> **Fila do Reversa: posição 1** (depois da 018).
>
> **Segunda entrega do fatiamento da 018.** Esta feature é a edição do armário e do item que já existem: mudar as
> medidas como conjunto, trocar o veio do armário inteiro e resolver a colisão no topo da seleção. Depende da 018
> apenas para o veio em graus; a colisão não depende de nenhuma das outras.

## 1. Resumo executivo

Hoje o armário só muda de medida pelo painel, que regenera todas as peças, e o usuário que quer ajustar a largura
acaba indo em Item e mexendo em campo, com peças se deslocando. A colisão, por sua vez, exige descer até um painel
burocrático mesmo quando o usuário já está com o objeto selecionado na vista.

Esta entrega dá ao armário um comando de **redimensionar como conjunto** (diálogo e alças), um comando de **veio do
armário** por papel e põe a escolha de colisão **Herdar/Ativada/Desativada no topo da seleção**, sem duplicar a
propriedade que já existe.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/selection/requirements.md#RN-23` e `#RN-24` | Redimensionar muda só a largura do elemento e estica agregados; não existe redimensionar de armário inteiro | 🟢 |
| `caffmob_draw/ui/ops_resize.py` | Diálogo "Redimensionar" entrega a largura a `selection/resize.resize`; nada em `armario_v2/` trata redimensionamento (busca por `resize`/`redimension` na pasta não retorna nada) | 🟢 |
| `caffmob_draw/armario_v2/build.py:gerar` | Refaz todas as chapas a partir do spec; é o ponto que garante "conjunto" no redimensionar | 🟢 |
| `caffmob_draw/armario_v2/props.py` | `BTM_PG_ArmarioProps` (medidas, vãos, gavetas, portas, fundo) e `GRAIN_ITEMS` para o veio | 🟢 |
| `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-17` | Todo parâmetro do armário fica gravado nele; reabrir devolve o mesmo estado | 🟢 |
| `caffmob_draw/data/properties.py:collision_override` | Já existe `INHERIT`/`ON`/`OFF` em `Object.btm_plane`, com rótulos Herdar/Ativa/Desativada | 🟢 |
| `_reversa_sdd/collision/requirements.md#RN-10` e `#RN-11` | Chave global `scene.btm_settings.collision_global`; só `OFF` age por item e a global desligada vence tudo | 🟢 |
| `caffmob_draw/ui/sidebar_check.py` | A colisão aparece na seção Verificar ("Colisões"), com a chave "Impedir atravessamento" e o Diagnóstico técnico | 🟢 |
| `caffmob_draw/ui/object_properties.py:_draw_position` | O campo de colisão do item some quando o painel de colisão está visível | 🟢 |
| `caffmob_draw/operators/viewport_hud.py` | HUD por `POST_PIXEL` na `VIEW_3D` (`_draw_hud`), já com desenho acima do objeto e leitura do alvo por `ui/context_menu.item_actions` | 🟢 |
| `caffmob_draw/cutting/part_roles.py:part_grain` | O veio de corte vem de `btm_part.grain` (`H`/`V`/`NONE`); é o que o plano de corte lê | 🟢 |
| `CLAUDE.md` / `AGENTS.md` | Operadores com `UNDO`, `unregister` desfaz tudo, texto novo em português | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro na produção | Mudar medida sem perder o desenho | Digita 1200 × 2200 × 600 e o armário inteiro se redistribui |
| Projetista | Ajustar o veio do móvel | Troca o veio de todas as peças do armário de uma vez |
| Usuário do dia a dia | Desligar a colisão de um item | Seleciona o objeto e muda Herdar/Ativada/Desativada na própria vista |

## 4. Regras de negócio novas ou alteradas

1. **RN-12:** **Redimensionar armário** tem duas entradas com a mesma regra: diálogo com largura, altura e
   profundidade, e **alças de arraste na viewport**. Nos dois caminhos o armário é regenerado como conjunto: vãos,
   gavetas, portas e internos acompanham pelas regras do spec, sem esticar peça solta nem deixar chapa fora da caixa. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-23); `caffmob_draw/ui/ops_resize.py`;
     `_reversa_sdd/selection/requirements.md#RN-23`; `caffmob_draw/armario_v2/build.py`
   - Tipo: nova (o redimensionamento atual só muda a largura do elemento)
2. **RN-13:** O armário tem um comando de **veio do armário** que troca o veio de todas as peças de uma vez por papel
   (estrutura, portas, fundo, internos), sem tocar em peça de outro armário. 🟢
   - Origem: `caffmob_draw/cutting/part_roles.py:part_grain`;
     `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-19`
   - Tipo: nova
3. **RN-16:** A colisão do objeto é editável **no topo da seleção**: com um item selecionado, o HUD mostra Herdar /
   Ativada / Desativada com o valor atual, e a mesma escolha aparece na seção Colisões junto das ferramentas de
   colisão, sem duplicar propriedade. 🟢
   - Origem: `caffmob_draw/data/properties.py:collision_override`; `_reversa_sdd/collision/requirements.md#RN-11`
   - Tipo: alterada (a propriedade existe; falta o acesso à mão)
4. **RN-17:** "Ativada" continua **não vencendo** a chave global desligada, como a colisão do legado determina, mas o
   HUD e a seção dizem em texto que a global está desligada e que a escolha por item não terá efeito. 🟢
   - Origem: `_reversa_sdd/collision/requirements.md#RN-10` e `#RN-11`; CA-19
   - Tipo: mantida
5. **RN-18:** Todo texto novo entra em português no código e no catálogo em `pt_BR` e `en_US`; todo operador que muda
   a cena declara `UNDO` e todo handler novo tem remoção no `unregister`. 🟢
   - Origem: `caffmob_draw/data/i18n.py`; `CLAUDE.md`
   - Tipo: mantida

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-11 | Redimensionar armário por diálogo de medidas e por alças de arraste, regenerando o conjunto (RN-12) | Must | Mudar 1000 × 2000 × 550 para 1200 × 2200 × 600 pelo diálogo ou arrastando a alça de largura mantém vãos, gavetas e portas distribuídos e nenhuma peça solta fora da caixa | 🟢 |
| RF-12 | Veio do armário em um comando, por papel (RN-13) | Should | Trocar o veio do armário para vertical altera estrutura, portas, fundo e internos daquele armário somente | 🟢 |
| RF-15 | Colisão Herdar/Ativada/Desativada no HUD acima da seleção, refletindo o valor atual (RN-16) | Must | Selecionar um item mostra as três opções com a atual marcada; trocar no HUD muda `btm_plane.collision_override` e a verificação passa a respeitar | 🟢 |
| RF-16 | A mesma escolha na seção Colisões, junto das ferramentas de colisão, sem campo duplicado (RN-16) | Must | A seção Colisões mostra o seletor do item ativo e o diagnóstico; o campo antigo não aparece duas vezes | 🟢 |
| RF-17 | HUD e seção avisam em texto quando a chave global desliga a colisão (RN-17) | Should | Com "Evitar Sobreposição" desligada, o HUD mostra que a escolha por item não tem efeito | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Redimensionar não reconstrói duas vezes: o spec novo é calculado uma vez e a geração substitui as peças existentes | `armario_v2/build.py` gera por spec; gerar em laço multiplicaria o custo | 🟢 |
| Desempenho | O HUD de colisão desenha em todo redesenho da vista sem consultar o estado de colisão a cada quadro | `operators/viewport_hud.py` já usa leitura barata do alvo | 🟡 |
| Compatibilidade | Alvo Blender 5.2; leitura de dimensão por biblioteca como em `selection/editing.py`; sem campo novo na cena | `CLAUDE.md`; `_reversa_sdd/selection/requirements.md#RN-18` | 🟢 |
| Robustez | Medida fora de faixa, vão menor que a peça interna e armário sem peças recusam com mensagem, sem geometria parcial | `selection/resize.py` já levanta `ValueError` com faixa | 🟢 |
| Ciclo de vida | Handlers novos (HUD, alças) têm remoção no `unregister`; nenhuma propriedade nova em `bpy.types.*` sem remoção | `CLAUDE.md` | 🟢 |
| Idiomas | Catálogo novo em `pt_BR` e `en_US`, contextos padrão e de operador | `caffmob_draw/data/i18n.py` | 🟢 |
| Custo | Nenhuma chamada a modelo de IA ou serviço externo | Diretriz de controle de custo do projeto | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Redimensionar o armário como conjunto
  Dado um armário de 1000 por 2000 por 550 com dois vãos e quatro gavetas
  Quando o usuário usa Redimensionar e digita 1200 por 2200 por 600
  Então os dois vãos continuam divididos e as quatro gavetas redistribuídas no novo vão
  E nenhuma peça fica fora da caixa nem se move para fora do armário

Cenário: Redimensionar pelas alças
  Dado um armário selecionado com o Redimensionar ativo
  Quando o usuário arrasta a alça de largura até 1200 mm
  Então o armário acompanha durante o arraste, com as peças redistribuídas
  E a medida final é a mesma que o diálogo mostraria

Cenário: Redimensionar valor inválido
  Dado o diálogo Redimensionar
  Quando o usuário digita uma profundidade menor que a espessura das chapas
  Então o operador recusa com a mensagem de faixa
  E o armário continua com as medidas anteriores

Cenário: Veio do armário
  Dado dois armários com textura igual
  Quando o usuário troca o veio de um deles para vertical
  Então só as peças daquele armário giram
  E o plano de corte do outro continua com o veio anterior

Cenário: Colisão no topo da seleção
  Dado um item selecionado com colisão Herdar
  Quando o usuário abre o HUD do objeto
  Então as opções Herdar, Ativada e Desativada aparecem com Herdar marcada
  Quando ele escolhe Desativada
  Então a verificação deixa de listar aquele item
  E a escolha sobrevive a salvar e reabrir

Cenário: Colisão global desligada
  Dado "Evitar Sobreposição" desligada na cena
  Quando o usuário escolhe Ativada para um item
  Então o HUD informa que a escolha não tem efeito enquanto a global estiver desligada
  E a verificação continua sem rodar
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-15, RF-16 | Must | A colisão é usada todo dia e hoje exige procurar painel; é o menor custo da feature |
| RF-11 | Must | É o pedido literal: redimensionar sem mexer nas peças |
| RF-12, RF-17 | Should | Completam o uso sem bloquear a primeira entrega |
| Alças em todas as três medidas (largura, altura e profundidade) | Should | A largura resolve o caso comum; altura e profundidade podem entrar depois |
| Redimensionar vão por vão | Could | O pedido fala em armário |

## 9. Esclarecimentos

### Sessão 2026-11-23

- **Q:** O pedido "redimensionar um armário e o…" terminou truncado. Como o redimensionamento deve funcionar?
  **R:** Diálogo de medidas e alças de arraste na viewport; nos dois caminhos o armário é regenerado como conjunto.
- **Q:** A colisão deve continuar respeitando a chave global desligada?
  **R:** Sim; o HUD apenas informa que a escolha por item não terá efeito.

## 10. Lacunas

- 🟡 A faixa de valores do Redimensionar e o comportamento quando a medida nova torna um vão menor que a peça interna
  ficam para o `/reversa-plan`.
- 🟡 O gesto das alças (quantas, em que eixos e como cancelar) fica definido no plano.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-23 | Criada pelo fatiamento da 018: RN-12, RN-13, RN-16, RN-17 e RF-11, RF-12, RF-15, RF-16, RF-17 movidos com IDs preservados | reversa |
