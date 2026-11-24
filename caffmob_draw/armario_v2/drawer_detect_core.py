"""Análise geométrica pura de gaveteiros para conversão (feature 021, T015; RF-12, RF-13, RN-11).

Reconhece as 6 peças padrão de uma gaveta de marcenaria — seja em malha única particionada em ilhas conexas, seja em
objetos separados — e **nunca bloqueia** a conversão quando faltam peças: devolve a lista exata de peças faltantes e
pode sintetizar as caixas faltantes caso o usuário opte por completar automaticamente.

Anatomia padrão:
1. Peças Estruturais (Caixa, referência MDF 15 mm exceto fundo):
   - LATERAL_ESQ, LATERAL_DIR (2 peças)
   - CONTRAFRENTE (1 peça)
   - TRASEIRA (Posterior / Contrafundo, 1 peça)
   - FUNDO (1 peça, referência MDF 6 mm)
2. Peça de Acabamento:
   - FRENTE (1 peça, referência MDF 15 mm ou 18 mm)
3. Ferragens e Acessórios Essenciais:
   - Par de corrediças (TELESCOPICA ou OCULTA)
   - Puxador (EXTERNO, EMBUTIDO ou CAVA)
   - Fixadores e acabamento (parafusos, fita de borda nos topos superiores da caixa e 4 lados da frente, tapa-furos)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


ALL_ROLES = ('LATERAL_ESQ', 'LATERAL_DIR', 'CONTRAFRENTE', 'TRASEIRA', 'FUNDO', 'FRENTE')

ROLE_LABELS = {
    'LATERAL_ESQ': "Lateral Esquerda",
    'LATERAL_DIR': "Lateral Direita",
    'CONTRAFRENTE': "Contrafrente",
    'TRASEIRA': "Traseira / Contrafundo",
    'FUNDO': "Fundo",
    'FRENTE': "Frente da Gaveta",
}


@dataclass
class PartBox:
    part_id: str
    min_pt: Tuple[float, float, float]
    max_pt: Tuple[float, float, float]

    @property
    def size(self) -> Tuple[float, float, float]:
        return (
            max(self.max_pt[0] - self.min_pt[0], 0.0),
            max(self.max_pt[1] - self.min_pt[1], 0.0),
            max(self.max_pt[2] - self.min_pt[2], 0.0),
        )

    @property
    def center(self) -> Tuple[float, float, float]:
        return (
            0.5 * (self.min_pt[0] + self.max_pt[0]),
            0.5 * (self.min_pt[1] + self.max_pt[1]),
            0.5 * (self.min_pt[2] + self.max_pt[2]),
        )

    @property
    def thin_axis(self) -> int:
        """Eixo de menor dimensão (0=X lateral, 1=Y frente/trás, 2=Z fundo)."""
        s = self.size
        return min(range(3), key=lambda i: s[i])


@dataclass
class SynthesizedPart:
    role: str
    label: str
    min_pt: Tuple[float, float, float]
    max_pt: Tuple[float, float, float]
    thickness_mm: float


@dataclass
class DrawerAnalysis:
    role_map: Dict[str, PartBox] = field(default_factory=dict)
    unclassified: List[PartBox] = field(default_factory=list)
    missing_roles: List[str] = field(default_factory=list)
    bounds_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounds_max: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    @property
    def is_complete(self) -> bool:
        return len(self.missing_roles) == 0


def default_hardware(
    slide_type: str = 'TELESCOPICA',
    handle_type: str = 'EXTERNO',
    bottom_mount: str = 'RASGO',
) -> Dict[str, object]:
    """Metadados padrão de ferragens e acessórios essenciais da gaveta (RN-11)."""
    return {
        'corredica_tipo': slide_type,            # TELESCOPICA | OCULTA
        'corredica_qtd': 2,                      # 1 par
        'puxador_tipo': handle_type,             # EXTERNO | EMBUTIDO | CAVA
        'fundo_fixacao': bottom_mount,           # RASGO | PARAFUSADO
        'parafusos': True,
        'tapa_furos': True,
        'fita_borda': {
            'caixa_topos_superiores': True,
            'frente_quatro_lados': True,
        },
    }


def analyze_drawer_parts(boxes: List[PartBox]) -> DrawerAnalysis:
    """Classifica `boxes` nos 6 papéis de gaveta pelo formato e posição relativa. Nunca lança erro por falta de peça."""
    if not boxes:
        return DrawerAnalysis(missing_roles=list(ALL_ROLES))

    min_x = min(b.min_pt[0] for b in boxes)
    min_y = min(b.min_pt[1] for b in boxes)
    min_z = min(b.min_pt[2] for b in boxes)
    max_x = max(b.max_pt[0] for b in boxes)
    max_y = max(b.max_pt[1] for b in boxes)
    max_z = max(b.max_pt[2] for b in boxes)

    cx_all = 0.5 * (min_x + max_x)
    cy_all = 0.5 * (min_y + max_y)

    role_map: Dict[str, PartBox] = {}
    used_ids = set()

    # 1. Fundo: placa horizontal (thin_axis == 2), mais próxima de min_z
    z_plates = sorted([b for b in boxes if b.thin_axis == 2], key=lambda b: (b.center[2], b.size[2]))
    if z_plates:
        role_map['FUNDO'] = z_plates[0]
        used_ids.add(z_plates[0].part_id)

    # 2. Laterais: placas verticais finas em X (thin_axis == 0), esquerda (menor X) e direita (maior X)
    x_plates = sorted([b for b in boxes if b.part_id not in used_ids and b.thin_axis == 0], key=lambda b: b.center[0])
    if len(x_plates) >= 2:
        role_map['LATERAL_ESQ'] = x_plates[0]
        role_map['LATERAL_DIR'] = x_plates[-1]
        used_ids.add(x_plates[0].part_id)
        used_ids.add(x_plates[-1].part_id)
    elif len(x_plates) == 1:
        side_role = 'LATERAL_ESQ' if x_plates[0].center[0] <= cx_all else 'LATERAL_DIR'
        role_map[side_role] = x_plates[0]
        used_ids.add(x_plates[0].part_id)

    # 3. Placas verticais finas em Y (thin_axis == 1): Frente (menor Y), Contrafrente (atrás da frente), Traseira (maior Y)
    y_plates = sorted([b for b in boxes if b.part_id not in used_ids and b.thin_axis == 1], key=lambda b: b.center[1])
    if len(y_plates) >= 3:
        role_map['FRENTE'] = y_plates[0]
        role_map['CONTRAFRENTE'] = y_plates[1]
        role_map['TRASEIRA'] = y_plates[-1]
        used_ids.update((y_plates[0].part_id, y_plates[1].part_id, y_plates[-1].part_id))
    elif len(y_plates) == 2:
        # Mais à frente = FRENTE (ou CONTRAFRENTE se muito próxima do centro), mais atrás = TRASEIRA
        front_cand, back_cand = y_plates[0], y_plates[1]
        if back_cand.center[1] > cy_all:
            role_map['TRASEIRA'] = back_cand
            used_ids.add(back_cand.part_id)
            # Se front_cand é mais larga/alta ou está na borda frontal -> FRENTE
            if front_cand.center[1] <= cy_all:
                role_map['FRENTE'] = front_cand
                used_ids.add(front_cand.part_id)
        else:
            role_map['FRENTE'] = front_cand
            role_map['CONTRAFRENTE'] = back_cand
            used_ids.update((front_cand.part_id, back_cand.part_id))
    elif len(y_plates) == 1:
        p = y_plates[0]
        role = 'FRENTE' if p.center[1] <= cy_all else 'TRASEIRA'
        role_map[role] = p
        used_ids.add(p.part_id)

    unclassified = [b for b in boxes if b.part_id not in used_ids]
    missing = [r for r in ALL_ROLES if r not in role_map]

    return DrawerAnalysis(
        role_map=role_map,
        unclassified=unclassified,
        missing_roles=missing,
        bounds_min=(min_x, min_y, min_z),
        bounds_max=(max_x, max_y, max_z),
    )


def synthesize_missing_parts(
    analysis: DrawerAnalysis,
    box_thickness_m: float = 0.015,
    bottom_thickness_m: float = 0.006,
    front_thickness_m: float = 0.018,
) -> List[SynthesizedPart]:
    """Gera especificações geométricas das peças faltantes com base no envelope detectado."""
    if analysis.is_complete:
        return []

    bx0, by0, bz0 = analysis.bounds_min
    bx1, by1, bz1 = analysis.bounds_max
    if bx1 <= bx0 or by1 <= by0 or bz1 <= bz0:
        return []

    lat_e = analysis.role_map.get('LATERAL_ESQ')
    lat_d = analysis.role_map.get('LATERAL_DIR')
    frente = analysis.role_map.get('FRENTE')

    # Limites internos da caixa
    inner_x0 = lat_e.max_pt[0] if lat_e else (bx0 + box_thickness_m)
    inner_x1 = lat_d.min_pt[0] if lat_d else (bx1 - box_thickness_m)
    box_y0 = frente.max_pt[1] if frente else (by0 + front_thickness_m)
    box_y1 = by1
    box_z0 = lat_e.min_pt[2] if lat_e else (lat_d.min_pt[2] if lat_d else bz0 + 0.01)
    box_z1 = lat_e.max_pt[2] if lat_e else (lat_d.max_pt[2] if lat_d else bz1)

    if inner_x1 <= inner_x0:
        inner_x0, inner_x1 = bx0 + box_thickness_m, bx1 - box_thickness_m
    if box_y1 <= box_y0 + box_thickness_m:
        box_y0 = by0

    generated: List[SynthesizedPart] = []
    for role in analysis.missing_roles:
        if role == 'LATERAL_ESQ':
            mn, mx = (bx0, box_y0, box_z0), (bx0 + box_thickness_m, box_y1, box_z1)
            t_mm = box_thickness_m * 1000.0
        elif role == 'LATERAL_DIR':
            mn, mx = (bx1 - box_thickness_m, box_y0, box_z0), (bx1, box_y1, box_z1)
            t_mm = box_thickness_m * 1000.0
        elif role == 'CONTRAFRENTE':
            mn, mx = (inner_x0, box_y0, box_z0), (inner_x1, box_y0 + box_thickness_m, box_z1)
            t_mm = box_thickness_m * 1000.0
        elif role == 'TRASEIRA':
            mn, mx = (inner_x0, box_y1 - box_thickness_m, box_z0), (inner_x1, box_y1, box_z1)
            t_mm = box_thickness_m * 1000.0
        elif role == 'FUNDO':
            mn, mx = (inner_x0, box_y0, box_z0), (inner_x1, box_y1, box_z0 + bottom_thickness_m)
            t_mm = bottom_thickness_m * 1000.0
        elif role == 'FRENTE':
            mn, mx = (bx0, by0 - front_thickness_m, bz0), (bx1, by0, bz1)
            t_mm = front_thickness_m * 1000.0
        else:
            continue
        generated.append(SynthesizedPart(role=role, label=ROLE_LABELS[role], min_pt=mn, max_pt=mx, thickness_mm=t_mm))

    return generated
