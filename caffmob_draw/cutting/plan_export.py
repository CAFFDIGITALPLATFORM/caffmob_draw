"""Exportação atômica do Plano de Corte OpCut em SVG, HTML autocontido e PDF 1.4 puro (feature 021, T013; RF-02).

Zero dependências externas: gera SVG vetorial em mm, HTML offline com lista agrupada por módulo + SVGs embutidos,
e PDF 1.4 vetorial determinístico. Toda escrita usa arquivo temporário + `os.replace`.
"""

import html as html_mod
import os
from typing import List

from .module_list_core import ModuleGroup
from .opcut_core import CutPlanResult, SheetLayout

_PALETTE = [
    ("#F07A2A", "#1A1B1E"),
    ("#3B82F6", "#FFFFFF"),
    ("#10B981", "#0F172A"),
    ("#EAB308", "#1A1B1E"),
    ("#8B5CF6", "#FFFFFF"),
    ("#EC4899", "#FFFFFF"),
    ("#06B6D4", "#0F172A"),
]


def _color_for_module(module_ref: str):
    key = module_ref or "Avulso"
    idx = sum(ord(c) for c in key) % len(_PALETTE)
    return _PALETTE[idx]


def _atomic_write(path: str, data: bytes):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp = f"{path}.tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise


