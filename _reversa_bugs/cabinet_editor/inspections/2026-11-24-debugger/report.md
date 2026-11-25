# Inspeção /reversa-debugger — feature 021 (perguntas de interface com olhos frescos)

> Data: 2026-11-24
> Feature: `_reversa_forward/021-plano-corte-camadas-gaveteiro`
> Contexto: `cabinet_editor`
> Motivo: a auditoria anterior respondeu às perguntas de interface citando respostas antigas, sem verificação
> própria. Esta inspeção refaz cada uma com evidência executável.

## Como reproduzir

```bash
# Banco íntegro antes de tudo (o objeto do último commit tinha sido podado localmente):
git fetch origin master

# Sonda headless das três perguntas de interface
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python _reversa_bugs/cabinet_editor/inspections/2026-11-24-debugger/probe_editor_021.py

# Fumaças da 021 e da 022
blender --background --factory-startup --python-exit-code 1 --python tests/blender_021_mcp_e2e.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_022_mover_sobre_frente.py

# Suíte pura
cd tests && python -m unittest discover -s . -t . -p "test_*.py"
```

## Placar obtido nesta inspeção

| Evidência | Resultado |
|---|---|
| `probe_editor_021.py` | **22/22**, exit 0 |
| `tests/blender_021_mcp_e2e.py` | **50/50**, exit 0 |
| `tests/blender_022_mover_sobre_frente.py` | **10/10**, exit 0 |
| `tests/blender_017_armario_smoke.py` | **OK**, exit 0 |
| Suíte pura | **1581/1582**, 5 pulados; resta só a permissão POSIX |

## (a) O Editor de Armário abre e tem a cara/funções do mockup?

**Fato apurado:** existem dois operadores com o mesmo `bl_idname`:

- `caffmob_draw/cabinet_editor/ops_editor.py:313` — o editor 2D (`BTM_OT_CabinetEditor`);
- `caffmob_draw/armario_v2/ops.py:338` — o construtor v2 (`BTM_OT_ArmarioV2Abrir`).

Medido no Blender:

```
IDNAME_OWNER_LABEL: Abrir armário v2
editor_class_registered: False
v2_class_registered: True
```

Quem responde a `caffmob.cabinet_editor` é o **construtor v2**; a classe do editor 2D fica fora do registro. Isso
**não é regressão da 021**: é decisão da 017 (T027), documentada em `caffmob_draw/armario_v2/ops.py:16` e na guarda
`_dividido()` (`ops.py:645-649`), e coberta por `tests/blender_017_armario_smoke.py` e
`tests/blender_015_construtor_smoke.py`. O editor 2D está aposentado (`tests/retired/blender_006_cabinet_editor_tabs_smoke.py`).

Consequência para a pergunta do titular: o "Editor de Armário" que abre hoje é o **construtor v2 no painel
`View3D > CAFFMob Draw`**, não a janela 2D de vista frontal. As sete abas do v2 são exatamente as do mockup
(`caffmob_draw/armario_v2/panel.py:169-184`): Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos —
o mesmo conjunto de `data-tab` do `mockup_construtor_armarios.html`. O cabeçalho traz o título do mockup
(`tests/blender_021_mcp_e2e.py:474`, "Construtor de Armários") e a 021 acrescentou o acesso rápido ao Plano de Corte.

**O que não foi verificado:** paridade visual pixel a pixel com o mockup. O mockup é uma página clara
(`#f8fafc`, `#ffffff`, `#334155`, laranja `#ea580c`) e o painel do Blender é desenhado com os tokens do tema; sem
sessão gráfica não há captura comparável. Isso continua **aberto** e é o único item de interface que exige GUI.

Observação de código morto (não corrigida, fora do escopo): `caffmob_draw/cabinet_editor/window.py:43` ainda pinta o
fundo com `#10302F`, o verde escuro legado que a RN-09 mandou eliminar. Como o editor 2D está fora do registro, esse
caminho não é alcançável hoje; fica registrado para quando alguém reativar o editor.

## (b) O botão geral de colisão do viewport está corrigido?

Sim, com evidência de comportamento e de desenho:

- operador alterna e não levanta: `colisão: desliga sem erro {'FINISHED'}`, `colisão: religa sem erro`;
- `block_penetration` acompanha o estado global;
- `draw_header_collision` desenha com um layout de teste sem exceção, aponta para
  `caffmob.toggle_global_collision`, usa o rótulo do estado atual ("Colisão: ON") e o ícone/depress corretos;
