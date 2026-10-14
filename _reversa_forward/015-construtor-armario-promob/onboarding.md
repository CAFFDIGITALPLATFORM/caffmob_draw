# Onboarding: testar a feature 015 pela primeira vez

> Para quem vai validar o construtor de armário com a arquitetura do Promob. Tempo estimado: 30 minutos.
> Alvo: Blender 5.2 com o CAFFMob Draw gerado deste repositório.

## 1. Preparar

```bash
cd /home/theleoinfo/www/BlenderToMob
ruff check caffmob_draw/
python3 docs/rag/tools/check_api.py
python3 -m pytest tests -q -k "structures or carcass or gallery"        # testes puros desta feature
blender --background --factory-startup --python-exit-code 1 --python tests/blender_015_construtor_smoke.py
python3 build.py                                                       # gera caffmob_draw.zip
```

No Blender: Edit → Preferences → Get Extensions → Install from Disk → `caffmob_draw.zip`. Abra um arquivo novo.

## 2. Balcão de cozinha (o problema original)

1. Barra lateral → Biblioteca → **Criar armário**. Abre a galeria "Selecione uma estrutura de caixa para iniciar a
   construção", com as abas Cozinhas e Dormitórios.
2. Em Cozinhas, clique em **Inferior c/ Divisória** → OK.
3. Confira no editor:
   - o cabeçalho diz "Tipo: Inferior c/ Divisória";
   - as medidas são 500 × 720 × 550 (altura e profundidade do seu Padrão de Dimensões).
4. Na árvore de componentes devem aparecer:
   - **marcados:** Laterais, Base Inferior, Sarrafo Frontal e Sarrafo Traseiro;
   - **desmarcados:** Tampo Linear, Pés Plásticos e Rodapés.
5. Clique OK e olhe o 3D: o alto do balcão fica aberto, com um sarrafo na frente e outro atrás.
6. Gere o plano de corte: aparecem "Sarrafo frontal" e "Sarrafo traseiro", e **não** aparece "Base superior".

## 3. Mesmas medidas, tipos diferentes

1. Crie um **Superior c/ Divisória** e ponha 800 × 700 × 550.
2. Crie outro **Inferior c/ Divisória** com 800 × 700 × 550.
3. No plano de corte, o superior tem "Base superior" e o inferior tem os dois sarrafos.

## 4. Roupeiro

1. Galeria → Dormitórios → **Armário** → OK.
2. Ponha Número de vãos 3, largura 3000, altura 2500, profundidade 550.
3. Os três vãos têm 976 de largura. Com rodapé de 100, a altura interna é 2500 − 18 − 18 − 100 = 2364 e a altura
   total continua 2500.
4. Selecione o vão do meio e digite 900: os vãos das pontas ficam com 1014.
5. Selecione o vão da esquerda → aba Internos → **Cabideiro 01** → Inserir. O tubo fica 70 abaixo da prateleira de
   cima e aparece na lista de ferragens.
6. Aba Divisões → **Invisível** → Inserir. O vão se divide, e nenhuma peça nova aparece no 3D nem no corte.
7. Aba Deslizantes: "Sobre a caixa" aparece desabilitado, com "Disponível numa próxima versão".

## 5. Projeto antigo

1. Abra um `.blend` salvo antes desta feature, com um balcão.
2. O plano de corte fica igual ao de antes.
3. Abra o balcão no editor e clique **Cancelar**: nada muda.
4. Abra de novo e clique **OK**: o balcão passa a "Inferior c/ Divisória", com sarrafos.

## 6. Padrão editável

1. Configurador de Dimensões → linha Cozinha → Dimensões Externas → **Sarrafo - Largura** = 80 → reaplicar o
   padrão.
2. Os sarrafos dos balcões passam a 80 no plano de corte; os aéreos não mudam.

## 7. Design

- **Cores:** a galeria e a vista do editor usam a família Noite, com o laranja só na seleção e o teal no vão alvo.
- **Fonte:** o título da galeria é em Sora.
- **Estado em texto:** passe o mouse numa estrutura e selecione: o nome aparece também em texto.

## 8. Em inglês

Preferences → Interface → Language: English. A galeria mostra "Select a carcass structure to start building", com
"Base w/ Divider" e "Wardrobe".

## Se algo falhar

- Galeria vazia com aviso: o `data/cabinet_structures.json` tem erro de versão. Veja a mensagem no rodapé da galeria.
- Estrutura faltando na galeria: o aviso no Info diz qual estrutura foi pulada e por quê.
- Registre o defeito com `/reversa-debugger`.
