# Evidência, BUG-20261123-RW3G

Ambiente: Windows, `python` 3.13.7 (fora do Blender, o empacotador não precisa do Blender). Base: `3ca484f6`.

## 1. Vermelho (antes da correção)

`python build.py` (exit 0) e a listagem do zip, feita durante a conferência do BUG-20261123-56YQ:

```
arquivos: 2367 | 167.8 MB
entradas na raiz: ['.impeccable', 'LICENSE', 'LICENSES', '__init__.py', ...]
estranhos: 1 ['.impeccable/hook.cache.json']
```

Comando que reproduz:

```bash
python -c "import zipfile; print([n for n in zipfile.ZipFile('caffmob_draw.zip').namelist() if n.startswith('.') or '__pycache__' in n])"
```

Antes: `['.impeccable/hook.cache.json']`.

Pasta de trabalho com quatro `.impeccable/` (todas cache de ferramenta, nada lido pelo add-on):

```
caffmob_draw/.impeccable
caffmob_draw/product_libraries/closets/.impeccable
caffmob_draw/product_libraries/common/.impeccable
caffmob_draw/product_libraries/face_frame/.impeccable
```

## 2. Teste de reprodução

`tests/test_packaging.py::EmpacotamentoTest::test_entradas_excluidas_do_pacote`

Antes da correção, `build.entrada_excluida` não existia (o filtro estava embutido no `os.walk`), então o teste não importa. Depois:

```
test_entradas_excluidas_do_pacote ... ok
Ran 1 test in 0.005s
OK
```

## 3. Verde (depois da correção)

`python build.py` → `BUILD_STATUS=0`, *Successfully created 'caffmob_draw.zip'!*

```
arquivos: 2363 | 167.8 MB
entradas com ponto: []
pyc/pyo: []
manifesto raiz: True | __init__.py raiz: True
impeccable: []
wheels: 12
blends: 113
assets/slides: True
```

Diferença: 2367 → 2363 arquivos, exatamente os quatro `.impeccable/hook.cache.json`. Manifesto, `__init__.py`, wheels, `.blend` e o OBJ da corrediça continuam no pacote.

Regressão do pacote (teste que roda o `build.py` numa cópia temporária):

```
test_zip_tem_manifesto_na_raiz ... ok
Ran 1 test in 25.274s
OK
```

## 4. Fora de escopo, confirmado

- Tamanho do zip: 167,8 MB por causa dos 113 `.blend` que o add-on carrega. Não muda com esta correção e não é defeito.
- `tests/test_packaging.py::test_raiz_nao_e_extensao` continua vermelho por causa do manifesto em `novo_arm_building/`, falha anterior a este bug e ao 017.
