# Cápsula de reprodução (lote 30)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_7SNG_openings.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_7SNG_openings.py (exit 1):
OK   7SNG: na face da frente o giro fica como escolhido []
FALHA 7SNG: na face de trás a porta abre para ela []
FALHA 7SNG: trocar o giro na face de trás mantém o espelho 
FALHA D3GC: o desenho não desliga a região 
OK   D3GC: a leitura dos operadores ainda desliga a região sem parede 
FALHA CHWX: janela BTM não pode ser redimensionada 
blender_bug_7SNG_openings: FALHAS: 7SNG: na face de trás a porta abre para ela, 7SNG: trocar o giro na face de trás mantém o espelho, D3GC: o desenho não desliga a região, CHWX: janela BTM não pode ser redimensionada
```
