"""Núcleo puro de substituição da Biblioteca CAFFMob ("Substituir pelo selecionado", feature 078, T022; D-11 a D-13).

Regras:
- Compatibilidade estrita de família (`DOOR ↔ DOOR`, `WINDOW ↔ WINDOW`, `MODULE ↔ MODULE`).
- Preserva a posição, a orientação e as dimensões do item selecionado na cena:
  - Abertura (`DOOR` / `WINDOW`): mantém `width_mm`, `height_mm`, `sill_mm` e `wall_thickness_mm` do vão selecionado e
    troca `opening_model` e `opening_material`.
  - Móvel (`MODULE`): mantém `width_mm`, `height_mm` e `depth_mm` do móvel selecionado. Na troca entre armário reto e
    armário de canto (`L` ou `OBLIQUE`), `width_mm` e `depth_mm` vão para o braço principal e o segundo braço
    (`right_width_mm`) usa a largura padrão da linha ativa no Padrão de Dimensões (ou é preservado entre dois cantos).
"""

from collections import namedtuple

from ..caffmob.v2 import contrato as v2_contrato
from ..data.i18n import N_, tr
from . import models_core

FAMILIES = ('DOOR', 'WINDOW', 'MODULE')

SelectionTarget = namedtuple(
    'SelectionTarget',
    'family width_mm height_mm depth_mm sill_mm wall_thickness_mm right_width_mm corner_kind line',
    defaults=(0.0, 0.0, 0.0, 150.0, 0.0, 'NONE', 'COZ'),
)

ReplacementPlan = namedtuple(
    'ReplacementPlan',
    'family model_id opening_model opening_material cabinet_type door_swing shelves drawers '
    'corner_kind structure_id width_mm height_mm depth_mm right_width_mm sill_mm wall_thickness_mm line',
)

# Limites dimensionais seguros em milímetros
LIMITS_MM = {
    'DOOR': {'width': (300.0, 6000.0), 'height': (500.0, 4000.0)},
    'WINDOW': {'width': (200.0, 6000.0), 'height': (200.0, 4000.0)},
    'MODULE': {'width': (100.0, 3000.0), 'height': (100.0, 3000.0), 'depth': (100.0, 2000.0)},
}

MSG_NO_SCENE_SELECTION = N_("Selecione uma porta, janela ou móvel na cena para substituir")
MSG_MULTI_SCENE_SELECTION = N_("Selecione apenas um item na cena para substituir")
MSG_UNSUPPORTED_TARGET = N_("O objeto selecionado não é uma porta, janela ou móvel substituível")
MSG_NO_LIBRARY_SELECTION = N_("Escolha um modelo na biblioteca para substituir")
MSG_FAMILY_MISMATCH_DOOR = N_("Incompatível: uma porta só pode ser substituída por outra porta")
MSG_FAMILY_MISMATCH_WINDOW = N_("Incompatível: uma janela só pode ser substituída por outra janela")
MSG_FAMILY_MISMATCH_MODULE = N_("Incompatível: um móvel só pode ser substituído por outro móvel")
MSG_DIMENSION_OUT_OF_RANGE = N_("As dimensões do item selecionado estão fora dos limites permitidos para este modelo")


def candidate_family(candidate):
    """Família (`'DOOR'`, `'WINDOW'`, `'MODULE'` ou `None`) de um `models_core.Model` ou dict de entrada da grade."""
    if candidate is None:
        return None
    if isinstance(candidate, models_core.Model):
        return candidate.kind if candidate.kind in FAMILIES else 'MODULE'
    if isinstance(candidate, dict):
        kind = candidate.get('kind')
        if kind in ('DOOR', 'WINDOW'):
            return kind
        if kind in ('MODEL', 'PRESET', 'MODULE'):
            return 'MODULE'
        model_id = candidate.get('model') or candidate.get('opening_model') or ""
        found = models_core.find_any(model_id) if model_id else None
        if found is not None:
            return found.kind if found.kind in FAMILIES else 'MODULE'
    return None


def validate_replacement(targets, candidate):
    """Valida a seleção da cena (`targets`: lista de `SelectionTarget`) e o candidato da biblioteca.

    Retorna `(True, "")` quando válido ou `(False, mensagem_traduzida)` quando deve recusar.
    """
    if not targets:
        return False, tr(MSG_NO_SCENE_SELECTION)
    if len(targets) > 1:
        return False, tr(MSG_MULTI_SCENE_SELECTION)
    target = targets[0]
    if target is None or target.family not in FAMILIES:
        return False, tr(MSG_UNSUPPORTED_TARGET)
    if candidate is None:
        return False, tr(MSG_NO_LIBRARY_SELECTION)
    cand_fam = candidate_family(candidate)
    if cand_fam not in FAMILIES:
        return False, tr(MSG_NO_LIBRARY_SELECTION)
    if target.family != cand_fam:
        if target.family == 'DOOR':
            return False, tr(MSG_FAMILY_MISMATCH_DOOR)
        if target.family == 'WINDOW':
            return False, tr(MSG_FAMILY_MISMATCH_WINDOW)
        return False, tr(MSG_FAMILY_MISMATCH_MODULE)

    limits = LIMITS_MM[target.family]
    w_min, w_max = limits['width']
    h_min, h_max = limits['height']
    if not (w_min <= float(target.width_mm) <= w_max and h_min <= float(target.height_mm) <= h_max):
        return False, tr(MSG_DIMENSION_OUT_OF_RANGE)
    if target.family == 'MODULE':
        d_min, d_max = limits['depth']
        if not (d_min <= float(target.depth_mm) <= d_max):
            return False, tr(MSG_DIMENSION_OUT_OF_RANGE)
    return True, ""


