"""Decisão de aplicar o Padrão de Dimensões à cena (feature 012, T014; D-20, RN-10, RN-11). Python puro.

Cada módulo da cena entra num de três grupos:
- **segue**: módulo CAFFMob no padrão global anterior (ou sem origem gravada);
- **difere**: módulo CAFFMob com padrão próprio, ou criado com outro padrão global;
- **não aplicável**: armário de biblioteca herdada ainda não convertido, item importado, objeto da biblioteca.

As duas perguntas decidem quem é atualizado: Não na 1ª → ninguém; Sim → os que seguem; Sim na 2ª → também os que
diferem.
"""

from collections import namedtuple

CAFFMOB, LEGACY, OTHER = 'CAFFMOB', 'LEGACY', 'OTHER'
ModuleInfo = namedtuple('ModuleInfo', 'name kind standard_uid own')
Plan = namedtuple('Plan', 'follow differ not_applicable legacy')


def is_own(overrides, assembly, origin_assembly, role_thickness):
    """Padrão próprio: valores à mão, montagem diferente da de origem ou espessura por papel definida."""
    return bool(overrides) or assembly != origin_assembly or any(t > 0.0 for t in role_thickness)


def plan(modules, previous_uid, current_uid=None):
    """`current_uid`: o padrão global novo; quem já está nele sem padrão próprio sai das duas listas (2ª pergunta)."""
    follow, differ, not_applicable, legacy = [], [], [], []
    for module in modules:
        if module.kind != CAFFMOB:
            not_applicable.append(module.name)
            if module.kind == LEGACY:
                legacy.append(module.name)
        elif current_uid and not module.own and module.standard_uid == current_uid:
            continue                                    # já recebeu o padrão novo (pergunta 50)
        elif module.own or (module.standard_uid and module.standard_uid != previous_uid):
            differ.append(module.name)
        else:
            follow.append(module.name)
    return Plan(follow, differ, not_applicable, legacy)


def targets(the_plan, apply_all, apply_differ):
    """Nomes dos módulos a atualizar pelas respostas das duas perguntas."""
    if not apply_all:
        return []
    return list(the_plan.follow) + (list(the_plan.differ) if apply_differ else [])
