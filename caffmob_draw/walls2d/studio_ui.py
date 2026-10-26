"""Ações e campos da prancheta v2 no Blender (operador `caffmob.wall_studio_action`, `WindowManager.btm_wall_studio`) e
o despacho dos eventos. O desenho e os painéis do editor ficam em `classico_v2`; regras e documento, em
studio/paredes_edicao."""
import bpy
from ..caffmob.v2 import paredes_edicao as pe
from ..data import units
from ..data.i18n import tr
from . import props
from . import studio_painel as sp
from .studio import pontos


def mm(s):
    return tuple(v * 1000 for v in s.cursor) if s.cursor else (0, 0)


def tela(view, q):
    return view.to_screen((q[0] / 1000, q[1] / 1000))


def erro(s):
    s.error = '; '.join(e['mensagem'] for e in s.v2.erros)


def medir(texto):
    # O painel do Studio usa milímetros; a expressão mantém contas e sufixos do addon.
    return units.parse_length(texto, 'MM', allow_zero=False) * 1000


def tratar(op, context, event, s, view, pixel):
    from .studio_interacao import tratar as despachar
    desenhando = s.v2.desenhando
    try:
        resultado = despachar(op, event, s, view, pixel)
    except ValueError as exc:
        s.error = str(exc)
        return True
    if desenhando and not s.v2.desenhando and s.v2.paredes():
        view.fit(s.v2.bounds(), margin=0.15)
    elif s.v2.desenhando and s.v2.inicio:
        x, y = tela(view, s.v2.inicio)
        if (x < 40 or y < 40 or x > view.rect[2] - 40 or y > view.rect[3] - 40) and s.v2.paredes():
            view.fit(s.v2.bounds(), margin=0.15)
    if event.type == 'LEFTMOUSE' and s.v2.abertura:
        a = next((a for a in s.v2.documento['aberturas'] if a['id'] == s.v2.abertura), None)
        if a:
            campos = context.window_manager.btm_wall_studio
            for k in ('posicao', 'largura', 'altura', 'peitoril'):
                setattr(campos, 'abertura_' + k, a[k])
    return resultado

def _v():
    s = props.session()
    return s.v2 if s else None


def campo(chave, padrao=0):
    def get(_):
        v = _v()
        t = v.trecho()[2] if v else None
        return float(t.get(chave, padrao)) if t else float(padrao)
    def set_(_, valor):
        v = _v()
        if v and v.selecao:
            v.editar(**{('angulo' if chave == 'angulo_absoluto' else chave): valor})
            v.checkpoint()
            erro(props.session())
            props.session().redraw()
    return bpy.props.FloatProperty(name={'angulo_absoluto':'Direção (°)', 'flecha':'Arco (mm)',
        'comprimento':'Comprimento (mm)', 'espessura':'Espessura (mm)', 'pe_direito_inicial':'Altura inicial (mm)',
        'pe_direito_final':'Altura final (mm)', 'afastamento':'Afastamento (mm)'}[chave], get=get, set=set_, precision=1)


def medida_texto_get(_):
    return _v().texto if _v() else ''


def medida_texto_set(_, valor):
    if _v():
        _v().texto = valor


def material_itens(_, context):
    v = _v()
    return [('nenhum', 'Sem material', '')] + [(m['id'], m['nome'], '') for m in v.documento['materiais']] if v else []


def material_campo(face):
    chave = 'material_' + face + '_id'
    def get(_):
        v = _v()
        t = v.trecho()[2] if v else None
        ids = [x[0] for x in material_itens(None, None)]
        valor = t.get(chave) if t else None
        return ids.index(valor) if valor in ids else 0
    def set_(_, valor):
        v = _v()
        ids = [x[0] for x in material_itens(None, None)]
        v.tentar(pe.material_da_face(v.documento, v.selecao, 'interna' if face == 'interno' else 'externa',
                                    None if valor == 0 else ids[valor]))
        v.checkpoint()
        erro(props.session())
    return bpy.props.EnumProperty(name='Face interna' if face == 'interno' else 'Face externa', items=material_itens, get=get, set=set_)


def ponto_campo(eixo):
    def get(_):
        v = _v()
        if not v or not v.ponto:
            return 0.0
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        return float(pontos(p)[v.ponto[1]][eixo])
    def set_(_, valor):
        v = _v()
        if not v or not v.ponto:
            return
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        q = list(pontos(p)[v.ponto[1]])
        q[eixo] = valor
        v.tentar(pe.mover_vertice(v.documento, *v.ponto, dict(x=q[0], y=q[1])))
        v.checkpoint()
        erro(props.session())
        props.session().redraw()
    return bpy.props.FloatProperty(name='Posição X (mm)' if eixo == 0 else 'Posição Y (mm)', get=get, set=set_, precision=1)


