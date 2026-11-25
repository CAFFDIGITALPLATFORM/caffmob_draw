"""E2E da feature 021 executado no Blender 5.2, pela API real do add-on (mesma superfície do MCP).

Rode dentro do Blender (MCP ou `--background --python`) e leia o JSON final: PASS/FAIL por função.
"""

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Vector

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:  # executado pelo MCP: o add-on já está registrado nesta sessão
    ROOT = None
if ROOT is not None:
    if str(ROOT / "tests") not in sys.path:
        sys.path.insert(0, str(ROOT / "tests"))
    if not hasattr(bpy.types.Scene, "btm_settings"):
        import _blender_env  # noqa: F401,E402  (registra o add-on num Blender limpo)

SCENE = bpy.context.scene
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name if ok else f"{name} :: {detail}")


def section(fn):
    try:
        fn()
    except Exception:
        FAIL.append(f"{fn.__name__} :: exceção {traceback.format_exc(limit=3)}")


def clean():
    for o in list(bpy.data.objects):
        try:
            bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)


def select(obj):
    bpy.context.view_layer.update()
    for o in list(bpy.context.view_layer.objects):
        if o is not None:
            o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    if obj is not None:
        obj.select_set(True)


def cube(name, size=(1, 1, 1), loc=(0, 0, 0)):
    m = bpy.data.meshes.new(name)
    import bmesh

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(m)
    bm.free()
    o = bpy.data.objects.new(name, m)
    SCENE.collection.objects.link(o)
    o.location = loc
    return o


# 1. Camadas
def layers_block():
    from caffmob_draw.data import layers

    clean()
    names = []
    for kind in ("WALL", "FLOOR", "CEILING", "OPENING"):
        c = layers.ensure_arquitetura(SCENE, kind)
        arq = bpy.data.collections.get("Arquitetura")
        names.append(
            (kind, c.name, "Arquitetura" if (arq is not None and arq.children.get(c.name) is not None) else None)
        )
    check(
        "camadas: subcoleções Arquitetura", [n for _k, n, _p in names] == ["Parede", "Piso", "Teto", "Aberturas"], names
    )
    check("camadas: pai é Arquitetura", all(p == "Arquitetura" for _k, _n, p in names), names)
    mar = layers.ensure_marcenaria(SCENE)
    check("camadas: Marcenaria na cena", mar.name == "Marcenaria" and any(x == mar for x in SCENE.collection.children))
    layers.ensure_marcenaria(SCENE)
    layers.ensure_arquitetura(SCENE, "WALL")
    dup = [c.name for c in bpy.data.collections if c.name.endswith(".001")]
    check("camadas: reexecutar não duplica coleções", not dup, dup)
    o = cube("Parede_teste")
    layers.place(o, layers.ensure_arquitetura(SCENE, "WALL"), SCENE)
    check(
        "camadas: place move o objeto para a subcoleção",
        o.users_collection[0].name == "Parede" and len(o.users_collection) == 1,
        [c.name for c in o.users_collection],
    )
    kid = cube("Filho_teste")
    kid.parent = o
    layers.place_hierarchy(o, mar, SCENE)
    check(
        "camadas: place_hierarchy move raiz e filhos", o.users_collection[0] == mar and kid.users_collection[0] == mar
    )


