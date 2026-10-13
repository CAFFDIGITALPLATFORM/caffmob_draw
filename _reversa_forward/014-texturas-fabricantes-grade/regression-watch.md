# Regression watch: Texturas dos fabricantes de chapas e biblioteca em grade

> Identificador: `014-texturas-fabricantes-grade`
> Criado em: `2026-10-12` (rodada 1 do `/reversa-coding`)

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `_reversa_sdd/object_library/requirements.md#RN-17` | A imagem própria quadrada continua gerando o material "Textura: <arquivo> <tamanho> mm", com escala `1/(mm/1000)` nos três eixos e reaproveitado por caminho e tamanho; a chamada com dois argumentos não muda | presença | A re-extração descreve a RN-17 sem o caso quadrado, com outro nome de material, ou a `blender_009_library_smoke` falha em "a mesma imagem e tamanho reaproveitam o material" |
| W002 | `_reversa_sdd/object_library/requirements.md#RN-17` | O material de imagem aceita largura e altura distintas, tem uma variante de veio chamada `<nome> ROTATED` (com rotação de 90°) e guarda `btm_texture_id` quando vem do catálogo | redação | A re-extração descreve o material de imagem só com um tamanho, ou sem a variante de veio |
| W003 | `_reversa_sdd/architecture.md#Integrações e distribuição` | O manifesto declara a permissão `network`, e o pacote não contém imagem de fabricante em tamanho real | presença | Manifesto sem `network`, ou o ZIP contendo arquivos de `caffmob_draw/textures/` fora de `thumbs/` e `catalog.json` |
| W004 | `_reversa_sdd/library_panel/design.md#F-09` | O painel tem três estados (minimizado, aberto, maximizado), desenhados com a placa Noite e o ícone CAFF MOBI DRAW; o aberto mostra o botão de maximizar no rótulo; o maximizado desenha cabeçalho, coluna de fabricantes, grade de miniaturas com recorte e rodapé de download; o desenho não grava no estado | redação | A re-extração descreve o `draw_panel` só com o rótulo azul (`BG_TITLE`) e a coluna cinza, sem os três estados, ou o desenho gravando no `WindowManager.btm_library` |
| W005 | `_reversa_sdd/library_panel/requirements.md#RN-13` e `_reversa_sdd/domain.md#RN-LIBRARY_PANEL-02` | Clique fora e Esc fecham o painel como na 012, **exceto** com o retângulo maximizado fixo: aí o clique fora segue para a cena sem fechar e o Esc não é consumido | redação | A re-extração descreve o clique fora e o Esc sem a exceção do painel fixo, ou a `blender_014_panel_smoke` falha em "fixo: clique fora segue para a cena e não fecha" |
| W006 | `_reversa_sdd/library_panel/requirements.md#RN-14` e `_reversa_sdd/domain.md#RN-LIBRARY_PANEL-03` | Escolher uma categoria grava categoria e linha e abre a grade dela no retângulo maximizado (aba Blocos: modelos prontos e módulos salvos, com miniatura do módulo); o popover existe só como reserva | redação | A re-extração descreve a categoria abrindo o popover como rota principal, ou a `blender_012_library_ui` falha em "categoria abre a grade da categoria pelo keymap" |

## Histórico de re-extrações

_Vazio: será preenchido pelo agente reverso quando `/reversa` rodar de novo._

## Arquivadas

_Vazio._

## Observações

- RN-LIBRARY_PANEL-02 e RN-LIBRARY_PANEL-03 (🟢) mudaram na rodada 5 e viraram W005 e W006.
- O desvio das áreas ocupadas (T029) e o veio pelo eixo X da peça (RN-06) são decisões 🟡 e ficam fora do watch.
- As regras novas da feature (RN-01 a RN-14 do `requirements.md`) não vêm de `_reversa_sdd/` e não entram como watch
  de regressão. A próxima re-extração deve registrá-las como regras novas do domínio.
