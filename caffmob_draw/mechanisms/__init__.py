"""Registro de mecanismos das frentes e folhas (feature 067, T075; D-23; RF-100 a RF-102).

Quatro mecanismos, sempre pelos dados gravados (nunca pelo nome ou sufixo, RF-102):
- HINGE (giro): folha com movimento SWING e dobradiça à esquerda ou à direita; porta do módulo rápido (L ou R);
- TILT (basculante): SWING com dobradiça no topo ou na base; porta basculante do módulo rápido (FLIP);
- SLIDE (correr): folha com movimento SLIDE, no eixo X do móvel;
- DRAWER (gaveta): folha com movimento DRAWER, que corre em profundidade (para fora da frente).

`of(obj)` acha o adaptador do objeto: a folha agregada (`btm_aggregate`, a pose pelo pivô) ou a porta do módulo
rápido (`btm_front_hinge`, a pose pelo Empty controlador, que move todas as portas do módulo juntas). Cada adaptador
lê e grava a abertura (0 a 1) e descreve os parâmetros com rótulos. Ferragens e puxadores filhos acompanham a folha;
carcaça e vidro fixo não se movem.
"""

from ..data.i18n import N_

HINGE, TILT, SLIDE, DRAWER = 'HINGE', 'TILT', 'SLIDE', 'DRAWER'
LABELS = {HINGE: N_("Giro"), TILT: N_("Basculante"), SLIDE: N_("Correr"), DRAWER: N_("Gaveta")}


class LeafMechanism:
    """Folha agregada (feature 003/007), pela pose do pivô."""

    def __init__(self, obj):
        self.obj = obj
        agg = obj.btm_aggregate
        if agg.motion == 'SLIDE':
            self.kind = SLIDE
        elif agg.motion == 'DRAWER':
            self.kind = DRAWER
        else:
            self.kind = TILT if agg.hinge in ('TOP', 'BOTTOM') else HINGE

    def fraction(self):
        from ..aggregates import leaf
        return leaf.current_fraction(self.obj)

    def set_fraction(self, value):
        self.obj.btm_aggregate.open_value = max(0.0, min(1.0, float(value)))
        return self.fraction()

    def params(self):
        if self.kind in (SLIDE, DRAWER):
            return (('travel', N_("Curso")),) + ((('slide_dir', N_("Sentido")),) if self.kind == SLIDE else ())
        axis = N_("Eixo horizontal") if self.kind == TILT else N_("Dobradiça")
        return (('hinge', axis), ('swing_sign', N_("Sentido")), ('max_angle', N_("Ângulo máximo")))

    def value_label(self):
        agg = self.obj.btm_aggregate
        if self.kind in (SLIDE, DRAWER):
            return "%.0f mm" % (agg.travel * self.fraction() * 1000.0)
        return "%.0f°" % (agg.max_angle * self.fraction())


class QuickDoorMechanism:
    """Porta do módulo rápido: o Empty controlador gira todas as portas do módulo pelo `btm_cabinet.door_open`."""

    def __init__(self, obj):
        self.obj = obj
        self.module = obj.parent
        self.kind = TILT if obj.get('btm_front_hinge') == 'FLIP' else HINGE

    def fraction(self):
        return float(self.module.btm_cabinet.door_open)

    def set_fraction(self, value):
        self.module.btm_cabinet.door_open = max(0.0, min(1.0, float(value)))
        return self.fraction()

    def params(self):
        return (('door_swing', N_("Tipo de abertura")),)

    def value_label(self):
        return "%.0f°" % (90.0 * self.fraction())


def of(obj):
    """O mecanismo do objeto, ou None (carcaça, vidro fixo, peça sem movimento)."""
    if obj is None:
        return None
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate and agg.kind == 'LEAF':
        return LeafMechanism(obj)
    if obj.get('btm_front_hinge') in ('L', 'R', 'FLIP') and obj.parent is not None \
            and getattr(obj.parent, 'btm_cabinet', None) is not None:
        return QuickDoorMechanism(obj)
    return None


def all_of(owner):
    """Os mecanismos de um componente com várias folhas (o editor anima todas juntas)."""
    found, seen = [], set()
    for obj in ([owner] + list(owner.children_recursive)) if owner is not None else []:
        mech = of(obj)
        key = getattr(mech, 'module', None) or obj
        if mech is not None and key.name not in seen:
            seen.add(key.name)
            found.append(mech)
    return found


def register():
    from . import editor
    editor.register()


def unregister():
    from . import editor
    editor.unregister()
