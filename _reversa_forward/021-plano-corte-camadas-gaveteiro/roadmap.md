# Roadmap: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/021-plano-corte-camadas-gaveteiro/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A entrega é estruturada como um conjunto de deltas cirúrgicos sobre os módulos existentes do pacote `caffmob_draw/`, preservando a arquitetura local offline da extensão no Blender ≥ 5.2 e o padrão de núcleos puros testáveis fora do Blender. Em produção (`cutting/`), um novo motor Python puro inspirado no algoritmo guilhotinado recursivo do OpCut substitui/estende o shelf-packing atual, com agrupamento hierárquico por módulo, prévia interna via imagem/painel do Blender e exportação HTML/SVG/PDF. Em organização de cena e fluxo, unificamos a gestão de coleções (`Arquitetura > Parede|Piso|Teto|Aberturas` e `Marcenaria`), adicionamos direção de espessura do piso (±Z), controles rápidos de pé-direito/espessura na aba Ferramentas, botão global de colisão no cabeçalho da Viewport 3D, botão de sincronização de texturas perdidas no painel de Texturas/Materiais, quebra do ciclo infinito do ímã em `stick/`, acesso direto ao Construtor v2 em "Criar Armário" com reestilização/compatibilidade v2 na biblioteca, reconhecimento de paredes rebaixadas no classificador e o conversor não destrutivo "Converter em: Gaveteiro" com detecção geométrica tolerante a peças faltantes.

## 2. Princípios aplicados

