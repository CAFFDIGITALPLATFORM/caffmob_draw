# Data delta: 026 — paridade restante

## 1. Campos persistidos

| Onde | Campo | Tipo | Default | Uso |
|------|-------|------|---------|-----|
| `Object.btm_armario.ajustes[]` | `duplicada` | bool | `False` | Marca a peça cuja cópia o `build.gerar` deve recriar; o ajuste já existente guarda `uid`, `papel` e `nome`. |

Nenhum outro campo é gravado no `.blend`. O JSON exportado é um arquivo do usuário, não estado da cena.

## 2. Estado transitório

| Onde | Campo | Uso |
|------|-------|-----|
| `JanelaSessao` | `vista`, `tema`, `apenas_laterais`, `escala_frontal`, `escala_lateral`, `deslocamento_frontal` | Toolbar/preview/arraste; recriado ao abrir a janela. |
| `WindowManager.btm_library` | `theme` (`LIGHT`/`DARK`) | Botão de tema da Biblioteca; estado de sessão, não salvo no `.blend`. |

## 3. Formato do export

```json
{
  "schema": "caffmob.armario.v1",
  "armario": {"largura": 800.0, "altura": 1800.0, "profundidade": 500.0},
  "pecas": [{"nome": "Lateral esquerda", "papel": "LATERAL", "comprimento_mm": 15.0, "altura_mm": 1800.0,
             "profundidade_mm": 500.0, "espessura_mm": 15.0, "material": "MADEIRADO", "ferragem": "NENHUMA"}],
  "cutlist": [{"nome": "Lateral esquerda", "papel": "LATERAL", "quantidade": 1}],
  "totais": {"pecas": 5, "grupos_cutlist": 5}
}
```

Os campos do spec são copiados com `getattr`; campos ausentes são omitidos. A cutlist agrupa por
`nome + papel + espessura + comprimento + altura` e conta a quantidade.

## 4. Migração

Nenhuma migração de cena: o campo novo tem default `False` e PropertyGroups antigos o leem como desligado.
