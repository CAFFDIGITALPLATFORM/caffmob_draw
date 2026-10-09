# Regression watch: 011-selecao-por-componente

> Gerado por `/reversa-coding` em 2026-10-09. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **Seleção por componente** (`selection/component_select.py`): com `Scene.btm_component_select` ligado (padrão), a
  seleção de peças sobe para a raiz do componente (`selection/component.py`, nota D-01). Uma re-extração deve
  descrever a seleção como por componente, com Alt + clique para a peça. 🟢
- **Undo da seleção**: o `view3d.select` grava a etapa de desfazer antes de o handler promover a peça. Ctrl+Z depois
  de um clique pode voltar à seleção da peça, não do componente. Desfazer seleção não muda dado do projeto; risco
  aceito (roadmap §9). 🟡
- **Exclusão em profundidade** (`aggregates/ops_aggregate.delete_components`): X/Delete e "Delete Door/Window" apagam
  a subárvore inteira e o furo; parede, piso e teto continuam no Delete do Blender. Uma re-extração que volte a ver
  "apaga só os filhos diretos" é regressão. 🟢
- **Importação agrupada** (`aggregates/ops_import._group_import`): OBJ/FBX/glTF com várias malhas entram num grupo
  PLAIN; "Montar esquadria" aceita o grupo e o desfaz. 🟢
- **Região na parede** (`openings/region*.py`, `operators/doors_windows.place_in_region`): o vão nasce com a largura
  e a altura exatas da região (porta do piso ao topo, janela com a base como peitoril); região inválida volta ao modo
  de hoje. 🟢
- **Alt + clique** do Blender (lista de objetos sob o cursor) fica sob o da extensão enquanto o interruptor está
  ligado; conflita com "Emular mouse de 3 botões". 🟡
- **Prefixo dos operadores novos**: `caffmob.*`, como exige o `tests/test_identity.py`. O teste continua acusando dois
  operadores `btm.*` anteriores a esta feature (`btm.door_invert_hand`, `btm.resize_width`). 🟢

## Histórico de re-extrações

## Arquivadas
