# Cápsula de reprodução — BUG-20261117-744U

## Ambiente

- Windows, Blender 5.2.0 LTS (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`), `py -3`.
- Extensão instalada: `%APPDATA%\Blender Foundation\Blender\5.2\extensions\mobi_caff_digital\caffmob_draw`
  (sincronizada do repositório nesta correção).
- Base: working tree do repositório `BlenderToMob` (nada commitado nesta linha de trabalho; o HEAD não tem o
  change set).

## Defeito relatado

O editor de paredes não tem ação de imprimir a planta baixa: nem botão, nem operador, nem PDF.

## Como foi reproduzido (antes do change set)

1. Leitura do código: `caffmob_draw/walls2d/ops_editor.py`, `panels.py` e `classico_v2.py` não têm operador de
   impressão; o painel Confirmar só tem OK e Cancelar.
2. Sondagem MCP (`../../intake/sondagem-mcp-20261117.md`): nenhum operador `caffmob.*` imprime ou exporta a planta do
   editor. `caffmob_layouts.export_all_to_pdf` (`caffmob_draw/operators/layouts.py:804`) renderiza câmeras de layout
   view, não a planta do editor.
3. Teste de reprodução, vermelho antes do operador:

```text
$ cd tests && py -3 -m unittest test_impressao -v
test_modulo_de_impressao_existe ... FAIL   (módulo impressao ausente)
test_operador_de_impressao_existe ... FAIL
AssertionError: 'caffmob.wall_editor_print' not found in '...'
FAILED (failures=2)
```

Classificação: `deterministic`, taxa 2/2. Não é intermitente.

## Prova depois do change set

```text
$ cd tests && py -3 -m unittest test_impressao test_i18n_coverage
Ran 16 tests ... OK

$ py -3 docs/rag/tools/check_api.py
Scanned 580 files against 24382 Blender 5.2 symbols.
OK: no unknown API references found.

$ blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_744U_imprimir.py
OK   REPRODUÇÃO: sem planta o operador recusa e não escreve arquivo {'CANCELLED'} arquivo=False
OK   REGRESSÃO: o operador grava o PDF da planta {'FINISHED'} bytes=1822
OK   REGRESSÃO: PDF de uma página A4 com a escala no rodapé
OK   REGRESSÃO: as quatro paredes e as quatro medidas entraram medidas=4
OK   REGRESSÃO: imprimir não altera o rascunho dirty=False request=None
OK   REGRESSÃO: objeto abaixo do corte entra como hachura clara {'FINISHED'}
OK   REGRESSÃO: os objetos acrescentam geometria ao PDF com=2069 sem=1822
EXIT=0
```

## Cena real do titular (Blender aberto via MCP, add-on instalado)

```text
ARQUIVO G:\.shortcut-targets-by-id\...\ELEDÊ MAGALHAES - PROJETOS.blend
OBJETOS 2272
OBJETOS_NA_PLANTA 1625  TRACOS 2666  ESCALA 75
TEMPO leitura=13.21s pdf=0.24s total=13.45s
PDF 2295479 bytes  C:\Users\RYZEN\AppData\Local\Temp\blender_a21380\planta_744U_instalada.pdf
OPERADOR_REGISTRADO True
```

O custo de 13,2 s é a leitura da cena por `scene_io.plant_objects` (2.272 objetos), função entregue no
BUG-20261117-JXDJ; a geração do PDF custa 0,24 s.

## O que não foi verificado

- O PDF da cena real não foi aberto para inspeção visual: a conferência foi de estrutura (cabeçalho, uma página A4,
  comandos de traço/preenchimento, penas e escala) e dos testes no Blender. Falta o titular olhar a prancha impressa.
- A cena aberta no Blender não tinha documento v2 (`caffmob_ambiente`), então o caminho v2 foi provado com o caso-ouro
  em `tests/test_impressao.py#V2Test`, não na cena real.
