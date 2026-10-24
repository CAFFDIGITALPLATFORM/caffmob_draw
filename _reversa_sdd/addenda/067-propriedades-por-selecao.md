# Adendo: 067-propriedades-por-selecao

- **Feature:** 067, nova interface do CAFFMob Draw: as propriedades pertencem ao objeto selecionado
- **Data:** 2026-10-24
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)
- **Entrega:** sincronização parcial, onda 1 (versão 1.9.0 ainda por publicar), commits `e307ccf2` e `cd507483` na
  branch `feat/067-onda1-selecao`. As ondas 2 a 7 complementam este adendo com seções `## Atualização`

## Vigência

Vigente desde 2026-10-24.

## Resumo da entrega

A 067 troca o painel por tipo do objeto ativo por um painel relacional ao selecionado, em 7 ondas. A onda 1 entrega:

- **Alvo resolvido:** um alvo da seleção (snapshot) refeito fora do draw, lido pelo painel, pelo menu do botão direito
  e pelas cotas. Os 15 tipos da auditoria têm adaptador próprio, e o tipo desconhecido cai num fallback rotulado.
- **Cabeçalho e modos:** o cabeçalho mostra tipo, escopo e caminho do dono, com "Selecionar conjunto". Os modos
  Essencial e Completa ficam nas preferências; a Completa guarda toda capacidade da 1.8.0.
- **Chapa:** mostra as próprias medidas. A de biblioteca é somente leitura com o motivo; a autoral edita a própria
  malha. Construir → Chapa nasce do Padrão de Dimensões ativo com o material "MDF Branco".
- **Cotas:** fixas sempre para a seleção, sem chave, no escopo Peça ou Conjunto; as antigas viram ação na Completa.
- **Padrão de Dimensões:** persiste num banco local (`padroes.sqlite3`), com exportar e importar tudo.
- **Corte e revestimento:** o veio da peça vai ao corte; o revestimento é editado num rascunho e refeito só em
  "Aplicar".

Ações concluídas: **63 de 176** (onda 1 inteira, menos a versão 1.9.0, o aceite do titular, este adendo e o fechamento
do #142).

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|---|---|---|---|
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Limites e organização | componente-novo | Camada nova `target/` (resolvedor, snapshot, capacidades, CommandRouter, ViewModel e adaptadores) entre `selection` e `ui`; o painel Selecionado passa a depender dela |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Fluxos entre componentes | regra-alterada | O fluxo 3 (seleção → cotas → mover) passa pelo snapshot do alvo, com escopo Peça ou Conjunto; a peça gerada pelo módulo nunca é alvo móvel |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 › Persistência e unidades | delta-de-dados | Além do `.blend`, o Padrão de Dimensões da marcenaria fica em `extension_path_user(<pacote>, "standards")/padroes.sqlite3` |
| `_reversa_sdd/selection/requirements.md` | RN-16 | regra-alterada | O painel não mostra as dimensões do módulo numa peça ou frente; `editable_dimensions` continua valendo para quem a chama |
| `_reversa_sdd/selection/requirements.md` | RN-21 | regra-alterada | `element_size.element` continua mapeando frente e peça para o módulo (aviso e Redimensionar), mas o painel mede a própria peça |
| `_reversa_sdd/overlays/requirements.md` e `addenda/bug-BUG-20261023-HYCE-v001.md` | Cotas fixas | regra-alterada | Leia a versão `-v002` abaixo: sem a chave "Medidas laterais", cotas sempre para a seleção |
| `_reversa_sdd/addenda/066-reparo-do-addon-caffmob.md` | D-10, RF-013, RF-014, RF-020 | regra-removida | A chave das cotas sai da interface; "chave desligada não desenha" e "as laterais suprimem as antigas" não valem mais |
| `_reversa_sdd/standards/requirements.md` | Responsabilidades e RN-10 a RN-19 | delta-de-dados | Os operadores do padrão gravam também no banco local; abrir arquivo traz do banco os uids que faltam e nunca grava nele (067 D-26, D-27) |
| `_reversa_sdd/cutting/requirements.md` | Origem das peças (`part_sources`) | regra-alterada | `PartRecord.grain` sai de `btm_part.grain` (H → HORIZONTAL, V → VERTICAL) nas peças CUTPART e na geometria livre; sem `btm_part`, NONE |
| `_reversa_sdd/aggregates/requirements.md` | Agregados e folhas | regra-alterada | Os botões do armário autoral ganham `poll` com motivo; `member_remove` sem membro devolve `CANCELLED` |
| `_reversa_sdd/ui/requirements.md` | Seção Selecionado e Construir | regra-alterada | Selecionado desenha o ViewModel do alvo (Essencial/Completa); Construir por finalidade (Ambiente, Móveis, Chapas e peças, Iluminação) |
| `_reversa_sdd/geometry_free/requirements.md` | Criação | componente-novo | `caffmob.geometry_sheet` (Construir → Chapa) e o material "MDF Branco" achado pela marca `btm_builtin_material` |

### Versões `-v002` das regras superadas (067 D-32, RF-143)

- **Cotas fixas (HYCE-v002, ver `bug-BUG-20261023-HYCE-v002.md`):** as quatro cotas fixas aparecem sempre que há
  seleção com alvo móvel, sem a chave "Medidas laterais", que continua registrada só para ler arquivos antigos. O alvo
  vem do snapshot, no escopo de `WindowManager.btm_target.cota_scope`. Parede, piso, teto, porta, janela, luz e câmera
  soltas dizem "indisponível para <motivo>". As cotas antigas (afastamento, anterior, posterior, Mover na Parede) só
  aparecem em "Cotas antigas" da Completa, para módulo.
- **selection RN-16 (-v002):** campos de dimensão do painel por tipo: módulo e porta/janela como antes; peça, frente,
  membro, folha e geometria mostram duas medidas da face e a espessura da própria peça (`target/part_geometry`).
- **selection RN-21 (-v002):** sem mudança em `element_size`; o painel deixa de usá-lo para medir.
- **standards (-v002):** o padrão da marcenaria persiste fora do arquivo; arquivo novo recebe as definições do banco e
  a última ativa; uid igual com conteúdo diferente vale o do arquivo, dentro do arquivo.

## Regras sob vigilância

W001, W002, W003, W004 e W005, em `caff_systems:_reversa_forward/067-propriedades-por-selecao/regression-watch.md`.

## Fontes

- `caff_systems:_reversa_forward/067-propriedades-por-selecao/legacy-impact.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/regression-watch.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/requirements.md`
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/roadmap.md` (D-02 a D-13, D-26 a D-29, D-32)
- `caff_systems:_reversa_forward/067-propriedades-por-selecao/progress.jsonl`
