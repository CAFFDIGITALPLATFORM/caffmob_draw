"""Campos do editor de escadas (071 D-23, M-05, RN-09) e os campos da escada selecionada no painel (D-28).

`WindowManager.btm_stairs` guarda o editor (fora do arquivo e do Undo). As medidas ficam em mm e aparecem em texto na
unidade do projeto. `WindowManager.btm_stair_sel` lê a escada selecionada; o setter agenda, por timer, o operador que
regrava o spec e regenera as peças, e o passo de desfazer é gravado depois (padrão da onda 8 da 067).
"""
import bpy  # type: ignore

from ..data import units
from ..data.i18n import N_
from . import core

TIPOS = [('reta', N_("Reta"), ''), ('L', N_("Em L (patamar)"), ''), ('U', N_("Em U (patamar)"), '')]
GIROS = [('direita', N_("Direita"), ''), ('esquerda', N_("Esquerda"), '')]
MEDIDAS = ('altura', 'largura', 'largura_total', 'comprimento', 'degrau', 'vao')
CAMPO_DO_SPEC = dict(altura='z', largura='largura', largura_total='x', comprimento='y', degrau='degrau', vao='vao')
LIMITE = dict(altura='altura', largura='largura', largura_total='largura_total', comprimento='comprimento',
              degrau='degrau', vao='vao')


def _unidade():
    return units.get_scene_length_unit(bpy.context.scene)


def texto(mm):
    return units.format_length(mm / 1000, unit=_unidade())


def ler_mm(texto_digitado, zero=False):
    return units.parse_length(texto_digitado, _unidade(), allow_zero=zero) * 1000


def _redesenhar():
    for janela in bpy.context.window_manager.windows:
        for area in janela.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _texto_do_editor(campo):
    def get(self):
        return texto(self.get('mm_' + campo, getattr(core.Escada(), CAMPO_DO_SPEC[campo])))

    def set_(self, valor):
        try:
            mm = ler_mm(valor, zero=campo == 'vao')
        except ValueError:
            return
        lo, hi = core.LIMITES[LIMITE[campo]]
        self['mm_' + campo] = min(max(mm, lo), hi)
        _redesenhar()
    return get, set_


def _ao_mudar_tipo(self, _context):
    e = self.escada()
    x, y = core.planta_confortavel(e)
    self['mm_largura_total'], self['mm_comprimento'] = x, y
    _redesenhar()


def _ao_mudar(self, _context):
    _redesenhar()


class BTM_PG_StairEditor(bpy.types.PropertyGroup):
    tipo: bpy.props.EnumProperty(name=N_("Tipo"), items=TIPOS, update=_ao_mudar_tipo)  # type: ignore
    giro: bpy.props.EnumProperty(name=N_("Giro"), items=GIROS, update=_ao_mudar)  # type: ignore
    altura: bpy.props.StringProperty(name=N_("Altura a vencer"), get=_texto_do_editor('altura')[0],  # type: ignore
                                     set=_texto_do_editor('altura')[1])
    largura: bpy.props.StringProperty(name=N_("Largura do lance"), get=_texto_do_editor('largura')[0],  # type: ignore
                                      set=_texto_do_editor('largura')[1])
    largura_total: bpy.props.StringProperty(name=N_("Largura total"),  # type: ignore
                                            get=_texto_do_editor('largura_total')[0],
                                            set=_texto_do_editor('largura_total')[1])
    comprimento: bpy.props.StringProperty(name=N_("Comprimento"), get=_texto_do_editor('comprimento')[0],  # type: ignore
                                          set=_texto_do_editor('comprimento')[1])
    degrau: bpy.props.StringProperty(name=N_("Espessura do degrau"), get=_texto_do_editor('degrau')[0],  # type: ignore
                                     set=_texto_do_editor('degrau')[1])
    vao: bpy.props.StringProperty(name=N_("Vão entre os lances"), get=_texto_do_editor('vao')[0],  # type: ignore
                                  set=_texto_do_editor('vao')[1])
    espelhos: bpy.props.BoolProperty(name=N_("Espelhos"), default=True, update=_ao_mudar)  # type: ignore
    laterais: bpy.props.BoolProperty(name=N_("Laterais"), default=True, update=_ao_mudar)  # type: ignore
    corrimao: bpy.props.BoolProperty(name=N_("Corrimão"), default=True, update=_ao_mudar)  # type: ignore
    material_frente: bpy.props.PointerProperty(name=N_("Degraus"), type=bpy.types.Material)  # type: ignore
    material_corpo: bpy.props.PointerProperty(name=N_("Espelhos e laterais"), type=bpy.types.Material)  # type: ignore
    editando: bpy.props.StringProperty(name=N_("Escada em edição"))  # type: ignore
    previa: bpy.props.BoolProperty(name=N_("Prévia na vista 3D"), default=True, update=_ao_mudar)  # type: ignore

    def escada(self):
        padrao = core.Escada()
        valores = {CAMPO_DO_SPEC[c]: self.get('mm_' + c, getattr(padrao, CAMPO_DO_SPEC[c])) for c in MEDIDAS}
        return core.Escada(tipo=self.tipo, giro=self.giro, espelhos=self.espelhos, laterais=self.laterais,
                           corrimao=self.corrimao, material_frente=self.material_frente.name if self.material_frente else '',
                           material_corpo=self.material_corpo.name if self.material_corpo else '',
                           **valores).normalizada()

    def carregar(self, e, editando=''):
        e = e.normalizada()
        self.tipo, self.giro = e.tipo, e.giro
        for campo in MEDIDAS:
            self['mm_' + campo] = getattr(e, CAMPO_DO_SPEC[campo])
        self.espelhos, self.laterais, self.corrimao = e.espelhos, e.laterais, e.corrimao
        self.material_frente = bpy.data.materials.get(e.material_frente) if e.material_frente else None
        self.material_corpo = bpy.data.materials.get(e.material_corpo) if e.material_corpo else None
        self.editando = editando

    def inicial(self):
        e = core.Escada()
        e.x, e.y = core.planta_confortavel(e)
        self.carregar(e)


