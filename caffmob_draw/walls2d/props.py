"""Estado do Editor de Paredes (T007; data-delta §1).

- `Session` (em memória, uma por vez): rascunho (`model.WallPlan`), vista 2D, seleção, lápis, janela/área do editor.
- `WindowManager.btm_wall_editor`: ferramenta, grade, padrões do lápis e os campos do trecho selecionado. Os campos do
  trecho são propriedades virtuais (`get`/`set`) sobre o rascunho: nada vai para o 3D até o OK (RN-16).
"""

import math

import bpy  # type: ignore

from ..data import units
from ..data.i18n import N_
from . import history, model, selecao_classica


class Session:
    """Editor aberto: rascunho e estado de interação."""

    def __init__(self, plan, scene_name):
        self.plan = plan
        self.v2 = None
        self.scene_name = scene_name
        self.view = None
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None     # quando o editor ocupa uma área da janela atual
        self.selected = None              # (cadeia, trecho)
        self.selected_node = None         # (cadeia, nó) — digitação direta no vértice (D-27)
        self.multi = []                   # 067 onda 8 (D-39): trechos selecionados juntos; `selected` é o último
        self.selection_box = None         # retângulo de seleção em andamento, em pixels (início, fim)
        self.line = model.INNER
        self.drawing = None               # cadeia sendo desenhada a lápis
        self.cursor = None                # posição do cursor no mundo 2D
        self.typed = ""
        self.prompt = None                # 'close' = pergunta de fechamento
        self.error = ""
        self.warnings = []
        self.removed_modules = []         # módulos de trechos apagados (D-21)
        self.remove_modules = False       # "Remover os módulos junto?" (padrão: não)
        self.confirm_pending = False
        self.confirm_signature = None     # rascunho e pé-direito do 1º aviso do OK (DT-04)
        self.request = None               # 'ok' | 'cancel'
        self.signature = model.plan_signature(plan)   # rascunho na abertura (confirmação do Cancelar, D-30)
        self.prompt_chain = None          # cadeia da pergunta de fechamento por arraste (D-34)
        self.pending_point = None         # trecho digitado que chegou ao início, aplicado se a resposta for "Não"
        self.project_height = 2.6         # pé-direito do projeto lido na abertura (D-36)
        self.equalize_height = True       # "Igualar ao pé-direito do projeto" (D-37)
        self.height_mismatches = []
        self.history = history.History(plan)   # Ctrl+Z / Ctrl+Shift+Z no rascunho (BUG-20261007-ZZUK)
        # Feature 009 (T002; RN-02, RN-05, RN-06): direção atual do lápis e mira com alinhamento
        self.direction = None             # radianos; None até o primeiro trecho
        self.direction_locked = False     # só o clique e as setas mudam; o movimento do mouse, nunca
        self.lock_x = None                # (x travado, ponto de referência) da linha vertical da mira
        self.lock_y = None                # (y travado, ponto de referência) da linha horizontal
        self.typed_preview = ""           # "= 16 mm" ou "Valor Inválido"
        self.inference_index = None       # índice do alinhamento; refeito quando o plano muda
        self.inference_signature = None
        self.snap_point = None            # (ponto travado, tipo da trava) da mira para o próximo clique
        # Feature 013 (D-09): lupa com quadrado (zoom janela). Estado só da vista: fora do histórico de desfazer
        # (`history._sign` assina só o rascunho) e sem mexer na ferramenta do painel.
        self.zoom_window = None           # None = desligado; 'ARMED' = lupa apertada; (x, y) px = início do retângulo
        self.zoom_box_end = None          # canto atual do retângulo elástico, em pixels

    def reset_direction(self):
        self.direction, self.direction_locked = None, False
        self.lock_x = self.lock_y = None
        self.typed_preview = ""

    def dirty(self):
        return self.v2.documento != self.v2.original if self.v2 else model.plan_signature(self.plan) != self.signature

    def segment(self):
        if self.selected is None:
            return None, None
        ci, si = self.selected
        if ci >= len(self.plan.chains) or si >= self.plan.chains[ci].segment_count():
            self.selected = None
            return None, None
        return self.plan.chains[ci], si

    def lote(self):
        """Trechos da edição em lote (D-40): os de `multi` que ainda existem, quando são mais de um."""
        self.multi = selecao_classica.validos(self.plan, self.multi)
        return self.multi if len(self.multi) > 1 else []

    def checkpoint(self):
        """Grava um passo de desfazer se o rascunho mudou."""
        return self.v2.checkpoint() if self.v2 else self.history.checkpoint(self.plan)

    def _restore(self, plan):
        if plan is None:
            return False
        self.plan = plan
        self.drawing, self.selected_node, self.typed = None, None, ""
        self.prompt, self.prompt_chain, self.pending_point = None, None, None
        self.reset_direction()
        self.segment()                    # descarta a seleção que não existe mais
        self.multi = selecao_classica.validos(plan, self.multi)
        return True

    def undo(self):
        return self.v2.historico(-1) if self.v2 else self._restore(self.history.undo())

    def redo(self):
        return self.v2.historico(1) if self.v2 else self._restore(self.history.redo())

    def redraw(self):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.as_pointer() == self.area_ptr:
                    area.tag_redraw()


