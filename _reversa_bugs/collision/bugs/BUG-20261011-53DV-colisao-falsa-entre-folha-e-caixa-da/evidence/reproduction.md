# Cápsula de reprodução (lote 21)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_NQ2L_aggregates.py, blender_003_aggregates_smoke.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_NQ2L_aggregates.py (exit 1):
FALHA NQ2L: desconverter depois de mover o pai fica onde está (1.0, 7.450580596923828e-09, 0.6000000238418579) → (0.0, 0.0, 0.6000000238418579)
FALHA VPY5: sem módulo, só o pai sai da colisão ['Item', 'Outro filho', 'Painel']
FALHA I7QE: trocar o sentido com a folha aberta reabre pela varredura (para no obstáculo) abertura=1.00 contato=''
FALHA PON4: caixa de pai Empty é a das malhas [0.0, 0.0, 0.0]
FALHA 4OV4: esquadria sem peças é recusada com mensagem None
FALHA MQPR: o ícone do pivô segue o movimento PLAIN_AXES
FALHA 5DDZ: parede não HB recebe o aviso de converter parede=None motivo='Selecione também a parede'
FALHA 53DV: folha aberta não colide com a própria caixa nem com a parede dela [('WALL', 'Door - folha 1', 'Wall'), ('ITEM', 'Door', 'Door - folha 1')]
blender_bug_NQ2L_aggregates: FALHAS: NQ2L: desconverter depois de mover o pai fica onde está, VPY5: sem módulo, só o pai sai da colisão, I7QE: trocar o sentido com a folha aberta reabre pela varredura (para no obstáculo), PON4: caixa de pai Empty é a das malhas, 4OV4: esquadria sem peças é recusada com mensagem, MQPR: o ícone do pivô segue o movimento, 5DDZ: parede não HB recebe o aviso de converter, 53DV: folha aberta não colide com a própria caixa nem com a parede dela

blender_003_aggregates_smoke.py (exit 1):
Traceback (most recent call last):
```