def render_svg_string(sheet: SheetLayout, scale: float = 0.35) -> str:
    """Renderiza uma `SheetLayout` em string SVG vetorial autocontida."""
    w = sheet.width * scale
    h = sheet.height * scale
    m = sheet.margin * scale
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
        f'width="{w:.1f}" height="{h:.1f}" style="background:#18191C;border:1px solid #3A3D45">',
        f'<rect x="0" y="0" width="{w:.1f}" height="{h:.1f}" fill="#26282E" stroke="#F07A2A" stroke-width="1.5"/>',
        f'<rect x="{m:.1f}" y="{m:.1f}" width="{max(w - 2*m, 0):.1f}" height="{max(h - 2*m, 0):.1f}" '
        f'fill="none" stroke="#6B7280" stroke-dasharray="4 3" stroke-width="0.8"/>',
    ]
    for c in sheet.cuts:
        parts.append(
            f'<line x1="{c.x1 * scale:.1f}" y1="{c.y1 * scale:.1f}" '
            f'x2="{c.x2 * scale:.1f}" y2="{c.y2 * scale:.1f}" '
            f'stroke="#EF4444" stroke-width="0.7" stroke-dasharray="3 2"/>'
        )
    for r in sheet.used:
        bg, fg = _color_for_module(r.module_ref)
        rx, ry = r.x * scale, r.y * scale
        rw, rh = r.width * scale, r.height * scale
        rot_tag = " [R]" if r.rotated else ""
        label = html_mod.escape(f"{r.label}{rot_tag}")
        dims = f"{r.width:.0f}x{r.height:.0f}mm"
        cx, cy = rx + rw * 0.5, ry + rh * 0.5
        parts.append(
            f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" '
            f'fill="{bg}" fill-opacity="0.86" stroke="#111215" stroke-width="1"/>'
        )
        if rw > 28 and rh > 18:
            parts.append(
                f'<text x="{cx:.1f}" y="{cy - 3:.1f}" fill="{fg}" font-family="sans-serif" '
                f'font-size="9" font-weight="bold" text-anchor="middle">{label}</text>'
            )
            parts.append(
                f'<text x="{cx:.1f}" y="{cy + 9:.1f}" fill="{fg}" font-family="sans-serif" '
                f'font-size="8" text-anchor="middle">{dims}</text>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def write_svg(sheet: SheetLayout, path: str, scale: float = 0.35) -> str:
    """Grava arquivo SVG de uma chapa de forma atômica."""
    svg = render_svg_string(sheet, scale=scale)
    _atomic_write(path, svg.encode("utf-8"))
    return path


def write_html(plan: CutPlanResult, module_groups: List[ModuleGroup], path: str, title: str = "Plano de Corte CAFFMob") -> str:
    """Grava documento HTML 100% offline com lista agrupada por módulo e SVGs de todas as chapas."""
    esc_title = html_mod.escape(title)
    mod_blocks = []
    for grp in module_groups:
        rows = []
        for p in grp.parts:
            rows.append(
                f"<tr><td>{html_mod.escape(p.name)}</td><td>{html_mod.escape(p.component)}</td>"
                f"<td>{p.width_mm:.0f} × {p.height_mm:.0f} mm</td><td>{p.thickness_mm:.0f} mm</td>"
                f"<td>{html_mod.escape(p.material)}</td><td>{html_mod.escape(p.grain_direction)}</td>"
                f"<td>{p.quantity}</td></tr>"
            )
        mod_blocks.append(
            f"<section class='mod'><h3>{html_mod.escape(grp.module_name)} "
            f"({grp.total_pieces} peças · {grp.total_area_m2:.2f} m²)</h3>"
            f"<table><thead><tr><th>Peça</th><th>Tipo</th><th>Dimensão</th><th>Esp.</th>"
            f"<th>Material</th><th>Veio</th><th>Qtd</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></section>"
        )

    sheet_blocks = []
    for sh in plan.sheets:
        sheet_blocks.append(
            f"<section class='sheet'><h3>Chapa #{sh.sheet_index} — {html_mod.escape(sh.material)} "
            f"{sh.thickness:.0f} mm ({sh.width:.0f} × {sh.height:.0f} mm · Aproveitamento {sh.efficiency_pct:.1f}%)</h3>"
            f"{render_svg_string(sh, scale=0.35)}</section>"
        )

    unplaced_html = ""
    if plan.unplaced:
        items_li = "".join(
            f"<li>{html_mod.escape(u.label)} ({u.width:.0f} × {u.height:.0f} mm, {html_mod.escape(u.material)})</li>"
            for u in plan.unplaced
        )
        unplaced_html = f"<section class='warn'><h3>Peças fora da área útil ({len(plan.unplaced)})</h3><ul>{items_li}</ul></section>"

    doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{esc_title}</title>
<style>
body{{font-family:system-ui,sans-serif;background:#141518;color:#ECEEF2;margin:24px}}
h1,h2,h3{{color:#F07A2A}}
table{{width:100%;border-collapse:collapse;margin-bottom:16px;font-size:13px}}
th,td{{border:1px solid #2E3138;padding:6px 8px;text-align:left}}
th{{background:#1E2025;color:#F8FAFC}}
.sheet,.mod{{margin-bottom:24px;page-break-inside:avoid}}
.warn{{background:#3B1919;border:1px solid #EF4444;padding:12px;border-radius:6px;margin-bottom:20px}}
@media print{{body{{background:#FFF;color:#111}}th{{background:#EEE;color:#111}}}}
</style>
</head>
<body>
<h1>{esc_title}</h1>
<p>Total de chapas: <strong>{len(plan.sheets)}</strong> · Módulos: <strong>{len(module_groups)}</strong></p>
{unplaced_html}
<h2>Lista de Peças Agrupadas por Módulo</h2>
{''.join(mod_blocks) or '<p>Nenhuma peça listada.</p>'}
<h2>Plano de Corte Otimizado (OpCut)</h2>
{''.join(sheet_blocks) or '<p>Nenhuma chapa gerada.</p>'}
</body>
</html>
"""
    _atomic_write(path, doc.encode("utf-8"))
    return path


def _pdf_escape(text: str) -> str:
    safe = text.encode("latin-1", errors="replace").decode("latin-1")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf(plan: CutPlanResult, module_groups: List[ModuleGroup], path: str, title: str = "Plano de Corte CAFFMob") -> str:
    """Grava PDF 1.4 vetorial puro (A4 paisagem) sem dependências externas."""
    page_w, page_h = 842.0, 595.0  # A4 paisagem em pontos
    streams: List[bytes] = []

    # Página 1: Lista de peças agrupadas por módulo
    cmds = [
        "0.94 0.48 0.16 rg",
        f"BT /F1 16 Tf 36 {page_h - 42:.1f} Td ({_pdf_escape(title)}) Tj ET",
        "0.15 0.15 0.15 rg",
        f"BT /F1 10 Tf 36 {page_h - 62:.1f} Td (Chapas: {len(plan.sheets)} | Modulos: {len(module_groups)}) Tj ET",
    ]
    y = page_h - 88.0
    for grp in module_groups:
        if y < 60:
            break
        cmds.append("0.94 0.48 0.16 rg")
        cmds.append(f"BT /F1 11 Tf 36 {y:.1f} Td ({_pdf_escape(grp.module_name)} - {grp.total_pieces} pecas) Tj ET")
        y -= 15.0
        cmds.append("0.1 0.1 0.1 rg")
        for p in grp.parts:
            if y < 44:
                break
            line = f"  {p.name} | {p.width_mm:.0f}x{p.height_mm:.0f}x{p.thickness_mm:.0f}mm | {p.material} | Qtd: {p.quantity}"
            cmds.append(f"BT /F1 9 Tf 42 {y:.1f} Td ({_pdf_escape(line)}) Tj ET")
            y -= 12.0
        y -= 6.0
    streams.append("\n".join(cmds).encode("latin-1"))

    # Uma página por chapa
    for sh in plan.sheets:
        sc = min((page_w - 72.0) / max(sh.width, 1.0), (page_h - 110.0) / max(sh.height, 1.0))
        ox = 36.0
        oy = 40.0
        scmds = [
            "0.94 0.48 0.16 rg",
            f"BT /F1 13 Tf 36 {page_h - 36:.1f} Td ({_pdf_escape(f'Chapa #{sh.sheet_index} - {sh.material} {sh.thickness:.0f}mm ({sh.efficiency_pct:.1f}%)')}) Tj ET",
            "0.2 0.2 0.2 RG 1 w",
            f"{ox:.2f} {oy:.2f} {sh.width * sc:.2f} {sh.height * sc:.2f} re S",
        ]
        for r in sh.used:
            rx = ox + r.x * sc
            ry = oy + r.y * sc
            rw = r.width * sc
            rh = r.height * sc
            scmds.append("0.95 0.88 0.80 rg 0.15 0.15 0.15 RG 0.6 w")
            scmds.append(f"{rx:.2f} {ry:.2f} {rw:.2f} {rh:.2f} re B")
            if rw > 34 and rh > 16:
                scmds.append("0.1 0.1 0.1 rg")
                scmds.append(
                    f"BT /F1 7 Tf {rx + 3:.2f} {ry + rh * 0.5:.2f} Td "
                    f"({_pdf_escape(f'{r.label} {r.width:.0f}x{r.height:.0f}')}) Tj ET"
                )
        streams.append("\n".join(scmds).encode("latin-1"))

    # Montagem de objetos PDF 1.4: 1=Catalog, 2=Pages, 3=Font, depois pares (Page, Content)
    objs: List[bytes] = []
    page_ids = []
    next_id = 4
    for _ in streams:
        page_ids.append(next_id)
        next_id += 2

    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii"))
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for pid, content in zip(page_ids, streams):
        cid = pid + 1
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w:.0f} {page_h:.0f}] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {cid} 0 R >>".encode("ascii")
        )
        objs.append(f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out.extend(f"{idx} 0 obj\n".encode("ascii"))
        out.extend(body)
        out.extend(b"\nendobj\n")

    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objs) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )

    _atomic_write(path, bytes(out))
    return path
