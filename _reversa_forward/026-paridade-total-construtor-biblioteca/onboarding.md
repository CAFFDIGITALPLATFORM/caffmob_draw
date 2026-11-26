# Handoff — Feature 026: paridade total do Construtor e da Biblioteca

> **ATUALIZAÇÃO 2026-11-26:** a feature 026 foi implementada e fechada nesta rodada. Este arquivo nasceu como
> handoff (antes da implementação) e as seções 5–6 descrevem o estado **histórico** daquele momento; o estado
> vigente está em `requirements.md`, `roadmap.md`, `actions.md` (12/12) e `audit/cross-check.md` (0/0/0/0).
> Versão 1.35.0, commit local sem push.

- **Feature:** `026-paridade-total-construtor-biblioteca`
- **Diretório:** `_reversa_forward/026-paridade-total-construtor-biblioteca/`
- **Base:** `master`, `cd818a43` (025), tag `v1.34.0`; a 026 está commitada localmente após esta rodada
- **Data do handoff original:** 2026-11-26
- **Idioma do projeto:** português (código, UI, docs e mensagens)
- **Regra de ouro:** o documento vence o código onde divergir; nada do mockup pode ser marcado como “fora de escopo”.

---

## 1. Prompt de retomada (copiar para o próximo agente)

```text
Você é o agente de continuação da feature 026 do CAFFMob Draw (Blender 5.2).

Antes de escrever código:
1. Leia _reversa_forward/026-paridade-total-construtor-biblioteca/onboarding.md inteiro.
2. Rode `git status --short` e `git log -3 --oneline --decorate`; confirme se ainda está em cd818a43/v1.34.0.
3. Rode `git diff -- caffmob_draw/armario_v2/window.py caffmob_draw/armario_v2/preview.py` e trate as edições
   parciais descritas na seção 5 como NÃO integradas.
4. Não altere AGENTS.md nem commite os arquivos proibidos da seção 12.
5. Use a estrutura Reversa: crie requirements.md, roadmap.md e actions.md da 026 antes de codar; só então
   atualize .reversa/active-requirements.json para a 026. A 025 está fechada e não deve ser reaberta.
6. Implemente a paridade listada na seção 6 e a Biblioteca da seção 7; cada item precisa de código + prova
   automatizada executada nesta rodada.
7. Só escreva audit/cross-check.md com 0 CRITICAL/HIGH/MEDIUM/LOW se a matriz da seção 9 não tiver nenhuma
   linha PENDENTE/BLOQUEADA/fora de escopo. Impossibilidade técnica é bloqueio explícito para o usuário,
   nunca uma decisão de escopo.
8. Não faça push. Commit local coerente ao final.

Objetivo: paridade total do Construtor com
novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html
e da Biblioteca com os dois pacotes docs/Caff+Mob+Biblioteca+Mockup.tar.gz e
docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz.
Mantenha intacto o fluxo 025: Criar armário abre a viewport; Aplicar pergunta Escolher vs Cursor 3D;
Escolher mostra a caixa de arame com setas e clique; Cursor 3D preserva o giro.
```

---

## 2. Missão e definição de pronto

### 2.1 Construtor

Cada função visual e funcional do mockup HTML deve existir e funcionar **dentro do Blender**, sem item
“fora da paridade”. Os dez itens que a entrega 023 deixou de fora e que a 026 precisa implementar de verdade:

1. toolbar completa;
2. export JSON;
3. titlebar;
4. abas horizontais;
5. menu de contexto da janela 023;
6. popover de medida;
7. arraste de peças;
8. cutlist;
9. “Apenas Laterais”;
10. alternador Light/Dark.

Além disso, preservar sem regressão:

- Criar armário abre a viewport direto;
- Aplicar pergunta “Escolher” ou “Cursor 3D”;
- “Escolher” desenha o armário em linhas acompanhando o mouse;
- setas cima/baixo/esquerda/direita mudam a orientação da caixa de arame;
- clique adiciona no ponto escolhido;
- “Cursor 3D” cria na posição do cursor 3D preservando o giro;
- Esc/botão direito cancelam o fluxo;
- fallback sem viewport continua funcionando.

### 2.2 Biblioteca

