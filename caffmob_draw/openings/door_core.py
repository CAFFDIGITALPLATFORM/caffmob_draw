"""Porta paramétrica da parede (feature 010/078, T012/T015; RN-01, RN-02, D-07). Python puro, sem `bpy`.

Suporta os 10 modelos de porta do catálogo (`MODELOS_DE_PORTA`: 5 de giro e 5 de correr) nos 3 acabamentos
(`madeira`, `aluminio`, `blindex`), mantendo compatibilidade integral com a porta almofadada original da 010.
"""

from dataclasses import dataclass

FRAME, FRAME_HW, LEAF, LEAF_HW = 'FRAME', 'FRAME_HW', 'LEAF', 'LEAF_HW'
WOOD, METAL, RUBBER, SLOT, BRASS, ALU, GLASS = 'WOOD', 'METAL', 'RUBBER', 'SLOT', 'BRASS', 'ALU', 'GLASS'
LEAF_T = 0.040                 # espessura da folha
FLOOR_GAP = 0.008              # folga no piso
MARCO = 0.046                  # largura do marco
GAP = 0.003                    # folga lateral entre folha e marco
SIDE = MARCO + GAP             # da borda do furo à folha
TOP = 0.059                    # da folha ao topo do furo (folga, batente e marco superior)
CENTER_GAP = 0.003             # folga entre as folhas da porta dupla
HANDLE_Z = 1.02

SWING_MODELS = (
    'porta_giro_lisa',
    'porta_giro_almofadada',
    'porta_giro_frisada',
    'porta_giro_visor',
    'porta_giro_dupla',
)
SLIDING_MODELS = (
    'porta_correr_aparente',
    'porta_correr_embutida',
    'porta_correr_2f',
    'porta_correr_4f',
    'porta_correr_camarao',
)
DOOR_MODELS = SWING_MODELS + SLIDING_MODELS

FINISH_MAP = {
    'madeira': WOOD,
    'aluminio': ALU,
    'blindex': GLASS,
}


def resolve_finish(material):
    if material in (WOOD, ALU, GLASS):
        return material
    return FINISH_MAP.get(material or 'madeira', WOOD)


def is_sliding(model='porta_giro_almofadada'):
    return model in ('porta_correr_aparente', 'porta_correr_embutida', 'porta_correr_2f', 'porta_correr_4f')


def is_double_leaf(model='porta_giro_almofadada', double=False):
    return bool(double or model == 'porta_giro_dupla')


def door_travel(hole_w, model='porta_correr_2f'):
    inner = max(0.2, hole_w - 2 * SIDE)
    if model in ('porta_correr_aparente', 'porta_correr_embutida'):
        return round(inner * 0.9, 6)
    if model == 'porta_correr_4f':
        return round(inner * 0.24, 6)
    return round(inner * 0.48, 6)


@dataclass(frozen=True)
class Part:
    role: str
    name: str
    shape: str                 # 'BOX' ou 'CYL_X' / 'CYL_Y' / 'CYL_Z'
    center: tuple
    size: tuple                # BOX: (dx, dy, dz); CYL: (diâmetro, diâmetro, altura) no eixo do cilindro
    material: str = WOOD
    bevel: float = 0.001
    leaf: int = None
    horizontal: bool = False   # veio da madeira na horizontal

    @property
    def lo(self):
        return tuple(self.center[i] - self.size_xyz[i] / 2 for i in range(3))

    @property
    def hi(self):
        return tuple(self.center[i] + self.size_xyz[i] / 2 for i in range(3))

    @property
    def size_xyz(self):
        if self.shape == 'BOX':
            return self.size
        d, _d, h = self.size
        return {'CYL_X': (h, d, d), 'CYL_Y': (d, h, d), 'CYL_Z': (d, d, h)}[self.shape]


def hole_size(width, height, double=False):
    """Furo na parede (largura, altura) para a folha `width` × `height` (cada folha, na dupla)."""
    leaves = 2 * width + CENTER_GAP if double else width
    return round(leaves + 2 * SIDE, 6), round(height + TOP, 6)


