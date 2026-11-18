"""Grade de ferramentas do Editor de Paredes (BUG-20261117-RP9Q).

Um desenho só para o rascunho clássico (`panels.py`) e a cena v2 (`classico_v2.py`): cada item do enum `tool` vira um
botão com o ícone do próprio enum, e a ferramenta ativa fica pressionada (`depress`). O rótulo curto sai do nome do
enum ("Selecionar/Mover" vira "Selecionar"), então não existe segunda lista de ferramentas para manter em sincronia.
A caixa de tema da planta também vem daqui, para as duas telas (BUG-20261117-6OXN).
"""

from ..data.i18n import tr

COLUNAS = 2


def _curto(nome):
    return nome.split('/')[0].split(' ')[0]


def ferramentas(layout, state):
    """Desenha os botões de ferramenta do estado (`BTM_PG_WallEditorState`)."""
    itens = list(state.bl_rna.properties['tool'].enum_items)
    grade = layout.column(align=True)
    for i, item in enumerate(itens):
        if i % COLUNAS == 0:
            linha = grade.row(align=True)
        op = linha.operator("caffmob.wall_editor_tool", text=_curto(item.name), icon=item.icon,
                            depress=state.tool == item.identifier)
        op.tool = item.identifier


def caixa_tema(layout, state):
    """Escolha do tema da planta: Escuro ou Claro (BUG-20261117-6OXN), igual nas duas telas."""
    caixa = layout.box()
    caixa.label(text=tr("Aparência"), icon='COLOR')
    caixa.prop(state, "tema", expand=True)