A galeria deve seguir **por inteiro** os dois pacotes de `docs/`, não apenas a paleta Light: categorias,
estrutura de blocos/texturas, layout, estados, filtros, card de detalhe, conta/avatar, controles de janela,
tema Light/Dark e padrões visuais. O documento vence o código atual.

### 2.3 Fechamento Reversa

- `requirements.md`, `roadmap.md`, `actions.md` com 100% das ações concluídas;
- `data-delta.md`, `legacy-impact.md`, `regression-watch.md` e `progress.jsonl` coerentes;
- catálogos i18n completos (`armario_v2.json`, `library.json`), sem chave ausente;
- matriz função→código→teste sem linha pendente;
- `audit/cross-check.md` estrito, 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW;
- versão/CHANGELOG atualizados;
- commit local, **sem push**.

---

## 3. Fontes de verdade

| Fonte | Caminho | Uso |
|---|---|---|
| Mockup do Construtor | `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html` | Funções visuais/funcionais do Construtor |
| Pacote visual da Biblioteca | `docs/Caff+Mob+Biblioteca+Mockup.tar.gz` | Aparência, categorias, layout, estados |
| Requisitos da Biblioteca | `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz` | RF01–RF14, cores Light/Dark, critérios |
| Feature 023 | `_reversa_forward/023-janela-mockup-construtor/` | Escopo híbrido antigo, auditoria, ações; **não** é a decisão vigente |
| Feature 025 | `_reversa_forward/025-criacao-posicionamento-armario/` | Fluxo já entregue, provas e auditoria 0/0/0/0 |
| RAG Blender 5.2 | `docs/rag/` | Assinaturas de API; consultar antes de usar `bpy`/`gpu`/`blf` |

Os dois `.tar.gz` são **untracked** no git neste momento. Não os commite. Extraia para `/tmp` ou para uma pasta
ignorada e leia o conteúdo; não dependa dos arquivos `/tmp/library_ui.tsx` e `/tmp/library_app.tsx` citados na
memória anterior, porque `/tmp` pode ter sido limpo.

Trechos já mapeados do mockup do Construtor (números de linha aproximados; reconfirme no arquivo):

- titlebar ~767;
- toolbar ~780;
- export JSON ~791;
- “Apenas Laterais” ~810;
- menu de contexto ~866;
- popover de medida ~884;
- modal do contrato de chapas ~892;
- cutlist ~906.

---

## 4. O que já está entregue e não pode regredir

A feature 025 está fechada e commitada em `cd818a43`, tag `v1.34.0`, sem push.

Ela entregou:

- Criar armário na viewport;
- Aplicar com popup “Escolher” ou “Cursor 3D”;
- caixa de arame seguindo o mouse;
- setas mudando a orientação;
- clique para inserir;
- Cursor 3D preservando o giro;
- fallback quando não há viewport;
- paleta Light da Biblioteca (`#FFFBF5`, `#FFF8EC`, `#F5EFE3`, `#2B1A0E`, `#B45309`, `#0E7C74`);
- auditoria 025 em `_reversa_forward/025-criacao-posicionamento-armario/audit/cross-check.md` com 0/0/0/0.

Provas registradas na 025 (repetir antes de encerrar a 026):

- `tests/blender_025_place.py` — 16/16;
- `test_placement_025` + `test_library_style_025` — 7/7;
- card da Biblioteca — 38/38;
- UI 012 — 9/9;
- puros da Biblioteca — 36/36;
- puros amplos — 54/54;
- i18n — 3/3;
- smoke 017 — OK;
- `check_api.py` — 637 arquivos OK;
- ruff nos arquivos novos limpo.

Não reabra a 025 como se fosse correção. A 026 é uma feature nova.

---

## 5. Estado real do working tree (importante)

No momento do handoff, `git status --short` mostra:

```text
 M AGENTS.md
 M caffmob_draw/armario_v2/preview.py
 M caffmob_draw/armario_v2/window.py
?? biblioteca_detalhe.png
?? docs/Caff+Mob+Biblioteca+Mockup.tar.gz
?? docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz
?? prompt_025.png
```

### 5.1 Edições parciais da 026 já aplicadas (não integradas)

**`caffmob_draw/armario_v2/window.py`**

