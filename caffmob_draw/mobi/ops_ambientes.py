# (063 RF-01, RF-06, RF-11; D-03, D-04) Ambientes e conflitos do MOBI.
import json
from urllib.parse import urlencode, quote
import bpy  # type: ignore
from ..data.i18n import N_, tr
from ..caffmob.contrato import ler_documento, serializar, sem_envelope_do_servidor
from ..caffmob.validacao import validar_ambiente
from . import cena, tarefas, texturas, respostas
from .cena import regenerar_parede
from ..caffmob.geometria import mudar_comprimento
from ..caffmob.contrato import arredondar_medida, arredondar_angulo

LISTING = N_('Listando ambientes do MOBI…')
LOADING = N_('Baixando ambiente e texturas…')
SENDING = N_('Enviando ambiente ao MOBI…')
INVALID = N_('Documento recusado: {}')
CONFLICT = N_('HTTP 409: escolha entre a versão do Blender e a versão do MOBI')


def same_document(a, b):
    return serializar(sem_envelope_do_servidor(a)) == serializar(sem_envelope_do_servidor(b))


def prepare(job, document, callback):
    job.progress(0.2)
    job.batch = texturas.TextureBatch(document.get('modulos', []),
        lambda images: job.apply(lambda context: callback(context, images)) if job.alive() else None,
        lambda value: job.progress(0.2 + value * 0.7))
    job.batch.start()


def set_conflict(context, kind, local, response, object_name=''):
    state = context.window_manager.btm_caffmob
    state.conflito_local = serializar(local)
    state.conflito_mobi = serializar(response['documento_atual'])
    state.conflito_versao = response['versao_atual']
    state.conflito_id, state.conflito_tipo = local['id'], kind
    state.conflito_objeto = object_name
    if not bpy.app.background:
        bpy.ops.caffmob.mobi_resolver_conflito('INVOKE_DEFAULT')


def sent(job, kind, document, status, body, incoming, object_name=''):
    if status == 409 and body.get('documento_atual') and same_document(document, body['documento_atual']):
        status, body = 200, {'version': body['versao_atual']}
    if status in (200, 201):
        def commit(context):
            updated = dict(document, version=body['version'])
            if kind == 'ambiente':
                context.scene['caffmob_ambiente'] = serializar(updated)
                context.scene['caffmob_versao'] = body['version']
            else:
                obj = bpy.data.objects.get(object_name)
                if obj is not None:
                    obj['caffmob_modelo_id'] = body.get('id', document['id'])
                    obj['caffmob_modelo_versao'] = body['version']
                    stored = ler_documento(obj['caffmob_modulo'])
                    stored['modelo'] = {'id':obj['caffmob_modelo_id'], 'version':body['version']}
                    obj['caffmob_modulo'] = serializar(stored)
            state = context.window_manager.btm_caffmob
            state.conflito_local = state.conflito_mobi = ''
        job.apply(commit)
    elif status == 409 and body.get('documento_atual'):
        set_conflict(bpy.context, kind, document, body, object_name)
        job.finish(CONFLICT)
    else:
        job.finish(respostas.message(status, body, incoming))


class MOBI_OT_ListarAmbientes(bpy.types.Operator):
    """Listar uma página de ambientes do titular"""
    bl_idname = 'caffmob.mobi_listar_ambientes'
    bl_label = 'Listar ambientes do MOBI'
    mais: bpy.props.BoolProperty(default=False)  # type: ignore

    def execute(self, context):
        state = context.window_manager.btm_caffmob
        previous = [dict(id=i.id, nome=i.nome, version=i.version) for i in state.ambientes] if self.mais else []
        cursor = state.proximo_ambiente if self.mais else ''
        job = tarefas.Job(context, LISTING)
        def received(status, body, incoming):
            if status != 200:
                job.finish(respostas.message(status, body, incoming))
                return
            def commit(context):
                target = context.window_manager.btm_caffmob
                target.ambientes.clear()
                for raw in previous + body['itens']:
                    item = target.ambientes.add()
                    item.id, item.nome, item.version = raw['id'], raw['nome'], raw['version']
                target.proximo_ambiente = body.get('proximo') or ''
            job.apply(commit)
        job.request('GET', '/api/draw/v1/ambientes?' + urlencode({'depois':cursor or '0'}), callback=received)
        return {'FINISHED'}


class MOBI_OT_BaixarAmbiente(bpy.types.Operator):
    """Baixar o ambiente e preparar as texturas antes de trocar a cena"""
    bl_idname = 'caffmob.mobi_baixar_ambiente'
    bl_label = 'Baixar ambiente do MOBI'
    ambiente_id: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        job = tarefas.Job(context, LOADING)
        def received(status, body, incoming):
            if status != 200:
                job.finish(respostas.message(status, body, incoming))
                return
            errors = validar_ambiente(body)
            if errors:
                job.finish(tr(INVALID).format(errors))
                return
            prepare(job, body, lambda context, images: cena.construir_cena(context, body, images))
        job.request('GET', '/api/draw/v1/ambientes/' + quote(self.ambiente_id, safe=''), callback=received)
        return {'FINISHED'}


