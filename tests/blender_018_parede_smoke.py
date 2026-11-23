"""Fumaça no Blender da 018: parede recebe textura pelo nó (T014), material da peça no armário v2 (T011) e o
destaque de parte do conta-gotas (T019).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_018_parede_smoke.py

Verifica:
A. T014: `common.set_cutpart_material` numa parede grava o material nos seis sockets do nó, sem tocar no slot da malha.
B. T014: parede marcada sem o modificador devolve False e não grava material nenhum.
C. T014: piso e teto (`IS_FLOOR_BP`/`IS_CEILING_BP`) recebem o material nos slots.
D. T014: a vista mostra a textura de verdade — o pixel da parede fica com a cor da imagem (render, antes e depois).
E. T011: `build.gerar` aplica o material gravado em `btm_armario_parte.material`, mantém entre gerações e cai no
   acabamento do spec nas outras peças, sem duplicar slot.
F. T019: o conta-gotas acende a peça e nomeia a parte (Porta), as props da sessão existem e o desenho é removido
   no `unregister` e recriado no `register`.
G. T016/T017: a captura guarda a assinatura, e aplicar só com Porta muda as portas dos três armários, sem tocar nas
   laterais.
H. T017: recusa sem origem, recusa sem parte marcada e cancela tudo quando um alvo saiu da cena (sem aplicação
   parcial).
I. T009/T020–T022: o ângulo da chapa gira a textura na normal sem reescrever o enum, o `sync` é idempotente e o
   corte fica com o múltiplo de 90 mais próximo, tanto na chapa do v2 quanto no `btm_part` das bibliotecas.
J. T017+T020: aplicar só a Porta com uma origem a 45° leva o giro para as três portas, e o `btm_grain_rot` das três
   fica igual ao da origem.
"""

import json
import math
import os
import sys
import traceback
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402

from caffmob_draw.armario_v2 import build, spec as spec_mod  # noqa: E402
from caffmob_draw.cutting import part_roles, part_sources  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.operators import viewport_hud  # noqa: E402
from caffmob_draw.texture_library import grain, grain_core, ops_pick, pick, uv_core  # noqa: E402
from caffmob_draw.walls2d import apply as walls_apply, model as walls_model  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = {}
FALHAS = []


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FALHAS.append(nome)


def _imagem():
    imagem = bpy.data.images.new('smoke_parede_tex', 2, 2, alpha=True)
    imagem.pixels = [1.0, 0.0, 0.0, 1.0] * 4
    caminho = os.path.join(ROOT, 'smoke_018_parede_tex.png')
    imagem.filepath_raw = caminho
    imagem.file_format = 'PNG'
    imagem.save()
    return caminho


