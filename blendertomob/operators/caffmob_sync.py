"""
CAFF MOB DRAW ligado ao CAFF MOBI (feature 061, RF-36 a RF-39).

- Conectar: o aparelho pede um código ao MOBI (RFC 8628), mostra-o e abre mobi.caff.digital/conectar;
  a pessoa confirma logada no navegador, e o Blender recebe um token próprio. Nunca a senha.
- Listar e baixar: o ambiente vira cena parede a parede (mesmos segmentos, vãos, piso e módulos).
- Enviar: a cena volta ao contrato e sobe com a versão lida; versão divergente (409) abre a escolha.

A conta e a geometria moram em ..caffmob (Python puro, provado pelos casos-ouro). Aqui só há bpy.
"""

import json
import math
import os
import socket
import uuid
import webbrowser

import bpy  # type: ignore

from ..caffmob import conexao
from ..caffmob.chapas import CONSTRUCAO_DE_FABRICA
from ..caffmob.contrato import SCHEMA_AMBIENTE, arredondar_angulo, arredondar_medida, ler_documento, serializar
from ..caffmob.geometria import mudar_comprimento, trechos_da_parede
from ..caffmob.validacao import validar_ambiente
from ..geometry.mesh_gen import generate_cabinet_mesh, generate_floor_from_contract, generate_wall_from_contract

NOME_DA_COLECAO = "CAFF MOB"
PORTAS_DO_ADDON = {"NONE", "LEFT", "RIGHT", "DOUBLE", "FLIP"}
TOLERANCIA_DE_POSICAO_M = 1e-5

# ---------------------------------------------------------------------------
# Sessão com o MOBI
# ---------------------------------------------------------------------------


def base_do_mobi():
    return os.environ.get("CAFFMOB_BASE", conexao.BASE_PADRAO).rstrip("/")


def arquivo_da_sessao():
    """Tokens no diretório do usuário da extensão; fora dela (testes), na configuração do Blender."""
    raiz = (__package__ or "blendertomob").rsplit(".operators", 1)[0]
    try:
        pasta = bpy.utils.extension_path_user(raiz, path="caffmob", create=True)
    except Exception:
        pasta = bpy.utils.user_resource('CONFIG', path="caffmob", create=True)
    return os.path.join(pasta, "sessao.json")


def sessao():
    return conexao.Sessao(arquivo_da_sessao(), base_do_mobi())


# ---------------------------------------------------------------------------
# Contrato → cena
# ---------------------------------------------------------------------------


def _colecao(context):
    colecao = bpy.data.collections.get(NOME_DA_COLECAO)
    if colecao is None:
        colecao = bpy.data.collections.new(NOME_DA_COLECAO)
        context.scene.collection.children.link(colecao)
    return colecao


def _novo_objeto(context, nome, tipo):
    obj = bpy.data.objects.new(nome, bpy.data.meshes.new(f"{nome}_Mesh"))
    _colecao(context).objects.link(obj)
    obj["caffmob_tipo"] = tipo
    return obj


def segmentos_legados(parede):
    """O formato antigo (btm_wall_segments, em metros) que a inserção de abertura ainda lê."""
    return [{"start": [a[0] / 1000.0, a[1] / 1000.0], "end": [b[0] / 1000.0, b[1] / 1000.0], "thickness": s["espessura"] / 1000.0,
             "height": s["pe_direito_inicial"] / 1000.0, "offset": s["afastamento"] / 1000.0}
            for s, (a, b) in zip(parede["segmentos"], trechos_da_parede(parede))]


def regenerar_parede(context, obj, parede, aberturas):
    obj["caffmob_parede"] = serializar(parede)
    obj["btm_wall_segments"] = json.dumps(segmentos_legados(parede))
    obj.btm_plane.object_kind = 'WALL'
    piso = generate_wall_from_contract(obj, parede, aberturas)
    nome_do_piso = f"Piso {parede['id'][:8]}"
    existente = next((o for o in context.scene.objects if o.get("caffmob_tipo") == "piso" and o.get("caffmob_parede_id") == parede["id"]), None)
    if piso:
        alvo = existente or _novo_objeto(context, nome_do_piso, "piso")
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