class MOBI_OT_EnviarAmbiente(bpy.types.Operator):
    """Enviar as paredes e os módulos de contrato desta cena"""
    bl_idname = 'caffmob.mobi_enviar_ambiente'
    bl_label = 'Enviar ambiente ao MOBI'

    def execute(self, context):
        try:
            document = cena.documento_da_cena(context)
            errors = validar_ambiente(document)
            if errors:
                raise ValueError(tr(INVALID).format(errors))
        except ValueError as exc:
            self.report({'WARNING'}, tr(str(exc)))
            return {'CANCELLED'}
        job = tarefas.Job(context, SENDING)
        version = context.scene.get('caffmob_versao', document.get('version', 0))
        method, path = ('PUT', '/api/draw/v1/ambientes/' + document['id']) if version else ('POST', '/api/draw/v1/ambientes')
        job.request(method, path, document, {'If-Match':'"{}"'.format(version)} if version else {},
                    lambda status, body, headers: sent(job, 'ambiente', document, status, body, headers))
        return {'FINISHED'}


class MOBI_OT_ResolverConflito(bpy.types.Operator):
    """Comparar e escolher qual documento fica no MOBI"""
    bl_idname = 'caffmob.mobi_resolver_conflito'
    bl_label = 'Resolver conflito com o MOBI'
    escolha: bpy.props.EnumProperty(name='Ficar com', items=[
        ('BLENDER', 'Versão do Blender', 'Enviar o documento deste Blender'),
        ('MOBI', 'Versão do MOBI', 'Usar o documento atual do MOBI')], default='MOBI')  # type: ignore

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.btm_caffmob.conflito_local)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        state = context.window_manager.btm_caffmob
        row = self.layout.row()
        for label, raw in ((N_('Versão do Blender'), state.conflito_local), (N_('Versão do MOBI'), state.conflito_mobi)):
            box = row.box()
            box.label(text=tr(label))
            doc = ler_documento(raw)
            box.label(text=doc.get('nome', ''))
            for key in ('version', 'largura', 'altura', 'profundidade'):
                if key in doc:
                    box.label(text='{}: {}'.format(key, doc[key]))
            for key in ('paredes', 'aberturas', 'modulos', 'chapas_editadas'):
                if key in doc:
                    box.label(text='{}: {}'.format(key, len(doc[key])))
        self.layout.prop(self, 'escolha')

    def execute(self, context):
        state = context.window_manager.btm_caffmob
        local, remote = ler_documento(state.conflito_local), ler_documento(state.conflito_mobi)
        kind, version, object_name = state.conflito_tipo, state.conflito_versao, state.conflito_objeto
        job = tarefas.Job(context, SENDING)
        choice = self.escolha
        chosen = remote if choice == 'MOBI' else local
        path = '/api/draw/v1/{}/{}'.format('ambientes' if kind == 'ambiente' else 'modelos', state.conflito_id)
        def received(status, body, incoming):
            if status == 200 and choice == 'MOBI':
                if kind == 'ambiente':
                    updated = dict(remote, version=body['version'])
                    prepare(job, updated, lambda context, images: cena.construir_cena(context, updated, images))
                    state.conflito_local = state.conflito_mobi = ''
                else:
                    from .ops_biblioteca import replace_model
                    replace_model(job, remote, object_name, body['version'])
            else:
                sent(job, kind, chosen, status, body, incoming, object_name)
        job.request('PUT', path, chosen, {'If-Match':'"{}"'.format(version)}, received)
        return {'FINISHED'}


class MOBI_OT_EditarSegmento(bpy.types.Operator):
    """Editar um segmento da parede pelo contrato; mudar o comprimento desloca os vértices seguintes"""
    bl_idname = "caffmob.mobi_editar_segmento"
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
        documento = {"aberturas": json.loads(obj.get("caffmob_aberturas", "[]"))}
        ids = {s["id"] for s in nova["segmentos"]}
        aberturas = [a for a in documento["aberturas"] if a["segmento_id"] in ids]
        erros = validar_ambiente({"paredes": [nova], "aberturas": aberturas, "modulos": []})
        if erros:
            self.report({'ERROR'}, tr(INVALID).format(erros))
            return {'CANCELLED'}
        regenerar_parede(context, obj, nova, aberturas)
        return {'FINISHED'}


classes = (MOBI_OT_ListarAmbientes, MOBI_OT_BaixarAmbiente, MOBI_OT_EnviarAmbiente,
           MOBI_OT_ResolverConflito, MOBI_OT_EditarSegmento)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
