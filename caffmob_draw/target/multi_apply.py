"""Medidas na seleção múltipla (027, RF-04): o que o painel mostra e o que a confirmação aplica.

`SIZE_FIELDS` são as propriedades de item que valem para vários objetos: largura, altura, profundidade e espessura.
`sizes` devolve, na ordem de `selected_uids`, a medida de cada objeto — `None` onde ela não existe (peça de chapa não
tem largura editável, por exemplo), para o painel saber o que é comum e o que diverge. `apply` escreve a mesma medida
em todos os objetos, devolvendo quantos mudaram, quantos ficaram de fora e as recusas com o nome do objeto; quem chama
(o operador de confirmação) faz tudo num passo de Desfazer.
"""

from ..selection import editing

SIZE_FIELDS = ('width', 'height', 'depth', 'thickness')


def _thickness(context, obj):
    """Espessura da chapa do objeto, pelo alvo de medida da peça."""
    from . import snapshot

    sheet = snapshot.sheet_target(context, obj)
    measures = getattr(sheet, 'measures', None) if sheet is not None else None
    return float(measures.thickness.value) if measures is not None else None


def size_of(context, obj):
    """(largura, altura, profundidade, espessura) editáveis do objeto; `None` no que não se edita por aqui."""
    from ..selection import classify

    info = classify.classify(obj) if obj is not None else None
    if info is None:
        return None
    editaveis = editing.editable_dimensions(info)
    values = []
    for field in SIZE_FIELDS[:3]:
        value = None
        if field in editaveis:
            try:
                value = float(editing.get_dimension(info, field))
            except (AttributeError, TypeError, ValueError, ReferenceError):
                value = None
        values.append(value)
    values.append(_thickness(context, obj))
    return tuple(values)


def sizes(context, uids):
    """Medidas por objeto da seleção, na ordem recebida."""
    from . import snapshot

    result = []
    for uid in uids:
        obj = snapshot.object_for(context, uid)
        result.append(size_of(context, obj) if obj is not None else None)
    return tuple(result)


def apply(context, uids, field, meters):
    """Escreve `field` em cada objeto da seleção. Devolve (aplicados, fora, [(nome, motivo)])."""
    from ..selection import classify
    from . import part_edit, snapshot

    done = ignored = 0
    failures = []
    for uid in uids:
        obj = snapshot.object_for(context, uid)
        info = classify.classify(obj) if obj is not None else None
        if info is None:
            ignored += 1
            continue
        try:
            if field == 'thickness':
                sheet = snapshot.sheet_target(context, obj)
                if sheet is None or getattr(sheet, 'measures', None) is None:
                    ignored += 1
                    continue
                part_edit.resize(sheet, obj, 'part_thickness', meters)
            elif field in editing.editable_dimensions(info):
                editing.set_dimension(context, info, field, meters)
            else:
                ignored += 1
                continue
            done += 1
        except ValueError as exc:
            failures.append((getattr(obj, 'name', ''), str(exc)))
    return done, ignored, failures
