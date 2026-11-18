"""BUG-20261117-6OXN (#147): tema claro do editor de paredes.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6OXN_tema.py

Reprodução: o estado do editor não tem propriedade de tema e o painel Grid não oferece nenhuma escolha de cor, então o
editor só existe no escuro. Regressões: a preferência salva é lida ao abrir o editor, trocar o tema grava o arquivo do
usuário, o desenho recebe a paleta escolhida, o tema escuro continua exatamente o de antes e o painel Grid mantém as
opções que já tinha.
"""

import sys
import tempfile
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
addon.load_file_post(None)

from caffmob_draw.data.i18n import tr  # noqa: E402
from caffmob_draw.walls2d import cores, panels, props, tema  # noqa: E402

ctx = bpy.context
scene = ctx.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

PASTA = tempfile.TemporaryDirectory()
ARQUIVO = Path(PASTA.name) / 'tema.json'
tema.arquivo = lambda: str(ARQUIVO)


def estado():
    return ctx.window_manager.btm_wall_editor


class Layout:
    """UILayout de mentira: grava rótulos, propriedades e botões do N-panel."""

    def __init__(self, registro):
        self.r = registro
        self.enabled = True
        self.alert = True
        self.scale_y = 1
        self.use_property_split = False
        self.use_property_decorate = True

    def label(self, text='', icon='NONE'):
        self.r.append(('label', text, icon))

    def prop(self, dono, nome, **kw):
        self.r.append(('prop', nome, kw))

    def operator(self, idname, text='', **kw):
        self.r.append(('op', idname, text, kw))
        return types.SimpleNamespace()

    def row(self, **kw):
        return Layout(self.r)

    box = column = row

    def separator(self):
        pass


def painel_grid():
    registro = []
    panels.BTM_PT_WallEditorGrid.draw(types.SimpleNamespace(layout=Layout(registro)), ctx)
    return registro


def propriedades(registro):
    return [rec for rec in registro if rec[0] == 'prop']


# Reprodução -------------------------------------------------------------------------------------------------
assert 'tema' in props.BTM_PG_WallEditorState.bl_rna.properties, \
    'o estado do editor não tem propriedade de tema: não há como escolher o fundo'

itens = props.BTM_PG_WallEditorState.bl_rna.properties['tema'].enum_items
assert [i.identifier for i in itens] == ['ESCURO', 'CLARO'], [(i.identifier, i.name) for i in itens]
assert [i.name for i in itens] == ['Escuro', 'Claro'], [i.name for i in itens]
print('OK reprodução: estado do editor tem o tema com Escuro e Claro')

# Preferência: grava, lê ao abrir e sobrevive a fechar e reabrir -------------------------------------------------
estado().tema = 'ESCURO'
assert ARQUIVO.exists(), 'trocar o tema não gravou a preferência'
assert tema.ler() == 'ESCURO', tema.ler()

estado().tema = 'CLARO'
assert tema.ler() == 'CLARO', tema.ler()
props.aplicar_preferencia()
assert estado().tema == 'CLARO', estado().tema

estado().tema = 'ESCURO'
props.aplicar_preferencia()
assert estado().tema == 'ESCURO', estado().tema
print('OK preferência: grava, reabre e aplica o tema salvo')

# Escolha chega ao desenho -------------------------------------------------------------------------------------
estado().tema = 'CLARO'
assert tema.paleta(estado().tema) is tema.CLARO
assert cores.cor('NORMAL', claro=True) == tema.CLARO['wall'], cores.cor('NORMAL', claro=True)
estado().tema = 'ESCURO'
assert tema.paleta(estado().tema) is tema.ESCURO
print('OK desenho: paleta vem do tema escolhido')

# Regressões ---------------------------------------------------------------------------------------------------
from caffmob_draw.walls2d import ops_editor  # noqa: E402

assert ops_editor.COLORS['background'] == (0.12, 0.12, 0.13, 1.0), ops_editor.COLORS['background']
assert ops_editor.COLORS['wall'] == cores.cor('NORMAL'), ops_editor.COLORS['wall']
assert ops_editor.COLORS['selected'] == (1.0, 0.62, 0.15, 1.0), ops_editor.COLORS['selected']
assert ops_editor.COLORS['muted'] == (0.65, 0.65, 0.68, 1.0), ops_editor.COLORS['muted']

registro = painel_grid()
temas = [rec for rec in propriedades(registro) if rec[1] == 'tema']
assert len(temas) == 1, propriedades(registro)
assert temas[0][2].get('expand') is True, temas[0][2]
rotulos = [rec[1] for rec in registro if rec[0] == 'label']
assert tr('Aparência') in rotulos, rotulos

nomes = [rec[1] for rec in propriedades(registro)]
for nome in ('grid_size', 'magnetic', 'new_direction', 'new_thickness', 'new_height'):
    assert nome in nomes, (nome, nomes)
print('OK regressão: tema escuro intacto e painel Grid mantém as opções')

props.end()
assert props.session() is None
PASTA.cleanup()
print('OK BUG-20261117-6OXN')
