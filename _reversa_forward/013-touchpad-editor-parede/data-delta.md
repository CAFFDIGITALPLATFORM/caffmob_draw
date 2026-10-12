# Data Delta: Zoom e navegação por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-10`

## 1. Resumo

Nada persistido muda: nenhum `bpy.props` novo, nenhum campo em `.blend` e nenhum arquivo do usuário. Só estado
transitório em memória, mais a leitura de uma preferência que o Blender já tem.

## 2. Campos novos (transitórios)

| Onde | Campo | Tipo | Valores | Vida |
|------|-------|------|---------|------|
| `caffmob_draw/walls2d/props.py#Session` | `zoom_window` | `None` / `'ARMED'` / `(x, y)` px | `None` = modo desligado; `'ARMED'` = lupa apertada, esperando o clique; `(x, y)` = início do retângulo | Enquanto o editor está aberto; volta a `None` ao enquadrar, cancelar ou fechar |
| `caffmob_draw/walls2d/props.py#Session` | `zoom_box_end` | `None` / `(x, y)` px | Canto atual do retângulo elástico | Igual |

Os dois ficam fora de `history._sign(plan)`, então não geram passo de desfazer, e somem com a sessão quando `props.end()` a encerra.

## 3. Constantes novas

| Onde | Nome | Valor inicial | Observação |
|------|------|---------------|------------|
| `caffmob_draw/canvas2d/gestures.py` | `PINCH_SENSITIVITY` | calibrado na prova D-02 | Sensibilidade da pinça |
| `caffmob_draw/canvas2d/gestures.py` | `WHEEL_STEP` | `1.15` | Passo da roda, hoje literal em `ops_editor.py` (l. 520) |
| `caffmob_draw/canvas2d/gestures.py` | `ZOOM_WINDOW_MIN_PX` | `5` | Lado mínimo do retângulo (RN-07) |
| `caffmob_draw/walls2d/ops_editor.py` | `TOOLBAR_HEIGHT` | `32` (× `ui_scale`) | Altura da barra superior |

## 4. Leitura de dados existentes

| Fonte | Campo | Uso |
|-------|-------|-----|
| `context.preferences.inputs` | `invert_zoom_wheel` | Sentido da roda e do Ctrl + roda (RN-04) |
| `context.preferences.system` | `ui_scale` | Altura da barra e tamanho da lupa |

## 5. Migrações

n/a.