def criar_modulo(context, modulo):
    obj = _novo_objeto(context, modulo["nome"][:60] or "Módulo", "modulo")
    obj.btm_plane.object_kind = 'MODULE'
    obj.btm_cabinet.width = modulo["largura"] / 1000.0
    obj.btm_cabinet.height = modulo["altura"] / 1000.0
    obj.btm_cabinet.depth = modulo["profundidade"] / 1000.0
    obj.btm_cabinet.thickness = modulo["espessura"] / 1000.0
    obj.btm_cabinet.cabinet_type = modulo["tipo"]
    if modulo["portas"] in PORTAS_DO_ADDON:
        obj.btm_cabinet.door_swing = modulo["portas"]
    generate_cabinet_mesh(obj, modulo["largura"] / 1000.0, modulo["altura"] / 1000.0, modulo["profundidade"] / 1000.0, modulo["espessura"] / 1000.0)
    obj.location = _origem_do_modulo(modulo)
    obj.rotation_euler = (0.0, 0.0, math.radians(modulo["rotacao_z"]))
    obj["caffmob_modulo"] = serializar(modulo)
    obj["caffmob_lugar_m"] = [*obj.location, obj.rotation_euler.z]
    return obj


def construir_cena(context, documento):
    """Reproduz o ambiente parede a parede. Troca o que veio antes do MOBI; não toca no resto da cena."""
    for obj in [o for o in context.scene.objects if o.get("caffmob_tipo")]:
        bpy.data.objects.remove(obj, do_unlink=True)
    for i, parede in enumerate(documento["paredes"]):
        ids = {segmento["id"] for segmento in parede["segmentos"]}
        obj = _novo_objeto(context, f"Parede {i + 1}", "parede")
        regenerar_parede(context, obj, parede, [a for a in documento["aberturas"] if a["segmento_id"] in ids])
    for modulo in documento["modulos"]:
        criar_modulo(context, modulo)
    context.scene["caffmob_ambiente"] = serializar(documento)
    context.scene["caffmob_versao"] = documento["version"]


# ---------------------------------------------------------------------------
# Cena → contrato
# ---------------------------------------------------------------------------


def _mudou(atual, guardado):
    return any(abs(a - b) > TOLERANCIA_DE_POSICAO_M for a, b in zip(atual, guardado))


def _modulo_do_objeto(obj):
    """O módulo guardado; posição e medidas só são relidas do Blender se alguém mexeu (float de 32 bits)."""
    if obj.get("caffmob_modulo"):
        modulo = ler_documento(obj["caffmob_modulo"])
    else:
        modulo = {"id": str(uuid.uuid4()), "nome": obj.name, "tipo": obj.btm_cabinet.cabinet_type, "material": "MDF", "portas": obj.btm_cabinet.door_swing,
                  "construcao": json.loads(json.dumps(CONSTRUCAO_DE_FABRICA)), "chapas_editadas": [], "plano_pai": {"tipo": "FLOOR", "id": None}}
    medidas = {"largura": obj.btm_cabinet.width, "altura": obj.btm_cabinet.height, "profundidade": obj.btm_cabinet.depth, "espessura": obj.btm_cabinet.thickness}
    for campo, metros in medidas.items():
        if campo not in modulo or abs(modulo[campo] - metros * 1000) > 0.05:
            modulo[campo] = arredondar_medida(metros * 1000)
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
        raise ValueError("Esta cena não veio do MOBI: baixe um ambiente antes.")
    documento = ler_documento(cena["caffmob_ambiente"])
    ordem = {parede["id"]: i for i, parede in enumerate(documento["paredes"])}
    paredes = [ler_documento(o["caffmob_parede"]) for o in cena.objects if o.get("caffmob_tipo") == "parede"]
    paredes.sort(key=lambda parede: ordem.get(parede["id"], len(ordem)))
    segmentos = {segmento["id"] for parede in paredes for segmento in parede["segmentos"]}
    aberturas = [abertura for abertura in documento["aberturas"] if abertura["segmento_id"] in segmentos]
    for obj in cena.objects:
        if obj.get("caffmob_abertura"):
            nova = ler_documento(obj["caffmob_abertura"])
            if nova["segmento_id"] in segmentos and all(a["id"] != nova["id"] for a in aberturas):
                aberturas.append(nova)
    modulos = [_modulo_do_objeto(o) for o in cena.objects if o.get("caffmob_tipo") == "modulo" or (o.btm_plane.object_kind == 'MODULE' and not o.get("caffmob_tipo"))]
    ordem_dos_modulos = {modulo["id"]: i for i, modulo in enumerate(documento["modulos"])}
    modulos.sort(key=lambda modulo: ordem_dos_modulos.get(modulo["id"], len(ordem_dos_modulos)))
    return {**documento, "schema": SCHEMA_AMBIENTE, "origem": "blender", "paredes": paredes, "aberturas": aberturas, "modulos": modulos}


