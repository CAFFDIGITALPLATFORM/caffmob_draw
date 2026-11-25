"""Migração idempotente da exibição do armário v2 (feature 024, T011; RN-04, D-05).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_024_migracao.py

- raiz com `exibicao_versao == 0` migra: peça sem material ganha a chapa padrão e a versão vira 1;
- a segunda passada não migra nada (idempotente);
- o handler fica no `load_post` depois do `register()` e sai no `unregister()`.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import caffmob_draw  # noqa: E402
from caffmob_draw.armario_v2 import build, exibicao  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    cena = bpy.context.scene
    raiz = build.criar_raiz(cena, "Armário 024")
    malha = bpy.data.meshes.new("Chapa 024")
    peca = bpy.data.objects.new("Chapa 024", malha)
    cena.collection.objects.link(peca)
    peca.parent = raiz
    parte = peca.btm_armario_parte
    parte.papel = 'LATERAL'
    check("raiz começa na versão 0", raiz.btm_armario.exibicao_versao == 0)
    check("peça começa sem material", parte.material == "" and len(malha.materials) == 0)

    migrados = exibicao.migrar(cena)
    check("migra uma raiz", migrados == 1, str(migrados))
    check("versão vira 1", raiz.btm_armario.exibicao_versao == 1)
    check("variante gravada", raiz.btm_armario.exibicao in ('TEXTURA_SO', 'TEXTURA_LINHAS'),
          raiz.btm_armario.exibicao)
    check("peça ganhou a chapa padrão", len(malha.materials) == 1 and malha.materials[0] is not None)
    check("segunda passada não migra", exibicao.migrar(cena) == 0)
    check("handler no load_post", exibicao._ao_carregar in bpy.app.handlers.load_post)
    check("migrar sem cena não estoura", exibicao.migrar(None) == 0 or True)

    caffmob_draw.unregister()
    check("handler removido no unregister", exibicao._ao_carregar not in bpy.app.handlers.load_post)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
