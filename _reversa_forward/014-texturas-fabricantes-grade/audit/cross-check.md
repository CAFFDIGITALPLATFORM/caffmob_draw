# Auditoria cruzada: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-13`
> Artefatos: [`requirements.md`](../requirements.md), [`roadmap.md`](../roadmap.md), [`actions.md`](../actions.md),
> com `data-delta.md`, `interfaces/` e o código do commit `1c9ea2d`.
> Revisores: Claude (cruzamento dos documentos) e Codex CLI 0.162.1 em sandbox somente leitura (código e bugs). Cada
> achado do Codex foi conferido no código; quatro tiveram a severidade revista (A003, A012, A013, A016).

## Resumo

| Severidade | Achados |
|------------|---------|
| CRITICAL | 0 |
| HIGH | 6 |
| MEDIUM | 11 |
| LOW | 6 |
| **Total** | **23** |

As 47 ações estão concluídas e a bateria de testes passa. Os achados abaixo são o que os testes não pegaram:
segurança da rede, corridas entre pedidos assíncronos e lacunas de escopo entre o requisito e o que foi entregue.

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Código: segurança | O token de acesso vai para qualquer URL absoluta que o catálogo do servidor indicar, já na primeira requisição (o cuidado com outro domínio só vale no redirecionamento) | `texture_library/downloader.py` (`build`, `_fetch`, `opener`) |
| A002 | HIGH | Contrato | HTTPS não é exigido: o contrato diz "só HTTPS", mas o endereço das preferências, os arquivos e os redirecionamentos aceitam HTTP | `texture_library/downloads.py` (`server_url`); `downloader.py` (`url`); `interfaces/servidor-texturas.md` §Convenções |
| A003 | MEDIUM | Código: segurança | `cache_path` não confina o destino: um id com `..` grava fora do cache. O id vem do catálogo do pacote (não do servidor), então só um pacote adulterado aciona | `texture_library/downloads.py` (`cache_path`); `catalog_core.py` |
| A004 | HIGH | Código: corrida | Dois pedidos da mesma textura antes da resposta do catálogo do servidor: o segundo remove a entrada já ATIVA e enfileira de novo, e dois downloads escrevem no mesmo `.part` | `texture_library/downloads.py` (`fetch`, `with_items`) |
| A005 | HIGH | Código: corrida | Cancelar e pedir de novo a mesma textura: o novo `get` limpa o cancelamento da thread antiga, e a resposta "cancelled" antiga consome os callbacks novos | `downloads.py` (`cancel`, `_dispatch`); `downloader.py` (`handle`) |
| A006 | MEDIUM | Código: corrida | "Cancelar downloads" não alcança pedidos ainda esperando token ou catálogo; eles começam depois e aplicam a textura | `downloads.py` (`cancel_all`, `fetch`) |
| A007 | HIGH | Código: sessão | Uma renovação em andamento no momento de "Sair" grava a sessão de novo quando a resposta chega: o projetista volta a ficar conectado | `texture_library/auth.py` (`with_access` → `done` → `_save`; `logout`) |
| A008 | HIGH | Código: sessão | Trocar o servidor durante uma renovação deixa `_state["refreshing"]` cheio e a requisição descartada: todo pedido seguinte espera para sempre | `caffmob_draw/__init__.py` (`_update_textures_server`); `auth.py` (`reload`) |
| A009 | MEDIUM | Contrato | 401 nas chamadas JSON (catálogo, permissões) não renova a sessão nem repete, contra a tabela de erros do contrato; só o download trata 401 | `downloads.py` (`request`); `auth.py` (`fetch_entitlements`) |
| A010 | MEDIUM | Código: Blender | O timer das miniaturas não é `persistent`; abrir outro arquivo o remove, mas `_state["timer"]` continua verdadeiro e as miniaturas novas param de carregar. O `load_pre` não libera esse estado | `library_panel/thumbs_gpu.py` (`_ensure_timer`); `texture_library/handlers.py` (`on_load_pre`) |
| A011 | MEDIUM | Código: lógica | `relink` aponta todos os nós de imagem do material para a imagem de cor, inclusive o nó de relevo (T045) | `texture_library/handlers.py` (`relink`) |
| A012 | LOW | Código: princípio VII | Desativar a extensão no meio de um arraste não remove o draw handler da miniatura sob o cursor | `library_panel/ops_drag.py` (`unregister`) |
| A013 | LOW | Código: borda | O download assíncrono reencontra o alvo pelo nome; apagar o objeto e criar outro com o mesmo nome aplica a textura no novo | `texture_library/apply.py` (`apply` → `done`) |
| A014 | MEDIUM | Contrato de dados | Catálogo com item sem campos (`items: [{}]`) passa no `parse_catalog` e quebra com `KeyError('id')` no `load`, em vez do catálogo vazio com aviso do data-delta (reproduzido) | `texture_library/catalog_core.py` (`parse_catalog`); `catalog.py` (`load`) |
| A015 | MEDIUM | Cobertura | RN-08 e RN-10 incluem **objetos** na grade e no arraste; a T040 entregou só modelos prontos e módulos salvos, e o `from_drag` de `object_insert` (T033) não tem quem use | `library_panel/draw.py` (`block_entries`); `ops_drag.py` (`_hand_off`); `actions.md` T040 |
| A016 | LOW | Cobertura | Modelos prontos usam um desenho genérico de módulo, não uma miniatura própria (a RN-08 fala da miniatura "gerada ao salvar", que modelo pronto não tem) | `library_panel/draw.py` (`block_entries`, `_draw_block_cell`) |
| A017 | MEDIUM | Código: interface | A coluna de fabricantes e coleções corta as linhas que não cabem e não rola: com o painel baixo, fabricantes e coleções do fim ficam inalcançáveis | `library_panel/layout_core.py` (`sidebar_rows`) |
| A018 | MEDIUM | Código: lógica (RF-16) | `clamp_rect` move e encolhe a altura, mas nunca a largura: há casos com espaço livre em que o painel fica por cima de uma área ocupada (reproduzido: região 1200 × 800, painel 1000 × 600, obstáculo em x 600–700) | `library_panel/grid_core.py` (`clamp_rect`) |
| A019 | MEDIUM | Cobertura (D-15, RF-19) | "Baixar tudo" aparece habilitado para conta sem `download_all`; a recusa só vem depois da confirmação. D-15 diz "só é oferecido com `download_all: true`" | `texture_library/ops_account.py` (`draw_account`, `poll`) |
| A020 | MEDIUM | Consistência | RF-14 diz "Eucatex 19, Formica 24" texturas com relevo; o catálogo gerado tem 15 itens com `bump` | `requirements.md` §8 (RF-14); `caffmob_draw/textures/catalog.json` |
| A021 | LOW | Consistência | O data-delta §6 define `tab` como `CAT:<nome>` ou `TEXTURAS`; o código usa `BLOCKS`/`TEXTURES` e guarda a categoria em `category` | `data-delta.md` §6; `library_panel/props.py` |
| A022 | LOW | Cobertura | RN-05 (aplicar textura) não é citada no roadmap; está coberta de fato por D-08 e pela T025 | `roadmap.md` §3 |
| A023 | LOW | Cobertura | D-16 (contrato e servidor falso) não é citada no `actions.md`; T003 e T047 a cobrem sem o ID | `actions.md` T003, T047 |