_session = [None]


def session():
    return _session[0]


def start(plan, scene_name):
    _session[0] = Session(plan, scene_name)
    return _session[0]


def end():
    _session[0] = None


# Campos virtuais do trecho -----------------------------------------------------------------------------------

def _guard(apply):
    s = session()
    if s is None:
        return
    try:
        apply()
        s.error = ""
    except ValueError as exc:
        s.error = str(exc)
    s.checkpoint()                        # edição pelo painel também é um passo de desfazer
    s.redraw()


def multiplos(s, field):
    """Os trechos do lote têm valores diferentes em `field` (o painel mostra "Múltiplos")."""
    lote = s.lote() if s else []
    return bool(lote) and selecao_classica.valor_comum(s.plan, lote, field) is selecao_classica.MULTIPLOS


def campo_de_um_trecho_editavel(s, field):
    """Comprimento, ângulos, direção e trava valem um trecho por vez (D-40): cinza em seleção múltipla."""
    return not (s and s.lote()) or field in selecao_classica.CAMPOS_DO_LOTE


def _seg_get(field, default=0.0):
    def get(_self):
        s = session()
        chain, i = s.segment() if s else (None, None)
        if chain is None:
            return default
        if field in selecao_classica.CAMPOS_DO_LOTE and s.lote():
            valor = selecao_classica.valor_comum(s.plan, s.lote(), field)
            return default if valor is selecao_classica.MULTIPLOS else valor
        if field == 'length':
            return chain.face_length(i, s.line)
        if field == 'angle_abs':
            return math.radians(chain.angle_abs(i))
        if field == 'angle_rel':
            return math.radians(chain.angle_rel(i))
        return getattr(chain.segments[i], field)
    return get


def _seg_set(field):
    def set_(_self, value):
        s = session()
        chain, i = s.segment() if s else (None, None)
        if chain is None:
            return
        if field in selecao_classica.CAMPOS_DO_LOTE and s.lote():
            _guard(lambda: selecao_classica.aplicar(s.plan, s.lote(), field, value))     # um passo de desfazer
        elif field == 'length':
            _guard(lambda: chain.set_length(i, value, s.line))
        elif field == 'angle_abs':
            _guard(lambda: chain.set_angle_abs(i, math.degrees(value) % 360.0))
        elif field == 'angle_rel':
            _guard(lambda: chain.set_angle_rel(i, math.degrees(value)))
        else:
            _guard(lambda: chain.set_segment_value(i, field, value))
    return set_


def _type_get(_self):
    s = session()
    chain, i = s.segment() if s else (None, None)
    if chain is None:
        return 0
    if s.lote():
        valor = selecao_classica.valor_comum(s.plan, s.lote(), 'wall_type')
        return 0 if valor is selecao_classica.MULTIPLOS else model.WALL_TYPES.index(valor)
    return model.WALL_TYPES.index(chain.segments[i].wall_type)