# ---------------------------------------------------------------------------
# Operadores
# ---------------------------------------------------------------------------


class BTM_PG_CaffmobAmbiente(bpy.types.PropertyGroup):
    ambiente_id: bpy.props.StringProperty()  # type: ignore
    nome: bpy.props.StringProperty()  # type: ignore
    version: bpy.props.IntProperty()  # type: ignore
    tem_cliente: bpy.props.BoolProperty()  # type: ignore


_espera = {"codigo": None, "sessao": None}


def _redesenhar():
    for janela in bpy.context.window_manager.windows:
        for area in janela.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _consultar():
    """Timer da espera pelo código: devolve o próximo intervalo, ou None para parar."""
    codigo, alvo = _espera["codigo"], _espera["sessao"]
    if codigo is None:
        return None
    wm = bpy.context.window_manager
    try:
        resposta = conexao.consultar_token(alvo.base, codigo["device_code"])
    except Exception as erro:  # rede fora: tenta de novo no próximo intervalo
        wm.caffmob_situacao = f"Sem resposta do MOBI ({erro}). Tentando de novo…"
        return float(codigo.get("interval", 5))
    if "access_token" in resposta:
        alvo.guardar(resposta)
        _espera["codigo"] = None
        wm.caffmob_codigo = ""
        wm.caffmob_situacao = f"Conectado a {alvo.titular}."
        _redesenhar()
        return None
    erro = resposta.get("error")
    if erro == "slow_down":
        codigo["interval"] = codigo.get("interval", 5) + 5
    elif erro != "authorization_pending":
        _espera["codigo"] = None
        wm.caffmob_codigo = ""
        wm.caffmob_situacao = {"access_denied": "Conexão recusada no MOBI.", "expired_token": "O código venceu. Peça outro."}.get(erro, f"Não conectou ({erro}).")
        _redesenhar()
        return None
    return float(codigo.get("interval", 5))


class BTM_OT_CaffmobConectar(bpy.types.Operator):
    """Conectar este Blender ao CAFF MOBI por código, sem senha"""
    bl_idname = "btm.caffmob_conectar"
    bl_label = "Conectar ao MOBI"

    def execute(self, context):
        alvo = sessao()
        try:
            codigo = conexao.pedir_codigo(alvo.base, f"Blender — {socket.gethostname()}"[:80])
        except Exception as erro:
            self.report({'ERROR'}, f"Não foi possível falar com o MOBI: {erro}")
            return {'CANCELLED'}
        _espera.update(codigo=codigo, sessao=alvo)
        wm = context.window_manager
        wm.caffmob_codigo = codigo["user_code"]
        wm.caffmob_situacao = f"Acesse {codigo['verification_uri']} e digite {codigo['user_code']}."
        try:
            webbrowser.open(codigo["verification_uri_complete"])
        except Exception:
            pass
        if not bpy.app.timers.is_registered(_consultar):
            bpy.app.timers.register(_consultar, first_interval=float(codigo.get("interval", 5)))
        return {'FINISHED'}