- adiciona `VISTAS = ('SPLIT', 'FRONTAL', 'LATERAL')`;
- adiciona `TEMAS = ('LIGHT', 'DARK')`;
- adiciona `ARRASTE_MIN_PX = 3.0`;
- adiciona à `JanelaSessao`: `vista`, `tema`, `apenas_laterais`, `escala_frontal`, `deslocamento_frontal`;
- adiciona `registrar_movimento(root, obj, dx_mm, dz_mm)`;
- adiciona `registrar_duplicata(root, obj)`.

**`caffmob_draw/armario_v2/preview.py`**

- adiciona `PALETAS` Light/Dark e `aplicar_tema(tema)`;
- mantém as cores Light existentes.

### 5.2 Defeitos latentes dessas edições (corrigir antes de usar)

1. `registrar_duplicata()` grava `ajuste.duplicada`, mas **`BTM_PG_ArmarioAjuste` ainda não tem essa propriedade**
   em `caffmob_draw/armario_v2/props.py`. Ou implemente a propriedade + recriação no `build.gerar`, ou remova o
   helper. Não deixe um caminho que estoura AttributeError.
2. `preview.aplicar_tema()` troca os globais `COR_*`, mas o dicionário **`CORES` é montado uma única vez no import**
   com as cores Light. Portanto, trocar o tema não repinta as peças até `CORES` passar a ser derivado em tempo de
   desenho (ou recalculado por `aplicar_tema`).
3. `aplicar_tema()` ainda **não é chamado** por nenhum caminho de desenho. O tema da sessão não tem efeito prático.
4. `escala_frontal` e `deslocamento_frontal` são declarados, mas ainda não são preenchidos pelo preview; sem isso o
   arraste não consegue converter pixels em milímetros.
5. Não há testes para essas edições. Não as considere “prontas” só porque o import funciona.

Se a próxima sessão não for continuar exatamente esse caminho, reverta **apenas** esses dois arquivos para o HEAD
(`git checkout -- caffmob_draw/armario_v2/window.py caffmob_draw/armario_v2/preview.py`) e recomece de forma
consciente. Nunca use `git checkout .`, porque `AGENTS.md` e os untracked não devem ser mexidos.

---

## 6. Lacunas do Construtor (checklist da 026)

Status inicial: **PENDENTE** para todos os itens abaixo. Nenhum deve ser marcado como “fora de escopo”.

| # | Item do mockup | Onde implementar | Prova mínima exigida |
|---|---|---|---|
| C01 | Toolbar completa (montar/limpar, vistas, cotas, portas, abrir/fechar tudo, export, laterais, tema, painel) | `armario_v2/panel_window.py`; operadores em `ops_window.py` | Ensaio de UI que encontra cada botão/operador e executa a ação |
| C02 | Export JSON | novo operador + serializador puro | Arquivo JSON gerado, campos e peças conferidos; teste puro do payload |
| C03 | Titlebar (título, dimensões/status, ações de janela) | `panel_window.py` (cabeçalho nativo) | Teste que valida o painel/rótulos e ações do cabeçalho |
| C04 | Abas horizontais | `panel_window.py`; manter `window.ABAS` e `sessao.aba` | Teste que percorre as 7 abas em uma única linha/ordem horizontal |
| C05 | Menu de contexto da janela 023 | `ops_window.py` (RIGHTMOUSE) + menu | Teste do `draw` do menu e do caminho modal de botão direito |
| C06 | Popover de medida | operador com `invoke_props_dialog` | Teste `EXEC_DEFAULT` alterando largura/altura/profundidade e regenerando |
| C07 | Arraste de peças | modal + `window.registrar_movimento` + escala do preview | Ensaio sintético press→move→release; posição e ajuste persistidos |
| C08 | Cutlist | painel de peças existente + export | Teste que lista peças e exporta; conferir totais/espessuras |
| C09 | “Apenas Laterais” | operador que liga laterais e desliga base/fundo, gera | Teste das flags e do resultado geométrico |
| C10 | Alternador Light/Dark | `preview.aplicar_tema` + botão na toolbar; Biblioteca em `library_panel` | Teste dos tokens Light/Dark e do clique que troca o tema |

