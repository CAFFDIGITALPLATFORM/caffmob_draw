# Cápsula de reprodução (lote 13: padrões dimensionais)

- Commit base: 83a6863 + lotes 1 a 12 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_KVDM_standards.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA KVDM: a Montagem volta do .btmdim.json LATERAL
FALHA ZK42: nan é recusado
FALHA ZK42: 'nan' é recusado
FALHA 3HN6: lines lista é recusado com mensagem erro Python AttributeError
FALHA 3HN6: edges inteiro é recusado com mensagem erro Python TypeError
FALHA 3HN6: schema_version booleano é recusado com mensagem aceito
FALHA 3HN6: Importar Definição recusa sem erro Python (traceback AttributeError)
FALHA EKM7: -1 mostra a faixa e o valor recebido Valor Inválido: Espessura da Chapa não aceita valor negativo.
FALHA EKM7: 'abc' mostra a faixa e o valor recebido Valor Inválido: Espessura da Chapa precisa ser numérico (recebido: abc).
```
