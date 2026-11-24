# Regression Watch: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Origem: `_reversa_forward/021-plano-corte-camadas-gaveteiro/legacy-impact.md`

## Regras sob vigilância

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `_reversa_sdd/domain.md#2.3` | Plano de corte padrão utiliza `opcut_core.py` (guilhotinado 2D offline), agrupa lista por módulo sem ferragens e exporta HTML/SVG/PDF | `presença` | Plano de corte voltar a usar apenas `nesting.py` ou misturar ferragens na lista de chapas |
| W002 | `_reversa_sdd/domain.md#collision` (`RN-COLLISION-08`) | `VIEW3D_HT_header` expõe botão global de colisão sincronizado com `collision_global` e `block_penetration`, removido no `unregister` | `presença` | Ausência do botão no header da Viewport 3D ou handler órfão após desregistro |
| W003 | `_reversa_sdd/domain.md#stick` (`RN-STICK-10`, `RN-STICK-12`) | Desgrudar armário grava `released_host_name` (e `opt_out` para parede) impedindo reacoplamento infinito pelo ímã ao mover para frente | `redação` | `magnet.find()` voltar a grudar no hospedeiro recém-desgrudado dentro da zona de histerese |
| W004 | `_reversa_sdd/domain.md#selection` (`RN-SELECTION-01`) | Proxy de parede rebaixada (`btm_is_lowered_wall` / `<parede>_Rebaixada`) é classificado como `WALL` e exibe "Restaurar Parede" no menu de contexto | `presença` | Parede rebaixada voltar a ser classificada como `OTHER` sem opção de restauração |
| W005 | `_reversa_sdd/domain.md#walls2d` (`RN-WALLS2D-16`) | Elementos arquiteturais vão para `Arquitetura > Parede\|Piso\|Teto\|Aberturas` e piso suporta espessura `DOWN` (−Z) e `UP` (+Z) | `redação` | Piso/teto/aberturas criados fora de `Arquitetura` ou sem opção de direção de espessura |
| W006 | `_reversa_sdd/addenda/017-construtor-armario-v2.md` | Armários v2 e gaveteiros convertidos nascem na coleção `Marcenaria` e `e_raiz()` usa `btm_armario_v2_root` com fallback para `CAFFMob Armário v2` | `redação` | `e_raiz()` voltar a depender exclusivamente do nome `CAFFMob Armário v2` ou criar armários fora de `Marcenaria` |
| W007 | `_reversa_sdd/code-analysis.md#17. Módulo library_panel` | "Criar Armário" abre diretamente o Construtor v2 e `library_panel/style.py` não contém a paleta verde escura legada (`#10302F`, `#0B2322`) | `ausência` | Retorno do desvio para `structure_gallery` ou reintrodução dos tokens verde-escuros em `style.py` |

## Observações

- Conversão em Gaveteiro (`armario_v2/drawer_detect_core.py` e `ops_drawer_convert.py`): nunca deve bloquear a criação quando faltarem peças, perguntando ao usuário se deseja completá-las e abrindo o editor ao final.
- Sincronização de texturas perdidas (`texture_library/sync_missing.py` e `ops_sync_missing.py`): mantém timeout de 15 s, até 2 retentativas e escrita atômica.

## Histórico de re-extrações

> Vazio — será preenchido automaticamente quando `/reversa` for executado novamente.

## Arquivadas

> Nenhuma regra arquivada.
