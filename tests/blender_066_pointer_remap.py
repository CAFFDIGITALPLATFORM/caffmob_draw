"""Protótipo do risco R8 da feature 066 (T004): `PointerProperty` dentro de PropertyGroup é remapeado?

Rodar: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_pointer_remap.py

Mede três caminhos com um PropertyGroup de teste (`Object.t066_link.target`):
1. Shift+D (`object.duplicate`) com dono e alvo selecionados juntos: a cópia do dono aponta para a cópia do alvo?
2. Shift+D só do dono: a cópia continua apontando para o alvo original?
3. Append de dono e alvo de outro .blend: o dono anexado aponta para o alvo anexado, não para um objeto da cena?
O resultado define se o uid basta como verdade de identidade ou se o vínculo precisa ser reconstruído (roadmap D-02).
"""
import tempfile
from pathlib import Path

import bpy

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


class T066Link(bpy.types.PropertyGroup):
    target: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore


def _pair(prefix):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    owner = bpy.context.object
    owner.name = f"{prefix}Dono"
    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    target = bpy.context.object
    target.name = f"{prefix}Alvo"
    owner.t066_link.target = target
    return owner, target


def _select(*objs):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def main():
    bpy.utils.register_class(T066Link)
    bpy.types.Object.t066_link = bpy.props.PointerProperty(type=T066Link)
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        owner, target = _pair("A")
        _select(owner, target)
        bpy.ops.object.duplicate()
        copies = {o.name: o for o in bpy.context.selected_objects}
        owner2 = next(o for o in copies.values() if o.name.startswith("ADono"))
        target2 = next(o for o in copies.values() if o.name.startswith("AAlvo"))
        check("Shift+D do par: a cópia do dono aponta para a cópia do alvo",
              owner2.t066_link.target == target2, f"{owner2.name} -> {owner2.t066_link.target.name}")

        _select(owner)
        bpy.ops.object.duplicate()
        lone = bpy.context.object
        check("Shift+D só do dono: a cópia aponta para o alvo original",
              lone.t066_link.target == target, f"{lone.name} -> {lone.t066_link.target.name}")

        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "fonte.blend")
            bpy.ops.wm.read_factory_settings(use_empty=True)
            _pair("B")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.read_factory_settings(use_empty=True)
            _pair("B")          # homônimos na cena de destino, para pegar resolução por nome
            local_owner = bpy.data.objects["BDono"]
            with bpy.data.libraries.load(path, link=False) as (src, dst):
                dst.objects = ["BDono", "BAlvo"]
            for obj in dst.objects:
                bpy.context.scene.collection.objects.link(obj)
            appended_owner = next(o for o in dst.objects if o.name.startswith("BDono"))
            appended_target = next(o for o in dst.objects if o.name.startswith("BAlvo"))
            check("append: o dono anexado aponta para o alvo anexado",
                  appended_owner.t066_link.target == appended_target,
                  f"{appended_owner.name} -> {appended_owner.t066_link.target.name}")
            check("append: o dono local continua apontando para o alvo local",
                  local_owner.t066_link.target.name == "BAlvo", local_owner.t066_link.target.name)
    finally:
        del bpy.types.Object.t066_link
        bpy.utils.unregister_class(T066Link)
    print(f"blender_066_pointer_remap: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    if FAILURES:
        raise SystemExit(1)


main()
