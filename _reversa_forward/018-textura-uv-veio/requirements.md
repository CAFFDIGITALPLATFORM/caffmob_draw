# Requirements: Textura por UV, veio e conta-gotas

> Identificador: `018-textura-uv-veio`
> Data: `2026-11-23`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
>
> **Escopo fatiado em 2026-11-23.** A feature nasceu com cinco blocos. A avaliação de escopo os separou em três
> entregas: esta 018 (textura, UV, veio, conta-gotas e parede), `019-redimensionar-e-colisao` (redimensionar o
> armário, veio do armário e colisão à mão) e `020-converter-em-armario` (conversão de móvel em armário e
> biblioteca). Os IDs de RN e RF foram preservados da versão original: números ausentes pertencem às outras duas
> features, e isso é intencional para a rastreabilidade não se perder.

## 1. Resumo executivo

A textura do addon hoje é uma caixa-preta: o material projeta em caixa sobre coordenadas de objeto, ignora o UV da
malha, recebe o nome do arquivo e, na parede, nem chega ao nó que desenha a superfície. O resultado é que o usuário
não consegue acertar o veio, não consegue usar o UV Editor e não reconhece a textura fora do addon.

Esta entrega põe a textura em UV Map com escala em milímetros, dá ao material o nome do catálogo, abre o veio em
graus por armário e por parte e acrescenta o conta-gotas que copia a textura de um armário para vários escolhendo
Porta, Exterior ou Interior. Junto vai a correção da parede, que passa a receber material pelos sockets do nó.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `caffmob_draw/object_library/retexture.py:image_material` | Material "Textura: `<arquivo>` `<tamanho>` mm" com Image Texture em **projeção de caixa** sobre **coordenadas de objeto** e escala real; nenhum material usa UV da malha | 🟢 |
| `caffmob_draw/retexture.material_name` | O nome do material é montado do basename do arquivo, não do item do catálogo | 🟢 |
| `caffmob_draw/texture_library/grain.py` | O giro do veio é um Vector Rotate alimentado pelo atributo `btm_grain_rot`; `grain.projection` só informa se o grafo está em BOX ou UV, e `sync` liga o grafo nos materiais de imagem | 🟢 |
| `caffmob_draw/target/props.py` e `caffmob_draw/armario_v2/props.py` | `btm_part.grain` e `btm_armario_parte.veio` são enum `NONE`/`H`/`V` (o armário v2 usa `NONE`/`VERTICAL`/`HORIZONTAL`) | 🟢 |
| `caffmob_draw/textures/catalog.json` e `catalog_core.py` | Catálogo por fabricante → coleção → item ("Arauco" / "Colecao Realce" / "Anis"); `size_mm` dá o tamanho real, com chapa inteira em 1 px = 1 mm e `DEFAULT_SIZE_MM = 600` | 🟢 |
| `caffmob_draw/customize/finish_core.py` | Quatro domínios de acabamento: `INTERNAL` (interior da caixa e do fundo, prateleiras e divisórias), `EXTERNAL` (faces aparentes e fundo por trás), `FRONTS` (só frentes, veio nasce V) e `EDGE` (fita) | 🟢 |
| `_reversa_sdd/customize/requirements.md#RN-05` e `#RN-13` | Precedência de material e grupos `CAIXA`, `FRENTES`, `FUNDO`, `INTERNO`; a textura sobrevive a refazer o módulo | 🟢 |
| `caffmob_draw/texture_library/apply.py:targets` | O alvo da textura solta é resolvido por `selection.classify` (peça, frente, módulo ou objeto) e a fita fica fora | 🟢 |
| `caffmob_draw/customize/adapters/common.py:set_cutpart_material` | Escreve material em `GeoNodeCutpart` (Top/Bottom Surface), em sockets `Material`/`Stile Material`/`Panel Material`/`Rail Material` e, sem modificador, nos slots da malha | 🟢 |
| `caffmob_draw/operators/walls.py:home_builder_walls_OT_apply_wall_material` | A parede recebe material por `set_input` nos sockets `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge` | 🟢 |
| `caffmob_draw/operators/walls.py` (piso e teto) | Piso e teto criam `UVMap` planar (X,Y → U,V) junto com a malha | 🟢 |
| `caffmob_draw/armario_v2/build.py:gerar` | As peças nascem com material por `spec.acabamento`; **nenhum layer de UV é criado** e a peça grava `parte.material` e `parte.veio` | 🟢 |
| `caffmob_draw/geometry/obra_v2.py:uv_da_textura` | Já existe uma transformação de UV com centro 0,5, repeat e rotação por veio, reaproveitável como referência de escala | 🟢 |
| `_reversa_sdd/selection/requirements.md#RN-01` | Precisa classificar qualquer objeto para o conta-gotas achar peça, frente, módulo ou parede | 🟢 |
| `docs/rag/project/02_padroes_blender_5_2.md` | Receitas verificadas de `bpy.props` por atributo, entrada GN por `compat` e remoção de handlers | 🟢 |
| `CLAUDE.md` / `AGENTS.md` | Alvo 5.2, diferenças em `compat.py`, operadores com `UNDO`, `unregister` desfaz tudo, texto novo em português | 🟢 |

