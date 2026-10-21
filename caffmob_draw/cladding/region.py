"""Região coplanar avaliada no referencial ortonormal do controlador, em mm (D-20/R10).

Referências: docs/rag/blender-api/corpus/Object: bpy.types.Object.to_mesh e
Mesh: bpy.types.Mesh.calc_loop_triangles. Nenhum modificador é aplicado ao hospedeiro.
"""
import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
from .core import area

PLANE_TOLERANCE = 0.0001  # m: 0,1 mm; não aceita a face oposta da parede.


def frame(host, origin, normal, axis_u):
    matrix = host.matrix_world
    n = (matrix.to_3x3().inverted().transposed() @ Vector(normal)).normalized()
    u = matrix.to_3x3() @ Vector(axis_u)
    u = (u - n * u.dot(n)).normalized()
    if n.length < .99 or u.length < .99:
        raise ValueError('Plano da face inválido')
    v = n.cross(u).normalized()
    basis = Matrix((u, v, n)).transposed().to_4x4()
    basis.translation = matrix @ Vector(origin)
    return basis


def extract(data, depsgraph=None):
    host = data.host
    if host is None:
        raise ValueError('Hospedeiro excluído; escolha Reassociar')
    basis = frame(host, data.plane_origin, data.plane_normal, data.plane_u)
    # Subtrair a origem no espaço do hospedeiro antes da transformação linear evita cancelamento
    # numérico de translações no mundo (que fazia uma peça intacta ganhar outra assinatura).
    linear = basis.to_3x3().transposed() @ host.matrix_world.to_3x3()
    origin = Vector(data.plane_origin)
    evaluated = host.evaluated_get(depsgraph or bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangles = []
    try:
        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            points = [linear @ (mesh.vertices[i].co - origin) for i in tri.vertices]
            if max(abs(p.z) for p in points) > PLANE_TOLERANCE:
                continue
            poly = tuple((p.x * 1000, p.y * 1000) for p in points)
            if area(poly) >= 1:  # R10: descartar fragmento menor que 1 mm².
                # Orientar todas as faces para fora, independentemente da triangulação do Boolean.
                if sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(poly, poly[1:]+poly[:1])) < 0:
                    poly = tuple(reversed(poly))
                triangles.append(poly)
    finally:
        evaluated.to_mesh_clear()
    if not triangles:
        raise ValueError('Nenhuma região coplanar na face escolhida')
    return basis, tuple(triangles)


def bounds(triangles):
    points = [p for tri in triangles for p in tri]
    x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
    y0, y1 = min(p[1] for p in points), max(p[1] for p in points)
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
