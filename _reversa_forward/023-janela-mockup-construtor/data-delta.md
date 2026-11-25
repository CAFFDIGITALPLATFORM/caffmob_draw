# Data Delta: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Requirements: `_reversa_forward/023-janela-mockup-construtor/requirements.md`

## Resumo

Nenhuma mudança de modelo de dados é necessária. A janela própria do Construtor edita o **armário v2** existente (`armario_v2`, `Object.btm_armario`) e o contrato de chapas (`Scene.btm_armario_contrato`), já gravados pelo addendo vigente `017-construtor-armario-v2.md`. A feature apenas adiciona uma nova camada de interface (janela Image Editor própria) sobre os mesmos dados.

## Novos campos

Nenhum. Os campos de interface do armário v2 (`contra_frente_ativa`, `peca_tras_ativa`, campos de inserção, `vao_ativo`, etc.) já existem conforme o adendo 017.

## Campos removidos

Nenhum.

## Migrações necessárias

Nenhuma. Não há alteração de esquema de dados, portanto não há migração de `.blend` nem de propriedades customizadas.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md` | Limites e organização | componente-extenso | Nova janela própria (Image Editor) espelhando o construtor v2; não altera componentes existentes |
| `_reversa_sdd/domain.md` | cabinet_editor | contrato-reutilizado | Reaproveita a máquina de estado fila + modal UNDO (EditorState, OK/Aplicar/Cancelar) |
