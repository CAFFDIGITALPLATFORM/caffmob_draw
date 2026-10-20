"""JSON canônico sem reordenar arrays, arredondar medidas ou descartar campos."""
import json
import math
from decimal import Decimal
from .contrato import LIMITES_STUDIO


class DocumentoInvalido(ValueError):
    def __init__(self, erros):
        self.erros = erros
        super().__init__(str(erros))


def serializar(documento):
    """Chaves ordenadas e números no formato JSON.stringify (inclusive -0 e expoentes)."""
    def codificar(v):
        if v is None or isinstance(v, (str, bool)):
            return json.dumps(v, ensure_ascii=False)
        if type(v) in (int, float):
            if not math.isfinite(v):
                raise ValueError('Número não finito no documento.')
            if v == 0:
                return '0'
            s = repr(v).lower()
            if 1e-6 <= abs(v) < 1e21:
                return format(Decimal(s), 'f').rstrip('0').rstrip('.') if '.' in format(Decimal(s), 'f') else format(Decimal(s), 'f')
            if 'e' in s:
                mantissa, expoente = s.split('e')
                return mantissa.removesuffix('.0') + 'e' + ('+' if int(expoente) >= 0 else '-') + str(abs(int(expoente)))
            return s
        if isinstance(v, list):
            return '[' + ','.join(codificar(x) for x in v) + ']'
        if isinstance(v, dict) and all(isinstance(k, str) for k in v):
            # sort() do JavaScript compara unidades UTF-16.
            return '{' + ','.join(codificar(k) + ':' + codificar(v[k]) for k in sorted(v, key=lambda k: k.encode('utf-16-be'))) + '}'
        raise ValueError('O documento precisa ser JSON sem ciclos.')
    return codificar(documento)


def conferir_bytes(texto):
    n = len(texto.encode('utf-8')) if isinstance(texto, str) else len(texto)
    teto = LIMITES_STUDIO['bytes']
    return [] if n <= teto else [dict(caminho='documento', codigo='DOCUMENTO_GRANDE_DEMAIS', mensagem=f'Documento com {n} bytes UTF-8; máximo {teto}.')]


def ler_documento(texto):
    from .validacao import validar_documento
    erros = conferir_bytes(texto)
    if erros:
        raise DocumentoInvalido(erros)
    try:
        documento = json.loads(texto, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise DocumentoInvalido([dict(caminho='documento', codigo='JSON_INVALIDO', mensagem='O arquivo não é JSON válido.')]) from None
    erros = validar_documento(documento)
    if erros:
        raise DocumentoInvalido(erros)
    return documento
