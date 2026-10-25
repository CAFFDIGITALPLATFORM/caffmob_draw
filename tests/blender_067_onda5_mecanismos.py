"""Mecanismos e contato real (feature 067, T031; RF-100 a RF-102, RF-105).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda5_mecanismos.py

- box (folha composta de vidro e puxador afastado): 0 → 50 → 100 → 0% volta à pose exata, pelo editor animado;
- giro, correr, basculante e gaveta: cada mecanismo vem dos dados (nunca do nome) e anda no eixo certo; a gaveta
  corre em profundidade; ferragem e puxador acompanham a folha;
- folha composta do armário autoral não acusa contato com o vidro fixo do próprio armário;
- folha contra a lateral do armário acusa contato;
- o editor anima um componente com várias folhas de uma vez, num passo de Desfazer.
"""

import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw import mechanisms  # noqa: E402
from caffmob_draw.aggregates import leaf, ops_authored  # noqa: E402
from caffmob_draw.aggregates.ops_members import set_member  # noqa: E402


def tower(name, x=0.0):
    """Armário autoral: duas laterais, base, tampo e um vidro fixo na metade de cima."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location.x = x
    parts = [authored_env.cube(f"{name} lateral E", (0.018, 0.4, 1.0), (-0.291, 0, 0.5), root),
             authored_env.cube(f"{name} lateral D", (0.018, 0.4, 1.0), (0.291, 0, 0.5), root),
             authored_env.cube(f"{name} base", (0.564, 0.4, 0.018), (0, 0, 0.009), root),
             authored_env.cube(f"{name} tampo", (0.564, 0.4, 0.018), (0, 0, 0.991), root)]
    glass = authored_env.cube(f"{name} vidro fixo", (0.56, 0.004, 0.45), (0, -0.19, 0.75), root)
    env.settle()
    ops_authored.adopt(root, [root] + parts + [glass])
    glass.btm_member.role = 'FIXED_FRONT'
    return root, parts, glass


def box_leaf(root, name, location, hinge='LEFT'):
    """Folha composta: vidro com um puxador afastado (a caixa envolvente inclui o vazio entre os dois)."""
    sheet = authored_env.cube(f"{name} vidro", (0.27, 0.004, 0.44), location, root)
    pull = authored_env.cube(f"{name} puxador", (0.02, 0.02, 0.2), (0.1, -0.05, 0.0), sheet)
    pull['IS_CABINET_PULL'] = True
    env.settle()
    set_member(sheet, root, 'LEAF_PART', reparent=False)
    leaf.make_leaf(sheet, root, motion='SWING', hinge=hinge)
    return sheet, pull


def matrix_close(a, b, tol=1e-6):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4)) <= tol


def body(w):
    env.clean_scene()
    bpy.context.scene.btm_component_select = False
    bpy.context.scene.btm_settings.block_penetration = True
    root, parts, glass = tower("Torre")
    # A folha fica na frente do vidro fixo, na metade de baixo, colada à lateral esquerda.
    sheet, pull = box_leaf(root, "Folha composta", (-0.135, -0.205, 0.25))
    mech = mechanisms.of(sheet)
    j.check(mech is not None and mech.kind == mechanisms.HINGE, "a folha do box é giro (pelos dados)")
    rest = sheet.matrix_world.copy()
    pull_rest = pull.matrix_world.copy()
    authored_env.select([sheet])
    bpy.context.view_layer.update()
    w.push("Antes de abrir")
    for percent in (0.0, 50.0, 100.0, 0.0):
        with w.override():
            result = bpy.ops.caffmob.mechanism_set('EXEC_DEFAULT', percent=percent)
        bpy.context.view_layer.update()
        if percent == 100.0:
            opened = sheet.matrix_world.copy()
            j.check(not matrix_close(opened, rest) and not matrix_close(pull.matrix_world, pull_rest),
                    "abrir gira a folha e o puxador vai junto")
    j.check(result == {'FINISHED'} and matrix_close(sheet.matrix_world, rest),
            "box 0 → 50 → 100 → 0% volta à pose exata")
    j.check(sheet.btm_aggregate.contact_name != glass.name, "a folha composta não acusa contato com o vidro fixo",
            sheet.btm_aggregate.contact_name)

    # #141: folha de correr composta (vidro + puxador afastado) passando com o vão entre os dois por cima de um
    # vidro fixo do próprio armário. As malhas reais não se tocam; a caixa envolvente tocaria.
    from caffmob_draw.aggregates import collision
    from caffmob_draw.aggregates import group
    glass_part = authored_env.cube("Correr composta vidro", (0.2, 0.004, 0.44), (-0.15, -0.215, 0.25))
    knob = authored_env.cube("Correr puxador", (0.02, 0.02, 0.04), (-0.15, -0.275, 0.45))
    pane = authored_env.cube("Vidro fixo baixo", (0.15, 0.004, 0.12), (0.15, -0.245, 0.1), root)
    env.settle()
    slider = group.create_group([glass_part, knob], name="Correr composta")    # folha composta: grupo de peças
    slider.parent = root
    env.settle()
    set_member(slider, root, 'LEAF_PART', reparent=False)
    set_member(pane, root, 'FIXED_FRONT', reparent=False)
    pane.btm_member.role = 'CARCASS'              # aqui o vidro conta como obstáculo: prova a geometria real
    leaf.make_leaf(slider, root, motion='SLIDE', slide_dir='POS_X', travel=0.3)
    collision.invalidate()
    tester = collision.Tester(slider)
    j.check(tester.parts and all(tester.hit(f) is None for f in (0.0, 0.5, 1.0)),
            "malhas reais: a folha composta passa sem contato com o vidro no vão")
    tester.parts = []                              # o teste antigo, pela caixa envolvente
    j.check(any(tester.hit(f) is not None for f in (0.0, 0.5, 1.0)),
            "a caixa envolvente acusaria o contato falso (o que o #141 relatou)")

    # Contato real: uma folha de correr dentro da caixa anda para a direita e bate na lateral.
    other = authored_env.cube("Contra", (0.27, 0.004, 0.44), (0.135, -0.1, 0.25), root)
    env.settle()
    set_member(other, root, 'LEAF_PART', reparent=False)
    leaf.make_leaf(other, root, motion='SLIDE', slide_dir='POS_X', travel=0.3)
    other.btm_aggregate.open_value = 1.0
    j.check(other.btm_aggregate.contact_name != "" and other.btm_aggregate.open_value < 1.0,
            "folha contra a lateral acusa contato", f"{other.btm_aggregate.contact_name} "
            f"{other.btm_aggregate.open_value:.3f}")

    # Os quatro mecanismos pelos dados.
    env.clean_scene()
    holder = bpy.data.objects.new("Suporte", None)
    bpy.context.collection.objects.link(holder)
    holder['IS_AUTHORED_CABINET'] = True
    holder.btm_authored.is_authored = True
    cases = (('giro', 'SWING', 'LEFT', mechanisms.HINGE), ('basculante', 'SWING', 'TOP', mechanisms.TILT),
             ('correr', 'SLIDE', 'LEFT', mechanisms.SLIDE), ('gaveta', 'DRAWER', 'LEFT', mechanisms.DRAWER))
    for i, (label, motion, hinge, kind) in enumerate(cases):
        panel = authored_env.cube(f"Painel {label}", (0.4, 0.018, 0.4), (i * 1.0, 0, 0.2), holder)
        env.settle()
        leaf.make_leaf(panel, holder, motion=motion, hinge=hinge, travel=0.3)
        mech = mechanisms.of(panel)
        before = panel.matrix_world.copy()
        mech.set_fraction(1.0)
        bpy.context.view_layer.update()
        after = panel.matrix_world
        moved = after.translation - before.translation
        if kind == mechanisms.DRAWER:
            ok = moved.y < -0.25 and abs(moved.x) < 1e-4
        elif kind == mechanisms.SLIDE:
            ok = abs(moved.x) > 0.25 and abs(moved.y) < 1e-4
        else:
            ok = not matrix_close(Matrix(before.to_3x3()).to_4x4(), Matrix(after.to_3x3()).to_4x4())
        j.check(mech.kind == kind and ok, f"{label}: mecanismo {kind} anda no eixo certo",
                f"{mech.kind} {tuple(round(v, 3) for v in moved)}")
        mech.set_fraction(0.0)

    # Componente com várias folhas: o editor anima todas juntas, num passo.
    authored_env.select([holder])
    bpy.context.view_layer.update()
    with w.override():
        result = bpy.ops.caffmob.mechanism_set('EXEC_DEFAULT', percent=100.0, scope='COMPONENT')
    fractions = [m.fraction() for m in mechanisms.all_of(holder)]
    j.check(result == {'FINISHED'} and len(fractions) == 4 and all(abs(f - 1.0) < 1e-6 for f in fractions),
            "o editor abre as quatro folhas do componente de uma vez", str(fractions))


j.run("blender_067_onda5_mecanismos", body)
