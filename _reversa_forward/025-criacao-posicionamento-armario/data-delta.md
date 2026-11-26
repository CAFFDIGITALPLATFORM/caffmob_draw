# Data delta: 025-criacao-posicionamento-armario

> Modelo extraído de referência: `_reversa_sdd/domain.md` e `_reversa_sdd/addenda/017-construtor-armario-v2.md`
> Nenhum campo existente é removido ou tem o tipo trocado.

## 1. Campos persistentes novos

Nenhum. O posicionamento é a transformação da raiz do armário:

| Onde | Campo | Tipo | Observação |
|------|-------|------|------------|
| `Object` raiz do armário v2 | `location` | vetor (já existente) | Posição escolhida no piso ou no Cursor 3D |
| `Object` raiz do armário v2 | `rotation_euler` | vetor (já existente) | Giro em Z (0°/90°/180°/270° + R) |
| `Object` raiz do armário v2 | `hide_viewport`/`hide_get` | booleano (já existente) | Oculto só durante o modo Escolher; restaurado ao fim |

## 2. Estado transitório (não persistido)

| Onde | Estado | Para que serve |
|------|--------|----------------|
| `BTM_OT_ArmarioV2PlaceChoose` | `_ocultos` | Lista de objetos ocultados para restaurar `hide_get` |
| `BTM_OT_ArmarioV2PlaceChoose` | `_inicio` (loc/rot/hide) | Cancelamento restaura o estado anterior |
| `BTM_OT_ArmarioV2PlaceChoose` | `_area`, `_region`, `_rv3d`, `_cage`, `_spec` | Contexto do modal e a caixa temporária |
| `placement` | `ORIENTACOES` | Mapa estável seta → yaw |

## 3. Campos que continuam iguais

- `Object.btm_armario` (spec, divisões, gavetas, internos, portas, fundo) não muda.
- `Object.btm_armario_parte` não muda.
- O contrato de chapas e o plano de corte não são tocados.

## 4. Migração

n/a. Não há campo novo para migrar; a posição/rotação já é salva no `.blend` como transformação normal e o undo do
Blender cobre confirmação e cancelamento.

## 5. Impacto no plano de corte

Nenhum: o plano lê medidas/espessura/veio; a transformação da raiz não altera a geometria das peças.
