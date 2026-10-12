# Cápsula de reprodução (lote 1: exclusão de parede)

- Commit base: 83a6863 (master, com mudanças locais da feature 013 em walls2d, fora deste caminho)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`, hash fbe6228777e7), `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python evidence/probe_lote1.py`
- Exit code: 0 · Taxa: 1/1 · Classificação: deterministic

## Saída

```
=== #12 filhos não grudados (sem agregados): Delete nativo ou do plugin
poll plugin: False {'FINISHED'}
Geo antes (4.3, 0.5, 0.0) depois (4.3, 0.5, 0.0)
porta ainda existe: True
=== #12/#13 com módulo e agregado, with_aggregates=False
poll plugin: True {'FINISHED'}
Geo salto: 1.811 Balcao salto: 2.236
Fruteira continua agregado: False pai: None
=== #14 com módulo e agregado, with_aggregates=True
poll plugin: True {'FINISHED'} Fruteira existe: True agregado: True
```

## Leitura

- Parede sem agregados: o `poll` do plugin é falso e o Delete nativo roda; a geometria filha fica no lugar,
  mas a caixa da porta fica solta na cena, sem parede (pergunta 5: deveria sair com a parede, `KEEP_WITH_WALL`).
- Parede com balcão + agregado: o plugin assume; geometria e balcão saltam (1,811 m e 2,236 m), porque
  `bpy.data.batch_remove` tira o pai sem preservar a matriz de mundo dos filhos.
- "Apagar também os agregados" desligado: a Fruteira do balcão que ficou deixa de ser agregado (EC-07/EC-16).
- Ligado: a pergunta aparece e nada além da parede é apagado (EC-16).