def _parede():
    env.clean_scene()
    walls_apply.apply_plan(bpy.context, walls_model.WallPlan([walls_model.rectangle(4.0, 3.0)]))
    env.settle()
    paredes = sorted((o for o in bpy.context.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)
    return paredes[0] if paredes else None


def _material(caminho, alvo):
    from caffmob_draw.object_library import retexture
    return retexture.image_material(caminho, 600.0, projection=retexture.projection_for(alvo))


def check_sockets(caminho):
    parede = _parede()
    if parede is None:
        return {'ok': False, 'motivo': 'nenhuma parede criada'}
    mod = common.surface_modifier(parede)
    material = _material(caminho, parede)
    antes_slots = len(parede.data.materials)
    mudou = common.set_cutpart_material(parede, material)
    env.settle()
    from caffmob_draw import compat
    valores = {socket: compat.try_get_gn_input(mod, socket) is material for socket in common.SURFACE_SOCKETS}
    return {'modificador': mod.name if mod is not None else '',
            'sockets': valores,
            'slots_antes': antes_slots, 'slots_depois': len(parede.data.materials),
            'projecao': material.get('btm_texture_projection'),
            'ok': mudou and bool(valores) and all(valores.values()) and antes_slots == len(parede.data.materials)}


def check_parede_sem_no():
    env.clean_scene()
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    objeto = bpy.context.active_object
    objeto.name = 'Parede sem nó'
    objeto['IS_WALL_BP'] = True
    material = bpy.data.materials.new('smoke_nao_deve_entrar')
    mudou = common.set_cutpart_material(objeto, material)
    return {'mudou': mudou, 'slots': [slot.name for slot in objeto.data.materials],
            'ok': mudou is False and len(objeto.data.materials) == 0}


def check_piso_teto():
    env.clean_scene()
    resultado = {}
    for flag, nome in (('IS_FLOOR_BP', 'piso'), ('IS_CEILING_BP', 'teto')):
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        objeto = bpy.context.active_object
        objeto[flag] = True
        material = bpy.data.materials.new(f'smoke_{nome}')
        resultado[nome] = common.set_cutpart_material(objeto, material) and material.name in [
            slot.name for slot in objeto.data.materials]
    return {**resultado, 'ok': all(resultado.values())}


def _camera_e_luz(parede):
    from caffmob_draw import compat  # noqa: F401  (garante o pacote carregado antes do render)
    cantos = [parede.matrix_world @ Vector(canto) for canto in parede.bound_box]
    minimo = Vector([min(p[i] for p in cantos) for i in range(3)])
    maximo = Vector([max(p[i] for p in cantos) for i in range(3)])
    centro = (minimo + maximo) / 2.0
    tamanho = maximo - minimo
    fino = min(range(3), key=lambda i: tamanho[i])
    direcao = Vector((0.0, 0.0, 0.0))
    direcao[fino] = 1.0
    dados = bpy.data.cameras.new('smoke_cam')
    dados.type = 'ORTHO'
    dados.ortho_scale = max(tamanho) * 0.8
    camera = bpy.data.objects.new('smoke_cam', dados)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = centro + direcao * (max(tamanho) * 2.0 + 0.5)
    camera.rotation_euler = (centro - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = camera
    luz_dados = bpy.data.lights.new('smoke_sun', 'SUN')
    luz_dados.energy = 3.0
    luz = bpy.data.objects.new('smoke_sun', luz_dados)
    bpy.context.scene.collection.objects.link(luz)
    luz.rotation_euler = camera.rotation_euler
    cena = bpy.context.scene
    mundo = cena.world or bpy.data.worlds.new('smoke_world')
    cena.world = mundo
    mundo.use_nodes = True
    fundo = mundo.node_tree.nodes.get('Background')
    if fundo is not None:
        fundo.inputs['Strength'].default_value = 0.1
    return cena


def _render(cena, nome, tamanho=32):
    cena.render.engine = 'CYCLES'
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 1
    cena.cycles.use_denoising = False
    cena.render.resolution_x = cena.render.resolution_y = tamanho
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = 'PNG'
    cena.view_settings.view_transform = 'Standard'
    caminho = os.path.join(ROOT, nome)
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    imagem = bpy.data.images.load(caminho)
    largura, altura = imagem.size
    pixels = list(imagem.pixels)
    base = ((altura // 2) * largura + largura // 2) * 4
    cor = tuple(round(v, 3) for v in pixels[base:base + 3])
    bpy.data.images.remove(imagem)
    if os.path.exists(caminho):
        os.remove(caminho)
    return cor


def check_render(caminho):
    parede = _parede()
    if parede is None:
        return {'ok': False, 'motivo': 'nenhuma parede criada'}
    cena = _camera_e_luz(parede)
    # Só a parede medida entra no render: as outras paredes da sala tapariam a vista da câmera.
    for obj in cena.objects:
        obj.hide_render = obj is not parede and obj.type == 'MESH'
    bpy.context.view_layer.update()
    antes = _render(cena, 'smoke_018_parede_antes.png')
    material = _material(caminho, parede)
    common.set_cutpart_material(parede, material)
    env.settle()
    depois = _render(cena, 'smoke_018_parede_depois.png')
    vermelho = depois[0] > depois[1] + 0.15 and depois[0] > depois[2] + 0.15
    return {'antes': antes, 'depois': depois, 'vermelho': vermelho,
            'ok': vermelho and (antes[0] - antes[1]) < 0.15}


def check_material_da_peca():
    env.clean_scene()
    raiz = build.criar_raiz(bpy.context.scene)
    spec = spec_mod.Spec(lateral_esq_ativa=True, lateral_dir_ativa=True, base_inf_ativa=True)
    primeira = build.gerar(raiz, spec)
    lateral = next(o for o in primeira if o.btm_armario_parte.papel == 'LATERAL')
    cliente = bpy.data.materials.new('Chapa do cliente')
    lateral.btm_armario_parte.material = cliente.name
    segunda = build.gerar(raiz, spec)
    nova = next(o for o in segunda if o.btm_armario_parte.papel == 'LATERAL')
    outra = next(o for o in segunda if o.btm_armario_parte.papel == 'BASE_INF')
    slots = [slot.name for slot in nova.data.materials]
    padrao = [slot.name for slot in outra.data.materials]
    return {'escolhido': nova.btm_armario_parte.material, 'slots': slots, 'padrao': padrao,
            'ok': slots == ['Chapa do cliente'] and nova.btm_armario_parte.material == 'Chapa do cliente'
            and padrao == ['Armário v2 madeirado']}


def check_destaque():
    env.clean_scene()
    ctx = bpy.context
    raiz = build.criar_raiz(ctx.scene)
    spec = spec_mod.Spec(lateral_esq_ativa=True, lateral_dir_ativa=True, base_inf_ativa=True, porta_ativa=True)
    pecas = build.gerar(raiz, spec)
    porta = next(o for o in pecas if o.btm_armario_parte.papel == 'PORTA')
    operadores = all(bpy.types.Operator.bl_rna_get_subclass_py(nome) is not None
                     for nome in ('CAFFMOB_OT_texture_pick', 'CAFFMOB_OT_texture_apply_parts'))
    props = hasattr(bpy.types.WindowManager, 'btm_texture_pick')
    pick.iniciar(ctx, [porta])
    pick.apontar(porta)
    ativo, parte, texto, alvos = pick.ativo(), pick.parte(), pick.rotulo(), list(pick.alvos())
    segmentos, ancora = pick.pontos_do_destaque(porta, None, None)       # fundo: sem vista 3D, devolve vazio
    pick.encerrar(ctx)
    parado = not pick.ativo()
    mantidos = list(pick.alvos())                                       # a aplicação por partes conta com eles
    viewport_hud.unregister()
    removido = viewport_hud._texture_highlight_handle is None
    viewport_hud.register()
    recriado = viewport_hud._texture_highlight_handle is not None
    return {'parte': parte, 'rotulo': texto, 'alvos': alvos, 'sem_vista': (segmentos, ancora),
            'operadores': operadores, 'props': props, 'removido': removido, 'recriado': recriado,
            'ok': ativo and parte == uv_core.PORTA and texto == pick.rotulo(uv_core.PORTA) and bool(texto)
            and alvos == [porta.name] and mantidos == [porta.name] and operadores and props and parado
            and removido and recriado and segmentos == [] and ancora is None}


def _tres_armarios():
    """Três armários iguais, com porta e laterais: o cenário do conta-gotas em vários armários (RF-10)."""
    env.clean_scene()
    spec = spec_mod.Spec(lateral_esq_ativa=True, lateral_dir_ativa=True, base_inf_ativa=True, porta_ativa=True)
    grupos = [build.gerar(build.criar_raiz(bpy.context.scene), spec) for _ in range(3)]
    portas = [next(o for o in grupo if o.btm_armario_parte.papel == 'PORTA') for grupo in grupos]
    laterais = [next(o for o in grupo if o.btm_armario_parte.papel == 'LATERAL') for grupo in grupos]
    return portas, laterais


def check_contagotas(caminho):
    portas, laterais = _tres_armarios()
    ctx = bpy.context
    origem = _material(caminho, portas[0])
    common.set_cutpart_material(portas[0], origem)
    pick.iniciar(ctx, portas + laterais)                                 # alvos congelados ao abrir
    capturou = ops_pick.capturar(ctx, portas[0])
    grupo = pick.estado(ctx)
    assinatura = {'nome': grupo.nome, 'size_mm': round(grupo.size_mm, 1), 'tem_path': bool(grupo.path),
                  'origem': grupo.origem}
    pick.encerrar(ctx)
    resultado = bpy.ops.caffmob.texture_apply_parts(porta=True)
    pintadas = all(origem.name in [m.name for m in porta.data.materials] for porta in portas)
    intactas = all('Armário v2 madeirado' in [m.name for m in lateral.data.materials] for lateral in laterais)
    return {'capturou': capturou, 'assinatura': assinatura, 'resultado': str(resultado),
            'portas_pintadas': pintadas, 'laterais_intactas': intactas,
            'ok': capturou and assinatura['tem_path'] and assinatura['origem'] == portas[0].name
            and resultado == {'FINISHED'} and pintadas and intactas}


def check_giro_do_contagotas(caminho):
    """J. T017+T020: aplicar só a Porta leva o giro do veio da origem para as três portas."""
    portas, _laterais = _tres_armarios()
    ctx = bpy.context
    origem = portas[0]
    common.set_cutpart_material(origem, _material(caminho, origem))
    origem.btm_armario_parte.grain_angle = 45.0
    grain.sync(origem)
    esperado = tuple(round(v, 6) for v in origem[grain.ATTR])
    pick.iniciar(ctx, portas)
    capturou = ops_pick.capturar(ctx, origem)
    angulo = float(pick.estado(ctx).angle)
    pick.encerrar(ctx)
    resultado = bpy.ops.caffmob.texture_apply_parts(porta=True)
    angulos = [round(float(porta.btm_armario_parte.grain_angle), 3) for porta in portas]
    giros = [tuple(round(v, 6) for v in porta.get(grain.ATTR, (0.0, 0.0, 0.0))) for porta in portas]
    return {'capturou': capturou, 'angulo': angulo, 'resultado': str(resultado), 'angulos': angulos,
            'giro_igual': giros[0] == esperado and all(giro == esperado for giro in giros),
            'ok': capturou and abs(angulo - 45.0) < 1e-6 and resultado == {'FINISHED'}
            and angulos == [45.0, 45.0, 45.0] and all(giro == esperado for giro in giros)}


def check_veio_em_graus(caminho):
    """I. T009/T020/T021/T022: o ângulo gira o veio na normal e o corte usa o múltiplo de 90 mais próximo."""
    portas, _laterais = _tres_armarios()
    porta = portas[0]
    common.set_cutpart_material(porta, _material(caminho, porta))
    grain.sync(porta)                                    # o material chegou: grava o giro do enum
    grupo = porta.btm_armario_parte
    veio0 = grupo.veio
    antes = tuple(porta[grain.ATTR])
    grupo.grain_angle = 45.0                             # o `update` do ângulo chama `grain.sync` (T021)
    meio = tuple(porta[grain.ATTR])
    grain.sync(porta)                                    # idempotente (T021)
    repetido = tuple(porta[grain.ATTR])
    deltas = [round(b - a, 6) for a, b in zip(antes, meio)]
    eixo = max(range(3), key=lambda i: abs(deltas[i]))
    somou = abs(deltas[eixo] - math.radians(45.0)) < 1e-4 and all(
        abs(deltas[i]) < 1e-6 for i in range(3) if i != eixo)
    grupo.grain_angle = 90.0
    corte = part_roles.grain_direction(grupo.veio, grupo.grain_angle)
    registro = [r for r in part_sources.armario_v2_records(bpy.context.scene) if r.key == porta.name]
    cortou = bool(registro) and registro[0].grain == corte \
        and corte != part_roles.grain_direction(veio0, 0.0)
    bpy.ops.mesh.primitive_plane_add(size=0.6)            # peça de biblioteca: o enum do `btm_part` segue o ângulo
    plano = bpy.context.object
    plano.btm_part.grain = 'H'
    plano.btm_part.grain_angle = 30.0
    biblioteca = part_roles.part_grain(plano)
    plano.btm_part.grain_angle = 90.0
    biblioteca_virada = part_roles.part_grain(plano)
    return {'giro': {'eixo': eixo, 'deltas': deltas, 'somou': somou, 'idempotente': repetido == meio},
            'corte': {'sem_angulo': part_roles.grain_direction(veio0, 0.0), 'com_90': corte,
                      'registro': registro[0].grain if registro else None, 'enum_intacto': grupo.veio == veio0},
            'biblioteca': [biblioteca, biblioteca_virada],
            'ok': somou and repetido == meio and cortou and grupo.veio == veio0
            and biblioteca == 'HORIZONTAL' and biblioteca_virada == 'VERTICAL'}


def check_recusas(caminho):
    portas, _laterais = _tres_armarios()
    ctx = bpy.context
    pick.iniciar(ctx, [portas[0]])
    try:
        bpy.ops.caffmob.texture_apply_parts(porta=True)
        sem_origem = False
    except RuntimeError:
        sem_origem = True
    grupo = pick.estado(ctx)
    grupo.path, grupo.size_mm, grupo.height_mm = caminho, 600.0, 600.0
    sem_marca = bpy.ops.caffmob.texture_apply_parts()
    antes = len(portas[0].data.materials)
    bpy.data.objects.remove(portas[0], do_unlink=True)
    alvo_sumiu = bpy.ops.caffmob.texture_apply_parts(porta=True)
    return {'sem_origem': sem_origem, 'sem_marca': str(sem_marca), 'alvo_sumiu': str(alvo_sumiu),
            'nada_mudou': antes == 1,
            'ok': sem_origem and sem_marca == {'CANCELLED'} and alvo_sumiu == {'CANCELLED'} and antes == 1}


def main():
    caminho = _imagem()
    RESULT['blender'] = bpy.app.version_string
    for nome, funcao in (('A_sockets', lambda: check_sockets(caminho)),
                         ('B_parede_sem_no', check_parede_sem_no),
                         ('C_piso_teto', check_piso_teto),
                         ('D_render', lambda: check_render(caminho)),
                         ('E_material_da_peca', check_material_da_peca),
                         ('F_destaque', check_destaque),
                         ('G_contagotas', lambda: check_contagotas(caminho)),
                         ('H_recusas', lambda: check_recusas(caminho)),
                         ('I_veio_em_graus', lambda: check_veio_em_graus(caminho)),
                         ('J_giro_do_contagotas', lambda: check_giro_do_contagotas(caminho))):
        try:
            RESULT[nome] = funcao()
        except Exception as exc:                     # noqa: BLE001 - a fumaça precisa terminar
            RESULT[nome] = {'erro': str(exc), 'trace': traceback.format_exc()}
        check(nome, bool(RESULT[nome].get('ok')), json.dumps(RESULT[nome], ensure_ascii=False, default=str))
    print('===SMOKE_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, default=str))
    print('===SMOKE_JSON_FIM===')
    arquivo = os.path.join(ROOT, 'smoke_018_parede_tex.png')
    if os.path.exists(arquivo):
        os.remove(arquivo)
    print('OK' if not FALHAS else 'FALHOU: ' + ', '.join(FALHAS))


main()
