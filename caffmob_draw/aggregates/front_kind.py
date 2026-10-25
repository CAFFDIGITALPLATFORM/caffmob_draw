"""Tipo de frente independente do material e da construção (066, D-18)."""


def front_kind(motion, hinge):
    if motion == 'SLIDE':
        return 'SLIDING'
    if motion == 'DRAWER':
        return 'DRAWER'
    return {'TOP': 'FLIP_UP', 'BOTTOM': 'FLIP_DOWN'}.get(hinge, 'DOOR')
