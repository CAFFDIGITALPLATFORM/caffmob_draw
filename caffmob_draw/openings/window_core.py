"""Janela paramétrica da parede (feature 010/078, T013/T016; RN-10, D-14). Python puro, sem `bpy`.

Suporta os 20 modelos de janela do catálogo (`MODELOS_DE_JANELA`: 5 de correr, 5 de abrir, 5 basculantes/maxim-ar e
5 fixas/venezianas) nos 3 acabamentos (`madeira`, `aluminio`, `blindex`), mantendo compatibilidade integral com a
janela de correr 2 folhas de alumínio original da 010.
"""

from .door_core import ALU, FRAME, FRAME_HW, GLASS, LEAF, LEAF_HW, METAL, WOOD, Part, resolve_finish

STONE = 'STONE'
PROFILE = 0.040                # marco
SASH = 0.035                   # perfil da folha
SASH_DEPTH = 0.030
GLASS_T = 0.004
OVERLAP = 0.050
SILL_T = 0.020
SILL_OUT = 0.030

SLIDING_WINDOW_MODELS = (
    'janela_correr_2f',
    'janela_correr_3f',
    'janela_correr_4f',
    'janela_correr_veneziana',
    'janela_correr_bandeira',
)
CASEMENT_WINDOW_MODELS = (
    'janela_abrir_1f',
    'janela_abrir_2f',
    'janela_abrir_bandeira',
    'janela_abrir_veneziana',
    'janela_abrir_camarao',
)
AWNING_WINDOW_MODELS = (
    'janela_maximar_1m',
    'janela_maximar_2m',
    'janela_maximar_fixo',
    'janela_basculante',
    'janela_pivotante',
)
FIXED_WINDOW_MODELS = (
    'janela_fixa',
    'janela_panoramica',
    'janela_bay',
    'janela_veneziana_fixa',
    'janela_vitro',
)
WINDOW_MODELS = (
    SLIDING_WINDOW_MODELS
    + CASEMENT_WINDOW_MODELS
    + AWNING_WINDOW_MODELS
    + FIXED_WINDOW_MODELS
)


def is_sliding_window(model='janela_correr_2f'):
    return model in SLIDING_WINDOW_MODELS


def _box(parts, role, name, lo, hi, material, leaf=None, bevel=0.0008):
    center = tuple((lo[i] + hi[i]) / 2 for i in range(3))
    size = tuple(max(0.001, hi[i] - lo[i]) for i in range(3))
    parts.append(Part(role, name, 'BOX', center, size, material, bevel, leaf))


def travel(width, model='janela_correr_2f'):
    """Curso de cada folha: do lugar fechado até o batente do marco do outro lado."""
    inner = max(0.2, width - 2 * PROFILE)
    if model == 'janela_correr_3f':
        return round(inner / 3, 6)
    if model == 'janela_correr_4f':
        return round(inner / 4, 6)
    return round(inner - (inner / 2 + OVERLAP / 2), 6)


def _add_sash_frame(parts, x0, x1, ya, yb, z0, z1, prof_mat, finish, leaf, louvers=False, grid=False):
    y_mid = (ya + yb) / 2
    if finish == GLASS and not louvers:
        _box(parts, LEAF, "Vidro", (x0, y_mid - 0.004, z0), (x1, y_mid + 0.004, z1), GLASS, leaf, 0.0)
        _box(parts, LEAF, "Folha_perfil_base", (x0, ya, z0), (x1, yb, z0 + 0.018), ALU, leaf)
        return
    sash = min(SASH, max(0.018, (x1 - x0) * 0.16, (z1 - z0) * 0.16))
    _box(parts, LEAF, "Folha_montante", (x0, ya, z0), (x0 + sash, yb, z1), prof_mat, leaf)
    _box(parts, LEAF, "Folha_montante", (x1 - sash, ya, z0), (x1, yb, z1), prof_mat, leaf)
    _box(parts, LEAF, "Folha_travessa", (x0 + sash, ya, z0), (x1 - sash, yb, z0 + sash), prof_mat, leaf)
    _box(parts, LEAF, "Folha_travessa", (x0 + sash, ya, z1 - sash), (x1 - sash, yb, z1), prof_mat, leaf)
    if louvers:
        louver_mat = GLASS if finish == GLASS else prof_mat
        inner_z0, inner_z1 = z0 + sash, z1 - sash
        count = max(4, int((inner_z1 - inner_z0) / 0.055))
        step = (inner_z1 - inner_z0) / count
        for idx in range(count):
            zs = inner_z0 + (idx + 0.2) * step
            _box(parts, LEAF, f"Palheta_veneziana_{idx}", (x0 + sash, ya + 0.004, zs),
                 (x1 - sash, yb - 0.004, zs + step * 0.65), louver_mat, leaf, 0.0005)
    else:
        _box(parts, LEAF, "Vidro", (x0 + sash - 0.006, y_mid - GLASS_T / 2, z0 + sash - 0.006),
             (x1 - sash + 0.006, y_mid + GLASS_T / 2, z1 - sash + 0.006), GLASS, leaf, 0.0)
        if grid:
            for frac in (1 / 3, 2 / 3):
                xg = x0 + sash + (x1 - x0 - 2 * sash) * frac
                _box(parts, LEAF, "Grade_vertical", (xg - 0.006, y_mid - 0.006, z0 + sash),
                     (xg + 0.006, y_mid + 0.006, z1 - sash), prof_mat, leaf)
            zg = (z0 + z1) / 2
            _box(parts, LEAF, "Grade_horizontal", (x0 + sash, y_mid - 0.006, zg - 0.006),
                 (x1 - sash, y_mid + 0.006, zg + 0.006), prof_mat, leaf)


