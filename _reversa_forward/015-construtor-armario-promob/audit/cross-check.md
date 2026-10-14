# Cross-check: 015-construtor-armario-promob

> Data: `2026-10-14`
> Artefatos analisados (somente leitura):
> - [`requirements.md`](../requirements.md)
> - [`roadmap.md`](../roadmap.md)
> - [`actions.md`](../actions.md), com 44 ações, todas `[X]`
> - também `data-delta.md`, `interfaces/` e `progress.jsonl`
>
> Legado: `_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md` e o código em `caffmob_draw/`, só para confirmar
> pontos citados.
> Este relatório não altera nenhum artefato da feature.

## Resumo

| Severidade | Findings |
|---|---|
| CRITICAL | 1 |
| HIGH | 2 |
| MEDIUM | 7 |
| LOW | 2 |
| **Total** | **12** |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|---|---|---|---|---|
| A001 | CRITICAL | Coerência com o legado | Frente e fundo trocados entre a caixa e as portas. A caixa (`structure.layout`, e na 015 o `carcass_parts`) tem a frente em Y = −profundidade e o fundo em Y = 0. O `door_controller` põe a porta em Y = +t ("alinha na face frontal"), atrás do fundo. A 015 adotou a convenção da caixa (sarrafo frontal, rodapé e recuos na frente em −profundidade) sem registrar o conflito | roadmap §1 e D-02 (referencial do `layout`); `caffmob_draw/geometry/door_controller.py:173,197,223`; `caffmob_draw/cabinet_editor/structure.py` (`layout`, `carcass_parts`); origem no commit inicial `c90aa8e` (`mesh_gen`: fundo em `-t..0`) |
| A002 | HIGH | Cobertura | RF-17 (gavetas de dormitório com "Interna p/ trilho", a de baixo mais alta) virou Must no clarify (Q1), mas nenhuma decisão do roadmap trata o fato de o módulo CAFF MOBI não ter gavetas. A T032 foi fechada com a nota "de baixo mais alta não aplicada" e gaveta só no caminho da biblioteca. O critério de aceite do RF-17 não é atingível num módulo CAFF MOBI | requirements §5 RF-17, §8; roadmap D-13 (sem decisão sobre gavetas no `btm`); actions T032; `progress.jsonl` (T032) |
| A003 | HIGH | Coerência com o legado | A regra 🟢 RN-STANDARDS-12 ("o fundo usa FUN_INF em todos os tipos") é alterada para FUN_SUP/FUN_ALT por grupo no `data-delta.md#4` e na T018. Nenhum requisito nem decisão do titular pede essa mudança; ela aparece só no delta de dados | `_reversa_sdd/domain.md#standards` (RN-STANDARDS-12); data-delta §4; actions T018; requirements sem RN correspondente |
| A004 | MEDIUM | Cobertura | Rastreabilidade indireta: o roadmap cita 9 dos 24 RF (RF-01, 02, 10, 13, 14, 18, 19, 20, 22) e cobre os demais pelas RN. As RN-06, RN-07, RN-09, RN-11, RN-18, RN-19 e RN-20 não aparecem por ID no roadmap. A cobertura existe (T017, T015, D-07, D-10…), mas não dá para seguir RF → D sem ler o texto | roadmap §3; requirements §4 e §5 |
| A005 | MEDIUM | Consistência | A tabela RN-03 traz medidas do Promob que o plano não usa. A Torre p/ Eletros tem 500 de largura no requirements e 600 no catálogo (T001). O Superior aparece com 800 × 950 × 320 a Z 1650, mas a D-19 manda altura e profundidade virem do padrão (700 × 350, instalação a 1500 no padrão BR). A tabela não foi alinhada à D-19 (só o cenário do balcão e o RF-11 foram) | requirements §4 RN-03; roadmap D-19; `caffmob_draw/data/cabinet_structures.json` |
| A006 | MEDIUM | Consistência | A D-15 manda redistribuir a diferença "para os vizinhos imediatos". A T019 foi feita com "os vãos livres dividem o resto". É igual com 3 vãos e diferente com 4 ou mais | roadmap D-15; actions T019; `progress.jsonl` (T019) |
| A007 | MEDIUM | Consistência | A D-11 decide o cache de miniaturas em `GPUOffScreen`; a T034 foi feita com cache da geometria por estrutura. O roadmap não registra a troca | roadmap D-11; actions T034; `progress.jsonl` (T034) |
| A008 | MEDIUM | Consistência | A D-09 descreve REBAIXADO diferente de ENCAIXADO ("+2 × rebaixo de 8 por lado"); a T018 entregou os dois iguais. O texto da própria D-09 é ambíguo ("o +16 de hoje" vale para os dois) | roadmap D-09; actions T018; `legacy-impact.md` (desvios) |
| A009 | MEDIUM | Consistência (contratos) | `interfaces/cut-plan-json.md` diz que `STRUCTURE_UNKNOWN` e `PART_DEGENERATE` vão em `limit_status` da peça. A T040 pôs `STRUCTURE_UNKNOWN` no módulo e omitiu a peça degenerada, e o contrato não foi atualizado | interfaces/cut-plan-json.md §Erros; actions T040; `progress.jsonl` (T040) |
| A010 | MEDIUM | Cobertura | O catálogo define `bays: 2` para "Armário Divisória sobre Base", mas a T028 faz toda estrutura nascer com 1 vão. Nem o requirements nem o roadmap decidem se o número de vãos da estrutura vale na criação | `cabinet_structures.json` (`dor_divisoria_sobre_base`); actions T028 (nota); requirements RN-03 |
| A011 | LOW | Sanidade do actions | O resumo do actions diz "maior cadeia 13". A cadeia T001 → T007 → T014 → … → T044 tem 14 ações, porque a T014 também depende da T007 | actions §Resumo |
| A012 | LOW | Consistência (termos) | O grupo DESPENSEIRO reúne a Torre p/ Eletros e o Armário de dormitório, e "Aéreo", "Superior", "Torre" e "Despenseiro" se alternam entre os documentos. A troca é coerente com o código, mas confunde quem lê | requirements §4 glossário; roadmap D-05; `cabinet_structures.json` |