# -- campos da escada selecionada (painel por seleção) ---------------------------------------------------------------
_pendentes = []


def _raiz_selecionada():
    from .scene import root_of
    return root_of(bpy.context.active_object) if bpy.context.active_object is not None else None


def _campo_da_selecao(campo):
    def get(_self):
        from .scene import spec
        raiz = _raiz_selecionada()
        return '' if raiz is None else texto(getattr(spec(raiz), CAMPO_DO_SPEC[campo]))

    def set_(_self, valor):
        raiz = _raiz_selecionada()
        if raiz is None:
            return
        try:
            mm = ler_mm(valor)
        except ValueError:
            return
        agendar(raiz.name, CAMPO_DO_SPEC[campo], mm)
    return get, set_


def _tipo_get(_self):
    from .scene import spec
    raiz = _raiz_selecionada()
    return [t[0] for t in TIPOS].index(spec(raiz).tipo) if raiz is not None else 0


def _tipo_set(_self, indice):
    raiz = _raiz_selecionada()
    if raiz is not None:
        agendar(raiz.name, 'tipo', TIPOS[indice][0])


def agendar(nome, campo, valor):
    _pendentes.append((nome, campo, valor))
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0)


def _tick():
    while _pendentes:
        nome, campo, valor = _pendentes.pop(0)
        try:
            if 'FINISHED' in bpy.ops.caffmob.escada_campo(escada=nome, campo=campo, valor=str(valor)):
                bpy.ops.ed.undo_push(message="Editar escada")
        except RuntimeError as exc:
            state = getattr(bpy.context.window_manager, 'btm_target', None)
            if state is not None:
                state.error = str(exc)
    return None


class BTM_PG_StairSelection(bpy.types.PropertyGroup):
    tipo: bpy.props.EnumProperty(name=N_("Tipo"), items=TIPOS, get=_tipo_get, set=_tipo_set)  # type: ignore
    altura: bpy.props.StringProperty(name=N_("Altura a vencer"), get=_campo_da_selecao('altura')[0],  # type: ignore
                                     set=_campo_da_selecao('altura')[1])
    largura: bpy.props.StringProperty(name=N_("Largura do lance"), get=_campo_da_selecao('largura')[0],  # type: ignore
                                      set=_campo_da_selecao('largura')[1])
    comprimento: bpy.props.StringProperty(name=N_("Comprimento"), get=_campo_da_selecao('comprimento')[0],  # type: ignore
                                          set=_campo_da_selecao('comprimento')[1])


classes = (BTM_PG_StairEditor, BTM_PG_StairSelection)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_stairs = bpy.props.PointerProperty(type=BTM_PG_StairEditor)
    bpy.types.WindowManager.btm_stair_sel = bpy.props.PointerProperty(type=BTM_PG_StairSelection)


def unregister():
    del bpy.types.WindowManager.btm_stair_sel
    del bpy.types.WindowManager.btm_stairs
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
