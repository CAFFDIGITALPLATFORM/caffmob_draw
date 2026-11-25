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

- Aparência do grão gerado (só o olho julga).
- Contorno de arestas no Solid depende do motor de desenho da GPU.
- Percepção de “mesma textura” entre Solid, Preview e render.
- Diálogo de aviso de migração na tela.
