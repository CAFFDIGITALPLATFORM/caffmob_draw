# Cápsula de reprodução (lote 25)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_MTPU_standards.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_MTPU_standards.py (exit 1):
FALHA MTPU: falha inesperada na migração não sobe para o load_file_post RuntimeError('falha simulada')
OK   QO2H: a 1ª pergunta leva os que seguem ao padrão novo 
FALHA QO2H: a 2ª pergunta não reaplica os já aplicados na 1ª COZ
OK   QO2H: a 2ª pergunta aplica o módulo de padrão próprio 0.0250
FALHA ZATR: import com substituição mantém a ativa Depois ZATR
FALHA 64UD: projeto só com face frame recebe o padrão EUA Padrão Brasil
blender_bug_MTPU_standards: FALHAS: MTPU: falha inesperada na migração não sobe para o load_file_post, QO2H: a 2ª pergunta não reaplica os já aplicados na 1ª, ZATR: import com substituição mantém a ativa, 64UD: projeto só com face frame recebe o padrão EUA
```
