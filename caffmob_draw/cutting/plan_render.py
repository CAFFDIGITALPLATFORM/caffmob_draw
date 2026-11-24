"""Renderizador interno de prévia de chapas do plano de corte em buffer RGBA (feature 021, T014; RF-02).

Gera um buffer RGBA em Python puro (testável fora do Blender) e publica em `bpy.data.images` para visualização direta
em painéis/Image Editor do Blender sem depender de navegador externo.
"""

from typing import List, Tuple

from .opcut_core import SheetLayout

_COLORS_RGBA = [
    (0.94, 0.48, 0.16, 1.0),  # Laranja CAFF
    (0.23, 0.51, 0.96, 1.0),
    (0.06, 0.73, 0.51, 1.0),
    (0.92, 0.70, 0.03, 1.0),
    (0.55, 0.36, 0.96, 1.0),
    (0.93, 0.29, 0.60, 1.0),
]


def _module_rgba(module_ref: str) -> Tuple[float, float, float, float]:
    key = module_ref or "Avulso"
    return _COLORS_RGBA[sum(ord(c) for c in key) % len(_COLORS_RGBA)]


def rasterize_sheet_rgba(sheet: SheetLayout, img_w: int = 512, img_h: int = 340) -> List[float]:
    """Desenha uma `SheetLayout` num buffer RGBA float (0..1) compatível com `bpy.types.Image.pixels`."""
    bg = (0.12, 0.13, 0.15, 1.0)
    border = (0.94, 0.48, 0.16, 1.0)
    cut_col = (0.92, 0.25, 0.25, 1.0)
    pixels = list(bg) * (img_w * img_h)

    sx = (img_w - 8) / max(sheet.width, 1.0)
    sy = (img_h - 8) / max(sheet.height, 1.0)
    scale = min(sx, sy)
    ox = int((img_w - sheet.width * scale) * 0.5)
    oy = int((img_h - sheet.height * scale) * 0.5)

    def fill_rect(x0, y0, x1, y1, rgba):
        ix0 = max(0, min(img_w - 1, int(x0)))
        ix1 = max(0, min(img_w, int(x1)))
        iy0 = max(0, min(img_h - 1, int(y0)))
        iy1 = max(0, min(img_h, int(y1)))
        r, g, b, a = rgba
        for py in range(iy0, iy1):
            row_off = py * img_w * 4
            for px in range(ix0, ix1):
                i = row_off + px * 4
                pixels[i] = r
                pixels[i + 1] = g
                pixels[i + 2] = b
                pixels[i + 3] = a

    sw = int(sheet.width * scale)
    sh = int(sheet.height * scale)
    fill_rect(ox, oy, ox + sw, oy + sh, (0.18, 0.19, 0.22, 1.0))

    # Borda da chapa
    fill_rect(ox, oy, ox + sw, oy + 2, border)
    fill_rect(ox, oy + sh - 2, ox + sw, oy + sh, border)
    fill_rect(ox, oy, ox + 2, oy + sh, border)
    fill_rect(ox + sw - 2, oy, ox + sw, oy + sh, border)

    # Peças alocadas
    for rect in sheet.used:
        rx0 = ox + int(rect.x * scale)
        ry0 = oy + int(rect.y * scale)
        rx1 = ox + int((rect.x + rect.width) * scale)
        ry1 = oy + int((rect.y + rect.height) * scale)
        col = _module_rgba(rect.module_ref)
        fill_rect(rx0, ry0, rx1, ry1, col)
        # Contorno fino escuro
        fill_rect(rx0, ry0, rx1, ry0 + 1, (0.06, 0.06, 0.08, 1.0))
        fill_rect(rx0, max(ry0, ry1 - 1), rx1, ry1, (0.06, 0.06, 0.08, 1.0))
        fill_rect(rx0, ry0, rx0 + 1, ry1, (0.06, 0.06, 0.08, 1.0))
        fill_rect(max(rx0, rx1 - 1), ry0, rx1, ry1, (0.06, 0.06, 0.08, 1.0))

    # Linhas de corte guilhotinado
    for c in sheet.cuts:
        cx0 = ox + int(c.x1 * scale)
        cy0 = oy + int(c.y1 * scale)
        cx1 = ox + int(c.x2 * scale)
        cy1 = oy + int(c.y2 * scale)
        fill_rect(min(cx0, cx1), min(cy0, cy1), max(cx0, cx1) + 1, max(cy0, cy1) + 1, cut_col)

    return pixels


def update_blender_preview_image(sheet: SheetLayout, image_name: str = "CAFFMob_PlanoCorte_Preview",
                                 img_w: int = 512, img_h: int = 340):
    """Cria ou atualiza a imagem de prévia no Blender (`bpy.data.images`)."""
    import bpy  # type: ignore

    img = bpy.data.images.get(image_name)
    if img is None or img.size[0] != img_w or img.size[1] != img_h:
        if img is not None:
            bpy.data.images.remove(img)
        img = bpy.data.images.new(image_name, width=img_w, height=img_h, alpha=True)
    img.pixels.foreach_set(rasterize_sheet_rgba(sheet, img_w=img_w, img_h=img_h))
    img.update()
    return img
