"""UV por face da chapa e UV próprio da fita (feature 024, T006/T007; RN-03, D-03).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_024_uv.py

- a chapa tem layer `UVMap` e as faces externa/interna não compartilham o mesmo retângulo;
- as quatro faces estreitas são fita e ficam no mapa delas;
- a faixa da fita tem `UVMap` com U no comprimento e V na espessura, em metros.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.armario_v2 import build, face_uv_core  # noqa: E402
from caffmob_draw.edgeband import build as band_build  # noqa: E402
from caffmob_draw.edgeband import core as band_core  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def _retangulos(malha, camada, caixa):
    """{(tipo, eixo dominante, sinal): (Umin, Umax, Vmin, Vmax)} por face da caixa."""
    saida = {}
    for poligono in malha.polygons:
        us = [camada.data[i].uv[0] for i in poligono.loop_indices]
        vs = [camada.data[i].uv[1] for i in poligono.loop_indices]
        tipo = face_uv_core.tipo_da_face(caixa, poligono.normal)
        eixo = face_uv_core.eixo_dominante(poligono.normal)
        sinal = 1 if poligono.normal[eixo] >= 0 else -1
        saida[(tipo, eixo, sinal)] = (min(us), max(us), min(vs), max(vs))
    return saida


def main():
    malha = build._malha("Chapa 024", ((0.0, 0.0, 0.0), (600.0, 18.0, 720.0)))
    camada = malha.uv_layers.get(face_uv_core.LAYER_UV)
    check("chapa tem layer UVMap", camada is not None)
    caixa = face_uv_core.limites(
        (tuple(min(v.co[i] for v in malha.vertices) for i in range(3)),
         tuple(max(v.co[i] for v in malha.vertices) for i in range(3))))
    faces = _retangulos(malha, camada, caixa)
    fora = [r for (tipo, _e, _s), r in faces.items() if tipo == face_uv_core.EXTERNA]
    dentro = [r for (tipo, _e, _s), r in faces.items() if tipo == face_uv_core.INTERNA]
    fita = [r for (tipo, _e, _s), r in faces.items() if tipo == face_uv_core.FITA]
    check("uma face externa e uma interna", (len(fora), len(dentro)) == (1, 1), f"{len(fora)}/{len(dentro)}")
    check("quatro faces de fita", len(fita) == 4, str(len(fita)))
    check("externa e interna com retângulos distintos", bool(fora and dentro and fora[0] != dentro[0]),
          f"{fora} x {dentro}")
    check("externa cobre o comprimento", bool(fora) and abs((fora[0][1] - fora[0][0]) - 0.72) < 1e-4,
          str(fora))

    dono = bpy.data.objects.new("Dono 024", bpy.data.meshes.new("Dono 024"))
    bpy.context.scene.collection.objects.link(dono)
    banda = band_core.Band(('peca|x+',), 0, 1, 0.018, ((0.0, 0.6), (0.0, 0.72)))
    faixa = band_build.create(dono, banda, 0.001)
    uv = faixa.data.uv_layers.get(face_uv_core.LAYER_UV)
    check("faixa tem layer UVMap", uv is not None)
    if uv is not None:
        us = [dado.uv[0] for dado in uv.data]
        vs = [dado.uv[1] for dado in uv.data]
        comprimento = max(rect[1] - rect[0] for rect in banda.rect)
        check("U = comprimento da faixa", abs((max(us) - min(us)) - comprimento) < 1e-4,
              f"{max(us) - min(us):.4f} x {comprimento:.4f}")
        check("V = espessura da fita", abs((max(vs) - min(vs)) - 0.001) < 1e-4, f"{max(vs) - min(vs):.6f}")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
