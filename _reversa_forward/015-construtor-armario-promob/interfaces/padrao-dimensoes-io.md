# Contrato: Padrão de Dimensões, JSON do CAFF e XML do Promob

> Feature: `015-construtor-armario-promob` · Decisões D-07, D-08 · Arquivos: `caffmob_draw/standards/io_json.py`,
> `caffmob_draw/standards/io_promob.py`, `caffmob_draw/data/dimension_schema.py`
> Regras de origem: `_reversa_sdd/domain.md#standards` (RN-STANDARDS-16 a RN-STANDARDS-21)

## Mudança no JSON do CAFF

1. **Valores numéricos novos por linha** (chave `<LINHA>.external.<campo>`, em mm): `stretcher_width`,
   `shelf_setback`, `hanger_rod_drop`. Seguem o mesmo formato dos campos `external` de hoje.
2. **`group_assembly`** no nível da definição, ao lado de `assembly`:

```json
{
  "unit": "mm",
  "assembly": "LATERAL",
  "group_assembly": {
    "INFERIOR": {"assembly": "LATERAL", "back_kind": "ENCAIXADO", "rear_stretcher": "HORIZONTAL"}
  },
  "values": {"COZ.external.stretcher_width": 100}
}
```

## Mudança no XML do Promob

Atributos do CAFF no fim do arquivo, como o `CAFF_MONTAGEM` da 012:
- `CAFF_GRUPO_INFERIOR`, `CAFF_GRUPO_SUPERIOR` e `CAFF_GRUPO_DESPENSEIRO`, com valor
  `"<assembly>;<back_kind>;<rear_stretcher>"` (ex.: `"LATERAL;ENCAIXADO;HORIZONTAL"`);
- `CAFF_SARRAFO_<LINHA>`, `CAFF_RECUO_PRAT_<LINHA>` e `CAFF_CABIDEIRO_<LINHA>`, para os três valores novos.

O Promob ignora IDs desconhecidos.

## Compatibilidade

- **Arquivo sem os campos novos** (JSON ou XML de antes da 015): importa normalmente. Os valores novos assumem o
  padrão de fábrica (100, 20, 70) e `group_assembly` fica vazio, valendo o da estrutura.
- **Exportação:** o XML continua reexportando o `raw` existente (RN-STANDARDS-20) e acrescenta os atributos `CAFF_*`
  no fim.
- **Versões futuras:** continuam recusadas (RN-STANDARDS-16).

## Erros

| Entrada | Comportamento |
|---|---|
| Grupo desconhecido em `group_assembly` | Ignorado, com aviso |
| `assembly`, `back_kind` ou `rear_stretcher` inválido | Só esse campo cai no valor da estrutura, com aviso (como RN-STANDARDS-19) |
| Valor numérico novo fora da faixa (`data-delta.md#2.1`) | Recusado na validação de `set_values`, que valida tudo antes de gravar (RN-STANDARDS-04) |
| `CAFF_GRUPO_*` com menos de 3 partes | Partes ausentes = valor da estrutura, com aviso |

## Idempotência

Exportar e importar o mesmo padrão devolve os mesmos valores e o mesmo `group_assembly`. A ida e volta é coberta por
teste.

## Timeouts

n/a. A escrita continua atômica (temporário no diretório de destino + `os.replace`, RN-STANDARDS-21).