# 2. Piso direcional
def floor_block():

    clean()
    SCENE.btm_settings.floor_thickness = 0.12
    SCENE.btm_settings.floor_thickness_direction = "DOWN"
    r = bpy.ops.caffmob.floor_builder(size_x=4.0, size_y=3.0)
    f = bpy.context.active_object
    zs = [(f.matrix_world @ v.co).z for v in f.data.vertices]
    check(
        "piso DOWN: criado no Piso de Arquitetura",
        r == {"FINISHED"} and f.users_collection[0].name == "Piso",
        [c.name for c in f.users_collection],
    )
    check(
        "piso DOWN: espessura para −Z",
        abs(min(zs) + 0.12) < 1e-4 and abs(max(zs)) < 1e-4,
        f"{min(zs):.4f}..{max(zs):.4f}",
    )
    check(
        "piso DOWN: direção gravada",
        f.get("btm_floor_direction") == "DOWN" and abs(f.get("btm_floor_thickness") - 0.12) < 1e-6,
    )
    SCENE.btm_settings.floor_thickness_direction = "UP"
    bpy.ops.caffmob.floor_builder(size_x=4.0, size_y=3.0)
    f2 = bpy.context.active_object
    zs2 = [(f2.matrix_world @ v.co).z for v in f2.data.vertices]
    check(
        "piso UP: espessura para +Z",
        abs(min(zs2)) < 1e-4 and abs(max(zs2) - 0.12) < 1e-4,
        f"{min(zs2):.4f}..{max(zs2):.4f}",
    )


# 3. OpCut: gerar, prévia e exportação
def opcut_block():
    from caffmob_draw.cutting import ops_opcut

    clean()
    bpy.ops.caffmob.cabinet_editor()
    root = bpy.context.view_layer.objects.active
    check("opcut: armário v2 aberto", root is not None and hasattr(root, "btm_armario"))
    bpy.ops.caffmob.armario_v2_montar_caixa()
    bpy.ops.caffmob.armario_v2_inserir_divisoria()
    root.btm_armario.bloco_quantidade = 2
    root.btm_armario.bloco_altura = 200.0
    bpy.ops.caffmob.armario_v2_criar_bloco_gavetas()
    r = bpy.ops.caffmob.opcut_generate()
    plan = ops_opcut._last_result.get("plan")
    groups = ops_opcut._last_result.get("groups")
    check(
        "opcut: gera plano e lista por módulo",
        r == {"FINISHED"} and plan is not None and len(plan.sheets) >= 1 and len(groups) >= 1,
        f"{r} chapas={len(plan.sheets) if plan else '?'} grupos={len(groups) if groups else '?'}",
    )
    names = [it.label for sh in plan.sheets for it in sh.used] if plan else []
    check(
        "opcut: peças do armário no plano", any("LATERAL" in n.upper() or "BASE" in n.upper() for n in names), names[:6]
    )
    check(
        "opcut: sem ferragem no plano",
        not any("CORREDI" in n.upper() for n in names),
        [n for n in names if "CORREDI" in n.upper()],
    )
    check("opcut: prévia RGBA no Blender", bpy.data.images.get("CAFFMob_PlanoCorte_Preview") is not None)
    bpy.ops.caffmob.opcut_preview_step(delta=1)
    tmp = tempfile.mkdtemp(prefix="caffmob_021_")
    for fmt in ("HTML", "SVG", "PDF"):
        p = os.path.join(tmp, f"plano.{fmt.lower()}")
        r2 = bpy.ops.caffmob.opcut_export(filepath=p, export_format=fmt)
        leftovers = [f for f in os.listdir(tmp) if f.endswith(".tmp")]
        check(
            f"opcut: exporta {fmt} atômico",
            r2 == {"FINISHED"} and os.path.isfile(p) and os.path.getsize(p) > 100 and not leftovers,
            f"{r2} {os.path.getsize(p) if os.path.isfile(p) else 'ausente'} {leftovers}",
        )
    return tmp


