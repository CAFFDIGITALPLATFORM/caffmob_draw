# Cápsula de reprodução: BUG-20261014-RWU2

- **Commit base:** `1c9ea2d` (master)
- **Ambiente:** Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`), janela por `xvfb-run`
- **Comando:**
  `xvfb-run -a /opt/blender/blender --factory-startup --enable-event-simulate --python evidence/repro_rwu2.py`
- **O que faz:** abre a BIBLIOTECA CAFFMOB maximizada na aba Blocos, categoria Cozinha, captura a área da vista 3D e
  compara pixel a pixel (tolerância 0,02) o quadrado da miniatura dos cinco modelos prontos.
- **Resultado:** `REPRO pares_iguais 10 de 10` (todas as miniaturas idênticas), exit 0
- **Taxa:** 3/3 execuções
- **Classificação:** determinístico
