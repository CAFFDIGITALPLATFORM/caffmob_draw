"""Soltar textura: "Onde deseja aplicar a textura?" (feature 067, T061; D-16, RF-040, RF-041).

`library_panel/ops_drag.drop` abre `caffmob.finish_drop` em vez de aplicar. O diálogo mostra o alvo, a prévia pela
miniatura, os domínios (Interno, Externo, Frentes, Fita) e o escopo (Peça selecionada ou Componente). Nada muda na
cena antes do OK; Cancelar não toca nada. O download só começa depois do OK:
- imagem já no cache: aplica na hora, neste operador (um passo de Undo);
- sem a imagem: baixa e, ao concluir, chama `caffmob.finish_apply` e grava um passo de Undo (o operador termina
  `CANCELLED`, sem passo vazio). Falha ou cancelamento do download não toca a cena.

Item da biblioteca com vários materiais (`entry["materials"]`) exige escolher o material fonte antes do destino.
Móvel sem papéis de acabamento abre a prévia do assistente em vez de aplicar (RF-042).
"""

import bpy  # type: ignore
from bpy.utils import previews  # type: ignore

from ..data.i18n import N_, tr
from . import catalog, downloads

_previews = {'collection': None}
NO_SOURCE = N_("Escolha o material fonte da textura")


def _source_items(self, _context):
    entry = catalog.item(self.key) or {}
    names = [str(m.get('name') if isinstance(m, dict) else m) for m in entry.get('materials') or ()]
    return [('NONE', N_("Escolha…"), "")] + [(n, n, "") for n in names] if len(names) > 1 else [('NONE', "—", "")]


def _thumb_icon(entry):
    """Ícone da miniatura (carregado no invoke, nunca no draw)."""
    path = catalog.thumb_path(entry) if entry else ""
    if not path:
        return 0
    if _previews['collection'] is None:
        _previews['collection'] = previews.new()
    collection = _previews['collection']
    if path not in collection:
        try:
            collection.load(path, path, 'IMAGE')
        except (KeyError, RuntimeError):
            return 0
    return collection[path].icon_id


def material_for(item_id, path):
    """Material de imagem com a escala do catálogo (o mesmo de `texture_library.apply`, sem a variante girada)."""
    from ..object_library import retexture
    from . import bump
    entry = catalog.item(item_id) or {}
    width, height = catalog.default_size(entry) if entry else (catalog.catalog_core.DEFAULT_SIZE_MM,) * 2
    mat = retexture.image_material(path, width, height, rotated=False, texture_id=item_id)
    if entry.get("sha256"):
        mat["btm_texture_sha256"] = entry["sha256"]
        mat["btm_texture_formato"] = entry.get("formato", entry.get("ext", "jpg"))
    bump.request(mat, entry)
    return mat, width


def fetch(item_id, callback):
    """Garante a imagem: `callback(path, erro, imediato)`; resolve o id do MOBI quando a textura é da conta."""
    entry = catalog.item(item_id)
    if entry is None:
        callback("", {"message": "Textura fora do catálogo"}, True)
        return
    if entry.get('mobi_id'):
        def resolved(remote, error):
            if error:
                callback("", error, False)
            else:
                fetch(remote['id'], callback)
        catalog.resolve(item_id, resolved)
        return
    path = downloads.cached(item_id)
    if path:
        callback(path, None, True)
        return
    reason = downloads.unavailable_reason()
    if reason:
        callback("", {"message": reason}, True)
        return
    state = {"inside": True}
    downloads.fetch(item_id, lambda p, e: callback(p, e, state["inside"]))
    state["inside"] = False