**Causas já localizadas**

1. **Parede não recebe textura** 🟢: `set_cutpart_material` não conhece os sockets da parede. A função cai no ramo
   "outras malhas", grava o material nos slots e devolve sucesso; o nó da parede continua com o material dos inputs.
   Nada muda na tela e nenhum aviso aparece.
2. **UV Editor sem efeito** 🟢: `image_material` monta `TexCoord → Mapping → Image Texture` em projeção `BOX` sobre
   coordenadas de objeto. O UV não participa do cálculo, então mover ilha de UV não muda nada. Em peça e parede
   geradas por Geometry Nodes há ainda o agravante de o UV avaliado vir do grafo.
3. **Veio binário** 🟢: o veio só existe como `NONE`/`H`/`V`; não há como girar 15°, 30° ou 45° para casar a
   textura com uma chapa vizinha.

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Fechar o acabamento do projeto | Aplica a textura do fabricante e gira o veio da porta até casar com o módulo vizinho |
| Projetista com vários armários iguais | Padronizar acabamento | Copia a textura de um armário com o conta-gotas e aplica nos outros só no exterior |
| Marceneiro | Reconhecer a chapa | Abre o material no Blender e vê "Arauco Anis", como no catálogo, sem abrir o addon |
| Arquiteto de ambiente | Texturizar a parede | Aplica a textura na parede e acerta o veio esticando o UV no UV Editor |

## 4. Regras de negócio novas ou alteradas

1. **RN-08:** Toda peça de armário recebe **UV Map próprio** com escala em milímetros: 1 unidade de UV equivale ao
   tamanho real da textura no catálogo (`texture_size_mm`), com a chapa inteira valendo 1 px = 1 mm quando a imagem
   estiver na faixa de chapa. Vale para a chapa do armário v2, que é malha simples; peça de biblioteca com
   `GeoNodeCutpart` recebe a textura pelo atributo `uv_map` que o nó gera (T001). 🟢
   - Origem: `caffmob_draw/texture_library/catalog_core.py:size_mm`; `caffmob_draw/geometry/obra_v2.py:uv_da_textura`
   - Tipo: nova
2. **RN-09:** O material de textura leva o **nome do item no addon** (fabricante + item, como "Arauco Anis"), e não
   o nome do arquivo; o arquivo, o tamanho e a projeção continuam gravados como propriedades do material. Coleção
   entra no nome só quando dois fabricantes têm item com o mesmo nome. 🟢
   - Origem: `caffmob_draw/textures/catalog.json`; `caffmob_draw/object_library/retexture.py:material_name`
   - Tipo: alterada
3. **RN-10:** O veio é girável **em graus**, por armário inteiro e por parte (porta, exterior, interior), sem criar
   material novo e sem refazer a malha; o veio de corte (`btm_part.grain`/`btm_armario_parte.veio`) acompanha o
   múltiplo de 90° mais próximo, para o plano de corte não divergir da imagem. 🟢
   - Origem: `caffmob_draw/texture_library/grain.py`; `caffmob_draw/target/props.py`
   - Tipo: alterada (hoje o veio é só NONE/H/V por peça)
