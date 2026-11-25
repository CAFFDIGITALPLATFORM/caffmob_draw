"""Textura padrão da chapa no material do armário v2 (feature 024, T005; RN-01, D-01).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_024_textura.py

- o material da chapa nasce com nó `TEX_IMAGE` apontando para a imagem empacotada de 512²;
- vidro e alumínio continuam sem textura;
- a peça com material do usuário continua vencendo o acabamento do spec;
- aplicar de novo não duplica nó nem imagem.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401  (registra o add-on inteiro)
from caffmob_draw.armario_v2 import build, textura_padrao  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    mapa = build.materiais('MADEIRADO')
    chapa = mapa['CHAPA']
    no = chapa.node_tree.nodes.get(textura_padrao.NOME_NO)
    check("material da chapa tem nó de imagem", no is not None)
    check("imagem empacotada", bool(no is not None and no.image is not None and no.image.packed_file))
    check("imagem 512x512", bool(no is not None and tuple(no.image.size) == (512, 512)),
          str(tuple(no.image.size)) if no is not None and no.image is not None else "")
    check("mapeamento em 1/tamanho", any(
        abs(no_mapa.inputs['Scale'].default_value[0] - 1.0 / textura_padrao.TAMANHO_M) < 1e-6
        for no_mapa in chapa.node_tree.nodes if no_mapa.type == 'MAPPING'))
    for chave in ('VIDRO', 'ALUMINIO'):
        check(f"{chave} sem textura", mapa[chave].node_tree.nodes.get(textura_padrao.NOME_NO) is None)
    usuario = bpy.data.materials.new("Material do usuário 024")
    material, _rotulo = build._material_da_peca({'material': 'CHAPA'}, mapa, usuario.name)
    check("material do usuário vence", material is usuario)
    textura_padrao.aplicar(chapa)
    check("sem nó duplicado", len([no_ for no_ in chapa.node_tree.nodes if no_.type == 'TEX_IMAGE']) == 1)
    check("uma imagem só no arquivo", len([img for img in bpy.data.images
                                           if img.name.startswith(textura_padrao.NOME_IMAGEM)]) == 1)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
