"""Fita de borda visual (feature 067, T029; RF-080 a RF-085).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda4_fita.py

- três chapas de 15 mm (um componente): a frente ganha uma faixa de 45 mm, sem emenda, com as normais para fora;
- o rótulo segue o estado (criar, mudar cor, misto) e repetir não duplica faixa;
- o componente girado 90° gera fita nas bordas certas;
- redimensionar a chapa atualiza a fita sem fresta nem sobra; apagar a chapa tira a fita (sem fita flutuante);
- a cor lisa preserva a imagem do material fonte;
- a fita fica fora do plano de corte, da colisão e dos alvos de textura: a lista de corte do módulo não muda;
- tudo num passo de Desfazer.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw.aggregates import ops_authored  # noqa: E402
from caffmob_draw.edgeband import core, ops as band_ops, pieces  # noqa: E402

T = 0.015


def component(name="Engrossado", x=0.0):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location.x = x
    plates = [authored_env.cube(f"{name} chapa {i}", (0.6, 0.4, T), (0, 0, T / 2 + i * T), root) for i in range(3)]
    env.settle()
    ops_authored.adopt(root, [root] + plates)
    return root, plates


def apply(root, **kwargs):
    authored_env.select([root])
    bpy.context.view_layer.update()
    return bpy.ops.caffmob.edgeband_apply('EXEC_DEFAULT', **kwargs)


def front(root):
    """A faixa da frente (−Y no referencial do componente), pelas chaves das bordas."""
    for obj in pieces.bands_of(root):
        keys = core.loads(obj.btm_edgeband.edge_keys)
        if keys and all(k.endswith('|Y-') for k in keys):
            return obj
    return None


def outward(obj):
    """Toda face da malha da faixa aponta para fora do centro dela (sem face invertida)."""
    center = sum((v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
    return all(p.normal.dot(p.center - center) > 0 for p in obj.data.polygons)


def cut_list():
    from caffmob_draw.cutting import part_extractor
    parts, _incompatible = part_extractor.extract_production_parts(bpy.context)
    return sorted((p.name, round(p.width, 2), round(p.height, 2), p.grain_direction) for p in parts)


def body(w):
    env.clean_scene()
    bpy.context.scene.btm_component_select = False
    oak = bpy.data.materials.new("Carvalho fita")
    root, plates = component()
    state, missing = band_ops.state_for(root)
    j.check(state == core.CREATE, "sem fita: Criar e aplicar fita de borda", str(state))
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    module = bpy.context.object
    module.location.x = 3.0
    env.settle()
    before = cut_list()

    w.push("Antes da fita")
    result = apply(root, material=oak.name)
    w.push("Fita")
    bands = pieces.bands_of(root)
    band = front(root)
    j.check(result == {'FINISHED'} and len(bands) == 4, "criar gera 4 faixas (uma por lado)", str(len(bands)))
    j.check(band is not None and abs(band.btm_edgeband.coverage_width - 0.045) < 1e-6
            and len(core.loads(band.btm_edgeband.edge_keys)) == 3 and len(band.data.polygons) == 6,
            "a frente das três chapas é uma faixa só de 45 mm, sem emenda")
    j.check(band is not None and outward(band), "faixa sem face invertida")
    j.check(all(o.btm_cut_exclude and o.btm_plane.collision_override == 'OFF' for o in bands),
            "a fita fica fora do corte e da colisão")
    j.check(band_ops.state_for(root)[0] == core.CHANGE, "com fita em todas as bordas: Mudar cor da fita")
    j.check(cut_list() == before, "a lista de corte não muda com a fita visual")
    from caffmob_draw.texture_library import apply as texture_apply
    j.check(not set(bands) & set(texture_apply.targets(plates[0])), "a fita não é alvo de textura")

    apply(root, material=oak.name)
    j.check(len(pieces.bands_of(root)) == 4, "repetir não duplica a fita")

    # Cor lisa preserva a imagem do material fonte.
    image = bpy.data.images.new("fonte", 4, 4)
    tex = oak.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    apply(root, use_color=True, color=(0.1, 0.2, 0.8, 1.0))
    j.check(all(o.data.materials[0].get('btm_edgeband_solid') for o in pieces.bands_of(root))
            and oak.node_tree.nodes.get(tex.name).image == image and oak.users >= 0,
            "cor lisa: material liso na fita, a imagem do material fonte fica")

    # Misto: apagar uma faixa deixa bordas faltantes.
    lone = next(o for o in pieces.bands_of(root) if o is not front(root))
    bpy.data.objects.remove(lone)
    state, missing = band_ops.state_for(root)
    j.check(state == core.MIXED and missing, "caso misto lista as bordas faltantes", f"{state} {len(missing)}")
    apply(root, material=oak.name)
    j.check(len(pieces.bands_of(root)) == 4 and band_ops.state_for(root)[0] == core.CHANGE,
            "criar nas faltantes completa sem duplicar")

    # Redimensionar a chapa: a faixa acompanha, sem fresta.
    from caffmob_draw.edgeband import sync
    for plate in plates:
        plate.data.transform(Matrix.Diagonal((1.5, 1.0, 1.0, 1.0)))
        plate.data.update()
    bpy.context.view_layer.update()
    j.check(sync._pending == {root.name}, "o handler anota o componente para o timer", str(sync._pending))
    sync.flush()                                    # o timer roda depois deste passo; o ensaio chama já
    band = front(root)
    j.check(band is not None and abs(band.btm_edgeband.length - 0.9) < 1e-6,
            "redimensionar a chapa estica a fita sem fresta", str(band.btm_edgeband.length if band else None))

    # Componente girado 90°.
    turned, turned_plates = component("Girado", x=6.0)
    turned.matrix_world = Matrix.Translation((6.0, 0, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Z')
    bpy.context.view_layer.update()
    apply(turned, material=oak.name)
    widths = sorted(round(o.btm_edgeband.coverage_width, 4) for o in pieces.bands_of(turned))
    j.check(widths == [0.045] * 4, "componente girado 90°: fita nas quatro bordas de 45 mm", str(widths))

    # Selecionar a fita abre as propriedades dela (RF-084).
    from caffmob_draw.target import resolver as r, snapshot, view
    band = pieces.bands_of(turned)[0]
    authored_env.select([band])
    bpy.context.view_layer.update()
    target = snapshot.ensure(bpy.context)
    model = view.build(target, view.COMPLETE)
    fields = {(f.data, f.prop) for f in view.fields(model)}
    j.check(target.kind == r.EDGEBAND and not target.move_uid, "a fita selecionada é Fita de borda, sem mover sozinha")
    j.check({('edgeband', p) for p in ('use_color', 'material', 'color', 'thickness', 'coverage_width', 'length')}
            <= fields, "a seção da fita mostra material, cor lisa, espessura, largura e comprimento", str(fields))
    from caffmob_draw.ui import layout_probe, object_properties as op
    import _desempenho_067 as perf
    op.panel_mode = lambda _c: 'COMPLETE'
    op.draw_selected(layout_probe.Probe(layout_probe.Recorder()), perf.CTX)
    j.check(True, "o draw da seção da fita não falha")

    # Apagar uma chapa do meio: as faixas encolhem ou saem; nenhuma fita flutuante.
    bpy.data.objects.remove(turned_plates[2])
    bpy.context.view_layer.update()
    sync.flush()
    widths = sorted(round(o.btm_edgeband.coverage_width, 4) for o in pieces.bands_of(turned))
    j.check(widths == [0.03] * 4, "apagar a chapa de cima encolhe a fita para 30 mm", str(widths))

    # Desfazer: a fita sai num passo.
    w.undo()
    j.check(not pieces.bands_of(bpy.data.objects["Engrossado"]), "um Desfazer tira a fita criada")

    # Último passo de propósito: por script, mexer na cena no mesmo passo de timer logo depois do Desfazer derrubou o
    # Blender de vez em quando (na interface o Desfazer roda entre eventos).


j.run("blender_067_onda4_fita", body)
