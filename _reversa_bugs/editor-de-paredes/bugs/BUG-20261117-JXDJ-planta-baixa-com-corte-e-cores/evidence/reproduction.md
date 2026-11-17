# Cápsula de Reprodução — BUG-20261117-JXDJ

## Identificação
- **Bug:** BUG-20261117-JXDJ (display_number 148)
- **Título:** Sem planta baixa dos objetos da cena com corte superior e cores
- **Contexto:** editor-de-paredes (módulo walls2d, feature 002-editor-parede-mover-sobre)
- **Status:** open → em investigação

## Ambiente
- **OS:** Windows 11 (workstation do titular)
- **Runtime:** Blender 5.2 (addon CAFF MOBI instalado, sondagem MCP confirma operadores disponíveis)
- **Git:** não disponível neste ambiente (commit base e branch não capturados)
- **Branch:** não capturada

## Comando executado / Steps to Reproduce
1. Abrir o Editor de Paredes com um ambiente e móveis na cena.
2. Procurar no painel do editor qualquer opção de mostrar objetos, corte superior ou cor por material.

## Resultado observado
Nenhuma dessas opções existe. `draw_plan` (`caffmob_draw/walls2d/ops_editor.py`) desenha apenas:
- fundo, grade,
- paredes do rascunho (`s.plan.chains`) com uma cor única (`COLORS['wall']`),
- paredes da camada nova como referência tracejada (`s.plan.references`),
- nós, crosshair, hints, toolbar.

Não há:
- leitura de objetos da cena (mobiliário, portas, janelas),
- plano de corte superior (altura configurável),
- preenchimento 2D por material (cor sólida ou textura real),
- toggle entre "só paredes" e "planta baixa com objetos".

## Resultado esperado
- Uma opção no editor troca entre "só paredes" e "planta baixa com objetos".
- Um campo de corte superior (altura) define onde a cena é cortada; objetos/partes acima do corte não aparecem.
- Objetos aparecem em 2D com preenchimento por material, alternando entre cor sólida e textura real.
- Navegação, zoom e edição de paredes continuam funcionando com a planta baixa ligada.

## Taxa e determinismo
- **Classificação:** deterministic
- **Taxa:** 1/1 (leitura do código e sondagem MCP: nenhum operador de planta no namespace do editor)
- **Gatilhos suspeitos:** nenhum (funcionalidade inexistente, não intermitente)

## Evidências
- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: captura do editor, sem controle de planta baixa, corte ou cor.
- `../../intake/relato-20261117-1430.md` (Problema 5).
- `../../intake/relato-20261117-1520.md` e `../../intake/manual-ctb-cores-espessuras-20261117.webp`: padrão CTB do titular.
- Código lido: `caffmob_draw/walls2d/ops_editor.py` (`draw_plan`), `caffmob_draw/operators/layouts.py` (`generate_2d_plan`, `create_plan_view`).
- `../../intake/sondagem-mcp-20261117.md`: dos 223 operadores `caffmob.*` instalados, nenhum desenha planta de objetos com corte ou cor dentro do editor.

## Testes existentes relacionados
- `tests/blender_002_ui_events.py` — eventos de UI do editor (não cobre planta baixa com objetos)
- `tests/blender_002_smoke.py` — teste de fumaça da feature 002 (não cobre planta baixa com objetos)