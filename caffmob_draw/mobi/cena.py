# (063 RF-01; D-09, D-10, D-11) Adaptador da cena do MOBI, sem rede.
import json
import math
import uuid
import bmesh  # type: ignore
import bpy  # type: ignore
from ..data.i18n import N_
from ..caffmob.chapas import caixas_das_chapas
from ..caffmob.contrato import SCHEMA_AMBIENTE, arredondar_angulo, arredondar_medida, ler_documento, serializar
from ..caffmob.geometria import trechos_da_parede
from ..caffmob.validacao import validar_ambiente
from ..geometry.mesh_gen import generate_floor_from_contract, generate_wall_from_contract

NOME_DA_COLECAO = "CAFF MOB"
TOLERANCIA_DE_POSICAO_M = 1e-5
MODULO_015 = N_("O módulo do construtor da 015 não pode ser enviado ao MOBI. Use um módulo baixado do MOBI")
SEM_AMBIENTE = N_("Esta cena não veio do MOBI: baixe um ambiente antes")


def _colecao(context):
    colecao = bpy.data.collections.get(NOME_DA_COLECAO)
    if colecao is None:
        colecao = bpy.data.collections.new(NOME_DA_COLECAO)
        context.scene.collection.children.link(colecao)
    return colecao


def _novo_objeto(context, nome, tipo, colecao=None):
    obj = bpy.data.objects.new(nome, bpy.data.meshes.new(f"{nome}_Mesh"))
    (colecao if colecao is not None else _colecao(context)).objects.link(obj)
    obj["caffmob_tipo"] = tipo
    return obj


def segmentos_legados(parede):
    """O formato antigo (btm_wall_segments, em metros) que a inserção de abertura ainda lê."""
    return [{"start": [a[0] / 1000.0, a[1] / 1000.0], "end": [b[0] / 1000.0, b[1] / 1000.0], "thickness": s["espessura"] / 1000.0,
             "height": s["pe_direito_inicial"] / 1000.0, "offset": s["afastamento"] / 1000.0}
            for s, (a, b) in zip(parede["segmentos"], trechos_da_parede(parede))]


def regenerar_parede(context, obj, parede, aberturas, colecao=None):
    obj["caffmob_parede"] = serializar(parede)
    obj["caffmob_aberturas"] = serializar(aberturas)
    obj["btm_wall_segments"] = json.dumps(segmentos_legados(parede))
    obj.btm_plane.object_kind = 'WALL'
    piso = generate_wall_from_contract(obj, parede, aberturas)
    nome_do_piso = f"Piso {parede['id'][:8]}"
    existente = next((o for o in (colecao.objects if colecao is not None else context.scene.objects) if o.get("caffmob_tipo") == "piso" and o.get("caffmob_parede_id") == parede["id"]), None)
    if piso:
        alvo = existente or _novo_objeto(context, nome_do_piso, "piso", colecao)
        alvo["caffmob_parede_id"] = parede["id"]
        generate_floor_from_contract(alvo, piso["vertices"])
    elif existente:
        bpy.data.objects.remove(existente, do_unlink=True)


def _origem_do_modulo(modulo):
    """Canto da frente à esquerda (contrato) → origem do armário no Blender (meio da traseira, na base)."""
    r = math.radians(modulo["rotacao_z"])
    u, v = modulo["largura"] / 2, modulo["profundidade"]
    x = modulo["posicao"]["x"] + u * math.cos(r) - v * math.sin(r)
    y = modulo["posicao"]["y"] + u * math.sin(r) + v * math.cos(r)
    return (x / 1000.0, y / 1000.0, modulo["posicao"]["z"] / 1000.0)


def _material_da_chapa(imagens, textura_id):
    """Material por textura (Principled BSDF + Image Texture, e Bump se houver mapa); sem textura, o neutro."""
    if not textura_id or textura_id not in imagens:
        material = bpy.data.materials.get("CAFFMOB chapa") or bpy.data.materials.new("CAFFMOB chapa")
        material.diffuse_color = (0.85, 0.77, 0.67, 1.0)
        return material
    from ..texture_library import catalog, downloads, bump
    from ..object_library import retexture
    entry = catalog.item(textura_id)
    if entry is None:
        return _material_da_chapa({}, None)
    width, height = catalog.default_size(entry)
    material = retexture.image_material(imagens[textura_id]["imagem"], width, height, texture_id=textura_id)
    material["btm_texture_sha256"] = entry["sha256"]
    material["btm_texture_formato"] = entry["formato"]
    if imagens[textura_id].get("bump"):
        bump.attach(material, imagens[textura_id]["bump"])
    return material


