# Gate 1 · o teste falha antes do change set

Arquivo: `tests/blender_bug_4MF7_colecoes.py` (novo, CHG-001).

Comando:

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_4MF7_colecoes.py
```

Saída (trecho final, exit code 1):

```
Traceback (most recent call last):
  File "tests/blender_bug_4MF7_colecoes.py", line 54, in <module>
    assert arq() is not None, "REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura"
AssertionError: REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura

Error: script failed, file: 'tests/blender_bug_4MF7_colecoes.py', exiting.
EXIT_TEST=1
```

O que fica provado: aplicar o rascunho no OK cria as 4 paredes e nenhuma coleção. A hierarquia
`Arquitetura > Parede` não existe, então as paredes só podem estar na raiz da cena.

Ajuste feito no próprio teste antes da prova final: a primeira execução parou em
`TypeError: bpy_prop_collection.__contains__: expected a string or a tuple of strings`, porque a asserção
"a parede ficou na raiz" comparava objetos em vez de nomes em `scene.collection.objects`. Corrigido para
`o.name in scene.collection.objects`; a execução seguinte falhou na asserção de reprodução, como esperado.
