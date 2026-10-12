# Histórias de Usuário — Construir e Configurar Armários (re-extração 2026-10)

> Gerado pelo **Writer** (Reversa) em 2026-10-10 a partir das specs das units `cabinet_editor`, `standards`,
> `customize`, `aggregates`, `molding` e `legacy`. As histórias descrevem o comportamento **atual** do código
> (engenharia reversa), não um roadmap.
>
> Legenda: 🟢 confirmado no código pela spec da unit · 🟡 inferido (intenção, prioridade, persona) · 🔴 lacuna que depende
> de validação humana ou de execução no Blender. Confirmação de código não implica validação visual no Blender.
> Referências no formato `<unit>/requirements.md#RF-xx` / `#CA-xx` (caminhos relativos a `_reversa_sdd/`).

## Personas

Não existe `_reversa_sdd/personas.md`; as personas vêm de `soul.md` e `domain.md`.

| ID | Persona | Fonte | Confiança |
|---|---|---|---|
| P1 | **Projetista de móveis planejados**: monta e personaliza os módulos do cliente (medidas, divisões, frentes, materiais) | `soul.md`; `domain.md` RN-CUSTOMIZE-16 | 🟡 |
| P2 | **Marceneiro / dono da fábrica**: define o padrão dimensional da linha (espessuras, alturas, recuos) que todo armário novo segue | `soul.md` (chapa 2750 × 1830 mm, mm, Promob); `standards` (Padrão Brasil) | 🟡 |
| P3 | **Usuário de projeto herdado (Home Builder 5)**: abre arquivos antigos com armários frameless, face frame ou closets | `legacy`; ADR 0006 | 🟡 |

---

## US-ARM-01 — Abrir o editor de armário e ajustar as medidas

🟡 **Como** projetista (P1), **quero** abrir o módulo numa vista frontal 2D e mudar largura, altura e profundidade validadas pela faixa da linha, **para** ajustar o armário ao vão do cliente com segurança.

Referências: `cabinet_editor/requirements.md#RF-01`, `#RF-03`, `#RF-04`, `#RF-05`.

**Critérios de aceitação**

- 🟢 **Feliz — abrir** (`cabinet_editor#CA-01`): Dado um módulo ativo e nenhuma sessão; Quando executo `caffmob.cabinet_editor`; Então abre uma janela com a aba Estrutura e um rascunho do módulo.
- 🟢 **Feliz — clique na vista** (`cabinet_editor#CA-11`, `#CA-12`): clicar escolhe a chapa (o fundo é ignorado) ou o vão e a barra mostra "Selecionado: {peça}".
- 🟢 **Falha — sem janela** (`cabinet_editor#CA-02`): "O Editor de Armário precisa de uma janela do Blender aberta." e `CANCELLED`.
- 🟢 **Falha — fora da faixa** (`cabinet_editor#CA-10`): Dado a profundidade limitada a 0,3–0,8 m; Quando escrevo 1,2; Então aparece DIM-003 "valor 1200 mm faixa 300 mm – 800 mm" e a medida não muda.
- 🟢 **Falha — sobreposição interna** (`cabinet_editor#CA-13`): duas prateleiras que se cruzam 5 mm geram GEO-002 e o OK fica bloqueado.

## US-ARM-02 — Experimentar com rascunho, Aplicar, OK e Cancelar

🟡 **Como** projetista (P1), **quero** desfazer, aplicar parcialmente e cancelar voltando ao último ponto aplicado, **para** testar variações do armário sem medo.

Referências: `cabinet_editor/requirements.md#RF-02`.

