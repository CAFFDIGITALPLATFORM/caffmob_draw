# (063 RF-05, RF-06; D-09) Biblioteca do titular e pessoal, com versões.
import uuid
from urllib.parse import quote
import bpy  # type: ignore
from ..data.i18n import N_, tr
from ..caffmob.contrato import ler_documento, serializar, sem_envelope_do_servidor, SCHEMA_MODULO
from ..caffmob.validacao import validar_medidas_do_modulo
from ..texture_library import downloads
from . import cena, tarefas, texturas, respostas
from .ops_ambientes import sent

LISTING = N_('Listando modelos do titular e pessoais…')
LOADING = N_('Baixando modelo e texturas…')
SENDING = N_('Enviando modelo ao MOBI…')
EMPTY = N_('A biblioteca está vazia. Crie um modelo na Biblioteca do MOBI')
NO_MODEL = N_('Este módulo ainda não tem modelo de origem. Envie como modelo novo')
INVALID = N_('Documento recusado: {}')


def instance(document, module_id, posicao=None, rotacao=0, plano=None):
    raw = sem_envelope_do_servidor(document)
    raw.pop('schema', None)
    return dict(raw, id=module_id, posicao=posicao or {'x':0, 'y':0, 'z':0}, rotacao_z=rotacao,
                plano_pai=plano or {'tipo':'FLOOR', 'id':None})


def model_document(document, model_id):
    raw = sem_envelope_do_servidor(document)
    for key in ('posicao', 'rotacao_z', 'plano_pai', 'modelo'):
        raw.pop(key, None)
    return dict(raw, id=model_id, schema=SCHEMA_MODULO, origem='blender')


def replace_model(job, document, object_name, version):
    def ready(images):
        def commit(context):
            obj = bpy.data.objects.get(object_name)
            if obj is not None:
                current = cena._modulo_do_objeto(obj)
                updated = instance(document, current['id'], current['posicao'], current['rotacao_z'], current['plano_pai'])
                updated['modelo'] = {'id':obj.get('caffmob_modelo_id', document['id']), 'version':version}
                obj['caffmob_modulo'] = serializar(updated)
                obj['caffmob_modelo_versao'] = version
                cena.malha_do_modulo(obj, updated, images)
                obj.scale = (1.0, 1.0, 1.0)
                obj.location = cena._origem_do_modulo(updated)
            context.window_manager.btm_caffmob.conflito_local = ''
            context.window_manager.btm_caffmob.conflito_mobi = ''
        job.apply(commit)
    job.batch = texturas.TextureBatch([document], ready, job.progress)
    job.batch.start()


class MOBI_OT_ListarModelos(bpy.types.Operator):
    """Listar os modelos do titular e pessoais com as imagens"""
    bl_idname = 'caffmob.mobi_listar_modelos'
    bl_label = 'Listar modelos do MOBI'

    def execute(self, context):
        job = tarefas.Job(context, LISTING)
        results = {}
        def listed(scope, status, body, incoming):
            if status != 200:
                job.finish(respostas.message(status, body, incoming))
                return
            results[scope] = body if isinstance(body, list) else body.get('itens', [])
            job.progress(len(results) * 0.15)
            if len(results) != 2:
                return
            entries = results['titular'] + results['pessoal']
            if not entries:
                context.window_manager.btm_caffmob.modelos.clear()
                job.finish(EMPTY)
                return
            pending = {'count': len(entries)}
            def image_done(raw, path):
                if not job.alive():
                    return
                raw['imagem'] = path or ''
                pending['count'] -= 1
                job.progress(0.3 + (1 - pending['count'] / len(entries)) * 0.6)
                if pending['count']:
                    return
                def commit(context):
                    target = context.window_manager.btm_caffmob.modelos
                    target.clear()
                    for raw in entries:
                        item = target.add()
                        item.id, item.nome, item.version = raw['id'], raw['nome'], raw['version']
                        item.categoria, item.escopo, item.imagem = raw.get('categoria', ''), raw.get('escopo', ''), raw['imagem']
                job.apply(commit)
            for index, raw in enumerate(entries):
                item_id = 'modelo-imagem:' + raw['id'] + ':' + str(raw['version'])
                entry = {'id': item_id, 'url':'/api/draw/v1/modelos/' + raw['id'] + '/imagem', 'ext':'png', 'bytes':0}
                job.items.append(item_id)
                downloads.fetch(item_id, lambda path, error, raw=raw: image_done(raw, path), entry=entry)
        for scope in ('titular', 'pessoal'):
            job.request('GET', '/api/draw/v1/modelos?escopo=' + scope,
                        callback=lambda s,b,h,scope=scope: listed(scope,s,b,h))
        return {'FINISHED'}