def _type_set(_self, value):
    s = session()
    chain, i = s.segment() if s else (None, None)
    if chain is None:
        return
    if s.lote():
        _guard(lambda: selecao_classica.aplicar(s.plan, s.lote(), 'wall_type', model.WALL_TYPES[value]))
    else:
        _guard(lambda: chain.set_segment_value(i, 'wall_type', model.WALL_TYPES[value]))


def _side_get(_self):
    s = session()
    chain, _i = s.segment() if s else (None, None)
    return model.SIDES.index(chain.side) if chain is not None else 0


def _side_set(_self, value):
    s = session()
    chain, i = s.segment() if s else (None, None)
    if chain is None:
        return
    _guard(lambda: setattr(chain, 'side', model.SIDES[value]))      # um passo de desfazer, como os outros campos
    if any(seg.source for seg in chain.segments):
        s.error = N_("Direção trocada em paredes existentes: no OK elas mudam de sentido; portas e janelas acompanham "
                     "e os módulos ficam onde estão.")
    s.redraw()


def _line_get(_self):
    s = session()
    return (model.INNER, model.OUTER).index(s.line) if s else 0


def _line_set(_self, value):
    s = session()
    if s is not None:
        s.line = (model.INNER, model.OUTER)[value]
        s.redraw()


def _equalize_get(_self):
    s = session()
    return bool(s and s.equalize_height)


def _equalize_set(_self, value):
    s = session()
    if s is not None:
        s.equalize_height = bool(value)


def _remove_modules_get(_self):
    s = session()
    return bool(s and s.remove_modules)


def _remove_modules_set(_self, value):
    s = session()
    if s is not None:
        s.remove_modules = bool(value)


def _length(name, field, description=""):
    return bpy.props.FloatProperty(name=name, description=description, subtype='DISTANCE', unit='LENGTH',
                                   precision=1, get=_seg_get(field), set=_seg_set(field))


def _project_unit():
    return units.get_scene_length_unit(bpy.context.scene)


def _text_get(field):
    """Medida do trecho na unidade do projeto, a mesma da planta ("4000 mm"), sem arredondar (BUG-20261007-VQ72)."""
    get = _seg_get(field, None)

    def text(_self):
        value = get(_self)
        return "" if value is None else units.format_length(value, unit=_project_unit())
    return text


def _text_set(field):
    """Lê a medida digitada (sem sufixo = unidade do projeto; aceita mm, cm e m) e grava como o campo numérico."""
    set_value = _seg_set(field)

    def text(_self, value):
        s = session()
        if s is None or s.segment()[0] is None:
            return
        try:
            meters = units.parse_length(value, default_unit=_project_unit(), allow_zero=False)
        except ValueError as exc:
            s.error = str(exc)
            s.redraw()
            return
        set_value(_self, meters)
    return text


def _length_text(name, field, description=""):
    return bpy.props.StringProperty(name=name, description=description, get=_text_get(field), set=_text_set(field))


def _angle(name, field):
    return bpy.props.FloatProperty(name=name, subtype='ANGLE', unit='ROTATION', precision=2,
                                   get=_seg_get(field), set=_seg_set(field))


SIDE_ITEMS = [('LEFT', "Esquerda", "A parede cresce para a esquerda da linha desenhada (face interna)"),
              ('RIGHT', "Direita", "A parede cresce para a direita da linha desenhada (face interna)")]
TYPE_ITEMS = [('NORMAL', "Normal", ""), ('DIVISORIA', "Divisória", "Padrão de espessura 100 mm"),
              ('MURETA', "Mureta", "Padrão de altura 1.100 mm")]


