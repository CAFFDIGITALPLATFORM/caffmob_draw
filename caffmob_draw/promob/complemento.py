"""Complemento local do projeto `.promob` (071 D-11, D-30): o que o documento do MOBI não comporta.

Móveis (grupos como Empty, folhas como caixa), lajes livres extrudadas e malhas OBJ vinculadas, numa coleção
"Promob · <ambiente>" fora da coleção do MOBI. Os objetos não recebem `caffmob_tipo`: assim a remontagem do
`cena_v2` (`_remover_colecao`) os preserva. As texturas do arquivo são embutidas no `.blend`.
"""
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone

import bpy
from mathutils import Matrix, Vector

MM = 0.001


def _linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _pasta_temporaria():
    pasta = os.path.join(tempfile.gettempdir(), 'caffmob_promob')
    os.makedirs(pasta, exist_ok=True)
    return pasta


def _arquivo_temporario(nome, dados):
    """Grava bytes do ZIP numa pasta temporária com nome saneado (D-02): só o hash e a extensão."""
    ext = os.path.splitext(nome)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.bmp', '.tga', '.obj', '.mtl'):
        ext = '.bin'
    caminho = os.path.join(_pasta_temporaria(), hashlib.sha256(dados).hexdigest()[:24] + ext)
    if not os.path.exists(caminho):
        with open(caminho, 'wb') as f:
            f.write(dados)
    return caminho


