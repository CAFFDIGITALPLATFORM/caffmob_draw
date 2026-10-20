# (063 RF-11; D-04) Pedidos canceláveis; nenhuma mutação da cena durante a espera.
import uuid
import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from ..data.i18n import N_, tr
from ..texture_library import downloads
from . import respostas

CANCELLED = N_('Operação cancelada. A cena foi preservada')
DONE = N_('Operação concluída')
_jobs = {}


class Job:
    def __init__(self, context, message):
        cancel_all()
        self.id, self.scene = uuid.uuid4().hex, context.scene.name
        self.cancelled, self.tickets, self.batch, self.items = False, [], None, []
        self.commit = None
        self.preparo, self.timer = None, None
        _jobs[self.id] = self
        state = context.window_manager.btm_caffmob
        state.ocupado, state.progresso, state.situacao = True, 0.0, tr(message)

    def alive(self):
        return not self.cancelled and self.id in _jobs and bpy.context.scene.name == self.scene

    def progress(self, value):
        if self.alive():
            bpy.context.window_manager.btm_caffmob.progresso = value

    def finish(self, message=DONE):
        if self.alive():
            state = bpy.context.window_manager.btm_caffmob
            state.ocupado, state.progresso, state.situacao = False, 1.0, tr(message)
        _jobs.pop(self.id, None)
        self._limpar_preparo()

    def _limpar_preparo(self):
        if self.timer is not None:
            if bpy.app.timers.is_registered(self.timer):
                bpy.app.timers.unregister(self.timer)
            self.timer = None
        if self.preparo is not None:
            self.preparo.cancelar()
            self.preparo = None

    def preparar_em_passos(self, preparo, concluir):
        """Cede a interface entre unidades; a troca continua no operador com Undo."""
        self.preparo = preparo
        def tick():
            if not self.alive():
                self.cancel()
                return None
            try:
                if preparo.avancar():
                    return 0.01
                self.timer = None
                self.apply(concluir)
            except Exception as exc:
                self.finish(str(exc))
            return None
        self.timer = tick
        bpy.app.timers.register(tick, first_interval=0.01)

    def request(self, method, path, body=None, headers=None, callback=None):
        def received(status, data, incoming):
            if not self.alive():
                return
            if not respostas.compatible(incoming):
                self.finish(respostas.message(status, data, incoming))
                return
            try:
                callback(status, data, incoming)
            except (KeyError, ValueError, TypeError, RuntimeError) as exc:
                self.finish(str(exc))
        ticket = downloads.request(method, path, body, headers=headers, callback=received, response_headers=True)
        self.tickets.append(ticket)
        return ticket

    def apply(self, function):
        if not self.alive():
            return
        self.commit = function
        bpy.ops.caffmob.mobi_aplicar_resultado(job_id=self.id)

    def cancel(self):
        self.cancelled = True
        self._limpar_preparo()
        for ticket in self.tickets:
            downloads.cancel_request(ticket)
        if self.batch:
            self.batch.cancel()
        for item in self.items:
            downloads.cancel(item)
        _jobs.pop(self.id, None)


def cancel_all():
    for job in list(_jobs.values()):
        job.cancel()


class MOBI_OT_Cancelar(bpy.types.Operator):
    """Cancelar os pedidos do MOBI em andamento"""
    bl_idname = 'caffmob.mobi_cancelar'
    bl_label = 'Cancelar operação do MOBI'

    def execute(self, context):
        from ..texture_library import auth, catalog
        auth.cancel_login()
        catalog.cancel()
        cancel_all()
        context.window_manager.btm_caffmob.ocupado = False
        context.window_manager.btm_caffmob.situacao = tr(CANCELLED)
        return {'FINISHED'}


class MOBI_OT_AplicarResultado(bpy.types.Operator):
    """Aplicar o resultado preparado do MOBI"""
    bl_idname = 'caffmob.mobi_aplicar_resultado'
    bl_label = 'Aplicar resultado do MOBI'
    bl_options = {'INTERNAL', 'UNDO'}
    job_id: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        job = _jobs.get(self.job_id)
        if job is None or not job.alive() or job.commit is None:
            return {'CANCELLED'}
        try:
            job.commit(context)
        except (ValueError, RuntimeError, KeyError) as exc:
            job.finish(str(exc))
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        job.finish()
        return {'FINISHED'}


@persistent
def on_load_pre(*_args):
    cancel_all()


classes = (MOBI_OT_Cancelar, MOBI_OT_AplicarResultado)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_pre.append(on_load_pre)


def unregister():
    cancel_all()
    if on_load_pre in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(on_load_pre)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
