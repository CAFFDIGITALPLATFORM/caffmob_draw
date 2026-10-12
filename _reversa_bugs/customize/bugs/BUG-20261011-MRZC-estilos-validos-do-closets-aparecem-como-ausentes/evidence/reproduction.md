# Cápsula de reprodução (lote 4: library_io)

- Commit base: 83a6863 + lotes 1 a 3 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_J2NY_library_io.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA J2NY: .blend sem .json entra sem exceção UnboundLocalError("cannot access local variable 'missing' ...")
FALHA J2NY: Inserir módulo aceita o grupo antigo RuntimeError(... UnboundLocalError ...)
FALHA MRZC: estilo válido do closets não é ausente; inválido é ['WIDE_SHAKER', 'XYZ']
FALHA MRZC: inserir o roupeiro não acusa estilo ausente ['Estilos ausentes neste arquivo (mantida a geometria salva): WIDE_SHAKER']
FALHA OJBL: .blend e .json continuam o par anterior (3052c5a2…, df8623e8…) → (1bf0a1fd…, df8623e8…)
```
