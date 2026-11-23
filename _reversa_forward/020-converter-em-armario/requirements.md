# Requirements: Converter em armário

> Identificador: `020-converter-em-armario`
> Data: `2026-11-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
>
> **Fila do Reversa: posição 2** (depois da 019).
>
> **Terceira entrega do fatiamento da 018.** É a feature de maior risco do conjunto: cria geometria nova a partir de
> malha do usuário. Por isso vem depois da 018 (materiais e UV confiáveis) e da 019 (armário editável no lugar).

## 1. Resumo executivo

O addon só cria armário pelos próprios caminhos: o construtor v2 gera do zero e as bibliotecas montam os próprios
módulos. Móvel que chega por importação ou modelagem à mão fica fora do sistema e não pode ser editado como armário.

Esta entrega converte a seleção em armário v2: o usuário aponta o papel de cada chapa e a porta pelo menu de botão
direito, o motor novo gera as peças a partir das medidas da cena, a origem fica preservada e o resultado pode ir para
a biblioteca no mesmo fluxo.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/selection/requirements.md#RN-01` e `#RN-02` | Classificação em 12 tipos e 5 bibliotecas; raiz de módulo por tag ou `btm_plane.object_kind == 'MODULE'`; malha sem marca é `OTHER` | 🟢 |
| `caffmob_draw/armario_v2/props.py` | `BTM_PG_ArmarioParte` (papel, veio, fitas, material) e as flags de presença `lateral_esq_ativa`, `lateral_dir_ativa`, `base_inf_ativa`, `base_sup_ativa` e `fundo_ativo` | 🟢 |
| `caffmob_draw/armario_v2/build.py:gerar` | Emite as chapas por spec, uma malha por peça, com papel, material e veio gravados | 🟢 |
| `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-17` e `#RN-23` | Parâmetros gravados no armário; móvel da construção antiga não é convertido pelo motor novo | 🟢 |
| `caffmob_draw/armario_v2/menu.py` | Gancho em `VIEW3D_MT_object_context_menu` filtrado pelo armário v2 da seleção | 🟢 |
| `caffmob_draw/ui/context_menu.py` | Menu de botão direito unificado desde a 005: submenu do objeto, ações do tipo, Redimensionar e plano de inserção | 🟢 |
| `caffmob_draw/object_library/ops.py:BTM_OT_ObjectLibraryAdd` | Salva a seleção ou um arquivo 3D na biblioteca, com nome, categoria, origem, licença e miniatura | 🟢 |
| `_reversa_sdd/customize/requirements.md#RN-14` | Módulo salvo = `.blend` + manifesto JSON + `.png` em `extension_path_user(<pacote>, "modules")` | 🟢 |
| `_reversa_sdd/customize/requirements.md#RN-02` e `#RN-05` | Material por nome, com precedência peça > vão > grupo; escolha sobrevive a refazer o módulo | 🟢 |
| `caffmob_draw/armario_v2/portas.py` e `baixas` | Portas de abrir com dobradiça e sentido, deslizante de 2 a 4 folhas, exclusividade entre as duas | 🟢 |
| `_reversa_sdd/collision/requirements.md#RN-02` | Peças do mesmo grupo não colidem; a origem preservada não pode entrar na colisão como móvel solto | 🟢 |
| `CLAUDE.md` / `AGENTS.md` | Operadores com `UNDO`, `unregister` desfaz tudo, texto novo em português | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro projetista | Reaproveitar móvel vindo de fora | Importa um `.obj`, clica com o botão direito, escolhe Converter em armário e aponta as chapas |
| Projetista | Guardar o móvel convertido | Confirma a oferta de adicionar à biblioteca e reusa o armário noutro projeto |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A conversão usa a **cena aberta como base**: medidas, posição, orientação e materiais vêm da
   **seleção**, que é lida como **um móvel** — várias chapas soltas selecionadas viram as peças de um mesmo armário.
   A geometria lida é a **avaliada**, com os modificadores da origem aplicados (espelho, array, subdivisão), e
   nenhum valor é pedido antes de o usuário apontar os papéis. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-23); `_reversa_sdd/selection/requirements.md#RN-01`
   - Tipo: nova
2. **RN-02:** As peças originais **não são apagadas** pela conversão: continuam na cena como origem, marcadas como
   fora do corte (`btm_cut_exclude`) e ocultas na vista, **com os modificadores originais intactos**, e o armário v2
   nasce como objeto novo no mesmo lugar. Um passo de desfazer devolve a cena inteira. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-23); princípio não destrutivo do projeto e
     precedente `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-23`
   - Tipo: nova
3. **RN-03:** Papéis atribuíveis: **fundo**, **lateral esquerda**, **lateral direita**, **base inferior**, **base
   superior** e **porta**. O usuário aponta cada papel **clicando a peça na viewport** dentro do diálogo, com a peça
   sob o cursor destacada. Cada papel estrutural aceita **uma** peça; a porta aceita uma ou duas (dupla). Papel não
   atribuído significa peça inexistente, com as mesmas flags de presença da 017. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-23); `caffmob_draw/armario_v2/props.py`
   - Tipo: nova