class MOBI_OT_BaixarModelo(bpy.types.Operator):
    """Inserir uma cópia da versão atual ou escolhida de um modelo"""
    bl_idname = 'caffmob.mobi_baixar_modelo'
    bl_label = 'Inserir modelo do MOBI'
    modelo_id: bpy.props.StringProperty()  # type: ignore
    versao: bpy.props.IntProperty(name='Versão do modelo', min=0, default=0)  # type: ignore

    def execute(self, context):
        model_id, requested = self.modelo_id, self.versao
        job = tarefas.Job(context, LOADING)
        path = '/api/draw/v1/modelos/' + quote(model_id, safe='')
        if requested:
            path += '/versoes/' + str(requested)
        def received(status, body, incoming):
            if status != 200:
                job.finish(respostas.message(status, body, incoming))
                return
            errors = validar_medidas_do_modulo(body)
            if errors:
                job.finish(tr(INVALID).format(errors))
                return
            version = requested or int(incoming.get('ETag', '0').strip('"') or body.get('version', 0))
            copy = instance(body, str(uuid.uuid4()))
            copy['modelo'] = {'id':model_id, 'version':version}
            def ready(images):
                def commit(context):
                    obj = cena.criar_modulo(context, copy, images)
                    obj['caffmob_modelo_id'], obj['caffmob_modelo_versao'] = model_id, version
                    context.view_layer.objects.active = obj
                    obj.select_set(True)
                job.apply(commit)
            job.batch = texturas.TextureBatch([copy], ready, job.progress)
            job.batch.start()
        job.request('GET', path, callback=received)
        return {'FINISHED'}


class MOBI_OT_EnviarModelo(bpy.types.Operator):
    """Enviar um módulo do MOBI como versão nova ou modelo novo"""
    bl_idname = 'caffmob.mobi_enviar_modelo'
    bl_label = 'Enviar modelo ao MOBI'
    novo: bpy.props.BoolProperty(name='Criar modelo novo', default=False)  # type: ignore
    escopo: bpy.props.EnumProperty(name='Biblioteca', items=[('titular','Do titular',''),('pessoal','Pessoal','')])  # type: ignore
    nome: bpy.props.StringProperty(name='Nome do modelo')  # type: ignore
    categoria: bpy.props.StringProperty(name='Categoria do modelo')  # type: ignore

    def execute(self, context):
        obj = context.object
        if obj is None or not obj.get('caffmob_modulo'):
            self.report({'WARNING'}, tr(cena.MODULO_015))
            return {'CANCELLED'}
        document = cena._modulo_do_objeto(obj)
        errors = validar_medidas_do_modulo(document)
        if errors:
            self.report({'WARNING'}, tr(INVALID).format(errors))
            return {'CANCELLED'}
        model_id = obj.get('caffmob_modelo_id') or document.get('modelo', {}).get('id')
        version = obj.get('caffmob_modelo_versao') or document.get('modelo', {}).get('version', 0)
        if not self.novo and not model_id:
            self.report({'WARNING'}, tr(NO_MODEL))
            return {'CANCELLED'}
        object_name = obj.name
        job = tarefas.Job(context, SENDING)
        model_doc = model_document(document, str(uuid.uuid4()) if self.novo else model_id)
        if self.novo:
            payload = {'escopo':self.escopo, 'nome':self.nome or document['nome'], 'categoria':self.categoria, 'documento':model_doc}
            job.request('POST', '/api/draw/v1/modelos', payload,
                        callback=lambda s,b,h: sent(job,'modelo',model_doc,s,b,h,object_name))
        else:
            job.request('PUT', '/api/draw/v1/modelos/' + model_id, model_doc,
                        {'If-Match':'"{}"'.format(version)},
                        lambda s,b,h: sent(job,'modelo',model_doc,s,b,h,object_name))
        return {'FINISHED'}


classes = (MOBI_OT_ListarModelos, MOBI_OT_BaixarModelo, MOBI_OT_EnviarModelo)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
