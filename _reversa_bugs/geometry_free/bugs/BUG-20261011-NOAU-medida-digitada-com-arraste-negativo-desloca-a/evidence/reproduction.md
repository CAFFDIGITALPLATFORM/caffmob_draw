# Cápsula de reprodução (lote 31)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: test_canvas2d_view.py, blender_bug_LWF6_move_over.py, blender_bug_LM42_canvas2d.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
test_canvas2d_view.py (exit 1):
FAILED (failures=1)

blender_bug_LWF6_move_over.py (exit 1):
FALHA LWF6: a caixa de A inclui a porta ((-0.30000001192092896, -0.550000011920929, 0.0), (0.30000001192092896, -0.0, 0.7200000286102295)) × ((-0.2999999523162842, -0.550000011920929, 0.0), (0.2999999523162842, 0.029999999329447746, 0.7200000286102295))
FALHA LWF6: a caixa de B inclui a porta ((-0.30000001192092896, -0.550000011920929, 0.0), (0.30000001192092896, -0.0, 0.7200000286102295)) × ((-0.30000001192092896, -0.550000011920929, 0.0), (0.30000001192092896, 0.029999999329447746, 0.7200000286102295))
FALHA LWF6: a sobreposição conta a porta que sai da caixa [] porta até y=0.030
FALHA X5OS: o módulo novo não herda a escala do antigo (1.5, 1.0, 1.0)
FALHA NOAU: largura digitada mantém o canto em X 0.5000
FALHA NOAU: profundidade digitada mantém o canto em Y (limitada a 10 m) 10.000 0.6000
FALHA NOAU: largura fora do limite fica em 10 m e o canto não se afasta 15.0 -14.0000
blender_bug_LWF6_move_over: FALHAS: LWF6: a caixa de A inclui a porta, LWF6: a caixa de B inclui a porta, LWF6: a sobreposição conta a porta que sai da caixa, X5OS: o módulo novo não herda a escala do antigo, NOAU: largura digitada mantém o canto em X, NOAU: profundidade digitada mantém o canto em Y (limitada a 10 m), NOAU: largura fora do limite fica em 10 m e o canto não se afasta

blender_bug_LM42_canvas2d.py (exit 1):
FALHA LM42: a área volta a ser a vista 3D IMAGE_EDITOR
FALHA LM42: com cabeçalho e menus 
blender_bug_LM42_canvas2d: FALHAS: LM42: a área volta a ser a vista 3D, LM42: com cabeçalho e menus
```
