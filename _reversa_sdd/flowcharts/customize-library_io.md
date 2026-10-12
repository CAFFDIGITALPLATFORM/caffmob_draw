# Fluxograma: `library_io.save`, `library_io.load` e `common.set_removed` (customize)

Biblioteca de módulos do usuário (D-10, D-11, RF-07 a RF-10) e remoção de chapa por driver (006, D-07).

```mermaid
flowchart TD
    A[save context root name category thumbnail] --> B{adaptador da raiz?} -- não --> E0[O objeto não é um módulo]
    B -- sim --> C[paths_for: modules/categoria sanitizada/nome sanitizado .blend .png .json]
    C --> D[makedirs; build_manifest: adapter.read, world_box em mm, estilos, materiais, puxadores, agregados, btm_structure, divisões]
    D --> E[.blend temporário: libraries.write objetos + dados + materiais + imagens + node groups, RELATIVE_ALL, fake_user]
    E --> F[.json temporário: manifest.dumps]
    F --> G[os.replace dos dois para o destino]
    G -- OSError ou RuntimeError em qualquer passo --> H[remove temporários; erro Não foi possível gravar]
    G --> I{thumbnail?} -- sim --> J[library_common.thumbnail 256 px]
    I -- não --> K[paths, sem erros]
    J --> K
```

```mermaid
flowchart TD
    A[load context entry] --> B{has_manifest?}
    B -- sim --> C[manifest.loads] --> D{erros?} -- sim --> E[Manifesto inválido; nada inserido]
    B -- não --> F
    D -- não --> F[libraries.load link=False: todos os objetos]
    F --> G[liga à coleção da cena]
    G --> H[root = objeto sem pai com module_library]
    H --> I[refs de inputs NodeSocketObject dos GN: hide_set, hide_viewport, hide_render]
    I --> J{manifesto?} -- sim --> K[_missing_styles por biblioteca → aviso geral]
    J -- não --> L
    K --> L{root e manifesto?} -- sim --> M[reapply.reapply]
    L -- não --> N
    M --> N{root?} -- sim --> O[_renew_divisions: uids novos; reflow force]
    N -- não --> P[aviso Nenhum módulo encontrado]
    O --> Q[remove avisos por estilo dos adaptadores se houve aviso geral]
    P --> Q
    Q --> R[root, objetos, avisos únicos]
```

```mermaid
flowchart TD
    A[set_removed obj removed] --> B[obj btm_removed = removed]
    B --> C[Para hide_viewport e hide_render]
    C --> D{fcurve de driver existe?}
    D -- não --> E{removed?} -- não --> C
    E -- sim --> F[driver_add; expressão = btm_rm]
    D -- sim --> G
    F --> G{variável btm_rm no driver?}
    G -- não --> H[cria SINGLE_PROP → obj btm_removed; expressão = expr or btm_rm se não era só btm_rm]
    G -- sim --> I
    H --> I{não removed e expressão = btm_rm?} -- sim --> J[driver_remove: a biblioteca volta a mandar]
    I -- não --> C
    J --> C
    C -- fim --> K{não removed?} -- sim --> L[sem driver: hide_viewport/hide_render = False]
    K -- não --> M[update_tag]
    L --> M
```

Gravação atômica: os dois arquivos só aparecem no destino depois de completos; falha no meio não deixa parciais.
A remoção por driver soma-se ao esconder que a biblioteca já dirige, em vez de substituí-lo.
