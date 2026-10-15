"""Os 52 casos-ouro no Blender: cena, contrato, peças e isolamento (063 T057).

Adapta o teste da 061 ao master: 19 ambientes válidos, 27 módulos e 6 recusas.
Os operadores de baixar e enviar usam transporte simulado, sem rede.
"""
import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env
import bpy
from test_casos_ouro import calcular, divergencias
from caffmob_draw.caffmob.chapas import pecas_do_modulo
from caffmob_draw.caffmob.contrato import ler_documento, sem_envelope_do_servidor, serializar
from caffmob_draw.caffmob.geometria import trechos_da_parede
from caffmob_draw.cutting import part_sources
from caffmob_draw.mobi import cena
from caffmob_draw.mobi.ops_biblioteca import instance
from caffmob_draw.operators import floor_builder
from caffmob_draw.texture_library import downloads, catalog
from caffmob_draw.walls2d import model, scene_io

context = bpy.context
env.clean_scene()
root = Path(__file__).resolve().parent
cases = [json.loads(p.read_text()) for p in sorted((root / 'casos_ouro').rglob('*.json'))]
assert len(cases) == 52
base = next(c['entrada'] for c in cases if c['caso'] == 'parede-ambiente-l')
scenes, refused = 0, 0
for case in cases:
    assert not divergencias(calcular(case), case['esperado']), case['caso']
    document = copy.deepcopy(case['entrada'])
    if case['tipo'] == 'ambiente' and case['esperado'].get('erros'):
        before = {o.as_pointer() for o in context.scene.objects}
        try:
            cena.construir_cena(context, document)
        except ValueError:
            pass
        else:
            raise AssertionError(case['caso'] + ': documento inválido foi aceito')
        assert before == {o.as_pointer() for o in context.scene.objects}, case['caso']
        refused += 1
        continue
    textures = case.get('texturas', {})
    if case['tipo'] == 'modulo':
        document = copy.deepcopy(base)
        document['modulos'] = [instance(case['entrada'], case['entrada']['id'])]
    with patch.object(catalog, 'item', side_effect=textures.get):
        cena.construir_cena(context, document)
        walls = [o for o in context.scene.objects if o.get('caffmob_parede')]
        assert len(walls) == len(document['paredes']), case['caso']
        for obj, wall in zip(walls, document['paredes']):
            assert ler_documento(obj['caffmob_parede']) == wall, case['caso']
            assert len(obj.data.vertices) > 0, case['caso']
        floors = [o for o in context.scene.objects if o.get('caffmob_tipo') == 'piso']
        assert len(floors) == sum(p['fechada'] for p in document['paredes']), case['caso']
        actual = cena.documento_da_cena(context)
        assert serializar(sem_envelope_do_servidor(actual)) == serializar(sem_envelope_do_servidor(document)), case['caso']
        sources = part_sources.iter_modules(context.scene)
        assert len(sources) == len(document['modulos']), case['caso']
        for source in sources:
            assert source.library == 'caffmob' and not source.obj.children, case['caso']
            assert not source.obj.btm_cabinet.structure_id, case['caso']
            expected = pecas_do_modulo(cena._modulo_do_objeto(source.obj), textura=textures.get)
            parts = part_sources.caffmob_parts(source)
            assert len(parts) == len(expected), case['caso']
            for part, entry in zip(parts, expected):
                assert part.source == 'caffmob', case['caso']
                for key in ('id', 'name', 'width', 'height', 'thickness', 'quantity', 'material', 'grain_direction', 'module_ref'):
                    assert getattr(part, key) == entry[key], (case['caso'], key)
                for edge in ('top', 'bottom', 'left', 'right'):
                    assert getattr(part, 'edge_' + edge) == entry['edges'][edge], case['caso']
    scenes += 1
print('Casos-ouro: {} cenas com ida e volta; {} recusas sem mutação; total {}'.format(scenes, refused, len(cases)), flush=True)

# Ambiente em L: nem walls2d converte a parede, nem Atualizar piso cria outro piso.
cena.construir_cena(context, base)
wall = next(o for o in context.scene.objects if o.get('caffmob_parede'))
plan = model.WallPlan()
assert not scene_io.is_other_layer_wall(wall)
assert scene_io.convert_into(plan, [wall], context.scene) == [wall.name]
assert not plan.chains and not plan.converted_sources
assert floor_builder.scene_walls(context.scene) == ([], [])
floors = {o.as_pointer() for o in context.scene.objects if o.get('caffmob_tipo') == 'piso'}
assert len(floors) == 1
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
assert floors == {o.as_pointer() for o in context.scene.objects if o.get('caffmob_tipo') == 'piso'}

# Baixar e Enviar pelo operador não disparam updates da 015 nem criam portas/puxadores.
doc = copy.deepcopy(base)
mod = next(c['entrada'] for c in cases if c['caso'] == 'pecas-addon-base-double')
doc['modulos'] = [instance(mod, mod['id'])]
pending = []
def request(method, path, body=None, **kwargs):
    pending.append((method, path, copy.deepcopy(body), kwargs))
    return {'rid': len(pending)}
with patch.object(downloads, 'request', side_effect=request):
    assert bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id']) == {'FINISHED'}
    pending.pop()[3]['callback'](200, doc, {})
    obj = next(o for o in context.scene.objects if o.get('caffmob_modulo'))
    assert not obj.children and not obj.btm_cabinet.structure_id
    before = {o.as_pointer() for o in context.scene.objects}
    assert bpy.ops.caffmob.mobi_enviar_ambiente() == {'FINISHED'}
    method, path, sent, kwargs = pending.pop()
    assert method == 'PUT' and sent['modulos'] == doc['modulos']
    kwargs['callback'](200, dict(sent, version=2), {'ETag':'"2"'})
    assert not obj.children and before == {o.as_pointer() for o in context.scene.objects}

# Conserva a edição de segmento do teste da 061, com o operador do master.
opened = next(c['entrada'] for c in cases if c['caso'] == 'parede-polilinha-aberta')
cena.construir_cena(context, opened)
wall = next(o for o in context.scene.objects if o.get('caffmob_parede'))
context.view_layer.objects.active = wall
before = trechos_da_parede(ler_documento(wall['caffmob_parede']))
s = opened['paredes'][0]['segmentos'][1]
assert bpy.ops.caffmob.mobi_editar_segmento(indice=1, comprimento=s['comprimento'] + 200, espessura=s['espessura'],
    pe_direito_inicial=s['pe_direito_inicial'], pe_direito_final=s['pe_direito_final'], afastamento=0,
    flecha=0, sentido=s['sentido'], tipo=s['tipo']) == {'FINISHED'}
after = trechos_da_parede(ler_documento(wall['caffmob_parede']))
assert abs(after[2][1][1] - before[2][1][1] - 200) < 1e-6
print('BLENDER_CAFFMOB_OK', flush=True)
