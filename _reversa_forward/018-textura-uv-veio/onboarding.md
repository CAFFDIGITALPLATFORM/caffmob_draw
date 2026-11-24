# Onboarding: testar a textura por UV e o conta-gotas

> Identificador: `018-textura-uv-veio`
> Data: `2026-11-23`
> Alvo: Blender 5.2 com o addon instalado a partir do ZIP gerado por `python3 build.py`

## 1. Antes de começar

1. `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` precisam passar.
2. `python3 build.py` gera `caffmob_draw.zip`. Instalar em Edit → Preferences → Get Extensions → Install from Disk.
3. Abrir um arquivo novo com o addon carregado e uma parede criada (o `UVMap` de piso e teto já vem do gerador).
4. Confirmar que o catálogo de texturas está baixado ou disponível offline; sem imagem, a aplicação enfileira
   download e não dá para testar a vista.

## 2. Roteiro de aceitação

### 2.1 Textura em parede (RF-13)

1. Selecionar a parede.
2. Abrir o painel de texturas e aplicar "Arauco Anis".
3. **Esperado**: a textura aparece nas faces internas e externas.
4. Inspecionar o modificador da parede: os seis sockets (`Top Surface`, `Bottom Surface`, `Inside Face`,
   `Outside Face`, `Left Edge`, `Right Edge`) mostram o material.
5. Criar um cubo, marcar como parede por propriedade sem o modificador e aplicar a mesma textura.
   **Esperado**: aviso de que a parede não aceita textura; nada muda na cena.

### 2.2 Nome do material (RF-08)

1. Aplicar "Arauco Anis" numa chapa.
2. Abrir o material no Blender (fora do addon).
   **Esperado**: o material se chama "Arauco Anis" e mostra `btm_texture_path`, `btm_texture_size_mm` e
   `btm_texture_projection = "UV"`.
3. Aplicar um item homônimo de outro fabricante e conferir que o nome ganhou a coleção e que o primeiro material
   continua intacto.

### 2.3 UV em milímetros e UV Editor (RF-07, RF-14)

1. Gerar um armário com uma chapa de 600 × 400 e textura de 600 mm.
2. **Esperado**: uma repetição inteira na largura e dois terços na altura.
3. Entrar em Edit Mode, selecionar a face e mover a ilha de UV no UV Editor.
   **Esperado**: a textura acompanha na vista 3D.
4. Salvar, fechar e reabrir: o UV editado continua.
5. Aplicar a mesma textura num objeto importado sem UV.
   **Esperado**: projeção de caixa e aviso de malha sem UV.

### 2.4 Veio em graus (RF-09)

1. No armário, girar o veio do exterior para 90°.
   **Esperado**: só as chapas externas giram; a porta continua como estava.
2. Girar a mesma textura para 30° numa chapa e abrir o plano de corte.
   **Esperado**: a chapa continua listada como veio horizontal ou vertical (o múltiplo mais próximo) e o painel avisa
   que o ângulo é visual.
3. No painel da peça, conferir o campo **Veio (graus)**: fica na seção **Chapa** ao lado de **Veio** (peça de
   biblioteca) ou na seção **Acabamentos** (chapa gerada pelo armário v2, com o módulo na cena). Com 30° ou 45°,
   aparece abaixo do campo o aviso em vermelho "Ângulo do veio não é múltiplo de 90"; com 90° ou 180°, o aviso some.
4. Aplicar a mesma textura em outro armário e conferir que ele não girou junto.

### 2.5 Conta-gotas (RF-10)

1. Com um armário texturizado, acionar o conta-gotas, clicar na porta de origem.
   **Esperado**: a assinatura fica na sessão (nome, tamanho e ângulo).
2. Selecionar três armários sem textura, abrir "aplicar textura copiada", marcar só **Porta** e confirmar, clicando as
   portas na viewport quando pedido.
   **Esperado**: só as portas mudam; exterior e interior intactos.
3. Repetir marcando **Exterior** e depois **Interior**.
4. Acionar o conta-gotas sem origem escolhida.
   **Esperado**: aviso de que falta a origem e nenhum material trocado.

### 2.6 Interface e desfazer

1. Trocar o idioma para inglês e repetir 2.5.
   **Esperado**: rótulos em inglês.
2. Fazer uma aplicação e usar Ctrl+Z uma vez por operação.
   **Esperado**: cada aplicação volta inteira (material, nome, veio).
3. Desregistrar o addon (Preferences → desmarcar) e conferir que não fica handler de desenho nem propriedade
   pendurada: reabrir Preferences e recolocar o addon deve funcionar sem erro.

## 3. O que este roteiro não cobre

- Peça com Geometry Node que gere UV próprio: ver a verificação pendente em `investigation.md` §4.
- Textura de fabricante que exige download: depende de rede e conta.
- Planilha de corte com veio em ângulo intermediário: o corte só entende H/V/NONE por decisão de plano (D-06).
- Dicas ao passar o mouse (descrição dos operadores e das props do conta-gotas e do ângulo do veio): o roteiro confere
  os rótulos na tela; as dicas são cobertas só por `tests/test_i18n_coverage.py` (T026), que olha o catálogo, não o que
  o Blender mostra no tooltip.
- Desenho do painel e do destaque do conta-gotas: só com janela. `tests/blender_018_janela.py` já confere o campo,
  o aviso (45° mostra, 90° não) e a caixa da parte na vista; a conferência com o olho continua valendo porque o ensaio
  roda o desenho real, mas não julga se ele está bonito ou no lugar certo.
- Material migrado do formato antigo com nome ocupado: o conflito é sinalizado em `btm_texture_nome_conflito` e ainda
  não tem linha no painel; o roteiro não abre o material para ver a marca.
- Aviso de malha sem UV: aparece na barra de status por alguns segundos ao aplicar a textura, sem linha própria no
  painel. A fumaça `tests/blender_018_textura_smoke.py` (T025) confere o texto e a projeção de caixa; a leitura na tela
  depende desta conferência, porque o aviso some sozinho.

## 4. Se algo falhar

1. Guardar o `.blend` e a saída do console (`Window → Toggle System Console`).
2. Verificar se a falha ocorre com material já existente no arquivo (migração) ou com material novo.
3. Anotar o papel da peça e o domínio escolhido: `FRONTS` é a porta, `EXTERNAL` o exterior e `INTERNAL` o interior.