def can_replace(target, candidate):
    """Atalho booleano para saber se `target` (`SelectionTarget` ou lista) pode ser substituído por `candidate`."""
    if isinstance(target, SelectionTarget):
        targets = [target]
    elif isinstance(target, (list, tuple)):
        targets = list(target)
    else:
        targets = [target] if target is not None else []
    ok, _reason = validate_replacement(targets, candidate)
    return ok


def resolve_candidate_model(candidate):
    """Converte dict da grade ou `Model` num `models_core.Model` (ou `None` se for módulo salvo `.blend`)."""
    if isinstance(candidate, models_core.Model):
        return candidate
    if isinstance(candidate, dict):
        model_id = candidate.get('model') or candidate.get('opening_model') or ""
        if model_id:
            return models_core.find_any(model_id)
    return None


def plan_replacement(target, candidate, *, active_material=None, standard_width_mm=800.0):
    """Calcula o `ReplacementPlan` preservando as medidas do `target`.

    Levanta `ValueError` com a mensagem traduzida se a combinação for inválida.
    """
    ok, reason = validate_replacement([target], candidate)
    if not ok:
        raise ValueError(reason)

    model = resolve_candidate_model(candidate)
    family = target.family

    if family in ('DOOR', 'WINDOW'):
        opening_model = (
            model.opening_model
            if model is not None and model.opening_model
            else (candidate.get('opening_model') if isinstance(candidate, dict) else "")
        )
        if not opening_model:
            opening_model = v2_contrato.PADRAO_ABERTURA[family]['modelo']
        material = active_material if active_material in v2_contrato.MATERIAIS_DE_ABERTURA else None
        if not material:
            material = (
                model.default_material
                if model is not None and model.default_material in v2_contrato.MATERIAIS_DE_ABERTURA
                else v2_contrato.PADRAO_ABERTURA[family]['material']
            )
        return ReplacementPlan(
            family=family,
            model_id=model.id if model is not None else opening_model,
            opening_model=opening_model,
            opening_material=material,
            cabinet_type='BASE',
            door_swing='NONE',
            shelves=0,
            drawers=0,
            corner_kind='NONE',
            structure_id="",
            width_mm=float(target.width_mm),
            height_mm=float(target.height_mm),
            depth_mm=float(target.depth_mm),
            right_width_mm=0.0,
            sill_mm=float(target.sill_mm),
            wall_thickness_mm=float(target.wall_thickness_mm or 150.0),
            line=target.line or 'COZ',
        )

    # Família MODULE
    line = target.line or 'COZ'
    if model is not None:
        corner_kind = model.corner_kind or 'NONE'
        if corner_kind in ('L', 'OBLIQUE'):
            if target.corner_kind in ('L', 'OBLIQUE') and float(target.right_width_mm) > 0:
                right_width_mm = float(target.right_width_mm)
            elif float(standard_width_mm or 0.0) > 0:
                right_width_mm = float(standard_width_mm)
            else:
                right_width_mm = float(model.right_width_mm or target.width_mm)
        else:
            right_width_mm = 0.0
        return ReplacementPlan(
            family='MODULE',
            model_id=model.id,
            opening_model="",
            opening_material="",
            cabinet_type=model.cabinet_type,
            door_swing=model.door_swing,
            shelves=int(model.shelves),
            drawers=int(model.drawers),
            corner_kind=corner_kind,
            structure_id=models_core.model_structure(model, line),
            width_mm=float(target.width_mm),
            height_mm=float(target.height_mm),
            depth_mm=float(target.depth_mm),
            right_width_mm=right_width_mm,
            sill_mm=0.0,
            wall_thickness_mm=0.0,
            line=line,
        )

    # Módulo salvo do usuário (`.blend` em `candidate['blend']`)
    return ReplacementPlan(
        family='MODULE',
        model_id=candidate.get('id', "") if isinstance(candidate, dict) else "",
        opening_model="",
        opening_material="",
        cabinet_type='BASE',
        door_swing='NONE',
        shelves=0,
        drawers=0,
        corner_kind='NONE',
        structure_id="",
        width_mm=float(target.width_mm),
        height_mm=float(target.height_mm),
        depth_mm=float(target.depth_mm),
        right_width_mm=0.0,
        sill_mm=0.0,
        wall_thickness_mm=0.0,
        line=line,
    )
