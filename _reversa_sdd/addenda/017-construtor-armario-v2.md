# Adendo: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-23`
> Cenário: `legado`
> Extração de referência: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md`

## Vigência

Vigente desde 2026-11-23.

## Resumo da entrega

O construtor de armário do addon passou a ser o motor novo, que calcula e emite as peças em milímetros a partir de um
contrato de chapas do próprio projeto: caixa, divisões, gavetas com corrediça telescópica 3D, internos, portas de abrir,
portas deslizantes e fundo, com as sete abas do mockup na vista 3D, catálogo em português e inglês, modo de abertura
animado e um único passo de desfazer por confirmação. O antigo editor 2D saiu do registro, sem apagar nenhum arquivo, e
o plano de corte passou a consumir as peças do armário v2 por papel gravado, com a ferragem (corrediça) fora da lista.

Ações concluídas: **40 de 40** (`[X]`), sem nenhuma aberta.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Persistência e unidades | delta-de-dados | O armário v2 grava tudo em `Object.btm_armario`, cada peça em `Object.btm_armario_parte` (agora com o campo `ferragem`) e o contrato de chapas em `Scene.btm_armario_contrato` |
| `_reversa_sdd/architecture.md` | Limites e organização | componente-novo | Nasceram o pacote `caffmob_draw/armario_v2/` (núcleos puros mais cascata de registro) e o ativo `caffmob_draw/assets/slides/slide-st48-0200-0.obj` |
| `_reversa_sdd/architecture.md` | Fluxos entre componentes | regra-alterada | A interface do editor 2D deixa de ser registrada por `cabinet_editor`; `armario_v2` entra na cascata da extensão entre `customize` e `cabinet_editor` |
| `_reversa_sdd/architecture.md` | Integrações e distribuição | regra-alterada | O manifesto da extensão vai a `1.26.0` e o OBJ da corrediça passa a viajar no pacote (2367 arquivos no ZIP) |
| `_reversa_sdd/domain.md` | 1.2 Entidades de Produção | regra-nova | O corte ganhou a origem `ARMARIO_V2`; peça de ferragem tem `papel` vazio e `ferragem` preenchida, e não entra no plano de chapa |
| `_reversa_sdd/domain.md` | 2.3 Regras de Otimização de Plano de Corte | regra-alterada | `iter_modules` ignora módulo oculto ou com `btm_cut_exclude`, então o módulo convertido não duplica peças no plano |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | Valem as regras novas do motor v2: encontro das chapas, espessuras aceitas, contrato de chapas, recuo do fundo e da deslizante, gavetas, portas, internos, corrediça ST48, animação e lista de peças; ver `legacy-impact.md` da feature |

## Regras sob vigilância

`W001`, `W002`, `W003`, `W004`, `W005`, `W006`, `W007`, `W008`, `W009` e `W010`, em
`_reversa_forward/017-construtor-armario-v2/regression-watch.md`.

## Fontes

- `_reversa_forward/017-construtor-armario-v2/legacy-impact.md`
- `_reversa_forward/017-construtor-armario-v2/regression-watch.md`
- `_reversa_forward/017-construtor-armario-v2/requirements.md`
- `_reversa_forward/017-construtor-armario-v2/progress.jsonl`
- `_reversa_forward/017-construtor-armario-v2/actions.md`

## Atualização 2026-11-23

A segunda rodada de `/reversa-coding` fechou T041 a T051, depois do clarify da auditoria de mockup. Duas frentes
entraram: a inserção de divisórias, prateleiras, matriz, bloco de gavetas e internos passou a existir na interface, e a
contra-frente e a peça de trás passaram a ser geradas como travessa de 90 mm. Ações concluídas agora: **51 de 51**,
sem nenhuma aberta.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Persistência e unidades | delta-de-dados | `BTM_PG_ArmarioV2` ganhou `contra_frente_ativa`, `peca_tras_ativa` e nove campos de interface da inserção (variante, matriz e bloco), todos com padrão e sem migração |
| `_reversa_sdd/architecture.md` | Limites e organização | regra-alterada | `armario_v2/ops.py` ganhou cinco operadores de inserção e o `vao_ativo`; `panel.py` deixou de ser só leitura e passou a chamar operador |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-alterada | A RN-04 passa a ser lida como travessa de 90 mm entre as laterais, com a orientação trocando o eixo dos 90 mm; o RF-05 é gerado, não apenas calculado |
| `_reversa_sdd/domain.md` | 1.2 Entidades de Produção | regra-nova | Dois papéis novos no corte, `CONTRA_FRENTE` e `PECA_TRAS`, com componente `TRA`, sem mudança no adaptador `armario_v2_records` |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-nova | RF-07, RF-09 e RF-12 ganharam caminho de uso no painel: cada inserção regrava a coleção e gera no mesmo passo de desfazer |

### Regras sob vigilância (atualização)

`W011`, em `_reversa_forward/017-construtor-armario-v2/regression-watch.md`: a contra-frente e a peça de trás são
travessas de 90 mm com a espessura da base superior, e a orientação troca o eixo dos 90 mm. Os itens `W001` a `W010`
seguem valendo como na seção anterior.

### Fontes da atualização

- `_reversa_forward/017-construtor-armario-v2/legacy-impact.md`, seção 1.2
- `_reversa_forward/017-construtor-armario-v2/actions.md`
- `_reversa_forward/017-construtor-armario-v2/progress.jsonl`
- `_reversa_forward/017-construtor-armario-v2/regression-watch.md`
