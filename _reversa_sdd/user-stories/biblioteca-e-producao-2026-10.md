# Histórias de Usuário — Biblioteca e Produção (re-extração 2026-10)

> Gerado pelo **Writer** (Reversa) em 2026-10-10 a partir das specs das units `library_panel`, `object_library`,
> `aggregates` (importação e SketchUp), `customize` (biblioteca do usuário, `library_io`), `legacy` (grupos),
> `move_over` (Substituir), `standards` (arquivos JSON e Promob), `geometry_free` (peça de fabricação) e da unit antiga
> `cutting/` (2026-07). As histórias descrevem o comportamento **atual** do código (engenharia reversa), não um roadmap.
>
> Legenda: 🟢 confirmado no código pela spec da unit · 🟡 inferido (intenção, prioridade, persona) ou observado no código
> sem spec de unit · 🔴 lacuna que depende de validação humana, de execução no Blender ou de spec inexistente.
> Referências no formato `<unit>/requirements.md#RF-xx` / `#CA-xx` (caminhos relativos a `_reversa_sdd/`).

## Personas

Não existe `_reversa_sdd/personas.md`; as personas vêm de `soul.md` e `domain.md`.

| ID | Persona | Fonte | Confiança |
|---|---|---|---|
| P1 | **Projetista de móveis planejados**: insere módulos prontos, salva os próprios modelos e compõe o ambiente com objetos de decoração | `soul.md`; `library_panel`, `object_library` | 🟡 |
| P2 | **Marceneiro / dono da fábrica**: precisa da lista de peças, do plano de corte e de trocar o padrão de medidas com o Promob | `soul.md` ("gera a produção… lista de peças, plano de corte… exportação JSON"; referência ao Promob) | 🟡 |
| P3 | **Usuário de projeto herdado**: tem grupos salvos da biblioteca antiga | `legacy` RF-09 | 🟡 |

---

## US-BIB-01 — Abrir a Biblioteca CAFFMob e escolher uma categoria

🟡 **Como** projetista (P1), **quero** um painel sempre visível na viewport com as categorias (Cozinha, Banheiro, Sala…) e os módulos de cada uma, **para** inserir móveis sem procurar em menus.

Referências: `library_panel/requirements.md#RF-01`, `#RF-02`, `#RF-04`.

**Critérios de aceitação**

- 🟢 **Feliz — abrir** (`library_panel#CA-02`): Dado o painel fechado; Quando clico no rótulo "BIBLIOTECA CAFFMOB"; Então a coluna lista Criar armário, as categorias fixas, as do usuário e Criar categoria.
- 🟢 **Feliz — popover** (`library_panel#CA-08`): clicar em "Cozinha" fecha a coluna e o popover lista os modelos prontos do catálogo e os módulos salvos da pasta Cozinha.
- 🟢 **Falha — clique fora / Esc** (`library_panel#CA-03`): o painel fecha; o clique segue para a seleção e o Esc é consumido só com o painel aberto.
- 🟢 **Falha — biblioteca indisponível** (`library_panel#CA-09`): erro de leitura mostra "Biblioteca indisponível: <erro>" sem quebrar os modelos prontos.
- 🟢 **Falha — `categories.json` inválido** (`library_panel#CA-05`): ficam só as pastas soltas, com aviso, e o arquivo não é regravado.

## US-BIB-02 — Inserir um modelo pronto pela linha da categoria

🟡 **Como** projetista (P1), **quero** inserir um balcão pronto já nas medidas da linha da categoria, **para** começar o projeto rápido e dentro do padrão.

Referências: `library_panel/requirements.md#RF-05`; `standards/requirements.md#RF-05`.

- 🟢 **Feliz** (`library_panel#CA-10`): Dado o modelo `balcao_2p` e a linha BAN; Quando aciono `caffmob.library_insert_model`; Então o construtor recebe BASE, BAN, porta dupla, 1 prateleira, 0,8 m e o módulo é criado no cursor 3D.
- 🟢 **Falha** (`library_panel#CA-11`): id ausente do catálogo gera "Modelo não encontrado: <id>" sem criar nada.

## US-BIB-03 — Criar categorias e trocar a linha delas

