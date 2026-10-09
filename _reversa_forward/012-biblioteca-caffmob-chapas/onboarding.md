# Onboarding: testar a Biblioteca CAFFMob e os armários por chapas

> Identificador: `012-biblioteca-caffmob-chapas`
> Para quem vai testar a feature pela primeira vez no Blender 5.2.

## Preparar

1. Gere e instale o pacote: `python3 build.py`, depois Edit → Preferences → Get Extensions → Install from Disk →
   `caffmob_draw.zip`.
2. Abra um arquivo novo e importe o padrão do titular. Na barra lateral (N), abra **Configurador de Dimensões** e
   importe `tests/fixtures/dimensionexport_me_moveis.xml` (o mesmo `.dimensionExport` do titular).
3. Quando aparecer a pergunta **"Aplicar a todos os módulos existentes na cena?"**, responda Sim: a cena está vazia,
   então nada muda.

## Só CAFFMob na interface

1. Confira que a barra lateral não tem o seletor Frameless / Face frame / Closets, nem as galerias, nem os modos de
   seleção delas. O HUD (se ligado) não mostra os modos Cabinets, Bays, Openings…; Mover Sobre e Seleção por
   componente continuam.
2. Abra uma cena de detalhe de moldura: a biblioteca de molduras não aparece.
3. Em Preferências › CAFFMob Draw › Avançado, ligar **Mostrar bibliotecas herdadas** traz tudo de volta (só para
   suporte); desligue de novo.

## Painel e categorias

1. Confira o rótulo **BIBLIOTECA CAFFMOB** no canto superior esquerdo da viewport. Desligue o HUD nas preferências e
   confira que o rótulo continua.
2. Clique nele. Esperado, nesta ordem: **Criar armário**, Cozinha, Banheiro, Sala, Home office e **Criar categoria**.
3. Clique em **Cozinha**: abre a lista dos modelos prontos (balcão 1 e 2 portas, aéreo 1 e 2 portas, torre) e os
   módulos que você salvou em Cozinha. Insira o balcão 2 portas: ele vem com as medidas e as chapas de COZ.
4. **Criar categoria** → nome "Lavanderia", linha **Dormitório** → OK. Ela aparece depois de Home office. Tente criar
   "Cozinha" de novo: o motivo aparece e nada é criado.
5. Confira na barra lateral, em Inserir: só Objetos, Importar e o aviso do painel.

## Criar armário

1. **Criar armário** → tipo **Balcão**, largura 600 mm, montagem **Lateral passante** → OK.
2. Esperado: o balcão nasce no cursor com a altura e a profundidade de balcão do padrão, e o editor de armário abre
   nele. Confira as espessuras das chapas (laterais, base, tampo, fundo) na aba Estrutura.
3. No editor, troque a montagem para **Base passante**. Esperado:
   - a base passa a ter a largura toda (600 mm);
   - as laterais ficam com a altura menos a espessura da base;
   - a lista de corte mostra essas medidas;
   - a seção Selecionado mostra **Padrão próprio**.
4. **Criar armário** → **Cancelar**: nenhum objeto novo.

## Mudar o padrão

1. Ponha mais 4 balcões pela Cozinha e deixe o da etapa anterior com base passante.
2. No Configurador, mude a espessura da lateral de Cozinha e aplique. Esperado:
   1. Pergunta 1, com as contagens: "Aplicar a todos os módulos existentes na cena?". Responda **Sim**.
   2. Pergunta 2: "Aplicar também nos móveis que diferem do padrão global anterior?". Responda **Não**.
   3. Os 4 balcões mudam; o de padrão próprio fica igual.
3. Ctrl+Z desfaz tudo numa etapa só.
4. Importe um OBJ e repita a etapa 2: a pergunta mostra 1 item "não aplicável", e o OBJ não muda.
5. Mude o padrão e responda **Não** na pergunta 1: nada muda na cena, e um balcão novo já usa o padrão novo.

## Converter um arquivo antigo

1. Abra um arquivo feito antes da 012 com armários frameless, face frame ou closets (ou rode
   `tests/blender_012_convert_smoke.py`, que monta um).
2. Esperado: o aviso "N armários de bibliotecas antigas" e o botão **Converter para CAFFMob** na barra lateral.
3. Converta. Esperado: mesmos lugares e medidas externas; o relatório lista o que cada armário perdeu (gavetas,
   frentes especiais); Ctrl+Z volta tudo.

## Converter os grupos salvos

1. Com grupos salvos nas bibliotecas antigas ("Grupos frameless" ou "Grupos face frame"), abra o painel
   BIBLIOTECA CAFFMOB.
2. Esperado: "Converter grupos antigos" no topo da coluna. Aceite.
3. Esperado: os grupos aparecem como módulos em **Geral**, com os mesmos nomes; o relatório lista as perdas; os
   arquivos originais continuam na pasta `cabinet_groups`. A oferta não volta a aparecer; o comando fica em Criar
   categoria › Converter grupos antigos.

## Exportar

Exporte o padrão para `.dimensionExport`: o arquivo tem os 692 atributos do titular e mais `CAFF_MONTAGEM`.

## Testes automáticos

```bash
for t in tests/test_structure_assembly.py tests/test_cabinet_defaults.py tests/test_library_categories.py tests/test_library_layout.py tests/test_standards_apply_core.py tests/test_legacy_convert.py tests/test_promob_assembly.py; do python3 $t; done
blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_legacy_gate_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_convert_smoke.py
blender --factory-startup --enable-event-simulate --python tests/blender_012_convert_undo.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_cabinet_standard_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_apply_smoke.py
blender --factory-startup --enable-event-simulate --python tests/blender_012_library_ui.py
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
```