## Impacto e direção (CRITICAL e HIGH)

**A001 (CRITICAL).** É o defeito que o titular relatou nesta auditoria: ao abrir a porta aparece o fundo, e a frente
fica sem porta. O conflito é de origem (commit inicial):
- a caixa sempre teve o fundo em Y = 0;
- o controlador de portas posiciona as folhas em Y ≥ 0, no lado do fundo.

A 015 não criou o conflito, mas o espalhou: sarrafo frontal, rodapé, recuo das prateleiras, internos e a vista do
editor usam "frente = Y mínimo". Ao corrigir as portas, é preciso decidir uma convenção única (frente em
Y = −profundidade, como a caixa) e conferir tudo o que depende dela:
- portas;
- puxadores;
- `door_controller` (o slider de abertura usa `location.y`);
- encaixe na parede.

Direção: registrar e corrigir pelo `/reversa-debugger` (defeito com reprodução e teste de regressão), citando este
achado. Depois, um `/reversa-clarify` na 015 deixa a convenção escrita no requirements.

**A002 (HIGH).** O titular colocou as gavetas de dormitório como Must, mas o módulo CAFF MOBI não tem gaveta. Hoje a
aba mostra o item e o Inserir avisa "Esta biblioteca não tem gavetas". Isso se resolve junto com a "gaveta completa"
pedida nesta auditoria (frente, contra-frente, distanciadores, tipos de corrediça).

Direção: nova feature pelo `/reversa-requirements`, e depois `/reversa-clarify` na 015 para rebaixar o RF-17 ou
apontá-lo para a feature nova.

**A003 (HIGH).** A mudança faz sentido (o Configurador separa "Fundo - Superiores" e "Fundo - Altos") e só vale para
módulos com estrutura. Mesmo assim, altera uma regra 🟢 sem decisão escrita.