def leaf_size(hole_w, hole_h, double=False, model='porta_giro_almofadada'):
    leaves = hole_w - 2 * SIDE
    use_double = is_double_leaf(model, double)
    return round((leaves - CENTER_GAP) / 2 if use_double else leaves, 6), round(hole_h - TOP, 6)


class _Builder:
    """Peças no referencial do gerador (folha de 0 a w em x, centrada em y = 0) e conversão para a caixa."""

    def __init__(self, primary=WOOD):
        self.parts = []
        self.primary = primary

    def box(self, role, name, center, size, material=None, bevel=0.001, leaf=None, horizontal=False):
        mat = self.primary if material is None else material
        self.parts.append(Part(role, name, 'BOX', tuple(center), tuple(size), mat, bevel, leaf, horizontal))

    def cyl(self, role, name, center, radius, depth, axis='Z', material=METAL, leaf=None):
        self.parts.append(Part(role, name, 'CYL_' + axis, tuple(center), (2 * radius, 2 * radius, depth), material,
                               0.00035, leaf))

    def screw_y(self, role, name, x, y, z, leaf=None):
        self.cyl(role, name, (x, y, z), 0.0034, 0.0015, 'Y', leaf=leaf)
        side = -1 if y < 0 else 1
        for size in ((0.0045, 0.0003, 0.0008), (0.0008, 0.0003, 0.0045)):
            self.box(role, name + "_fenda", (x, y + side * 0.00085, z), size, SLOT, 0.0001, leaf)


def _swing_hardware(b, x0, w, h, leaf, hinge_left, lock):
    def X(x):
        return x0 + x if hinge_left else x0 + w - x
    hx = X(0.015)
    knuckle = X(-0.003)
    for z in (0.25, FLOOR_GAP + h / 2 - 0.008, FLOOR_GAP + h - 0.248):
        b.box(LEAF_HW, "Dobradica_folha", (hx, -0.0215, z), (0.032, 0.003, 0.09), METAL, leaf=leaf)
        b.box(FRAME_HW, "Dobradica_marco", (X(-0.019), -0.023, z), (0.032, 0.003, 0.09), METAL)
        for k in range(5):
            role = LEAF_HW if k % 2 == 0 else FRAME_HW
            b.cyl(role, "No_dobradica", (knuckle, -0.025, z - 0.036 + k * 0.018), 0.006, 0.0175,
                  leaf=leaf if role == LEAF_HW else None)
        for dz in (-0.047, 0.047):
            b.cyl(FRAME_HW, "Pino_dobradica", (knuckle, -0.025, z + dz), 0.0064, 0.003)
        for dz in (-0.030, 0.0, 0.030):
            b.screw_y(LEAF_HW, "Parafuso_dobradica", X(0.017), -0.024, z + dz, leaf=leaf)
            b.screw_y(FRAME_HW, "Parafuso_marco", X(-0.021), -0.026, z + dz)
    hx = X(w - 0.064)
    lever = X(w - 0.117)
    for side in (-1, 1):
        y = side * 0.024
        b.cyl(LEAF_HW, "Roseta_macaneta", (hx, y, HANDLE_Z), 0.026, 0.008, 'Y', leaf=leaf)
        b.cyl(LEAF_HW, "Anel_macaneta", (hx, side * 0.029, HANDLE_Z), 0.0215, 0.002, 'Y', leaf=leaf)
        b.cyl(LEAF_HW, "Eixo_macaneta", (hx, side * 0.048, HANDLE_Z), 0.009, 0.038, 'Y', leaf=leaf)
        b.box(LEAF_HW, "Alavanca_macaneta", (lever, side * 0.069, HANDLE_Z), (0.125, 0.020, 0.017), METAL, 0.007,
              leaf)
        if lock:
            b.cyl(LEAF_HW, "Roseta_chave", (hx, y, HANDLE_Z - 0.088), 0.024, 0.008, 'Y', leaf=leaf)
            b.cyl(LEAF_HW, "Cilindro_chave", (hx, side * 0.029, HANDLE_Z - 0.084), 0.009, 0.003, 'Y', BRASS, leaf)
            b.box(LEAF_HW, "Rasgo_chave", (hx, side * 0.031, HANDLE_Z - 0.087), (0.002, 0.001, 0.014), SLOT, 0.0003,
                  leaf)
    if lock:
        edge = X(w + 0.001)
        b.box(LEAF_HW, "Testa_fechadura", (edge, 0, HANDLE_Z - 0.042), (0.002, 0.026, 0.18), METAL, leaf=leaf)
        b.box(LEAF_HW, "Lingueta", (X(w + 0.005), 0, HANDLE_Z), (0.010, 0.014, 0.014), BRASS, 0.002, leaf)
        b.box(FRAME_HW, "Contratesta", (X(w + 0.002), 0, HANDLE_Z), (0.002, 0.034, 0.088), METAL)


