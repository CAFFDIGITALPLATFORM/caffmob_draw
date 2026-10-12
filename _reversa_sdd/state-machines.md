# Máquinas de Estado do Sistema — BlenderToMob

Este documento apresenta a especificação detalhada das máquinas de estado dos operadores modais e comportamentos dinâmicos do add-on **BlenderToMob**, conduzido pelo agente **Detective** no nível de documentação **Detalhado**.

---

## 1. Construtor de Parede Modal (`BTM_OT_WallBuilder`)

Esta máquina de estado gerencia a captura de coordenadas do cursor, buffer de entrada numérica via teclado e confirmação de segmentos polilinhas para geração geométrica final.

### 1.1 Diagrama de Estados (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> Inativo
    
    Inativo --> AguardandoPrimeiroClick : Invoke (chamar operador)
    AguardandoPrimeiroClick --> Inativo : ESC ou RMB (Cancelar)
    
    AguardandoPrimeiroClick --> DesenhandoSegmento : Mouse Click (Z=0)
    note right of DesenhandoSegmento
        Marca vértice inicial da polilinha
    end note
    
    state DesenhandoSegmento {
        [*] --> EditandoMouse
        
        EditandoMouse --> DigitandoValor : Qualquer dígito numérico (0-9, ., -)
        note right of DigitandoValor
            buffer de string 'typed_value' ativo
        end note
        
        DigitandoValor --> DigitandoValor : Digitar mais caracteres
        DigitandoValor --> EditandoMouse : Backspace (apaga último caractere)
        
        DigitandoValor --> EditandoMouse : ENTER (Aplica valor digitado no campo ativo)
        
        EditandoMouse --> EditandoMouse : MOUSEMOVE (Atualiza preview de comprimento/ângulo)
        EditandoMouse --> EditandoMouse : TAB (Alterna campo ativo: Length, Angle, Thickness, Height)
        
        DigitandoValor --> EditandoMouse : TAB (Commit temporário e muda campo ativo)
    }
    
    DesenhandoSegmento --> DesenhandoSegmento : Mouse Click ou ENTER (sem digitação)
    note right of DesenhandoSegmento
        _confirm_segment(): Grava segmento em JSON local
        Reseta comprimento do mouse e move origem
    end note
    
    DesenhandoSegmento --> Finalizado : Click próximo ao ponto de partida (fecha loop)
    DesenhandoSegmento --> Finalizado : RMB (Finaliza polilinha aberta)
    DesenhandoSegmento --> Inativo : ESC (Cancela e descarta todos os segmentos)
    
    Finalizado --> Inativo : _finish(): Limpa draw handler e reconstrói malhas
```

---

## 2. Inserção de Aberturas interativa (`BTM_OT_InsertOpening`)

Esta máquina de estado controla o arrasto de portas e janelas nas paredes da cena, aplicando lógica de snapping 2D e peitoril vertical.

### 2.1 Diagrama de Estados (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> Inativo
    
    Inativo --> ConfigurandoVao : Invoke (Janela de propriedades iniciais)
    ConfigurandoVao --> Inativo : Fechar caixa de diálogo
    ConfigurandoVao --> DeslizandoAbertura : Confirmar diálogo (OK)
    
    state DeslizandoAbertura {
        [*] --> TravadoNoSegmento
        
        TravadoNoSegmento --> TravadoNoSegmento : MOUSEMOVE (Busca parede mais próxima e snappa)
        TravadoNoSegmento --> TransicaoDeParede : MOUSEMOVE (Distância até parede adjacente é menor)
        TransicaoDeParede --> TravadoNoSegmento : Adota nova rotação, normal e espessura
        
        TravadoNoSegmento --> EditandoDimensoes : Qualquer dígito numérico
        EditandoDimensoes --> EditandoDimensoes : Digitar caracteres adicionais
        EditandoDimensoes --> TravadoNoSegmento : ENTER (Aplica cota de afastamento ou peitoril)
        
        TravadoNoSegmento --> TravadoNoSegmento : TAB (Alterna entre cota de Afastamento e Peitoril)
    }
    
    DeslizandoAbertura --> Inativo : ESC ou RMB (Cancela e remove preview_obj)
    DeslizandoAbertura --> Aplicado : Mouse Click ou ENTER (Confirma inserção)
    
    Aplicado --> Inativo : _confirm_insertion(): Cria cortador real, aplica Boolean e finaliza
```


