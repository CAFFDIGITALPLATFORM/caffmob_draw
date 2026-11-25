"""Teste puro de abertura/fechamento da janela própria (feature 023, T004).

Requer Blender (`bpy`). Sem Blender, a importação falha e o teste não é executado.
"""

import sys
from pathlib import Path

import bpy  # type: ignore  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caffmob_draw.armario_v2 import window  # noqa: E402


def test_janela_existe_inicial():
    assert not window.janela_existe()


def test_sessao_inicial_none():
    assert window.sessao() is None


def test_sessao_ciclo_iniciar_encerrar():
    s = window.JanelaSessao()
    assert s.window_ptr == 0
    assert s.area_ptr == 0
    assert s.aberto is False
    assert not window.janela_existe()

    window.iniciar_sessao()
    assert window.sessao() is not None
    assert not window.janela_existe()  # area_ptr ainda é 0

    window.encerrar_sessao()
    assert window.sessao() is None
    assert not window.janela_existe()


if __name__ == '__main__':
    for _nome, _teste in list(globals().items()):
        if _nome.startswith('test_') and callable(_teste):
            _teste()
    print('blender_023_janela_open: OK', flush=True)