def _leaf_body(b, x0, w, h, leaf, hinge_left, model, finish, y_offset=0.0):
    def X(x):
        return x0 + x if hinge_left else x0 + w - x
    zc = FLOOR_GAP + h / 2
    leaf_mat = GLASS if finish == GLASS else finish
    stile_w = min(0.11, max(0.045, w * 0.18))
    if finish == GLASS:
        b.box(LEAF, "Folha_vidro_temperado", (x0 + w / 2, y_offset, zc), (w, 0.010, h), GLASS, bevel=0.0, leaf=leaf)
        b.box(LEAF, "Folha_montante_dobradicas", (X(stile_w / 2), y_offset, zc), (stile_w, 0.012, h), GLASS,
              bevel=0.0, leaf=leaf)
        b.box(LEAF, "Folha_montante_fechadura", (X(w - stile_w / 2), y_offset, zc), (stile_w, 0.012, h), GLASS,
              bevel=0.0, leaf=leaf)
        for z_fit in (FLOOR_GAP + 0.18, FLOOR_GAP + h - 0.18):
            b.box(LEAF_HW, "Ferragem_blindex", (X(0.045), y_offset, z_fit), (0.075, 0.024, 0.045), METAL, leaf=leaf)
    else:
        b.box(LEAF, "Folha_montante_dobradicas", (X(stile_w / 2), y_offset, zc), (stile_w, LEAF_T, h), leaf_mat,
              leaf=leaf)
        b.box(LEAF, "Folha_montante_fechadura", (X(w - stile_w / 2), y_offset, zc), (stile_w, LEAF_T, h), leaf_mat,
              leaf=leaf)
        inner_w = max(0.05, w - 2 * stile_w)
        if model == 'porta_giro_lisa':
            b.box(LEAF, "Folha_painel_liso", (x0 + w / 2, y_offset, zc), (inner_w, LEAF_T, h), leaf_mat, leaf=leaf)
        elif model == 'porta_giro_frisada':
            b.box(LEAF, "Folha_painel_frisado", (x0 + w / 2, y_offset, zc), (inner_w, LEAF_T, h), leaf_mat, leaf=leaf)
            for idx in range(5):
                zf = FLOOR_GAP + h * (0.18 + idx * 0.16)
                for side in (-1, 1):
                    b.box(LEAF, f"Friso_decorativo_{idx}", (x0 + w / 2, y_offset + side * (LEAF_T / 2 + 0.002), zf),
                          (w - 0.08, 0.004, 0.010), METAL if finish == ALU else leaf_mat, bevel=0.001, leaf=leaf,
                          horizontal=True)
        elif model == 'porta_giro_visor':
            visor_w = min(0.18, inner_w * 0.45)
            visor_h = min(1.30, h * 0.62)
            b.box(LEAF, "Folha_travessa_inferior", (x0 + w / 2, y_offset, FLOOR_GAP + (h - visor_h) / 4),
                  (inner_w, LEAF_T, (h - visor_h) / 2), leaf_mat, leaf=leaf, horizontal=True)
            b.box(LEAF, "Folha_travessa_superior", (x0 + w / 2, y_offset, FLOOR_GAP + h - (h - visor_h) / 4),
                  (inner_w, LEAF_T, (h - visor_h) / 2), leaf_mat, leaf=leaf, horizontal=True)
            side_fill = max(0.02, (inner_w - visor_w) / 2)
            b.box(LEAF, "Folha_enchimento_esq", (x0 + stile_w + side_fill / 2, y_offset, zc),
                  (side_fill, LEAF_T, visor_h), leaf_mat, leaf=leaf)
            b.box(LEAF, "Folha_enchimento_dir", (x0 + w - stile_w - side_fill / 2, y_offset, zc),
                  (side_fill, LEAF_T, visor_h), leaf_mat, leaf=leaf)
            b.box(LEAF, "Visor_vidro", (x0 + w / 2, y_offset, zc), (visor_w, 0.008, visor_h), GLASS, bevel=0.0,
                  leaf=leaf)
            for side in (-1, 1):
                b.box(LEAF, "Moldura_visor", (x0 + w / 2, y_offset + side * 0.016, zc),
                      (visor_w + 0.024, 0.008, visor_h + 0.024), ALU if finish == ALU else leaf_mat, leaf=leaf)
        elif model in ('porta_correr_2f', 'porta_correr_4f') and finish == ALU:
            b.box(LEAF, "Folha_travessa_inferior", (x0 + w / 2, y_offset, FLOOR_GAP + 0.055),
                  (inner_w, LEAF_T, 0.11), ALU, leaf=leaf, horizontal=True)
            b.box(LEAF, "Folha_travessa_superior", (x0 + w / 2, y_offset, FLOOR_GAP + h - 0.055),
                  (inner_w, LEAF_T, 0.11), ALU, leaf=leaf, horizontal=True)
            b.box(LEAF, "Painel_vidro", (x0 + w / 2, y_offset, zc),
                  (inner_w + 0.012, 0.006, max(0.2, h - 0.20)), GLASS, bevel=0.0, leaf=leaf)
        else:
            z_low, z_mid, z_top = FLOOR_GAP + 0.07, FLOOR_GAP + h * (0.93 / 2.1), FLOOR_GAP + h - 0.065
            for name, z, height in (('inferior', z_low, 0.14), ('central', z_mid, 0.14), ('superior', z_top, 0.13)):
                b.box(LEAF, "Folha_travessa_" + name, (x0 + w / 2, y_offset, z), (inner_w, LEAF_T, height), leaf_mat,
                      leaf=leaf, horizontal=True)
            for index, (bottom, top) in enumerate(((z_low + 0.07, z_mid - 0.07), (z_mid + 0.07, z_top - 0.065))):
                b.box(LEAF, f"Almofada_{index}", (x0 + w / 2, y_offset, (bottom + top) / 2),
                      (inner_w + 0.002, 0.021, top - bottom + 0.002), leaf_mat, leaf=leaf)
                for side in (-1, 1):
                    y = y_offset + side * 0.014
                    for x in (stile_w + 0.007, w - stile_w - 0.007):
                        b.box(LEAF, "Friso_vertical", (x0 + x, y, (bottom + top) / 2), (0.014, 0.010, top - bottom),
                              leaf_mat, bevel=0.0025, leaf=leaf)
                    for z in (bottom + 0.007, top - 0.007):
                        b.box(LEAF, "Friso_horizontal", (x0 + w / 2, y, z),
                              (max(0.02, inner_w - 0.028), 0.010, 0.014), leaf_mat, bevel=0.0025, leaf=leaf,
                              horizontal=True)
    b.box(LEAF, "Vedacao_inferior", (x0 + w / 2, y_offset, FLOOR_GAP + 0.002), (max(0.04, w - 0.02), 0.021, 0.004),
          RUBBER, leaf=leaf)