> Nota: `.reversa/principles.md` não está presente no repositório. Aplicam-se as diretrizes permanentes do projeto (`CLAUDE.md`, `AGENTS.md` e `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual`).

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Edição exclusiva no pacote `caffmob_draw/` | Todos os deltas incidem em `caffmob_draw/` e testes em `tests/`; nenhum arquivo espelhado legado é editado | respeita |
| Operações não destrutivas com `UNDO` e limpeza no `unregister` | Conversão em gaveteiro preserva origens ocultas fora do corte; todos os operadores declaram `UNDO` e handlers novos têm remoção no `unregister` | respeita |
| Núcleos puros testáveis fora do Blender | Otimizador OpCut, agrupador de lista de peças, classificador geométrico de gavetas e regras de supressão do ímã vivem em módulos Python puros | respeita |
| Internacionalização bilíngue (`pt_BR` e `en_US`) | Todos os novos rótulos, menus e avisos entram nos catálogos de tradução | respeita |
| Operação local sem custo de API de IA | Motor OpCut e análise geométrica de gaveteiro executam 100% offline e localmente | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Embutir o algoritmo guilhotinado recursivo compatível com OpCut (`forward_greedy` / `greedy` com escolha de melhor corte e suporte a rotação por veio) em núcleo Python puro `caffmob_draw/cutting/opcut_core.py`, sem depender de servidor HTTP nem binário externo | Decisão 1a do `/reversa-clarify`; elimina dependência de processo externo, funciona 100% offline e mantém o pacote auto-contido no ZIP da extensão | Chamar CLI/servidor HTTP do OpCut; manter apenas o Next-Fit Decreasing atual (`nesting.py`) | 🟢 |
| D-02 | Renderizar visualização das chapas dentro do Blender em `bpy.data.images` (buffer RGBA desenhado em Python puro / SVG rasterizado ou preview em painel UI) e gerar exportação direta em SVG, HTML (com SVG embutido + lista agrupada por módulo) e PDF vetorial puro em Python (sem dependência externa) | Garante visualização imediata dentro do Blender e exportação multi-formato (HTML/SVG/PDF) sem exigir wheels pesados como ReportLab ou Cairo | Exigir biblioteca PDF externa no `blender_manifest.toml`; abrir apenas navegador externo | 🟢 |
| D-03 | Centralizar o roteamento de coleções em um helper compartilhado (`caffmob_draw/data/layers.py` ou extensão de `walls2d/layers.py`) com helpers explícitos `ensure_arch_subcollection(scene, kind)` (`Parede`, `Piso`, `Teto`, `Aberturas`) e `ensure_marcenaria_collection(scene)` (`Marcenaria`), preservando o comportamento de `e_raiz()` em `armario_v2/build.py` via propriedade customizada em vez de depender do nome da coleção | Hoje `armario_v2/build.py:e_raiz` testa `colecao.name == COLECAO`; mover armários para `Marcenaria` sem desvincular a detecção de raiz quebraria o motor v2 em arquivos novos e antigos | Manter `Armário v2` como coleção separada; duplicar lógica de criação de coleção em cada operador | 🟢 |
| D-04 | Modelar a direção da espessura do piso por propriedade de cena/piso `floor_thickness_direction` (`'DOWN'` padrão, `'UP'`) e `floor_thickness` (metros, padrão 0,15 m), aplicada na extrusão de `floor_builder.py` e `walls2d/apply.py` | Atende RF-06 de forma não destrutiva e consistente tanto no piso manual quanto no ajuste automático pelo contorno das paredes | Usar valor negativo de espessura (confuso na UI e propenso a erros de validação) | 🟢 |
| D-05 | Quebrar o ciclo infinito de `stick` registrando `released_host` e `released_world` (ou cooldown direcional por par item–hospedeiro) em `stick/link.py:release()`, além de marcar `opt_out` sempre que o usuário desgruda manualmente de uma parede (mesmo quando `orig_parent` era `None`); `stick/magnet.py` ignora o `released_host` até o item se afastar além de `tolerance + margem` (ex.: 100 mm) ou ser aproximado intencionalmente | Evidência direta em `stick/link.py:149-151` e `stick/settle.py:76`: quando `orig_parent` é `None`, `opt_out` não era gravado e `settle.run()` regrudava em 0,2 s | Desligar o ímã globalmente ao desgrudar (quebraria o ímã para outros móveis/paredes) | 🟢 |
| D-06 | Alterar `BTM_OT_LibraryCreateCabinet.invoke` (`library_panel/ops_cabinet.py`) para invocar diretamente o Construtor de Armários v2 (`armario_v2`), removendo o desvio para `structure_gallery`; manter o painel de Biblioteca acessível em seu fluxo próprio, reestilizando `library_panel/style.py` para a paleta oficial CAFFMob (removendo `#10302F`/`#0B2322` verde escuro) e roteando inserções de armários da biblioteca para gerarem/compatibilizarem instâncias `armario_v2` | Decisão 2d + compatibilidade v2 do `/reversa-clarify`; resolve a regressão de UX e unifica os armários no motor v2 | Apagar `library_panel/`; manter `structure_gallery` interceptando "Criar Armário" | 🟢 |
| D-07 | Marcar o proxy `<parede>_Rebaixada` criado por `operators/ops_wall_extras.py:lower_wall` com vínculo explícito (`btm_lowered_wall_ref` apontando para a parede original), ensinar `selection/classify.py` a reconhecê-lo como `WALL` (com flag de rebaixada) e exibir "Restaurar Parede" no painel contextual e no menu de contexto quando selecionado | Resolve RF-11 preservando 100% da geometria e medidas da parede original oculta | Deixar a parede original visível com escala Z alterada (distorceria aberturas, booleans e drivers) | 🟢 |
| D-08 | Adicionar botão global de `collision_global` no `VIEW3D_HT_header` (via `append` no registro e `remove` no `unregister`) com ícone/estado claro de ligado/desligado, e botão "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais (`texture_library/`), reaproveitando a fila assíncrona `texture_library/downloads.py` com timeout de 15 s, até 2 retentativas e escrita atômica | Decisão 5c do `/reversa-clarify`; reaproveita a infraestrutura de download já existente sem criar cliente HTTP paralelo | Bloquear a thread principal com `urllib` síncrono; duplicar estado de colisão | 🟢 |
| D-09 | Implementar "Converter em:" como submenu unificado em `ui/context_menu.py` contendo "Armário" (feature 020) e "Gaveteiro" (`caffmob.convert_to_drawer`), com analisador geométrico puro `caffmob_draw/armario_v2/drawer_detect_core.py` que separa submalhas conectadas (quando malha única) ou lê objetos selecionados, classifica os 6 papéis (2 laterais, contrafrente, traseira, fundo, frente) por orientação/dimensão relativa/posição, registra ferragens (corrediças, puxador, fixadores/fitas), pergunta ao usuário se deseja completar peças faltantes sem nunca bloquear e abre o editor ao concluir | Decisão 3d + 3c do `/reversa-clarify`; reutiliza a estrutura de `armario_v2/gavetas.py`, `corredica.py` e `menu.py` | Bloquear conversão se faltar alguma peça; exigir que o usuário separe manualmente a malha antes de converter | 🟢 |

## 4. Premissas

