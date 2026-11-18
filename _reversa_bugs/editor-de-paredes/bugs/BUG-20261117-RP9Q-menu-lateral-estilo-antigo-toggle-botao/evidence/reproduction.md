# Reprodução · BUG-20261117-RP9Q (#152)

## Cápsula

| Campo | Valor |
|---|---|
| Commit base | `8caf911e` (master, antes do change set) |
| Branch | `master` |
| Sistema | Windows, Blender 5.2.0 LTS (hash `fbe6228777e7`) |
| Runtime do teste | `--background --factory-startup` |
| Comando | `".../blender.exe" --background --factory-startup --python-exit-code 1 --python tests/blender_bug_RP9Q_paineis.py` |
| Exit code (antes) | `1` |
| Exit code (depois) | `0` |
| Taxa | 1 falha em 1 antes; 1 sucesso em 1 depois |
| Determinismo | `deterministic` |

## Como o defeito aparece

Abrir o Editor de Paredes e olhar o painel Ferramentas. O painel mostra o enum `tool` expandido
(`layout.prop(state, "tool", expand=True)`), com 7 linhas de largura total, sem grade; os booleanos saem como caixa de
marcar. Não existe botão de ferramenta com estado.

## Prova antes do change set

```
Traceback (most recent call last):
  File "tests/blender_bug_RP9Q_paineis.py", line 82, in <module>
    assert len(botoes(r)) == len(FERRAMENTAS), \
AssertionError: REPRODUÇÃO (#152): painel sem botões de ferramenta (0)
EXIT_TEST=1
```

Depois do change set:

```
blender_bug_RP9Q_paineis: OK
EXIT_TEST=0
```

Observação: a mensagem `ValueError: The "package" does not name an extension`, do padrão de dimensões, é
pré-existente em `--background` e não tem relação com este bug.
