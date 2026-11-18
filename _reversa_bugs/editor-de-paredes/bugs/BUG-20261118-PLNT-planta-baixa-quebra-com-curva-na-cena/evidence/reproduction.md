# Reprodução — BUG-20261118-PLNT

- **Ambiente:** Windows, Blender 5.2.0 LTS (`--background` e a sessão aberta do titular), addon `caffmob_draw` 1.25.0 na
  cópia instalada (`extensions/mobi_caff_digital/caffmob_draw`).
- **Base:** árvore de trabalho, sem commit (as mudanças do Reversa seguem não commitadas).
- **Comando:** execução via servidor MCP do Blender (`127.0.0.1:9877`, `execute`) lendo a cena aberta:

```python
scene_io.plant_objects(bpy.context.scene, 3.0)
```

- **Cena:** 1681 objetos — 1373 `MESH`, 163 `EMPTY`, 114 `CURVE`, 18 `LIGHT`, 10 `CAMERA`, 3 `FONT`.
- **Taxa:** 2/2 tentativas com falha antes do fix; 1/1 com sucesso depois.
- **Classificação:** determinística — o primeiro objeto que não é malha derruba a leitura.

## Vermelho (antes do fix)

```
Traceback (most recent call last):
  File "...\extensions\mobi_caff_digital\caffmob_draw\walls2d\scene_io.py", line 156, in plant_objects
    base_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices) if obj.data.vertices else 0.0
AttributeError: 'Curve' object has no attribute 'vertices'
```

A exceção sai de `draw_plan`/`desenhar` sem proteção, dentro do handler de desenho: com `plant_low` ligado o editor
inteiro deixa de desenhar.

## Verde (depois do fix)

Blender do titular, addon recarregado (1.25.0):

```
objetos da cena: 1681 {'MESH': 1373, 'EMPTY': 163, 'CURVE': 114, 'LIGHT': 18, 'CAMERA': 10, 'FONT': 3}
plant_objects OK: 1319
```

Teste do repositório:

```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_JXDJ_plant_baixa.py
...
OK   REGRESSÃO: planta lê a cena com curva, vazio e objeto acima do corte
OK   REGRESSÃO: malha abaixo do corte entra na planta nomes=['Caixa']
OK   REGRESSÃO: objeto acima do corte fica fora da planta nomes=['Caixa']
OK   REGRESSÃO: malha da planta tem contorno e cor pontos=8
blender_bug_JXDJ_plant_baixa: OK
EXIT=0
```

## Nota sobre o teste herdado

O teste do JXDJ (fechado, pasta travada) verificava só a existência de `plant_low`, `cut_height` e
`material_color_mode`; nunca chamava `plant_objects`. Por isso passou verde com o defeito presente. A checagem nova
encosta no caminho de leitura da cena, que é onde o defeito vive.