> Nenhuma premissa pendente oriunda de `[DÚVIDA]`: todas as 3 lacunas iniciais e 2 definições complementares foram fechadas em `/reversa-clarify` (2026-11-24).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| n/a (0 `[DÚVIDA]` restantes) | `requirements.md#9. Esclarecimentos` | n/a |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `cutting` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | componente-novo | Adiciona `opcut_core.py` (otimizador guilhotinado offline), `module_list_core.py` (agrupamento por módulo), `plan_render.py` (prévia interna Blender) e `plan_export.py` (HTML/SVG/PDF) |
| `texture_library` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | regra-alterada | Adiciona detector de texturas ausentes em disco e operador assíncrono "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais com timeout/retentativa/escrita atômica |
| `collision` + `ui` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | contrato-alterado | Expõe toggle global de `collision_global` no `VIEW3D_HT_header` com remoção no `unregister` |
| `walls2d` + `operators` + `data` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | regra-alterada | Unifica camadas em `Arquitetura > Parede|Piso|Teto|Aberturas`, adiciona direção de espessura do piso (`DOWN`/`UP`) e controles rápidos de pé-direito/espessura na aba Ferramentas |
| `armario_v2` | `_reversa_sdd/addenda/017-construtor-armario-v2.md#Impacto por artefato da extração` | regra-alterada | Vincula armários à coleção `Marcenaria` (desacoplando `e_raiz()` do nome da coleção) e adiciona núcleo de conversão/edição de Gaveteiro (`drawer_detect_core.py`, `ops_drawer_convert.py`) |
| `stick` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | regra-alterada | Corrige `release()` e `settle.py`/`magnet.py` para impedir reacoplamento infinito após desgrudar e mover para frente |
| `library_panel` | `_reversa_sdd/code-analysis.md#17. Módulo library_panel` | regra-alterada | "Criar Armário" abre diretamente o Construtor v2; `style.py` migra da paleta verde escura para a paleta oficial CAFFMob e inserções ficam compatíveis com `armario_v2` |
| `selection` + `operators/ops_wall_extras` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | regra-alterada | Classificador reconhece proxy de parede rebaixada (`btm_lowered_wall_ref`) e habilita "Restaurar Parede" no painel e menu de contexto |
| `ui/context_menu` | `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | regra-alterada | Adiciona submenu unificado "Converter em:" com "Armário" e "Gaveteiro" acessível por botão direito e toque longo |

## 6. Delta no modelo de dados

- Resumo das mudanças: acréscimo de propriedades opcionais com valores padrão seguros em `Scene` (direção/espessura padrão do piso, padrões rápidos de parede/pé-direito, estado do visualizador OpCut), em `Object.btm_stick` (`released_host_name` para evitar reacoplamento imediato), em objetos proxy de parede rebaixada (`btm_lowered_wall_ref`), na raiz do `armario_v2` (marca explícita `btm_armario_v2_root` desacoplada do nome da coleção) e nos metadados de gaveteiro convertido (`btm_gaveteiro_convertido` com peças reconhecidas/faltantes e ferragens). Nenhuma propriedade existente é removida ou quebrada.
- Detalhe completo em: `_reversa_forward/021-plano-corte-camadas-gaveteiro/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Sincronização de texturas perdidas (re-download do catálogo) | HTTP | `_reversa_forward/021-plano-corte-camadas-gaveteiro/interfaces/texture-sync-http.md` |
| Exportação do Plano de Corte OpCut (HTML, SVG e PDF) e Lista de Peças | arquivo | `_reversa_forward/021-plano-corte-camadas-gaveteiro/interfaces/opcut-export-files.md` |

## 8. Plano de migração