Direção: `/reversa-clarify` na 015 para o titular confirmar e registrar como RN alterada.

## Itens verificados que passaram

**Cobertura**
- Todas as decisões D-01 a D-19 do roadmap aparecem em pelo menos uma ação.
- Os cenários Gherkin do requirements têm ação correspondente: os de balcão, roupeiro, divisória sobre base, padrão,
  biblioteca, cabideiro, invisível, projeto antigo, padrão editável, estrutura inválida, cancelar galeria, galeria em
  inglês, tampo linear e vão digitado aparecem na T042 ou nos testes puros (T007, T008, T010, T011, T013).
- Os cenários de correr, de Salas/Escritórios e de caixa de gaveta ficaram fora por decisão do titular (clarify Q1,
  MoSCoW Won't), e o actions não os implementa.
- RF-23 e RF-24 (clarify) estão cobertos por T029, T037 e T002/T025.

**Consistência**
- Todos os IDs citados existem: D-01 a D-19 no roadmap; RF e RN citados no roadmap e no actions existem no
  requirements.
- Os três contratos de `interfaces/` aparecem no roadmap §7.
- Os termos principais são usados igual nos três documentos: estrutura de caixa, sarrafo, rodapé, Inferior c/
  Divisória, legacy_map, Padrão de Dimensões.

**Coerência com o legado**
- As alterações de regra 🟢 registradas como intencionais estão justificadas: RN-CABINET_EDITOR-12 (vão digitável,
  RN-14), RN-CABINET_EDITOR-15 (rodapé da estrutura, D-04 e clarify Q2), RN-STANDARDS-20 (atributos `CAFF_*`, D-08)
  e RN-LIBRARY_PANEL-03 (D-16).
- Os componentes citados no roadmap §5 existem: `geometry/mesh_gen`, `cabinet_editor/structure`, `cutting/part_sources`,
  `standards/*`, `library_panel/*` e `operators/cabinet_builder`.

**Sanidade do actions**
- Nenhuma dependência aponta para ID inexistente.
- Não há ciclo de dependência.
- As 22 ações `[//]` têm arquivos alvo diferentes entre si.
- As 44 ações estão `[X]`, com 44 linhas no `progress.jsonl`.

## Fora do escopo desta auditoria: pedidos novos do titular

O argumento desta auditoria trouxe pedidos que não são cruzamento de artefatos. Este skill só lê; a direção para
cada um:

1. **Fundo e frente trocados nos móveis do editor e da biblioteca** → `/reversa-debugger` (ver A001).
2. **Controle de abertura** que reconhece porta de giro, folha de correr ou gaveta, com slider manual e botões que
   animam a abertura, desenhado com `/impeccable` → nova feature (`/reversa-requirements`). Depende de A001: o slider
   atual (`door_controller`, 0 a 0,2 m em `location.y`) usa o eixo trocado.
3. **Gaveta completa e personalizável** (frente, contra-frente, laterais, fundo, distanciadores, folgas) e **tipos de
   corrediça** para escolher no editor. O titular pediu que o Codex modele → nova feature (`/reversa-requirements`).
   No `/reversa-coding` dela, a modelagem pode ser delegada ao Codex CLI, com git limpo antes e revisão do diff
   depois. As folgas e avanços já levantados nos vídeos estão em `inputs/notas-grupo-c.md#3`.
4. **Editor de armário reorganizado** ("mostrar menos botões; ao tocar, descobrir a seção"): mantém todas as funções,
   abre numa grade de botões grandes (Estrutura, Área interna, Divisões…) e cada seção tem "voltar" no alto com o nome
   da seção principal, tudo com `/impeccable` → nova feature (`/reversa-requirements`).

Sugestão de ordem:
- primeiro o defeito A001 (pequeno, e destrava o controle de abertura);
- depois o editor reorganizado e o controle de abertura (mesma tela, mesmo brief do `/impeccable`);
- por último a gaveta completa com as corrediças (fecha também o A002).
