# Cápsula de reprodução (lote 28)

- Commit base: c989c10 (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`)
- Sonda: inserir o item embutido "Cooktop 4 bocas" por `item_io.insert`, salvar o projeto, reabrir; depois inserir de
  novo e remover os objetos (caminho do Esc)
- Taxa: 1/1 · Classificação: deterministic (não reproduz o defeito relatado)

```
PROBE item Cooktop 4 bocas 3 2 2 [('Queimadores', 1, False), ('Mesa de vidro', 1, False)]
PROBE after reload objs 3 meshes 2 mats 2
PROBE after cancel orphans [('Mesa de vidro.001', 0), ('Queimadores.001', 0)]
```

Leitura: o que foi inserido (3 objetos, 2 malhas, 2 materiais) continua no arquivo depois de salvar e recarregar; as
malhas chegam sem fake user mas com 1 usuário (o objeto). Só os dados de uma inserção cancelada ficam órfãos (0
usuários) e somem ao recarregar, que é a limpeza esperada (EC-07).
