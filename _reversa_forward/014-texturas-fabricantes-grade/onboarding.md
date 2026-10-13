# Onboarding: testar Texturas e a biblioteca em grade pela primeira vez

> Identificador: `014-texturas-fabricantes-grade`
> Data: `2026-10-12` (revisão 2: modelo híbrido)

## Preparação (desenvolvedor)

1. Gere o catálogo, as miniaturas e o pacote do servidor a partir da pasta do titular (uma vez; idempotente):
   ```bash
   /opt/blender/blender --background --factory-startup --python tools/texturas_importar.py -- \
       /home/theleoinfo/Downloads/materials/textures
   ```
   Esperado: 12 fabricantes e 1.209 texturas no relatório. São criados `caffmob_draw/textures/catalog.json`,
   `caffmob_draw/textures/thumbs/` e `dist/texturas-servidor/` (imagens + `manifest.json`).
2. Suba o servidor falso com o pacote do servidor (substitui o site da CAF Mob até ele publicar o serviço):
   ```bash
   python3 tests/fake_texture_server.py --root dist/texturas-servidor --port 8765 \
       --account teste@cafmob.local --download-all
   ```
3. Rode os testes puros e o lint:
   ```bash
   ruff check caffmob_draw/
   python3 docs/rag/tools/check_api.py
   cd tests && python3 -m unittest test_texture_catalog test_library_grid test_texture_download test_texture_auth
   ```
4. Gere e instale o pacote:
   ```bash
   python3 build.py
   ```
   Instale em Edit › Preferences › Get Extensions › Install from Disk. Esperado: um ZIP pequeno, sem nenhuma imagem
   em tamanho real; o `build.py` recusa se encontrar uma.
5. Em Preferences › Add-ons › CAFFMob Draw, coloque o endereço do servidor como `http://127.0.0.1:8765`. Em
   Preferences › System › Network, ligue "Allow Online Access".

## Roteiro de teste (projetista)

1. Abra um projeto novo. No topo esquerdo da vista aparece só "BIBLIOTECA CAFFMOB" (minimizada).
2. Clique no rótulo: abre a coluna de categorias, como antes.
3. Maximize: abre o retângulo com a grade.
   - Esperado: pelo menos 4 colunas numa tela de 1.920 px.
   - O HUD e os botões de navegação continuam visíveis.
4. Escolha **Texturas › Duratex**: aparecem as miniaturas (vêm no plugin), marcadas como "não baixada". Role com a
   roda do mouse.
5. Busque "carvalho": só texturas com "carvalho" no nome, de todos os fabricantes.
6. Arraste "Carvalho Avela Design" até a frente de um balcão sem ter entrado com a conta: o plugin pede o login e
   nada muda.
7. Entre com a conta: aparecem um código e o navegador abre a página do servidor falso. Confirme lá e o plugin mostra
   o e-mail da conta.
8. Arraste a textura de novo: aparece o progresso do download, e a frente recebe a textura na escala real. A segunda
   vez é imediata.
9. Use **Baixar tudo**: o progresso total vai até 1.209. Desligue "Allow Online Access" e aplique outra textura: ela
   funciona sem internet.
10. Com "Allow Online Access" desligado e uma textura nunca baixada (passo opcional: apague o cache), tente aplicá-la:
    aparece o aviso, sem erro, e a interface continua respondendo.
11. Fixe o retângulo, clique na cena e gire a vista: continua aberto. Redimensione pela borda e mova pelo topo.
12. Arraste "Balcão 2 portas" até o piso: ele segue o mouse e entra na soltura. Ctrl+Z remove de uma vez.
13. Solte uma textura no vazio: nada muda e aparece um aviso curto. Comece um arraste e aperte Esc: nada acontece.
14. Feche e abra o Blender: o login continua, sem pedir de novo. **Sair** da conta: o arquivo de sessão some.
15. Salve o projeto, feche e abra: as texturas aplicadas continuam lá.

## Se algo der errado

| Sintoma | Onde olhar |
|---------|------------|
| Área Texturas sem miniaturas | Passo 1 não rodou (`catalog.json` e `thumbs/` ausentes) |
| "Sem acesso à internet" mesmo com servidor | Preferences › System › Network › "Allow Online Access" (D-14) |
| Login não completa | Servidor falso no ar? Endereço nas preferências? Prova de D-12 em `investigation.md` §6 |
| Download para no meio | Retomada (`.part`) e sha256 (D-11); log do subprocesso no console |
| Textura rosa depois de abrir em outro computador | Imagem ainda não baixada nesse computador; usar a textura ou "Baixar tudo" (D-09) |
| Processo `python` sobrando depois de fechar | Encerramento do subprocesso no `unregister`/`load_pre` (D-11) |
