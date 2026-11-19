# Adendo: 016-seletor-sobreposicao

- **Feature:** 016, seletor de objetos sobrepostos da viewport 3D
- **Identificador:** `016-seletor-sobreposicao`
- **Data:** 2026-11-19
- **Cenário:** legado (âncora: `_reversa_sdd/architecture.md` e `_reversa_sdd/domain.md` deste repositório)

## Vigência

Vigente desde 2026-11-19.

## Resumo da entrega

O projetista perde tempo quando vários objetos ficam empilhados no mesmo ponto da viewport, porque o clique pega
sempre o primeiro do Blender. A feature 016 traz para dentro da extensão o seletor de sobreposição do pacote
anexado: `Ctrl + Alt + clique` (ou o item do menu de contexto) abre, sobre o cursor, a lista dos objetos `MESH`
atingidos pelo raio, do mais próximo ao mais distante, com destaque do item em foco, marcação item a item, isolar e
confirmar ou cancelar. A seleção só é aplicada no `Enter`, com o item em foco como ativo; cancelar devolve seleção,
ativo e visibilidade exatamente como estavam. Nada é gravado na cena, então não há migração nem desfazer.

Ações concluídas: **15 de 15** (`T001` a `T015`). A T001 mediu o raio por objeto em 2.001 candidatos: 0,015 s de
mediana, 0,019 s no pior caso, muito abaixo do limite de 1 s, então a poda de candidatos prevista como mitigação não
entrou no código.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Limites e organização | componente-novo | A camada de Interação e Posicionamento ganha `selection/overlap_core.py` (núcleo puro) e `selection/overlap_select.py` (operador modal e item de keymap) |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Fluxos entre componentes | regra-alterada | Existe um fluxo modal de inspeção que abre pela viewport e pelo menu de contexto, desenha painel e destaque de sessão e devolve seleção, ativo e visibilidade em toda saída |
| `_reversa_sdd/architecture.md` | 4. Dívidas Técnicas e Lacunas Identificadas | regra-alterada | A limpeza incompleta de modal no cancelamento externo passou a ter um caminho pronto no seletor (`cancel_active()` chamado no `unregister`); os demais modais seguem como estavam |
| `_reversa_sdd/selection/design.md` | Visão de Camadas | componente-novo | Duas linhas novas: `overlap_core.py` na coluna de núcleo puro e `overlap_select.py` na de Blender; o pacote continua sem `register` próprio, o registro é do `caffmob_draw/__init__.py` |
| `_reversa_sdd/selection/design.md` | Interface | componente-novo | Núcleo: `rank`, `Picker`, `panel_rect`, `rows_rect`, `row_at` e `action_at`. Ponte: `hits_along`, `snapshot_state`, `apply_selection`, `restore_state`, `isolate`, `restore_visibility` e `cancel_active` |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas | regra-nova | O catálogo precisa receber as regras do seletor (RN-01 a RN-12 do `requirements.md` da 016): só `MESH` visível e selecionável, seleção aplicada só no `Enter`, isolamento temporário por `hide_set`, nada gravado na cena |
| `_reversa_sdd/data-dictionary.md` | Objetos e cena | delta-de-dados | Nenhum campo novo: achados, marcados, foco, rolagem, seleção e ativo originais e o mapa de `hide_get()` vivem na instância do modal e desaparecem ao fechar |
| `_reversa_sdd/deployment.md` | Re-extração 2026-10-10 — arquitetura atual (`blender_manifest.toml`) | delta-de-contrato-externo | Sem mudança de manifesto nem de versão: a entrega é de código, textos e testes, e o pacote continua no mesmo `blender_manifest.toml` |

## Regras sob vigilância

`W001` a `W004`, em `_reversa_forward/016-seletor-sobreposicao/regression-watch.md`: Alt + clique e Alt + Shift +
clique do `component_pick` (W001), normalizador suspenso durante modal (W002), seleção promovida à raiz no `Enter`
(W003) e ausência de propriedade nova na cena (W004).

## Fontes

- `_reversa_forward/016-seletor-sobreposicao/legacy-impact.md`
- `_reversa_forward/016-seletor-sobreposicao/regression-watch.md`
- `_reversa_forward/016-seletor-sobreposicao/requirements.md`
- `_reversa_forward/016-seletor-sobreposicao/actions.md`
- `_reversa_forward/016-seletor-sobreposicao/progress.jsonl`

## Atualização 2026-11-19

A feature foi exercitada com janela no Blender 5.2, por eventos simulados (`tests/blender_016_overlap_window.py`), e o
ensaio achou quatro defeitos que a fumaça em segundo plano não alcançava. Todos foram corrigidos e o ensaio ficou
verde: atalho, clique nas linhas, isolar, confirmar, cancelar e o botão do menu.

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/selection/design.md` | Interface | regra-nova | O núcleo puro ganha `confirm_selection(hits, staged, original, original_active, focus)`: o `Enter` soma à seleção anterior e tira o que foi desmarcado (RF-12), com o item em foco como ativo quando está marcado |
| `_reversa_sdd/domain.md` | Catálogo de regras extraídas (família do seletor) | regra-alterada | Leia a confirmação como delta sobre a seleção viva, nunca como substituição: o que está fora da lista continua selecionado e, dentro da lista, vale a marcação |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Fluxos entre componentes | regra-alterada | O painel fica preso ao ponto da abertura, e não acompanha o mouse; sem isso nenhuma linha seria clicável. O modal continua sem tocar seleção nem ativo antes do `Enter` |
| `_reversa_sdd/architecture.md` | Re-extração 2026-10-10 — arquitetura atual, Limites e organização | regra-alterada | O `poll` do operador vale por área `VIEW_3D` em modo objeto, porque dentro do popup do menu a região não é a da viewport; o `invoke` resolve a região `WINDOW` e o ponto do cursor sai de `Event.mouse_x/mouse_y` (`Window.mouse_x` não existe no 5.2) |
| `_reversa_sdd/data-dictionary.md` | Objetos e cena | delta-de-dados | Sem mudança: `anchor`, `mouse`, `picker`, `state` e o mapa de `hide_get()` seguem só na instância do modal |

As regras sob vigilância continuam as mesmas: `W001` a `W004`, em
`_reversa_forward/016-seletor-sobreposicao/regression-watch.md`.
