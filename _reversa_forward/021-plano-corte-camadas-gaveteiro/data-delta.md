# Data Delta: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Referência no legado: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/architecture.md#Persistência e unidades` e `_reversa_sdd/addenda/017-construtor-armario-v2.md`

## 1. Novas propriedades em `Scene` (`caffmob_draw/data/properties.py` e `cutting/`)

| PropertyGroup / Alvo | Campo | Tipo | Padrão | Descrição |
|----------------------|-------|------|--------|-----------|
| `Scene.btm_settings` | `floor_thickness` | `FloatProperty` (`DISTANCE`, min `0.005`, max `1.0`) | `0.15` (150 mm) | Espessura padrão do piso gerado pelo addon |
| `Scene.btm_settings` | `floor_thickness_direction` | `EnumProperty` (`'DOWN'`, `'UP'`) | `'DOWN'` | Direção de extrusão do piso: `'DOWN'` (topo em Z=0, cresce para −Z) ou `'UP'` (base em Z=0, cresce para +Z) |
| `Scene.btm_settings` | `default_wall_thickness` | `FloatProperty` (`DISTANCE`, min `0.01`, max `2.0`) | `0.15` (150 mm) | Espessura padrão de parede definida rapidamente na aba Ferramentas e lida pelo Editor de Parede |
| `Scene.btm_settings` | `cutting_engine` | `EnumProperty` (`'OPCUT'`, `'LEGACY_SHELF'`) | `'OPCUT'` | Motor de otimização do plano de corte (padrão OpCut offline) |
| `Scene.btm_settings` | `cutting_group_by_module` | `BoolProperty` | `True` | Exibe/exporta lista de peças agrupada hierarquicamente por módulo |
| `Scene.btm_settings` | `cutting_preview_sheet_index` | `IntProperty` (min `0`) | `0` | Índice da chapa atualmente exibida no visualizador interno do Blender |

> Nota: `Scene.home_builder.ceiling_height` (pé-direito padrão, 0,50–10,00 m) e `Scene.btm_settings.collision_global` (booleano global de colisão) **já existem** e são reutilizados diretamente sem duplicação.

## 2. Novas propriedades em `Object`

| PropertyGroup / Custom Prop | Campo | Tipo | Padrão | Descrição |
|-----------------------------|-------|------|--------|-----------|
| `Object.btm_stick` (`stick/props.py`) | `released_host_name` | `StringProperty` | `""` | Nome do último hospedeiro do qual o objeto foi desgrudado manualmente, usado para suprimir reacoplamento imediato pelo ímã |
| `Object` (custom prop) | `btm_armario_v2_root` | `bool` | `True` (apenas na raiz v2) | Identificador explícito da raiz de armário v2, desacoplado do nome da coleção (`Marcenaria`) |
| `Object` (custom prop) | `btm_is_lowered_wall` | `bool` | `True` (apenas no proxy) | Marca o proxy visual de 150 mm como representante de parede rebaixada |
| `Object` (custom prop) | `btm_lowered_wall_ref` | `str` | `""` | Nome do objeto da parede original vinculada ao proxy rebaixado |
| `Object` (custom prop) | `btm_floor_thickness` | `float` | `0.15` | Espessura aplicada ao piso para atualização/reconstrução consistente |
| `Object` (custom prop) | `btm_floor_direction` | `str` | `'DOWN'` | Direção (`'DOWN'` ou `'UP'`) aplicada ao piso |
| `Object` (custom prop) | `btm_gaveteiro_meta` | `str` (JSON) | `""` | Metadados do gaveteiro convertido: papéis mapeados (`laterais`, `contrafrente`, `traseira`, `fundo`, `frente`), lista de `pecas_faltantes`, `completado_auto` e `ferragens` (`corredica_tipo`, `puxador_tipo`, `fita_borda`, `fixadores`) |

## 3. Alterações na estrutura de coleções (camadas de cena)

```text
Scene Collection
├── Arquitetura
│   ├── Parede      (paredes e proxies de parede rebaixada)
│   ├── Piso        (pisos manuais e automáticos)
│   ├── Teto        (tetos e sancas)
│   └── Aberturas   (portas, janelas e vãos arquiteturais)
└── Marcenaria      (armários v2, armários de biblioteca, gaveteiros convertidos)
```

## 4. Campos removidos ou alterados

- **Nenhum campo removido.** Todas as propriedades novas possuem valores padrão seguros e retrocompatíveis.
- **Alteração semântica em `armario_v2/build.py:e_raiz()`:** passa a priorizar `obj.get('btm_armario_v2_root')` mantendo fallback para coleções legadas (`Armário v2`), garantindo abertura sem quebra de arquivos `.blend` anteriores.