🟡 **Como** projetista (P1), **quero** criar categorias próprias (ex. "Closet") ligadas a uma linha, **para** organizar meus módulos do jeito da minha loja.

Referências: `library_panel/requirements.md#RF-03`, `#RF-07`.

- 🟢 **Feliz — criar** (`library_panel#CA-06`): " Closet " com linha DOR cria a pasta `Closet`, grava em `categories.json` e mostra "Categoria criada: Closet".
- 🟢 **Feliz — trocar linha** (`library_panel#CA-14`): Lavanderia/DOR passa a Lavanderia/SAL.
- 🟢 **Falha — nome recusado** (`library_panel#CA-07`): "COZINHA" (repetido), vazio ou com "/" gera o motivo e nada é gravado.
- 🟢 **Falha — categoria fixa** (`library_panel#CA-15`): "Só as categorias do usuário trocam de linha".

## US-BIB-04 — Criar um armário pelo diálogo e já abrir o editor

🟡 **Como** projetista (P1), **quero** criar um armário com a linha e a montagem do padrão ativo e cair direto no editor, **para** desenhar módulos sob medida.

Referências: `library_panel/requirements.md#RF-06`; `cabinet_editor/requirements.md#RF-01`.

- 🟢 **Feliz** (`library_panel#CA-12`): com a última categoria em DOR, o diálogo vem com linha DOR, montagem e largura do padrão; ao confirmar, o módulo é criado e o editor de armário abre nele.
- 🟢 **Falha** (`library_panel#CA-13`): em modo de edição o comando não fica disponível; diálogo cancelado não cria nada.

## US-BIB-05 — Salvar um módulo personalizado na minha biblioteca

🟡 **Como** projetista (P1), **quero** salvar um módulo com a personalização (estilo, puxador, materiais, divisões) numa categoria, **para** reutilizá-lo em outros projetos.

Referências: `customize/requirements.md#RF-09`, `#RF-13`.

- 🟢 **Feliz** (`customize#CA-17`): `caffmob.module_save("Balcão vidro", "Balcões")` grava `.blend` e `.json` em `modules/Balcões/` e o módulo aparece com manifesto.
- 🟢 **Falha — nome repetido** (`customize#CA-18`): sem "Substituir" aparece "O módulo 'Balcão vidro' já existe…" e nada é escrito.
- 🟢 **Falha — gravação** (`customize#CA-19`).

## US-BIB-06 — Inserir, substituir e gerir meus módulos

🟡 **Como** projetista (P1), **quero** inserir um módulo salvo posicionando com o mouse, trocar um módulo da cena por ele e renomear ou apagar os salvos, **para** manter a biblioteca útil.

Referências: `customize/requirements.md#RF-10`, `#RF-11`; `move_over/requirements.md#RF-09`.

- 🟢 **Feliz — inserir direto** (`customize#CA-20`): o módulo entra no lugar salvo e continua paramétrico (estilo "Vidro", material "Laca branca").
- 🟢 **Feliz — posicionar** (`customize#CA-21`): a raiz segue o mouse com snap à grade, R gira 90°, clique confirma, Esc cancela.
- 🟢 **Feliz — substituir** (`move_over#CA-12`): o novo módulo ocupa o canto de A no referencial de B e A some.
- 🟢 **Falha — inserir** (`customize#CA-22`): manifesto inválido ou major 2 → "Manifesto inválido: …"; `.blend` sem módulo → "Nenhum módulo encontrado no arquivo".
- 🟢 **Falha — substituir** (`move_over#CA-12`): lista vazia ou carregamento que falha avisa e não apaga A.
- 🟢 **Apagar** (`customize#CA-24`): `.blend`, `.png` e `.json` somem com "Módulo apagado: <nome>".

## US-BIB-07 — Converter grupos da biblioteca antiga

🟡 **Como** usuário de projeto herdado (P3), **quero** converter meus grupos antigos em módulos da biblioteca do usuário, **para** não perder o acervo ao migrar.

Referências: `legacy/requirements.md#RF-09`, `#RF-10`; `library_panel/requirements.md#RF-08`.

