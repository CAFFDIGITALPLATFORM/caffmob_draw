"""BMesh: recortar a superfície avaliada e extrudar no plano do controlador (D-20).

API: docs/rag/blender-api/corpus/bmesh.ops: bmesh.ops.bisect_plane, #bmesh.ops.extrude_face_region.
"""
import bmesh  # type: ignore
import bpy  # type: ignore


def collection(controller, role):
    data = controller.btm_cladding
    parent = bpy.context.scene.collection
    # Nomes do Blender são globais: procurar pelo filho, nunca pela base global do nome.
    for label in ('Revestimentos', data.environment, data.host.name, role):
        child = next((c for c in parent.children if c.get('btm_cladding_label') == label), None)
        if child is None:
            child = bpy.data.collections.new(label)
            child['btm_cladding_label'] = label
            parent.children.link(child)
        parent = child
    return parent


def mesh_for(triangles, piece, backing_mm=0):
    bm = bmesh.new()
    mesh = None
    try:
        for tri in triangles:
            bm.faces.new([bm.verts.new((x/1000, y/1000, 0)) for x, y in tri])
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
        poly = piece.polygon
        for a, b in zip(poly, poly[1:] + poly[:1]):
            # Polígono anti-horário: normal aponta para fora; clear_outer retira o exterior.
            dx, dy = b[0] - a[0], b[1] - a[1]
            bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), dist=1e-7,
                                  plane_co=(a[0]/1000, a[1]/1000, 0), plane_no=(dy, -dx, 0), clear_outer=True)
        bmesh.ops.dissolve_limit(bm, angle_limit=1e-5, verts=list(bm.verts), edges=list(bm.edges))
        tiny = [f for f in bm.faces if f.calc_area() < 1e-6]
        if tiny:
            bmesh.ops.delete(bm, geom=tiny, context='FACES')
        if not bm.faces:
            return None
        # O fundo parte da face; as ripas partem da superfície externa do fundo.
        offset = 0 if piece.role == 'BACKING' else backing_mm / 1000
        bmesh.ops.translate(bm, verts=list(bm.verts), vec=(0, 0, offset))
        result = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        verts = [v for v in result['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0, 0, piece.thickness_mm / 1000))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        mesh = bpy.data.meshes.new('Peça de revestimento')
        bm.to_mesh(mesh)
        mesh.update()
        return mesh
    except Exception:
        if mesh is not None:
            bpy.data.meshes.remove(mesh)
        raise
    finally:
        bm.free()


def attach(controller, piece, mesh):
    obj = bpy.data.objects.new('Revestimento ' + piece.key, mesh)
    collection(controller, piece.role).objects.link(obj)
    obj.parent = controller
    obj['btm_cladding_piece'] = dict(owner=controller.btm_cladding.uid, key=piece.key, generated=True)
    # RN-COLLISION-02: OFF já é respeitado por scan/rules/guard. Acabamento não engrossa o obstáculo da parede.
    obj.btm_plane.collision_override = 'OFF'
    return obj


def remove(obj):
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
