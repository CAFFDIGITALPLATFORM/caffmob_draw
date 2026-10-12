"""Reprodução e regressão de BUG-20261011-C7IK e BUG-20261011-3UWR (categorias da Biblioteca CAFFMob).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_C7IK_library_panel.py

- `categories.json` inválido vira `categories.json.bak` antes de ser regravado (questions.md, pergunta 58);
- "Pia: Lavabo" é recusada e nenhuma pasta é criada (pergunta 57).
"""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.customize import library_io  # noqa: E402
from caffmob_draw.library_panel import categories  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    root = library_io.modules_root()
    path = os.path.join(root, categories.FILE_NAME)
    os.makedirs(root, exist_ok=True)
    for stale in (path, path + ".bak"):
        if os.path.exists(stale):
            os.remove(stale)
    broken = '{"categories": [{"name": "Varanda", "line": "DOR"}, '
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(broken)
    categories.invalidate()
    reason = categories.create("Lavanderia C7IK", 'DOR')
    check("C7IK: a categoria nova é criada", reason is None, str(reason))
    backup = path + ".bak"
    kept = open(backup, encoding="utf-8").read() if os.path.exists(backup) else None
    check("C7IK: o arquivo inválido fica em categories.json.bak", kept == broken, str(kept))

    reason = categories.create("Pia: Lavabo", 'COZ')
    check("3UWR: 'Pia: Lavabo' é recusada", reason is not None, str(reason))
    check("3UWR: nenhuma pasta criada", not os.path.isdir(os.path.join(root, "Pia: Lavabo"))
          and not os.path.isdir(os.path.join(root, "Pia_ Lavabo")))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_C7IK_library_panel: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