def _add_perimeter_and_sill(parts, w, h, wall, prof_mat):
    P = PROFILE
    _box(parts, FRAME, "Marco_esquerdo", (0, 0, 0), (P, wall, h), prof_mat)
    _box(parts, FRAME, "Marco_direito", (w - P, 0, 0), (w, wall, h), prof_mat)
    _box(parts, FRAME, "Marco_inferior", (P, 0, 0), (w - P, wall, P), prof_mat)
    _box(parts, FRAME, "Marco_superior", (P, 0, h - P), (w - P, wall, h), prof_mat)
    face = wall
    for name, lo, hi in (("Guarnicao_esquerda", (-0.05, face, 0), (0, face + 0.012, h + 0.05)),
                         ("Guarnicao_direita", (w, face, 0), (w + 0.05, face + 0.012, h + 0.05)),
                         ("Guarnicao_superior", (-0.05, face, h), (w + 0.05, face + 0.012, h + 0.05))):
        _box(parts, FRAME, name, lo, hi, prof_mat)
    _box(parts, FRAME, "Peitoril", (-SILL_OUT, -SILL_OUT, -SILL_T), (w + SILL_OUT, wall + SILL_OUT, 0.0), STONE,
         bevel=0.002)
    _box(parts, FRAME, "Peitoril_pingadeira", (-SILL_OUT + 0.01, -SILL_OUT + 0.008, -SILL_T - 0.004),
         (w + SILL_OUT - 0.01, -SILL_OUT + 0.014, -SILL_T), STONE, bevel=0.0)