class Montagem:
    def __init__(self, context, pacote, conversao):
        self.context, self.pacote, self.c = context, pacote, conversao['complemento']
        self.cache = {}
        self.criados = 0

    # -- materiais ------------------------------------------------------------------------------------------------
    def material(self, mid):
        if not mid or mid not in self.c['materiais']:
            return None, None
        if mid in self.cache:
            return self.cache[mid]
        dado = self.c['materiais'][mid]
        m = bpy.data.materials.new('Promob · ' + dado['nome'][:50])
        m['btm_promob_material'] = mid
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        cor = dado['cor'].lstrip('#')
        rgb = [_linear(int(cor[i:i + 2], 16)) for i in (0, 2, 4)]
        m.diffuse_color = (*rgb, 1.0)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
        escala = None
        if dado.get('textura'):
            dados = self.pacote.ler(dado['textura'])
            if dados:
                try:
                    imagem = bpy.data.images.load(_arquivo_temporario(dado['textura'], dados), check_existing=True)
                    imagem.pack()
                    no = m.node_tree.nodes.new('ShaderNodeTexImage')
                    no.image = imagem
                    if bsdf is not None:
                        m.node_tree.links.new(no.outputs['Color'], bsdf.inputs['Base Color'])
                    escala = dado.get('escala') or (1000.0, 1000.0)
                except RuntimeError:
                    escala = None
        self.cache[mid] = (m, escala)
        return self.cache[mid]

    # -- malhas ---------------------------------------------------------------------------------------------------
    @staticmethod
    def _uv_da_caixa(mesh, escala):
        uv = mesh.uv_layers.new(name='UVMap')
        ex, ey = (escala or (1000.0, 1000.0))
        for poly in mesh.polygons:
            n = poly.normal
            eixo = max(range(3), key=lambda k: abs(n[k]))
            a, b = [(1, 2), (0, 2), (0, 1)][eixo]
            for li in poly.loop_indices:
                co = mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv = (co[a] / (ex * MM), co[b] / (ey * MM))

    def _malha_da_caixa(self, nome, w, d, h, material):
        v = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        mesh = bpy.data.meshes.new(nome)
        mesh.from_pydata(v, [], f)
        mat, escala = material
        if mat is not None:
            mesh.materials.append(mat)
        self._uv_da_caixa(mesh, escala)
        return mesh

    def _malha_da_laje(self, nome, contorno, altura, material):
        n = len(contorno)
        area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(contorno, contorno[1:] + contorno[:1]))
        if area < 0:
            contorno = list(reversed(contorno))
        v = [(x * MM, y * MM, 0) for x, y in contorno] + [(x * MM, y * MM, altura * MM) for x, y in contorno]
        f = [tuple(reversed(range(n))), tuple(range(n, 2 * n))] + \
            [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        mesh = bpy.data.meshes.new(nome)
        mesh.from_pydata(v, [], f)
        mesh.validate()
        mat, escala = material
        if mat is not None:
            mesh.materials.append(mat)
        self._uv_da_caixa(mesh, escala)
        return mesh

    # -- objetos --------------------------------------------------------------------------------------------------
    @staticmethod
    def _matriz(origem, rotacao):
        return Matrix.Translation(Vector(origem) * MM) @ Matrix.Rotation(math.radians(rotacao), 4, 'Z')

    def _objeto(self, no, dados, colecao, pai, matriz):
        obj = bpy.data.objects.new(no['nome'], dados)
        colecao.objects.link(obj)
        obj['btm_promob_item'] = no['promob_id']
        if pai is not None:
            obj.parent = pai
        obj.matrix_world = matriz
        obj.hide_viewport = obj.hide_render = not no['visivel']
        self.criados += 1
        return obj

    def _malha_vinculada(self, no, colecao, pai):
        """Malha OBJ ajustada eixo a eixo à caixa do item, como o Promob estica a entidade externa.

        Os OBJ dos projetos vêm em escalas e eixos diferentes (a maioria em mm, Z para cima). Entre Z e Y para cima,
        vale a orientação que pede a escala mais uniforme.
        """
        dados = self.pacote.ler(no['entrada'])
        if not dados:
            return None
        antes = set(bpy.data.objects)
        try:
            bpy.ops.wm.obj_import(filepath=_arquivo_temporario(no['entrada'], dados), forward_axis='Y', up_axis='Z')
        except RuntimeError:
            return None
        novos = [o for o in bpy.data.objects if o not in antes]
        malhas = [o for o in novos if o.type == 'MESH']
        if not malhas:
            for o in novos:
                bpy.data.objects.remove(o, do_unlink=True)
            return None
        cantos = [o.matrix_world @ Vector(c) for o in malhas for c in o.bound_box]
        alvo = [max(v * MM, 1e-6) for v in no['dimensoes']]
        melhor = None
        for giro in (Matrix.Identity(4), Matrix.Rotation(math.radians(90), 4, 'X')):
            girados = [giro @ c for c in cantos]
            lo = Vector([min(c[k] for c in girados) for k in range(3)])
            ext = [max(max(c[k] for c in girados) - lo[k], 1e-9) for k in range(3)]
            escalas = [alvo[k] / ext[k] for k in range(3)]
            espalhamento = max(math.log(e) for e in escalas) - min(math.log(e) for e in escalas)
            if melhor is None or espalhamento < melhor[0]:
                melhor = (espalhamento, giro, lo, escalas)
        _, giro, lo, escalas = melhor
        raiz = self._objeto(no, None, colecao, pai, self._matriz(no['origem'], no['rotacao']))
        ajuste = Matrix.Diagonal((*escalas, 1.0)) @ Matrix.Translation(-lo) @ giro
        material = self.material(no.get('material'))[0]
        for o in novos:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            colecao.objects.link(o)
            mundo = o.matrix_world.copy()
            o.parent = raiz
            o.matrix_world = raiz.matrix_world @ ajuste @ mundo
            o['btm_promob_item'] = no['promob_id']
            if material is not None and o.type == 'MESH' and not o.data.materials:
                o.data.materials.append(material)
            o.hide_viewport = o.hide_render = not no['visivel']
        return raiz

    def no(self, no, colecao, pai=None):
        matriz = self._matriz(no['origem'], no['rotacao'])
        if no['tipo'] == 'grupo':
            obj = self._objeto(no, None, colecao, pai, matriz)
            obj.empty_display_size = 0.05
        elif no['tipo'] == 'laje':
            obj = self._objeto(no, self._malha_da_laje(no['nome'], no['contorno'], no['altura'],
                                                       self.material(no.get('material'))), colecao, pai, matriz)
        elif no['tipo'] == 'malha':
            obj = self._malha_vinculada(no, colecao, pai)
            if obj is None:
                no = dict(no, tipo='caixa')
                return self.no(no, colecao, pai)
        else:
            w, d, h = (v * MM for v in no['dimensoes'])
            obj = self._objeto(no, self._malha_da_caixa(no['nome'], w, d, h, self.material(no.get('material'))),
                               colecao, pai, matriz)
        for filho in no['filhos']:
            self.no(filho, colecao, obj)
        return obj

    def montar(self):
        cena = self.context.scene
        colecao = bpy.data.collections.new('Promob · ' + (self.c['ambiente'] or 'Ambiente')[:50])
        cena.collection.children.link(colecao)
        for no in self.c['moveis']:
            self.no(no, colecao)
        return colecao


def montar(context, pacote, conversao):
    """Cria o complemento na cena atual; devolve a coleção."""
    return Montagem(context, pacote, conversao).montar()


def registrar(context, caminho, sha256, conversao):
    """`scene['caffmob_promob']` (M-02): origem, relatório e cliente; nunca dados de licença."""
    context.scene['caffmob_promob'] = json.dumps(dict(
        arquivo=os.path.basename(caminho), pasta=os.path.dirname(caminho), sha256=sha256,
        ambiente=conversao['complemento']['ambiente'],
        importado_em=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        relatorio=conversao['relatorio'], cliente=conversao['cliente']), ensure_ascii=False)


def lido(context):
    texto = context.scene.get('caffmob_promob')
    try:
        return json.loads(texto) if texto else None
    except (TypeError, ValueError):
        return None