### 6.1 Arquitetura existente que deve ser reaproveitada

- `panel_window.py`: 7 abas, header/toolbar/lista/rodapé, empty state; hoje as abas são desenhadas em duas linhas.
- `ops_window.py`: modal, fila, Aplicar; hoje trata LEFTMOUSE/ESC, **não** trata RIGHTMOUSE/drag.
- `window.py`: `JanelaSessao`, seleção, `aplicar_lote`, memória, preview handler.
- `preview.py`: vista frontal/lateral, cores, hits.
- `ops_placement.py`, `placement.py`: fluxo 025 que deve permanecer.
- `validar.pecas_da_raiz`: fonte para cutlist/export.
- `build.gerar`: recria as peças; ajustes em `btm_armario.ajustes` sobrevivem ao Gerar.
- `anim.alternar(alvo)`: abre/fecha peças animáveis.
- `Scene.btm_armario_contrato` (`BTM_PG_ContratoChapas`): contrato de chapas já existe em `props.py`;
  `panel.py` já expõe `comprimento_max`/`largura_max`.
- `bpy_extras.io_utils.ExportHelper`: usar para o seletor de arquivo do JSON, se necessário.

### 6.2 Decisões já tomadas

- Emular titlebar/abas horizontais com painéis nativos do Blender, em vez de uma camada GPU própria, **se**
  funcionalmente equivalente. A 023 declarou isso “fora”; a 026 não pode repetir essa exclusão.
- O tema do Construtor pode colorir o preview (área desenhada); o chrome nativo do Blender não é repintado por
  add-on. Se isso for considerado não conforme, registrar como **bloqueio explícito**, não como decisão de escopo.
- “Apenas Laterais” deve ser uma ação real de geração (laterais ligadas, base/fundo desligados), não só um filtro
  visual.
- Cutlist pode reaproveitar o painel de peças existente, desde que exporte e seja provada.
- Export JSON deve sobreviver ao Gerar: serializar o spec/peças atuais com campos estáveis.

---

## 7. Lacunas da Biblioteca (pacotes de `docs/`)

### 7.1 Requisitos RF01–RF14 (números conforme o pacote de requisitos; reconfirme no tar)

| RF | Requisito | Estado atual | O que falta |
|---|---|---|---|
| RF01 | Cabeçalho/título da Biblioteca | `draw.py` tem título “Biblioteca”, logo, abas, busca, conta, Pin/min/close | Conferir contra o mockup; adicionar título/subtítulo e estados exatos |
| RF02 | Abas Biblioteca / Blocos / Texturas | `TABS` em `draw.py` | Conferir rótulos, ordem, estado ativo e ícones |
| RF03 | Categorias Armários / Portas / Janelas / Armários autorais | `categories_core.FIXED` ainda é Cozinha/Dormitório/Banheiro/Sala/Home office + Portas/Janelas | Trocar a navegação para as 4 categorias do documento, preservando as linhas/ambientes no card de detalhe |
| RF04 | Busca | existe | Conferir placeholder, limpar, foco e resultado vazio |
| RF05 | Filtros Madeira/Alumínio/Blindex | `_draw_blocks_controls` tem os três | Conferir estado ativo, contagem e combinação com busca |
| RF06 | 6 modelos em grade 2×3 | `grid_core.CELL_W/H = 140/188`; colunas calculadas pela largura (teste atual exige ≥4) | Implementar a grade 2×3 da Biblioteca (modo/célula própria); não quebrar a grade de texturas sem decisão explícita |
| RF07 | Seleção laranja + “Selecionado” | existe | Conferir no estado final e no card |
| RF08 | Card de detalhe/medidas/ambiente | `detail_core.py` existe | Conferir RFs e campos do pacote |
| RF09 | Inserir/Substituir pelo selecionado | `_draw_blocks_controls` + operadores | Provar os dois caminhos |
| RF10 | Conta/avatar e menu | `caffmob.texture_account_menu` existe; chip de conta no header | Conferir itens do documento (entrar, trocar, gerenciar, sair) e estados |
| RF11 | Pin/minimizar/fechar | existem | Conferir alvos, estados e persistência |
| RF12 | Light/Dark | `style.py` é Light fixo; comentário diz que Dark é só referência | Implementar tema dinâmico e alternador persistido, com tokens do documento |
| RF13 | Alvos de toque de 44 px | `BUTTON=22`, `CONTROL_H=22` | Ajustar/justificar por escala; provar que os controles atingem o mínimo do documento |
| RF14 | Layout responsivo/estados vazios | parcial | Conferir larguras, compactação, vazio e erro |

