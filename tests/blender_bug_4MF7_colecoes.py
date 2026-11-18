"""BUG-20261117-4MF7 (RF-08): paredes na coleção Arquitetura > Parede.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_4MF7_colecoes.py

Reprodução: aplicar o rascunho no OK e abrir o Outliner. Antes da correção nenhuma coleção é criada e as paredes ficam
na raiz da cena. Regressões: coleção existente é reaproveitada (sem duplicar nome nem perder dados próprios), parede
que já existia fora da hierarquia migra no OK seguinte, móvel e o empty auxiliar obj_x não são movidos, read_plan
continua lendo as paredes e um OK sem parede nenhuma não cria coleção vazia.
"""

import sys
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
addon.load_file_post(None)

from caffmob_draw.walls2d import apply, model, scene_io  # noqa: E402

ctx = bpy.context
scene = ctx.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
# Sem a extensão instalada não há preferências do add-on (cor da parede); o construtor de paredes precisa delas.
type(ctx.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0))

ARQUITETURA, PAREDE = "Arquitetura", "Parede"


def walls():
    return [o for o in scene.objects if o.get('IS_WALL_BP')]


def arq():
    return scene.collection.children.get(ARQUITETURA)


def colecao_parede():
    return arq().children.get(PAREDE) if arq() is not None else None


# 1. REPRODUÇÃO: o OK cria a hierarquia e põe as paredes dentro dela.
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
assert len(walls()) == 4, len(walls())
assert arq() is not None, "REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura"
assert colecao_parede() is not None, "REPRODUÇÃO (#151): Arquitetura não tem a subcoleção Parede"
assert {o.name for o in colecao_parede().objects} == {o.name for o in walls()}, \
    [o.name for o in colecao_parede().objects]
assert not any(o.name in scene.collection.objects for o in walls()), "a parede ficou na raiz da cena"

# 2. A coleção existente é reaproveitada, sem duplicar nome e sem perder dados próprios.
colecao = colecao_parede()
colecao['marcador'] = 'meu'
apply.apply_plan(ctx, scene_io.read_plan(scene))
assert colecao_parede() is colecao and colecao.get('marcador') == 'meu'
assert sum(1 for c in bpy.data.collections if c.name == ARQUITETURA) == 1
assert sum(1 for c in bpy.data.collections if c.name == PAREDE) == 1
assert len(walls()) == 4, "reaplicar o rascunho atualiza as paredes, não cria outras"

# 3. Parede que já existia fora da hierarquia migra no OK seguinte.
solta = bpy.data.collections.new("Minha coleção")
scene.collection.children.link(solta)
alvo = walls()[0]
colecao_parede().objects.unlink(alvo)
solta.objects.link(alvo)
apply.apply_plan(ctx, scene_io.read_plan(scene))
assert alvo.name in colecao_parede().objects, [c.name for c in alvo.users_collection]
assert alvo.name not in solta.objects

# 4. O que não é parede não é movido: móvel na raiz e o empty auxiliar obj_x continuam onde estavam.
movel = bpy.data.objects.new("Sofá", bpy.data.meshes.new("Sofá"))
scene.collection.objects.link(movel)
auxiliares = [c for w in walls() for c in w.children if c.get('obj_x')]
apply.apply_plan(ctx, scene_io.read_plan(scene))
assert movel.name in scene.collection.objects
assert auxiliares and all(a.name in scene.collection.objects for a in auxiliares)
assert not any(a.name in colecao_parede().objects for a in auxiliares)

# 5. read_plan continua lendo as paredes depois de organizadas.
reread = scene_io.read_plan(scene)
assert len(reread.chains) == 1 and reread.chains[0].closed and reread.chains[0].segment_count() == 4

# 6. OK sem parede nenhuma não cria coleção vazia (sem órfã).
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(colecao_parede())
bpy.data.collections.remove(arq())
bpy.data.collections.remove(solta)
apply.apply_plan(ctx, model.WallPlan([]))
assert not any(c.name in (ARQUITETURA, PAREDE) for c in bpy.data.collections)

print("blender_bug_4MF7_colecoes: OK")