# 4. Conversão em gaveteiro
def drawer_block():

    clean()
    src = cube("Gaveta_unica", size=(0.6, 0.4, 0.2), loc=(0, 0, 0.1))
    # 6 ilhas: duas laterais, contrafrente, traseira, fundo e frente
    import bmesh

    bm = bmesh.new()
    boxes = [
        ((-0.3, -0.2, 0), (-0.28, 0.2, 0.2)),
        ((0.28, -0.2, 0), (0.3, 0.2, 0.2)),
        ((-0.3, 0.18, 0), (0.3, 0.2, 0.2)),
        ((-0.3, -0.2, 0), (0.3, -0.18, 0.2)),
        ((-0.28, -0.18, 0), (0.28, 0.18, 0.02)),
        ((-0.28, -0.21, 0.02), (0.28, 0.21, 0.2)),
    ]
    for mn, mx in boxes:
        r = bmesh.ops.create_cube(bm, size=1.0)
        vs = r["verts"]
        for v in vs:
            v.co.x = mn[0] if v.co.x < 0 else mx[0]
            v.co.y = mn[1] if v.co.y < 0 else mx[1]
            v.co.z = mn[2] if v.co.z < 0 else mx[2]
    m = bpy.data.meshes.new("Gaveta_ilhas")
    bm.to_mesh(m)
    bm.free()
    src.data = m
    select(src)
    r = bpy.ops.caffmob.convert_to_drawer(completar_faltantes=False, abrir_editor=False)
    root = bpy.context.view_layer.objects.active
    meta = json.loads(root.get("btm_gaveteiro_meta", "{}")) if root else {}
    check("gaveteiro: converte sem bloquear", r == {"FINISHED"} and root is not None and root.get("btm_drawer_unit"), r)
    check(
        "gaveteiro: raiz na camada Marcenaria",
        root is not None and root.users_collection[0].name == "Marcenaria",
        [c.name for c in root.users_collection] if root else None,
    )
    check(
        "gaveteiro: meta grava reconhecidas/faltantes/ferragens",
        "reconhecidas" in meta and "faltantes" in meta and "ferragens" in meta,
        meta,
    )
    check("gaveteiro: original preservado e fora do corte", src.get("btm_cut_exclude") is True and src.hide_viewport)
    check("gaveteiro: peças vinculadas à raiz", any(c.parent == root for c in bpy.data.objects if c is not root))


# 5. Parede rebaixada e menu
def lowered_block():
    clean()
    wall = cube("Parede_HB", size=(2.0, 0.1, 2.6), loc=(0, 0, 1.3))
    wall["IS_WALL_BP"] = True
    select(wall)
    from caffmob_draw.operators import ops_wall_extras as owe

    class GW:
        def __init__(self, obj):
            self.obj = obj

        def get_input(self, name):
            return 2.0 if name == "Length" else 0.1

    _orig = owe.hb_types.GeoNodeWall
    owe.hb_types.GeoNodeWall = GW
    try:
        r = bpy.ops.caffmob.wall_lower()
    finally:
        owe.hb_types.GeoNodeWall = _orig
    proxy = bpy.data.objects.get("Parede_HB_Rebaixada")
    from caffmob_draw.selection import classify, lowered_wall_core

    check(
        "parede rebaixada: proxy criado e marcado",
        r == {"FINISHED"}
        and proxy is not None
        and proxy.get("btm_is_lowered_wall")
        and proxy.get("btm_lowered_wall_ref") == "Parede_HB",
        r,
    )
    check(
        "parede rebaixada: classificada como WALL",
        proxy is not None and classify.classify(proxy).kind == classify.WALL,
        classify.classify(proxy).kind if proxy else None,
    )
    check(
        "parede rebaixada: resolve para a parede original",
        proxy is not None and lowered_wall_core.resolve_lowered_wall(proxy, bpy.data.objects) == wall,
    )
    # menu de contexto
    from caffmob_draw.ui import context_menu

    class L:
        def __init__(self):
            self.ops, self.menus, self.labels = [], [], []

        def operator(self, idname, **kw):
            self.ops.append((idname, kw.get("text")))

        def menu(self, idname, **kw):
            self.menus.append(idname)

        def separator(self):
            pass

        def label(self, text="", **kw):
            self.labels.append(text)

        def prop(self, *a, **kw):
            pass

        def row(self, *a, **kw):
            return self

        def column(self, *a, **kw):
            return self

        def box(self):
            return self

    select(proxy)
    lay = L()
    fake = SimpleNamespace(layout=lay)
    context_menu.draw_context_menu(fake, bpy.context)
    check("menu: Restaurar Parede na parede rebaixada", "caffmob.wall_lower" in [o for o, _t in lay.ops], lay.ops)
    check("menu: submenu Converter em presente", "BTM_MT_ConvertToMenu" in lay.menus, lay.menus)
    r = bpy.ops.caffmob.wall_lower()
    check(
        "parede rebaixada: Restaurar remove o proxy e devolve a parede",
        r == {"FINISHED"} and bpy.data.objects.get("Parede_HB_Rebaixada") is None and not wall.hide_viewport,
    )


