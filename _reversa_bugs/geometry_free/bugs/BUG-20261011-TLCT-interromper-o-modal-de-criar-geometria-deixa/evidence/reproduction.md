# Cápsula de reprodução (lote 9: modais interrompidos)

- Commit base: 83a6863 + lotes 1 a 8 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS com janela (xvfb-run), `--factory-startup --enable-event-simulate`
- Comando: `xvfb-run -a /opt/blender/blender --factory-startup --enable-event-simulate --python tests/blender_bug_TLCT_modal_cancel.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic
- Gatilho: o modal é aberto numa janela nova e a janela é fechada (o Blender chama `cancel()`)

```
FALHA TLCT: interrompido, não fica peça provisória ['Placa']
FALHA JDYP: interrompido, não ficam objetos carregados ['Planta', 'Vaso', 'Vaso com planta']
FALHA 3T7M: Mover na Parede interrompido devolve o módulo poll=True (1.7, 0.0, 0.0)
```
