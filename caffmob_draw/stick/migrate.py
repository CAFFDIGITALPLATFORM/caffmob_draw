"""Migração dos módulos que já estão na parede (feature 004, T029; D-08, RN-10, RF-19).

Ao abrir um arquivo, cada módulo raiz filho de uma parede (`GeoNodeWall`) sem vínculo vira elemento filho dela, na face
em que está: frente (`NEG_Y`, Y local ≈ 0, sem giro) ou trás (`POS_Y`, giro de 180°), pela mesma regra das cotas
(`measure/scene_cotas._on_front_side`). `distance` guarda o recuo atual (negativo quando o produto entra na parede).
Nada se move. Idempotente: módulos já vinculados são pulados e a cena fica marcada com `btm_settings.stick_migrated`.
"""

import math

from ..selection import classify
from . import link


def wall_of(root):
    parent = root.parent
    return parent if parent is not None and parent.get('IS_WALL_BP') else None


def wall_side(root, wall):
    from .. import hb_types
    try:
        thickness = hb_types.GeoNodeWall(wall).get_input('Thickness')
    except Exception:
        thickness = 0.0
    rz = root.rotation_euler.z % (2 * math.pi)
    front = min(rz, 2 * math.pi - rz) < 0.01 and root.location.y < 0.5 * thickness
    return 'NEG_Y' if front else 'POS_Y'


def run(scene):
    """Devolve quantos módulos ganharam o vínculo."""
    if scene is None:
        return 0
    count = 0
    for obj in scene.objects:
        st = getattr(obj, 'btm_stick', None)
        if st is None or st.is_stuck or st.opt_out:
            continue
        info = classify.classify(obj)
        if info is None or info.kind != classify.MODULE or info.root is not obj:
            continue
        wall = wall_of(obj)
        if wall is None:
            continue
        link.link_in_place(obj, wall, wall_side(obj, wall))
        count += 1
    settings = getattr(scene, 'btm_settings', None)
    if settings is not None:
        settings.stick_migrated = True
    return count
