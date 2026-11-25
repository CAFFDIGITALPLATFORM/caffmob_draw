# Investigation: 024-materiais-uv-preferencias

> Pesquisa de fundo do `/reversa-plan`. Fatos medidos no código desta árvore, não de memória.

## 1. O que já existe

| Fato | Onde | Consequência para a 024 |
|------|------|--------------------------|
| A chapa já nasce com `UVMap` planar **em metros**, por eixo dominante da normal | `caffmob_draw/armario_v2/build.py:396-420` (`_uv_metros`) | Não é preciso criar UV do zero; falta **distinguir dentro/fora/fita** na mesma malha |
| O material da chapa é `Principled BSDF` com `Base Color` sólido por acabamento | `caffmob_draw/armario_v2/build.py:309-327` (`_material`, `materiais`) | O passo novo é o `ShaderNodeTexImage` + `Mapping`; o resto da cadeia (material por peça) fica |
| O material escolhido na peça vence o acabamento do spec | `build.py:608` (`_material_da_peca`) | A textura padrão **não pode** sobrescrever escolha do usuário |
| A fita de borda é uma **faixa fina separada**, caixa de 6 faces, com material liso por cor | `caffmob_draw/edgeband/build.py:16-55` | A faixa tem malha própria: o UV dela é independente e pode usar U no comprimento |
| O Solid é forçado para `color_type = 'OBJECT'` num fluxo de detalhes | `caffmob_draw/hb_details.py:98-99` | É o ponto exato do “cor de objeto” que a 024 troca por `'TEXTURE'` |
| A preferência de cor do armário é `cabinet_color` (FloatVector), em `BTM_AddonPreferences` | `caffmob_draw/__init__.py:195` | Vira cor de apoio/legado; o controle novo é o enum `exibicao_armario` |
| **Não existe** arquivo de textura MDF no pacote; `caffmob_draw/assets/` tem ícone, fontes, ferragens, corrediças e refs dimensionais | `find caffmob_draw -iname "*.png"` | A textura padrão precisa ser gerada (runtime) ou adicionada como asset novo |
| O veio e o UV de textura já têm núcleo puro | `caffmob_draw/texture_library/uv_core.py` | Reaproveitar `LAYER_UV` e o vocabulário de veio em vez de duplicar |
| O armário v2 guarda ajustes por peça e a raiz tem coleções versionadas | `armario_v2/props.py`, `build.py` | A marca `exibicao_versao` cabe na raiz, junto de `gerado`/`ajustes` |

## 2. Alternativas avaliadas

### 2.1 UV por face

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| **A. Classificar faces por normal + posição** e gravar UV por face num núcleo puro | Testável sem `bpy`; funciona com malha modificada; corrige dentro/fora | Precisa definir o referencial da peça (centro da caixa) e o sinal do espelho | **Escolhida (D-03)** |
| B. Material por face (slot por face) | Simples de ler no viewport | Estoura slots com 3+ materiais por peça e complica o plano de corte | Descartada |
| C. Textura projetada em caixa (`projection = 'BOX'`) sem UV explícito | Zero código de malha | Não distingue a fita, e o mesmo mapa cobre dentro e fora igual | Descartada |

### 2.2 Textura padrão

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| **A. Imagem gerada em runtime e empacotada** | Sem asset binário, sem licença, offline, determinístico | Aparência precisa de grão bem feito | **Escolhida (D-01)** |
| B. PNG novo em `caffmob_draw/assets/textures/` | Mais fácil de ficar bonito | Licença, peso no ZIP e `build.py` passa a depender do arquivo | Descartada nesta rodada |
| C. Baixar do catálogo MOBI na primeira abertura | Textura real do fabricante | Quebra offline e depende de login | Descartada |

### 2.3 Linhas

| Alternativa | Prós | Contras | Veredito |
|-------------|------|---------|----------|
| **A. Contorno da própria malha** (outline/arestas) | Sem objeto extra; acompanha edição | Aparência depende do motor de desenho | **Escolhida (D-06)** |
| B. Objeto wireframe por peça | Controle total da espessura | Duplica a cena, undo e seleção | Descartada |

## 3. Referências

- `docs/rag/blender-api/corpus/bpy.types.ShaderNodeTexImage.md` — `projection`, `extension` e `image` do nó de textura.
- `docs/rag/project/02_padroes_blender_5_2.md` — criação de material com nós e `Mapping`.
- `_reversa_sdd/addenda/017-construtor-armario-v2.md` — peças, materiais e contrato de chapa do v2.
- `_reversa_forward/018-textura-uv-veio/requirements.md` — precedente de UV em metros e veio.
- `caffmob_draw/edgeband/build.py` — geometria e material da fita.

## 4. Lacunas de pesquisa

- Aparência exata do MDF claro gerado: só uma sessão gráfica julga. O plano cobre com teste de que a imagem existe,
  está empacotada e é usada pelo material; o julgamento visual fica para o onboarding manual.
- “Cursos 3D” não aparece em nenhuma string do código; o plano trata como “não remover opções existentes”.