def _sliding_pull(b, x_pull, y_offset, leaf, recess=False):
    for side in (-1, 1):
        if recess:
            b.box(LEAF_HW, "Puxador_concha", (x_pull, y_offset + side * 0.021, HANDLE_Z), (0.036, 0.006, 0.14),
                  METAL, bevel=0.002, leaf=leaf)
        else:
            b.box(LEAF_HW, "Puxador_barra", (x_pull, y_offset + side * 0.038, HANDLE_Z), (0.022, 0.028, 0.36),
                  METAL, bevel=0.004, leaf=leaf)


def _frame(b, span, h, wall, leaves, frame_mat=WOOD, model='porta_giro_almofadada'):
    """Marco, batentes, vedações e guarnições em volta das folhas (de 0 a `span` em x, no referencial da folha)."""
    marco_h = h + 0.016
    for x, label in ((-0.026, 'esquerdo'), (span + 0.026, 'direito')):
        b.box(FRAME, "Marco_" + label, (x, 0, marco_h / 2), (MARCO, wall, marco_h), frame_mat)
        if leaves:
            inner = 0.020 if x < 0 else -0.020
            b.box(FRAME, "Batente_" + label, (x + inner, 0.034, marco_h / 2), (0.019, 0.024, marco_h), frame_mat,
                  bevel=0.0015)
            b.box(FRAME, "Vedacao_" + label, (x + (0.023 if x < 0 else -0.023), 0.021, h / 2 + 0.006),
                  (0.010, 0.004, h), RUBBER)
    b.box(FRAME, "Marco_superior", (span / 2, 0, h + 0.036), (span + 0.098, wall, MARCO), frame_mat, horizontal=True)
    if leaves:
        b.box(FRAME, "Batente_superior", (span / 2, 0.034, h + 0.014), (span + 0.006, 0.024, 0.018), frame_mat,
              horizontal=True)
        b.box(FRAME, "Vedacao_superior", (span / 2, 0.021, h + 0.011), (span, 0.004, 0.004), RUBBER)
    face = wall / 2 + 0.0085
    for side in (-1, 1):
        for x in (-0.043, span + 0.043):
            b.box(FRAME, "Guarnicao_vertical", (x, side * face, (h + 0.044) / 2), (0.072, 0.017, h + 0.044),
                  frame_mat, bevel=0.002)
            b.box(FRAME, "Filete_guarnicao", (x, side * (face + 0.011), (h + 0.04) / 2), (0.043, 0.006, h + 0.04),
                  frame_mat, bevel=0.0015)
        b.box(FRAME, "Guarnicao_superior", (span / 2, side * face, h + 0.08), (span + 0.158, 0.017, 0.072),
              frame_mat, bevel=0.002, horizontal=True)
        b.box(FRAME, "Filete_superior", (span / 2, side * (face + 0.011), h + 0.08), (span + 0.154, 0.006, 0.043),
              frame_mat, bevel=0.0015, horizontal=True)
    if model == 'porta_correr_aparente':
        rail_y = -wall / 2 - 0.030
        b.box(FRAME_HW, "Trilho_aparente", (span * 0.75, rail_y, h + 0.055), (span * 1.9, 0.018, 0.045), METAL,
              horizontal=True)
        for rx in (0.12, span - 0.12):
            b.cyl(FRAME_HW, "Roldana_aparente", (rx, rail_y - 0.012, h + 0.055), 0.032, 0.012, 'Y', METAL)
        b.box(FRAME_HW, "Guia_piso", (span + 0.02, rail_y, 0.012), (0.04, 0.03, 0.024), METAL)
    elif model == 'porta_correr_embutida':
        b.box(FRAME, "Trilho_embutido", (span / 2, 0.0, h + 0.012), (span, 0.044, 0.020), ALU, horizontal=True)
        b.box(FRAME, "Marco_bolso", (span - 0.012, 0.0, h / 2), (0.024, 0.052, h), frame_mat)
    elif model in ('porta_correr_2f', 'porta_correr_4f'):
        b.box(FRAME, "Trilho_superior_correr", (span / 2, 0.0, h + 0.008), (span, 0.068, 0.018), ALU, horizontal=True)
        b.box(FRAME, "Trilho_inferior_correr", (span / 2, 0.0, 0.004), (span, 0.068, 0.008), ALU, horizontal=True)
    elif model == 'porta_correr_camarao':
        b.box(FRAME_HW, "Trilho_camarao", (span / 2, 0.0, h + 0.010), (span, 0.036, 0.018), METAL, horizontal=True)