# 6. Colisão global no cabeçalho
def collision_block():
    from caffmob_draw.ui import header_collision

    s = SCENE.btm_settings
    s.collision_global = False
    s.block_penetration = False
    r = bpy.ops.caffmob.toggle_global_collision()
    check(
        "colisão: alterna ON nos dois campos",
        r == {"FINISHED"} and s.collision_global and s.block_penetration,
        (s.collision_global, s.block_penetration),
    )

    class Row:
        def __init__(self, out):
            self.out = out

        def operator(self, idname, **kw):
            self.out.append((idname, kw.get("text")))

    class L:
        def __init__(self):
            self.out = []

        def row(self, **kw):
            return Row(self.out)

    lay = L()
    header_collision.draw_header_collision(SimpleNamespace(layout=lay), bpy.context)
    check(
        "colisão: botão no cabeçalho com rótulo ON",
        any(op == "caffmob.toggle_global_collision" for op, _t in lay.out),
        lay.out,
    )
    bpy.ops.caffmob.toggle_global_collision()
    check("colisão: alterna OFF", not s.collision_global and not s.block_penetration)


# 7. Texturas perdidas
def texture_block():
    from caffmob_draw.texture_library import sync_missing

    src = bpy.data.images.new("Textura_teste_021", 8, 8)
    src["caffmob_texture_id"] = "teste-021"
    src.filepath = "//nao_existe_teste_021.png"
    missing, present = sync_missing.find_missing_addon_textures()
    ids = [m["id"] for m in missing]
    check("texturas: detector acha a textura perdida", "teste-021" in ids, ids)
    sync_missing.cancel_sync()
    check("texturas: cancelar deixa o estado limpo", sync_missing._active_sync["running"] is False)
    bpy.data.images.remove(src)
    r = bpy.ops.caffmob.sync_missing_textures()
    check("texturas: operador sem perdidas finaliza", r == {"FINISHED"}, r)


# 8. Stick: desgrudar sem reacoplar
def stick_block():
    from caffmob_draw.stick import link

    clean()
    wall = cube("Parede_stick", size=(2.0, 0.1, 2.6), loc=(0, 0, 1.3))
    wall["IS_WALL_BP"] = True
    item = cube("Armario_stick", size=(0.6, 0.35, 0.8), loc=(0, -1, 0.8))
    select(item)
    try:
        host, face = link.stick(item, wall, Vector((0, 0, 1.0)), Vector((0, -1, 0)))
        check("stick: gruda na face", host == wall and item.btm_stick.is_stuck and item.parent == wall, (host, face))
        antes = item.matrix_world.copy()
        ok = link.release(item)
        check(
            "stick: desgruda mantendo a posição",
            ok and not item.btm_stick.is_stuck and (item.matrix_world.translation - antes.translation).length < 1e-5,
        )
        check(
            "stick: grava released_host_name",
            item.btm_stick.released_host_name == wall.name,
            item.btm_stick.released_host_name,
        )
    except Exception:
        check("stick: grudar/desgrudar na API real", False, traceback.format_exc(limit=3))


