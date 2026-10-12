# Cápsula de reprodução (lote 6: porta real)

- Commit base: 83a6863 + lotes 1 a 5 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_MMVI_opening_sync.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA MMVI: refazer a porta mantém o objeto do usuário
FALHA A2Z4: Atualizar segue com uma caixa com erro RuntimeError(... caixa com defeito simulado ...)
FALHA A2Z4: o OK do Editor de Paredes segue e lista a caixa com erro RuntimeError('caixa com defeito simulado')
FALHA IDPP: a caixa ganha marco e folga
FALHA IDPP: a porta real foi refeita
FALHA UV6S: Toggle Double Door refaz como dupla DOOR, 1 folha(s)
FALHA SX4T: o símbolo de giro é o Door Swing, não a cota A cota
```
