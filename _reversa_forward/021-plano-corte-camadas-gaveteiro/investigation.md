# Investigation: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Roadmap: `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md`

## 1. Pesquisa de fundo no legado e referências

### 1.1 Otimização de corte OpCut (`https://github.com/bozokopic/opcut`)
- **Referência externa:** OpCut (licença GPL-3.0, compatível com a licença `SPDX:GPL-3.0-or-later` do CAFFMob Draw em `_reversa_sdd/dependencies.md`).
- **Modelo algorítmico do OpCut:** O OpCut modela o problema de corte guilhotinado 2D usando cortes ortogonais completos (`cut_width` = kerf) sobre painéis retangulares (`Panel(width, height)`), produzindo árvores de corte (`Used` + `Unused` gerados por corte horizontal ou vertical). Seus métodos clássicos são `greedy` e `forward_greedy` (lookahead de um passo para escolher o corte/peça que minimiza fragmentação de sobra), respeitando `can_rotate` (controlado pelo sentido do veio: `NONE` permite rotação 90°, `VERTICAL`/`HORIZONTAL` bloqueia).
- **Situação atual no legado:** `caffmob_draw/cutting/nesting.py` implementa apenas Next-Fit Decreasing em prateleiras horizontais (`R-09`, `R-10` em `_reversa_sdd/domain.md#2.3`). O modelo de peça `NestingPart` já carrega `module_ref`, `module_uid`, `thickness`, `material`, `grain_direction`, `edges` e `component`, facilitando tanto o agrupamento por módulo quanto a entrada direta para o motor OpCut.
- **Alternativas avaliadas:**
  1. **Portar o núcleo algorítmico do OpCut em Python puro (`opcut_core.py`)** — escolhida: 100% offline, zero dependências externas, licença GPL-3.0 compatível, fácil de testar unitariamente fora do Blender.
  2. **Integrar via CLI/HTTP local do OpCut** — descartada: viola o requisito 1a (offline e embutido no addon) e complica empacotamento multiplataforma.

### 1.2 Ciclo infinito ao desgrudar armário (`caffmob_draw/stick/`)
- **Causa raiz confirmada no código:**
  - `caffmob_draw/stick/link.py:143-162` (`release(item)`): só marca `opt_out = True` quando `st.orig_parent` é uma parede (`if parent is not None and (parent.get('IS_WALL_BP') or classify.classify(parent).kind == classify.WALL)`).
  - Quando o armário foi grudado via ímã (`magnet.try_stick`), `orig_parent` era `None`. Logo, ao clicar em "Desgrudar", `opt_out` permanece `False`.
  - Quando o usuário move o armário para frente (ex.: 20–45 mm, ainda dentro da tolerância padrão de 50 mm do ímã em `RN-STICK-12`), `stick/settle.py:run()` dispara após 0,2 s, vê `opt_out == False`, executa `_stick_guarded(obj)` → `magnet.try_stick(obj)` e **puxa o armário de volta para a parede**, reiniciando o ciclo infinito.
- **Solução cirúrgica:** gravar `released_host_name` no `btm_stick` ao executar `release()` (e marcar `opt_out = True` sempre que o hospedeiro atual `st.host` for parede, ou manter guarda por `released_host_name` até o item sair da zona de captura + margem de histerese de 100 mm).

### 1.3 "Criar Armário" e paleta verde escura da Biblioteca (`caffmob_draw/library_panel/`)
- **Causa raiz confirmada:**
  - `caffmob_draw/library_panel/ops_cabinet.py:44-48` intercepta `caffmob.library_create_cabinet` e chama `bpy.ops.caffmob.structure_gallery('INVOKE_DEFAULT', environment=line)` em vez de abrir o Construtor v2 (`armario_v2`).
  - `caffmob_draw/library_panel/style.py:17-20` define cores verde-petróleo/verde-escuro (`#10302F`, `#16403E`, `#1F5250`, `#0B2322`) herdadas da feature 014.
- **Alinhamento:** rotear "Criar Armário" diretamente para o Construtor v2, atualizar `style.py` para a paleta neutra/escura + laranja oficial CAFFMob (alinhada ao tema atual do addon e ao Construtor v2) e assegurar que armários inseridos pela biblioteca sejam instâncias compatíveis com `armario_v2` (ou convertidos transparentemente pelo adaptador `armario_v2/ponte.py`).

