"""Teste de fumaça da porta e janela na região marcada (feature 011, T024; RF-09, RF-10; D-11, D-12).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_011_region_smoke.py

Sem janela não há modal: `place_in_region` e `modal_in_region` de `doors_windows._PlaceWallObjectBase` rodam sobre um
objeto de teste com o mesmo protocolo (caixa, relatório, cotas), e a confirmação é a do clique (`cut_wall` + `sync`):
- porta de 820 × 2120 a partir do piso: vão e furo exatos, na posição da região;
- janela de 1200 × 1000 com a borda de baixo a 1100: peitoril de 1100;
- região que passa da parede ou encosta em outra abertura: recusa com aviso, inserção normal;
- Esc no modo "na região" cancela a porta e mantém a região; confirmar limpa a região.
"""

import sys
import traceback
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_types  # noqa: E402
from caffmob_draw.openings import region_props, sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
FAILURES = []
Base = dw._PlaceWallObjectBase
dw.hb_placement.draw_header_text = lambda *_args: None      # sem janela não há cabeçalho de área
dw.hb_placement.clear_header_text = lambda *_args: None


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


class Placement:
    """O que `place_in_region`/`modal_in_region` usam do operador de inserção."""

    def __init__(self, kind):
        self.OPENING_KIND = kind
        self.placed_obj = hb_types.GeoNodeCage()
        self.placed_obj.create("Window" if kind == 'WINDOW' else "Door")
        self.placed_obj.obj['IS_WINDOW_BP' if kind == 'WINDOW' else 'IS_ENTRY_DOOR_BP'] = True
        self.placed_obj.obj.btm_opening_real.kind = kind
        self.placed_obj.set_input('Dim X', 0.9)
        self.placed_obj.set_input('Dim Z', 2.0)
        self.placement_objects = [self.placed_obj.obj]
        self.reports = []
        self.cancelled = False

    def report(self, level, message):
        self.reports.append((level, message))

    def update_placement_dimensions(self, *_args):
        pass

    def delete_placement_dimensions(self):
        pass

    def cancel_placement(self, _context):
        self.cancelled = True

    def place(self):
        return Base.place_in_region(self, ctx)

    def confirm(self):
        region_props.clear(ctx)
        dw.cut_wall(self.selected_wall, self.placed_obj.obj)
        sync.sync(ctx, self.placed_obj.obj)
        env.settle()

    def dims(self):
        return round(self.placed_obj.get_input('Dim X'), 6), round(self.placed_obj.get_input('Dim Z'), 6)


def mark(wall, x0, x1, z0, z1):
    region = ctx.window_manager.btm_wall_region
    region.wall, region.side = wall.name, 'FRONT'
    region.x0, region.x1, region.z0, region.z1 = x0, x1, z0, z1
    region.active = True


def main():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    wall = max((o for o in ctx.scene.objects if o.get('IS_WALL_BP')),
               key=lambda o: hb_types.GeoNodeWall(o).get_input('Length'))
    length = hb_types.GeoNodeWall(wall).get_input('Length')
    print(f"parede {wall.name}: {length:.3f} m", flush=True)

    sem = Placement('DOOR')
    check("sem região: inserção de hoje", sem.place() is False and not sem.reports)
    bpy.data.objects.remove(sem.placed_obj.obj, do_unlink=True)

    mark(wall, 0.5, 1.32, 0.0, 2.12)
    door = Placement('DOOR')
    check("porta entra na região", door.place() is True, str(door.reports))
    check("vão de 820 × 2120, nem um milímetro a mais", door.dims() == (0.82, 2.12), str(door.dims()))
    obj = door.placed_obj.obj
    check("na posição da região, presa à parede", obj.parent == wall and abs(obj.location.x - 0.5) < 1e-6
          and abs(obj.location.z) < 1e-9, f"{tuple(obj.location)}")
    door.confirm()
    hole = any(m.type == 'BOOLEAN' and m.object == obj for m in wall.modifiers)
    check("furo de 820 × 2120 na parede e porta real montada", hole and door.dims() == (0.82, 2.12)
          and obj.btm_opening_real.assembly is not None)
    check("confirmar limpa a região", not ctx.window_manager.btm_wall_region.active)

    mark(wall, 1.8, 3.0, 1.1, 2.1)
    window = Placement('WINDOW')
    check("janela entra na região", window.place() is True, str(window.reports))
    check("janela de 1200 × 1000", window.dims() == (1.2, 1.0), str(window.dims()))
    check("peitoril de 1100", abs(window.placed_obj.obj.location.z - 1.1) < 1e-6,
          f"{window.placed_obj.obj.location.z:.4f}")
    window.confirm()

    mark(wall, length - 0.5, length + 4.0, 0.0, 2.1)
    longe = Placement('DOOR')
    check("região que passa da parede: recusa com aviso", longe.place() is False and longe.reports,
          str(longe.reports))
    check("e a região continua marcada", ctx.window_manager.btm_wall_region.active)
    bpy.data.objects.remove(longe.placed_obj.obj, do_unlink=True)

    mark(wall, 0.9, 1.7, 0.0, 2.1)
    cola = Placement('DOOR')
    check("região sobre outra porta: recusa", cola.place() is False and cola.reports, str(cola.reports))
    bpy.data.objects.remove(cola.placed_obj.obj, do_unlink=True)

    mark(wall, 3.1, 3.7, 0.0, 2.1)
    esc = Placement('DOOR')
    esc.place()
    result = Base.modal_in_region(esc, ctx, types.SimpleNamespace(type='ESC', value='PRESS'))
    check("Esc cancela a porta e mantém a região", result == {'CANCELLED'} and esc.cancelled
          and ctx.window_manager.btm_wall_region.active)

    wall.name = "Parede renomeada"
    check("parede renomeada descarta a região sem erro", region_props.region_wall(ctx) == (None, None))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_011_region_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
