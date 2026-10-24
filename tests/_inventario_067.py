"""Captura, pela camada falsa, dos comandos e campos que o painel "Selecionado" e o menu do botão direito mostram para
cada um dos 15 tipos da fixture (feature 067, T004; referência de RF-004 e RF-013)."""

import bpy

import _desempenho_067 as perf
import _fixtures_067 as fx
from caffmob_draw.ui import layout_probe

TYPES = ('btm_module', 'hb_module', 'authored', 'member', 'part', 'geometry', 'front', 'leaf', 'wall', 'room_door',
         'window', 'cladding', 'floor', 'ceiling', 'light', 'camera', 'annotation', 'free')


def _menu(recorder, errors, name):
    menu = bpy.types.VIEW3D_MT_object_context_menu
    for func in list(getattr(menu.draw, '_draw_funcs', [])):
        if not getattr(func, '__module__', '').startswith('caffmob_draw'):
            continue
        proxy = type('MenuProxy', (), {'layout': layout_probe.Probe(recorder)})()
        with recorder.section("[menu]"):
            try:
                func(proxy, perf.CTX)
            except Exception as exc:          # noqa: BLE001 - erro de desenho é achado
                errors.append(f"{name}: menu {func.__name__}: {exc}")


def capture(mode=None):
    from caffmob_draw.ui import object_properties
    if mode is not None:                                   # sem a extensão instalada não há preferências
        object_properties.panel_mode = lambda _context: mode
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False      # a peça fica ativa (sem subir ao módulo)
    result, errors = {}, []
    for name in TYPES:
        perf.select(getattr(s, name))
        bpy.context.view_layer.update()
        recorder = layout_probe.Recorder()
        with recorder.section("[painel]"):
            try:
                object_properties.draw_selected(layout_probe.Probe(recorder), perf.CTX)
            except Exception as exc:          # noqa: BLE001
                errors.append(f"{name}: painel: {exc.__class__.__name__}: {exc}")
        _menu(recorder, errors, name)
        operators = sorted({r['name'] for r in recorder.records if r['kind'] == 'operator'})
        props = sorted({f"{r.get('owner', '')}.{r['name']}" for r in recorder.records if r['kind'] == 'prop'})
        result[name] = {'operators': operators, 'props': props}
    return result, errors
