"""Medição comum dos ensaios de desempenho da 067 (T005, T006): cena de 461 objetos e troca de seleção até o painel
"Selecionado" desenhado pela camada falsa (`ui/layout_probe.py`), que roda o mesmo código de desenho sem tela."""

import statistics
import time

import bpy

import _fixtures_067 as fx
from caffmob_draw.collision import guard
from caffmob_draw.ui import layout_probe

SCENE_SIZE = 461


class _FakeSpace:
    type = 'VIEW_3D'

    class shading:  # noqa: N801
        color_type = 'MATERIAL'
        type = 'SOLID'

    class overlay:  # noqa: N801
        show_overlays = True
        grid_scale = 1.0


class ContextProxy:
    space_data = _FakeSpace()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


CTX = ContextProxy()


@guard.suspended()
def build_scene():
    """Os 15 tipos da fixture mais cópias soltas até 461 objetos; devolve os alvos da troca de seleção."""
    s = fx.scene_15()
    targets = [v for v in vars(s).values()]
    source = s.free
    i = 0
    while len(bpy.context.scene.objects) < SCENE_SIZE:
        copy = source.copy()
        copy.data = source.data
        copy.location = (-5.0 - (i % 20) * 0.5, -5.0 - (i // 20) * 0.5, 0.2)
        bpy.context.collection.objects.link(copy)
        i += 1
    bpy.context.view_layer.update()
    return targets


def select(obj):
    view_layer = bpy.context.view_layer
    for o in view_layer.objects.selected:
        o.select_set(False)
    obj.select_set(True)
    view_layer.objects.active = obj


def draw_panel():
    from caffmob_draw.ui import object_properties
    probe = layout_probe.Probe(layout_probe.Recorder())
    object_properties.draw_selected(probe, CTX)


def measure(targets, rounds=20, before_draw=None):
    """Tempo (ms) de cada troca de seleção até o painel desenhado; `before_draw(obj)` roda dentro da medida."""
    samples = []
    for _round in range(rounds):
        for obj in targets:
            start = time.perf_counter()
            select(obj)
            bpy.context.view_layer.update()
            if before_draw is not None:
                before_draw(obj)
            draw_panel()
            samples.append((time.perf_counter() - start) * 1000.0)
    return samples


def percentiles(samples):
    ordered = sorted(samples)

    def at(p):
        return round(ordered[min(len(ordered) - 1, int(round(p / 100.0 * (len(ordered) - 1))))], 2)
    return {'n': len(samples), 'p50': at(50), 'p95': at(95), 'p99': at(99),
            'media': round(statistics.fmean(samples), 2)}