4. **RN-11:** O **conta-gotas** copia de uma peça de origem a textura completa (imagem, tamanho em mm, calibração do
   veio e giro). Com mais de um armário selecionado, pergunta onde aplicar — **Porta**, **Exterior**, **Interior** —
   e aplica somente nas partes marcadas. A parte é marcada **clicando as peças na viewport**. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-23); `caffmob_draw/texture_library/apply.py:targets`;
     `caffmob_draw/customize/finish_core.py` (domínios)
   - Tipo: nova
5. **RN-14:** Parede, piso e teto recebem textura pelo **material do nó** (os seis sockets de parede e os de piso e
   teto), não pelo slot da malha; aplicar textura devolve sucesso só quando o material chegou ao nó, e falha com
   aviso quando o objeto não tem o modificador esperado. 🟢
   - Origem: `caffmob_draw/operators/walls.py:home_builder_walls_OT_apply_wall_material`;
     `caffmob_draw/customize/adapters/common.py:set_cutpart_material`
   - Tipo: alterada (correção da causa 1)
6. **RN-15:** O UV do usuário é **preservado** onde existe layer editável: material de textura lê o layer de UV
   quando a malha tem um, e a edição no UV Editor muda o resultado na vista. Sem layer, o material cai na projeção de
   caixa e a interface avisa. Em geometria gerada por Geometry Nodes (peça de biblioteca e parede), o UV é recalculado
   pelo grafo a cada avaliação: o addon avisa que ali o UV Editor não tem efeito, em vez de prometer edição (T001). 🟢
   - Origem: `caffmob_draw/object_library/retexture.py:image_material`; `caffmob_draw/texture_library/grain.py`
   - Tipo: alterada (correção da causa 2)
7. **RN-18:** Todo texto novo entra em português no código e no catálogo em `pt_BR` e `en_US`; todo operador que muda
   a cena declara `UNDO` e todo handler novo tem remoção no `unregister`. 🟢
   - Origem: `caffmob_draw/data/i18n.py`; `CLAUDE.md`
   - Tipo: mantida

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-07 | UV Map em mm em todas as peças do armário, respeitando `texture_size_mm` do catálogo (RN-08) | Must | Chapa de 600 × 400 com textura de 600 mm mostra uma repetição inteira na largura e 2/3 na altura | 🟢 |
| RF-08 | Material de textura nomeado pelo item do catálogo e reconhecível fora do addon (RN-09) | Must | Aplicar "Arauco Anis" cria material chamado "Arauco Anis", com arquivo, tamanho e projeção preservados em propriedades | 🟢 |
| RF-09 | Rotação do veio em graus, por armário e por parte, sem recriar material nem malha (RN-10) | Must | Girar 90° no exterior gira o veio das chapas externas daquele armário e não muda as portas; outro armário com a mesma textura não muda | 🟢 |
| RF-10 | Conta-gotas de textura com escolha de parte por clique ao aplicar em vários armários (RN-11) | Must | Copiar de um armário e aplicar em três com só "Porta" marcada muda as portas dos três e deixa o interior intacto | 🟢 |
| RF-13 | Textura aplicável em parede, piso e teto pelos sockets do nó, com erro visível quando não há nó (RN-14) | Must | Aplicar textura numa parede muda a vista e grava o material nos seis sockets; objeto marcado como parede sem modificador devolve aviso e não muda a cena | 🟢 |
| RF-14 | UV Editor funcional onde há layer editável: material lê UV e a edição muda a vista; em malha com GN o addon explica que o UV é do grafo (RN-15) | Must | No armário v2, mover a ilha muda a textura na face; em peça com `GeoNodeCutpart` a textura aparece pelo `uv_map` e o painel avisa que aquele UV vem do grafo; malha sem layer avisa e usa projeção de caixa | 🟢 |
| RF-18 | Textos novos em português e inglês nos contextos padrão e de operador (RN-18) | Must | Com a interface em inglês, conta-gotas, veio e aviso de parede aparecem traduzidos e o teste de cobertura de i18n passa | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Aplicar conta-gotas em 10 armários em até 0,5 s; girar o veio sem recriar malha em até 100 ms | `grain.sync` só reescreve atributo e liga nós; a aplicação reusa material por (arquivo, tamanho, projeção) | 🟡 |
| Compatibilidade | Alvo Blender 5.2; leitura e escrita de input de Geometry Nodes só por `compat.get_gn_input`/`set_gn_input`/`gn_input_data_path` | `CLAUDE.md`; `docs/rag/project/03_compatibilidade_5x.md` | 🟢 |
| Compatibilidade | Arquivo antigo com material "Textura: arquivo tamanho" abre, é reconhecido e adota o nome novo na primeira edição; arquivo sem UV continua editável | Precedente M-05 (`grain.py:_restore_legacy`) | 🟢 |
| Manutenibilidade | Escala de UV, rotação, nome de material e mapa de partes em núcleo puro, testável fora do Blender | Padrão das features 014, 016 e 017 | 🟢 |
| Robustez | Textura solta em objeto sem malha, parede sem modificador, malha sem UV e material de catálogo ausente devolvem mensagem, sem traceback e sem material parcial | `apply.py` já devolve `ERROR`/`NO_TARGET`; `walls.py` só aplica em `IS_WALL_BP` | 🟢 |
| Ciclo de vida | Handlers novos (conta-gotas, destaque de partes) têm remoção no `unregister`; propriedades novas em `bpy.types.*` são apagadas | `CLAUDE.md` | 🟢 |
| Idiomas | Catálogo novo em `pt_BR` e `en_US`, contextos padrão e de operador, sem chave repetida de catálogos existentes | `caffmob_draw/data/i18n.py`; `tests/test_i18n_coverage.py` | 🟢 |
| Custo | Nenhuma chamada a modelo de IA ou serviço externo: UV, nome e veio são regra determinística local | Diretriz de controle de custo do projeto | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Textura do catálogo com nome do addon
  Dado o catálogo com o item "Arauco Anis"
  Quando o usuário aplica essa textura numa chapa
  Então o material criado se chama "Arauco Anis"
  E o arquivo de origem, o tamanho em mm e a projeção continuam gravados no material

