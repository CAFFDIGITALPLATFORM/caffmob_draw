# Onboarding: testar a 024 pela primeira vez

> Para quem vai validar materiais/UV/preferências numa sessão gráfica. O que é automatizado está em
> `tests/`; aqui ficam os passos que exigem olho humano.

## 0. Preparar

1. `python3 build.py` na raiz do projeto e instalar o ZIP: Edit → Preferences → Get Extensions → Install from Disk.
2. Blender 5.2, cena nova, unidade em milímetros (padrão do add-on).
3. Ativar o Viewport 3D e abrir o painel lateral do CAFFMob.

## 1. Armário novo já texturizado

1. Criar um armário v2 (Construtor de Armários) com 600 × 720 × 550 mm e **Montar Caixa**.
2. Olhar o armário em **Solid** (Z).
   - Esperado: cada chapa mostra o **MDF claro** com grão; nenhuma peça cinza ou com cor de objeto.
3. Trocar para **Material Preview** (Z duas vezes).
   - Esperado: a mesma textura, no mesmo canto e mesma escala, sem costura entre peças.
4. Aplicar um material do usuário na lateral esquerda (painel de materiais) e voltar ao **Gerar**.
   - Esperado: a lateral mantém o material do usuário; as demais continuam no MDF claro.

## 2. UV por face

1. Selecionar a base inferior e abrir o **UV Editor**.
2. Conferir que as faces de **fora** e de **dentro** têm retângulos distintos (não espelhados errado).
3. Espelhar a peça em lote (Shift+clique → Espelhar) e voltar ao Gerar.
   - Esperado: o mapa continua no canto certo, sem invertido.
4. Com fita de borda ativa, aproximar a câmera da aresta:
   - Esperado: a fita mostra o comprimento ao longo da aresta e a largura no perfil; não estica na quina.

## 3. Preferências

1. Edit → Preferences → Add-ons → CAFFMob Draw.
2. Procurar a opção de exibição do armário.
   - Esperado: **Textura** com **Somente textura** e **Textura com linhas**; nenhuma outra opção existente sumiu.
3. Escolher **Textura com linhas**, fechar e olhar o armário no Solid.
   - Esperado: contorno em **todas as arestas** de cada chapa.
4. Voltar para **Somente textura**: o contorno desaparece, a textura permanece.

## 4. Migração de cena antiga

1. Abrir um `.blend` salvo antes desta feature, com armário v2 gerado.
2. Esperado: **um** aviso de migração e o armário com textura padrão; nada apagado.
3. Salvar, fechar e reabrir.
   - Esperado: **nenhum** aviso de novo (marca `exibicao_versao = 1`).

## 5. O que ainda não está coberto por ensaio automático

- Aparência do grão gerado (só o olho julga se *parece* MDF; o ensaio prova que ele existe e distingue do liso).
- Contorno de arestas no Solid depende do motor de desenho da GPU (o ensaio prova as flags, não o traço na tela).
- Diálogo de aviso de migração na tela (o ensaio prova a chamada, com contagem, e o silêncio na segunda abertura).

## 6. Resultado da rodada de implementação (2026-11-25)

O que já está provado sem olho humano:

- textura MDF gerada em runtime, 512², empacotada no `.blend`, só na chapa (vidro/alumínio sem textura);
- UV por face: EXTERNA e INTERNA em retângulos distintos, quatro faces de fita, tudo em metros;
- faixa da fita com `UVMap` próprio (U no comprimento, V na espessura);
- `exibicao_armario` com dois itens e `cabinet_color` preservado;
- migração única por `exibicao_versao`, com handler removido no `unregister()`;
- i18n das chaves novas em pt_BR e en_US.

Segunda rodada (mesmo dia), com janela real do Blender 5.2 — no Windows não há `xvfb-run`; o equivalente é
`blender.exe --factory-startup --enable-event-simulate --python <ensaio>`, e `--python-exit-code 1` reprova o ensaio.

- `tests/blender_024_exibicao.py`: 23 checagens OK. O fluxo de detalhes (`hb_details.DetailView().create()`) deixa a
  vista 3D em `SOLID`/`TEXTURE` (T008), o operador de preferências recomendadas aplica `TEXTURE` (T016) e o aviso da
  barra lateral não aparece nem em `TEXTURE` nem em `OBJECT` (T017).
- `tests/blender_024_visual.py`: 20 checagens OK, render EEVEE. Cor média da chapa (0,6285) igual ao material liso de
  controle com a cor média da textura (0,6279); close-up com grão 0,00353 contra 0,00005 do liso (dithering desligado
  para o degrau de 8 bits não imitar grão); render idêntico com a vista em Material Preview (0,6285); “Textura com
  linhas” liga `show_wireframes` com o limiar/opacidade de `view_mode_core` e “Somente textura” desliga; o aviso de
  migração é chamado uma vez com a contagem e não volta na segunda abertura. O PNG fica em
  `%TEMP%\caffmob_024_mdf.png` para inspeção.

O que continua só no olho: se o grão *parece* MDF à distância de trabalho, se o traço do contorno fica bom na sua GPU e
como o aviso de migração aparece na tela (o ensaio prova a chamada e o texto, não o desenho do popup).
