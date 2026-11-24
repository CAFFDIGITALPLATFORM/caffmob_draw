# Contrato de Interface: Sincronização de Texturas Perdidas (HTTP)

> Feature: `021-plano-corte-camadas-gaveteiro`
> Tipo: HTTP (cliente assíncrono em `caffmob_draw/texture_library/downloads.py`)
> Referência: RF-03, RN-03, RNF de Confiabilidade e Rede

## 1. Propósito

Detectar imagens/texturas pertencentes ao catálogo do CAFFMob Draw referenciadas nos materiais da cena atual cujo arquivo local no cache/disco esteja ausente ou corrompido (0 bytes / ilegível) e re-baixá-las pelo endpoint de texturas já utilizado por `texture_library/downloads.py`, reconectando `bpy.data.images` automaticamente.

## 2. Request

- **Método e caminho:** reaproveita o cliente autenticado existente em `texture_library/downloads.py` (`GET /api/draw/v1/texturas/<texture_id>` e URL de arquivo da entrada do catálogo).
- **Filtro de disparo:** somente texturas com ID/metadado do catálogo do addon cujo caminho local não exista ou esteja corrompido. Texturas íntegras no disco nunca são re-baixadas.
- **Autenticação:** token/sessão gerenciado por `texture_library/auth.py` (mesmo fluxo já existente).

## 3. Response e Reconciliação

- **200 OK:** stream de imagem gravado em arquivo temporário (`<destino>.part`) no mesmo diretório do cache e promovido via `os.replace()` (escrita atômica). Após promoção, recarrega `image.filepath` + `image.reload()` na thread principal via timer do Blender.
- **401 / 403:** interrompe o lote, informa ao usuário para reconectar a conta no painel de Texturas/Materiais.
- **404 Not Found:** marca a textura específica como indisponível no catálogo, não tenta novamente e segue com as demais do lote.
- **5xx / Erro de rede / Timeout:** aplica até **2 retentativas** com backoff curto (1 s, 2 s) antes de registrar falha para aquela textura e prosseguir com o lote.

## 4. Limites, Timeout, Concorrência e Idempotência

- **Timeout por arquivo:** máximo **15 segundos**.
- **Cancelamento:** o usuário pode cancelar a sincronização em andamento; downloads pendentes são cancelados e nenhum `.part` permanece órfão.
- **Idempotência:** acionar "Sincronizar Texturas Perdidas" com todas as texturas íntegras não efetua nenhuma chamada HTTP e informa `"Todas as texturas do addon já estão presentes localmente."`.
- **Relatório final:** sempre exibe resumo objetivo na UI (`X sincronizada(s), Y com falha, Z já presente(s)`).
