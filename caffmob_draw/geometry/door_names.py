"""Nomes que o construtor do módulo rápido dá às peças que ele mesmo cria (feature 067, T173; D-25, RN-07).

Só o construtor (`geometry/door_controller.py`) e a migração M-08 (`selection/migration_front_roles.py`) usam estes
sufixos: o construtor acha, apaga e recria pelo nome as portas, o puxador e o Empty controlador que ele criou. Fora
deles, ninguém reconhece frente pelo nome: a frente tem `hb_part_role`, a porta tem `btm_front_hinge` e o Empty tem
`btm_door_controller` (RF-102).
"""

DOOR_L = "_Door_L"
DOOR_R = "_Door_R"
DOOR_FLIP = "_Door_Flip"
DOOR_SUFFIXES = (DOOR_L, DOOR_R, DOOR_FLIP)
CONTROLLER_SUFFIX = "_Controller"
PULL_SUFFIX = "_Puxador"

# Papel e dobradiça gravados pelo construtor em cada porta (D-25).
ROLE_BY_SUFFIX = {DOOR_L: 'DOOR', DOOR_R: 'DOOR', DOOR_FLIP: 'TILT_OUT'}
HINGE_BY_SUFFIX = {DOOR_L: 'L', DOOR_R: 'R', DOOR_FLIP: 'FLIP'}
HINGE_PROP = 'btm_front_hinge'
CONTROLLER_PROP = 'btm_door_controller'


def suffix_of(name):
    """O sufixo de porta do nome, ou ''."""
    return next((s for s in DOOR_SUFFIXES if name.endswith(s)), '')
