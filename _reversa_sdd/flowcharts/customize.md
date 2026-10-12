# Fluxograma: módulo `customize`

Personalização por instância e biblioteca de módulos do usuário (feature 003, bloco A; 006 e 008 estendem).

```mermaid
flowchart TD
    subgraph Entradas
        OPS[caffmob.customize_set_front / set_style / set_pull / set_material / set_interior / clear]
        SAVE[caffmob.module_save]
        INS[caffmob.module_insert]
        HOOK[Bibliotecas: after_rebuild context obj no fim de recálculos]
    end
    OPS --> RES[adapters.for_object ativo → raiz, adaptador; vão pelo caminho estável]
    RES --> STRUCT{mudança estrutural?}
    STRUCT -- frente / interior --> LIB[adapter.set_front / set_interior pela própria biblioteca; o operador não grava btm_custom antes]
    STRUCT -- estilo / puxador / material --> WRITE[grava o pedido em btm_custom do vão, peça ou raiz]
    WRITE --> RE
    LIB --> RE[reapply.reapply: adapter.reapply relê btm_custom e reaplica estilo, puxador, materiais]
    HOOK --> HC{after_rebuild: has_custom raiz?}
    HC -- não --> OUT0[sai sem custo]
    HC -- sim --> RE2H[reapply.reapply]
    RE2H --> HS{has_structure? só em after_rebuild}
    HS -- sim --> REAF[reaffirm remoções e espessuras; set_back_recess; reflow de divisões, extras, interiores, corrediças]
    SAVE --> BM[library_io.build_manifest: adapter.read + caixa + estilos + materiais + puxadores + estrutura + divisões]
    BM --> WR[libraries.write .blend temporário + .json; os.replace; miniatura 256 px]
    INS --> LD[library_io.load: valida manifesto; libraries.load; liga à cena; oculta refs de GN; estilos ausentes → aviso]
    LD --> RE2[reapply.reapply + divisões com uids novos] --> PL[PlacementMixin: snap, R gira, Esc cancela]
    subgraph Saídas
        PAN[painel Personalizar módulo: por vão + grupos de material + Salvar]
        LIBP[painel Biblioteca de módulos: inserir, renomear, apagar, abrir pasta]
        REP[report: mensagens dos adaptadores ou sucesso]
    end
```

Núcleos puros: `spec.py` (o que mudou na instância, validação, serialização) e `manifest.py` (contrato
`caffmob_draw.user-module` 1.1.0). Um adaptador por biblioteca (`frameless`, `face_frame`, `closets`, `btm`) traduz
o `Spec` para os mecanismos de cada uma; `common.py` concentra materiais, drivers de remoção e espaços internos.

_(Revisão cruzada 2026-10-10: ops_customize.py:92-99 chama `adapter.set_front` sem gravar `btm_custom` antes (só os operadores de estilo, puxador e material gravam); `reapply.reapply` (reapply.py:46-55) não testa `has_structure` — o reafirmar/reflow fica em `after_rebuild` (reapply.py:58-80))_
