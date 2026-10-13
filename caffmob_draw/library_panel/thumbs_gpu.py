"""Miniaturas da grade na GPU (feature 014, T027; D-05, investigation.md §6).

Medido no Blender 5.2 (T001 e T027):
- `bpy.utils.previews` → `image_pixels_float` → `GPUTexture`: cerca de 25 ms por miniatura;
- `bpy.data.images.load` → `pixels.foreach_get` → `GPUTexture` próprio, removendo a `Image` na mesma conversão:
  cerca de 9 ms. É o caminho usado aqui; o arquivo do usuário não fica com nenhuma `Image` (D-05).

Criar e remover data-blocks dentro do callback de desenho não é seguro, então o desenho só pede (`texture`) e um
timer converte a fila fora dele, dentro do orçamento por chamada, e pede outro redesenho da vista 3D até esvaziar.
`free()` libera tudo (chamado no `unregister`).
"""

import time
from array import array

import bpy  # type: ignore
import gpu  # type: ignore

BUDGET_S = 0.008                           # orçamento por chamada (investigation.md §6)
TIMER_INTERVAL = 0.01

_state = {"tex": {}, "queue": [], "queued": set(), "failed": set(), "timer": False}


def texture(key, path):
    """GPUTexture da miniatura, ou None enquanto ela não foi convertida (ou se falhou)."""
    tex = _state["tex"].get(key)
    if tex is not None:
        return tex
    if key not in _state["queued"] and key not in _state["failed"] and path:
        _state["queued"].add(key)
        _state["queue"].append((key, path))
        _ensure_timer()
    return None


def failed(key):
    return key in _state["failed"]


def pending():
    return len(_state["queue"])


def _convert(path):
    image = bpy.data.images.load(path, check_existing=False)
    try:
        width, height = image.size[:]
        if not width or not height:
            return None
        size = width * height * 4
        pixels = array('f', bytes(4 * size))
        image.pixels.foreach_get(pixels)
    finally:
        bpy.data.images.remove(image)
    return gpu.types.GPUTexture((width, height), format='RGBA8', data=gpu.types.Buffer('FLOAT', size, pixels))


def process(budget=BUDGET_S):
    """Converte miniaturas da fila até o orçamento (segundos), pelo menos uma. Devolve quantas continuam na fila."""
    start = time.perf_counter()
    while _state["queue"]:
        key, path = _state["queue"].pop(0)
        _state["queued"].discard(key)
        try:
            tex = _convert(path)
        except (RuntimeError, OSError, ValueError, TypeError):
            tex = None
        if tex is None:
            _state["failed"].add(key)        # arquivo ilegível: a célula mostra o fundo vazio
        else:
            _state["tex"][key] = tex
        if time.perf_counter() - start >= budget:
            break
    return len(_state["queue"])


def _tag_redraw():
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except (AttributeError, ReferenceError):
        pass


def _tick():
    left = process()
    _tag_redraw()
    if left:
        return TIMER_INTERVAL
    _state["timer"] = False
    return None


def _ensure_timer():
    if not _state["timer"]:
        _state["timer"] = True
        bpy.app.timers.register(_tick, first_interval=0.0)


def free():
    if _state["timer"] and bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    _state["timer"] = False
    _state["tex"].clear()
    _state["queue"].clear()
    _state["queued"].clear()
    _state["failed"].clear()
