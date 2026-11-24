"""Agrupamento hierárquico de lista de peças por módulo (feature 021, T012; RF-01, RN-01).

Python puro, testável fora do Blender. Exclui ferragens e itens marcados fora do corte (`cut_exclude` / `btm_cut_exclude`).
"""

from dataclasses import dataclass, field
from typing import List


HARDWARE_COMPONENTS = {'FER', 'HARDWARE', 'FERRAGEM', 'CORREDICA', 'PUXADOR', 'DOBRADICA'}


@dataclass
class ModulePartRow:
    id: str
    name: str
    component: str
    width_mm: float
    height_mm: float
    thickness_mm: float
    material: str
    grain_direction: str
    quantity: int


@dataclass
class ModuleGroup:
    module_name: str
    parts: List[ModulePartRow] = field(default_factory=list)

    @property
    def total_pieces(self) -> int:
        return sum(p.quantity for p in self.parts)

    @property
    def total_area_m2(self) -> float:
        return round(sum((p.width_mm * p.height_mm * p.quantity) / 1_000_000.0 for p in self.parts), 4)


def is_cuttable_part(part) -> bool:
    """Retorna True se a peça é uma chapa de corte (não é ferragem nem excluída do corte)."""
    if getattr(part, 'is_hardware', False) or getattr(part, 'cut_exclude', False):
        return False
    comp = str(getattr(part, 'component', '') or '').upper()
    if comp in HARDWARE_COMPONENTS:
        return False
    if float(getattr(part, 'width', 0.0)) <= 0.0 or float(getattr(part, 'height', 0.0)) <= 0.0:
        return False
    return True


def group_by_module(parts) -> List[ModuleGroup]:
    """Agrupa peças cortáveis pelo nome do módulo (`module_ref`), preservando ordenação previsível."""
    buckets = {}
    for p in parts:
        if not is_cuttable_part(p):
            continue
        mod = str(getattr(p, 'module_ref', '') or '').strip() or "Peças Avulsas"
        row = ModulePartRow(
            id=str(getattr(p, 'uid', None) or getattr(p, 'id', '')),
            name=str(getattr(p, 'name', 'Peça')),
            component=str(getattr(p, 'component', 'UNCLASSIFIED') or 'UNCLASSIFIED'),
            width_mm=round(float(getattr(p, 'width', 0.0)), 1),
            height_mm=round(float(getattr(p, 'height', 0.0)), 1),
            thickness_mm=round(float(getattr(p, 'thickness', 15.0)), 1),
            material=str(getattr(p, 'material', 'MDF Padrão') or 'MDF Padrão'),
            grain_direction=str(getattr(p, 'grain_direction', 'NONE') or 'NONE').upper(),
            quantity=max(1, int(getattr(p, 'quantity', 1))),
        )
        buckets.setdefault(mod, []).append(row)

    groups: List[ModuleGroup] = []
    for mod_name in sorted(buckets.keys()):
        rows = sorted(buckets[mod_name], key=lambda r: (r.material, r.thickness_mm, r.name))
        groups.append(ModuleGroup(module_name=mod_name, parts=rows))
    return groups
