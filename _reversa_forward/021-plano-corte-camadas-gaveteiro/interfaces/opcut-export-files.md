# Contrato de Interface: Exportação do Plano de Corte OpCut e Lista por Módulo (Arquivo Local)

> Feature: `021-plano-corte-camadas-gaveteiro`
> Tipo: Arquivo local (SVG, HTML, PDF) + Imagem interna no Blender (`bpy.data.images`)
> Referência: RF-01, RF-02, RN-01, RN-02

## 1. Entrada do Motor (`opcut_core.py`)

- **Chapas (`panels`):** lista de chapas disponíveis agrupadas por `(material, thickness_mm)` com `width_mm` (padrão `2750.0`), `height_mm` (padrão `1830.0`), `margin_mm` (refilo perimetral padrão `10.0`), `kerf_mm` (espessura da serra padrão `4.0`).
- **Peças (`items`):** lista de `NestingPart` filtrada (excluindo ferragens e `btm_cut_exclude`), contendo `id`, `name`, `module_ref`, `width_mm`, `height_mm`, `thickness_mm`, `material`, `can_rotate` (`grain_direction == 'NONE'`), `edges[4]` e `quantity`.
- **Método:** `forward_greedy` (padrão) ou `greedy`, determinístico para a mesma entrada.

## 2. Saída Estruturada (`CutPlanResult`)

- `sheets`: lista de chapas alocadas, cada uma com `sheet_index`, `material`, `thickness_mm`, `width_mm`, `height_mm`, `margin_mm`, `used_rects` (posição `x`, `y`, `w`, `h`, `rotated`, `part_id`, `label`, `module_ref`), `unused_rects`, `cuts` (segmentos guilhotinados) e `efficiency_pct`.
- `unplaced`: lista explícita de peças que não couberam na área útil da chapa, com motivo (`EXCEEDS_SHEET_AREA`).
- `modules_summary`: lista agrupada por `module_ref` com total de chapas, área total em m² e itens ordenados.

## 3. Formatos de Saída

| Formato | Conteúdo | Escrita |
|---------|----------|---------|
| **Preview Blender** | Imagem RGBA em memória (`bpy.data.images`, ex.: `CAFFMob_PlanoCorte_Chapa_N`) exibida no painel com seletor de chapa (anterior/próxima), cores por módulo e cotas | Em memória |
| **SVG** | Vetorial em escala real (mm), contorno da chapa, linha de refilo, peças rotuladas com ID/dimensões/indicador de rotação e linhas de corte guilhotinado | Atômica (`.tmp` + `os.replace`) |
| **HTML** | Documento autocontido (offline, zero CDNs externas) contendo resumo por módulo (lista de peças agrupadas), métricas de aproveitamento e SVGs embutidos de todas as chapas, pronto para impressão (`@media print`) | Atômica (`.tmp` + `os.replace`) |
| **PDF** | Documento PDF 1.4 vetorial gerado em Python puro (1 página de lista agrupada por módulo + 1 página por chapa com desenho vetorial e legendas) | Atômica (`.tmp` + `os.replace`) |

## 4. Tratamento de Erros

- Lista de peças vazia: não gera arquivo e exibe aviso informativo.
- Peça maior que a área útil (`width - 2*margin`, `height - 2*margin`): não trava o algoritmo; registra em `unplaced` e reporta aviso claro com o nome e dimensão da peça.
- Diretório de destino sem permissão de escrita: captura `OSError`, remove eventual `.tmp` e reporta erro legível ao usuário.
