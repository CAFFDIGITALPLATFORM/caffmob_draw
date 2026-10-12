# Cápsula de reprodução (lote 29)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_B5JP_inspection.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_B5JP_inspection.py (exit 1):
OK   B5JP: o arquivo é gravado com as frentes fechadas (0.0, 0.0)
FALHA B5JP: a frente em animação volta no alvo (90°) 0.0
FALHA B5JP: o pendente do gizmo foi gravado (45°) 0.0
FALHA NWRA: o unregister encerra a sessão ativa []
FALHA UURX: o teste de profundidade volta ao anterior NONE
FALHA 6AX3: a mensagem conta só as frentes alteradas ['Janela de informações: 3 frente(s) abertas.']
FALHA B54S: 'Abrir tudo' usa o ângulo de abertura (45°) TypeError('Converting py args to operator properties: enum "OPEN_DEFAULT" not found in (\'CLOSE\', \'OPEN_45\', \'OPEN_90\')')
blender_bug_B5JP_inspection: FALHAS: B5JP: a frente em animação volta no alvo (90°), B5JP: o pendente do gizmo foi gravado (45°), NWRA: o unregister encerra a sessão ativa, UURX: o teste de profundidade volta ao anterior, 6AX3: a mensagem conta só as frentes alteradas, B54S: 'Abrir tudo' usa o ângulo de abertura (45°)
```
