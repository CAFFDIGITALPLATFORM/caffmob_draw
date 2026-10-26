"""Protótipo da 071 (T003; D-12): importar abre um arquivo novo do Blender e monta o ambiente nele.

Um operador lê o arquivo (aqui, o documento sintético do MOBI), troca para um arquivo vazio com
`wm.read_homefile(use_empty=True)` e, num timer de um disparo, monta a cena e grava um passo de desfazer. Prova que o
addon segue registrado, que a cena monta no arquivo novo e que um Ctrl+Z volta ao arquivo vazio. Precisa de janela:

    xvfb-run -a blender --factory-startup --python tests/prototipo_071_arquivo_novo.py

Sai com 0 se verde, 1 se vermelho.
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401
import _mobi_sintetico  # noqa: E402

falhas = []
PENDENTE = {}


def conferir(ok, texto):
    print(('OK   ' if ok else 'FALHA ') + texto, flush=True)
    if not ok:
        falhas.append(texto)


def montar():
    from caffmob_draw.mobi.cena_v2 import construir_cena
    documento = PENDENTE.pop('documento')
    construir_cena(bpy.context, documento)
    bpy.ops.ed.undo_push(message='Importar Promob')
    return None


class PROTO_OT_importar(bpy.types.Operator):
    bl_idname = 'caffmob.proto_071_importar'
    bl_label = 'Protótipo: importar em arquivo novo'

    def execute(self, context):
        PENDENTE['documento'] = _mobi_sintetico.ambiente()
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.app.timers.register(montar, first_interval=0.0)
        return {'FINISHED'}


bpy.utils.register_class(PROTO_OT_importar)


def passo1():
    bpy.ops.mesh.primitive_cube_add()
    bpy.context.scene.objects[0].name = 'Antes'
    # `is_dirty` só acende depois de um evento da janela; a confirmação do operador é conferida no ensaio.
    bpy.ops.caffmob.proto_071_importar()
    bpy.app.timers.register(passo2, first_interval=1.5)
    return None


def passo2():
    nomes = {o.name for o in bpy.context.scene.objects}
    conferir('Antes' not in nomes, 'o arquivo novo não tem o objeto do anterior')
    conferir('caffmob_ambiente' in bpy.context.scene, 'a cena do MOBI montou no arquivo novo')
    conferir(any(o.get('caffmob_tipo') == 'abertura' for o in bpy.context.scene.objects), 'o portão está na cena')
    conferir(hasattr(bpy.ops.caffmob, 'mobi_editar_entidade') and 'mobi_editar_entidade' in dir(bpy.ops.caffmob),
             'o addon segue registrado depois da troca de arquivo')
    conferir(bpy.context.scene.unit_settings.length_unit == 'MILLIMETERS', 'a cena nova está em mm')
    bpy.ops.ed.undo()
    bpy.app.timers.register(passo3, first_interval=1.0)
    return None


def passo3():
    conferir('caffmob_ambiente' not in bpy.context.scene and not any(
        o.get('caffmob_tipo') for o in bpy.context.scene.objects), 'um Ctrl+Z volta ao arquivo vazio')
    print('RESULTADO', 'VERDE' if not falhas else 'VERMELHO', flush=True)
    os._exit(1 if falhas else 0)


bpy.app.timers.register(passo1, first_interval=1.0)