- 🟢 **Feliz — desfazer/refazer** (`cabinet_editor#CA-03`): Ctrl+Z e Ctrl+Shift+Z reaplicam instantâneos do rascunho sem gravar passo novo.
- 🟢 **Feliz — OK** (`cabinet_editor#CA-05`): com rascunho sem erro, OK reporta "Armário atualizado: {raiz}" e fecha a janela.
- 🟢 **Feliz — cancelar depois de Aplicar** (`cabinet_editor#CA-07`): Dado largura 0,60 aplicada e depois 0,50; Quando cancelo e confirmo "Descartar"; Então o módulo volta a 0,60.
- 🟢 **Falha — OK bloqueado** (`cabinet_editor#CA-06`): com erro DIV-001, OK/Aplicar recusam com "Corrija os erros para confirmar"/"…para aplicar".
- 🟢 **Falha — nada para desfazer** (`cabinet_editor#CA-04`).

## US-ARM-03 — Dividir o armário em vãos

🟡 **Como** projetista (P1), **quero** inserir divisórias verticais, horizontais, múltiplas, móveis ou fixas e definir o número de vãos, **para** organizar o interior conforme o uso do cliente.

Referências: `cabinet_editor/requirements.md#RF-07`, `#RF-08`, `#RF-09`, `#RF-16`.

- 🟢 **Feliz — divisória no meio** (`cabinet_editor#CA-17`): Dado subvão de 0,764 m e chapa de 15 mm; Quando insiro divisória vertical; Então dois subvãos de 0,3745 m e um objeto "Divisória N" filho da raiz.
- 🟢 **Feliz — inserção múltipla** (`cabinet_editor#CA-19`): subvão de 0,90 m com 2 chapas de 15 mm vira três subvãos de 0,29 m.
- 🟢 **Feliz — reflow fora do editor** (`cabinet_editor#CA-31`): mudando a largura por driver, as chapas são reposicionadas mantendo o offset.
- 🟢 **Falha — perto da borda** (`cabinet_editor#CA-18`): offset de 30 mm gera DIV-001 "Deixe pelo menos 50 mm de cada lado".
- 🟢 **Falha — Sem Divisória num vão-raiz** (`cabinet_editor#CA-20`): "Este vão não tem divisória para remover" e nada muda.

## US-ARM-04 — Editar a estrutura: laterais, extras e fundo

🟡 **Como** projetista (P1), **quero** remover ou restaurar laterais escolhendo manter, estender ou reduzir o armário, e escolher o tipo de fundo, **para** encaixar o módulo entre paredes ou outros módulos.

Referências: `cabinet_editor/requirements.md#RF-06`, `#RF-10`, `#RF-14`, `#RF-17`.

- 🟢 **Feliz — remover lateral reduzindo** (`cabinet_editor#CA-15`): Dado lateral de 18 mm e largura 0,80; Quando removo em "Reduzir o armário"; Então a largura vira 0,782 e as outras chapas não saem do lugar.
- 🟢 **Feliz — fundo recuado** (`cabinet_editor#CA-29`): "Inteiro Recuado" restaura o fundo e aplica recuo de 0,02 m.
- 🟢 **Feliz — extras** (`cabinet_editor#CA-24`): com Pés Plásticos ligados surgem 4 cilindros de raio 20 mm a 50 mm dos cantos, 150 mm abaixo da caixa, marcados como ferragem `PE_PLASTICO`.
- 🟢 **Falha — modo não suportado** (`cabinet_editor#CA-16`): biblioteca que só faz KEEP recusa EXTEND com o motivo; pelo bridge o modo cai em KEEP com LIB-001.

## US-ARM-05 — Inserir gavetas, portas, internos para eletro e deslizantes

🟡 **Como** projetista (P1), **quero** inserir frentes e internos pelas abas do Construtor, **para** completar o módulo sem sair do editor.

Referências: `cabinet_editor/requirements.md#RF-11`, `#RF-12`, `#RF-13`, `#RF-15`.

