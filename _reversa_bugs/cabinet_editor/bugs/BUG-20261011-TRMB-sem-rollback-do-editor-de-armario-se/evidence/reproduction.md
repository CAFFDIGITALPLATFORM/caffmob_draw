# Análise (lote 12): sem defeito

- `rollback` reaplica o instantâneo inicial **na raiz** (`bridge.apply_state(context, root, initial)`); sem a raiz não há
  onde reaplicar.
- Tudo o que o editor cria é filho da raiz: `scene_parts._link` (`obj.parent = root`), `scene_divisions`
  (`obj.parent = root`) e `scene_slides` (grupo FRAME das peças da raiz). Apagar a raiz leva tudo junto: não sobra
  nada a desfazer.
- A revisão de 2026-10-10 corrigiu a RN-06 para descrever exatamente isso ("raiz apagada encerra com WARNING e
  CANCELLED, sem rollback"; `.reversa/context/review-2026-10/cabinet_editor.json`, text_corrections).
