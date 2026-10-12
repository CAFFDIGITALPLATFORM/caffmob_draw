# Cápsula de reprodução (lote 23)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_XPD2_stick.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_XPD2_stick.py (exit 1):
FALHA XPD2: trocar o pai à mão desfaz o vínculo 
FALHA XF4S: hospedeiro renomeado continua achando o item []
FALHA XF4S: apagar o hospedeiro desfaz o vínculo 
FALHA 73SM: desgrudado da parede não é regrudado na carga 
FALHA EE4E: o painel Grudar não aparece para parede 
FALHA I3I3: depois de giro livre o item volta a encostar na face (0.866, -0.0, -0.5)
FALHA TNY3: erro no assentar vai para o log, sem derrubar o temporizador RuntimeError('falha simulada no assentar')
blender_bug_XPD2_stick: FALHAS: XPD2: trocar o pai à mão desfaz o vínculo, XF4S: hospedeiro renomeado continua achando o item, XF4S: apagar o hospedeiro desfaz o vínculo, 73SM: desgrudado da parede não é regrudado na carga, EE4E: o painel Grudar não aparece para parede, I3I3: depois de giro livre o item volta a encostar na face, TNY3: erro no assentar vai para o log, sem derrubar o temporizador
```
