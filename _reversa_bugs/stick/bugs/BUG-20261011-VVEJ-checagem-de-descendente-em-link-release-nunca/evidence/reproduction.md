# Cápsula de reprodução (lote 2: checagem de descendência)

- Commit base: 83a6863 + lote 1 aplicado (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`), `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python evidence/probe_lote2.py`
- Exit code: 0 · Taxa: 1/1 · Classificação: deterministic

## Saída

```
can_convert(peca filha da caixa, caixa): 'O pai não pode ser o próprio objeto nem um filho dele'
can_convert(obj, pai=filho do obj): None
Blender aceita ciclo A<->B: False
release: item.parent = None | desc.parent = Item | ciclo: False
release: item world = (0.0, 0.0, -1.0) (era (2, 0, 0))
convert(obj, filho): POS_X | obj.parent = None | is_aggregate = True | parent_ref = Filho
```

## Leitura

- O Blender 5.2 recusa em silêncio a atribuição de pai que fecharia um ciclo (A↔B): o ciclo em si não se forma.
- `can_convert` recusa a peça que já é filha do pai (caso legítimo) e aceita o pai descendente do objeto; `convert`
  então grava o agregado (`is_aggregate`, `parent_ref`) com a atribuição de pai ignorada: agregado inconsistente.
- `link.release` com `orig_parent` descendente do item: a checagem compara string com objetos e sempre passa; a
  atribuição de pai é ignorada, mas `matrix_basis` é calculada no espaço do descendente e o item salta de lugar.