4. **RN-04:** A porta é definida junto da conversão com três eixos: **tipo** (de giro, de correr, basculante),
   **direção** (esquerda, direita, dupla, para o giro e o basculante; esquerda→direita ou direita→esquerda para o
   correr) e **sentido de abertura** (para dentro ou para fora). Sem porta apontada, o armário nasce sem frente. 🟢
   - Origem: `_reversa_sdd/customize/requirements.md#RN-07`; `caffmob_draw/armario_v2/portas.py`
   - Tipo: nova
5. **RN-05:** A entrada da conversão é o **menu de botão direito** da peça, com toque longo equivalente em tela
   sensível. O item "Converter em armário" só aparece quando a seleção é malha que não pertence a módulo, e é
   recusado com aviso quando já é armário v2. 🟢
   - Origem: `caffmob_draw/ui/context_menu.py`; `caffmob_draw/armario_v2/menu.py`;
     `_reversa_sdd/selection/requirements.md#RN-02`
   - Tipo: alterada (o menu de contexto ganha a ação)
6. **RN-06:** A conversão grava no armário novo o **material e o veio herdados** de cada peça de origem, e a textura
   de origem continua aplicada depois de gerar as peças. 🟢
   - Origem: `_reversa_sdd/customize/requirements.md#RN-02` e `#RN-05`; materiais da 018
   - Tipo: nova
7. **RN-07:** Ao concluir a conversão, o mesmo fluxo oferece **Adicionar à biblioteca**, reaproveitando o operador
   de biblioteca existente com nome, categoria e miniatura; recusar a oferta não desfaz a conversão. 🟢
   - Origem: `caffmob_draw/object_library/ops.py:BTM_OT_ObjectLibraryAdd`;
     `_reversa_sdd/customize/requirements.md#RN-14`
   - Tipo: alterada (o operador passa a aceitar o armário recém-convertido)
8. **RN-18:** Todo texto novo entra em português no código e no catálogo em `pt_BR` e `en_US`; todo operador que muda
   a cena declara `UNDO` e todo handler novo tem remoção no `unregister`. 🟢
   - Origem: `caffmob_draw/data/i18n.py`; `CLAUDE.md`
   - Tipo: mantida

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | "Converter em armário" no menu de botão direito e no toque longo, visível só para malha que não é módulo, lendo a seleção inteira como um móvel (RN-01, RN-05) | Must | Selecionar um `.obj` importado mostra a ação; selecionar três chapas soltas mostra a ação e converte as três; selecionar um armário v2 não mostra; num armário antigo a ação aparece como conversão para o motor v2 | 🟢 |
| RF-02 | Diálogo de papéis por clique na viewport, com destaque da peça sob o cursor: fundo, laterais, bases superior e inferior e porta (RN-03) | Must | Clicar cinco peças e confirmar cria o armário com cinco papéis; deixar a base superior sem clicar gera o armário sem ela | 🟢 |
| RF-03 | Porta definida na conversão por tipo (giro, correr, basculante), direção e sentido de abertura (RN-04) | Must | Porta de correr com duas folhas nasce com as duas folhas e a direção escolhida; basculante nasce com o eixo no topo | 🟢 |
| RF-04 | Conversão não destrutiva, com as origens preservadas ocultas, fora do corte e com os modificadores intactos, em um passo de desfazer (RN-02) | Must | Depois de converter, cada peça original continua na cena, oculta, fora da lista de corte e com o mesmo empilhamento de modificadores; um Ctrl+Z devolve a cena ao estado anterior | 🟢 |
| RF-05 | Material e veio herdados das peças de origem sobrevivem à geração (RN-06) | Must | Peça de origem com textura "Arauco Anis" gera armário cujas chapas mantêm a mesma textura | 🟢 |
| RF-06 | Oferta "Adicionar à biblioteca" ao fim da conversão, usando o operador de biblioteca existente (RN-07) | Should | Confirmar a oferta grava o armário na biblioteca com nome, categoria e miniatura; recusar não desfaz a conversão | 🟢 |
| RF-18 | Textos novos em português e inglês nos contextos padrão e de operador (RN-18) | Must | Com a interface em inglês, conversão e oferta de biblioteca aparecem traduzidas e o teste de cobertura de i18n passa | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Converter um armário de até 40 peças em até 1 s | Mesma ordem de grandeza da geração da 017 (0,5 s) mais a leitura da seleção | 🟡 |
| Compatibilidade | Alvo Blender 5.2; geometria avaliada por depsgraph, sem aplicar modificador na malha do usuário | `CLAUDE.md`; decisão de preservar a origem com o empilhamento intacto | 🟢 |
| Manutenibilidade | Papéis, validação de seleção e montagem do spec em núcleo puro, testável fora do Blender | Padrão da 017 | 🟢 |
| Robustez | Seleção vazia, malha sem face, papel repetido e porta em peça de outro móvel devolvem mensagem, sem geometria parcial | `armario_v2/menu.py` já recusa com `WARNING` | 🟢 |
| Compatibilidade de dados | Armas armário convertido abre em versão anterior sem perder as peças (o armário v2 é o mesmo motor da 017) | `_reversa_forward/017-construtor-armario-v2/requirements.md#RN-17` | 🟢 |
| Ciclo de vida | Handlers novos (destaque de papel, diálogo) têm remoção no `unregister` | `CLAUDE.md` | 🟢 |
| Idiomas | Catálogo novo em `pt_BR` e `en_US`, contextos padrão e de operador | `caffmob_draw/data/i18n.py` | 🟢 |
| Custo | Nenhuma chamada a modelo de IA ou serviço externo | Diretriz de controle de custo do projeto | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Converter um móvel importado em armário
  Dado três chapas soltas selecionadas, sem marca de módulo
  Quando o usuário abre o botão direito e escolhe Converter em armário
  Então o diálogo pede o papel de cada chapa e destaca a peça sob o cursor
  Quando ele clica laterais, bases, fundo e a porta e confirma
  Então existe um armário v2 no lugar, com uma peça por papel
  E as três chapas de origem continuam na cena, ocultas e fora do plano de corte