class BTM_OT_CaffmobDesconectar(bpy.types.Operator):
    """Esquecer o token deste Blender (para revogar no servidor, use Aparelhos conectados no MOBI)"""
    bl_idname = "btm.caffmob_desconectar"
    bl_label = "Desconectar"

    def execute(self, context):
        sessao().esquecer()
        context.window_manager.caffmob_situacao = "Desconectado."
        context.window_manager.caffmob_ambientes.clear()
        return {'FINISHED'}


class BTM_OT_CaffmobListar(bpy.types.Operator):
    """Listar os ambientes do titular no MOBI"""
    bl_idname = "btm.caffmob_listar"
    bl_label = "Listar ambientes"

    def execute(self, context):
        try:
            itens = sessao().listar_ambientes()
        except conexao.ErroDoMobi as erro:
            self.report({'ERROR'}, f"MOBI respondeu {erro.status}: {erro.corpo}")
            return {'CANCELLED'}
        lista = context.window_manager.caffmob_ambientes
        lista.clear()
        for item in itens:
            novo = lista.add()
            novo.ambiente_id, novo.nome, novo.version, novo.tem_cliente = item["id"], item["nome"], item["version"], item["vinculado_a_cliente"]
        self.report({'INFO'}, f"{len(itens)} ambientes.")
        return {'FINISHED'}


class BTM_OT_CaffmobBaixar(bpy.types.Operator):
    """Baixar o ambiente e reproduzi-lo parede a parede"""
    bl_idname = "btm.caffmob_baixar"
    bl_label = "Baixar ambiente"
    bl_options = {'REGISTER', 'UNDO'}

    ambiente_id: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        try:
            documento = sessao().baixar_ambiente(self.ambiente_id)
        except conexao.ErroDoMobi as erro:
            self.report({'ERROR'}, f"MOBI respondeu {erro.status}: {erro.corpo}")
            return {'CANCELLED'}
        construir_cena(context, documento)
        self.report({'INFO'}, f"{documento['nome']}: versão {documento['version']}.")
        return {'FINISHED'}


def _gravar_resultado(context, documento, status, corpo):
    if status == 200:
        documento = {**documento, "version": corpo["version"], "atualizado_em": corpo["atualizado_em"]}
        context.scene["caffmob_ambiente"] = serializar(documento)
        context.scene["caffmob_versao"] = corpo["version"]
        if "caffmob_conflito" in context.scene:
            del context.scene["caffmob_conflito"]
        return True
    context.scene["caffmob_conflito"] = serializar({"versao_atual": corpo["versao_atual"], "documento_atual": corpo["documento_atual"], "meu": documento})
    return False


class BTM_OT_CaffmobEnviar(bpy.types.Operator):
    """Enviar ao MOBI o que mudou, com a versão lida"""
    bl_idname = "btm.caffmob_enviar"
    bl_label = "Enviar ao MOBI"

    def execute(self, context):
        try:
            documento = documento_da_cena(context)
        except ValueError as erro:
            self.report({'ERROR'}, str(erro))
            return {'CANCELLED'}
        erros = validar_ambiente(documento)
        if erros:
            self.report({'ERROR'}, f"O ambiente tem {len(erros)} problema(s): {erros[0]['caminho']} ({erros[0]['codigo']}).")
            return {'CANCELLED'}
        try:
            status, corpo = sessao().enviar_ambiente(documento, context.scene["caffmob_versao"])
        except conexao.ErroDoMobi as erro:
            self.report({'ERROR'}, f"MOBI respondeu {erro.status}: {erro.corpo}")
            return {'CANCELLED'}
        if _gravar_resultado(context, documento, status, corpo):
            self.report({'INFO'}, f"Enviado: versão {corpo['version']}.")
            return {'FINISHED'}
        self.report({'WARNING'}, f"O ambiente mudou no MOBI (versão {corpo['versao_atual']}). Escolha qual fica.")
        if not bpy.app.background:
            bpy.ops.btm.caffmob_resolver_conflito('INVOKE_DEFAULT')
        return {'FINISHED'}


