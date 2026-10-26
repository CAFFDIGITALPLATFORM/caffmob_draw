"""Prévia do editor de escadas na vista 3D (071 D-24, RF-27): planta e corte lateral num quadro no canto.

Desenhada enquanto o grupo "Escadas" da barra lateral está aberto e a prévia ligada; não mexe na cena nem no Undo.
"""
import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..data.i18n import tr
from . import core

_handle = None
QUADRO = (380, 190)
MARGEM = 16


def _ativa(context):
    wm = context.window_manager
    state = getattr(wm, 'btm_stairs', None)
    if state is None or not state.previa:
        return False
    try:
        from ..ui import sidebar
        return bool(getattr(sidebar.state(context), 'open_group_stairs', False))
    except (AttributeError, ImportError):
        return False


def _retangulos(pecas, u, v, w, h, caixa):
    x0, y0, largura, altura = caixa
    escala = min(largura / max(w, 1), altura / max(h, 1))
    ox = x0 + (largura - w * escala) / 2
    oy = y0 + (altura - h * escala) / 2
    linhas = []
    ordenadas = sorted(pecas, key=lambda p: p['pos'][2] + p['tam'][2]) if v == 1 else pecas
    for p in ordenadas:
        a = (ox + p['pos'][u] * escala, oy + p['pos'][v] * escala)
        b = (a[0] + p['tam'][u] * escala, a[1] + p['tam'][v] * escala)
        linhas += [(a[0], a[1]), (b[0], a[1]), (b[0], a[1]), (b[0], b[1]), (b[0], b[1]), (a[0], b[1]),
                   (a[0], b[1]), (a[0], a[1])]
    return linhas


def desenhar():
    context = bpy.context
    if not _ativa(context):
        return
    regiao = context.region
    e = context.window_manager.btm_stairs.escada()
    pecas, _ = core.pecas(e)
    paineis = [p for p in pecas]
    w, h = QUADRO
    x0, y0 = MARGEM, MARGEM + 30
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    fundo = batch_for_shader(shader, 'TRIS', {'pos': [(x0 - 8, y0 - 8), (x0 + w + 8, y0 - 8), (x0 + w + 8, y0 + h + 24),
                                                      (x0 - 8, y0 - 8), (x0 + w + 8, y0 + h + 24), (x0 - 8, y0 + h + 24)]})
    shader.uniform_float('color', (0.12, 0.12, 0.12, 0.85))
    fundo.draw(shader)
    metade = (w - 16) / 2
    planta = _retangulos(paineis, 0, 1, e.x, e.y, (x0, y0, metade, h))
    corte = _retangulos(paineis, 1, 2, e.y, e.z, (x0 + metade + 16, y0, metade, h))
    shader.uniform_float('color', (0.85, 0.62, 0.35, 1.0))
    batch_for_shader(shader, 'LINES', {'pos': planta + corte}).draw(shader)
    gpu.state.blend_set('NONE')
    fonte = 0
    blf.size(fonte, 12)
    blf.color(fonte, 0.9, 0.9, 0.9, 1.0)
    blf.position(fonte, x0, y0 + h + 6, 0)
    blf.draw(fonte, tr("Planta"))
    blf.position(fonte, x0 + metade + 16, y0 + h + 6, 0)
    blf.draw(fonte, tr("Corte lateral"))
    plano, texto = core.leitura(e)
    blf.position(fonte, x0, y0 - 24, 0)
    blf.color(fonte, *((0.8, 0.8, 0.8, 1.0) if plano.confortavel else (0.95, 0.4, 0.35, 1.0)))
    blf.draw(fonte, texto)
    del regiao


def register():
    global _handle
    if _handle is None:
        _handle = bpy.types.SpaceView3D.draw_handler_add(desenhar, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    global _handle
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        _handle = None
