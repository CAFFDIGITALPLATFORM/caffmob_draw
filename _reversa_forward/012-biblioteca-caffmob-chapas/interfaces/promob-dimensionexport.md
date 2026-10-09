# Contrato (delta): `DIMENSIONEXPORT` do Promob com a montagem do CAFFMob

> Feature `012-biblioteca-caffmob-chapas` · RF-11 · D-14
> Contrato base: `_reversa_forward/001-addon-moveis-planejados/interfaces/promob-dimensionexport.md` (importar e
> exportar, mapeamento das famílias `MAT`, `L`, `C`, `ESP`, `FIT`, `ALT_*`, `PROF_*`).
> Arquivo de referência: `tests/fixtures/dimensionexport_me_moveis.xml`, idêntico ao anexo do titular, com **692**
> atributos (o `requirements.md` cita 694; o número certo é 692).

## O que muda

O Promob não tem atributo para a regra de montagem. A família `MON` do arquivo de referência descreve a **chapa do
montante** e os afastamentos dela, não lateral ou base passante:
- `COZ_ESP_MON_LAT`, `COZ_C_MON_LAT`, `COZ_L_MON_LAT` e `COZ_MAT_MON_LAT`;
- `COZ_MON_AFA_F_LAT` e `COZ_MON_AFA_T_LAT`;
- `COZ_MON_REC_SAR_FRO`.

A montagem do CAFFMob vai num atributo próprio:

```xml
<ATTRIBUTE ID="CAFF_MONTAGEM" VALUE="LATERAL" />   <!-- ou "BASE" -->
```

## Exportar

- Escreve os atributos do padrão como hoje, na mesma ordem dos `raw_attributes`.
- Acrescenta `CAFF_MONTAGEM` ao fim de `<ATTRIBUTES>`, com o valor de `BTM_PG_StandardDefinition.assembly`.
- Não escreve outro atributo novo.

## Importar

| Situação | Resultado |
|----------|-----------|
| `CAFF_MONTAGEM` ausente (arquivo do Promob) | `assembly = LATERAL`; nenhum aviso |
| `VALUE="LATERAL"` ou `"BASE"` (sem diferenciar maiúsculas) | `assembly` com esse valor |
| Outro valor | `assembly = LATERAL` e aviso no relatório da importação: "Montagem desconhecida: <valor>; usada lateral passante" |

`CAFF_MONTAGEM` não vai para `raw_attributes`, para não ser escrito duas vezes.

## Compatibilidade

- Promob: o ID é desconhecido para ele e fica guardado na definição, sem efeito.
- Round-trip: importar o arquivo do titular e exportar de volta devolve os 692 atributos iguais, mais
  `CAFF_MONTAGEM`.
- Idempotência: importar e exportar duas vezes dá o mesmo arquivo.
- Tempo: leitura e escrita locais, sem rede e sem timeout.

## Erros

Arquivo inválido segue o contrato base (001): nada é criado e o motivo aparece.