def door_parts(width, height, wall, hinge='LEFT', side='NEG_Y', double=False, open_door=False,
               model='porta_giro_almofadada', material='madeira'):
    """Peças da porta no referencial da caixa. `width` e `height` são da folha (de cada folha, na dupla)."""
    finish = resolve_finish(material)
    frame_mat = ALU if finish in (ALU, GLASS) else WOOD
    b = _Builder(primary=frame_mat)
    use_double = is_double_leaf(model, double)
    if open_door:
        span = width
    elif model == 'porta_correr_aparente':
        span = width
        y_off = -wall / 2 - 0.030
        _leaf_body(b, 0.0, width, height, 0, hinge == 'LEFT', model, finish, y_offset=y_off)
        _sliding_pull(b, width - 0.08 if hinge == 'LEFT' else 0.08, y_off, 0, recess=False)
    elif model == 'porta_correr_embutida':
        span = width
        _leaf_body(b, 0.0, width, height, 0, hinge == 'LEFT', model, finish, y_offset=0.0)
        _sliding_pull(b, width - 0.07 if hinge == 'LEFT' else 0.07, 0.0, 0, recess=True)
    elif model == 'porta_correr_2f':
        span = 2 * width + CENTER_GAP if double else width
        sash_w = span * 0.52
        for idx, (x0, y_off) in enumerate(((0.0, -0.018), (span - sash_w, 0.018))):
            _leaf_body(b, x0, sash_w, height, idx, idx == 0, model, finish, y_offset=y_off)
            pull_x = x0 + 0.07 if idx == 0 else x0 + sash_w - 0.07
            _sliding_pull(b, pull_x, y_off, idx, recess=False)
    elif model == 'porta_correr_4f':
        span = 2 * width + CENTER_GAP if double else width
        sash_w = span * 0.26
        positions = (
            (0.0, -0.018),
            (span * 0.24, 0.018),
            (span * 0.50, 0.018),
            (span - sash_w, -0.018),
        )
        for idx, (x0, y_off) in enumerate(positions):
            _leaf_body(b, x0, sash_w, height, idx, idx < 2, model, finish, y_offset=y_off)
            pull_x = x0 + sash_w - 0.06 if idx == 1 else x0 + 0.06
            _sliding_pull(b, pull_x, y_off, idx, recess=False)
    elif model == 'porta_correr_camarao':
        span = 2 * width + CENTER_GAP if double else width
        panel_w = (span - CENTER_GAP) / 2
        for idx in (0, 1):
            x0 = idx * (panel_w + CENTER_GAP)
            _leaf_body(b, x0, panel_w, height, idx, idx == 0, 'porta_giro_almofadada', finish, y_offset=0.0)
            for z_h in (0.30, height / 2, height - 0.30):
                b.box(LEAF_HW, "Dobradica_central", (panel_w, -0.021, z_h), (0.028, 0.004, 0.075), METAL, leaf=idx)
        _sliding_pull(b, panel_w - 0.05, 0.0, 0, recess=True)
    elif use_double:
        span = 2 * width + CENTER_GAP
        _leaf_body(b, 0.0, width, height, 0, True, model, finish)
        _swing_hardware(b, 0.0, width, height, 0, True, True)
        _leaf_body(b, width + CENTER_GAP, width, height, 1, False, model, finish)
        _swing_hardware(b, width + CENTER_GAP, width, height, 1, False, False)
    else:
        span = width
        _leaf_body(b, 0.0, width, height, 0, hinge == 'LEFT', model, finish)
        _swing_hardware(b, 0.0, width, height, 0, hinge == 'LEFT', True)
    _frame(b, span, height, wall, not open_door, frame_mat=frame_mat, model=model)
    flip = -1 if side == 'POS_Y' else 1
    out = []
    for p in b.parts:
        x, y, z = p.center
        out.append(Part(p.role, p.name, p.shape, (x + SIDE, wall / 2 + y * flip, z), p.size, p.material, p.bevel,
                        p.leaf, p.horizontal))
    return out
