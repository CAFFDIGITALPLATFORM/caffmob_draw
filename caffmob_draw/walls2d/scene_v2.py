"""Fronteira Blender do editor v2: abrir cópia; aplicar pela montagem transacional."""
import json
from . import model, props
from .studio import Prancheta
from ..caffmob.v2.validacao import validar_documento


def documento_da_cena(context):
    guardado = context.scene.get('caffmob_ambiente')
    if not guardado:
        return None
    d = json.loads(guardado)
    return d if d.get('schema') == 'caffmob.ambiente/v2' else None


def abrir(context):
    d = documento_da_cena(context)
    if d is None:
        return None
    erros = validar_documento(d)
    if erros:
        raise ValueError(str(erros))
    obj = context.active_object
    piso = obj.get('caffmob_pavimento_id') if obj else None
    piso = piso or context.scene.get('caffmob_pavimento_ativo')
    if piso not in {p['id'] for p in d['pavimentos']}:
        piso = None
    parede = obj.get('caffmob_id') if obj and obj.get('caffmob_tipo') == 'parede' else None
    s = props.start(model.WallPlan(), context.scene.name)
    s.v2 = Prancheta(d, piso, parede)
    return s


def aplicar(context, s):
    from ..mobi.cena_v2 import construir_cena
    # Não sobrescreve uma importação/edição que ocorreu enquanto esta janela estava aberta.
    if documento_da_cena(context) != s.v2.original:
        raise ValueError('O ambiente mudou na cena. Cancele e abra o editor novamente.')
    erros = validar_documento(s.v2.documento)
    if erros:
        raise ValueError(str(erros))
    root = construir_cena(context, s.v2.documento)
    # Montagem conserva os IDs e grava contrato, aberturas e malha nos novos objetos.
    if s.v2.selecao:
        obj = next((o for o in root.all_objects if o.get('caffmob_tipo') == 'parede'
                    and any(t['id'] == s.v2.selecao for t in json.loads(o['caffmob_parede'])['segmentos'])), None)
        if obj:
            context.view_layer.objects.active = obj
            obj.select_set(True)
    return root
