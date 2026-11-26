# Regression watch: 025-criacao-posicionamento-armario

> Identificador: `025-criacao-posicionamento-armario`
> Gerado em 2026-11-26 pelo fechamento da feature.

## Itens de vigilância

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `requirements.md`, RN-01 | Criar armário abre a Vista 3D sem criar janela nova | presença + ensaio `blender_025_place` | `len(window_manager.windows)` aumenta ao chamar `caffmob.cabinet_editor` |
| W002 | `requirements.md`, RN-02 | Todo Aplicar (painel e janela 023) chama `abrir_prompt` uma vez | presença + ensaio com gancho | Aplicar grava snapshot e não pergunta; ou pergunta duas vezes |
| W003 | `requirements.md`, RN-03 | A caixa tem 8 vértices, 12 arestas, 0 faces, `WIRE`, medidas do spec | ensaio puro + Blender | Caixa com faces, material, medidas erradas ou armário real visível |
| W004 | `requirements.md`, RN-04 | Setas cardeais mapeiam 0/90/180/270 e R soma 90 | teste puro + ensaio com `RIGHT_ARROW` | Giro em eixo errado, sinal invertido ou evento não tratado |
| W005 | `requirements.md`, RN-05 | Clique confirma e remove a caixa; Esc/botão direito restauram loc/rot/hide | ensaio de janela | Caixa órfã, armário oculto ou posição não restaurada |
| W006 | `requirements.md`, RN-06 | Cursor 3D move só a raiz; peças filhas acompanham | ensaio de janela | Peça filha para trás ou raiz com pai |
| W007 | `requirements.md`, RN-07 | Sem viewport, Escolher cai no Cursor 3D e retorna `FINISHED` | teste puro/`EXEC_DEFAULT` | Exceção, `CANCELLED` inesperado ou posição não aplicada |
| W008 | `requirements.md`, RN-08 | Galeria usa os tokens Light do mockup e mantém abas/busca/grade/seleção/filtros | teste puro + card 38/38 + UI 9/9 | Token antigo, texto ilegível, controle sumido |
| W009 | `requirements.md`, RN-09 | A paridade integral do mockup continua na 023 (D-05), sem regressão da 023 | cross-check 023 + smoke 017 | A 025 declarar paridade total ou remover escopo da 023 |
| W010 | `roadmap.md`, D-03 | O popup é agendado e aberto com janela/área/região da Vista 3D; não prende o Aplicar | ensaio + inspeção do código | Popup morto, Aplicar travado ou `temp_override` sem janela |

## Histórico de re-extrações

(vazio — preenchido quando rodar `/reversa` de novo)

## Observações

- O print do Blender (`screen.screenshot`) não captura popups; o ensaio prova que o operador retorna `RUNNING_MODAL` e
  que o gancho é chamado. O desenho do popup fica na verificação humana da §5 do onboarding.
- A suíte pura tem uma falha ambiente-gated conhecida no NTFS (`test_sessao_mobi`, permissão POSIX); não tem relação
  com a 025.