def window_parts(width, height, wall, model='janela_correr_2f', material='aluminio'):
    """Peças da janela no furo `width` × `height` de uma parede `wall`."""
    finish = resolve_finish(material)
    prof_mat = WOOD if finish == WOOD else ALU
    hw_mat = ALU if prof_mat == ALU else METAL
    w, h, P = width, height, PROFILE
    parts = []
    _add_perimeter_and_sill(parts, w, h, wall, prof_mat)
    mid = wall / 2
    inner = max(0.12, w - 2 * P)
    z0, z1 = P + 0.005, h - P - 0.005

    # Transom (bandeira superior ou fixo inferior)
    if model in ('janela_correr_bandeira', 'janela_abrir_bandeira'):
        zb = P + (h - 2 * P) * 0.72
        _box(parts, FRAME, "Travessa_bandeira", (P, 0, zb - P / 2), (w - P, wall, zb + P / 2), prof_mat)
        _box(parts, FRAME, "Vidro_bandeira", (P + 0.006, mid - GLASS_T / 2, zb + P / 2),
             (w - P - 0.006, mid + GLASS_T / 2, h - P), GLASS, None, 0.0)
        z1 = zb - P / 2 - 0.004
    elif model == 'janela_maximar_fixo':
        zf = P + (h - 2 * P) * 0.35
        _box(parts, FRAME, "Travessa_fixo", (P, 0, zf - P / 2), (w - P, wall, zf + P / 2), prof_mat)
        _box(parts, FRAME, "Vidro_fixo", (P + 0.006, mid - GLASS_T / 2, P),
             (w - P - 0.006, mid + GLASS_T / 2, zf - P / 2), GLASS, None, 0.0)
        z0 = zf + P / 2 + 0.004

    if model in ('janela_correr_2f', 'janela_correr_bandeira') and finish == ALU and model == 'janela_correr_2f':
        # Mantém a geometria exata da 010 para janela_correr_2f em alumínio
        tracks = (mid - 0.020, mid + 0.020)
        for name, tz0, tz1 in (("Trilho_inferior", P, P + 0.008), ("Trilho_superior", h - P - 0.008, h - P)):
            for y in tracks:
                _box(parts, FRAME, name, (P, y - 0.0015, tz0), (w - P, y + 0.0015, tz1), ALU)
        sash_w = inner / 2 + OVERLAP / 2
        for leaf, (x0, y) in enumerate(((P, tracks[0]), (w - P - sash_w, tracks[1]))):
            x1 = x0 + sash_w
            ya, yb = y - SASH_DEPTH / 2, y + SASH_DEPTH / 2
            _box(parts, LEAF, "Folha_montante", (x0, ya, z0), (x0 + SASH, yb, z1), ALU, leaf)
            _box(parts, LEAF, "Folha_montante", (x1 - SASH, ya, z0), (x1, yb, z1), ALU, leaf)
            _box(parts, LEAF, "Folha_travessa", (x0 + SASH, ya, z0), (x1 - SASH, yb, z0 + SASH), ALU, leaf)
            _box(parts, LEAF, "Folha_travessa", (x0 + SASH, ya, z1 - SASH), (x1 - SASH, yb, z1), ALU, leaf)
            _box(parts, LEAF, "Vidro", (x0 + SASH - 0.006, y - GLASS_T / 2, z0 + SASH - 0.006),
                 (x1 - SASH + 0.006, y + GLASS_T / 2, z1 - SASH + 0.006), GLASS, leaf, 0.0)
            grip_x = x0 + SASH / 2 if leaf == 0 else x1 - SASH / 2
            zc = (z0 + z1) / 2
            _box(parts, LEAF_HW, "Puxador_concha", (grip_x - 0.008, ya - 0.006, zc - 0.06),
                 (grip_x + 0.008, ya, zc + 0.06), ALU, leaf, 0.003)
        return parts

    if model in SLIDING_WINDOW_MODELS:
        tracks = (mid - 0.020, mid + 0.020) if model != 'janela_correr_3f' else (mid - 0.024, mid, mid + 0.024)
        for name, tz0, tz1 in (("Trilho_inferior", P, P + 0.008), ("Trilho_superior", z1, z1 + 0.008)):
            for y in tracks:
                _box(parts, FRAME, name, (P, y - 0.0015, tz0), (w - P, y + 0.0015, tz1), prof_mat)
        if model == 'janela_correr_3f':
            sash_w = inner / 3 + OVERLAP / 2
            coords = ((P, tracks[0], False), (P + (inner - sash_w) / 2, tracks[1], False), (w - P - sash_w, tracks[2], False))
        elif model == 'janela_correr_4f':
            sash_w = inner / 4 + OVERLAP / 2
            coords = (
                (P, tracks[0], False),
                (P + inner * 0.24, tracks[1], False),
                (P + inner * 0.50, tracks[1], False),
                (w - P - sash_w, tracks[0], False),
            )
        elif model == 'janela_correr_veneziana':
            sash_w = inner / 2 + OVERLAP / 2
            coords = ((P, tracks[0], True), (w - P - sash_w, tracks[0], True), (P + inner * 0.24, tracks[1], False))
        else:
            sash_w = inner / 2 + OVERLAP / 2
            coords = ((P, tracks[0], False), (w - P - sash_w, tracks[1], False))
        zc = (z0 + z1) / 2
        for leaf, (x0, y, is_louver) in enumerate(coords):
            x1 = x0 + sash_w
            ya, yb = y - SASH_DEPTH / 2, y + SASH_DEPTH / 2
            _add_sash_frame(parts, x0, x1, ya, yb, z0, z1, prof_mat, finish, leaf, louvers=is_louver)
            grip_x = x0 + SASH / 2 if leaf == 0 else x1 - SASH / 2
            _box(parts, LEAF_HW, "Puxador_concha", (grip_x - 0.008, ya - 0.006, zc - 0.06),
                 (grip_x + 0.008, ya, zc + 0.06), hw_mat, leaf, 0.003)
    elif model in CASEMENT_WINDOW_MODELS:
        ya, yb = mid - SASH_DEPTH / 2, mid + SASH_DEPTH / 2
        zc = (z0 + z1) / 2
        n_leaves = 1 if model == 'janela_abrir_1f' else (4 if model == 'janela_abrir_camarao' else 2)
        louvers = model == 'janela_abrir_veneziana'
        leaf_w = inner / n_leaves
        for leaf in range(n_leaves):
            x0 = P + leaf * leaf_w
            x1 = x0 + leaf_w
            _add_sash_frame(parts, x0, x1, ya, yb, z0, z1, prof_mat, finish, leaf, louvers=louvers)
            hx = x0 + 0.006 if leaf % 2 == 0 else x1 - 0.006
            for zh in (z0 + 0.12, z1 - 0.12):
                _box(parts, LEAF_HW, "Dobradica_janela", (hx - 0.004, ya - 0.004, zh - 0.025),
                     (hx + 0.004, ya + 0.004, zh + 0.025), hw_mat, leaf)
            cx = x1 - 0.018 if leaf % 2 == 0 else x0 + 0.018
            _box(parts, LEAF_HW, "Cremona", (cx - 0.008, ya - 0.018, zc - 0.055),
                 (cx + 0.008, ya, zc + 0.055), hw_mat, leaf, 0.002)
    elif model in AWNING_WINDOW_MODELS:
        ya, yb = mid - SASH_DEPTH / 2, mid + SASH_DEPTH / 2
        if model == 'janela_maximar_2m':
            xm = w / 2
            _box(parts, FRAME, "Montante_central", (xm - P / 2, 0, P), (xm + P / 2, wall, h - P), prof_mat)
            spans = ((P, xm - P / 2), (xm + P / 2, w - P))
        else:
            spans = ((P, w - P),)
        for leaf, (x0, x1) in enumerate(spans):
            _add_sash_frame(parts, x0, x1, ya, yb, z0, z1, prof_mat, finish, leaf)
            zc = (z0 + z1) / 2
            xc = (x0 + x1) / 2
            if model == 'janela_basculante':
                _box(parts, FRAME_HW, "Pivo_basculante", (x0 - 0.004, mid - 0.008, zc - 0.012),
                     (x0 + 0.006, mid + 0.008, zc + 0.012), hw_mat)
                _box(parts, LEAF_HW, "Alavanca_basculante", (x1 - 0.016, ya - 0.022, z0 + 0.08),
                     (x1 - 0.004, ya, z0 + 0.22), hw_mat, leaf)
            elif model == 'janela_pivotante':
                for zp in (z0 - 0.004, z1 + 0.004):
                    _box(parts, FRAME_HW, "Pivo_vertical", (x0 + (x1 - x0) * 0.22 - 0.010, mid - 0.010, zp - 0.005),
                         (x0 + (x1 - x0) * 0.22 + 0.010, mid + 0.010, zp + 0.005), hw_mat)
                _box(parts, LEAF_HW, "Puxador_pivotante", (x1 - 0.03, ya - 0.024, zc - 0.12),
                     (x1 - 0.01, ya, zc + 0.12), hw_mat, leaf)
            else:
                for sx in (x0 + 0.01, x1 - 0.01):
                    _box(parts, FRAME_HW, "Braco_maximar", (sx - 0.004, mid - 0.006, zc),
                         (sx + 0.004, mid + 0.006, z1 - 0.04), hw_mat)
                _box(parts, LEAF_HW, "Fecho_maximar", (xc - 0.025, ya - 0.016, z0 + 0.012),
                     (xc + 0.025, ya, z0 + 0.032), hw_mat, leaf)
    else:
        # FIXED_WINDOW_MODELS: janela_fixa, janela_panoramica, janela_bay, janela_veneziana_fixa, janela_vitro
        ya, yb = mid - SASH_DEPTH / 2, mid + SASH_DEPTH / 2
        if model == 'janela_panoramica':
            xm = w / 2
            _box(parts, FRAME, "Montante_panoramico", (xm - 0.014, mid - 0.018, P), (xm + 0.014, mid + 0.018, h - P),
                 prof_mat)
            _add_sash_frame(parts, P, xm - 0.014, ya, yb, z0, z1, prof_mat, finish, 0)
            _add_sash_frame(parts, xm + 0.014, w - P, ya, yb, z0, z1, prof_mat, finish, 1)
        elif model == 'janela_bay':
            x_left = P + inner * 0.22
            x_right = w - P - inner * 0.22
            _box(parts, FRAME, "Montante_bay_esq", (x_left - 0.015, -0.04, P), (x_left + 0.015, wall, h - P), prof_mat)
            _box(parts, FRAME, "Montante_bay_dir", (x_right - 0.015, -0.04, P), (x_right + 0.015, wall, h - P), prof_mat)
            _add_sash_frame(parts, P, x_left - 0.015, ya - 0.02, yb - 0.02, z0, z1, prof_mat, finish, 0)
            _add_sash_frame(parts, x_left + 0.015, x_right - 0.015, ya - 0.045, yb - 0.045, z0, z1, prof_mat, finish, 1)
            _add_sash_frame(parts, x_right + 0.015, w - P, ya - 0.02, yb - 0.02, z0, z1, prof_mat, finish, 2)
        elif model == 'janela_veneziana_fixa':
            _add_sash_frame(parts, P, w - P, ya, yb, z0, z1, prof_mat, finish, 0, louvers=True)
        elif model == 'janela_vitro':
            _add_sash_frame(parts, P, w - P, ya, yb, z0, z1, prof_mat, finish, 0, grid=True)
        else:
            _add_sash_frame(parts, P, w - P, ya, yb, z0, z1, prof_mat, finish, 0)
            _box(parts, LEAF, "Baguete_inferior", (P, ya - 0.004, z0), (w - P, ya, z0 + 0.014), prof_mat, 0)

    return parts
