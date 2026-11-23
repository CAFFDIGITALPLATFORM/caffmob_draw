---
schema_version: 1
id: BUG-20261123-56YQ
display_number: 154
title: "Arrastar o zip para o Blender 5.2 falha no lock do repositório (cookie da pasta temporária ausente)"
status: open
phase: triaging
severity: high
priority: P1
created: 2026-11-23
updated: 2026-11-23

origin:
  type: manual-report
  external_ref: null

area: plugin
module: hb_core
feature: unclassified
labels: ["instalacao", "ambiente", "blender-upstream", "especulacao-de-causa"]

change_risk:
  classification: baixa
  reasons: ["a falha está no instalador do Blender, não no pacote", "o zip precisa apenas ser conferido contra o manifesto e os wheels", "a correção provável é orientação de ambiente, não código do add-on"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: ["pasta temporária do Blender (bpy.app.tempdir) removida ou inválida", "limpeza do %TEMP% durante a sessão", "pasta temporária em unidade removível ou rede"]

blocking: []

relationships:
  - bug: BUG-20261006-SCVF
    type: related-to
    state: proposed
    evidence: []
  - bug: BUG-20261123-RW3G
    type: related-to
    state: confirmed
    evidence:
      - ref: evidence/reproduction.md
        observation: "o vazamento de .impeccable no zip foi achado nesta conferência e virou bug próprio, já corrigido"

traceability:
  specs: ["_reversa_sdd/deployment.md"]
  affected_code: []
  root_cause:
    state: likely
    hypothesis: "O instalador de extensões trava os repositórios com RepoLock, que usa `bpy.app.tempdir` como cookie. Quando essa pasta não existe, `acquire()` levanta `Exception: acquire(): cookie doesn't exist! (when it should)` antes de abrir o pacote. A falha é do Blender (deveria recriar a pasta), não do zip do caffmob_draw."
    causal_path:
      - "arrastar o zip: bl_extension_ops.py, execute (linha 1504) chama exec_command_iter"
      - "exec_command_iter (linha 2627) chama repo_lock.acquire() com cookie = cookie_from_session()"
      - "bl_pkg/__init__.py:103 devolve bpy.app.tempdir como cookie"
      - "bl_extension_utils.py:2244 testa os.path.exists(cookie) e a linha 2245 levanta a exceção"
    evidence:
      - ref: evidence/reproduction.md
        observation: "traceback do Blender 5.2 com as linhas 1504, 2627 e 2245 idênticas à tag v5.2.0"
      - ref: evidence/erro-instalar-cookie-lock-20261123.webp
        observation: "print do relatório de erro enviado pelo usuário"
    code_refs: []
  reproduction_tests: []
  regression_tests: []

spec_verdict: spec-gap

change_set: []
closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---

# Arrastar o zip para o Blender 5.2 falha no lock do repositório (cookie da pasta temporária ausente)

## Summary

Arrastar `caffmob_draw.zip` para a janela do Blender 5.2 no Windows termina em `Exception: acquire(): cookie doesn't exist! (when it should)`, levantada em `bl_extension_utils.py:2245`. A exceção acontece no instalador de extensões, antes de o zip ser lido, então nada indica defeito no pacote: o próprio Blender não consegue criar o lock do repositório porque a pasta temporária da sessão (`bpy.app.tempdir`) não existe naquele momento.

## Expected Behavior

Arrastar o zip instala a extensão, ou o Blender recusa com uma mensagem legível. O chunk esperado é o do fluxo "Install from Disk", que não deveria depender de uma pasta temporária pré-existente para travar os repositórios.

Spec efetiva: `_reversa_sdd/deployment.md`. O caso "instalador do Blender falha por ambiente" nunca foi especificado (`spec-gap`); a pergunta "é bug nosso ou do ambiente?" fica aberta para o fix, com a evidência já apontando para o ambiente.

## Actual Behavior

```
Exception: acquire(): cookie doesn't exist! (when it should)
```

`bl_pkg/__init__.py:103` devolve `bpy.app.tempdir` como cookie do `RepoLock`, e `RepoLock.acquire()` (`bl_extension_utils.py:2244`) levanta quando esse caminho não existe. A instalação para no primeiro passo e o relatório de erro não mostra nenhuma outra exceção.

## Steps to Reproduce

1. No repositório, `python build.py` gera `caffmob_draw.zip` (167,8 MB, 2367 arquivos, manifesto e `__init__.py` na raiz do zip).
2. Arrastar o zip sobre a janela do Blender 5.2 no Windows.
3. O relatório de erro abre com o traceback de `bl_extension_ops.py` / `bl_extension_utils.py`.

Roteiro e fonte conferida em `evidence/reproduction.md`.

## Evidence

- `evidence/erro-instalar-cookie-lock-20261123.webp`: print do relatório de erro.
- `evidence/reproduction.md`: traceback literal, linhas conferidas contra a tag `v5.2.0` do Blender e ocorrências iguais em outros add-ons.
- Relato: `../../intake/relato-20261123-1104.md`, item 1.

## Suspected Area

- Instalador de extensões do Blender (`scripts/addons_core/bl_pkg/`), não o `caffmob_draw`.
- Ambiente do titular: pasta temporária do Blender (`Preferences, File Paths, Temporary Files`).
- Verificação pendente do pacote: zip íntegro e wheels compatíveis com Python 3.13 (conferidos apenas por leitura do manifesto neste turno).

## Acceptance Criteria

- A instalação do zip conclui num Blender 5.2 limpo, com a pasta temporária existente, sem exceção no relatório de erro.
- Um teste ou roteiro reproduzível registra o estado da pasta temporária e o resultado da instalação, para separar falha de ambiente de falha de pacote.
- Se a causa for só do Blender, o registro fica como orientação de ambiente (workaround documentado) e não como mudança de código do add-on.

## Traceability

- Specs: `_reversa_sdd/deployment.md`
- Código afetado: nenhum arquivo do pacote até aqui (a exceção nasce em `bl_pkg`, do Blender)
- Causa raiz: não confirmada (fica com o `/reversa-debugger-fix`)
- Relações propostas: `related-to` BUG-20261006-SCVF (mesma área, instalação)

## Agent Notes

- Severidade `high` e prioridade `P1` propostas pelo agente: bloqueia a instalação por completo, embora a causa provável esteja no ambiente e não no pacote.
- `module: hb_core` reaproveitado do BUG-20261006-SCVF, que também trata instalação. O `taxonomy.yaml` não tem termo para empacotamento/instalação; proposta de novo termo (`packaging`) registrada aqui, sem inventar valor fora do catálogo.
- `spec-gap` porque nenhuma spec descreve o que fazer quando o instalador do Blender falha por ambiente.
- Achado lateral que NÃO é este bug: `.impeccable/hook.cache.json` entrou no zip, porque `build.py` só exclui `__pycache__` e o `catalog/` da raiz. **Registrado e corrigido em BUG-20261123-RW3G** (`build.py` passou a excluir dotfiles, dot-dirs e caches; zip de 2367 para 2363 arquivos, integridade conferida).
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix`.
