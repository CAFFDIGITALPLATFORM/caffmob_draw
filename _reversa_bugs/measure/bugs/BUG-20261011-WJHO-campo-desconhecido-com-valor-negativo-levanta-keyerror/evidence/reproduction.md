# Cápsula de reprodução (lote 18: cotas de módulo)

- Commit base: 83a6863 + lotes 1 a 17 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Python 3 (teste puro) e Blender 5.2.0 LTS, `--background --factory-startup`
- Comandos: `python3 -m unittest test_cotas` (em tests/) e
  `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_NBKB_measure.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
test_cotas: FAILED (failures=1, errors=1)   # posterior 2,0 e inferior 3,0 aceitos; KeyError no campo desconhecido negativo
FALHA NBKB: cota anterior mede até a lateral do módulo rápido anterior=1.5000 esperado=0.7000
FALHA 4ZPJ: o getter da cota não quebra com a parede sem Length ValueError('Object does not have geometry node modifier')
```