### 1.4 Parede rebaixada irreconhecível (`operators/ops_wall_extras.py` + `selection/classify.py`)
- **Causa raiz confirmada:**
  - `ops_wall_extras.py:lower_wall` cria um proxy `<parede>_Rebaixada` (150 mm de altura) e esconde a parede real (`obj.hide_viewport = True`, `obj[LOWERED_PROP] = True`).
  - Ao clicar no proxy na viewport, `selection/classify.py:classify()` não reconhece o proxy como parede (ele não tem `IS_WALL_BP` nem `caffmob_tipo == 'parede'`), caindo em `OTHER` — impedindo que a barra lateral e o menu de contexto exibam "Restaurar Parede".
- **Solução:** marcar o proxy com `btm_lowered_wall_ref` (nome da parede original) + `btm_is_lowered_wall = True`, reconhecê-lo em `selection/classify.py` apontando para a parede original (ou tipo reconhecido com flag `is_lowered`) e expor o botão "Restaurar Parede" (`caffmob.wall_lower` / `caffmob.wall_restore`) no painel contextual e no menu de contexto.

### 1.5 Camadas de cena (`Arquitetura` e `Marcenaria`) e espessura do piso
- **Situação atual:**
  - `walls2d/layers.py` cria apenas `Arquitetura > Parede`.
  - Pisos (`floor_builder.py`, `operators/walls.py`, `walls2d/apply.py`), tetos (`IS_CEILING_BP`) e aberturas não são garantidamente vinculados às subcoleções `Arquitetura > Piso`, `Arquitetura > Teto` e `Arquitetura > Aberturas`.
  - `armario_v2/build.py:340-344` usa `any(colecao.name == COLECAO for colecao in obj.users_collection)` para identificar a raiz do armário — acoplamento que precisa ser substituído por flag explícita `btm_armario_v2_root` ao mover armários para `Marcenaria`.

### 1.6 Anatomia de gaveteiro para conversão geométrica (`drawer_detect_core.py`)
- **Regras geométricas para detecção automática (malha única ou objetos separados):**
  - Em uma malha única, particionar por componentes conexos (ilha de faces/vértices via BFS/DFS em `bmesh` ou núcleo puro sobre lista de faces/boxes) gera as subpeças candidatas.
  - Cada subpeça tem sua caixa orientada/AABB (`dx`, `dy`, `dz` e centroide relativo ao volume total da gaveta):
    - **Frente da gaveta:** placa perpendicular ao eixo frontal (`Y` mínimo), normalmente mais larga/alta que a caixa interna (espessura típica 15–18 mm).
    - **Fundo:** placa horizontal (`dz` mínimo, espessura típica ~6 mm) na porção inferior (`Z` mínimo).
    - **Laterais (2 peças):** placas verticais delgadas em `X` (`dx` mínimo, espessura típica ~15 mm) nas extremidades `X` mínimo (esquerda) e `X` máximo (direita).
    - **Contrafrente:** placa vertical delgada em `Y` localizada logo atrás da frente (entre as laterais).
    - **Traseira / Contrafundo:** placa vertical delgada em `Y` localizada na extremidade `Y` máximo (entre as laterais).
  - Peças ausentes nunca bloqueiam: o analisador retorna `(encontradas, faltantes)` e a UI pergunta se o usuário quer gerar automaticamente as faltantes antes de abrir o editor.

## 2. Padrões aplicáveis

- **Separação núcleo puro / casca Blender:** toda lógica de cálculo (OpCut, agrupamento por módulo, exportação SVG/HTML/PDF, detecção geométrica de gavetas, regras de supressão do ímã) fica sem importação de `bpy` para rodar em `pytest`/`unittest` em milissegundos.
- **Escrita atômica:** tanto o re-download de texturas quanto as exportações HTML/SVG/PDF gravam em arquivo temporário no mesmo diretório e usam `os.replace()`.
- **Ciclo de vida seguro:** registro no `VIEW3D_HT_header` e submenus de contexto têm par exato de remoção no `unregister()`.
