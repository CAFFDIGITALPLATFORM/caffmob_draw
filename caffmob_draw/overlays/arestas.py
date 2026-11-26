"""Arestas do viewport: linha preta fina com a espessura da preferência (027, T004/T005).

O interruptor Linhas (`Scene.btm_view_lines`) não usa mais o wireframe do Blender, que sai na cor do tema e com
espessura fixa: as arestas das malhas passam a ser desenhadas em preto, com a espessura escolhida em
`BTM_AddonPreferences.espessura_aresta` (padrão 0,2 px). Com o interruptor desligado — "Somente textura" — este
módulo não desenha nada: sem aresta e sem vértice, a cena fica limpa.

Os lotes de desenho ficam em cache por objeto (arestas já no mundo). O `depsgraph_update_post` descarta só as
entradas dos objetos ou malhas que mudaram, então mover um armário não reconstrói a cena inteira, e editar a malha
não deixa aresta velha na tela.
"""

from bpy.app.handlers import persistent  # type: ignore

ESPESSURA_PADRAO = 0.2
_caches = {}            # nome do objeto -> {'mesh', 'matrix', 'verts', 'edges', 'batch'}
_handler = None


def valor(preferencias):
    """Espessura em pixels a partir das preferências recebidas (0,2 sem valor salvo)."""
    try:
        return max(float(getattr(preferencias, 'espessura_aresta', ESPESSURA_PADRAO)), 0.2)
    except (TypeError, ValueError):
        return ESPESSURA_PADRAO


def espessura():
    """Espessura da aresta em pixels, das preferências do add-on (0,2 fora do Blender ou sem valor salvo)."""
    import bpy  # type: ignore

    addon = bpy.context.preferences.addons.get(__package__.rsplit('.', 1)[0])
    return valor(getattr(addon, 'preferences', None))


def _desenha(context):
    """Uma passada de desenho: as arestas de todas as malhas visíveis na vista que está pedindo o quadro."""
    scene = getattr(context, 'scene', None)
    space = getattr(context, 'space_data', None)
    region = getattr(context, 'region', None)
    if scene is None or space is None or region is None or not getattr(scene, 'btm_view_lines', False):
        return
    if getattr(space, 'type', '') != 'VIEW_3D' or space.shading.type != 'SOLID':
        return
    if not getattr(space.overlay, 'show_overlays', True):
        return
    view_layer = getattr(context, 'view_layer', None)
    if view_layer is None:
        return
    objetos = [o for o in view_layer.objects
               if o.type == 'MESH' and o.mode == 'OBJECT' and o.visible_get() and len(o.data.edges)]
    if not objetos:
        return

    import gpu  # type: ignore

    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    largura = espessura()
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('LESS_EQUAL')
    shader.bind()
    shader.uniform_float('color', (0.0, 0.0, 0.0, 1.0))
    shader.uniform_float('lineWidth', largura)
    shader.uniform_float('viewportSize', (region.width, region.height))
    try:
        for obj in objetos:
            batch = _batch(obj, shader)
            if batch is not None:
                batch.draw(shader)
    finally:
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('NONE')


def _batch(obj, shader):
    """Lote de arestas do objeto no mundo, refeito só quando a malha ou a matriz mudam."""
    from gpu_extras.batch import batch_for_shader  # type: ignore

    mesh = obj.data
    matrix = obj.matrix_world.copy()
    entry = _caches.get(obj.name)
    if (entry is not None and entry['mesh'] is mesh and entry['matrix'] == matrix
            and entry['verts'] == len(mesh.vertices) and entry['edges'] == len(mesh.edges)):
        return entry['batch']
    coords = [matrix @ v.co for v in mesh.vertices]
    positions = []
    for edge in mesh.edges:
        a, b = edge.vertices
        positions.append(coords[a])
        positions.append(coords[b])
    batch = batch_for_shader(shader, 'LINES', {'pos': positions}) if positions else None
    _caches[obj.name] = {'mesh': mesh, 'matrix': matrix, 'verts': len(mesh.vertices),
                         'edges': len(mesh.edges), 'batch': batch}
    return batch


@persistent
def _ao_atualizar(_scene, depsgraph=None):
    """Objeto ou malha mudou: esquece só o que ficou velho."""
    if depsgraph is None:
        return
    import bpy  # type: ignore

    mudaram = set()
    for update in depsgraph.updates:
        ident = update.id
        if isinstance(ident, bpy.types.Object):
            mudaram.add(ident.name)
        elif isinstance(ident, bpy.types.Mesh):
            mudaram.update(name for name, entry in _caches.items() if entry['mesh'] is ident)
    for name in mudaram:
        _caches.pop(name, None)


def forget():
    """Descarta o cache inteiro (desfazer, arquivo novo, preferência trocada)."""
    _caches.clear()


def register():
    import bpy  # type: ignore

    global _handler
    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_VIEW')
    if _ao_atualizar not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_ao_atualizar)


def unregister():
    import bpy  # type: ignore

    global _handler
    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, 'WINDOW')
        _handler = None
    if _ao_atualizar in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_ao_atualizar)
    forget()


def _draw():
    """Entrada do handler de desenho: erro de desenho nunca derruba a viewport."""
    import bpy  # type: ignore

    try:
        _desenha(bpy.context)
    except Exception:
        pass