class BTM_OT_CaffmobResolverConflito(bpy.types.Operator):
    """O ambiente mudou no MOBI enquanto você editava: escolha qual versão fica"""
    bl_idname = "btm.caffmob_resolver_conflito"
    bl_label = "O ambiente mudou no MOBI"

    escolha: bpy.props.EnumProperty(
        name="Ficar com",
        items=[('MINHA', "A minha", "Gravar a versão deste Blender por cima da do MOBI"),
               ('DO_MOBI', "A do MOBI", "Trocar a cena pela versão do MOBI")],
        default='DO_MOBI',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return bool(context.scene.get("caffmob_conflito"))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        conflito = ler_documento(context.scene["caffmob_conflito"])
        if self.escolha == 'DO_MOBI':
            construir_cena(context, conflito["documento_atual"])
            del context.scene["caffmob_conflito"]
            return {'FINISHED'}
        try:
            status, corpo = sessao().enviar_ambiente(conflito["meu"], conflito["versao_atual"])
        except conexao.ErroDoMobi as erro:
            self.report({'ERROR'}, f"MOBI respondeu {erro.status}: {erro.corpo}")
            return {'CANCELLED'}
        if not _gravar_resultado(context, conflito["meu"], status, corpo):
            self.report({'WARNING'}, "Mudou de novo no MOBI. Escolha outra vez.")
        return {'FINISHED'}


class BTM_OT_CaffmobEditarSegmento(bpy.types.Operator):
    """Editar um segmento da parede pelo contrato; mudar o comprimento desloca os vértices seguintes"""
    bl_idname = "btm.caffmob_editar_segmento"
    bl_label = "Editar segmento"
    bl_options = {'REGISTER', 'UNDO'}

    indice: bpy.props.IntProperty(name="Segmento", min=0)  # type: ignore
    comprimento: bpy.props.FloatProperty(name="Comprimento (mm)", min=0.1)  # type: ignore
    espessura: bpy.props.FloatProperty(name="Espessura (mm)", min=0.1)  # type: ignore
    pe_direito_inicial: bpy.props.FloatProperty(name="Pé-direito inicial (mm)", min=0.1)  # type: ignore
    pe_direito_final: bpy.props.FloatProperty(name="Pé-direito final (mm)", min=0.1)  # type: ignore
    afastamento: bpy.props.FloatProperty(name="Afastamento (mm)", min=0.0)  # type: ignore
    flecha: bpy.props.FloatProperty(name="Flecha (mm)")  # type: ignore
    sentido: bpy.props.EnumProperty(name="Espessura para", items=[('LEFT', "Esquerda", ""), ('RIGHT', "Direita", "")])  # type: ignore
    tipo: bpy.props.EnumProperty(name="Tipo", items=[('NORMAL', "Alvenaria", ""), ('DRYWALL', "Drywall", ""), ('GLASS', "Vidro", "")])  # type: ignore

    CAMPOS = ("espessura", "pe_direito_inicial", "pe_direito_final", "afastamento", "flecha", "sentido", "tipo")

    @classmethod
    def poll(cls, context):
        return bool(context.object and context.object.get("caffmob_parede"))

    def invoke(self, context, event):
        segmentos = ler_documento(context.object["caffmob_parede"])["segmentos"]
        segmento = segmentos[min(self.indice, len(segmentos) - 1)]
        self.comprimento = segmento["comprimento"]
        for campo in self.CAMPOS:
            setattr(self, campo, segmento[campo])
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.object
        parede = ler_documento(obj["caffmob_parede"])
        if not 0 <= self.indice < len(parede["segmentos"]):
            self.report({'ERROR'}, "Segmento inexistente.")
            return {'CANCELLED'}
        nova = mudar_comprimento(parede, self.indice, arredondar_medida(self.comprimento))
        segmento = nova["segmentos"][self.indice]
        for campo in self.CAMPOS:
            valor = getattr(self, campo)
            segmento[campo] = valor if isinstance(valor, str) else arredondar_medida(valor)
        nova["segmentos"] = [{**s, "comprimento": arredondar_medida(s["comprimento"]), "angulo_absoluto": arredondar_angulo(s["angulo_absoluto"] % 360)} for s in nova["segmentos"]]
        documento = ler_documento(context.scene["caffmob_ambiente"]) if context.scene.get("caffmob_ambiente") else {"aberturas": []}
        ids = {s["id"] for s in nova["segmentos"]}
        aberturas = [a for a in documento["aberturas"] if a["segmento_id"] in ids]
        erros = validar_ambiente({"paredes": [nova], "aberturas": aberturas, "modulos": []})
        if erros:
            self.report({'ERROR'}, f"Recusado: {erros[0]['caminho']} ({erros[0]['codigo']}).")
            return {'CANCELLED'}
        regenerar_parede(context, obj, nova, aberturas)
        return {'FINISHED'}


class BTM_PT_CaffmobDraw(bpy.types.Panel):
    bl_label = "CAFF MOBI"
    bl_idname = "BTM_PT_caffmob_draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFF MOB"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        atual = sessao()
        if wm.caffmob_codigo:
            caixa = layout.box()
            caixa.label(text="Digite no MOBI o código:")
            caixa.label(text=wm.caffmob_codigo, icon='KEY_HLT')
            caixa.label(text=f"{atual.base}/conectar")
        if wm.caffmob_situacao:
            layout.label(text=wm.caffmob_situacao)
        if not atual.conectado:
            layout.operator("btm.caffmob_conectar", icon='LINKED')
            return
        layout.label(text=f"Titular: {atual.titular}", icon='CHECKMARK')
        linha = layout.row(align=True)
        linha.operator("btm.caffmob_listar", icon='FILE_REFRESH')
        linha.operator("btm.caffmob_desconectar", text="", icon='UNLINKED')
        for item in wm.caffmob_ambientes:
            botao = layout.operator("btm.caffmob_baixar", text=f"{item.nome} · v{item.version}", icon='IMPORT')
            botao.ambiente_id = item.ambiente_id
        if context.scene.get("caffmob_ambiente"):
            layout.separator()
            layout.label(text=f"Cena do MOBI · versão {context.scene.get('caffmob_versao')}")
            layout.operator("btm.caffmob_enviar", icon='EXPORT')
            if context.scene.get("caffmob_conflito"):
                layout.operator("btm.caffmob_resolver_conflito", icon='ERROR')
        if context.object and context.object.get("caffmob_parede"):
            layout.separator()
            for i, segmento in enumerate(ler_documento(context.object["caffmob_parede"])["segmentos"]):
                botao = layout.operator("btm.caffmob_editar_segmento", text=f"Segmento {i + 1}: {segmento['comprimento']:g} mm")
                botao.indice = i


classes = (
    BTM_PG_CaffmobAmbiente,
    BTM_OT_CaffmobConectar,
    BTM_OT_CaffmobDesconectar,
    BTM_OT_CaffmobListar,
    BTM_OT_CaffmobBaixar,
    BTM_OT_CaffmobEnviar,
    BTM_OT_CaffmobResolverConflito,
    BTM_OT_CaffmobEditarSegmento,
    BTM_PT_CaffmobDraw,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.caffmob_ambientes = bpy.props.CollectionProperty(type=BTM_PG_CaffmobAmbiente)
    bpy.types.WindowManager.caffmob_codigo = bpy.props.StringProperty()
    bpy.types.WindowManager.caffmob_situacao = bpy.props.StringProperty()


def unregister():
    if bpy.app.timers.is_registered(_consultar):
        bpy.app.timers.unregister(_consultar)
    _espera.update(codigo=None, sessao=None)
    for nome in ("caffmob_ambientes", "caffmob_codigo", "caffmob_situacao"):
        if hasattr(bpy.types.WindowManager, nome):
            delattr(bpy.types.WindowManager, nome)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