- 🟢 **Feliz — portas invertidas** (`cabinet_editor#CA-25`): escopo "Inteira" + "Inserir invertido" aplica DOOR_RIGHT no vão da biblioteca.
- 🟢 **Falha — gaveta interna fora do frameless** (`cabinet_editor#CA-26`): "Gaveta interna só existe no frameless".
- 🟢 **Falha — painel de forno que não cabe** (`cabinet_editor#CA-27`): subvão de 500 × 700 mm recusa "Painel Forno Externo precisa de um vão de 615 × 615 mm".
- 🟢 **Falha — deslizantes sem profundidade** (`cabinet_editor#CA-28`): vão de 80 mm de profundidade recusa com "Os trilhos precisam de mais profundidade (profundidade 0.090)".
- 🟡 Deslizantes têm geometria simplificada (docstring de `slides.py`); a prioridade Could é inferida.

## US-ARM-06 — Definir o padrão de dimensões da fábrica

🟡 **Como** marceneiro (P2), **quero** editar no Configurador as espessuras, alturas e recuos de cada linha (cozinha, banheiro, dormitório…) numa definição própria, **para** que todo armário novo saia no meu padrão de produção.

Referências: `standards/requirements.md#RF-01` a `#RF-04`, `#RF-12`.

- 🟢 **Feliz — projeto novo** (`standards#CA-03`): a cena nasce com "Padrão Brasil" (ativo) e "Padrão EUA (HB5)".
- 🟢 **Feliz — editar** (`standards#CA-07`): numa definição USER com a cena em cm, digitar "1,8" na espessura da lateral grava 18 mm no rascunho e mostra a pendência antes → depois.
- 🟢 **Feliz — aplicar rascunho** (`standards#CA-09`): a definição recebe valores e montagem, `version` sobe e o relatório lista as mudanças.
- 🟢 **Falha — embutida protegida** (`standards#CA-04`): gravar, aplicar ou apagar "Padrão Brasil" levanta erro; Renomear e Excluir ficam indisponíveis.
- 🟢 **Falha — fora da faixa** (`standards#CA-08`): "99 cm" gera "Valor Inválido" e o rascunho mantém o último valor válido.

## US-ARM-07 — Propagar uma mudança de padrão aos módulos existentes

🟡 **Como** marceneiro (P2), **quero** escolher se a nova definição vale para os módulos já na cena e também para os que diferiam do padrão anterior, **para** atualizar o projeto sem perder ajustes feitos à mão.

Referências: `standards/requirements.md#RF-05`, `#RF-06`, `#RF-07`.

- 🟢 **Feliz — duas perguntas** (`standards#CA-12`): respondendo Sim às duas, módulos no padrão anterior e sem padrão são atualizados na 1ª, o de padrão próprio na 2ª e o herdado é contado como não aplicável com sugestão de conversão.
- 🟢 **Feliz — mantém largura** (`standards#CA-14`): um balcão de 0,9 m recebe a altura 0,8 m do padrão e a largura continua 0,9 m.
- 🟢 **Falha — primeira pergunta cancelada** (`standards#CA-13`): nenhum módulo CAFFMob muda, mas destinos legados da cena já foram gravados e o plano de corte fica desatualizado.
- 🟢 **Regra — medida manual preservada** (`standards#CA-15`): no modo de suporte, medidas em `btm_overrides` não são sobrescritas sem `include_manual`.
- 🟢 **Sem padrão** (`standards#CA-11`): linha desconhecida usa FALLBACK com espessura 0,018 (fundo 0,006) e um aviso.

## US-ARM-08 — Personalizar frente, estilo, puxador e material de cada vão

🟡 **Como** projetista (P1), **quero** trocar por vão a frente (portas, gavetas, basculante), o estilo, o puxador e o material, **para** atender o gosto do cliente módulo a módulo.

Referências: `customize/requirements.md#RF-01` a `#RF-05`, `#RF-07`.