- 🟢 **Feliz** (`legacy#CA-14`): "Cozinha L" (2 armários) e "Ilha" (nome já existente) viram "Cozinha L 1", "Cozinha L 2" e "Ilha (2)" em Geral.
- 🟢 **Oferta** (`library_panel#CA-16`): "Converter grupos antigos" é o primeiro item do painel enquanto houver pendentes.
- 🟢 **Falha — grupo ilegível** (`legacy#CA-15`): "Não foi possível abrir o grupo <nome>: <erro>" e o grupo fica pendente.
- 🟢 **Falha — nada pendente** (`legacy#CA-16`): "Nenhum grupo antigo para converter".

## US-BIB-08 — Procurar e inserir objetos do ambiente

🟡 **Como** projetista (P1), **quero** buscar portas, mesas e decoração na biblioteca de objetos e posicioná-las com o mouse, **para** compor a cena de apresentação.

Referências: `object_library/requirements.md#RF-01`, `#RF-02`, `#RF-08`.

- 🟢 **Feliz — listar** (`object_library#CA-01`): itens embutidos e do usuário aparecem juntos, com miniatura quando há, e um aviso por arquivo inválido.
- 🟢 **Feliz — busca** (`object_library#CA-02`): "LIS" acha "Porta lisa" (sem acento e sem caixa).
- 🟢 **Feliz — inserir** (`object_library#CA-04`, `#CA-05`): o item entra no cursor 3D ou segue o mouse no plano do cursor até o clique.
- 🟢 **Falha — cancelar** (`object_library#CA-06`): Esc ou botão direito removem os objetos carregados.
- 🟢 **Falha — item ausente ou corrompido** (`object_library#CA-07`): "Objeto não encontrado na biblioteca" / "Item corrompido: <nome>".
- 🟢 **Pacote limpo** (`object_library#CA-19`): seis itens embutidos modelados pelo projeto (GPL-3.0-or-later), sem modelo do 3D Warehouse.

## US-BIB-09 — Acrescentar meus objetos à biblioteca

🟡 **Como** projetista (P1), **quero** salvar a seleção ou um arquivo 3D na biblioteca com categoria, origem e licença, preservando as conversões (folha, agregado, grupo), **para** reaproveitar modelos importados.

Referências: `object_library/requirements.md#RF-03`, `#RF-04`, `#RF-05`.

- 🟢 **Feliz** (`object_library#CA-08`): "Porta copiada" grava `.blend`, `.json` e `.png` na categoria DOORS do usuário.
- 🟢 **Feliz — conversões voltam** (`object_library#CA-12`): uma porta com folha de giro de 90° continua assim noutra sessão.
- 🟢 **Nome repetido** (`object_library#CA-10`): RENAME cria "Meu teste 2"; REPLACE regrava.
- 🟢 **Falha — pedido inválido** (`object_library#CA-09`): "Dê um nome ao objeto" / "Selecione o objeto ou escolha um arquivo" / "A seleção não tem malhas".
- 🟢 **Falha — embutido protegido** (`object_library#CA-14`): "Os objetos que vêm com o plugin não podem ser removidos".

## US-BIB-10 — Trocar o acabamento de um objeto

🟡 **Como** projetista (P1), **quero** aplicar um acabamento do plugin ou uma imagem própria em escala real numa parte do objeto, **para** combinar a decoração com o projeto.

Referências: `object_library/requirements.md#RF-06`, `#RF-07`.

- 🟢 **Feliz — acabamento** (`object_library#CA-15`): só o tampo selecionado recebe o material ("1 peça(s) com <nome>").
- 🟢 **Feliz — imagem** (`object_library#CA-17`): `madeira.png` a 600 mm vira textura com projeção BOX e escala 1/0,6; repetir reaproveita o material.
- 🟢 **Falha** (`object_library#CA-16`, `#CA-18`): "Nada mudou: acabamento ausente ou seleção sem malhas"; "Escolha uma imagem" / "Não foi possível abrir a imagem: <erro>".

## US-BIB-11 — Importar modelos SketchUp, OBJ, FBX e glTF

🟡 **Como** projetista (P1), **quero** importar modelos de fornecedores (inclusive SketchUp) como um componente com a unidade certa, **para** usar peças reais no projeto.

