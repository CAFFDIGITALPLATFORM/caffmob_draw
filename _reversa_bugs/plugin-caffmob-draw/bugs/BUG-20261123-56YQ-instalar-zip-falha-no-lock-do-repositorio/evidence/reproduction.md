# Evidência, BUG-20261123-56YQ

## 1. Traceback enviado pelo usuário

Blender 5.2 no Windows, arrastando `caffmob_draw.zip` para a janela:

```
Relatório: Erro

Python: Traceback (most recent call last):
  File "C:\Program Files\Blender Foundation\Blender 5.2\5.2\scripts\addons_core\bl_pkg\bl_extension_ops.py", line 1504, in execute
    cmd_batch = self.exec_command_iter(is_modal)
  File "C:\Program Files\Blender Foundation\Blender 5.2\5.2\scripts\addons_core\bl_pkg\bl_extension_ops.py", line 2627, in exec_command_iter
    if lock_result_any_failed_with_report(self, self.repo_lock.acquire()):
                                            ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\Blender Foundation\Blender 5.2\5.2\scripts\addons_core\bl_pkg\bl_extension_utils.py", line 2245, in acquire
    raise Exception("acquire(): cookie doesn't exist! (when it should)")
Exception: acquire(): cookie doesn't exist! (when it should)
```

Print: `evidence/erro-instalar-cookie-lock-20261123.webp`.

## 2. Conferência da fonte do Blender (tag v5.2.0)

As três linhas do traceback batem com a tag `v5.2.0`:

| Arquivo | Linha | Trecho |
|---|---|---|
| `bl_extension_ops.py` | 1504 | `cmd_batch = self.exec_command_iter(is_modal)` |
| `bl_extension_ops.py` | 2627 | `if lock_result_any_failed_with_report(self, self.repo_lock.acquire()):` |
| `bl_extension_utils.py` | 2245 | `raise Exception("acquire(): cookie doesn't exist! (when it should)")` |

Cadeia lida na fonte:

1. `bl_pkg/__init__.py:103`, `cookie_from_session()` devolve `bpy.app.tempdir` ("This path is a unique string for this session").
2. `RepoLock.__init__` guarda esse caminho como `_cookie`; a docstring diz que o cookie "must point to a path that exists".
3. `RepoLock.acquire()` (linhas 2242 a 2245) faz `if not os.path.exists(self._cookie): raise Exception(...)`.

Conclusão de leitura: a exceção não fala do zip nem do manifesto. Ela só significa que `bpy.app.tempdir` não existe no instante do clique.

Fontes:
- `https://raw.githubusercontent.com/blender/blender/v5.2.0/scripts/addons_core/bl_pkg/__init__.py`
- `https://raw.githubusercontent.com/blender/blender/v5.2.0/scripts/addons_core/bl_pkg/bl_extension_utils.py`
- `https://raw.githubusercontent.com/blender/blender/v5.2.0/scripts/addons_core/bl_pkg/bl_extension_ops.py`

## 3. Ocorrências iguais em outros add-ons

- QRemeshify, issue #49 (Blender 5.2, linhas 1504, 2627 e 2245, as mesmas): `https://github.com/ksami/QRemeshify/issues/49`
- BlenderKit, issue #1744 (4.4): `https://github.com/BlenderKit/blenderkit/issues/1744`
- Blender Stack Exchange 337385 (4.5, resolvido rodando como administrador): `https://blender.stackexchange.com/questions/337385/`
- QRemeshify discussion #26 (4.4.3) e GMIC Node Editor (4.5): mesmo traceback.

O padrão nos relatos: o zip raramente importa, a falha acontece antes de ler o pacote, e reiniciar o Blender ou mudar a pasta temporária resolve.

## 4. Verificação do pacote neste turno (leitura, sem Blender na máquina)

| Item | Resultado |
|---|---|
| `blender_manifest.toml` na raiz do zip | presente |
| `__init__.py` na raiz do zip | presente |
| `version` | `1.26.0` |
| `blender_version_min` | `5.2.0` |
| wheels | 12, todas `cp313` ou `py3-none-any` (Blender 5.2 usa Python 3.13) |
| arquivos / tamanho | 2367 / 167,8 MB |
| `build.py` | exit 0, `Successfully created 'caffmob_draw.zip'!` |
| achado lateral | `.impeccable/hook.cache.json` dentro do zip (não bloqueia instalação) |

## 5. Pendente para o fix

- Confirmar `bpy.app.tempdir` no Blender do titular e se a pasta existe (Python Console: `import bpy; print(bpy.app.tempdir, os.path.exists(bpy.app.tempdir))`).
- Repetir a instalação logo depois de reiniciar o Blender.
- Registrar se o erro aparece também em `Preferences, Get Extensions, Install from Disk` (mesmo caminho de código) e na linha de comando (`blender --command extension install-file -r user_default caffmob_draw.zip`).
