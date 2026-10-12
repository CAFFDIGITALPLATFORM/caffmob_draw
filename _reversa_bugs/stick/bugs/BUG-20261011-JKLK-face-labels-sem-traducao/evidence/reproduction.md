# Cápsula de reprodução (lote 17: traduções)

- Commit base: 83a6863 + lotes 1 a 16 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`, interface em en_US no teste
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_35HE_i18n.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
OK   35HE: aviso do Salvar como módulo em inglês (tradução do Blender) Error: Type a name for the module
FALHA JKLK: rótulos das faces em inglês Direita (+X)
FALHA DLHX: nomes das chapas têm tradução ['Trás']
FALHA FGTR: sem vão interno não vira falta de profundidade ['Os trilhos precisam de mais profundidade (sem vão interno)']
FALHA FGTR: profundidade na unidade da cena ['Os trilhos precisam de mais profundidade (profundidade 0.090)']
```

O primeiro OK é a evidência do #31 (35HE): com o código antigo, o aviso já sai em inglês, porque o Blender traduz o
texto do report pelo catálogo (a entrada já existia em `customize.json`).
