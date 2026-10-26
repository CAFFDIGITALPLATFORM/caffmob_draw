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
import traceback
import uuid
from datetime import datetime, timezone

import bpy
from mathutils import Matrix, Vector

from . import cameras

MM = 0.001
CHAPA_PROP = 'btm_promob_chapa'


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
        self.a_baixar = {}           # textura do catálogo só com a miniatura → objetos que a usam
        self.que_abrem = []          # (objeto, mecanismo) para ligar depois que a árvore inteira existe
        self.camadas = {}            # (coleção, camada do Promob) → subcoleção

    # -- materiais ------------------------------------------------------------------------------------------------
    def material(self, mid):
        if not mid or mid not in self.c['materiais']:
            return None, None
        if mid in self.cache:
            return self.cache[mid]
        dado = self.c['materiais'][mid]
        if dado.get('textura_catalogo'):
            mat = self._material_do_catalogo(dado)
            if mat is not None:
                self.cache[mid] = (mat, None)
                return self.cache[mid]
        m = bpy.data.materials.new('Promob · ' + dado['nome'][:50])
        m['btm_promob_material'] = mid
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        cor = dado['cor'].lstrip('#')
        rgb = [_linear(int(cor[i:i + 2], 16)) for i in (0, 2, 4)]
        alfa = 1.0 - float(dado.get('transparencia') or 0.0)
        m.diffuse_color = (*rgb, alfa)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
            classe = dado.get('classe')
            if classe in ('metal', 'espelho'):
                bsdf.inputs['Metallic'].default_value = 1.0
                bsdf.inputs['Roughness'].default_value = 0.05 if classe == 'espelho' else 0.3
            elif classe == 'vidro':
                bsdf.inputs['Roughness'].default_value = 0.05
                bsdf.inputs['Alpha'].default_value = alfa
        if alfa < 1.0:
            if hasattr(m, 'surface_render_method'):
                m.surface_render_method = 'BLENDED'
            else:
                m.blend_method = 'BLEND'
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

    def _material_do_catalogo(self, dado):
        """Material de imagem da chapa do catálogo do addon (Duratex, Arauco...), com o tamanho real da chapa.

        Com a imagem baixada, ela; sem, a miniatura do pacote, e a imagem entra pelo download ao fim da montagem."""
        from ..object_library import retexture
        from ..texture_library import catalog, downloads
        entrada = catalog.item(dado['textura_catalogo'])
        if entrada is None:
            return None
        caminho = downloads.cached(entrada['id'], entrada)
        if not caminho:
            caminho = catalog.thumb_path(entrada)
            if not caminho:
                return None
            self.a_baixar.setdefault(entrada['id'], [])
        largura, altura = dado.get('tamanho') or catalog.default_size(entrada)
        return retexture.image_material(caminho, largura, altura, texture_id=entrada['id'])

    def _baixar_texturas(self):
        """Troca a miniatura pela imagem de trabalho: o mesmo caminho do soltar textura (download e aplicação)."""
        from ..texture_library import apply, downloads
        if not self.a_baixar or downloads.unavailable_reason():
            return
        for item_id, objetos in self.a_baixar.items():
            try:
                apply.apply(objetos, item_id)
            except Exception:           # sem conta ou sem rede: a miniatura fica, e soltar a textura depois resolve
                traceback.print_exc()

    def _peca(self, obj, no):
        """Veio da chapa e componentes do Promob na peça."""
        dado = self.c['materiais'].get(no.get('material')) or {}
        if dado.get('textura_catalogo') in self.a_baixar:
            self.a_baixar[dado['textura_catalogo']].append(obj)
        if no.get('componente'):
            obj['btm_component'] = no['componente']
        if no.get('componentes'):
            obj['btm_promob_componentes'] = json.dumps(no['componentes'], ensure_ascii=False)
        if dado.get('veio') and getattr(obj, 'btm_part', None) is not None:
            obj.btm_part.grain = dado['veio']          # gira a imagem pelo serviço de veio (067, RF-063)
        if no.get('chapa'):
            obj[CHAPA_PROP] = json.dumps(no['chapa'], ensure_ascii=False)     # vai ao plano de corte (PROMOB)
            obj['btm_uid'] = obj.get('btm_uid') or uuid.uuid4().hex

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

    @staticmethod
    def _cilindro(v, f, centro, raio, comprimento, eixo, lados=16):
        """Acrescenta a `v`/`f` um cilindro fechado a partir de `centro`, ao longo do eixo 0, 1 ou 2."""
        a, b = [k for k in range(3) if k != eixo]
        i0 = len(v)
        for ponta in (0.0, comprimento):
            for i in range(lados):
                t = 2 * math.pi * i / lados
                p = list(centro)
                p[a] += raio * math.cos(t)
                p[b] += raio * math.sin(t)
                p[eixo] += ponta
                v.append(tuple(p))
        f.append(tuple(i0 + i for i in reversed(range(lados))))
        f.append(tuple(i0 + lados + i for i in range(lados)))
        f.extend((i0 + i, i0 + (i + 1) % lados, i0 + lados + (i + 1) % lados, i0 + lados + i) for i in range(lados))

    def _malha_da_forma(self, nome, forma, w, d, h, material):
        """Silhueta da louça ou do metal do catálogo dentro da caixa do item (frente em y = 0, fundo em y = d)."""
        v, f = [], []
        if forma == 'torneira':
            r = min(w, d) * 0.18
            self._cilindro(v, f, (w / 2, d - r * 1.5, 0), r, h, 2)
            self._cilindro(v, f, (w / 2, 0, h - r * 1.2), r * 0.7, d - r * 1.5, 1)
        else:
            # cuba: caixa aberta em cima, com parede e fundo de 2% da largura
            e = max(min(w, d) * 0.02, 0.002)
            v = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h),
                 (e, e, h), (w - e, e, h), (w - e, d - e, h), (e, d - e, h),
                 (e, e, e), (w - e, e, e), (w - e, d - e, e), (e, d - e, e)]
            f = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
                 (4, 5, 9, 8), (5, 6, 10, 9), (6, 7, 11, 10), (7, 4, 8, 11),
                 (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15)]
        mesh = bpy.data.meshes.new(nome)
        mesh.from_pydata(v, [], f)
        mesh.validate()
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
    def _matriz(origem, rotacao, eixos=None):
        """Origem em mm e os eixos do item (X, Y, Z: colunas); sem eixos, só o giro em Z."""
        if eixos is None:
            return Matrix.Translation(Vector(origem) * MM) @ Matrix.Rotation(math.radians(rotacao), 4, 'Z')
        x, y, z = (Vector(e) for e in eixos)
        m = Matrix(((x.x, y.x, z.x, 0), (x.y, y.y, z.y, 0), (x.z, y.z, z.z, 0), (0, 0, 0, 1)))
        return Matrix.Translation(Vector(origem) * MM) @ m

    def _camada(self, colecao, nome):
        """Subcoleção da camada do Promob: a camada desligada no projeto entra oculta, e o olho a liga de novo."""
        nome = (nome or 'Default').strip()[:50] or 'Default'
        chave = (colecao.name, nome)
        if chave not in self.camadas:
            sub = bpy.data.collections.new('Camada · ' + nome)
            colecao.children.link(sub)
            sub['btm_promob_camada'] = nome
            sub.hide_viewport = sub.hide_render = nome in set(self.c.get('camadas_ocultas') or ())
            self.camadas[chave] = sub
        return self.camadas[chave]

    def _objeto(self, no, dados, colecao, pai, matriz):
        obj = bpy.data.objects.new(no['nome'], dados)
        self._camada(colecao, no.get('camada')).objects.link(obj)
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
        giros = (Matrix.Identity(4),) if no.get('eixos') else (Matrix.Identity(4), Matrix.Rotation(math.radians(90), 4, 'X'))
        for giro in giros:
            girados = [giro @ c for c in cantos]
            lo = Vector([min(c[k] for c in girados) for k in range(3)])
            ext = [max(max(c[k] for c in girados) - lo[k], 1e-9) for k in range(3)]
            escalas = [alvo[k] / ext[k] for k in range(3)]
            espalhamento = max(math.log(e) for e in escalas) - min(math.log(e) for e in escalas)
            if melhor is None or espalhamento < melhor[0]:
                melhor = (espalhamento, giro, lo, escalas)
        _, giro, lo, escalas = melhor
        raiz = self._objeto(no, None, colecao, pai, self._matriz(no['origem'], no['rotacao'], no.get('eixos')))
        ajuste = Matrix.Diagonal((*escalas, 1.0)) @ Matrix.Translation(-lo) @ giro
        material = self.material(no.get('material'))[0]
        for o in novos:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            self._camada(colecao, no.get('camada')).objects.link(o)
            mundo = o.matrix_world.copy()
            o.parent = raiz
            o.matrix_world = raiz.matrix_world @ ajuste @ mundo
            o['btm_promob_item'] = no['promob_id']
            if material is not None and o.type == 'MESH' and not o.data.materials:
                o.data.materials.append(material)
            o.hide_viewport = o.hide_render = not no['visivel']
        return raiz

    def no(self, no, colecao, pai=None):
        obj = self._no(no, colecao, pai)
        if obj is not None and no.get('abertura'):
            obj['btm_promob_abertura'] = no['abertura']         # a folha genérica do vão some (cena_v2)
        if obj is not None and no.get('mecanismo'):
            self.que_abrem.append((obj, no['mecanismo']))
        return obj

    def _no(self, no, colecao, pai=None):
        matriz = self._matriz(no['origem'], no['rotacao'], no.get('eixos'))
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
            material = self.material(no.get('material'))
            malha = (self._malha_da_forma(no['nome'], no['forma'], w, d, h, material) if no.get('forma') else
                     self._malha_da_caixa(no['nome'], w, d, h, material))
            obj = self._objeto(no, malha, colecao, pai, matriz)
            self._peca(obj, no)
            if no.get('catalogo'):
                obj.display_type = 'WIRE'                  # marca o lugar e a medida sem tapar a vista
                obj.hide_render = True
                obj['btm_promob_catalogo'] = True
        for filho in no['filhos']:
            self.no(filho, colecao, obj)
        return obj

    def montar(self):
        cena = self.context.scene
        colecao = bpy.data.collections.new('Promob · ' + (self.c['ambiente'] or 'Ambiente')[:50])
        cena.collection.children.link(colecao)
        for no in self.c['moveis']:
            self.no(no, colecao)
        from ..mobi.cena_v2 import SEM_FOLHA_PROP, esconder_folhas_substituidas
        cena[SEM_FOLHA_PROP] = json.dumps(self.c.get('aberturas_sem_folha') or [])   # vale em toda remontagem
        esconder_folhas_substituidas(cena)
        self._baixar_texturas()
        self.context.view_layer.update()
        self.abrem = sum(1 for obj, mecanismo in self.que_abrem if self._abrir_e_fechar(obj, mecanismo))
        self.cameras = cameras.criar(self.context, self.c.get('cameras') or [])
        return colecao

    def _abrir_e_fechar(self, obj, mecanismo):
        """Porta, basculante, correr ou gaveta do Promob vira folha do addon (067 D-23): o painel abre e fecha, e o
        estado salvo no projeto (CURRENTVALUE) entra sem a varredura de contato."""
        from ..aggregates import apply, leaf
        pai = obj.parent
        if pai is None:
            return False
        fechar = mecanismo.get('fechar')
        if fechar:
            # A peça veio na pose aberta do projeto: fecha antes de virar folha, e a fração salva reabre.
            if 'translacao' in fechar:
                volta = Matrix.Translation(Vector(fechar['translacao']) * MM)
            else:
                c = Vector(fechar['centro']) * MM
                volta = Matrix.Translation(c) @ Matrix.Rotation(math.radians(fechar['angulo']), 4, 'Z') @ \
                    Matrix.Translation(-c)
            obj.matrix_world = volta @ obj.matrix_world
            self.context.view_layer.update()
        canonico = leaf.front_frame(pai).inverted() @ pai.matrix_world.inverted()
        cantos = [canonico @ (o.matrix_world @ Vector(c)) for o in [obj] + list(obj.children_recursive)
                  if o.type == 'MESH' for c in o.bound_box]
        if not cantos:
            return False
        lo = Vector([min(c[k] for c in cantos) for k in range(3)])
        hi = Vector([max(c[k] for c in cantos) for k in range(3)])
        tipo, maximo = mecanismo['tipo'], float(mecanismo['maximo'])
        opcoes = dict(motion={'HINGE': 'SWING', 'TILT': 'SWING'}.get(tipo, tipo))
        base = Vector(lo)
        if tipo in ('HINGE', 'TILT'):
            eixo = canonico @ (Vector(mecanismo['eixo']) * MM)
            # O eixo do Promob fica no meio da espessura, 7,5 mm para dentro da borda: girar ali enfia o canto da
            # porta na lateral. Ele decide o lado; o giro é pela quina da frente, como nas folhas do addon.
            if tipo == 'HINGE':
                esquerda = abs(eixo.x - lo.x) <= abs(eixo.x - hi.x)
                opcoes['hinge'] = 'LEFT' if esquerda else 'RIGHT'
                base = Vector((lo.x if esquerda else hi.x, lo.y, lo.z))
            else:
                topo = eixo.z >= (lo.z + hi.z) / 2
                opcoes['hinge'] = 'TOP' if topo else 'BOTTOM'
                base = Vector((lo.x, lo.y, hi.z if topo else lo.z))
            opcoes['max_angle'] = min(maximo, 180.0)
        else:
            sentido = canonico.to_3x3() @ Vector(mecanismo['sentido'])
            if tipo == 'SLIDE':
                opcoes['slide_dir'] = 'POS_X' if sentido.x >= 0 else 'NEG_X'
            elif sentido.y > 0.5:
                return False              # gaveta que não sai pela frente do dono: fica fixa
            opcoes['travel'] = maximo * MM
        obj['btm_leaf_manual_base'] = list(base)
        try:
            leaf.make_leaf(obj, pai, **opcoes)
        except Exception:
            traceback.print_exc()
            return False
        if mecanismo.get('abertura'):
            apply._write(obj, 'open_value', float(mecanismo['abertura']))
            leaf.apply_fraction(obj, float(mecanismo['abertura']))
        return True


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