## Re-extração 2026-10-10 — estados atuais

Os diagramas anteriores descrevem operadores da base antiga. Os estados abaixo são abstrações documentais dos campos e eventos atuais, não novos enums persistidos. 🟢 Transições extraídas do código; runtime Blender não executado nesta análise.

### Editor de paredes

Fonte: `caffmob_draw/walls2d/ops_editor.py; props.py`.

```mermaid
stateDiagram-v2
    [*] --> Rascunho
    Rascunho --> Desenhando : escolher lápis e ponto inicial
    Desenhando --> Desenhando : confirmar segmento
    Desenhando --> PerguntaFechar : chegar ao início
    PerguntaFechar --> Rascunho : aceitar fechamento
    PerguntaFechar --> Desenhando : recusar fechamento
    Rascunho --> Rascunho : editar, undo e redo locais
    Rascunho --> ZoomJanela : ativar lupa
    ZoomJanela --> Rascunho : retângulo ou Esc
    Rascunho --> Aplicado : OK com validação
    Rascunho --> Descartado : Cancelar ou fechar janela
    Aplicado --> [*]
    Descartado --> [*]
```

Zoom/pan não registram passo de undo nem reaplicam o snap. Esc tem significado contextual: zoom, buffer, desenho ou encerramento, conforme estado.

### Editor de armário

Fonte: `caffmob_draw/cabinet_editor/ops_editor.py; state.py`.

```mermaid
stateDiagram-v2
    [*] --> Editando
    Editando --> PedidoPendente : UI enfileira ação
    PedidoPendente --> Editando : modal executa e recalcula
    Editando --> Editando : undo e redo do rascunho
    Editando --> Bloqueado : mensagem ERROR
    Bloqueado --> Editando : corrigir erro
    Editando --> Aplicado : Aplicar
    Aplicado --> Editando : novo snapshot de retorno
    Editando --> Confirmado : OK
    Editando --> Restaurado : Cancelar ou fechar janela
    Confirmado --> [*]
    Restaurado --> [*]
```

Cancelamento restaura o último ponto Aplicar, ou o inicial se nunca aplicou. WARNING não bloqueia; ERROR bloqueia Aplicar/OK.

### Inspeção de frentes

Fonte: `caffmob_draw/inspection/ops_inspect.py`.

```mermaid
stateDiagram-v2
    [*] --> Inativa
    Inativa --> Ativa : invoke
    Ativa --> Animando : clicar frente
    Animando --> Animando : inverter alvo durante tween
    Animando --> Ativa : duração concluída e commit
    Ativa --> Encerrada : Esc, saída ou nova invocação
    Animando --> Encerrada : saída com commit do alvo
    Encerrada --> [*]
```

60 Hz, duração 0,35 s e smoothstep. Esc finaliza no alvo; não retorna automaticamente ao estado inicial. Unregister não percorre explicitamente os timers da sessão.

### Proteção de frentes ao salvar

Fonte: `caffmob_draw/inspection/save_guard.py`.

```mermaid
stateDiagram-v2
    [*] --> EstadoAtual
    EstadoAtual --> Snapshot : save_pre sem opt-out
    Snapshot --> Fechadas : deduplicar keys e fechar
    Fechadas --> Redescobertas : save_post ou save_post_fail
    Redescobertas --> EstadoAtual : restaurar valores por key
    EstadoAtual --> EstadoAtual : save_pre com opt-out
```

Snapshot efêmero por cena/key. Frente removida não é restaurada; animação e commit pendente podem interferir com o ciclo.

### Colisão de corpo

Fonte: `caffmob_draw/collision/ops_collision.py; stale.py`.

```mermaid
stateDiagram-v2
    [*] --> SemResultado
    SemResultado --> Atual : verificar
    Atual --> Desatualizado : depsgraph altera objeto verificado
    Desatualizado --> Atual : verificar novamente
    Atual --> SemResultado : limpar resultados
    Desatualizado --> SemResultado : limpar resultados
    SemResultado --> Avulso : check_moved antes de qualquer verificar
    Avulso --> Atual : verificar
    Desatualizado --> Atual : check_moved esvazia _changed (rechecked)
    SemResultado --> Erro : verificar com exceção
    Atual --> Erro : verificar com exceção
    Erro --> Atual : verificar com sucesso
    Erro --> SemResultado : limpar resultados
```