### 7.2 Arquitetura atual da Biblioteca

- `caffmob_draw/library_panel/categories_core.py`: categorias fixas + `OPENING_CATEGORIES` + usuário.
  `LINES`/`LINE_LABELS` continuam sendo os ambientes usados pelo card; não misture linha com categoria.
- `caffmob_draw/library_panel/style.py`: tokens Light fixos; `CELL_W/H` vêm de `grid_core`.
- `caffmob_draw/library_panel/draw.py`: header, abas, busca, conta, botões, sidebar, grade, card, controles.
- `caffmob_draw/library_panel/layout_core.py`: `max_layout`, `BUTTON_KEYS = ('CLOSE','MINIMIZE','PIN')`,
  `hit_max`, sidebar.
- `caffmob_draw/library_panel/grid_core.py`: `CELL_W/H=140/188`, `columns()` por largura, `visible_cells()`.
- `caffmob_draw/library_panel/props.py`: estado `btm_library`.
- `caffmob_draw/library_panel/ops_click.py`: cliques; conta chama `caffmob.texture_account_menu`.
- `caffmob_draw/library_panel/detail_core.py`: card/medidas/ambiente.
- `caffmob_draw/texture_library/ops_account.py`: menu de conta existente.

### 7.3 Decisões da Biblioteca

- O documento vence o código atual. Se a grade 2×3 conflitar com a grade de texturas, separe os modos em vez de
  violar um dos dois.
- Categorias do documento substituem a navegação por ambientes; os ambientes podem continuar no detalhe/inserção.
- Tema Light é o padrão; Dark precisa ser real e persistido, não só um comentário.
- Conta/avatar: reutilizar o menu existente e completar o que o RF10 exigir; não inventar backend.
- Alvos de 44 px: se a escala do painel impedir, registrar como bloqueio de plataforma, não como “detalhe visual”.

---

## 8. Provas e comandos

### 8.1 Blender

```bash
BLENDER="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
"$BLENDER" --factory-startup --enable-event-simulate --python-exit-code 1 \
  --python tests/blender_026_parity.py
```

Regras:

- `screen.screenshot` do Blender **não captura popups/modais**. A prova de popup/modal deve ser por hook do
  operador, evento sintético ou chamada direta de `execute`/`invoke`, não por screenshot.
- `Window.width/height` são readonly no Blender 5.2 (limitação A015).
- `--factory-startup` é obrigatório para isolar preferências.

### 8.2 Testes puros

```bash
cd tests
PYTHONIOENCODING=utf-8 python -m unittest test_placement_025 test_library_style_025
PYTHONIOENCODING=utf-8 python -m unittest test_library_detail test_library_environments test_library_grid test_library_layout
```

Bateria ampla registrada na 025:

```bash
cd tests
PYTHONIOENCODING=utf-8 python -m unittest test_017_build test_017_corte test_janela_023_core \
  test_face_uv_024 test_mdf_core_024 test_view_mode test_placement_025 test_library_style_025
```

### 8.3 Compatibilidade e lint

```bash
PYTHONIOENCODING=utf-8 python docs/rag/tools/check_api.py
ruff check caffmob_draw/armario_v2 caffmob_draw/library_panel
```

`check_api.py`: `[UNKNOWN in 5.2]` é erro. Não use assinatura “de memória”; consulte `docs/rag/`.

### 8.4 i18n

```bash
PYTHONIOENCODING=utf-8 python -m unittest tests.test_i18n
```

Conferir também `caffmob_draw/data/translations/armario_v2.json` e `library.json`; toda string nova de UI precisa
de chave nos dois catálogos quando aplicável.

### 8.5 Prova de popup/modal por hook (obrigatória)

