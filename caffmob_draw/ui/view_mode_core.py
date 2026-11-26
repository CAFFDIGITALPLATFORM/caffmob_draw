"""Modo de vista Sólido · Textura com o interruptor Linhas (feature 010, T011; RN-06, D-05; 027, RF-03).

`settings` traduz o estado da cena nos valores de `View3DShading` que a vista recebe. Linhas não usa mais o wireframe
do Blender (cor do tema e espessura fixa): quem desenha as arestas pretas com a espessura da preferência é
`overlays/arestas.py`, ligado pela mesma `Scene.btm_view_lines`. Voltar a Sólido devolve o `color_type` que a vista
tinha antes de Textura.
"""

from ..data.i18n import N_, tr

MODES = (('SOLID', N_("Sólido")), ('TEXTURE', N_("Textura")))


def settings(mode, lines, previous_color):
    color = 'TEXTURE' if mode == 'TEXTURE' else (previous_color if previous_color and previous_color != 'TEXTURE'
                                                 else 'MATERIAL')
    # A vista liga/desliga o wireframe do Blender e as arestas próprias pela mesma `lines`: os dois nunca somam.
    return {'shading_type': 'SOLID', 'color_type': color, 'show_wireframes': False, 'edges': bool(lines)}


def label(mode, lines):
    if mode == 'TEXTURE':
        return tr("Textura com linha") if lines else tr("Textura")
    return tr("Sólido com linha") if lines else tr("Sólido")
