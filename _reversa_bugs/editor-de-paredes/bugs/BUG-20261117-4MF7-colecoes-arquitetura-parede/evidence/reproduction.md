# Reprodução · BUG-20261117-4MF7 (Arquitetura > Parede)

## Cápsula

| Campo | Valor |
|---|---|
| Commit base | `8caf911e` (master, antes do change set) |
| Branch | `master` |
| Sistema | Windows, Blender 5.2.0 LTS (hash `fbe6228777e7`, build 2026-07-14) |
| Runtime do teste | `--background --factory-startup`, Python 3 do Blender |
| Comando | `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python tests/blender_bug_4MF7_colecoes.py` |
| Exit code (antes) | `1` |
| Exit code (depois) | `0` |
| Taxa | 1 falha em 1 tentativa antes; 1 sucesso em 1 tentativa depois |
| Determinismo | `deterministic` |

## Passos

1. Abrir o Editor de Paredes com a cena vazia.
2. Desenhar uma sala e clicar em OK (`apply_plan`).
3. Olhar o Outliner.

## Resultado antes do change set

`caffmob_draw/hb_types.py:73` linka o objeto novo em `bpy.context.scene.collection.objects`; nenhuma coleção é criada
por `walls2d/`. O teste falha na primeira asserção de reprodução:

```
Traceback (most recent call last):
  File "tests/blender_bug_4MF7_colecoes.py", line 54, in <module>
    assert arq() is not None, "REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura"
AssertionError: REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura
EXIT_TEST=1
```

## Resultado depois do change set

```
blender_bug_4MF7_colecoes: OK
EXIT_TEST=0
```

Observação: a mensagem `CAFFMob Draw: falha inesperada na migração do Padrão de Dimensões`
(`ValueError: The "package" does not name an extension`) é pré-existente em `--background`, não é fatal e não tem
relação com este bug.
