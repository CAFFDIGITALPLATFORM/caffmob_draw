# Onboarding: testar a 025 pela primeira vez

> Para validar o fluxo de criação/posicionamento e a galeria clara numa sessão gráfica. O que é automatizado está em
> `tests/`; aqui ficam os passos que exigem olho humano.

## 0. Preparar

1. Instalar o add-on (ZIP do `build.py`) ou registrar o pacote pelo ensaio.
2. Blender 5.2, cena nova, Vista 3D ativa.
3. Abrir a Biblioteca CAFFMob na barra lateral.

## 1. Criar armário direto na viewport

1. Na Biblioteca, clicar em **Criar armário**.
   - Esperado: o armário v2 fica ativo e o painel **Construtor de Armários** aparece na Vista 3D; **nenhuma janela
     nova** do Blender é criada. A janela 023 só deve abrir pelo botão **Abrir Janela**.
2. Clicar em **Montar Caixa**.
   - Esperado: as cinco chapas aparecem no armário.

## 2. Aplicar pergunta onde adicionar

1. Clicar em **Aplicar** no painel da Vista 3D.
   - Esperado: o popup **“Onde adicionar o armário?”** com **Escolher na viewport** e **Cursor 3D**; a cena ainda não
     mudou de posição.
2. Repetir pelo **Aplicar** do rodapé da janela 023 (abrir por **Abrir Janela**).
   - Esperado: o mesmo popup, aberto na Vista 3D principal.

## 3. Escolher na viewport

1. Escolher **Escolher na viewport**.
   - Esperado: o armário real some e uma **caixa de arame** com as medidas do armário acompanha o mouse no piso.
2. Pressionar **seta direita**; depois **seta baixo**; depois **R**.
   - Esperado: 90°, 180° e +90° na caixa; a frente de construção é 0° (seta cima).
3. Clicar no piso.
   - Esperado: a caixa some, o armário aparece na posição/giro e um Ctrl+Z desfaz o posicionamento.
4. Repetir e pressionar **Esc** (ou botão direito).
   - Esperado: a caixa some e o armário volta à posição, ao giro e à visibilidade anteriores.

## 4. Cursor 3D

1. Posicionar o Cursor 3D no piso (Shift+clique direito ou painel lateral).
2. **Aplicar → Cursor 3D**.
   - Esperado: a raiz do armário vai para o cursor, o giro atual é preservado e as chapas acompanham.

## 5. Galeria

1. Abrir a Biblioteca CAFFMob.
   - Esperado: janela em creme claro, sidebar mais clara, cards em `#F5EFE3`, tinta café, botões/realce âmbar e teal;
     abas Biblioteca/Blocos/Texturas, busca, grade, seleção laranja e filtros continuam funcionando.
2. Abrir o card de um módulo.
   - Esperado: card branco com texto café e campos creme, legível.

## 6. O que ainda não está coberto por ensaio automático

- O desenho do popup na tela (o `screen.screenshot` do Blender não captura popups; o ensaio prova o gancho e o
  retorno `RUNNING_MODAL`).
- O clique real do mouse no popup e a sensação do arraste da caixa (o ensaio envia eventos sintéticos).
- A paridade integral do mockup do Construtor (toolbar completa, export JSON, titlebar, menu de contexto, cutlist):
  escopo da 023, com a decisão híbrida e o `cross-check.md` próprio.
- Categorias da Biblioteca (Armários/Portas/Janelas) e alternador Dark: fora desta rodada (a aparência Light é o que
  foi entregue).

## 7. Resultado da rodada de implementação (2026-11-26)

- `tests/test_placement_025.py` + `tests/test_library_style_025.py`: **7/7**.
- `tests/blender_025_place.py`: **16/16**, janela real do Blender 5.2, incluindo Criar armário sem janela nova,
  gancho do Aplicar, Cursor 3D, caixa de arame, mouse, seta direita, clique e Esc.
- `tests/blender_biblioteca_detalhe.py`: **38/38**; `tests/blender_012_library_ui.py`: **9/9**; puros **36**;
  puros amplos **54**; `test_i18n_coverage` **3/3** (28 chaves novas em `armario_v2.json`/`library.json`);
  smoke 017 OK; `check_api.py`: 637 arquivos, nenhuma API desconhecida.
- `ruff check` nos arquivos novos: limpo.