# 9. Criar armário abre o construtor v2
def library_block():
    clean()
    try:
        r = bpy.ops.caffmob.library_create_cabinet("INVOKE_DEFAULT")
        root = bpy.context.view_layer.objects.active
        check(
            "biblioteca: Criar Armário abre o construtor v2",
            "FINISHED" in r and root is not None and hasattr(root, "btm_armario"),
            (r, getattr(root, "name", None)),
        )
    except Exception:
        check("biblioteca: Criar Armário abre o construtor v2", False, traceback.format_exc(limit=3))


# 10. Painel: superfície do mockup
def panel_block():
    from caffmob_draw.armario_v2 import panel

    clean()
    bpy.ops.caffmob.cabinet_editor()
    root = bpy.context.view_layer.objects.active
    bpy.ops.caffmob.armario_v2_montar_caixa()
    select(root)

    class L:
        def __init__(self):
            self.ops, self.labels, self.enums, self.props = [], [], [], []

        def box(self):
            return self

        def row(self, *a, **kw):
            return self

        def column(self, *a, **kw):
            return self

        def grid_flow(self, *a, **kw):
            return self

        def separator(self):
            pass

        def scale_y(self, *a):
            pass

        def operator(self, idname, **kw):
            self.ops.append((idname, kw.get("text")))

        def label(self, text="", **kw):
            self.labels.append(text)

        def prop(self, owner, name, **kw):
            self.props.append(name)

        def prop_enum(self, owner, name, value, **kw):
            self.enums.append(value)

    lay = L()
    ctx = SimpleNamespace(scene=SCENE, active_object=root)
    panel.draw_painel(lay, ctx)
    check("painel: cabeçalho com título do mockup", "Construtor de Armários" in lay.labels, lay.labels[:12])
    check(
        "painel: status de chapa no cabeçalho",
        any("Chapa" in t or "Contrato" in t for t in lay.labels),
        lay.labels[:12],
    )
    check(
        "painel: barra de ferramentas (Montar/Limpar/Gerar)",
        {"caffmob.armario_v2_montar_caixa", "caffmob.armario_v2_limpar", "caffmob.armario_v2_gerar"}
        <= {o for o, _t in lay.ops},
        lay.ops,
    )
    check(
        "painel: rodapé Aplicar/Cancelar",
        {"caffmob.armario_v2_aplicar", "caffmob.armario_v2_cancelar"} <= {o for o, _t in lay.ops},
        lay.ops,
    )
    check(
        "painel: sete abas do mockup",
        lay.enums[:7] == ["ESTRUTURA", "DIVISOES", "GAVETAS", "INTERNOS", "PORTAS", "DESLIZANTES", "FUNDOS"],
        lay.enums[:9],
    )
    check(
        "painel: subcabeçalho com dimensões/montagem/vão",
        any("Armário:" in t for t in lay.labels)
        and any("Montagem:" in t for t in lay.labels)
        and any("Vão ativo:" in t for t in lay.labels),
        lay.labels,
    )
    check("painel: acesso rápido ao Plano de Corte", any(o == "caffmob.opcut_generate" for o, _t in lay.ops), lay.ops)


# 11. Painéis OpCut e Texturas: desenho real com layout falso
def panels_extra_block():
    from caffmob_draw.cutting import ops_opcut
    from caffmob_draw.texture_library import ops_sync_missing

    class Op:
        def __init__(self):
            self.delta = 0
            self.export_format = ""

    class L:
        def __init__(self):
            self.ops, self.labels, self.props = [], [], []

        def box(self):
            return self

        def row(self, *a, **kw):
            return self

        def label(self, text="", **kw):
            self.labels.append(text)

        def prop(self, owner, name, **kw):
            self.props.append(name)

        def operator(self, idname, **kw):
            self.ops.append(idname)
            return Op()

        def template_ID_preview(self, *a, **kw):
            pass

    bpy.ops.caffmob.opcut_generate()
    lay = L()
    ops_opcut.BTM_PT_OpCutPanel.draw(SimpleNamespace(layout=lay), bpy.context)
    check(
        "painel OpCut: motor, agrupamento e gerar",
        {"cutting_engine", "cutting_group_by_module"} <= set(lay.props) and "caffmob.opcut_generate" in lay.ops,
        (lay.props, lay.ops),
    )
    check(
        "painel OpCut: lista por módulo e navegação de chapas",
        any("Lista de Peças" in t for t in lay.labels) and "caffmob.opcut_preview_step" in lay.ops,
        (lay.labels, lay.ops),
    )
    check(
        "painel OpCut: exportação HTML/SVG/PDF",
        [o for o in lay.ops if o == "caffmob.opcut_export"].__len__() == 3,
        lay.ops,
    )
    lay2 = L()
    ops_sync_missing.BTM_PT_SyncMissingTextures.draw(SimpleNamespace(layout=lay2), bpy.context)
    check("painel Texturas: botão Sincronizar Texturas Perdidas", "caffmob.sync_missing_textures" in lay2.ops, lay2.ops)