def padrao_get(_):
    return float(_v().espessura) if _v() else 150.0


def padrao_set(_, valor):
    if _v():
        _v().espessura = valor


def divisao_get(_):
    return float(_v().divisao) if _v() else 0.0


def divisao_set(_, valor):
    if _v():
        _v().divisao = valor


def material_itens_lote(_, context):
    v = _v()
    return [('nenhum', 'vários', '')] + [(m['id'], m['nome'], '') for m in v.documento['materiais']] if v else []


def _lote():
    v = _v()
    if not v:
        return None, None
    p = sp.painel_de(v)
    p.preparar_lote(v)
    return v, p


def lote_texto(chave):
    def get(_):
        _v2, p = _lote()
        return sp.formatar(p.lote.get(chave, '')) if p else ''
    def set_(_, valor):
        v, p = _lote()
        if not p:
            return
        try:
            if valor.strip():
                sp.numero(valor)
            p.lote[chave] = valor.strip()
            props.session().error = ''
        except ValueError as exc:
            props.session().error = str(exc)
    return bpy.props.StringProperty(name='Espessura (mm)' if chave == 'espessura' else 'Altura (mm)', get=get, set=set_)


def lote_material(face):
    chave = 'material_' + face + '_id'
    def get(_):
        _v2, p = _lote()
        ids = [x[0] for x in material_itens_lote(None, None)]
        return ids.index(p.lote.get(chave)) if p and p.lote.get(chave) in ids else 0
    def set_(_, valor):
        _v2, p = _lote()
        if p:
            ids = [x[0] for x in material_itens_lote(None, None)]
            p.lote[chave] = '' if valor == 0 else ids[valor]
    return bpy.props.EnumProperty(name='Face interna' if face == 'interno' else 'Face externa', items=material_itens_lote,
                                  get=get, set=set_)


def lote_ocultar_get(_):
    _v2, p = _lote()
    return bool(p and p.lote.get('ocultar'))


def lote_ocultar_set(_, valor):
    _v2, p = _lote()
    if p:
        p.lote['ocultar'] = bool(valor)


class CamposStudio(bpy.types.PropertyGroup):
    lote_espessura: lote_texto('espessura')
    lote_altura: lote_texto('altura')
    lote_material_interno: lote_material('interno')
    lote_material_externo: lote_material('externo')
    lote_ocultar: bpy.props.BoolProperty(name='Ocultar selecionadas', get=lote_ocultar_get, set=lote_ocultar_set)
    ponto_x: ponto_campo(0)
    ponto_y: ponto_campo(1)
    padrao: bpy.props.FloatProperty(name='Espessura padrão (mm)', min=1, get=padrao_get, set=padrao_set)
    divisao: bpy.props.FloatProperty(name='Posição da divisão (mm)', get=divisao_get, set=divisao_set)
    comprimento: campo('comprimento')
    espessura: campo('espessura')
    angulo: campo('angulo_absoluto')
    arco: campo('flecha')
    altura: campo('pe_direito_inicial')
    altura_final: campo('pe_direito_final')
    afastamento: campo('afastamento')
    texto: bpy.props.StringProperty(name='Medida (mm)', get=medida_texto_get, set=medida_texto_set)
    modelo_largura: bpy.props.FloatProperty(name='Largura (mm)', default=4000, min=10)
    modelo_profundidade: bpy.props.FloatProperty(name='Profundidade (mm)', default=3000, min=10)
    abertura_posicao: bpy.props.FloatProperty(name='Posição (mm)', default=0)
    abertura_largura: bpy.props.FloatProperty(name='Largura (mm)', default=800, min=1)
    abertura_altura: bpy.props.FloatProperty(name='Altura (mm)', default=2100, min=1)
    abertura_peitoril: bpy.props.FloatProperty(name='Peitoril (mm)', default=0, min=0)
    material_interno: material_campo('interno')
    material_externo: material_campo('externo')


