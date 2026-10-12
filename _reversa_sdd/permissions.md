# Matriz de Acesso e Permissões do Sistema — BlenderToMob

Este documento mapeia o controle de acesso de execução e permissões do add-on **BlenderToMob**, conduzido pelo agente **Detective** no nível de documentação **Detalhado**.

---

## 1. Contexto de Segurança e Execução

O **BlenderToMob** opera como uma extensão embutida dentro do processo principal do Blender 3D. Portanto, ele herda as permissões do usuário que executa o processo do Blender no sistema operacional. No entanto, do ponto de vista da arquitetura de add-ons do Blender, existem restrições de escopo e limites de acesso à API que governam o comportamento dos componentes.

---

## 2. Matriz de Acesso a API e Recursos

| Componente | Acesso à API (`bpy.data`) | Manipulação do Grid / GPU | Escrita no File System | Alteração de Malhas (`bmesh`) | Descrição do Escopo |
|------------|:-------------------------:|:-------------------------:|:----------------------:|:-----------------------------:|---------------------|
| **data** | Leitura/Escrita | - | - | - | Registra e remove tipos de dados e custom properties globais. |
| **geometry** | Leitura/Escrita | - | - | Leitura/Escrita | Gera malhas poligonais de forma imperativa limpando e adicionando vértices/faces. |
| **operators** | Leitura/Escrita | Leitura | - | Leitura/Escrita | Modais interceptam mouse/teclado do sistema e alteram transformações espaciais. |
| **overlays** | Leitura | Leitura/Escrita | - | - | Registra handlers na viewport para desenho gráfico imediato via OpenGL/Vulkan. |
| **ui** | Leitura | - | - | - | Apresenta propriedades na interface gráfica e executa polling ativo de contexto. |
| **cutting** | - | - | Leitura/Escrita | - | Lógica pura Python sem dependência de APIs Blender. Otimiza planos de corte de chapas. |

---

## 3. Classificação de Confiança de Modificações de Malha (Mesh Mutability)

Para evitar vazamentos de memória e corrupção de malhas no Blender (uma vez que operações em background na API `bmesh` sem liberação de dados podem travar a aplicação):

* **Mutação de Geometria de Parede (R-11)**: Apenas permitida via chamadas síncronas em update callbacks ou durante a finalização do operador modal.
* **Mutação de Aberturas (R-12)**: Feita de forma não-destrutiva via modificadores `Boolean` vinculados. O add-on não remove vértices da parede manualmente durante a inserção da porta, garantindo que o histórico da malha e integridade de renderização sejam mantidos.
* **Cálculo de Nesting (R-13)**: Lógica isolada em puro Python que não modifica objetos na cena 3D. Garante estabilidade operacional mesmo sob grandes volumes de peças.


## Re-extração 2026-10-10 — permissões e capacidades atuais

🟢 Não foi identificado RBAC/ACL interno nos módulos analisados. Preferência de biblioteca legada, `poll`, visibilidade de objetos e capacidade de adaptadores são filtros de funcionalidade/contexto, não fronteiras de autorização. Permissões de arquivo são herdadas do processo Blender e do sistema operacional.

| Grupo | Cena / UI | Disco | Restrição relevante |
|---|---|---|---|
| canvas2d, walls2d, cabinet_editor | Editor, handlers, rascunho e aplicação | Persistência no blend | Tipo de área, sessão e objeto compatível |
| selection, measure, move_over, stick | Leitura e alteração de objetos | No `.blend`: `Object.btm_stick` (vínculo do grudar), `Scene.btm_saved_positions` (posições salvas do Mover Sobre) e `Scene.btm_component_select`; estado de sessão em `WindowManager` (`btm_move_over`, `btm_insertion_plane`, `btm_component_exempt`); measure sem propriedade própria _(Revisão cruzada 2026-10-10: stick/props.py:65, move_over/props.py:54-57, selection/component_props.py:35-39)_ | Modo/contexto e plano elegível |
| collision, inspection | Checagem, overlay e estado de frentes | Save handlers do blend | Escopo de itens; não segregação por usuário |
| aggregates, customize | Conversão, reconstrução e filhos | Bibliotecas e importações | Formatos/capacidades suportados |
| standards | Definições e sincronização | JSON/XML e migração | BR/US protegidos na API; USER editável |
| legacy | UI e conversão | Leitura de arquivos/grupos e marcador | show_legacy_libraries controla UI |
| library_panel | POST_PIXEL e popover | Categorias/modelos do usuário | Catálogo fixo e categorias próprias |
| object_library | Salvar/inserir/retexturar | Raiz embutida e raiz do usuário | Embutida somente leitura na UI/fluxo |
| molding, geometry_free | Criar/reconstruir malhas/curvas | Perfis blend; dados no projeto | Molding restrito a bibliotecas legadas |

A descrição antiga de cutting como inteiramente independente de bpy só se aplica ao núcleo de cálculo: a extração de PartRecord atual lê a cena em `cutting/part_sources.py`. Escrita da biblioteca não é sandbox de segurança; arquivo externo requer validação de formato, não ganha confiança só por estar em uma pasta conhecida.