Cenário: Origem com modificadores
  Dado um conjunto de chapas com espelho e array no empilhamento
  Quando o usuário converte em armário
  Então as medidas e as peças saem da geometria avaliada, com espelho e array aplicados
  E as origens preservadas continuam com os modificadores originais

Cenário: Conversão desfeita por inteiro
  Dado um armário convertido
  Quando o usuário desfaz uma vez
  Então as malhas de origem voltam visíveis e no plano de corte
  E nenhuma peça do armário novo permanece na cena

Cenário: Papel repetido é recusado
  Dado o diálogo de conversão com a lateral esquerda já apontada
  Quando o usuário tenta apontar outra peça para a mesma lateral
  Então o papel anterior é substituído, nunca somado
  E o armário gerado tem uma lateral esquerda só

Cenário: Porta de correr com direção escolhida
  Dado o diálogo de conversão com tipo Correr
  Quando o usuário escolhe duas folhas e direção direita para esquerda
  Então o armário nasce com duas folhas deslizantes
  E a folha externa é a da direita

Cenário: Armário sem porta
  Dado um armário convertido sem peça apontada como porta
  Quando a geração termina
  Então as chapas existem e nenhuma frente é criada
  E o painel mostra o armário sem porta

Cenário: Converter o que já é armário
  Dado um armário v2 selecionado
  Quando o usuário abre o menu de botão direito
  Então a ação Converter em armário não aparece

Cenário: Adicionar à biblioteca
  Dado um armário recém-convertido
  Quando o usuário aceita a oferta de adicionar à biblioteca
  Então o armário é gravado com nome, categoria e miniatura
  E recusar a oferta mantém o armário na cena

Cenário: Interface em inglês
  Dado o Blender com a interface em inglês
  Quando o usuário abre o menu de conversão
  Então os textos aparecem em inglês
  E o teste de cobertura de i18n passa
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | São o pedido central: transformar a peça em armário |
| RF-04, RF-05 | Must | Converter sem preservar origem e acabamento destrói trabalho do usuário |
| RF-06 | Should | A biblioteca completa o fluxo, mas não bloqueia a conversão |
| RF-18 | Must | Regra do projeto e condição do teste de cobertura |
| Conversão de móvel com pai, instância ou coleção vinculada | Could | Exige decidir o vínculo; malha estática resolve a maioria |
| Conversão de móvel com peças já marcadas por material | Could | O clique por papel resolve sem heurística |

## 9. Esclarecimentos

### Sessão 2026-11-23

- **Q:** O que qualifica "qualquer peça que tenha requisitos de armários"?
  **R:** Um conjunto de malhas selecionadas é lido como um móvel e cada chapa recebe um papel.
- **Q:** Como o usuário aponta fundo, lateral, base e porta?
  **R:** Clicando cada peça no diálogo, com destaque na viewport; o gesto nasce na 018 e é reusado aqui.
- **Q:** O que acontece com a malha original na conversão?
  **R:** Continua na cena, oculta, fora do corte e com os modificadores intactos, com um passo de desfazer.
- **Q:** E se a origem tiver modificadores ou hierarquia?
  **R:** Os modificadores são aplicados e a conversão usa a geometria avaliada; a origem preservada guarda o
  empilhamento original.

## 10. Lacunas

- 🟡 O que fazer com pai, instância e coleção vinculada da origem fica para o `/reversa-plan`.
- 🟡 A conversão de um móvel cujas chapas não são paralelas aos eixos (móvel girado) precisa de decisão de plano:
  ou o armário nasce no referencial da seleção, ou a seleção é recusada.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-23 | Criada pelo fatiamento da 018: RN-01 a RN-07 e RF-01 a RF-06 movidos com IDs preservados, já com as respostas do clarify | reversa |