- 🟢 **Feliz — trocar frente** (`customize#CA-03`): num balcão frameless, `set_front(..., 'DRAWERS', 3)` deixa os três vãos como gavetas.
- 🟢 **Feliz — estilo por vão** (`customize#CA-06`): estilo "Vidro" num vão continua após mudar o estilo do projeto.
- 🟢 **Feliz — puxador em todas as frentes** (`customize#CA-08`).
- 🟢 **Feliz — material por grupo e peça** (`customize#CA-10`): grupo CAIXA "MDF" e lateral "Laca" persistem após o recálculo (material da peça vence o do grupo).
- 🟢 **Falha — frente recusada** (`customize#CA-04`): closets recusa "Basculante"; frameless empilha no máximo 4 gavetas e avisa.
- 🟢 **Falha — estilo/puxador/material ausente** (`customize#CA-07`, `#CA-09`, `#CA-11`): a frente não muda e o aviso cita o nome inexistente.

## US-ARM-09 — Configurar o interior do vão

🟡 **Como** projetista (P1), **quero** definir prateleiras, divisórias e gavetas internas com alturas digitadas, **para** organizar o interior sem abrir o editor completo.

Referências: `customize/requirements.md#RF-06`.

- 🟢 **Feliz** (`customize#CA-12`): `Interior(shelves=2, heights=[0.2, 0.45])` cria as prateleiras; `Interior(drawers=2)` cria 2 "Rollout".
- 🟢 **Falha** (`customize#CA-13`): altura fora do vão devolve "altura fora do vão"; alturas que `units.parse_length` não entende geram "Alturas inválidas".

## US-ARM-10 — Manter a personalização quando a biblioteca reconstrói o módulo

🟡 **Como** projetista (P1), **quero** que minhas escolhas sobrevivam a qualquer recálculo do módulo (medida, estilo do projeto, divisões), **para** não refazer o trabalho.

Referências: `customize/requirements.md#RF-08`; `cabinet_editor/requirements.md#RF-16`.

- 🟢 **Feliz — gancho com estrutura** (`customize#CA-16`): depois de cada reconstrução `after_rebuild` reaplica personalização, estrutura, fundo recuado e divisões; chamada aninhada não faz nada.
- 🟢 **Sem custo** (`customize#CA-15`): módulo sem personalização sai sem chamar o adaptador.

## US-ARM-11 — Prender acessórios (agregados) numa face do móvel

🟡 **Como** projetista (P1), **quero** converter uma fruteira, puxador ou nicho em agregado de uma face, posicioná-lo por medida e, se preciso, furar o painel, **para** que o acessório acompanhe o móvel e apareça na produção.

Referências: `aggregates/requirements.md#RF-01` a `#RF-07`, `#RF-17`.

- 🟢 **Feliz — converter** (`aggregates#CA-01`): a fruteira vira filha do painel na face −Y com o relatório "Agregado(s) de <painel>: …".
- 🟢 **Feliz — limite no contorno** (`aggregates#CA-03`): u = −1 vira 0 e v = 5 vira o máximo (700 − 100 mm).
- 🟢 **Feliz — pai muda de tamanho** (`aggregates#CA-05`): o agregado é reposicionado ao novo máximo.
- 🟢 **Feliz — perfurar** (`aggregates#CA-07`): agregado afundado cria o recorte booleano no painel.
- 🟢 **Falha — converter recusado** (`aggregates#CA-02`): objeto grudado ("desgrude antes") ou pai que é folha de porta.
- 🟢 **Falha — afundar além da espessura** (`aggregates#CA-04`): offset −0,030 fica −0,018.
- 🟢 **Falha — furo real indisponível** (`aggregates#CA-08`): fora do topo/base da chapa o "Furo real no plano de corte" fica desabilitado com o motivo.
- 🟢 **Desconverter** (`aggregates#CA-10`): o objeto volta ao pai e à matriz originais.

## US-ARM-12 — Montar folhas de giro e de correr com parada no contato

