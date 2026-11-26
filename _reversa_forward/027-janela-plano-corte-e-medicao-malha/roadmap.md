# Roadmap: Janela do plano de corte, medição de malha e controle de arestas

> Identificador: `027-janela-plano-corte-e-medicao-malha`
> Data: `2026-11-26`
> Requirements: `_reversa_forward/027-janela-plano-corte-e-medicao-malha/requirements.md`

## 1. Estratégia

Quatro frentes independentes, ordenadas por risco crescente. RF-05 saiu primeiro porque era defeito e já está
provado. RF-03 e RF-04 são pequenas e destravam percepção de qualidade. RF-01 substitui um caminho existente e
precisa de cuidado com o legado. RF-02 é uma janela nova de porte grande: só entra depois que o padrão de janela
própria do add-on (o da 023/025) estiver reutilizável.

## 2. Fases

| Fase | Conteúdo | Depende de | Saída |
|------|----------|------------|-------|
| 1 | RF-05 coleção de câmeras | - | ✅ provado nesta rodada |
| 2 | RF-03 arestas (linha 0,2 px ajustável, “só textura”) | - | preferência + caminho de desenho |
| 3 | RF-04 aplicar em todos os selecionados | - | preferência + `get/set` multi-objeto + confirmação |
| 4 | RF-01 janela do plano de corte | 3 | janela própria; sistema antigo desligado do caminho de entrada |
| 5 | RF-02 V-Ray Mesh Measure, núcleo | 4 | janela com partes soltas, camadas, medidas e câmera orbital |
| 6 | RF-02, representações e snap | 5 | Aramado, Linhas Ocultas, Sólido, Raio-X, Material; snap |
| 7 | RF-02, medição manual e unidades | 6 | arraste entre extremidades; absoluta/arredondada em cm/mm/m |
| 8 | RF-02, impressão e views | 7 | folhas, badge por view, tamanho/proporção |
| 9 | Provas, regressão, i18n, auditoria | 2–8 | matriz fechada e cross-check |

## 3. Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| RF-02 virar uma janela que não fecha e não libera handlers | Alto | um `unregister`/saída única; teste de fumaça que conta handlers antes e depois |
| Custo de quadro em malha densa | Médio | decimar a malha só na cópia de exibição; nunca no objeto do usuário |
| RF-01 quebrar o export/cutlist da 026 | Alto | manter `parity_core` como fonte e só trocar a janela de apresentação |
| RF-04 aplicar valor divergente por engano | Alto | confirmação explícita + passo de desfazer próprio |
| Sem GPU nesta máquina de trabalho | Médio | provas de lógica em `--background`; o que exige janela fica registrado como não verificado |

## 4. Fora do caminho crítico

- Tema Light/Dark das janelas novas (herda o padrão da 026).
- Atalhos de teclado (só depois que as janelas existirem).
