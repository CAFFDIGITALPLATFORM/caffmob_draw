"""Protótipo da onda 8 (T180; D-42): o setter de um campo agenda, por timer, um operador `UNDO` que edita o documento
do MOBI e remonta a cena. Prova que sai um passo de desfazer só: um Ctrl+Z volta o documento e o 3D, e um refazer
devolve a edição. Precisa de janela (o desfazer do Blender não roda em `--background`):

    xvfb-run -a blender --factory-startup --python tests/prototipo_067_onda8_desfazer.py

Sai com 0 se verde, 1 se vermelho (o resultado também vai para a saída padrão).
"""
import json
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
import _mobi_sintetico  # noqa: E402
from caffmob_draw.caffmob.v2 import paredes_edicao as pe  # noqa: E402
from caffmob_draw.mobi.cena_v2 import construir_cena  # noqa: E402

falhas = []


def conferir(ok, texto):
    print(('OK   ' if ok else 'FALHA ') + texto, flush=True)
    if not ok:
        falhas.append(texto)


def largura():
    d = json.loads(bpy.context.scene['caffmob_ambiente'])
    return next(a['largura'] for a in d['aberturas'] if a['id'] == _mobi_sintetico.PORTAO)


def furo():
    """Largura do portão no 3D: o vão vem da malha das peças, então a folha mede o que a montagem fez."""
    obj = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'abertura'
               and o.get('caffmob_id') == _mobi_sintetico.PORTAO)
    return json.loads(obj['caffmob_abertura'])['largura']


class PROTO_OT_editar(bpy.types.Operator):
    bl_idname = 'caffmob.proto_067_editar'
    bl_label = 'Protótipo: editar abertura do MOBI'
    bl_options = {'REGISTER', 'UNDO'}
    valor: bpy.props.IntProperty()

    def execute(self, context):
        d = json.loads(context.scene['caffmob_ambiente'])
        r = pe.editar_abertura(d, _mobi_sintetico.PORTAO, dict(largura=self.valor))
        if not r['ok']:
            self.report({'ERROR'}, str(r['erros']))
            return {'CANCELLED'}
        construir_cena(context, r['valor'])
        return {'FINISHED'}


def _setter(_self, texto):
    valor = int(texto)
    def depois():
        # Operador chamado por timer não grava passo de desfazer sozinho (1ª rodada do protótipo): o passo é
        # gravado aqui, depois da edição, só quando ela termina.
        if 'FINISHED' in bpy.ops.caffmob.proto_067_editar(valor=valor):
            bpy.ops.ed.undo_push(message='Editar abertura do MOBI')
        return None
    bpy.app.timers.register(depois, first_interval=0.0)


bpy.utils.register_class(PROTO_OT_editar)
bpy.types.WindowManager.proto_067_largura = bpy.props.StringProperty(get=lambda _s: str(largura()), set=_setter)


def passo1():
    fx.ambiente_mobi_sintetico()
    bpy.ops.ed.undo_push(message='antes')
    conferir(largura() == 3500 and furo() == 3500, 'começa com 3500')
    bpy.context.window_manager.proto_067_largura = '3000'
    bpy.app.timers.register(passo2, first_interval=1.0)


def passo2():
    conferir(largura() == 3000 and furo() == 3000, f'edição pelo timer grava 3000 (veio {largura()})')
    bpy.ops.ed.undo()
    bpy.app.timers.register(passo3, first_interval=1.0)


def passo3():
    conferir(largura() == 3500 and furo() == 3500, f'um desfazer volta a 3500 (veio {largura()})')
    bpy.ops.ed.redo()
    bpy.app.timers.register(passo4, first_interval=1.0)


def passo4():
    conferir(largura() == 3000, f'refazer devolve 3000 (veio {largura()})')
    print('RESULTADO', 'VERDE' if not falhas else 'VERMELHO', flush=True)
    os._exit(1 if falhas else 0)


bpy.app.timers.register(passo1, first_interval=1.0)