1. **Compatibilidade de raízes `armario_v2` em arquivos `.blend` existentes:** `armario_v2/build.py:e_raiz()` passa a aceitar tanto a nova marca explícita `obj.get('btm_armario_v2_root') == True` quanto o critério legado (`COLECAO` anterior ou coleção `Marcenaria` com `btm_armario` preenchido), evitando quebrar projetos salvos na 017.
2. **Paredes rebaixadas já existentes em arquivos antigos:** `selection/classify.py` reconhece tanto o novo atributo `btm_lowered_wall_ref` quanto o padrão legado de nome `<parede>_Rebaixada` cujo pai possua `LOWERED_PROP`, garantindo restauração inclusive em projetos salvos antes desta entrega.
3. **Coleções existentes:** nenhum objeto de projeto aberto é movido silenciosamente sem ação do usuário; apenas criações, atualizações pelo Editor de Parede/Piso/Teto e conversões roteiam para `Arquitetura > ...` e `Marcenaria`.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Quebrar `armario_v2` ao trocar a coleção de `Armário v2` para `Marcenaria` porque `e_raiz()` verifica o nome da coleção | alto | alta | Desacoplar `e_raiz()` para usar flag explícita `btm_armario_v2_root` + fallback legado, coberto por teste unitário e smoke |
| Heurística de detecção geométrica em malha única de gaveteiro classificar erroneamente peças em modelos fora do padrão | médio | média | Permitir revisão/ajuste manual dos papéis no diálogo de conversão e no editor aberto em seguida, e nunca bloquear conversão quando faltar peça |
| Algoritmo OpCut em Python puro ficar lento para listas muito grandes (> 150 peças) | médio | baixa | Implementar poda por heurística (`forward_greedy` padrão + limite de tempo/iteração configurável) e validar benchmark em testes puros |
| Reestilização de `library_panel/style.py` afetar contraste de textos ou ícones na GPU | médio | baixa | Definir tokens de cor centralizados com razão de contraste verificada (≥ 4,5:1 para texto) sobre a paleta CAFFMob |
| Exportação PDF sem bibliotecas externas gerar arquivo inválido em visualizadores específicos | médio | baixa | Construir escritor PDF 1.4 mínimo validado com estrutura de xref/stream determinística e teste automatizado de integridade do PDF |
| Regressão no `stick` impedir grudar novamente após o usuário querer reaproximar o armário de outra parede | médio | média | Escopar a supressão do ímã exclusivamente ao `released_host` (nunca bloquear outros hospedeiros) e limpar a supressão após afastamento seguro ou ação explícita de "Grudar" |

## 10. Critério de pronto

- [X] As 32 ações de implementação fechadas desde `f2f35215` — resta aberta **apenas** a T033 (verificação visual)
- [X] Suíte pura com os ensaios da 021: **1582 de 1582**, OK com 5 pulados (`unittest discover`, 198,7 s). Os
      pulados são ensaios que exigem as fontes do MOBI da pasta de entrega. Os números anteriores (186/186, 187/187)
      contavam **arquivos**, não ensaios
- [X] Blender 5.2: `tests/blender_021_mcp_e2e.py` **52/52** exit 0 (inclui a prova headless do RF-08);
      `tests/blender_022_mover_sobre_frente.py` **10/10**; `tests/blender_017_armario_smoke.py` OK; sonda de
      interface da 021 **22/22**
      (`_reversa_bugs/cabinet_editor/inspections/2026-11-24-debugger/`)
- [X] Cobertura de internacionalização (`pt_BR` e `en_US`) sem chaves faltantes — `tests/test_i18n_coverage.py`;
      strings da 021 em `caffmob_draw/data/translations/feature_021.json`
- [X] `cross-check.md` fechado pela auditoria de 2026-11-24, sem CRITICAL nem HIGH: 0 MEDIUM e 1 LOW (A004), com a
      situação de cada achado declarada
- [X] `regression-watch.md` gerado — `_reversa_forward/021-plano-corte-camadas-gaveteiro/regression-watch.md`
- [ ] **Aberto:** paridade visual do construtor com o `mockup_construtor_armarios.html` (T033). Exige sessão gráfica;
      a estrutura (sete abas, título, Plano de Corte) está provada, o pixel a pixel não

### 10.1 O que mudou na verificação de 2026-11-24

A auditoria anterior afirmava `202/204` na suíte Blender e `187/187` na pura sem executar. A inspeção do
`/reversa-debugger` executou: das cinco falhas puras, três eram defeito real de ensaio no Windows (ordenação de
`SHA256SUMS`) e uma era `select` em pipe (também defeito de ensaio); as duas viraram os cartões
`BUG-20261124-7H3K` e `BUG-20261124-Q2MF`. A quinta (permissão POSIX) não se reproduziu na reexecução final: a suíte
fechou **1582/1582, OK**, com 5 pulados por fontes do MOBI da pasta de entrega. Na suíte Blender, as duas falhas
restantes são as que exigem MOBI em 127.0.0.1 e foram reproduzidas na asserção exata
(`blender_065_ida_e_volta.py:34` e `blender_ensaio_mobi.py:19`).

O fechamento desta rodada também tirou o RF-08 da cobertura só por inspeção: a seção 12 do
`tests/blender_021_mcp_e2e.py` prova que a aba Ferramentas expõe pé-direito e espessura padrão e que o Editor de
Paredes nasce com os valores gravados na cena (2,85 m e 180 mm). Com isso o ensaio passou a **52/52**. O RF-10 foi
redigido com a condição real do móvel legado (RN-23), e o `cross-check.md` fechou A001/A002/A003/A005; resta aberto
apenas A004, que exige GUI.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-11-24 | §10 marcado com a evidência de cada critério na reconciliação do `/reversa-audit` (a feature já estava entregue; os `[ ]` eram do plano, não do código) | reversa |
