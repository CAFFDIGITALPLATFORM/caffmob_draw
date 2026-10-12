# Regression watch: 010-porta-real-textura-linha

> Gerado por `/reversa-coding` em 2026-10-09. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **Porta e janela de ambiente** (`operators/doors_windows.py`, `openings/sync.py`): a caixa `GeoNodeCage` continua
  cortando a parede, em arame. Dentro dela ficam a porta ou a janela real (grupo FRAME alinhado à caixa, folhas da
  003/007), e o texto "DOOR"/"WINDOW" fica escondido. Uma re-extração deve descrever a porta como peças reais, não
  como a caixa com texto. 🟢
- **Medida da porta** = folha; furo = folha + 98 mm na largura e + 59 mm na altura (`openings/door_core.hole_size`). A
  largura por dois pontos na parede continua sendo a do furo. 🟢
- **Padrões das portas:** 0,80 / 1,60 × 2,10 m (`hb_props.py`). 🟢
- **Colisão da folha** (`aggregates/collision.py`): o marco marcado com `btm_opening_frame` não é obstáculo para as
  folhas da mesma montagem. 🟢
- **SketchUp** (`aggregates/skp_core.tree`): árvore com instâncias aninhadas; instâncias repetidas recebem as
  primitivas pela origem mais próxima; figuras de escala puladas; material reaproveitado pelo nome, cor e imagem;
  `Layer_<x>` → `<x>`. 🟢
- **Modo de vista** (`ui/view_mode.py`): `Scene.btm_view_mode`, `btm_view_lines` e `btm_view_prev_color`; limiar de
  linhas 0,5 e opacidade 0,6 (`view_mode_core`). 🟡
- **Lado e sentido** vindos do símbolo de giro medido no Blender 5.2 (`Swing Inside` → −Y; `Is Left` → dobradiça em
  x = largura). 🟡

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| — | — | nenhum watch item na tabela principal; nada a verificar |

| Data | Resultado | Observação |
|------|-----------|------------|

## Arquivadas

| ID | Arquivada em | Motivo |
|----|--------------|--------|
