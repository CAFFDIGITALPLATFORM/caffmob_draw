"""Validação geométrica do armário v2 (feature 023; RF-03, RN-CABINET_EDITOR-21).

Núcleo puro, importável sem `bpy`. As regras vêm do legado (`cabinet_editor/validate.py`):

- `GEO-001`: peça que passa da largura ou da altura do módulo em mais de 1 mm.
- `GEO-002`: prateleiras/divisórias que se sobrepõem em mais de 1 mm.

A profundidade não entra no GEO-001: frentes e puxadores podem passar da face, como no editor antigo.
"""

TOLERANCIA = 1.0      # mm
PAPEIS_INTERNOS = ('DIVISORIA', 'PRATELEIRA')


def _intersecao(a, b):
    """(dx, dy, dz) da interseção de duas caixas, zero quando não se tocam."""
    (ax0, ay0, az0), (ax1, ay1, az1) = a
    (bx0, by0, bz0), (bx1, by1, bz1) = b
    return (max(0.0, min(ax1, bx1) - max(ax0, bx0)),
            max(0.0, min(ay1, by1) - max(ay0, by0)),
            max(0.0, min(az1, bz1) - max(az0, bz0)))


def violacoes(pecas, largura, altura, tolerancia=TOLERANCIA):
    """[dict] com `codigo`, `nome` e `detalhe` das peças reprovadas.

    `pecas` é a lista de `build.pecas` (chaves `papel`, `nome`, `box`). Ferragem fica de fora: não é chapa do módulo.
    """
    x0_modulo, x1_modulo = -largura / 2.0, largura / 2.0
    saida = []
    for peca in pecas:
        if peca.get('ferragem'):
            continue
        (px0, _py0, pz0), (px1, _py1, pz1) = peca['box']
        if px0 < x0_modulo - tolerancia or px1 > x1_modulo + tolerancia:
            saida.append({'codigo': 'GEO-001', 'nome': peca['nome'],
                          'detalhe': f"passa da largura do módulo ({largura:.0f} mm)"})
        elif pz0 < -tolerancia or pz1 > altura + tolerancia:
            saida.append({'codigo': 'GEO-001', 'nome': peca['nome'],
                          'detalhe': f"passa da altura do módulo ({altura:.0f} mm)"})

    internos = [p for p in pecas if p.get('papel') in PAPEIS_INTERNOS and not p.get('ferragem')]
    for i, primeira in enumerate(internos):
        for segunda in internos[i + 1:]:
            if not (primeira.get('nome', '').startswith('Prateleira')
                    and segunda.get('nome', '').startswith('Prateleira')):
                # Divisória contra prateleira encostada é montagem normal; só peças do mesmo tipo se sobrepõem.
                if primeira.get('papel') != segunda.get('papel'):
                    continue
            dx, dy, dz = _intersecao(primeira['box'], segunda['box'])
            if dx > tolerancia and dy > tolerancia and dz > tolerancia:
                saida.append({'codigo': 'GEO-002', 'nome': primeira['nome'],
                              'detalhe': f"sobrepõe {segunda['nome']} em {min(dx, dy, dz):.1f} mm"})
    return saida


def pecas_da_raiz(raiz):
    """(spec, peças) do armário v2 da raiz; `(None, [])` sem raiz ou sem o grupo do armário."""
    if raiz is None or getattr(raiz, 'btm_armario', None) is None:
        return None, []
    from . import build
    from . import ops

    armario = raiz.btm_armario
    spec = ops.spec_do_armario(raiz)
    itens = build.pecas(spec, ops.divisoes_do_armario(armario), ops.gavetas_do_armario(armario),
                        ops.internos_do_armario(armario))
    return spec, itens


def violacoes_da_raiz(raiz):
    """Atalho para o painel e para os operadores: violações do armário da raiz."""
    spec, itens = pecas_da_raiz(raiz)
    if spec is None:
        return []
    return violacoes(itens, spec.largura, spec.altura)
