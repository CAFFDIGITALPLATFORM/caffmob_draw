"""Achar o espaço livre na cena (072 D-20, D-21, D-23): vão do módulo rápido ou caixa livre do armário autoral.

O alvo é um dicionário serializável: `tipo` ('BTM' ou 'AUTHORED'), `raiz` (nome), `caminho` (vão do módulo rápido),
`lo`/`hi` (caixa no referencial da raiz, em m) e as medidas em mm.
"""
import bpy
from mathutils import Vector

from . import espaco_core
from .scene import DRAWER_PROP, PART_PROP


def _alvo(tipo, raiz, caminho, lo, hi, ocupado=False):
    return dict(tipo=tipo, raiz=raiz.name, caminho=caminho, lo=list(lo), hi=list(hi), ocupado=ocupado,
                largura=round((hi[0] - lo[0]) * 1000, 1), profundidade=round((hi[1] - lo[1]) * 1000, 1),
                altura=round((hi[2] - lo[2]) * 1000, 1))


def vaos_do_modulo(context, raiz):
    """Vãos do módulo rápido com as medidas (lista de alvos); o vão 'module' só quando não há subvãos."""
    from ..customize.adapters import btm
    from ..geometry import subspace_fronts
    caixas = btm.space_boxes(context, raiz)
    caminhos = [p for p in caixas if p not in ('module', 's0')] or ['module']    # sem divisões, s0 é o módulo
    ocupados = set(subspace_fronts.specs(raiz))
    return [_alvo('BTM', raiz, p, caixas[p][0], caixas[p][1], p in ocupados) for p in sorted(caminhos)]


def _caixas_do_autoral(raiz):
    inversa = raiz.matrix_world.inverted()
    caixas = []
    for obj in raiz.children_recursive:
        if obj.type != 'MESH' or obj.get(PART_PROP) is not None or obj.get(DRAWER_PROP) is not None:
            continue
        if obj.get('hb_part_role') in ('DRAWER_FRONT', 'DOOR'):
            continue
        cantos = [inversa @ obj.matrix_world @ Vector(c) for c in obj.bound_box]
        caixas.append(espaco_core.Caixa(tuple(min(c[k] for c in cantos) for k in range(3)),
                                        tuple(max(c[k] for c in cantos) for k in range(3))))
    return caixas


def no_ponto(context, obj, ponto, direcao):
    """Alvo do espaço livre no ponto da superfície clicada (recuado 5 mm na direção da câmera), ou None."""
    from ..selection import classify
    raiz, library = classify.module_root(obj) if obj is not None else (None, None)
    if raiz is None:
        return None
    p = raiz.matrix_world.inverted() @ (Vector(ponto) - Vector(direcao).normalized() * 0.005)
    if library == 'BTM':
        candidatos = [a for a in vaos_do_modulo(context, raiz)
                      if all(a['lo'][k] - 1e-4 <= p[k] <= a['hi'][k] + 1e-4 for k in range(3))]
        return min(candidatos, key=lambda a: a['largura'] * a['altura']) if candidatos else None
    if library == 'AUTHORED':
        caixas = _caixas_do_autoral(raiz)
        if not caixas:
            return None
        caixa = espaco_core.livre(caixas, tuple(p), espaco_core.envelope_de(caixas))
        return _alvo('AUTHORED', raiz, '', caixa.lo, caixa.hi) if caixa is not None else None
    return None


def espaco_livre_do_autoral(raiz, ponto_local):
    caixas = _caixas_do_autoral(raiz)
    caixa = espaco_core.livre(caixas, tuple(ponto_local), espaco_core.envelope_de(caixas)) if caixas else None
    return _alvo('AUTHORED', raiz, '', caixa.lo, caixa.hi) if caixa is not None else None


def raiz_do_alvo(alvo):
    return bpy.data.objects.get(alvo['raiz'])