- os quatro rótulos traduzem em pt_BR sem chave faltante;
- `tests/blender_021_mcp_e2e.py` confirma o efeito na API real ("colisão: alterna OFF").

O que não foi verificado: o botão desenhado de fato no cabeçalho da janela 3D (exige GUI).

## (c) Criar do zero, redimensionar sem deformar e editar peça a peça

| Pergunta | Evidência | Veredito |
|---|---|---|
| Criar do zero, rápido | `Abrir` do v2 num projeto limpo cria a raiz em um passo (`{'FINISHED'}`, raiz "Armário v2") | **Sim** |
| Camada correta | raiz nasce em `Marcenaria` | **Sim** (RF-07) |
| Redimensionar | largura 1000 → 1200 mm, **5 peças antes e 5 depois**, nenhuma peça achatada (rect com largura/altura zero) | **Sim** |
| Editar todas as peças | estrutura (espessura da lateral), divisória, prateleira e bloco de gavetas rodam sem exceção e as peças crescem de 5 para 33 | **Sim** |
| As sete abas | `panel.ABAS` = ESTRUTURA, DIVISOES, GAVETAS, INTERNOS, PORTAS, DESLIZANTES, FUNDOS | **Sim** |

Caminho negativo verificado de propósito: `caffmob.library_create_cabinet` num cenário com um móvel legado ativo cai
no diálogo antigo e cria um `BTM_Cabinet` (construção antiga), que o construtor v2 recusa com a mensagem própria. É o
comportamento documentado da RN-23, não um defeito novo.

## As duas falhas restantes da suíte Blender são ambiente?

Reproduzidas nesta máquina, sem o MOBI de ensaio:

```
tests/blender_065_ida_e_volta.py:34
    assert urlsplit(BASE).scheme == 'http' and urlsplit(BASE).hostname == '127.0.0.1', 'Somente o MOBI de ensaio em 127.0.0.1'
AssertionError: Somente o MOBI de ensaio em 127.0.0.1

tests/blender_ensaio_mobi.py:19
    assert urlsplit(base).hostname == '127.0.0.1' and urlsplit(base).scheme == 'http', base
AssertionError
```

Ambas abortam **antes** de registrar o addon e exigem, além do host, `--online-mode`, `T121_PREPARO` e
`BLENDER_USER_RESOURCES`. São dependências de ambiente (MOBI descartável em 127.0.0.1), **não defeitos de produto**.
`tests/blender_065_ida_e_volta.py` ainda pede o arquivo de preparo gerado pela web (`t121-preparo.mts`), que não existe
nesta máquina.

## Defeitos reais encontrados nesta inspeção (e corrigidos)

1. **Três ensaios de SHA256SUMS ordenavam por `Path`.** No Windows a comparação de `PurePath` é insensível a
   maiúsculas, então `parede-L.json` vinha depois de `parede-aberturas-arco.json` e 16 linhas divergiam do arquivo
   gravado em ordem ordinal. Corrigido com `key=lambda p: p.name` em `test_contrato_v2.py`, `test_obra_v2.py` e
   `test_paredes_edicao_v2.py`. Nenhuma asserção foi afrouxada.
2. **`test_subprocesso_transporta_formulario_headers_e_etag` usava `select` num pipe.** No Windows `select` só
   aceita soquetes (`OSError: [WinError 10038]`). Corrigido com uma thread leitora com timeout de 5 s; as asserções
   de status, ETag, `If-Match` e corpo do formulário seguem idênticas.

Nenhum arquivo de produto foi alterado nesta inspeção.

## Limitações honestas

- Sem GUI: paridade visual com o mockup, aparência do botão no cabeçalho e os ensaios de janela
  (`blender_004_cabinet_editor_smoke.py`, `blender_012_convert_undo.py`, `blender_012_library_ui.py`) não rodaram.
- `test_sessao_mobi.test_permissao_e_endereco` continua vermelho **por plataforma**: o NTFS não tem permissão POSIX e
  `os.stat().st_mode` devolve `0o666` qualquer que seja o `chmod`. A asserção está correta para POSIX e não foi
  alterada.
- A suíte Blender completa (204 arquivos) não foi reexecutada nesta rodada; foram rodados os ensaios afetados pela
  021/022 e a fumaça de registro da 017.