Referências: `aggregates/requirements.md#RF-14`, `#RF-15`.

- 🟢 **Feliz — unidade automática** (`aggregates#CA-19`): OBJ com maior medida 1400 em escala 1 é lido em mm ("unidade: mm").
- 🟢 **Feliz — SketchUp em árvore** (`aggregates#CA-21`): o armário vira grupo com os grupos das portas como filhos; figuras de escala "2D Woman" são ignoradas e contadas no relatório.
- 🟢 **Falha — formato** (`aggregates#CA-20`): ".3ds" gera "Formato não suportado: .3ds (use OBJ, FBX, glTF, GLB ou SKP)".
- 🟢 **Falha — SketchUp ilegível** (`aggregates#CA-22`): "Não foi possível ler o SketchUp: <motivo>. Salve numa versão recente do SketchUp ou exporte em glTF, OBJ ou FBX." e nada é criado.

## US-BIB-12 — Trocar o padrão de medidas com o Promob e entre projetos

🟡 **Como** marceneiro (P2), **quero** importar e exportar o padrão de dimensões no formato `DIMENSIONEXPORT` do Promob e em `.btmdim.json`, **para** usar as mesmas medidas da fábrica nos dois programas.

Referências: `standards/requirements.md#RF-08`, `#RF-09`, `#RF-11`.

- 🟢 **Feliz — ida e volta Promob** (`standards#CA-18`): o fixture de 692 atributos é reexportado com os mesmos 692 pares (ID, VALUE) e o nome "ME MOVEIS - COZ. ESCR.".
- 🟢 **Feliz — ida e volta JSON** (`standards#CA-16`): nasce uma definição USER com UID novo, mesmos valores, nome único e não ativa.
- 🟢 **Falha — XML inválido** (`standards#CA-19`): XML malformado, raiz errada ou sem ATTRIBUTE gera erro em português.
- 🟢 **Falha — JSON recusado** (`standards#CA-17`): schema estranho, versão 2, unidade "cm" ou espessura 999 não criam definição.
- 🟢 **Relatório** (`standards#CA-22`): a última aplicação/importação fica consultável.

## US-BIB-13 — Gerar a lista de peças e o plano de corte

🟡 **Como** marceneiro (P2), **quero** calcular o plano de corte das peças do projeto em chapas, respeitando serra, refilo e veio, **para** comprar e cortar o MDF com o menor desperdício.

Referências: `cutting/requirements.md#RF-01`, `#RF-02`, `#RF-03` (unit de 2026-07, só `nesting.py`); `geometry_free/requirements.md#RF-05`; `aggregates/requirements.md#RF-06`; `standards/requirements.md#RF-06` (plano desatualizado).

- 🟢 **Feliz — encaixe** (`cutting/requirements.md#RF-01`): peças maiores são empacotadas primeiro em faixas de corte guilhotinado, com kerf (4 mm) e refilo (10 mm) descontados.
- 🟢 **Falha — peça maior que a chapa** (`cutting/requirements.md#RF-02`; `cutting/edge-cases.md` 1.1): a peça vai para a lista de não posicionadas com o motivo.
- 🟢 **Regra — veio** (`cutting/requirements.md#RF-03`): peça com veio travado não gira 90°.
- 🟢 **Fontes de peças** (`geometry_free#CA-10`, `#CA-11`, `#CA-12`; `aggregates#CA-09`): placa gera 1 chapa, caixa 6, agregado marcado como produção gera a sua; geometria não fabricada ou oculta fica fora.
- 🟡 **Feliz — comando** (observado em `operators/ops_cutting.py`, sem unit): "Calcular Plano de Corte" (`caffmob.calculate_nesting`) extrai as peças com a definição ativa, guarda o resultado na cena e informa "Plano de corte: N chapa(s), M peça(s), aproveitamento X%."; peças maiores que o limite do componente ou que não couberam viram aviso.
- 🟡 **Falha — sem peças** (observado em `operators/ops_cutting.py`): "Nenhum módulo com peças de marcenaria encontrado no projeto." e `CANCELLED`.
- 🟢 **Regra — plano desatualizado** (`standards#CA-13`): aplicar padrão marca o plano como desatualizado; abrir frentes não marca (`inspection#CA-03`).

