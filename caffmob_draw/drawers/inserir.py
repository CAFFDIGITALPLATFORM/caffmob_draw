"""Inserir gavetas num alvo (072 RF-03, D-20 a D-23): vão do módulo rápido ou espaço livre do armário autoral.

No módulo rápido, as gavetas vão pelo `btm.set_front` (o pedido do vão guarda o spec e o rebuild do módulo as
refaz). No armário autoral, que não se reconstrói, a frente entra embutida no espaço livre, com a caixa do núcleo e a
folha `DRAWER`; a frente é a raiz da gaveta, como no módulo rápido.
"""
from . import build, catalogo, core
from .espaco import raiz_do_alvo

MARGEM = 0.002


def _no_modulo(context, raiz, alvo, n, gaveta):
    from ..customize.adapters import btm
    from ..geometry import subspace_fronts
    caminho = alvo['caminho']
    abertura = raiz if caminho == 'module' else subspace_fronts.holder(raiz, caminho)
    return btm.set_front(context, raiz, abertura, 'DRAWERS', n, gaveta.para_dict())


def _no_autoral(raiz, alvo, n, gaveta):
    from ..aggregates import leaf
    from ..geometry import subspace_fronts
    lo, hi = alvo['lo'], alvo['hi']
    tf = gaveta.frente_espessura / 1000
    largura, altura = hi[0] - lo[0], hi[2] - lo[2]
    profundidade = (hi[1] - lo[1]) * 1000 - gaveta.frente_espessura
    corredica = catalogo.por_id(gaveta.corredica, build.pasta_do_usuario())
    alturas = core.dividir_altura((altura - 2 * MARGEM) * 1000, n, MARGEM * 1000)
    espaco = core.Espaco(largura * 1000, alturas[0], profundidade)
    motivos = core.motivos(espaco, gaveta, corredica, alturas[0])
    if motivos:
        return motivos
    z = lo[2] + MARGEM
    for i, h in enumerate(alturas):
        frente = subspace_fronts._panel(raiz, f"{raiz.name} gaveta {i + 1}", largura - 2 * MARGEM, h / 1000, tf,
                                        (lo[0] + MARGEM, lo[1], z), 'autoral', 'DRAWER_FRONT')
        frente['btm_drawer_index'] = i
        caixa = build.aplicar(frente, core.Espaco(largura * 1000, h, profundidade), gaveta, h, MARGEM * 1000,
                              gaveta.frente_espessura)
        import bpy
        bpy.context.view_layer.update()
        leaf.make_leaf(frente, raiz, motion='DRAWER', travel=caixa.comprimento / 1000)
        z += h / 1000 + MARGEM
    return []


def inserir(context, alvo, n, gaveta):
    """Insere N gavetas no alvo; devolve os motivos da recusa (lista vazia se entrou)."""
    raiz = raiz_do_alvo(alvo)
    if raiz is None:
        return ["O móvel do espaço escolhido não existe mais."]
    if alvo['tipo'] == 'BTM':
        return _no_modulo(context, raiz, alvo, n, gaveta)
    return _no_autoral(raiz, alvo, n, gaveta)
