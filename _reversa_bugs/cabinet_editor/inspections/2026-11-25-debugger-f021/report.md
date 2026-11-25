# Inspeção `/reversa-debugger` — feature 021 (2026-11-25)

> Feature: `_reversa_forward/021-plano-corte-camadas-gaveteiro`
> Motivo: a auditoria anterior respondeu às perguntas de interface por memória, sem executar. Esta rodada virou cada
> pergunta em comando executado: ou passa, ou vira defeito com arquivo/linha e comando que falha.
> Harness novo: `tests/blender_021_ciclo_debug.py` (**12/12**, exit 0).

```
blender --background --factory-startup --python-exit-code 1 --python tests/blender_021_ciclo_debug.py
{"pass": 12, "fail": 0, "failures": []}
```

## (a) O editor de armário abre e é igual ao mockup?

**Provado sem GUI**

- O item de botão direito/toque longo é emitido pelo hook do armário v2:
  `caffmob_draw/armario_v2/menu.py` `desenhar_menu` → `layout.operator("caffmob.armario_v2_window_open",
  text=tr("Abrir janela do construtor"), icon='WINDOW')`.
  Ensaio: `tests/blender_023_fase7.py` →
  `OK menu de contexto abre a janela do construtor ['caffmob.armario_v2_window_open']` (**36/36**).
- O operador existe e está registrado: `caffmob.armario_v2_window_open`
  (`caffmob_draw/armario_v2/ops_window.py:73`), e a sessão/ciclo da janela é testada em
  `tests/blender_023_janela_open.py` (**OK**): sessão nasce vazia, `iniciar_sessao` cria e `encerrar_sessao` limpa.
- As sete abas existem e têm painel registrado (`panel_window.ABAS`, 11 classes `BTM_PT_ArmarioV2Window*`
  registradas): `OK editor: as sete abas têm painel registrado 11`.

**Só uma sessão gráfica prova**

- Que a área duplicada aparece na tela: no `--background` o `poll` recusa por contexto —
  reproduzido de propósito, `RuntimeError: Operator bpy.ops.caffmob.armario_v2_window_open.poll() failed, context is
  incorrect`. Não é defeito: sem janela, `area_dupli` não tem o que duplicar.
- Aparência igual ao `mockup_construtor_armarios.html` (paleta, espaçamento, ícones, tipografia, posição das abas):
  **não afirmada**. É exatamente a T033, que segue aberta.
- Gesto real de botão direito e de pressão longa em tela sensível, desenho efetivo dos painéis, rolagem, modal e
  redimensionamento da janela. Nada disso é pixel nem evento provável em headless.

## (b) O botão geral de colisão do viewport ainda dá erro?

**Corrigido e provado em execução** (`tests/blender_021_ciclo_debug.py`):

```
OK colisão: operador do cabeçalho executa sem erro None
OK colisão: desliga as duas chaves (False, False)
OK colisão: religa as duas chaves (True, True)
OK colisão: cabeçalho emite o botão com o estado [('caffmob.toggle_global_collision', 'Colisão: ON')]
```

Cobertura: `caffmob_draw/ui/header_collision.py` (`caffmob.toggle_global_collision`, `draw_header_collision` em
`VIEW3D_HT_header`), alternando `collision_global` e `block_penetration`; o desenho foi exercitado com layout falso.
O que só a GUI vê: o botão pintado no cabeçalho e o clique real.

## (c) Criar do zero, redimensionar e editar todas as peças?

**Criar do zero** — `OK armário do zero: montar caixa cria as cinco chapas 5`, `OK armário do zero: Gerar repete o
resultado 5` (`bpy.ops.caffmob.armario_v2_montar_caixa` + `caffmob.armario_v2_gerar`).

**Redimensionar sem perder/deformar** —

```
OK redimensionar: mesmo número de peças (5, 5)
OK redimensionar: largura acompanha o módulo 0.8999999761581421   # 900 mm em metros
OK redimensionar: nenhuma peça degenerada []
```

Além disso, `tests/blender_066_resize_rules.py` → `PASSOU: regras dimensionais 066` (folha preserva abertura, fecha na
nova largura, sem deriva, vão externo 579,4 → 799,4 mm, vão negativo bloqueia sem mutação).

**Editar todas as peças pelo editor** — `OK editar cada peça: o lote move e devolve todas []`: para cada peça do
armário gerado, seleção pelo editor + `aplicar_lote` (`MOVER_DIR` 10 mm e volta) sem sobra. O lote grava `ajustes` e o
Gerar reaplica (`tests/blender_023_fase7.py`, 36/36). O que só a GUI vê: editar pelo campo de cada aba e ver o
resultado na tela.

## Falhas restantes das suítes — todas reproduzidas, todas ambiente-gated

| Comando | Falha reproduzida | Por que é ambiente, não produto |
|---|---|---|
| `blender ... --python tests/blender_065_ida_e_volta.py` | `tests/blender_065_ida_e_volta.py:34: AssertionError: Somente o MOBI de ensaio em 127.0.0.1` | O ensaio só aceita o servidor MOBI de ensaio em loopback (`T121_PREPARO`); não há MOBI servido nesta máquina. |
| `blender ... --python tests/blender_ensaio_mobi.py` | `tests/blender_ensaio_mobi.py:19: AssertionError` (mesma guarda de `CAFFMOB_BASE` em 127.0.0.1, seguida de `assert bpy.app.online_access`) | Exige `CAFFMOB_BASE` apontando para o MOBI de ensaio e o Blender iniciado com `--online-mode`. |
| `cd tests && python -m unittest test_sessao_mobi.Sessao.test_permissao_e_endereco` | `tests/test_sessao_mobi.py:19: AssertionError: 438 != 384` | `os.stat().st_mode & 0o777` = 438 (`0o666`) no NTFS/Windows; o ensaio exige `0o600`. Semântica POSIX não existe aqui. |

Nenhuma delas exercita código de produto: as duas primeiras param na guarda de endereço antes de qualquer chamada, e a
terceira mede permissão de arquivo do sistema operacional.

## Veredito

- Nenhum defeito de produto novo encontrado neste ciclo; o código da 021 **não precisou de correção**.
- Pendências reais: **T033/A004** (paridade visual e gestos, só em GUI) e a lacuna de **material/UV/preferências**, que
  não é da 021 e virou a candidata `024-materiais-uv-preferencias`.
- Placar desta rodada: harness novo 12/12; `blender_023_fase7` 36/36; `blender_021_mcp_e2e` 52/52;
  `blender_017` OK; `blender_022_mover_sobre_frente` 10/10; `blender_066` OK; `blender_067` OK; sonda de menu OK;
  suíte pura 1600 ensaios com apenas a falha de permissão acima.
