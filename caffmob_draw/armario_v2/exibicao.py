"""Exibição do armário v2: variante da preferência e migração da marca de versão (024, T010/T011; RN-01, RN-04).

Dois níveis, como decidido no clarify (D-08):

- `BTM_AddonPreferences.exibicao_armario` é o **padrão de fábrica** dos armários novos;
- `Scene.btm_view_mode` continua sendo o **estado do arquivo** e o controle "Sólido·Textura" da barra lateral manda
  na cena. A variante não inventa mecanismo: liga/desliga o interruptor Linhas que já existe (`ui/view_mode.apply`
  aplica a vista e `overlays/arestas.py` desenha as arestas pretas, com a espessura da preferência).

A migração (T011) percorre uma vez as raízes `btm_armario` com `exibicao_versao == 0`, garante a textura padrão nas
peças sem material, aplica a variante da preferência, grava `exibicao_versao = 1` e avisa uma vez por cena. Rodar de
novo não muda nada (idempotente).
"""

from bpy.app.handlers import persistent  # type: ignore

from ..data.i18n import N_, tr

EXIBICAO_SO, EXIBICAO_LINHAS = 'TEXTURA_SO', 'TEXTURA_LINHAS'
EXIBICAO_ITEMS = [
    (EXIBICAO_SO, N_("Somente textura"), N_("Material puro, sem linhas de aresta")),
    (EXIBICAO_LINHAS, N_("Textura com linhas"), N_("Material com as arestas de todos os objetos")),
]
VARIANTES = {EXIBICAO_SO: (True, False), EXIBICAO_LINHAS: (True, True)}
VERSAO_ATUAL = 1


def linhas(variante):
    """O interruptor Linhas da variante (`TEXTURA_SO` desliga, `TEXTURA_LINHAS` liga)."""
    return VARIANTES.get(variante, VARIANTES[EXIBICAO_SO])[1]


def preferencia():
    """Valor de `exibicao_armario` nas preferências do add-on, ou `TEXTURA_SO` fora do Blender."""
    import bpy  # type: ignore

    pacote = __package__.rsplit('.', 1)[0]
    addon = bpy.context.preferences.addons.get(pacote)
    return getattr(getattr(addon, 'preferences', None), 'exibicao_armario', EXIBICAO_SO)


def aplicar(context, variante=None):
    """Leva a variante para a cena pelo modo de vista existente; devolve True quando aplicou."""
    from ..ui import view_mode

    cena = getattr(context, 'scene', None)
    if cena is None or not hasattr(cena, 'btm_view_mode'):
        return False
    variante = preferencia() if variante is None else variante
    cena.btm_view_mode = 'TEXTURE'
    cena.btm_view_lines = linhas(variante)
    view_mode.apply(context, cena)
    return True


def migrar(cena=None):
    """Migra uma vez cada raiz com `exibicao_versao == 0`; devolve quantas raízes mudaram."""
    import bpy  # type: ignore

    from . import build

    padrao = preferencia()
    migrados = 0
    for raiz in list(bpy.data.objects):
        if not build.e_raiz(raiz):
            continue
        armario = getattr(raiz, 'btm_armario', None)
        if armario is None or armario.exibicao_versao != 0:
            continue
        chapa = build.materiais(armario.acabamento).get('CHAPA')
        for filho in raiz.children:
            parte = getattr(filho, 'btm_armario_parte', None)
            if parte is None or parte.material or filho.type != 'MESH' or chapa is None:
                continue
            if chapa.name not in [material.name for material in filho.data.materials]:
                filho.data.materials.append(chapa)
        armario.exibicao = padrao
        armario.exibicao_versao = VERSAO_ATUAL
        migrados += 1
    return migrados


def _avisar(texto):
    """Aviso único na barra de status das janelas abertas (sem janela, só o registro no console)."""
    import bpy  # type: ignore

    print(texto)
    gerenciador = getattr(bpy.context, 'window_manager', None)
    if gerenciador is None:
        return
    for janela in gerenciador.windows:
        try:
            janela.workspace.status_text_set(texto)
        except (AttributeError, RuntimeError):
            pass


@persistent
def _ao_carregar(_arquivo):
    """Arquivo aberto: migra as raízes pendentes e avisa uma vez."""
    import bpy  # type: ignore

    migrados = migrar(getattr(bpy.context, 'scene', None))
    if migrados:
        _avisar(tr("Textura padrão aplicada em {} armário(s)").format(migrados))


def register():
    import bpy  # type: ignore

    if _ao_carregar not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_ao_carregar)


def unregister():
    import bpy  # type: ignore

    if _ao_carregar in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_ao_carregar)