class AcaoStudio(bpy.types.Operator):
    bl_idname = 'caffmob.wall_studio_action'
    bl_label = 'Editar parede'
    bl_options = {'INTERNAL'}
    acao: bpy.props.StringProperty()
    valor: bpy.props.FloatProperty()
    alvo: bpy.props.StringProperty()

    def execute(self, context):
        s = props.session()
        if not s or not s.v2:
            return {'CANCELLED'}
        v, campos = s.v2, context.window_manager.btm_wall_studio
        try:
            if self.acao == 'iniciar':
                v.iniciar()
            elif self.acao in ('retangulo', 'L', 'U'):
                v.modelo(self.acao, campos.modelo_largura, campos.modelo_profundidade)
            elif self.acao == 'ambiente_atual':
                v.tentar(pe.ambiente_atual_na_prancheta(v.documento, v.original, v.pavimento_id, v.gerar_id, v.espessura))
                v.concluir()
            elif self.acao == 'fixar':
                p = v.previa(mm(s), s.view.scale / 1000 if s.view else 0.1, medir(v.texto or '1000'))
                v.fixar(p['fim'])
            elif self.acao == 'confirmar' and v.texto and v.selecao:
                v.editar(comprimento=medir(v.texto))
                v.texto = ''
            elif self.acao == 'fechar':
                v.fechar()
            elif self.acao == 'concluir':
                v.concluir()
            elif self.acao == 'continuar':
                v.continuar()
            elif self.acao == 'direcao':
                if v.desenhando:
                    v.direcao, v.direcao_travada = self.valor, True
                elif v.selecao:
                    v.editar(angulo=self.valor)
            elif self.acao == 'ortogonal':
                v.ortogonal = not v.ortogonal
            elif self.acao == 'dividir':
                v.dividir()
            elif self.acao == 'excluir' and len(v.selecionadas) > 1:
                v.pedir_exclusao()
            elif self.acao in ('excluir', 'confirmar_excluir'):
                v.excluir(self.acao == 'confirmar_excluir')
            elif self.acao in ('todas', 'pronto', 'lote_aplicar', 'confirmar_exclusao', 'cancelar_exclusao', 'alternar'):
                sp.executar(s, self.acao, self.alvo or None)
            elif self.acao == 'ocultar':
                _, _, t = v.trecho()
                v.tentar((pe.restaurar_trecho if t['estado'] == 'oculto' else pe.ocultar_trecho)(v.documento, v.selecao))
            elif self.acao in ('inicio', 'fim'):
                v.ancora = self.acao
            elif self.acao in ('interna', 'externa', 'eixo'):
                v.lado = self.acao
            elif self.acao == 'espessura':
                v.tentar(pe.aplicar_espessura_a_todas(v.documento, v.pavimento_id, v.espessura))
            elif self.acao in ('DOOR', 'WINDOW'):
                if v.abertura_nova(self.acao):
                    a = next(a for a in v.documento['aberturas'] if a['id'] == v.abertura)
                    for k in ('posicao', 'largura', 'altura', 'peitoril'):
                        setattr(campos, 'abertura_' + k, a[k])
            elif self.acao == 'editar_abertura':
                v.tentar(pe.editar_abertura(v.documento, v.abertura,
                    {k: getattr(campos, 'abertura_' + k) for k in ('posicao', 'largura', 'altura', 'peitoril')}))
            elif self.acao == 'desfazer':
                s.undo()
            elif self.acao == 'refazer':
                s.redo()
            erro(s)
            if self.acao in ('retangulo', 'L', 'U', 'ambiente_atual', 'concluir') and s.view and v.paredes():
                s.view.fit(v.bounds(), margin=0.15)
            v.checkpoint()
        except ValueError as exc:
            s.error = str(exc)
        s.redraw()
        return {'FINISHED'}


def botao(layout, texto, acao, valor=0, depress=False, icon='NONE', alvo=''):
    op = layout.operator('caffmob.wall_studio_action', text=tr(texto), depress=depress, icon=icon)
    op.acao, op.valor, op.alvo = acao, valor, alvo


def campo_texto(layout, dono, nome, dica):
    """Campo de texto com a dica "vários" quando o Blender aceita `placeholder` (5.x)."""
    try:
        layout.prop(dono, nome, placeholder=dica)
    except TypeError:
        layout.prop(dono, nome)


def painel_lote(layout, context, s):
    """Alternativa nativa do painel "N paredes" (T133): os mesmos campos e a mesma regra de "vários"."""
    v = s.v2
    c = context.window_manager.btm_wall_studio
    n = len(v.selecionadas)
    layout.label(text=tr('{} paredes selecionadas').format(n), icon='STICKY_UVS_LOC')
    campo_texto(layout, c, 'lote_espessura', tr('vários'))
    campo_texto(layout, c, 'lote_altura', tr('vários'))
    layout.prop(c, 'lote_material_interno')
    layout.prop(c, 'lote_material_externo')
    layout.prop(c, 'lote_ocultar')
    botao(layout, 'Aplicar às selecionadas', 'lote_aplicar', icon='CHECKMARK')
    botao(layout, 'Excluir selecionadas', 'excluir', icon='TRASH')


classes = (CamposStudio, AcaoStudio)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_studio = bpy.props.PointerProperty(type=CamposStudio)


def unregister():
    del bpy.types.WindowManager.btm_wall_studio
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
