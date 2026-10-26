"""
BlenderToMob Cutting & Nesting Optimization Engine
Algoritmo de otimização de corte 2D Guilhotina / Bin-Packing para chapas de MDF.
Suporta refilo perimetral por borda, espessura da lâmina (kerf), veio da madeira e fitas de borda.
"""

from ..data.i18n import tr


class NestingPart:
    """Peça de corte em mm. `height` é o comprimento (veio VERTICAL acompanha o comprimento) e `width` a largura.

    `edges[4]`: espessura da fita por lado; lados 1–2 = bordas do comprimento, 3–4 = bordas da largura (clarify C-1).
    Os nomes antigos `edge_left/right/top/bottom` continuam aceitos e são aliases de leitura de `edges`.
    """

    def __init__(
        self,
        id,
        name,
        width,
        height,
        quantity=1,
        thickness=15.0,
        material="MDF Padrão",
        grain_direction='NONE',
        module_ref="",
        edge_top=0.0,
        edge_bottom=0.0,
        edge_left=0.0,
        edge_right=0.0,
        uid=None,
        component="UNCLASSIFIED",
        edges=None,
        finish="",
        source="SYNTHETIC",
        limit_status="OK",
        module_uid=None,
        machining=None,
        machining_clipped=False,
        drilling=None,
    ):
        self.id = id
        self.uid = str(uid) if uid else str(id)
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.quantity = int(quantity)
        self.thickness = float(thickness)
        self.material = material
        self.grain_direction = grain_direction.upper()  # 'NONE', 'VERTICAL', 'HORIZONTAL'
        self.module_ref = module_ref
        self.module_uid = module_uid
        self.component = component or "UNCLASSIFIED"
        if edges is None:
            edges = [edge_left, edge_right, edge_top, edge_bottom]
        self.edges = [float(e or 0.0) for e in list(edges)[:4]] + [0.0] * (4 - min(4, len(edges)))
        self.finish = finish or ""
        self.source = source
        self.limit_status = limit_status
        self.machining = list(machining or [])          # feature 003: recortes de agregados (JSON `machining`)
        self.machining_clipped = bool(machining_clipped)
        self.drilling = list(drilling or [])            # feature 008: furação das divisórias móveis (JSON `drilling`)

    # Aliases dos nomes antigos (v1)
    @property
    def edge_left(self):
        return self.edges[0]

    @property
    def edge_right(self):
        return self.edges[1]

    @property
    def edge_top(self):
        return self.edges[2]

    @property
    def edge_bottom(self):
        return self.edges[3]

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "quantity": self.quantity,
            "thickness": self.thickness,
            "material": self.material,
            "finish": self.finish,
            "component": self.component,
            "source": self.source,
            "limit_status": self.limit_status,
            "grain_direction": self.grain_direction,
            "module_ref": self.module_ref,
            "module_uid": self.module_uid,
            "edges": {
                "top": self.edge_top,
                "bottom": self.edge_bottom,
                "left": self.edge_left,
                "right": self.edge_right
            }
        }


class NestingSheet:
    def __init__(self, id, width, height, refilo_top=10.0, refilo_bottom=10.0, refilo_left=10.0, refilo_right=10.0):
        self.id = id
        self.width = float(width)
        self.height = float(height)
        self.refilo_top = float(refilo_top)
        self.refilo_bottom = float(refilo_bottom)
        self.refilo_left = float(refilo_left)
        self.refilo_right = float(refilo_right)
        self.usable_width = self.width - (self.refilo_left + self.refilo_right)
        self.usable_height = self.height - (self.refilo_top + self.refilo_bottom)


def _orientacoes(part, grain_along_width, allow_rotation, respect_grain):
    """(extensão em x, extensão em y, girada) permitidas. Sem girar: largura em x e comprimento em y.

    Veio como no OpenMob (`openmob-bom/nesting.rs`): o veio da chapa corre no lado maior dela; peça com veio no
    comprimento (VERTICAL) põe o comprimento nesse lado, com veio na largura (HORIZONTAL) põe a largura."""
    w, h = part["width"], part["height"]
    normal, girada = (w, h, False), (h, w, True)
    g = part["grain_direction"] if respect_grain else 'NONE'
    if g == 'VERTICAL':
        return [girada if grain_along_width else normal]
    if g == 'HORIZONTAL':
        return [normal if grain_along_width else girada]
    return [normal, girada] if allow_rotation else [normal]


