# Roadmap: Paridade restante do Construtor e padrão completo da Biblioteca

> Identificador: `026-paridade-total-construtor-biblioteca`
> Data: `2026-11-26`

## Decisões

| ID | Decisão | Requisitos | Justificativa |
|----|---------|------------|---------------|
| D-01 | A toolbar usa operadores reais e campos da sessão; nada de botão decorativo. | RF-01, RF-09, RF-10 | O mockup é funcional; cada controle precisa de efeito e prova. |
| D-02 | O export é um operador com `ExportHelper` e um núcleo puro `parity_core.payload`. | RF-02, RF-08 | Permite testar o payload sem Blender e manter o schema estável. |
| D-03 | O titlebar é o cabeçalho nativo do painel, com título, dimensões e ações. | RF-03 | Emula o mockup sem uma camada GPU própria, decisão aceita na 023. |
| D-04 | As sete abas ficam em uma única `row` horizontal, com ícones e aba ativa deprimida. | RF-04 | Corrige a exclusão “sem abas horizontais” da 023. |
| D-05 | Botão direito seleciona e chama um `Menu` com Duplicar/Medida/Espelhar/Apagar. | RF-05, RF-06 | Reaproveita os operadores de lote e medida. |
| D-06 | A duplicata copia o objeto e grava `ajustes.duplicada`; `build.gerar` recria a cópia. | RF-05 | Sem isso a duplicata sumiria no próximo Gerar. |
| D-07 | O popover de medida usa `invoke_props_dialog` e altera o spec + regenera. | RF-06 | É o caminho nativo para um popover modal no Blender. |
| D-08 | O arraste é tratado no modal: press guarda posição, move converte px→mm pela escala do preview, release grava o ajuste. | RF-07 | O modal já existe; evita handler concorrente e mantém um único undo. |
| D-09 | A cutlist reutiliza o painel de peças e o mesmo payload do export. | RF-08 | Uma fonte de verdade para lista e arquivo. |
| D-10 | Apenas Laterais altera as flags do spec e chama o Gerar; o preview filtra `papel == LATERAL`. | RF-09 | Ação de produto, não apenas filtro visual. |
| D-11 | O tema do preview troca tokens globais e as peças leem a cor em tempo de desenho; a Biblioteca troca tokens e usa `THEME` no cabeçalho. | RF-10, RF-13 | Remove o `CORES` estático que impedia o Dark. |
| D-12 | A Biblioteca usa as quatro categorias do documento; “Armários” mostra todo o acervo de armários; a grade de Blocos fixa 2 colunas e o acerto mínimo é 44 px. | RF-11, RF-12, RF-14 | O documento vence o código; a grade de texturas não é quebrada. |
| D-13 | A regressão preserva 025, 023, card, UI, i18n, API e smoke. | RF-15–RF-18 | A 026 é aditiva; não reabre as anteriores. |

## Fluxo

1. Sessão: `vista`, `tema`, `apenas_laterais`, escalas.
2. Preview: tema → filtro de portas/laterais → vista única/dupla → hits/escala.
3. Operadores: vista/tema/laterais/abrir-tudo/painel/medida/duplicar/export.
4. Modal: seleção, contexto, arraste, N, Esc.
5. Painel: titlebar, abas, toolbar, seleção, cutlist, contrato, rodapé.
6. Biblioteca: categorias, tema, grade 2×3, alvo 44 px.
7. Provas e fechamento Reversa.

## Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Arraste competir com o clique de seleção | Limite de 3 px; clique parado continua seleção. |
| Duplicata sumir no Gerar | Ajuste persistido + cópia no `build.gerar`, provado por ensaio. |
| Tema não repintar peças | `_cor_do_papel` lê os globais no desenho, não um dicionário congelado. |
| Categorias quebrarem o card | Linhas/ambientes continuam em `LINES`; só a navegação mudou. |
| Grade 2×3 quebrar texturas | `fixed=2` só para Blocos; texturas usam o cálculo por largura. |