# 12. RF-08: padrões rápidos do projeto alimentam o Editor de Paredes
def project_defaults_block():
    from caffmob_draw.ui import sidebar_build
    from caffmob_draw.walls2d import ops_editor

    clean()
    ambiente = SCENE.get("caffmob_ambiente")
    if ambiente is not None:
        del SCENE["caffmob_ambiente"]
    hb = SCENE.home_builder
    settings = SCENE.btm_settings
    antes = (hb.ceiling_height, settings.default_wall_thickness)
    hb.ceiling_height = 2.85
    settings.default_wall_thickness = 0.18

    class L:
        def __init__(self):
            self.props, self.labels = [], []

        def box(self):
            return self

        def column(self, *a, **kw):
            return self

        def row(self, *a, **kw):
            return self

        def prop(self, owner, name, **kw):
            self.props.append(name)

        def label(self, text="", **kw):
            self.labels.append(text)

    lay = L()
    sidebar_build.draw_project_defaults(lay, SimpleNamespace(scene=SCENE))
    check(
        "RF-08: aba Ferramentas expõe pé-direito e espessura padrão",
        {"ceiling_height", "default_wall_thickness"} <= set(lay.props),
        lay.props,
    )

    original = ops_editor.window.open_editor
    poll = ops_editor.BTM_OT_WallEditor.poll

    def sem_janela(context):
        raise RuntimeError("ensaio headless: sem janela do Blender")

    def sem_gui(cls, context):
        return True

    ops_editor.window.open_editor = sem_janela
    ops_editor.BTM_OT_WallEditor.poll = classmethod(sem_gui)
    try:
        try:
            resultado = bpy.ops.caffmob.wall_editor()
        except RuntimeError as exc:
            resultado = {"CANCELLED"} if "sem janela" in str(exc) else {"ERRO", str(exc)}
    finally:
        ops_editor.window.open_editor = original
        ops_editor.BTM_OT_WallEditor.poll = poll
    wm = bpy.context.window_manager.btm_wall_editor
    check(
        "RF-08: Editor de Paredes nasce com pé-direito e espessura do projeto",
        resultado == {"CANCELLED"} and abs(wm.new_height - 2.85) < 1e-6 and abs(wm.new_thickness - 0.18) < 1e-6,
        (resultado, wm.new_height, wm.new_thickness),
    )

    hb.ceiling_height, settings.default_wall_thickness = antes
    if ambiente is not None:
        SCENE["caffmob_ambiente"] = ambiente


def run():
    global result
    section(project_defaults_block)
    section(layers_block)
    section(floor_block)
    section(opcut_block)
    section(drawer_block)
    section(lowered_block)
    section(collision_block)
    section(texture_block)
    section(stick_block)
    section(library_block)
    section(panel_block)
    section(panels_extra_block)
    result = {"pass": len(PASS), "fail": len(FAIL), "failures": FAIL, "passed": PASS}
    print(json.dumps({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL}, ensure_ascii=False))


run()