class BTM_PG_WallEditorState(bpy.types.PropertyGroup):
    tool: bpy.props.EnumProperty(
        name="Ferramenta",
        items=[('SELECT', "Selecionar/Mover", "Selecionar trechos e arrastar vértices", 'RESTRICT_SELECT_OFF', 0),
               ('DRAW', "Construir Parede", "Desenhar paredes a lápis", 'GREASEPENCIL', 1),
               ('INVERT', "Inverter Sentido", "Inverter o sentido da parede clicada", 'ARROW_LEFTRIGHT', 2),
               ('ADD_NODE', "Adicionar Vértice", "Dividir o trecho no ponto clicado", 'ADD', 3),
               ('REMOVE_NODE', "Remover Vértice", "Unir os trechos do vértice clicado", 'REMOVE', 4)],
        default='SELECT')  # type: ignore
    grid_size: bpy.props.FloatProperty(name="Tamanho", subtype='DISTANCE', unit='LENGTH', default=1.0, min=0.01,
                                       max=5.0, update=lambda s, c: session() and session().redraw())  # type: ignore
    magnetic: bpy.props.BoolProperty(name="Linhas Magnéticas", default=False,
                                     description="Vértices encaixam nos cruzamentos da grade")  # type: ignore
    new_direction: bpy.props.EnumProperty(
        name="Direção", items=SIDE_ITEMS, default='LEFT',
        description="Lado da espessura nas paredes novas; ao fechar uma sala, a espessura vai para fora")  # type: ignore
    new_thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', default=0.15,
                                           min=0.01, max=2.0)  # type: ignore
    new_height: bpy.props.FloatProperty(name="Pé-direito", subtype='DISTANCE', unit='LENGTH', default=2.6,
                                        min=0.5, max=10.0)  # type: ignore
    line: bpy.props.EnumProperty(name="Linha", items=[('INNER', "Interna", "Face interna (medida real, tracejada)"),
                                                      ('OUTER', "Externa", "Face externa (interna + espessuras)")],
                                 get=_line_get, set=_line_set)  # type: ignore
    length: _length(N_("Comprimento"), 'length', N_("Comprimento na linha selecionada (interna ou externa)"))  # type: ignore
    angle_abs: _angle(N_("Ângulo Absoluto"), 'angle_abs')  # type: ignore
    angle_rel: _angle(N_("Ângulo Relativo"), 'angle_rel')  # type: ignore
    lock_angle: bpy.props.BoolProperty(name="Bloquear Ângulo", get=_seg_get('lock_angle', False),
                                       set=_seg_set('lock_angle'))  # type: ignore
    thickness: _length(N_("Espessura"), 'thickness')  # type: ignore
    height: _length(N_("Pé-direito Inicial"), 'height')  # type: ignore
    end_height: _length(N_("Pé-direito Final"), 'end_height')  # type: ignore
    # O painel usa estes: a unidade do projeto, a mesma da planta (BUG-20261007-VQ72).
    length_text: _length_text(N_("Comprimento"), 'length',
                              N_("Comprimento na linha selecionada; sem unidade, vale a do projeto"))  # type: ignore
    thickness_text: _length_text(N_("Espessura"), 'thickness')  # type: ignore
    height_text: _length_text(N_("Pé-direito Inicial"), 'height')  # type: ignore
    end_height_text: _length_text(N_("Pé-direito Final"), 'end_height')  # type: ignore
    direction: bpy.props.EnumProperty(name="Direção", items=SIDE_ITEMS, get=_side_get, set=_side_set,
                                      description="Lado para onde a espessura cresce; a medida interna não muda")  # type: ignore
    wall_type: bpy.props.EnumProperty(name="Tipo de Parede", items=TYPE_ITEMS, get=_type_get,
                                      set=_type_set)  # type: ignore
    equalize_height: bpy.props.BoolProperty(
        name="Igualar ao pé-direito do projeto",
        description="As paredes listadas passam ao pé-direito das Configurações (Mureta, meia-parede e parede falsa "
                    "ficam como estão)",
        get=_equalize_get, set=_equalize_set)  # type: ignore
    remove_modules: bpy.props.BoolProperty(
        name="Remover os módulos junto?",
        description="Os módulos dos trechos apagados saem com a parede; desmarcado, ficam soltos no lugar",
        get=_remove_modules_get, set=_remove_modules_set)  # type: ignore


classes = (BTM_PG_WallEditorState,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_editor = bpy.props.PointerProperty(type=BTM_PG_WallEditorState)


def unregister():
    end()
    if hasattr(bpy.types.WindowManager, 'btm_wall_editor'):
        del bpy.types.WindowManager.btm_wall_editor
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
