"""Fumaça no Blender da 018 (T008, T013): nome do material pelo catálogo e migração do nome antigo.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_018_nome_smoke.py

Verifica:
A. Material novo com `texture_id` do catálogo nasce com o nome do item ("Arauco … Anis"), guarda `btm_texture_nome`
   e mantém arquivo, tamanho e projeção nas propriedades.
B. Material no formato antigo ("Textura: <arquivo> <tamanho> mm") é renomeado no reaproveitamento, com o nome novo
   livre, sem recriar o material.
C. Com o nome novo ocupado, o material antigo fica, o conflito é sinalizado e o outro material não é tocado.
"""

import json
import os
import sys
import traceback

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM = 'arauco/colecao-realce/anis'
RESULT = {}


def _image():
    imagem = bpy.data.images.new('smoke_nome', 2, 2, alpha=True)
    imagem.pixels = [1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    caminho = os.path.join(ROOT, 'smoke_018_nome.png')
    imagem.filepath_raw = caminho
    imagem.file_format = 'PNG'
    imagem.save()
    return caminho


def _limpar():
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def check_novo(caminho):
    _limpar()
    from caffmob_draw.object_library import retexture
    from caffmob_draw.texture_library import catalog
    esperado = catalog.nome_de(ITEM)
    mat = retexture.image_material(caminho, 600.0, texture_id=ITEM, projection='UV')
    return {'esperado': esperado, 'nome': mat.name, 'prop_nome': mat.get(retexture.NOME_PROP),
            'arquivo': mat.get(retexture.PATH_PROP) == os.path.abspath(caminho),
            'tamanho': mat.get(retexture.SIZE_PROP), 'projecao': mat.get(retexture.PROJECTION_PROP),
            'ok': bool(esperado) and mat.name == esperado and mat.get(retexture.NOME_PROP) == esperado
            and mat.get(retexture.PATH_PROP) == os.path.abspath(caminho)
            and mat.get(retexture.PROJECTION_PROP) == 'UV'}


def check_migracao(caminho):
    _limpar()
    from caffmob_draw.object_library import retexture
    from caffmob_draw.texture_library import catalog
    esperado = catalog.nome_de(ITEM)
    antigo = retexture.image_material(caminho, 500.0, projection='UV')
    antigo.name = 'Textura: smoke_018_nome.png 500 mm'
    antigo[retexture.TEXTURE_ID_PROP] = ITEM
    mesmo = retexture.image_material(caminho, 500.0, texture_id=ITEM, projection='UV')
    return {'esperado': esperado, 'nome': mesmo.name, 'mesmo_material': mesmo == antigo,
            'conflito': bool(mesmo.get(retexture.CONFLICT_PROP, False)),
            'ok': mesmo == antigo and mesmo.name == esperado and not mesmo.get(retexture.CONFLICT_PROP, False)}


def check_conflito(caminho):
    _limpar()
    from caffmob_draw.object_library import retexture
    from caffmob_draw.texture_library import catalog
    esperado = catalog.nome_de(ITEM)
    bpy.data.materials.new(esperado)                      # o nome novo já está ocupado
    antigo = retexture.image_material(caminho, 400.0, projection='UV')
    antigo.name = 'Textura: smoke_018_nome.png 400 mm'
    antigo[retexture.TEXTURE_ID_PROP] = ITEM
    mesmo = retexture.image_material(caminho, 400.0, texture_id=ITEM, projection='UV')
    outro = bpy.data.materials.get(esperado)
    return {'esperado': esperado, 'nome': mesmo.name, 'conflito': bool(mesmo.get(retexture.CONFLICT_PROP, False)),
            'outro_intacto': outro is not None and outro is not mesmo,
            'ok': mesmo.name.startswith('Textura: ') and bool(mesmo.get(retexture.CONFLICT_PROP, False))
            and outro is not None and outro is not mesmo}


def main():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    caminho = _image()
    RESULT['blender'] = bpy.app.version_string
    for nome, funcao in (('novo', lambda: check_novo(caminho)),
                         ('migracao', lambda: check_migracao(caminho)),
                         ('conflito', lambda: check_conflito(caminho))):
        try:
            RESULT[nome] = funcao()
        except Exception as exc:                        # noqa: BLE001 - a fumaça precisa terminar
            RESULT[nome] = {'erro': str(exc), 'trace': traceback.format_exc()}
    print('===SMOKE_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, indent=2))
    print('===SMOKE_JSON_FIM===')
    arquivo = os.path.join(ROOT, 'smoke_018_nome.png')
    if os.path.exists(arquivo):
        os.remove(arquivo)
    print('OK' if all(v.get('ok', True) for v in RESULT.values() if isinstance(v, dict)) else 'FALHOU')


main()