def malha_do_modulo(obj, modulo, imagens, material_da_chapa=None):
    """O módulo chapa a chapa: uma caixa por chapa, com o material dela e a imagem inteira em cada face (o veio
    vertical gira a imagem 90°). Origem como a do armário do addon: meio da traseira, na base."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    materiais = []
    larg, prof = modulo["largura"], modulo["profundidade"]
    for caixa in caixas_das_chapas(modulo):
        material = (material_da_chapa or _material_da_chapa)(imagens, caixa["textura_id"])
        if material not in materiais:
            materiais.append(material)
        x0, y0, z0 = (caixa["x"] - larg / 2) / 1000.0, (caixa["y"] - prof) / 1000.0, caixa["z"] / 1000.0
        x1, y1, z1 = x0 + caixa["dx"] / 1000.0, y0 + caixa["dy"] / 1000.0, z0 + caixa["dz"] / 1000.0
        v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
        cantos = [(0, 0), (1, 0), (1, 1), (0, 1)] if caixa["veio"] != "VERTICAL" else [(0, 1), (0, 0), (1, 0), (1, 1)]
        for indices in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            face = bm.faces.new([v[i] for i in indices])
            face.material_index = materiais.index(material)
            for laco, canto in zip(face.loops, cantos):
                laco[uv].uv = canto
    obj.data.clear_geometry()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    for material in materiais:
        obj.data.materials.append(material)
    obj.data.update()


def criar_modulo(context, modulo, imagens=None, colecao=None, material_da_chapa=None):
    obj = _novo_objeto(context, modulo["nome"][:60] or "Módulo", "modulo", colecao)
    obj.btm_plane.object_kind = 'MODULE'
    malha_do_modulo(obj, modulo, imagens or {}, material_da_chapa)
    obj.location = _origem_do_modulo(modulo)
    obj.rotation_euler = (0.0, 0.0, math.radians(modulo["rotacao_z"]))
    obj["caffmob_modulo"] = serializar(modulo)
    obj["caffmob_lugar_m"] = [*obj.location, obj.rotation_euler.z]
    return obj


def construir_cena(context, documento, imagens=None):
    """Monta uma coleção de preparo; só troca a cena depois que tudo estiver pronto."""
    erros = validar_ambiente(documento)
    if erros:
        raise ValueError(str(erros))
    preparo = bpy.data.collections.new("CAFF MOB preparo")
    try:
        for i, parede in enumerate(documento["paredes"]):
            ids = {segmento["id"] for segmento in parede["segmentos"]}
            obj = _novo_objeto(context, "Parede {}".format(i + 1), "parede", preparo)
            regenerar_parede(context, obj, parede,
                             [a for a in documento["aberturas"] if a["segmento_id"] in ids], preparo)
        for modulo in documento["modulos"]:
            criar_modulo(context, modulo, imagens, preparo)
    except Exception:
        for obj in list(preparo.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(preparo)
        raise
    antigos = [o for o in context.scene.objects if o.get("caffmob_tipo")]
    colecao = _colecao(context)
    for obj in list(preparo.objects):
        colecao.objects.link(obj)
    bpy.data.collections.remove(preparo)
    for obj in antigos:
        bpy.data.objects.remove(obj, do_unlink=True)
    context.scene["caffmob_ambiente"] = serializar(documento)
    context.scene["caffmob_versao"] = documento.get("version", 0)


# ---------------------------------------------------------------------------
# Cena → contrato
# ---------------------------------------------------------------------------


def _mudou(atual, guardado):
    return any(abs(a - b) > TOLERANCIA_DE_POSICAO_M for a, b in zip(atual, guardado))


def _modulo_do_objeto(obj):
    """O módulo guardado; posição e medidas só são relidas do Blender se alguém mexeu (float de 32 bits)."""
    if not obj.get("caffmob_modulo"):
        raise ValueError(MODULO_015)
    modulo = ler_documento(obj["caffmob_modulo"])
    for campo, escala in (("largura", obj.scale.x), ("altura", obj.scale.z), ("profundidade", obj.scale.y)):
        if abs(escala - 1) > 1e-6:
            modulo[campo] = arredondar_medida(modulo[campo] * escala)
    lugar = [*obj.location, obj.rotation_euler.z]
    if "posicao" not in modulo or _mudou(lugar, obj.get("caffmob_lugar_m", [math.inf] * 4)):
        r = obj.rotation_euler.z
        u, v = modulo["largura"] / 2, modulo["profundidade"]
        x = obj.location.x * 1000 - (u * math.cos(r) - v * math.sin(r))
        y = obj.location.y * 1000 - (u * math.sin(r) + v * math.cos(r))
        modulo["posicao"] = {"x": arredondar_medida(x), "y": arredondar_medida(y), "z": arredondar_medida(obj.location.z * 1000)}
        modulo["rotacao_z"] = arredondar_angulo(math.degrees(r))
    return modulo


def documento_da_cena(context):
    cena = context.scene
    if not cena.get("caffmob_ambiente"):
        raise ValueError(SEM_AMBIENTE)
    if any(getattr(getattr(o, "btm_cabinet", None), "structure_id", "") and not o.get("caffmob_modulo") for o in cena.objects):
        raise ValueError(MODULO_015)
    documento = ler_documento(cena["caffmob_ambiente"])
    ordem = {parede["id"]: i for i, parede in enumerate(documento["paredes"])}
    paredes = [ler_documento(o["caffmob_parede"]) for o in cena.objects if o.get("caffmob_parede")]
    paredes.sort(key=lambda parede: ordem.get(parede["id"], len(ordem)))
    segmentos = {segmento["id"] for parede in paredes for segmento in parede["segmentos"]}
    aberturas = [abertura for abertura in documento["aberturas"] if abertura["segmento_id"] in segmentos]
    for obj in cena.objects:
        if obj.get("caffmob_abertura"):
            nova = ler_documento(obj["caffmob_abertura"])
            if nova["segmento_id"] in segmentos and all(a["id"] != nova["id"] for a in aberturas):
                aberturas.append(nova)
    modulos = [_modulo_do_objeto(o) for o in cena.objects if o.get("caffmob_modulo")]
    ordem_dos_modulos = {modulo["id"]: i for i, modulo in enumerate(documento["modulos"])}
    modulos.sort(key=lambda modulo: ordem_dos_modulos.get(modulo["id"], len(ordem_dos_modulos)))
    return {**documento, "schema": SCHEMA_AMBIENTE, "origem": "blender", "paredes": paredes, "aberturas": aberturas, "modulos": modulos}