Cenário: Item homônimo em dois fabricantes
  Dado "Anis" na Arauco e "Anis" em outro fabricante
  Quando o usuário aplica as duas texturas
  Então o primeiro material se chama "Arauco Anis"
  E o segundo leva a coleção no nome, sem sobrescrever o primeiro

Cenário: UV em milímetros
  Dado um armário com textura de 600 mm e uma chapa de 600 por 400
  Quando a textura é aplicada
  Então o UV da chapa repete exatamente uma textura na largura
  E dois terços da textura na altura

Cenário: Edição no UV Editor muda a vista
  Dado um armário com textura aplicada por UV
  Quando o usuário move uma ilha de UV no UV Editor
  Então a textura da face correspondente se move na vista 3D
  E salvar o arquivo preserva o UV editado

Cenário: Malha sem UV
  Dado uma malha importada sem layer de UV
  Quando o usuário aplica a textura
  Então a textura aparece pela projeção de caixa
  E o addon avisa que a malha não tem UV e que o UV Editor não terá efeito nela

Cenário: Veio girado por parte
  Dado um armário com a mesma textura no exterior e na porta
  Quando o usuário gira o veio do exterior em 90 graus
  Então só as chapas externas giram
  E a porta e o veio de corte da porta continuam como estavam

Cenário: Veio em ângulo intermediário
  Dado um veio girado em 30 graus numa chapa
  Quando o usuário abre o plano de corte
  Então a chapa continua listada com o veio horizontal ou vertical mais próximo
  E o aviso do ângulo visual aparece no painel da textura

Cenário: Conta-gotas em vários armários
  Dado um armário com textura de referência e outros três selecionados
  Quando o usuário usa o conta-gotas, clica a porta de origem e marca só Porta
  Então as portas dos três recebem a textura, o tamanho e o giro
  E exterior e interior deles não mudam

Cenário: Conta-gotas sem origem
  Dado que nenhuma peça com textura foi escolhida como origem
  Quando o usuário aciona o conta-gotas
  Então o addon avisa que falta a origem
  E nenhum material é trocado

Cenário: Parede recebe textura
  Dado uma parede do projeto com o modificador de parede
  Quando o usuário aplica a textura do catálogo
  Então a vista mostra a textura nas faces internas e externas
  E o material está nos sockets do nó, não só no slot da malha

Cenário: Parede sem modificador
  Dado um objeto marcado como parede, sem o modificador esperado
  Quando o usuário aplica textura
  Então o addon avisa que a parede não aceita textura
  E a cena não muda