🟡 **Como** projetista (P1), **quero** converter peças importadas em folhas que abrem e param ao bater, montar esquadrias e instalá-las na parede, **para** simular portas e janelas de móveis ou de obra.

Referências: `aggregates/requirements.md#RF-08` a `#RF-13`.

- 🟢 **Feliz — giro para no contato** (`aggregates#CA-11`): com uma parede a 40° no caminho, a folha para no último ângulo livre e o painel mostra "Folha bateu em <parede>".
- 🟢 **Feliz — curso livre** (`aggregates#CA-13`): folha de correr na esquadria recebe sentido e curso até o batente.
- 🟢 **Feliz — instalar na parede** (`aggregates#CA-18`): a esquadria vira janela HB na parede com peitoril escolhido.
- 🟢 **Falha — pivô ausente** (`aggregates#CA-12`): "Pivô ausente; desconverta e converta de novo".
- 🟢 **Falha — batente pela outra folha** (`aggregates#CA-14`): A para em 0,30 m ao encontrar B.
- 🟢 **Falha — parede não convertida** (`aggregates#CA-18`): "Converta a parede pelo editor de paredes antes de instalar".

## US-ARM-13 — Aplicar molduras (coroa, rodapé, light rail)

🟡 **Como** projetista (P1) usando as linhas herdadas, **quero** aplicar coroa e rodapé contínuos por pacote, **para** dar acabamento de cozinha sem modelar cada perfil.

Referências: `molding/requirements.md#RF-01`, `#RF-02`, `#RF-06`, `#RF-08`.

- 🟢 **Feliz — coroa simples** (`molding#CA-01`): três aéreos face frame alinhados recebem um sweep "MoldingSweep" contínuo.
- 🟢 **Feliz — rodapé atravessa eletro** (`molding#CA-04`) e **canto em L** (`molding#CA-10`).
- 🟢 **Idempotência** (`molding#CA-14`): reconstruir duas vezes não duplica objetos.
- 🟢 **Falha — nenhum alvo** (`molding#CA-06`): cena só com módulos CAFFMob ou closets não gera molduras ("Rebuilt 0 molding run(s)").
- 🟢 **Falha — topos desalinhados** (`molding#CA-02`): diferença > 0,02 m gera sweeps separados.
- 🟡 As molduras só atendem armários frameless/face frame herdados, que ficam atrás da porta legado (ADR 0006); não há equivalente para o módulo CAFFMob.

## US-ARM-14 — Converter armários antigos em módulos CAFFMob

🟡 **Como** usuário de projeto herdado (P3), **quero** ser avisado dos armários antigos ao abrir o arquivo e convertê-los com um relatório do que se perdeu, **para** continuar o projeto com o editor e o padrão novos.

Referências: `legacy/requirements.md#RF-01` a `#RF-08`.

- 🟢 **Feliz — aviso ao abrir** (`legacy#CA-05`): "3 armário(s) de bibliotecas antigas: use Converter para CAFFMob na barra lateral", uma vez.
- 🟢 **Feliz — converter a cena** (`legacy#CA-10`): 5 armários herdados viram 5 módulos CAFFMob com os nomes originais e a mesma caixa (tolerância 2 mm), com relatório de perdas.
- 🟢 **Regra — perdas contadas** (`legacy#CA-08`): gavetas, painéis e frentes especiais sem equivalente são contados no relatório.
- 🟢 **Falha — só o ativo sem armário antigo** (`legacy#CA-11`): "Selecione um armário de biblioteca antiga" e nada muda.
- 🟢 **Falha — erro no meio do lote** (`legacy#CA-13`): o erro sobe e os módulos já construídos ficam ao lado dos originais (sem rollback).
- 🟢 **Porta legado** (`legacy#CA-01`, `#CA-02`): a interface herdada fica oculta por padrão e reaparece com `show_legacy_libraries`.

---

## Lacunas (🔴 relevantes das units)

