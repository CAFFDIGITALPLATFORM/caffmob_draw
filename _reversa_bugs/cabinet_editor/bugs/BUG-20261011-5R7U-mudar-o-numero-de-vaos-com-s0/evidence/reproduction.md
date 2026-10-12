# Cápsula de reprodução (lote 24)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_5R7U_cabinet_editor.py, test_cabinet_appliances.py, test_cabinet_catalog.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_5R7U_cabinet_editor.py (exit 1):
FALHA 5R7U: Número de vãos com s0 cortado por divisória comum é recusado aceitou (2 vãos)
FALHA FHQN: deslizantes em armário com vãos são recusados ['Folha 1 não corre: esbarra em Divisória 1', 'Folha 2 não corre: esbarra em Divisória 1']
FALHA HF2J: 'Tras 15mm' aplica 15 mm de recuo atrás {'use_back': False, 'back': 0.019999999552965164}
FALHA HR3U: item de Internos não serve na aba Deslizantes None
FALHA HLV6: apply_state sem mudança não recria internos nem deslizantes 8 objeto(s) recriado(s)
FALHA FYXD: 'Sem Divisória' não tira uma divisória de vão sem aviso []
blender_bug_5R7U_cabinet_editor: FALHAS: 5R7U: Número de vãos com s0 cortado por divisória comum é recusado, FHQN: deslizantes em armário com vãos são recusados, HF2J: 'Tras 15mm' aplica 15 mm de recuo atrás, HR3U: item de Internos não serve na aba Deslizantes, HLV6: apply_state sem mudança não recria internos nem deslizantes, FYXD: 'Sem Divisória' não tira uma divisória de vão sem aviso

test_cabinet_appliances.py (exit 1):
FAILED (failures=2)

test_cabinet_catalog.py (exit 1):
FAILED (failures=1)
```
