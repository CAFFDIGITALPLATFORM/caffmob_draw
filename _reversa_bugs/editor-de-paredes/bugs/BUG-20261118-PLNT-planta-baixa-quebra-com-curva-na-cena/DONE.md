# Bug Encerrado — BUG-20261118-PLNT

- **Data:** 2026-11-18
- **Resolution kind:** fixed
- **Closure policy:** local-software (regressão passando + veredito de spec)
- **Spec verdict:** spec-desatualizada (adendo em `_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md`)
- **Causa raiz:** `plant_objects` aceitava `CURVE` e `FONT` no filtro mas lia `obj.data.vertices` de todo objeto, e o `AttributeError` subia pelo `draw_plan`. Estado epistemológico: `confirmed`.

Este bug está encerrado. Nenhum agente deve modificar esta pasta.
Reabertura: remova este arquivo conscientemente ou registre um bug novo com `regression-of` apontando para BUG-20261118-PLNT.