## US-BIB-14 — Exportar a produção (JSON global e CSV)

🟡 **Como** marceneiro (P2), **quero** exportar projeto, peças, ferragens e plano de corte num JSON e a lista de peças em CSV, **para** levar a produção a planilhas e otimizadores externos.

Referências: 🔴 nenhuma unit cobre (`operators/ops_cutting.py`, `cutting/json_exporter.py`, `cutting/csv_exporter.py`, `cutting/hardware.py`; ver `traceability/code-spec-matrix.md` R4/R5).

- 🟡 **Feliz — JSON global** (observado em `operators/ops_cutting.py`): `caffmob.export_cut_plan_json` grava o JSON global v2 com dados do cliente opcionais e recalcula o plano se ele estiver ausente ou desatualizado; informa "JSON global exportado: N peça(s) em <arquivo>".
- 🟡 **Feliz — CSV** (observado): `caffmob.export_parts_csv` grava a lista com separador `;` e vírgula decimal.
- 🟡 **Falha** (observado): sem peças, "Nenhuma peça para exportar."; erro de gravação, "Não foi possível gravar: <erro>"; JSON inválido na validação reporta os 3 primeiros erros.
- 🟡 **Importar** (observado): `caffmob.import_cut_plan_json` lê v2 ou v1 e mostra o resumo de peças e chapas.

---

## Lacunas (🔴 relevantes das units)

| Unit | Caso | Lacuna | Fonte |
|---|---|---|---|
| produção | — | 🔴 Lista de peças, furação, ferragens, exportação JSON/CSV e plano desatualizado (`cutting/part_extractor.py`, `part_sources.py`, `part_roles.py`, `drilling.py`, `hardware.py`, `machining.py`, `json_exporter.py`, `csv_exporter.py`, `stale.py`, `operators/ops_cutting.py`) não têm spec; a unit `cutting/` de 2026-07 só descreve `nesting.py` | `traceability/code-spec-matrix.md` R4/R5 |
| `cutting` | 1.2 | 🟡 Peças estreitas com kerf grande: perda alta e risco de precisão; mínimo de largura sugerido, não implementado | `cutting/edge-cases.md` |
| `library_panel` | EC-04 | 🔴 Categoria com `:` ou terminada em `.`: a pasta criada e a pasta onde o módulo é salvo divergem | `library_panel/edge-cases.md` |
| `library_panel` | EC-05 | 🔴 Muitas categorias: sem rolagem, itens (a começar por "Criar categoria") saem da área visível | `library_panel/edge-cases.md` |
| `library_panel` | EC-16 | 🔴 Duas viewports/janelas: estado aberto e popover são globais | `library_panel/edge-cases.md` |
| `customize` | EC-01 | 🔴 Inserir `.blend` sem `.json` (grupo antigo, "sem personalização") quebra com `UnboundLocalError` | `customize/edge-cases.md`; `customize/requirements.md` (lacunas) |
| `object_library` | EC-07 | 🔴 Cancelar ou item corrompido deixa malhas, materiais e imagens órfãos | `object_library/edge-cases.md` |
| `object_library` | EC-08 | 🔴 Salvar peças que têm pai provavelmente leva o pai para o `.blend` | `object_library/edge-cases.md` |
| `object_library` | EC-10 | 🔴 Inserir pelo botão da barra lateral: região do modal não verificada | `object_library/edge-cases.md` |
| `object_library` | EC-13 | 🔴 Biblioteca grande relida a cada redesenho | `object_library/edge-cases.md` |
| `object_library` | EC-14 | 🔴 Inserção sem snapping nem colisão; grupo fica fora da verificação de colisão | `object_library/edge-cases.md`; `collision/edge-cases.md` EC-15 |
| `object_library` | EC-16 | 🔴 Imagem própria em objeto com escala ≠ 1 perde o "tamanho real"; imagem não empacotada | `object_library/edge-cases.md` |
| `object_library` | EC-19 | 🔴 Cancelamento externo do modal deixa os objetos na cena | `object_library/edge-cases.md` |
| `standards` | EC-03 | 🔴 `.btmdim.json` perde a montagem "Base passante" | `standards/edge-cases.md` |