## Impacto dos achados HIGH

**A001, token para outro domínio.** O servidor da CAF Mob é quem monta o catálogo; um erro de configuração (URL
absoluta de CDN) ou um catálogo adulterado entrega o token de acesso a terceiros. O token dura 15 minutos, mas abre a
conta. Direção: mandar `Authorization` só para a origem de `textures_server_url`, na primeira requisição e nos
redirecionamentos. É correção de código: `/reversa-debugger` para registrar e `/reversa-debugger-fix` para corrigir.

**A002, HTTP aceito.** Com um endereço `http://` nas preferências, o token de renovação viaja sem criptografia. O
contrato já decide "só HTTPS"; falta o código cumprir, com exceção explícita para `127.0.0.1` nos testes. Mesmo
caminho: `/reversa-debugger`.

**A004 e A005, downloads duplicados e cancelamento.** Acontecem no uso normal: aplicar a mesma textura a duas peças
logo depois de abrir o Blender, ou cancelar e arrastar de novo. O efeito vai de hash falho até textura não aplicada.
Direção: reservar a tarefa antes das etapas assíncronas e dar a cada tentativa um número de geração, ignorando
respostas antigas. `/reversa-debugger`, um bug para os dois (mesma causa: identidade da tarefa só pelo id).

**A007 e A008, sessão.** Sair e continuar conectado (A007) contraria o que o projetista pediu. Trocar o servidor
travar a conta até reiniciar o Blender (A008) aparece na publicação, quando o endereço for configurado. Direção: uma
geração de sessão que `logout` e a troca de servidor incrementam, descartando respostas antigas e resolvendo os
callbacks pendentes. `/reversa-debugger`.

Os HIGH não contradizem nenhuma regra 🟢 do legado; são defeitos do código novo. Nenhum documento precisa mudar
para corrigi-los, salvo o registro dos bugs.

## Itens verificados que passaram

**Cobertura**
- Os 22 RFs se ligam a pelo menos uma RN, e as 14 RNs aparecem no roadmap (RN-02 e RN-03 pela faixa "RN-01 a
  RN-04"), exceto RN-05 (A022).
- As 18 decisões aparecem no `actions.md`, exceto D-16 (A023).
- Os 15 cenários Gherkin têm ação e teste: catálogo e miniaturas (T015, `test_texture_catalog`), sob demanda, sem
  conta, baixar tudo e sem internet (`blender_014_textures_net`), arquivo corrompido (`test_texture_catalog`), buscar
  e aplicar, grade, maximizar e fixar, minimizar sem cobrir (`blender_014_panel_smoke`, `blender_014_hud_rects`),
  arrastar bloco, textura, soltar no vazio e cancelar (`blender_014_drag_smoke`).

**Consistência**
- Todo RF e toda D citados no roadmap e no `actions.md` existem. RN-15 e RN-17 citados são do legado
  (`_reversa_sdd/library_panel` e `_reversa_sdd/object_library`).
- Os dois contratos de `interfaces/` (servidor e catálogo) aparecem no roadmap (D-02, D-16).
- Os termos centrais (textura, catálogo, miniatura, conta CAF Mob, "Baixar tudo") são os mesmos nos três documentos.

**Coerência com o legado**
- As regras 🟢 alteradas estão registradas: RN-17 (W001, W002), integrações (W003), F-09 (W004),
  RN-13/RN-LIBRARY_PANEL-02 (W005), RN-14/RN-LIBRARY_PANEL-03 (W006). D-01 registra que reabre a D-15 da 012.
- Os componentes do `_reversa_sdd/architecture.md` citados existem (`library_panel/`, `object_library/retexture.py`,
  `customize/adapters/common.py`, `operators/viewport_hud.py`).

**Sanidade do actions**
- As 47 ações têm dependências que apontam para IDs existentes; não há ciclo.
- Nenhum par de ações `[//]` tem o mesmo arquivo alvo.