def _colocada(part, x, y, xw, yh, rot):
    return {
        "id": part["id"], "part_id": part["part_id"], "part_uid": part["part_uid"], "name": part["name"],
        "x": x, "y": y, "width": xw, "height": yh, "thickness": part["thickness"], "material": part["material"],
        "rotated": rot, "module_ref": part["module_ref"],
        "edges": {"top": part["edge_top"], "bottom": part["edge_bottom"], "left": part["edge_left"],
                  "right": part["edge_right"]},
    }


def optimize_nesting(
    parts,
    sheet_width=2750.0,
    sheet_height=1830.0,
    refilo_top=10.0,
    refilo_bottom=10.0,
    refilo_left=10.0,
    refilo_right=10.0,
    kerf=4.0,
    allow_rotation=True,
    respect_grain=True
):
    """
    Otimização de corte 2D em guilhotina por faixas, inspirada no OpenMob (`openmob-bom/nesting.rs`), corrigida.

    Do OpenMob: uma chapa por matéria-prima (aqui também por espessura e acabamento, clarify C-2), peças em ordem
    decrescente da altura da faixa e do comprimento, e o veio no lado maior da chapa. A faixa nasce com a altura da
    primeira peça e nunca cresce: nenhuma peça invade a faixa de cima (o motor anterior crescia a faixa já ocupada e
    sobrepunha peças). Corrigido em relação ao OpenMob: refilo nas quatro bordas, a faixa existente de menor sobra
    (best-fit) no lugar da primeira que coube, a orientação que gasta menos altura, e o teste de "maior que a chapa"
    respeitando o veio.

    Args:
        parts: Lista de objetos NestingPart.
        sheet_width: Largura nominal da chapa MDF em mm (padrão: 2750mm).
        sheet_height: Altura nominal da chapa MDF em mm (padrão: 1830mm).
        refilo_*: Margens de refilo em mm para as 4 bordas.
        kerf: Espessura do corte da serra em mm (padrão: 4mm).
        allow_rotation: Permite girar peças se não houver restrição de veio.
        respect_grain: Habilita a checagem estrita de veio da madeira.

    Retorna:
        Dicionário estruturado com chapas usadas, peças alocadas, peças excedentes e estatísticas.
    """
    usable_width = sheet_width - (refilo_left + refilo_right)
    usable_height = sheet_height - (refilo_top + refilo_bottom)
    grain_along_width = sheet_width >= sheet_height

    groups = {}
    for p in parts:
        groups.setdefault((p.material, p.thickness, getattr(p, 'finish', '')), []).append(p)

    all_sheets_used, all_unplaced = [], []
    global_sheet_id = 1

    for (mat, th, finish), group_parts in groups.items():
        flat_parts = []
        for p in group_parts:
            base = {"part_id": p.id, "part_uid": p.uid, "name": p.name, "width": p.width, "height": p.height,
                    "thickness": p.thickness, "material": p.material, "grain_direction": p.grain_direction,
                    "module_ref": p.module_ref, "edge_top": p.edge_top, "edge_bottom": p.edge_bottom,
                    "edge_left": p.edge_left, "edge_right": p.edge_right}
            cabem = [o for o in _orientacoes(base, grain_along_width, allow_rotation, respect_grain)
                     if o[0] <= usable_width + 1e-6 and o[1] <= usable_height + 1e-6]
            if not cabem:
                all_unplaced.append({
                    "id": p.id, "uid": p.uid, "name": p.name, "width": p.width, "height": p.height,
                    "thickness": p.thickness, "material": p.material,
                    "reason": tr("Dimensões ({}x{}mm) excedem a área útil ({}x{}mm)").format(
                        p.width, p.height, usable_width, usable_height)})
                continue
            for i in range(p.quantity):
                flat_parts.append(dict(base, id=f"{p.id}_{i+1}" if p.quantity > 1 else p.id, orientations=cabem))

        # A faixa de cada peça é a menor altura que ela pode ocupar; a maior primeiro, depois a mais comprida.
        flat_parts.sort(key=lambda q: (min(o[1] for o in q["orientations"]),
                                       max(o[0] for o in q["orientations"])), reverse=True)

        group_sheets = []
        for part in flat_parts:
            escolha = None                   # (sobra na altura da faixa, sobra no comprimento, chapa, faixa, orientação)
            for sheet in group_sheets:
                for shelf in sheet["shelves"]:
                    for xw, yh, rot in part["orientations"]:
                        if yh <= shelf["height"] + 1e-6 and shelf["current_x"] + xw <= usable_width + 1e-6:
                            chave = (shelf["height"] - yh, usable_width - shelf["current_x"] - xw)
                            if escolha is None or chave < escolha[0]:
                                escolha = (chave, sheet, shelf, (xw, yh, rot))
            if escolha is not None:
                _chave, sheet, shelf, (xw, yh, rot) = escolha
                shelf["parts"].append(_colocada(part, shelf["current_x"] + refilo_left, shelf["y"] + refilo_bottom,
                                                xw, yh, rot))
                shelf["current_x"] += xw + kerf
                continue
            # Faixa nova: na primeira chapa aberta com altura livre, na orientação mais baixa.
            orientacoes = sorted(part["orientations"], key=lambda o: o[1])
            colocada = False
            for sheet in group_sheets:
                proxima_y = usable_height - sheet["remaining_height"]
                for xw, yh, rot in orientacoes:
                    if proxima_y + yh <= usable_height + 1e-6:
                        sheet["shelves"].append({"y": proxima_y, "height": yh, "current_x": xw + kerf, "parts": [
                            _colocada(part, refilo_left, proxima_y + refilo_bottom, xw, yh, rot)]})
                        sheet["remaining_height"] = usable_height - (proxima_y + yh + kerf)
                        colocada = True
                        break
                if colocada:
                    break
            if colocada:
                continue
            xw, yh, rot = orientacoes[0]
            group_sheets.append({
                "id": global_sheet_id, "material": mat, "thickness": th, "finish": finish,
                "width": sheet_width, "height": sheet_height, "usable_width": usable_width,
                "usable_height": usable_height,
                "refilos": {"top": refilo_top, "bottom": refilo_bottom, "left": refilo_left, "right": refilo_right},
                "remaining_height": usable_height - (yh + kerf),
                "shelves": [{"y": 0.0, "height": yh, "current_x": xw + kerf,
                             "parts": [_colocada(part, refilo_left, refilo_bottom, xw, yh, rot)]}],
            })
            global_sheet_id += 1
        all_sheets_used.extend(group_sheets)

    total_nominal_sheet_area = len(all_sheets_used) * sheet_width * sheet_height
    total_placed_area, total_placed_count = 0.0, 0
    for s in all_sheets_used:
        sheet_placed_area = sum(p["width"] * p["height"] for sh in s["shelves"] for p in sh["parts"])
        total_placed_count += sum(len(sh["parts"]) for sh in s["shelves"])
        s["used_area_mm2"] = sheet_placed_area
        s["utilization_percentage"] = round((sheet_placed_area / (sheet_width * sheet_height)) * 100.0, 2)
        total_placed_area += sheet_placed_area

    utilization_overall = (total_placed_area / total_nominal_sheet_area * 100.0) if total_nominal_sheet_area > 0 else 0.0
    return {
        "sheets": all_sheets_used,
        "unplaced": all_unplaced,
        "stats": {
            "sheets_count": len(all_sheets_used),
            "total_placed_parts": total_placed_count,
            "unplaced_count": len(all_unplaced),
            "utilization_percentage": round(utilization_overall, 2),
            "total_placed_area_m2": round(total_placed_area / 1_000_000.0, 3),
            "total_sheet_area_m2": round(total_nominal_sheet_area / 1_000_000.0, 3),
            "waste_area_m2": round(max(0.0, total_nominal_sheet_area - total_placed_area) / 1_000_000.0, 3)
        }
    }
