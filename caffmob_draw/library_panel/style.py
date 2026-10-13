"""Tokens da direção visual da BIBLIOTECA CAFFMOB (feature 014, T018; D-18). Python puro.

Fonte: `_reversa_forward/014-texturas-fabricantes-grade/design-direction.md` (identidade CAFF MOBI DRAW, brief
confirmado pelo titular em 2026-10-12). Cores em RGBA de 0 a 1, para o desenho na GPU; medidas em pixels de escala
1, multiplicadas pela escala da interface no desenho.
"""

from . import grid_core


def hex_rgba(value, alpha=1.0):
    h = value.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, alpha)


# Cores ---------------------------------------------------------------------------------------------------------------
SURFACE = hex_rgba("#10302F", 0.96)          # Noite CAFF MOBI DRAW
SURFACE_RAISED = hex_rgba("#16403E", 0.98)   # cabeçalho, coluna de filtros
SURFACE_HOVER = hex_rgba("#1F5250")
SURFACE_SUNKEN = hex_rgba("#0B2322")         # fundo da miniatura, busca, chip da conta
BORDER = (1.0, 1.0, 1.0, 0.10)
BORDER_STRONG = (1.0, 1.0, 1.0, 0.22)
TEXT = hex_rgba("#EEF4F2")
TEXT_MUTED = hex_rgba("#C9D6D2")
TEXT_SUBTLE = hex_rgba("#93ADA8")            # 3,7:1 sobre SURFACE_HOVER: não usar ali
ACCENT = hex_rgba("#F07A2A")                 # laranja CAFF: seleção, aba ativa, ação principal, fixar ligado
ACCENT_INK = hex_rgba("#10302F")             # texto sobre o laranja
ACCENT_TINT = hex_rgba("#F07A2A", 0.18)
SUCCESS = hex_rgba("#1BB3AD")                # baixada, conta conectada
INFO = hex_rgba("#5BC0FF")                   # progresso, aviso de rede, espera do login
ERROR = hex_rgba("#FF6B5E")
CREAM, ORANGE, BLUE_SPARK = hex_rgba("#FFF4EA"), hex_rgba("#D35400"), hex_rgba("#2EA8F5")   # só no ícone

# Tipografia (px) -----------------------------------------------------------------------------------------------------
FONT_SMALL, FONT_LABEL, FONT_BODY, FONT_TITLE, FONT_CODE = 10, 11, 12, 14, 22

# Espaços, raios e medidas (px) ---------------------------------------------------------------------------------------
SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL = 4, 8, 12, 16, 24
RADIUS_PANEL, RADIUS_CELL, RADIUS_CONTROL, RADIUS_CHIP = 8, 6, 5, 10
HEADER_H = grid_core.HEADER_H
SIDEBAR_W = grid_core.SIDEBAR_W
CELL_W, CELL_H = grid_core.CELL_W, grid_core.CELL_H
FOOTER_H = 28.0
ROW_H = 22.0                                 # linha da coluna de filtros
CAPTION_H = 28.0                             # rótulo "Fabricantes" no topo da coluna
INDENT = 26.0                                # recuo das coleções
LOGO = 20.0                                  # ícone no cabeçalho
TITLE_GAP = 8.0                              # entre o ícone e o título
TABS_X = 150.0                               # início das abas a partir da borda esquerda
TAB_GAP = 24.0
BUTTON = 22.0                                # botões fixar/minimizar/fechar
BUTTON_STEP = 30.0
CONTROL_H = 22.0                             # busca e chip da conta
SEARCH_W = 230.0
SEARCH_MIN = 110.0                           # abaixo disso a conta vira só o ponto de estado
CHIP_PAD = 30.0                              # ponto de estado + respiro do chip da conta
MAXIMIZE_W = 26.0                            # espaço do botão de maximizar no rótulo
LABEL_LOGO = 22.0                            # ícone CAFF MOBI DRAW (16 px) antes do texto do rótulo

# Tempos (s) ----------------------------------------------------------------------------------------------------------
HOVER_TIME, OPEN_TIME = 0.12, 0.16