Padrão já usado na 025: chamar o operador com `EXEC_DEFAULT`/`INVOKE_DEFAULT` em contexto controlado e inspecionar
o estado resultante (fila, sessão, cena, arquivo JSON). Para menus, chamar `draw` com um layout falso e conferir os
operadores; para modal, enviar eventos sintéticos e ler `sessao`.

---

## 9. Matriz de rastreabilidade (modelo obrigatório)

Cada linha precisa de **código implementado + prova executada nesta rodada**. Não basta citar teste antigo.
Uma linha `PENDENTE`, `BLOQUEADA` ou “fora de escopo” impede o cross-check 0/0/0/0.

```markdown
| ID | Fonte | Função/requisito | Código | Prova executada | Resultado |
|---|---|---|---|---|---|
| C01 | mockup :780 | toolbar completa | panel_window.py / ops_window.py | tests/blender_026_parity.py::... | PASSOU |
| C02 | mockup :791 | export JSON | ops_window.py / parity_core.py | ... | PASSOU |
| C03 | mockup :767 | titlebar | panel_window.py | ... | PASSOU |
| C04 | mockup | abas horizontais | panel_window.py | ... | PASSOU |
| C05 | mockup :866 | menu de contexto | ops_window.py | ... | PASSOU |
| C06 | mockup :884 | popover de medida | ops_window.py | ... | PASSOU |
| C07 | mockup | arraste de peças | ops_window.py / window.py | ... | PASSOU |
| C08 | mockup :906 | cutlist | panel_window.py / ops_window.py | ... | PASSOU |
| C09 | mockup :810 | Apenas Laterais | ops_window.py / build.py | ... | PASSOU |
| C10 | mockup | Light/Dark | preview.py / library_panel/style.py | ... | PASSOU |
| L01 | RF01 | cabeçalho Biblioteca | library_panel/draw.py | ... | PASSOU |
| ... | RF02–RF14 | ... | ... | ... | PASSOU |
| F01 | 025 | Criar→Aplicar→Escolher/Cursor 3D | placement.py / ops_placement.py | tests/blender_025_place.py | PASSOU |
```

Sugestão de IDs: `C` para Construtor, `L` para Biblioteca, `F` para fluxo legado.

---

## 10. Ordem de execução recomendada

1. **Revisar o estado parcial** e decidir: continuar as duas edições ou revertê-las. Corrigir os defeitos da seção 5.2.
2. **Gerar os artefatos Reversa da 026** (`requirements.md`, `roadmap.md`, `actions.md`) a partir do mockup e dos
   dois pacotes. Só então atualizar `.reversa/active-requirements.json`.
3. **Construtor primeiro**, porque o fluxo 025 já está estável e o risco de regressão é conhecido:
   - tema/vista/laterais no preview e na sessão;
   - toolbar/titlebar/abas;
   - export JSON + cutlist;
   - medida + menu de contexto;
   - arraste;
   - contrato de chapas.
4. **Biblioteca depois**:
   - categorias do documento;
   - tema Light/Dark persistido;
   - grade 2×3/6 modelos;
   - conta/avatar;
   - alvos/estados vazios.
5. **Ensaios dirigidos** por item, depois bateria 025 + puros + i18n + `check_api`.
6. **i18n e versão**; CHANGELOG.
7. **Auditoria estrita**; corrigir achados de produto/código e refazer a prova. A auditoria não corrige artefatos.
8. **Commit local**; tag local se o padrão da 025 for mantido; **sem push**.

---

## 11. Regras do Reversa e da auditoria

- O skill `reversa-audit` é **estritamente leitor**: a única escrita permitida é
  `feature-dir/audit/cross-check.md`. Não altere `requirements.md`, `roadmap.md`, `actions.md`, `data-delta.md`,
  `interfaces/`, `investigation.md` nem `onboarding.md` durante a auditoria.
- A auditoria só pode terminar 0/0/0/0 se **nenhuma** função do mockup e **nenhum** RF da Biblioteca estiver
  listado como não implementado, pendente ou fora de escopo.
- Impossibilidade técnica no Blender é **bloqueio explícito** para o usuário; não é uma decisão de escopo e não
  pode ser escondida para “fechar” a matriz.