class BTM_OT_FinishDrop(bpy.types.Operator):
    """Onde deseja aplicar a textura? Escolha os domínios e o escopo; nada muda antes de confirmar"""
    bl_idname = 'caffmob.finish_drop'
    bl_label = N_("Onde deseja aplicar a textura?")
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    key: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    object_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    internal: bpy.props.BoolProperty(name=N_("Interno"), default=False)  # type: ignore
    external: bpy.props.BoolProperty(name=N_("Externo"), default=False)  # type: ignore
    fronts: bpy.props.BoolProperty(name=N_("Frentes"), default=False)  # type: ignore
    edge: bpy.props.BoolProperty(name=N_("Fita"), default=False)  # type: ignore
    scope: bpy.props.EnumProperty(name=N_("Escopo"), items=(
        ('PART', N_("Peça selecionada"), N_("Só a peça em que a textura caiu")),
        ('COMPONENT', N_("Componente"), N_("Todas as peças do móvel nos domínios escolhidos"))),
        default='COMPONENT')  # type: ignore
    source_material: bpy.props.EnumProperty(name=N_("Material fonte"), items=_source_items)  # type: ignore

    def _target(self):
        from ..customize import finish
        obj = bpy.data.objects.get(self.object_name)
        return obj, finish.owner_of(obj)

    def invoke(self, context, event):
        from ..customize import finish
        obj, owner = self._target()
        if owner is None:
            self.report({'WARNING'}, tr("Solte a textura sobre uma peça, frente, módulo ou objeto"))
            return {'CANCELLED'}
        if not _roles_or_assistant(self, owner):
            return {'CANCELLED'}
        piece_in_set = obj is not owner
        front = finish.is_front(obj)
        self.scope = 'PART' if piece_in_set else 'COMPONENT'        # não expande em silêncio
        self.fronts = front
        self.external = not front
        self._icon = _thumb_icon(catalog.item(self.key))
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        obj, owner = self._target()
        entry = catalog.item(self.key) or {}
        row = layout.row()
        icon = getattr(self, '_icon', 0)
        if icon:
            row.template_icon(icon_value=icon, scale=4.0)
        col = row.column()
        col.label(text=entry.get("name", self.key), icon='TEXTURE')
        if obj is not None:
            col.label(text=tr("Alvo: {}").format(obj.name if obj is owner else f"{obj.name} · {owner.name}"))
        if len(_source_items(self, context)) > 1:
            layout.prop(self, 'source_material')
        col = layout.column(heading=tr("Aplicar em"))
        for prop in ('internal', 'external', 'fronts', 'edge'):
            col.prop(self, prop)
        if obj is not owner:
            layout.prop(self, 'scope', expand=True)

    def _domains(self):
        from ..customize import finish_core as fc
        return {d for d, on in ((fc.INTERNAL, self.internal), (fc.EXTERNAL, self.external),
                                (fc.FRONTS, self.fronts), (fc.EDGE, self.edge)) if on}

    def execute(self, context):
        _obj, owner = self._target()
        if owner is None:
            return {'CANCELLED'}
        if not _roles_or_assistant(self, owner):
            return {'CANCELLED'}
        domains = self._domains()
        if not domains:
            self.report({'WARNING'}, tr("Escolha ao menos um domínio"))
            return {'CANCELLED'}
        if len(_source_items(self, context)) > 1 and self.source_material == 'NONE':
            self.report({'WARNING'}, tr(NO_SOURCE))
            return {'CANCELLED'}
        args = dict(domains=domains, scope=self.scope, object_name=self.object_name, source='LIBRARY')
        key = self.key                            # o download pode terminar depois que o operador acabou
        label = (catalog.item(key) or {}).get("name", key)
        result = {}

        def done(path, error, immediate):
            if error:
                if immediate:
                    result['error'] = error
                elif error.get("code") != "cancelled":
                    _notify(tr("Textura {} não aplicada: {}").format(label, tr(error.get("message") or "")))
                return
            outcome = _apply(path, key, args)
            if immediate:
                result['outcome'] = outcome
                return
            if 'FINISHED' in outcome:
                try:
                    bpy.ops.ed.undo_push(message=tr("Aplicar acabamento"))
                except RuntimeError:
                    pass
                _notify(tr("Textura {} aplicada").format(label))

        fetch(key, done)
        if 'error' in result:
            self.report({'WARNING'}, tr(result['error'].get("message") or ""))
            return {'CANCELLED'}
        if 'outcome' in result:
            return {'FINISHED'} if 'FINISHED' in result['outcome'] else {'CANCELLED'}
        _notify(tr("Baixando {}… a textura entra quando o download terminar").format(label))
        return {'CANCELLED'}                      # o passo de Undo é o da aplicação, no fim do download


def _roles_or_assistant(operator, owner):
    """Sem papéis de acabamento: liga a prévia do assistente em vez de aplicar (RF-042); nunca pintar por suposição."""
    from ..customize import finish, ops_finish_classify
    if finish.has_roles(owner):
        return True
    ops_finish_classify.build_preview(owner)
    operator.report({'WARNING'}, tr("Este móvel não tem papéis de acabamento: classifique as peças no assistente"))
    return False


def _apply(path, item_id, args):
    material, width = material_for(item_id, path)
    return bpy.ops.caffmob.finish_apply('EXEC_DEFAULT', material=material.name, scale_mm=width, **args)


def _notify(text):
    from ..ui import save_feedback
    save_feedback.show(text)


classes = (BTM_OT_FinishDrop,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
    if _previews['collection'] is not None:
        previews.remove(_previews['collection'])
        _previews['collection'] = None
