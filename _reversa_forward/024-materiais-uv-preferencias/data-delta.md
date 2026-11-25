# Data delta: 024-materiais-uv-preferencias

> Modelo extraído de referência: `_reversa_sdd/domain.md` e `_reversa_sdd/addenda/017-construtor-armario-v2.md`
> Nenhum campo existente é removido ou tem o tipo trocado.

## 1. Campos novos

| Onde | Campo | Tipo | Padrão | Observação |
|------|-------|------|--------|------------|
| `Object.btm_armario` (raiz do armário v2) | `exibicao_versao` | Int | `0` | `0` = ainda não migrado; `1` = textura padrão já aplicada. Marca a migração única de D-07 |
| `Object.btm_armario` (raiz) | `exibicao` | Enum `TEXTURA_SO` \| `TEXTURA_LINHAS` | `TEXTURA_SO` | Variante escolhida na janela/painel; a preferência do add-on é o valor inicial |
| `BTM_AddonPreferences` | `exibicao_armario` | Enum `TEXTURA_SO` \| `TEXTURA_LINHAS` | `TEXTURA_SO` | Substitui o controle de cor do armário na tela de preferências |

## 2. Campos que mudam de significado (sem mudar de tipo)

| Campo | Antes | Depois |
|-------|-------|--------|
| `BTM_AddonPreferences.cabinet_color` | Cor de objeto do armário, usada pelo Solid | Cor **de apoio/legado**; a leitura do armário passa a vir da textura. O valor salvo é lido pela migração e não é apagado |
| `UVMap` da chapa | Projeção planar por eixo dominante | Mesmo layer, retângulo por **classificação de face** (EXTERNA/INTERNA/FITA), ainda em metros |
| Material da chapa | `Base Color` sólido por acabamento | Material com `ShaderNodeTexImage` (textura padrão MDF claro) + `Mapping` em 1/tamanho em metros |

## 3. Campos que continuam iguais

- `Object.btm_armario_parte.material` continua vencendo qualquer padrão (peça do usuário não é sobrescrita).
- `Object.btm_edgeband.use_color`/`color` continuam valendo para fita sólida.
- `Object.btm_armario.ajustes` (023) e as chaves de geração não são tocadas.

## 4. Migração

1. `load_post` percorre raízes de `Marcenaria` com `btm_armario` e `exibicao_versao == 0`.
2. Aplica o material com textura padrão nas peças cujo `material` está vazio; não regenera geometria.
3. Grava `exibicao_versao = 1` e mostra um aviso por cena.
4. Segunda abertura: nada acontece.
5. Não há downgrade automático; voltar atrás é reaplicar material manualmente ou limpar `exibicao_versao`.

## 5. Impacto no plano de corte

Nenhum: o plano lê dimensões, espessura, veio e material pelo nome. A textura é exibição, não produção.