Cenário: Interface em inglês
  Dado o Blender com a interface em inglês
  Quando o usuário abre o conta-gotas e o painel de veio
  Então todos os textos aparecem em inglês
  E o teste de cobertura de i18n passa
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-07, RF-08, RF-14 | Must | Sem UV em mm, sem nome do catálogo e sem UV Editor a textura continua imprevisível |
| RF-13 | Must | Textura em parede é hoje um no-op silencioso: é defeito, não melhoria |
| RF-09 | Must | O usuário pediu veio fácil; hoje só existe H/V |
| RF-10 | Should | O conta-gotas é o ganho de escala; sem ele a aplicação peça a peça ainda resolve |
| RF-18 | Must | Regra do projeto e condição do teste de cobertura |
| Girar o veio por face (não por parte) | Could | O pedido fala em armário e parte; face fica para depois |
| Projeção cilíndrica ou esférica | Won't (nesta feature) | Chapas são planas; projeção por UV cobre o caso |

## 9. Esclarecimentos

### Sessão 2026-11-23

- **Q:** O pedido "redimensionar um armário e o…" terminou truncado. Como o redimensionamento deve funcionar?
  **R:** Diálogo de medidas e alças de arraste na viewport; nos dois caminhos o armário é regenerado como conjunto.
  Movido para `019-redimensionar-e-colisao`.
- **Q:** O que qualifica "qualquer peça que tenha requisitos de armários"?
  **R:** Um conjunto de malhas selecionadas é lido como um móvel e cada chapa recebe um papel. Movido para
  `020-converter-em-armario`.
- **Q:** Como o usuário aponta fundo, lateral, base e porta, e depois exterior/interior no conta-gotas?
  **R:** Clicando cada peça no diálogo, com destaque na viewport; o mesmo gesto marca exterior e interior. Aplicado
  em RN-11, RF-10 e no cenário do conta-gotas.
- **Q:** O que acontece com a malha original na conversão?
  **R:** Continua na cena, oculta, fora do corte e com os modificadores intactos, com um passo de desfazer. Movido
  para `020-converter-em-armario`.
- **Q:** E se a origem tiver modificadores ou hierarquia?
  **R:** Os modificadores são aplicados e a conversão usa a geometria avaliada; a origem preservada guarda o
  empilhamento original. Movido para `020-converter-em-armario`.

**Consequências registradas**

- O gesto de apontar parte por clique nasce nesta feature, porque o conta-gotas precisa dele; a conversão da 020
  reaproveita o mesmo gesto.
- O domínio de acabamento da 067 (`INTERNAL`/`EXTERNAL`/`FRONTS`) é o mapa oficial para Interior/Exterior/Porta: não
  se cria um segundo vocabulário de partes.

## 10. Lacunas

- 🟢 Sem dúvidas abertas para esta fatia.
- 🟡 O nome do material antigo ("Textura: arquivo tamanho") precisa de migração na primeira edição; a regra de
  renomear sem quebrar material compartilhado entre armários fica para o `/reversa-plan`.
- 🟡 A interação entre UV gravado na malha base e o UV gerado pelo Geometry Node de chapa e de parede precisa ser
  verificada no Blender; se o grafo gerar UV, o material precisa de uma fonte de UV explícita por objeto.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-23 | Versão inicial gerada por `/reversa-requirements` a partir do pedido do titular, da extração reversa e do código de textura, menu de contexto e redimensionamento | reversa |
| 2026-11-23 | `/reversa-clarify`: redimensionamento por diálogo e alças, conversão de conjunto de malhas, marcação por clique, origem preservada e modificadores aplicados; RN-01, RN-02, RN-03, RN-11, RN-12, RF-01, RF-02, RF-04, RF-10 e RF-11 ajustados | reversa |
| 2026-11-23 | Escopo fatiado: textura/UV/veio/conta-gotas/parede ficam nesta 018; redimensionar, veio do armário e colisão vão para a 019; conversão e biblioteca vão para a 020. IDs de RN/RF preservados | reversa |
| 2026-11-23 | T001 no Blender 5.2: RN-08, RN-15 e RF-14 ajustados ao que o nó realmente entrega (peça de biblioteca sem layer de UV, parede com `UVMap` gerado, UV Editor garantido só onde há layer editável) | reversa |