| Unit | Caso | Lacuna | Fonte |
|---|---|---|---|
| geral | — | 🔴 Fumaças com `bpy` (`blender_004/006/008`, `blender_003_customize_smoke`, `blender_012_*`) não foram reexecutadas nesta extração | requirements de cada unit |
| `cabinet_editor` | EC-03 | 🔴 Montagem e opções da aba Fundos gravam direto no módulo, fora da fila: Ctrl+Z e Cancelar não revertem a montagem e o recuo só vale no próximo pedido | `cabinet_editor/edge-cases.md` |
| `cabinet_editor` | EC-06 | 🔴 Divisória "Tras 15mm": o recuo de trás do item é ignorado | `cabinet_editor/edge-cases.md` |
| `cabinet_editor` | EC-12 | 🔴 Ctrl+Z com deslizantes, internos ou extras apaga e recria as peças a cada passo (nomes e custo no Blender não verificados) | `cabinet_editor/edge-cases.md` |
| `standards` | EC-03 | 🔴 Exportar/importar `.btmdim.json` perde a montagem "Base passante" (volta LATERAL) | `standards/edge-cases.md` |
| `standards` | EC-13 | 🔴 Projeto herdado só com face frame: a migração M-02 ativa "Padrão Brasil" em vez de "Padrão EUA (HB5)" (intenção a confirmar) | `standards/edge-cases.md` |
| `standards` | EC-15 | 🔴 Clicar de novo na linha ativa da árvore pode não disparar a ação | `standards/edge-cases.md` |
| `customize` | EC-02 | 🔴 Closets: estilos do closets tratados como ausentes, com aviso falso | `customize/requirements.md` (lacunas); `customize/edge-cases.md` |
| `customize` | EC-05 | 🔴 Posição de puxador "Lateral" sem efeito em nenhum adaptador | `customize/edge-cases.md` |
| `customize` | EC-06 | 🔴 O painel só grava `door_style`: estilo de gaveta não é editável pelo painel | `customize/edge-cases.md` |
| `aggregates` | EC-01 | 🔴 Agregado com pai Empty (grupo, esquadria, FBX) usa o `bound_box` do Empty, não das peças | `aggregates/edge-cases.md` |
| `aggregates` | EC-02 | 🔴 Desconverter depois de mover o pai devolve a matriz da primeira conversão | `aggregates/edge-cases.md` |
| `aggregates` | EC-07 | 🔴 Folha cujo pai não está num módulo (ex. parede) exclui o pai e todos os descendentes da verificação de contato | `aggregates/edge-cases.md` |
| `aggregates` | EC-16 | 🔴 X/Delete numa parede com balcão que tem agregado (ver `selection` EC-07) | `aggregates/edge-cases.md` |
| `molding` | EC-04 | 🔴 Pack com perfil malha (não curva) causa erro de tipo | `molding/edge-cases.md` |
| `molding` | EC-06 | 🔴 Armários em T: o percurso salta pelo ar até o ramo sobrante | `molding/edge-cases.md` |
| `molding` | EC-07 | 🔴 Corrida só de armários de canto: a "direita do percurso" pode cair para dentro | `molding/edge-cases.md` |
| `molding` | EC-08 | 🔴 1º membro com escala ≠ 1 ou inclinado distorce o sweep | `molding/edge-cases.md` |
| `legacy` | EC-01 | 🔴 Aberturas face frame `PULLOUT`/`TILT_OUT`/`INSET_PANEL`: a mesma frente aparece duas vezes no relatório de perdas | `legacy/edge-cases.md` |
| `legacy` | EC-02 | 🔴 Portas somadas entre aberturas (3 → `DOUBLE` + `EXTRA_DOORS`), divergindo da nota D-24 da 012 ("a maior manda") | `legacy/edge-cases.md` |
| `legacy` | EC-05 | 🔴 Exceção no meio do lote deixa a cena com originais e convertidos lado a lado | `legacy/edge-cases.md` |
