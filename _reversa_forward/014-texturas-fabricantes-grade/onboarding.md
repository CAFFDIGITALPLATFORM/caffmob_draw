# Onboarding: testar Texturas e a biblioteca em grade pela primeira vez

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12`

## Preparação (desenvolvedor)

1. Traga as texturas da pasta do titular para o pacote (uma vez; idempotente):
   ```bash
   /opt/blender/blender --background --factory-startup --python tools/texturas_importar.py -- \
       /home/theleoinfo/Downloads/materials/textures
   ```
   Esperado: 12 fabricantes e 1.209 texturas no relatório; `caffmob_draw/textures/catalog.json` e `thumbs/` criados.
2. Rode os testes puros e o lint:
   ```bash
   ruff check caffmob_draw/
   python3 docs/rag/tools/check_api.py
   cd tests && python3 -m unittest test_texture_catalog test_library_grid
   ```
3. Gere e instale o pacote:
   ```bash
   python3 build.py
   ```
   Instale em Edit › Preferences › Get Extensions › Install from Disk. Esperado: o ZIP com cerca de 600 MB; o
   `build.py` recusa se faltar alguma imagem do catálogo.

## Roteiro de teste (projetista)

1. Abra um projeto novo. No topo esquerdo da vista aparece só "BIBLIOTECA CAFFMOB" (minimizada).
2. Clique no rótulo: abre a coluna de categorias, como antes.
3. Use o botão de maximizar: abre o retângulo com a grade.
   - Esperado: pelo menos 4 colunas numa tela de 1.920 px.
   - O HUD e os botões de navegação continuam visíveis, sem nada por cima.
4. Escolha **Texturas › Duratex**: aparecem as coleções e a grade com miniaturas. Role com a roda do mouse.
5. Busque "carvalho": só texturas com "carvalho" no nome, de todos os fabricantes.
6. Fixe o retângulo, clique na cena e gire a vista: o retângulo continua aberto. Arraste a borda para redimensionar e
   o topo para mover.
7. Insira um balcão (categoria Cozinha, arraste "Balcão 2 portas" até o piso): o balcão segue o mouse e entra na
   soltura. Ctrl+Z remove de uma vez.
8. Arraste "Carvalho Avela Design" até a frente do balcão: só a frente muda, na escala real. Arraste até a lateral: o
   veio fica no sentido do comprimento.
9. Solte uma textura no vazio: nada muda e aparece um aviso curto. Comece um arraste e aperte Esc: nada acontece.
10. Solte o retângulo (desfixe) e clique fora: ele fecha. Minimize: volta a ser só o rótulo.
11. Salve o projeto, feche e abra de novo: as texturas aplicadas continuam lá.

## Se algo der errado

| Sintoma | Onde olhar |
|---------|------------|
| Área Texturas diz "Texturas não instaladas" | Passo 1 não rodou ou o clone não tem as imagens (D-04) |
| Miniaturas cinza ou vazias | Resultado da prova de D-05 em `investigation.md` §6 |
| Arraste não insere o bloco | Prova de D-07 e o keymap do painel (`library_panel/ops_click.py`) |
| Textura rosa (imagem faltando) depois de abrir em outro computador | `load_post` de D-09 e o aviso "Textura do catálogo não encontrada" |
