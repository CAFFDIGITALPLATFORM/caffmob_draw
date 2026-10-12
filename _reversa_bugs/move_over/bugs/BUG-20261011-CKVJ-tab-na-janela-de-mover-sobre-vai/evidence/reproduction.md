# Cápsula de reprodução (lote 16: janela Mover Sobre)

- Commit base: 83a6863 + lotes 1 a 15 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup` (modal exercitado com objeto falso)
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_CKVJ_move_over_dialog.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA CKVJ: Tab com valor válido grava e vai ao próximo campo campo=0
FALHA CKVJ: Tab com valor inválido fica no campo com o aviso campo=2 texto='abc'
FALHA JMDR: seta depois do aviso zera o aviso warned=True
FALHA CNTL: rotação inválida mostra mensagem traduzida "could not convert string to float: '1.2.3'"
```
