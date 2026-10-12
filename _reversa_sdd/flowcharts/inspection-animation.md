# Tween e saída do modo de inspeção

🟢 **CONFIRMADO** — inspection/ops_inspect.py:142–251. Extração: 2026-10-10.

```mermaid
flowchart TD
 A[Invoke sem sessão] --> B[Timer 60 Hz e registro no HUD]
 B --> C[Clique numa frente]
 C --> D{Tween existente?}
 D -->|Sim| E[Inverter alvo a partir da pose corrente]
 D -->|Não| F[Alternar estado aberto ou fechado]
 E --> G[TIMER: smoothstep por 0.35 s]
 F --> G
 G --> H{Terminou?}
 H -->|Não| I[Apply sem commit]
 I --> G
 H -->|Sim| J[Commit alvo e remover tween]
 K[Esc, direito, cancel ou segunda invocação] --> L[Commit alvos pendentes; limpar timers, HUD e status]
```

Esc sai do modo, mas não desfaz abertura. Unregister não chama _finish da sessão ativa.
