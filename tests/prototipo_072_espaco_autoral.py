"""Protótipo da 072 (T050; D-23): espaço livre e gavetas no armário autoral (066), que não tem vãos do addon.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/prototipo_072_espaco_autoral.py

Monta um armário autoral de chapas (laterais, base, tampo, fundo e duas prateleiras), acha a caixa livre entre as
prateleiras pelo `espaco_core` e insere 2 gavetas com telescópica soft. Sai com 0 se verde.
"""
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
from caffmob_draw import mechanisms  # noqa: E402
from caffmob_draw.aggregates import ops_authored  # noqa: E402
from caffmob_draw.drawers import core, espaco, inserir, scene  # noqa: E402

FALHAS = []


def check(ok, texto, detalhe=''):
    print(('OK   ' if ok else 'FALHA ') + texto + (f' ({detalhe})' if detalhe and not ok else ''), flush=True)
    if not ok:
        FALHAS.append(texto)


def armario():
    env.clean_scene()
    raiz = bpy.data.objects.new('Armário', None)
    bpy.context.collection.objects.link(raiz)
    t = 0.018
    pecas = [('Lateral E', (t, .56, 2.0), (t / 2, .28, 1.0)), ('Lateral D', (t, .56, 2.0), (.6 - t / 2, .28, 1.0)),
             ('Base', (.6 - 2 * t, .554, t), (.3, .277, t / 2)), ('Tampo', (.6 - 2 * t, .554, t), (.3, .277, 2 - t / 2)),
             ('Fundo', (.6 - 2 * t, .006, 2.0), (.3, .557, 1.0)),
             ('Prateleira 1', (.6 - 2 * t, .54, t), (.3, .27, .7 + t / 2)),
             ('Prateleira 2', (.6 - 2 * t, .54, t), (.3, .27, 1.4 + t / 2))]
    objs = [authored_env.cube(n, s, l, raiz) for n, s, l in pecas]
    env.settle()
    ops_authored.adopt(raiz, [raiz] + objs, 'NEG_Y')
    return raiz


try:
    raiz = armario()
    alvo = espaco.espaco_livre_do_autoral(raiz, (0.3, 0.2, 1.0))
    check(alvo is not None and (alvo['largura'], alvo['altura'], alvo['profundidade']) == (564.0, 682.0, 554.0),
          'caixa livre entre as prateleiras: 564 × 682 × 554 mm', str(alvo and (alvo['largura'], alvo['altura'],
                                                                              alvo['profundidade'])))
    motivos = inserir.inserir(bpy.context, alvo, 2, core.Gaveta(corredica='telescopica_soft'))
    check(motivos == [], '2 gavetas entram no armário autoral', str(motivos))
    frentes = [o for o in raiz.children_recursive if scene.is_drawer(o)]
    check(len(frentes) == 2, 'duas frentes do construtor', len(frentes))
    if frentes:
        check(mechanisms.of(frentes[0]) is not None and mechanisms.of(frentes[0]).kind == mechanisms.DRAWER,
              'a gaveta do armário autoral corre (mecanismo DRAWER)')
        contra = next(c for c in frentes[0].children if 'contra_frente' in (c.get(scene.PART_PROP) or ''))
        check(round(contra.dimensions.x * 1000, 1) == 564 - 26 - 30, 'contra-frente = 564 − 26 − 30',
              round(contra.dimensions.x * 1000, 1))
except Exception:
    traceback.print_exc()
    FALHAS.append('exceção')
print('RESULTADO', 'VERDE' if not FALHAS else 'VERMELHO', flush=True)
sys.exit(1 if FALHAS else 0)