_(Revisão cruzada 2026-10-10: estados Avulso e Erro e a volta por `check_moved` acrescentados; collision/design.md › Máquina de Estados do Resultado, scan.py:check_all/check_moved, stale.py:rechecked)_ Avulso = `checked < 0` com linhas (collision EC-04): nunca fica desatualizado. Erro = `error != ""`; `check_moved` bem-sucedido não sai dele (collision EC-10).

A flag stale não reexecuta automaticamente a análise. A interferência de abertura em inspection usa outro armazenamento e não herda automaticamente esse contrato.

### Geometria livre

Fonte: `caffmob_draw/geometry_free/ops_create.py`.

```mermaid
stateDiagram-v2
    [*] --> Origem
    Origem --> Dimensoes : primeiro clique
    Dimensoes --> Dimensoes : mouse, largura ou profundidade digitada (2º Enter avança ou conclui)
    Dimensoes --> Altura : confirmar base da caixa
    Dimensoes --> Confirmada : confirmar placa
    Altura --> Confirmada : clicar ou digitar altura
    Origem --> Removida : Esc ou botão direito
    Dimensoes --> Removida : Esc ou botão direito
    Altura --> Removida : Esc ou botão direito
    Confirmada --> [*]
    Removida --> [*]
```

Objeto existe desde invoke. Dígitos digitados antes do primeiro clique ficam no buffer e valem no passo seguinte (geometry_free EC-05) _(Revisão cruzada 2026-10-10: geometry_free/design.md › Divergências; ops_create.py)_. Cancelamento externo não tem método cancel explícito; transição nessa condição é lacuna.

### Biblioteca lateral

Fonte: `caffmob_draw/library_panel/ops_click.py; draw.py`.

```mermaid
stateDiagram-v2
    [*] --> Fechada
    Fechada --> Aberta : clicar rótulo BIBLIOTECA CAFFMOB (invalida o cache de categorias)
    Aberta --> Fechada : clicar rótulo de novo (alterna)
    Aberta --> Fechada : Esc ou clique fora (o clique segue para a seleção)
    Aberta --> Acao : clicar qualquer item (fecha antes de agir)
    Acao --> Popover : categoria (popover de módulos)
    Acao --> Operador : criar armário, criar categoria ou converter grupos
    Popover --> [*]
    Operador --> [*]
```

_(Revisão cruzada 2026-10-10: library_panel/ops_click.py:dispatch — `LABEL` alterna `state.open`; qualquer outro item faz `state.open = False` antes de agir; painel desenhado no topo da viewport, não na lateral; library_panel/design.md (a))_

Painel POST_PIXEL não usa modal permanente. Estado aberto global, não isolado por janela.

### Inserção de objeto da biblioteca

Fonte: `caffmob_draw/object_library/ops.py`.

```mermaid
stateDiagram-v2
    [*] --> Carregado
    Carregado --> Posicionando : iniciar modal
    Posicionando --> Posicionando : mouse no plano horizontal do cursor
    Posicionando --> Confirmado : clique
    Posicionando --> Removido : Esc ou botão direito
    Confirmado --> [*]
    Removido --> [*]
```

Cancel externo limpa somente cabeçalho no código observado; não inferir remoção do grupo nesse caminho.

### Vínculo do grudar

Fonte: `caffmob_draw/stick/apply.py; link.py; settle.py` (tabela completa em `_reversa_sdd/stick/design.md` › Máquina de Estados do Vínculo). _(Revisão cruzada 2026-10-10: máquina ausente deste documento; acrescentada a partir de stick/design.md)_

```mermaid
stateDiagram-v2
    [*] --> Solto
    Solto --> Grudado : grudar, ímã ao soltar ou módulo filho de parede (migração)
    Grudado --> ForaDaFace : hospedeiro encolhe (aviso só na entrada)
    ForaDaFace --> Grudado : pegada volta ao retângulo (sem aviso)
    Grudado --> Solto : Desgrudar
    Grudado --> Quebrado : hospedeiro apagado fora do operador
    Quebrado --> Solto : próximo handler com índice válido (lose_link)
    Grudado --> Orfao : pai trocado fora do plugin
    Orfao --> Solto : só Desgrudar
```

Órfão não tem saída automática e a colisão continua usando `btm_stick.host` como ligado (stick EC-02; collision `_links`). `btm_stick` é salvo no `.blend`.