- Não prometa no cross-check que um skill fará a correção; indique a direção e devolva ao humano.
- Se o usuário pedir correção durante a auditoria, oriente `/reversa-clarify` ou edição manual, não edite os
  artefatos auditados.

### 11.1 Política de escrita no legado

`.reversa/reversa-config.json` está com:

```json
{
  "allowLegacyEdits": true,
  "allowedPaths": ["***", "caffmob_draw/*", "tests/*"]
}
```

Ou seja, a escrita em `caffmob_draw/` e `tests/` está liberada. Ainda assim, **não** altere `AGENTS.md` nem
`.reversa/reversa-config.json` por iniciativa própria.

---

## 12. Arquivos proibidos no commit

Não commitar:

- `AGENTS.md` (link simbólico problemático; “Function not implemented” ao tentar diff global);
- `biblioteca_detalhe.png`;
- `prompt_025.png`;
- `docs/Caff+Mob+Biblioteca+Mockup.tar.gz`;
- `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`;
- `.reversa/` (ignorado pelo git);
- `caffmob_draw.zip`, `.blend` de projeto e PDFs de treinamento.

`git diff` global pode falhar por causa do `AGENTS.md`; use `git diff -- <arquivo>` e `git status --short`.
Nunca use `git add .`.

---

## 13. Armadilhas conhecidas

1. **Screenshot não prova popup.** O Blender não captura popups/modais em `screen.screenshot`.
2. **`Window.width/height` readonly** no 5.2; não tente redimensionar a janela por eles.
3. **Tema nativo:** um add-on não repinta o chrome do Blender; só a área GPU própria. Se o requisito exigir o
   chrome inteiro, registre bloqueio.
4. **`CORES` do preview é estático** (ver 5.2). O tema não repinta peças até corrigir.
5. **`registrar_duplicata` incompleto** (ver 5.2). Não chame sem a propriedade e o `build.gerar`.
6. **`library_panel/draw.py:206` tem `E731` pré-existente** da feature 073; não foi corrigido e não é regressão da
   026. Não “conserte” de passagem sem necessidade.
7. **Categorias x ambientes:** `categories_core.FIXED` é navegação; `LINES` é ambiente do card. O documento muda a
   primeira, não necessariamente a segunda.
8. **Grade 2×3 x grade de texturas:** `test_library_grid` hoje exige ≥4 colunas. Separar modos ou atualizar a prova
   com justificativa do documento; não apenas afrouxar a asserção.
9. **`/tmp/library_ui.tsx` e `/tmp/library_app.tsx` são efêmeros.** Reextraia dos tar.gz.
10. **Não confie nesta memória.** O working tree pode ter mudado. Rode `git status` e `git diff` específicos.

---

## 14. Critérios de encerramento (checklist final)

- [ ] `requirements.md`, `roadmap.md`, `actions.md` da 026 existem e estão coerentes.
- [ ] Todas as ações marcadas `[X]`; nenhuma pendente.
- [ ] Matriz C01–C10 + L01–L14 + F01 sem linha pendente/bloqueada/fora de escopo.
- [ ] Cada item tem prova executada nesta rodada, com saída registrada.
- [ ] Fluxo 025 reexecutado sem regressão (16/16 e testes relacionados).
- [ ] Biblioteca segue os dois pacotes: categorias, 6 modelos/2×3, filtros, conta, tema, 44 px, estados.
- [ ] i18n sem chaves ausentes.
- [ ] `check_api.py` sem `[UNKNOWN in 5.2]`.
- [ ] Ruff nos arquivos tocados limpo (exceto o E731 pré-existente, se intocado).
- [ ] Versão/CHANGELOG atualizados.
- [ ] `audit/cross-check.md` com 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW e sem exclusão de função.
- [ ] Commit local; **sem push**.
- [ ] Nenhum arquivo da seção 12 commitado.

---

## 15. O que este handoff NÃO afirma

- Não afirma que a 026 está implementada.
- Não afirma que a paridade total foi alcançada.
- Não afirma que a Biblioteca já segue os pacotes.
- Não afirma que a auditoria 026 foi feita.
- Não afirma que as edições parciais de `window.py`/`preview.py` estão corretas.

O próximo agente deve verificar, implementar, executar, ler as falhas, corrigir e só então registrar o resultado.
