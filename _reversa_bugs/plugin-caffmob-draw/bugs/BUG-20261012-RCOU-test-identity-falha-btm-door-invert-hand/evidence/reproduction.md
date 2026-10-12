# Cápsula de reprodução (lote 35)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: test_identity.py, blender_toast_resize_invert.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
test_identity.py (exit 1):
FAILED (failures=1)

blender_toast_resize_invert.py (exit 1):
OK   aviso: clique na folha mede a porta ('Door', 0.8, 2.1, 0.15000000596046448)
OK   aviso: texto Porta Door   L 800 mm × A 2100 mm × P 150 mm
OK   aviso: módulo tem largura 0.9143999814987183
OK   aviso: grupo de peças mede as malhas (1.200000286102295, 0.039999961853027344, 0.6000000238418579)
OK   aviso: cota não tem aviso 
FALHA I: atalho registrado no Object Mode 
Traceback (most recent call last):
```
