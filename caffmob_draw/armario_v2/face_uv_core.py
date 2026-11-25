"""Núcleo puro do UV por face da chapa do armário v2 (feature 024, T003; RN-03, D-03).

Sem `bpy`: decidir o que é face de fora, de dentro e de fita é geometria, não cena. A caixa chega no referencial da
peça, na mesma unidade da malha (o `build` usa metros), e o par UV sai nessa unidade — 1 unidade de UV = 1 m, como no
layer `UVMap` do resto do pacote (018, RN-08).

- **Eixo fino** é o da espessura. As duas faces grandes (perpendiculares a ele) são a **EXTERNA** (lado +) e a
  **INTERNA** (lado −); as quatro faces estreitas são a **FITA** da borda.
- **U no comprimento, V na largura**: o eixo mais comprido do plano corre em U. Na face INTERNA o U é espelhado dentro
  da própria peça, então o desenho continua no canto certo quando a chapa é virada e o veio não inverte.
- **Fita**: U no comprimento da faixa e V na espessura, o mesmo mapa próprio que `edgeband/build.py` grava.
- A peça espelhada por escala de objeto (`scale.x = -1`) não muda a malha; `espelhado` inverte o V para quem precisar
  do mesmo canto no referencial do armário.
"""

from ..texture_library.uv_core import LAYER_UV

EXTERNA, INTERNA, FITA = 'EXTERNA', 'INTERNA', 'FITA'
TIPOS = (EXTERNA, INTERNA, FITA)


def limites(box):
    """((lo_x, lo_y, lo_z), (hi_x, hi_y, hi_z)) com os lados normalizados (`lo <= hi`)."""
    (x0, y0, z0), (x1, y1, z1) = box
    return (min(x0, x1), min(y0, y1), min(z0, z1)), (max(x0, x1), max(y0, y1), max(z0, z1))


def tamanhos(box):
    """Extensão da caixa nos três eixos."""
    lo, hi = limites(box)
    return tuple(hi[i] - lo[i] for i in range(3))


def eixo_fino(box):
    """Eixo da espessura: o de menor extensão da caixa."""
    medidas = tamanhos(box)
    return min(range(3), key=lambda i: medidas[i])


def eixo_dominante(normal):
    """Eixo da normal da face (o de maior componente)."""
    return max(range(3), key=lambda i: abs(normal[i]))


def tipo_da_face(box, normal):
    """EXTERNA/INTERNA nas duas faces grandes; FITA nas quatro faces estreitas."""
    dominante = eixo_dominante(normal)
    if dominante != eixo_fino(box):
        return FITA
    return EXTERNA if normal[dominante] >= 0.0 else INTERNA


def eixos_uv(box, normal):
    """(eixo U, eixo V) do mapa: o mais comprido do plano em U; na fita o V é a espessura."""
    dominante = eixo_dominante(normal)
    medidas = tamanhos(box)
    plano = [i for i in range(3) if i != dominante]
    if tipo_da_face(box, normal) == FITA:
        return max(plano, key=lambda i: medidas[i]), eixo_fino(box)
    plano.sort(key=lambda i: medidas[i], reverse=True)
    return plano[0], plano[1]


def sinais(tipo, espelhado=False):
    """(sinal U, sinal V): a face INTERNA espelha o U; `espelhado` inverte o V."""
    return (-1.0 if tipo == INTERNA else 1.0), (-1.0 if espelhado else 1.0)


def deslocamento(box, tipo):
    """Avanço em U da face INTERNA: uma espessura, para ela não cair no mesmo retângulo da EXTERNA."""
    return tamanhos(box)[eixo_fino(box)] if tipo == INTERNA else 0.0


def _aplicar(valor, minimo, maximo, sinal):
    return minimo + maximo - valor if sinal < 0 else valor


def uv_metros(box, normal, co, espelhado=False):
    """Par UV (em metros) do vértice `co` na face de normal `normal`."""
    lo, hi = limites(box)
    tipo = tipo_da_face(box, normal)
    eixo_u, eixo_v = eixos_uv(box, normal)
    sinal_u, sinal_v = sinais(tipo, espelhado)
    u = _aplicar(co[eixo_u], lo[eixo_u], hi[eixo_u], sinal_u) + deslocamento(box, tipo)
    v = _aplicar(co[eixo_v], lo[eixo_v], hi[eixo_v], sinal_v)
    return u, v


def retangulo(box, normal, espelhado=False):
    """((U0, V0), (U1, V1)) que a face ocupa no mapa, em metros."""
    lo, hi = limites(box)
    tipo = tipo_da_face(box, normal)
    eixo_u, eixo_v = eixos_uv(box, normal)
    sinal_u, sinal_v = sinais(tipo, espelhado)
    avanco = deslocamento(box, tipo)
    u0 = _aplicar(lo[eixo_u], lo[eixo_u], hi[eixo_u], sinal_u) + avanco
    u1 = _aplicar(hi[eixo_u], lo[eixo_u], hi[eixo_u], sinal_u) + avanco
    v0 = _aplicar(lo[eixo_v], lo[eixo_v], hi[eixo_v], sinal_v)
    v1 = _aplicar(hi[eixo_v], lo[eixo_v], hi[eixo_v], sinal_v)
    return (min(u0, u1), min(v0, v1)), (max(u0, u1), max(v0, v1))
