"""V-Ray Mesh Measure: janela própria de medição de malha (027, T010 a T014; RF-02).

Detecta a malha selecionada (ou pede o conta-gotas), lista as partes soltas como camadas, mede cada parte, orbita o
objeto em perspectiva e ortográfica com snap configurável, desenha em Aramado, Linhas Ocultas, Sólido, Raio-X e
Material, aceita medidas manuais e imprime a malha em folhas com views de badge.

Módulos: `core.py` (núcleo puro), `camera.py` (câmera orbital), `scene.py` (leitura da malha e sessão), `draw.py`
(desenho na GPU) e `window.py` (janela, operadores e painéis).
"""

from . import window  # noqa: F401


def register():
    window.register()


def unregister():
    window.unregister()
