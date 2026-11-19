bl_info = {
    "name": "Construtor de Armários - CAFF MOB",
    "author": "CAFF MOB",
    "version": (2, 0, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > CAFF MOB | Viewport Right-Click",
    "description": "Construtor paramétrico de armários para Blender 5.2.0 com contrato de chapas, editor de gavetas, corrediça 3D ST48-0200, porta deslizante e menu Abrir/Fechar",
    "category": "3D View",
}

import json
import math
import os
import bpy
from bpy.types import Operator, Panel, PropertyGroup, Menu
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty,
)
from mathutils import Vector

COLLECTION_NAME = "CAFF_ARMARIO_GERADO"
SLIDE_OBJ_RELPATH = os.path.join("assets", "slide-st48-0200-0.obj")

THICKNESS_ITEMS = [
    ('6', "6 mm", "Chapa de 6 mm (fundo)"),
    ('15', "15 mm", "Chapa padrão de 15 mm"),
    ('18', "18 mm", "Chapa de 18 mm"),
    ('25', "25 mm", "Chapa encorpada de 25 mm"),
]

DRAWER_MODEL_ITEMS = [
    ('s_cf_reta',   "s/ CF Reta",   "Gaveta sem contra-frente, puxador reto"),
    ('s_cf_normal', "s/ CF Normal", "Gaveta sem contra-frente, normal"),
    ('s_cf_vidro',  "s/ CF Vidro",  "Gaveta sem contra-frente, frente vidro"),
    ('s_cf_gola',   "s/ CF Gola",   "Gaveta sem contra-frente, perfil gola"),
    ('s_cf_cava',   "s/ CF Cava",   "Gaveta sem contra-frente, puxador cava"),
    ('c_cf_reta',   "c/ CF Reta",   "Gaveta com contra-frente, puxador reto"),
    ('c_cf_normal', "c/ CF Normal", "Gaveta com contra-frente, normal"),
    ('c_cf_vidro',  "c/ CF Vidro",  "Gaveta com contra-frente, frente vidro"),
    ('c_cf_gola',   "c/ CF Gola",   "Gaveta com contra-frente, perfil gola"),
    ('c_cf_cava',   "c/ CF Cava",   "Gaveta com contra-frente, puxador cava"),
]


def mm(val: float) -> float:
    return float(val) / 1000.0


def addon_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def slide_obj_path() -> str:
    return os.path.join(addon_dir(), SLIDE_OBJ_RELPATH)


def ensure_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection(col):
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_pbr_material(name, base_color, roughness=0.55, metallic=0.0, transmission=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    mat.diffuse_color = (*base_color, alpha)
    return mat


def link_only_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)


def add_box(col, name, loc, dims, material, parent=None, bevel_mm=0.8):
    if min(dims) <= 0.0001:
        return None
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only_to_collection(obj, col)
    if material:
        obj.data.materials.append(material)
    if bevel_mm > 0:
        bevel = obj.modifiers.new("Micro_Bisel", "BEVEL")
        bevel.width = mm(bevel_mm)
        bevel.segments = 2
        bevel.limit_method = 'ANGLE'
    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj


def add_empty(col, name, loc, parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.location = loc
    empty.empty_display_size = 0.05
    col.objects.link(empty)
    if parent is not None:
        empty.parent = parent
        empty.matrix_parent_inverse = parent.matrix_world.inverted()
    return empty


# ============================================================================
# CONTRATO DE INTEGRAÇÃO COM O ADDON HOST (ELICITAÇÃO DE REQUISITOS)
# ============================================================================
class CAFF_HostContractProps(PropertyGroup):
    """Contrato obrigatório fornecido pelo addon host onde o construtor se integra."""
    host_conectado: BoolProperty(
        name="Addon Host Conectado",
        default=True,
        description="Indica se o addon principal forneceu o contrato de chapas e montagem",
    )
    chapa_max_comp: FloatProperty(
        name="Chapa Máx. Comprimento (mm)",
        default=2750.0, min=600.0, max=4000.0,
        description="Comprimento máximo da chapa MDF para não extrapolar no corte",
    )
    chapa_max_larg: FloatProperty(
        name="Chapa Máx. Largura (mm)",
        default=1830.0, min=600.0, max=3000.0,
        description="Largura máxima da chapa MDF para não extrapolar no corte",
    )
    bloquear_extrapolacao: BoolProperty(
        name="Bloquear se Extrapolar Chapa",
        default=False,
        description="Se ativo, impede gerar peças maiores que a chapa máxima",
    )
    esp_lateral_esq: EnumProperty(name="Lateral Esq.", items=THICKNESS_ITEMS, default='15')
    esp_lateral_dir: EnumProperty(name="Lateral Dir.", items=THICKNESS_ITEMS, default='15')
    esp_base_inf: EnumProperty(name="Base Inf.", items=THICKNESS_ITEMS, default='15')
    esp_base_sup: EnumProperty(name="Base Sup.", items=THICKNESS_ITEMS, default='15')
    esp_divisoria: EnumProperty(name="Divisória", items=THICKNESS_ITEMS, default='15')
    esp_prateleira: EnumProperty(name="Prateleira", items=THICKNESS_ITEMS, default='15')
    esp_fundo: EnumProperty(name="Fundo", items=THICKNESS_ITEMS, default='6')
    esp_gaveta: EnumProperty(name="Gaveta", items=THICKNESS_ITEMS, default='15')


def apply_host_contract(scene, config: dict):
    """API pública para o addon host injetar padrões de chapa e montagem."""
    hc = scene.caff_host_contract
    p = scene.caff_armario
    hc.host_conectado = True
    if "max_sheet_length" in config:
        hc.chapa_max_comp = float(config["max_sheet_length"])
    if "max_sheet_width" in config:
        hc.chapa_max_larg = float(config["max_sheet_width"])
    th_map = config.get("default_thickness", {})
    for src_key, dst_attr in (
        ("lateralEsq", "esp_lateral_esq"),
        ("lateralDir", "esp_lateral_dir"),
        ("baseInf", "esp_base_inf"),
        ("baseSup", "esp_base_sup"),
        ("divisoria", "esp_divisoria"),
        ("prateleira", "esp_prateleira"),
        ("fundo", "esp_fundo"),
        ("gaveta", "esp_gaveta"),
    ):
        if src_key in th_map and str(int(th_map[src_key])) in {'6', '15', '18', '25'}:
            setattr(hc, dst_attr, str(int(th_map[src_key])))
    if config.get("default_assembly") in {'BASE_PASSANTE', 'LATERAL_PASSANTE'}:
        p.tipo_montagem = config["default_assembly"]
    if config.get("default_contra_frente_orient") in {'EM_PE', 'DEITADA'}:
        p.orient_contra_frente = config["default_contra_frente_orient"]
    if config.get("default_traseira_orient") in {'EM_PE', 'DEITADA'}:
        p.orient_traseira = config["default_traseira_orient"]


def validate_part_against_sheet(hc, name, dim_a_mm, dim_b_mm, violations):
    max_l = max(hc.chapa_max_comp, hc.chapa_max_larg)
    max_w = min(hc.chapa_max_comp, hc.chapa_max_larg)
    p_l = max(dim_a_mm, dim_b_mm)
    p_w = min(dim_a_mm, dim_b_mm)
    if p_l > max_l or p_w > max_w:
        violations.append(f"{name} ({p_l:.0f}x{p_w:.0f}mm > {max_l:.0f}x{max_w:.0f}mm)")


# ============================================================================
# PROPRIEDADES DO CONSTRUTOR DE ARMÁRIOS
# ============================================================================
class CAFF_DrawerItemProps(PropertyGroup):
    modelo_frente: EnumProperty(
        name="Frente",
        items=DRAWER_MODEL_ITEMS,
        default='s_cf_reta',
    )


def _sync_drawer_items(self, context):
    target = max(0, int(self.gavetas_qtd))
    while len(self.gavetas_lista) < target:
        item = self.gavetas_lista.add()
        item.modelo_frente = self.gaveta_modelo_padrao
    while len(self.gavetas_lista) > target:
        self.gavetas_lista.remove(len(self.gavetas_lista) - 1)


def _apply_default_drawer_model(self, context):
    for item in self.gavetas_lista:
        item.modelo_frente = self.gaveta_modelo_padrao


class CAFF_ArmarioProps(PropertyGroup):
    aba: EnumProperty(
        name="Aba",
        items=[
            ('ESTRUTURA', "Estrutura", "Estrutura e montagem"),
            ('DIVISOES', "Divisões", "Divisórias e prateleiras"),
            ('GAVETAS', "Gavetas", "Editor de gavetas e corrediças"),
            ('INTERNOS', "Internos", "Cabideiro, maleiro e internos"),
            ('PORTAS', "Portas", "Portas de abrir"),
            ('DESLIZANTES', "Deslizantes", "Portas deslizantes e trilhos"),
            ('FUNDOS', "Fundos", "Painel traseiro"),
        ],
        default='ESTRUTURA',
    )

    # Dimensões gerais (mm)
    largura: FloatProperty(name="Largura total (mm)", default=1000.0, min=200.0, max=6000.0)
    altura: FloatProperty(name="Altura (mm)", default=2400.0, min=200.0, max=4000.0)
    profundidade: FloatProperty(name="Profundidade (mm)", default=510.0, min=150.0, max=1500.0)

    # Montagem e orientação de travessas
    tipo_montagem: EnumProperty(
        name="Tipo de montagem",
        items=[
            ('LATERAL_PASSANTE', "Lateral passante", "Laterais vão do piso ao topo"),
            ('BASE_PASSANTE', "Base passante", "Bases inferior e superior cobrem as laterais"),
        ],
        default='LATERAL_PASSANTE',
    )
    orient_contra_frente: EnumProperty(
        name="Contra-frente",
        items=[('EM_PE', "Em pé", "Vertical"), ('DEITADA', "Deitada", "Horizontal")],
        default='EM_PE',
    )
    orient_traseira: EnumProperty(
        name="Peça de trás",
        items=[('EM_PE', "Em pé", "Vertical"), ('DEITADA', "Deitada", "Horizontal")],
        default='EM_PE',
    )

    # Componentes estruturais — INICIAM DESMARCADOS (janela vazia!)
    lateral_esq: BoolProperty(name="Lateral Esquerda", default=False)
    lateral_dir: BoolProperty(name="Lateral Direita", default=False)
    base_inf: BoolProperty(name="Base Inferior", default=False)
    base_sup: BoolProperty(name="Base Superior", default=False)
    fundo: BoolProperty(name="Fundo", default=False)
    contra_frente: BoolProperty(name="Contra-frente", default=False)
    travessa_traseira: BoolProperty(name="Travessa Traseira", default=False)
    rodape: BoolProperty(name="Rodapé", default=False)
    rodape_altura: FloatProperty(name="Altura rodapé (mm)", default=80.0, min=40.0, max=200.0)

    # Divisões
    div_verticais: IntProperty(name="Divisórias verticais", default=0, min=0, max=10)
    prateleiras: IntProperty(name="Prateleiras por vão", default=0, min=0, max=15)
    passo_mm: FloatProperty(name="Passo (mm)", default=10.0, min=1.0, max=100.0)

    # Gavetas
    gavetas_vao: IntProperty(name="Vão das gavetas", default=1, min=1, max=12)
    gavetas_qtd: IntProperty(name="Quantidade de gavetas", default=0, min=0, max=12, update=_sync_drawer_items)
    gavetas_altura_bloco: FloatProperty(name="Altura do bloco (mm)", default=760.0, min=150.0, max=2200.0)
    gaveta_modelo_padrao: EnumProperty(
        name="Frente (todas)",
        items=DRAWER_MODEL_ITEMS,
        default='s_cf_reta',
        update=_apply_default_drawer_model,
    )
    gavetas_lista: CollectionProperty(type=CAFF_DrawerItemProps)
    gaveta_usar_corredica_3d: BoolProperty(
        name="Corrediça 3D (ST48-0200)",
        default=True,
        description="Importa slide-st48-0200-0.obj vinculando trilho externo na lateral e interno na gaveta",
    )
    gaveta_separador: BoolProperty(name="Separador de gaveta", default=False)
    gaveta_sep_cols: IntProperty(name="Colunas separador", default=3, min=2, max=6)
    gaveta_sep_rows: IntProperty(name="Linhas separador", default=2, min=1, max=5)
    afastador_fe: BoolProperty(name="Frontal Esq.", default=True)
    afastador_fd: BoolProperty(name="Frontal Dir.", default=True)
    afastador_te: BoolProperty(name="Traseiro Esq.", default=True)
    afastador_td: BoolProperty(name="Traseiro Dir.", default=True)

    # Internos
    cabideiro: BoolProperty(name="Cabideiro no vão", default=False)

    # Portas de abrir
    portas_abrir: BoolProperty(name="Portas de abrir", default=False)
    portas_abrir_qtd: IntProperty(name="Folhas abrir", default=2, min=1, max=6)

    # Porta Deslizante
    deslizante_ativa: BoolProperty(name="Ativar Porta Deslizante", default=False)
    deslizante_pos_base: EnumProperty(
        name="Posição das Bases",
        items=[
            ('DENTRO', "Dentro do armário (recua internos)",
             "Bases inferior/superior dentro do armário; divisórias, prateleiras e gavetas recuam automaticamente"),
            ('FRENTE', "Na frente do armário (sem recuo)",
             "Trilhos na frente do armário sem redimensionar nenhuma peça interna"),
        ],
        default='DENTRO',
    )
    deslizante_esp_base: FloatProperty(
        name="Espessura base desl. (mm)", default=18.0, min=12.0, max=40.0
    )
    deslizante_prof_trilho: FloatProperty(
        name="Profundidade trilho/recuo (mm)", default=70.0, min=40.0, max=120.0
    )
    deslizante_material: EnumProperty(
        name="Tipo de porta",
        items=[
            ('MDF_AMADEIRADO', "MDF Amadeirado", "Painel MDF amadeirado"),
            ('VIDRO', "Vidro", "Folha de vidro translúcido"),
            ('ALUMINIO', "Alumínio", "Perfil/folha de alumínio"),
        ],
        default='MDF_AMADEIRADO',
    )
    deslizante_folhas: IntProperty(name="Folhas deslizantes", default=2, min=2, max=4)
    deslizante_sobreposicao: FloatProperty(name="Sobreposição (mm)", default=30.0, min=10.0, max=80.0)

    # Fundos
    fundo_fixacao: EnumProperty(
        name="Fixação fundo",
        items=[('ENCAIXADO', "Encaixado em canal", ""), ('SOBREPOSTO', "Sobreposto", "")],
        default='ENCAIXADO',
    )
    fundo_recuo: FloatProperty(name="Recuo fundo (mm)", default=10.0, min=0.0, max=30.0)

    acabamento: EnumProperty(
        name="Acabamento",
        items=[('MADEIRA', "Madeirado", ""), ('BRANCO', "Branco", ""), ('CINZA', "Cinza", ""), ('PRETO', "Preto", "")],
        default='MADEIRA',
    )
    mostrar_cotas: BoolProperty(name="Mostrar cotas no nome", default=True)


# ============================================================================
# IMPORTAÇÃO DA CORREDIÇA 3D (slide-st48-0200-0.obj) COM CINEMÁTICA TELESCÓPICA
# ============================================================================
def attach_drawer_slide_3d(col, slide_mat, cabinet_parent, drawer_parent, side_sign, x_wall, y_front, z_center, box_depth_m):
    """
    Importa slide-st48-0200-0.obj (nativo em mm: X=[0..9.1], Y=[-17.5..17.5], Z=[0..200]).
    Mapeamento real das 4 peças do OBJ:
      - _1: Trilho externo -> fixado na lateral do armário (cabinet_parent, travel=0.0)
      - _2: Trilho interno -> fixado na lateral da gaveta (drawer_parent, travel=1.0)
      - _3 e _4: Gaiolas de esferas -> vinculadas ao armário com travel=0.5 (cinemática telescópica)
    side_sign: -1 para lado esquerdo (parede à esquerda), +1 para lado direito (parede à direita).
    """
    path = slide_obj_path()
    imported = []
    if os.path.exists(path):
        before = set(bpy.data.objects)
        try:
            bpy.ops.wm.obj_import(filepath=path)
            imported = [o for o in bpy.data.objects if o not in before]
        except Exception:
            imported = []

    length_scale = max(0.5, box_depth_m / 0.200)  # nativo 200mm -> box_depth_m
    mm_scale = 0.001

    if not imported:
        # Fallback geométrico fiel se OBJ não estiver presente
        outer = add_box(col, f"Corredica_Ext_{'E' if side_sign < 0 else 'D'}",
                        (x_wall - side_sign * mm(4.2), y_front + box_depth_m / 2, z_center),
                        (mm(8.5), box_depth_m, mm(35.0)), slide_mat, parent=cabinet_parent, bevel_mm=0.0)
        inner = add_box(col, f"Corredica_Int_{'E' if side_sign < 0 else 'D'}",
                        (x_wall - side_sign * mm(9.0), y_front + box_depth_m / 2, z_center),
                        (mm(6.0), box_depth_m * 0.9, mm(20.0)), slide_mat, parent=drawer_parent, bevel_mm=0.0)
        if outer:
            outer["caff_slide_part"] = "OUTER"
        if inner:
            inner["caff_slide_part"] = "INNER"
        return []

    cage_objs = []
    for obj in imported:
        link_only_to_collection(obj, col)
        if slide_mat:
            obj.data.materials.clear()
            obj.data.materials.append(slide_mat)

        # Converter de mm para metros e orientar Z(comprimento) -> +Y(profundidade)
        sx = mm_scale * (-side_sign)  # X=0 encosta na parede, X=+9.1 aponta para a gaveta
        obj.scale = (sx, mm_scale, mm_scale * length_scale)
        obj.rotation_euler = (-math.pi / 2.0, 0.0, 0.0)
        obj.location = (x_wall, y_front, z_center)

        lname = obj.name.lower()
        if lname.endswith("_1") or "_1." in lname:
            obj.name = f"Corredica_Externa_Lateral_{'E' if side_sign < 0 else 'D'}"
            obj.parent = cabinet_parent
            obj.matrix_parent_inverse = cabinet_parent.matrix_world.inverted()
            obj["caff_slide_part"] = "OUTER"
        elif lname.endswith("_2") or "_2." in lname:
            obj.name = f"Corredica_Interna_Gaveta_{'E' if side_sign < 0 else 'D'}"
            obj.parent = drawer_parent
            obj.matrix_parent_inverse = drawer_parent.matrix_world.inverted()
            obj["caff_slide_part"] = "INNER"
        else:
            obj.name = f"Corredica_Gaiola_Esferas_{'E' if side_sign < 0 else 'D'}"
            obj.parent = cabinet_parent
            obj.matrix_parent_inverse = cabinet_parent.matrix_world.inverted()
            obj["caff_slide_part"] = "CAGE"
            obj["caff_closed_y"] = obj.location.y
            cage_objs.append(obj)

    return cage_objs


# ============================================================================
# OPERADOR PRINCIPAL: GERAR / ATUALIZAR ARMÁRIO
# ============================================================================
class CAFF_OT_gerar(Operator):
    bl_idname = "caff.gerar_armario"
    bl_label = "Gerar / Atualizar Armário"
    bl_description = "Constrói a geometria paramétrica do armário validando o contrato de chapas"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        p = context.scene.caff_armario
        hc = context.scene.caff_host_contract

        if not hc.host_conectado:
            self.report({'ERROR'}, "Contrato do addon host não configurado (espessuras e chapa máxima obrigatórios).")
            return {'CANCELLED'}

        if not any((p.lateral_esq, p.lateral_dir, p.base_inf, p.base_sup, p.fundo)):
            col = ensure_collection()
            clear_collection(col)
            self.report({'INFO'}, "Armário vazio: ative Laterais/Bases na aba Estrutura.")
            return {'FINISHED'}

        t_le = float(hc.esp_lateral_esq)
        t_ld = float(hc.esp_lateral_dir)
        t_bi = float(hc.esp_base_inf)
        t_bs = float(hc.esp_base_sup)
        t_div = float(hc.esp_divisoria)
        t_pr = float(hc.esp_prateleira)
        t_fu = float(hc.esp_fundo)
        t_gv = float(hc.esp_gaveta)

        # Validação prévia contra chapa máxima
        violations = []
        base_passante = (p.tipo_montagem == 'BASE_PASSANTE')
        rod_h = p.rodape_altura if p.rodape else 0.0
        lat_h = p.altura - rod_h - ((t_bi if p.base_inf else 0.0) + (t_bs if p.base_sup else 0.0) if base_passante else 0.0)
        base_w = p.largura if base_passante else p.largura - (t_le if p.lateral_esq else 0.0) - (t_ld if p.lateral_dir else 0.0)

        if p.lateral_esq:
            validate_part_against_sheet(hc, "Lateral Esquerda", p.profundidade, lat_h, violations)
        if p.lateral_dir:
            validate_part_against_sheet(hc, "Lateral Direita", p.profundidade, lat_h, violations)
        if p.base_inf:
            validate_part_against_sheet(hc, "Base Inferior", base_w, p.profundidade, violations)
        if p.base_sup:
            validate_part_against_sheet(hc, "Base Superior", base_w, p.profundidade, violations)
        if p.fundo:
            validate_part_against_sheet(hc, "Fundo", p.largura, p.altura - rod_h, violations)

        if violations and hc.bloquear_extrapolacao:
            self.report({'ERROR'}, "Extrapola chapa máxima: " + "; ".join(violations[:3]))
            return {'CANCELLED'}

        col = ensure_collection()
        clear_collection(col)

        W, H, D = mm(p.largura), mm(p.altura), mm(p.profundidade)
        rod_m = mm(rod_h)
        front_y = -D / 2.0
        back_y = D / 2.0

        palettes = {
            'MADEIRA': ((0.43, 0.25, 0.12), (0.66, 0.48, 0.29)),
            'BRANCO': ((0.78, 0.80, 0.82), (0.90, 0.91, 0.92)),
            'CINZA': ((0.27, 0.29, 0.31), (0.48, 0.50, 0.52)),
            'PRETO': ((0.05, 0.055, 0.06), (0.18, 0.19, 0.20)),
        }
        core_col, front_col = palettes[p.acabamento]
        mat_box = make_pbr_material("CAFF_Caixa", core_col, roughness=0.58)
        mat_front = make_pbr_material("CAFF_Frente", front_col, roughness=0.45)
        mat_metal = make_pbr_material("CAFF_Corredica_Metal", (0.72, 0.74, 0.77), roughness=0.25, metallic=0.92)
        mat_glass = make_pbr_material("CAFF_Vidro", (0.75, 0.88, 0.96), roughness=0.06, transmission=0.82, alpha=0.45)
        mat_alu = make_pbr_material("CAFF_Aluminio", (0.76, 0.79, 0.82), roughness=0.28, metallic=0.88)

        root = add_empty(col, "CAFF_Armario_Root", (0.0, 0.0, 0.0))
        root["caff_is_cabinet_root"] = True

        x_in_l = -W / 2.0 + (mm(t_le) if p.lateral_esq else 0.0)
        x_in_r = W / 2.0 - (mm(t_ld) if p.lateral_dir else 0.0)
        inner_w = max(0.05, x_in_r - x_in_l)
        z_in_b = rod_m + (mm(t_bi) if p.base_inf else 0.0)
        z_in_t = H - (mm(t_bs) if p.base_sup else 0.0)
        inner_h = max(0.05, z_in_t - z_in_b)

        # Recuo automático dos internos se porta deslizante tiver base DENTRO
        sliding_recede = mm(p.deslizante_prof_trilho) if (p.deslizante_ativa and p.deslizante_pos_base == 'DENTRO') else 0.0
        back_thick = mm(t_fu) if p.fundo else 0.0
        back_offset = mm(p.fundo_recuo) if (p.fundo and p.fundo_fixacao == 'ENCAIXADO') else 0.0
        usable_d = max(mm(80.0), D - back_thick - back_offset - sliding_recede)
        internal_y_front = front_y + sliding_recede
        internal_y_center = internal_y_front + usable_d / 2.0

        def make_panel(name, x, y, z, dx, dy, dz, mat=mat_box, parent=root, role="STRUCT"):
            lbl = f"{name} ({dx*1000:.0f}x{dy*1000:.0f}x{dz*1000:.0f}mm)" if p.mostrar_cotas else name
            o = add_box(col, lbl, (x, y, z), (dx, dy, dz), mat, parent=parent)
            if o:
                o["caff_role"] = role
            return o

        # 1. Estrutura externa (NUNCA recua com porta deslizante!)
        lat_z_center = rod_m + (mm(t_bi) if (base_passante and p.base_inf) else 0.0) + mm(lat_h) / 2.0
        if p.lateral_esq:
            make_panel("Lateral Esquerda", -W / 2.0 + mm(t_le) / 2.0, 0.0, lat_z_center, mm(t_le), D, mm(lat_h))
        if p.lateral_dir:
            make_panel("Lateral Direita", W / 2.0 - mm(t_ld) / 2.0, 0.0, lat_z_center, mm(t_ld), D, mm(lat_h))
        if p.base_inf:
            bx = 0.0 if base_passante else (x_in_l + x_in_r) / 2.0
            make_panel("Base Inferior", bx, 0.0, rod_m + mm(t_bi) / 2.0, mm(base_w), D, mm(t_bi))
        if p.base_sup:
            bx = 0.0 if base_passante else (x_in_l + x_in_r) / 2.0
            make_panel("Base Superior", bx, 0.0, H - mm(t_bs) / 2.0, mm(base_w), D, mm(t_bs))
        if p.rodape:
            make_panel("Rodape", 0.0, front_y + mm(35.0), rod_m / 2.0, W, mm(18.0), rod_m)
        if p.fundo:
            fy = back_y - back_offset - back_thick / 2.0
            make_panel("Fundo", 0.0, fy, rod_m + (H - rod_m) / 2.0, W, back_thick, H - rod_m)

        # Contra-frente e Travessa traseira (Em pé ou Deitada)
        if p.contra_frente:
            em_pe = (p.orient_contra_frente == 'EM_PE')
            dy = mm(t_bs) if em_pe else mm(90.0)
            dz = mm(90.0) if em_pe else mm(t_bs)
            make_panel("Contra-frente", (x_in_l + x_in_r) / 2.0, internal_y_front + dy / 2.0, z_in_t - dz / 2.0, inner_w, dy, dz)
        if p.travessa_traseira:
            em_pe = (p.orient_traseira == 'EM_PE')
            dy = mm(t_bs) if em_pe else mm(90.0)
            dz = mm(90.0) if em_pe else mm(t_bs)
            make_panel("Travessa Traseira", (x_in_l + x_in_r) / 2.0, back_y - back_offset - back_thick - dy / 2.0, z_in_t - dz / 2.0, inner_w, dy, dz)

        # 2. Divisórias verticais e prateleiras (recuam automaticamente quando deslizante DENTRO!)
        n_bays = p.div_verticais + 1
        bay_w = inner_w / n_bays
        for i in range(1, n_bays):
            vx = x_in_l + bay_w * i
            o = make_panel(f"Divisoria Vertical {i}", vx, internal_y_center, (z_in_b + z_in_t) / 2.0, mm(t_div), usable_d, inner_h, role="VDIV")
            if o:
                o["caff_bay_min_x"] = x_in_l
                o["caff_bay_max_x"] = x_in_r

        for b in range(n_bays):
            cx = x_in_l + bay_w * (b + 0.5)
            for j in range(p.prateleiras):
                pz = z_in_b + inner_h * (j + 1) / (p.prateleiras + 1)
                o = make_panel(f"Prateleira V{b+1}-{j+1}", cx, internal_y_center, pz, bay_w - mm(t_div) * 0.5, usable_d, mm(t_pr), role="SHELF")
                if o:
                    o["caff_bay_min_z"] = z_in_b
                    o["caff_bay_max_z"] = z_in_t
            if p.cabideiro and b == 0:
                bpy.ops.mesh.primitive_cylinder_add(radius=mm(12.0), depth=bay_w - mm(20.0), location=(cx, internal_y_center, z_in_t - mm(260.0)), rotation=(0.0, math.pi / 2.0, 0.0))
                rod = bpy.context.object
                rod.name = "Cabideiro"
                link_only_to_collection(rod, col)
                rod.data.materials.append(mat_alu)
                rod.parent = root
                rod.matrix_parent_inverse = root.matrix_world.inverted()

        # 3. Editor de Gavetas + Corrediça 3D ST48-0200 + Separador Interno
        if p.gavetas_qtd > 0:
            _sync_drawer_items(p, context)
            target_bay = max(0, min(n_bays - 1, p.gavetas_vao - 1))
            bx0 = x_in_l + bay_w * target_bay + mm(t_div * 0.5 if target_bay > 0 else 0.0)
            bx1 = x_in_l + bay_w * (target_bay + 1) - mm(t_div * 0.5 if target_bay < n_bays - 1 else 0.0)
            bw = max(mm(120.0), bx1 - bx0)
            bcx = (bx0 + bx1) / 2.0
            gap = mm(3.0)
            block_h = min(inner_h, mm(p.gavetas_altura_bloco))
            each_h = (block_h - gap * (p.gavetas_qtd + 1)) / p.gavetas_qtd
            box_d = min(usable_d - mm(30.0), mm(450.0))
            slide_clearance = mm(12.7)  # folga padrão corrediça telescópica
            box_w = max(mm(80.0), bw - 2 * slide_clearance)
            travel_m = box_d * 0.72

            for idx in range(p.gavetas_qtd):
                z0 = z_in_b + gap + idx * (each_h + gap)
                zc = z0 + each_h / 2.0
                model_id = p.gavetas_lista[idx].modelo_frente if idx < len(p.gavetas_lista) else p.gaveta_modelo_padrao
                is_glass = "vidro" in model_id
                has_cf = model_id.startswith("c_cf")

                dr_pivot = add_empty(col, f"Gaveta_{idx+1}_Assembly", (bcx, internal_y_front, zc), parent=root)
                dr_pivot["caff_anim_role"] = "DRAWER"
                dr_pivot["caff_is_open"] = False
                dr_pivot["caff_closed_y"] = internal_y_front
                dr_pivot["caff_travel_m"] = travel_m

                # Frente da gaveta
                f_mat = mat_glass if is_glass else mat_front
                make_panel(f"Gaveta_{idx+1}_Frente_{model_id}", bcx, internal_y_front + mm(t_gv) / 2.0, zc, bw - mm(4.0), mm(t_gv), each_h, f_mat, parent=dr_pivot, role="DRAWER_PART")
                # Caixa da gaveta (laterais, traseira, fundo e contra-frente opcional)
                box_h = max(mm(50.0), each_h - mm(30.0))
                box_yc = internal_y_front + mm(t_gv) + box_d / 2.0
                make_panel(f"Gaveta_{idx+1}_LatEsq", bcx - box_w / 2.0 + mm(t_gv) / 2.0, box_yc, zc, mm(t_gv), box_d, box_h, mat_box, parent=dr_pivot, role="DRAWER_PART")
                make_panel(f"Gaveta_{idx+1}_LatDir", bcx + box_w / 2.0 - mm(t_gv) / 2.0, box_yc, zc, mm(t_gv), box_d, box_h, mat_box, parent=dr_pivot, role="DRAWER_PART")
                make_panel(f"Gaveta_{idx+1}_Traseira", bcx, internal_y_front + mm(t_gv) + box_d - mm(t_gv) / 2.0, zc, box_w - 2 * mm(t_gv), mm(t_gv), box_h, mat_box, parent=dr_pivot, role="DRAWER_PART")
                make_panel(f"Gaveta_{idx+1}_Fundo", bcx, box_yc, zc - box_h / 2.0 + mm(t_fu) / 2.0, box_w - mm(10.0), box_d - mm(10.0), mm(t_fu), mat_box, parent=dr_pivot, role="DRAWER_PART")
                if has_cf:
                    make_panel(f"Gaveta_{idx+1}_ContraFrente", bcx, internal_y_front + mm(t_gv) * 1.5, zc, box_w - 2 * mm(t_gv), mm(t_gv), box_h, mat_box, parent=dr_pivot, role="DRAWER_PART")

                # Separador interno de gaveta
                if p.gaveta_separador:
                    sep_h = box_h * 0.65
                    inner_bw = box_w - 2 * mm(t_gv)
                    inner_bd = box_d - 2 * mm(t_gv)
                    for c in range(1, p.gaveta_sep_cols):
                        sx = bcx - inner_bw / 2.0 + inner_bw * c / p.gaveta_sep_cols
                        make_panel(f"Gaveta_{idx+1}_SepCol_{c}", sx, box_yc, zc - mm(8.0), mm(6.0), inner_bd, sep_h, mat_box, parent=dr_pivot, role="DRAWER_PART")
                    for r in range(1, p.gaveta_sep_rows):
                        sy = internal_y_front + mm(t_gv) + inner_bd * r / p.gaveta_sep_rows
                        make_panel(f"Gaveta_{idx+1}_SepLin_{r}", bcx, sy, zc - mm(8.0), inner_bw, mm(6.0), sep_h, mat_box, parent=dr_pivot, role="DRAWER_PART")

                # Corrediças 3D (slide-st48-0200-0.obj): Esquerda e Direita
                if p.gaveta_usar_corredica_3d:
                    cages_l = attach_drawer_slide_3d(col, mat_metal, root, dr_pivot, -1, bx0, internal_y_front + mm(t_gv), zc, box_d)
                    cages_r = attach_drawer_slide_3d(col, mat_metal, root, dr_pivot, +1, bx1, internal_y_front + mm(t_gv), zc, box_d)
                    dr_pivot["caff_cage_names"] = json.dumps([o.name for o in (cages_l + cages_r)])

        # 4. Porta Deslizante (DENTRO vs NA FRENTE + espessura base + MDF/Vidro/Alumínio)
        if p.deslizante_ativa:
            is_inside = (p.deslizante_pos_base == 'DENTRO')
            track_d = mm(p.deslizante_prof_trilho)
            base_th = mm(p.deslizante_esp_base)
            rail_w = inner_w if is_inside else W
            rail_cx = (x_in_l + x_in_r) / 2.0 if is_inside else 0.0
            rail_y = (front_y + track_d / 2.0) if is_inside else (front_y - track_d / 2.0)
            z_bot_base = (z_in_b + base_th / 2.0) if is_inside else (rod_m + base_th / 2.0)
            z_top_base = (z_in_t - base_th / 2.0) if is_inside else (H - base_th / 2.0)

            make_panel(f"Base_Inf_Deslizante_{p.deslizante_pos_base}", rail_cx, rail_y, z_bot_base, rail_w, track_d, base_th, mat_alu)
            make_panel(f"Base_Sup_Deslizante_{p.deslizante_pos_base}", rail_cx, rail_y, z_top_base, rail_w, track_d, base_th, mat_alu)

            sd_mat = mat_glass if p.deslizante_material == 'VIDRO' else (mat_alu if p.deslizante_material == 'ALUMINIO' else mat_front)
            n_leaves = p.deslizante_folhas
            ov = mm(p.deslizante_sobreposicao)
            leaf_w = (rail_w + ov * (n_leaves - 1)) / n_leaves
            leaf_h = max(mm(100.0), (z_top_base - z_bot_base) - base_th - mm(8.0))
            leaf_zc = (z_bot_base + z_top_base) / 2.0
            step_x = (rail_w - leaf_w) / max(1, n_leaves - 1)
            x_start = rail_cx - rail_w / 2.0 + leaf_w / 2.0

            for i in range(n_leaves):
                lx = x_start + i * step_x
                ly = rail_y + (mm(-14.0) if i % 2 == 0 else mm(14.0))
                leaf = make_panel(f"Porta_Deslizante_{i+1}_{p.deslizante_material}", lx, ly, leaf_zc, leaf_w, mm(18.0), leaf_h, sd_mat, role="SLIDING_DOOR")
                if leaf:
                    leaf["caff_anim_role"] = "SLIDING_DOOR"
                    leaf["caff_is_open"] = False
                    leaf["caff_closed_x"] = lx
                    leaf["caff_slide_dx"] = (leaf_w * 0.80) * (1.0 if i == 0 else -1.0)

        # 5. Portas de Abrir
        elif p.portas_abrir:
            gap = mm(3.0)
            nd = p.portas_abrir_qtd
            dw = (W - gap * (nd + 1)) / nd
            dh = H - rod_m - mm(4.0)
            for i in range(nd):
                hinge_left = (i % 2 == 0)
                x0 = -W / 2.0 + gap + i * (dw + gap)
                px = x0 if hinge_left else x0 + dw
                piv = add_empty(col, f"Porta_Abrir_{i+1}_Dobradica", (px, front_y - mm(10.0), rod_m + dh / 2.0), parent=root)
                piv["caff_anim_role"] = "HINGED_DOOR"
                piv["caff_is_open"] = False
                piv["caff_hinge_sign"] = -1.0 if hinge_left else 1.0
                make_panel(f"Porta_Abrir_{i+1}", x0 + dw / 2.0, front_y - mm(10.0), rod_m + dh / 2.0, dw, mm(18.0), dh, mat_front, parent=piv, role="HINGED_PART")

        if violations:
            self.report({'WARNING'}, "Armário gerado, mas peças extrapolam chapa máxima: " + "; ".join(violations[:2]))
        else:
            self.report({'INFO'}, f"Armário CAFF MOB gerado ({p.largura:.0f}x{p.altura:.0f}x{p.profundidade:.0f}mm)")
        return {'FINISHED'}


# ============================================================================
# OPERADORES AUXILIARES: MONTAGEM RÁPIDA, LIMPAR, DUPLICAR VÃO LIVRE, ABRIR/FECHAR
# ============================================================================
class CAFF_OT_montar_caixa(Operator):
    bl_idname = "caff.montar_caixa_padrao"
    bl_label = "Montar Caixa Padrão"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        p = context.scene.caff_armario
        p.lateral_esq = True
        p.lateral_dir = True
        p.base_inf = True
        p.base_sup = True
        p.fundo = True
        bpy.ops.caff.gerar_armario()
        return {'FINISHED'}


class CAFF_OT_limpar(Operator):
    bl_idname = "caff.limpar_armario"
    bl_label = "Limpar (Janela Vazia)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        p = context.scene.caff_armario
        p.lateral_esq = False
        p.lateral_dir = False
        p.base_inf = False
        p.base_sup = False
        p.fundo = False
        p.contra_frente = False
        p.travessa_traseira = False
        p.gavetas_qtd = 0
        p.deslizante_ativa = False
        p.portas_abrir = False
        col = bpy.data.collections.get(COLLECTION_NAME)
        if col:
            clear_collection(col)
        return {'FINISHED'}


def find_animatable_target(obj):
    cur = obj
    while cur is not None:
        if cur.get("caff_anim_role") in {"DRAWER", "SLIDING_DOOR", "HINGED_DOOR"}:
            return cur
        cur = cur.parent
    return None


class CAFF_OT_toggle_abrir_fechar(Operator):
    """Anima suavemente a abertura/fechamento de gavetas (com corrediça ST48-0200) e portas."""
    bl_idname = "caff.toggle_abrir_fechar"
    bl_label = "Abrir / Fechar"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _target = None
    _step = 0
    _steps = 18
    _opening = True

    def execute(self, context):
        target = find_animatable_target(context.active_object)
        if target is None:
            self.report({'WARNING'}, "Selecione uma gaveta ou porta do armário CAFF MOB.")
            return {'CANCELLED'}
        self._target = target
        self._opening = not bool(target.get("caff_is_open", False))
        self._step = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.016, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _apply_progress(self, t: float):
        obj = self._target
        role = obj.get("caff_anim_role")
        # Ease in-out cubic
        e = t * t * (3.0 - 2.0 * t)
        if role == "DRAWER":
            closed_y = float(obj.get("caff_closed_y", obj.location.y))
            travel = float(obj.get("caff_travel_m", 0.30))
            obj.location.y = closed_y - travel * e
            # Move ball-bearing cages at 50% stroke!
            cage_names = json.loads(obj.get("caff_cage_names", "[]"))
            for cname in cage_names:
                cobj = bpy.data.objects.get(cname)
                if cobj:
                    c_closed = float(cobj.get("caff_closed_y", cobj.location.y))
                    cobj.location.y = c_closed - (travel * 0.5) * e
        elif role == "SLIDING_DOOR":
            closed_x = float(obj.get("caff_closed_x", obj.location.x))
            dx = float(obj.get("caff_slide_dx", 0.35))
            obj.location.x = closed_x + dx * e
        elif role == "HINGED_DOOR":
            sign = float(obj.get("caff_hinge_sign", -1.0))
            obj.rotation_euler.z = sign * math.radians(95.0) * e

    def modal(self, context, event):
        if event.type == 'TIMER':
            self._step += 1
            frac = min(1.0, self._step / self._steps)
            t = frac if self._opening else (1.0 - frac)
            self._apply_progress(t)
            if self._step >= self._steps:
                self._target["caff_is_open"] = self._opening
                context.window_manager.event_timer_remove(self._timer)
                return {'FINISHED'}
        return {'PASS_THROUGH'}


class CAFF_OT_duplicar_divisoria(Operator):
    """Duplica divisória vertical ou prateleira respeitando o vão livre disponível."""
    bl_idname = "caff.duplicar_divisoria"
    bl_label = "Duplicar Divisória (Respeitar Vão Livre)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.get("caff_role") not in {"VDIV", "SHELF"}:
            self.report({'WARNING'}, "Selecione uma divisória vertical ou prateleira.")
            return {'CANCELLED'}

        role = obj.get("caff_role")
        col = ensure_collection()
        min_clear = mm(80.0)

        if role == "VDIV":
            min_b = float(obj.get("caff_bay_min_x", -0.5))
            max_b = float(obj.get("caff_bay_max_x", 0.5))
            peers = sorted([o.location.x for o in col.objects if o.get("caff_role") == "VDIV"])
            idx = min(range(len(peers)), key=lambda i: abs(peers[i] - obj.location.x))
            left_b = min_b if idx == 0 else peers[idx - 1]
            right_b = max_b if idx == len(peers) - 1 else peers[idx + 1]
            free_r = right_b - obj.location.x
            free_l = obj.location.x - left_b
            if free_r >= min_clear and free_r >= free_l:
                new_x = (obj.location.x + right_b) / 2.0
            elif free_l >= min_clear:
                new_x = (left_b + obj.location.x) / 2.0
            else:
                self.report({'WARNING'}, "Vão livre insuficiente para duplicar esta divisória.")
                return {'CANCELLED'}
            dup = obj.copy()
            dup.data = obj.data.copy()
            dup.location.x = new_x
            col.objects.link(dup)
        else:
            min_b = float(obj.get("caff_bay_min_z", 0.0))
            max_b = float(obj.get("caff_bay_max_z", 2.0))
            peers = sorted([o.location.z for o in col.objects if o.get("caff_role") == "SHELF" and abs(o.location.x - obj.location.x) < 0.05])
            idx = min(range(len(peers)), key=lambda i: abs(peers[i] - obj.location.z))
            bot_b = min_b if idx == 0 else peers[idx - 1]
            top_b = max_b if idx == len(peers) - 1 else peers[idx + 1]
            free_t = top_b - obj.location.z
            free_b = obj.location.z - bot_b
            if free_t >= min_clear and free_t >= free_b:
                new_z = (obj.location.z + top_b) / 2.0
            elif free_b >= min_clear:
                new_z = (bot_b + obj.location.z) / 2.0
            else:
                self.report({'WARNING'}, "Vão vertical livre insuficiente para duplicar esta prateleira.")
                return {'CANCELLED'}
            dup = obj.copy()
            dup.data = obj.data.copy()
            dup.location.z = new_z
            col.objects.link(dup)

        self.report({'INFO'}, f"Peça duplicada respeitando o vão livre: {dup.name}")
        return {'FINISHED'}


# ============================================================================
# MENU DE CONTEXTO NA VIEWPORT 3D (BOTÃO DIREITO -> ABRIR / FECHAR DINÂMICO)
# ============================================================================
def draw_viewport_context_menu(self, context):
    obj = context.active_object
    if not obj:
        return
    layout = self.layout
    target = find_animatable_target(obj)
    if target is not None:
        is_open = bool(target.get("caff_is_open", False))
        layout.separator()
        # Mostra sempre o estado OPOSTO ao estado atual do objeto!
        label = "CAFF MOB: Fechar" if is_open else "CAFF MOB: Abrir"
        icon = 'TRIA_LEFT' if is_open else 'TRIA_RIGHT'
        layout.operator("caff.toggle_abrir_fechar", text=label, icon=icon)
    if obj.get("caff_role") in {"VDIV", "SHELF"}:
        layout.separator()
        layout.operator("caff.duplicar_divisoria", icon='DUPLICATE')


# ============================================================================
# PAINEL PRINCIPAL (INTERFACE ESPELHADA NO CONSTRUTOR DE ARMÁRIOS)
# ============================================================================
class CAFF_PT_main(Panel):
    bl_label = "Construtor de Armários"
    bl_idname = "CAFF_PT_construtor_armarios"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFF MOB"

    def draw(self, context):
        layout = self.layout
        p = context.scene.caff_armario
        hc = context.scene.caff_host_contract

        layout.prop(p, "aba", expand=True)
        layout.separator()

        if p.aba == 'ESTRUTURA':
            box = layout.box()
            box.label(text="Contrato Addon Host (Chapas)", icon='SETTINGS')
            row = box.row(align=True)
            row.prop(hc, "chapa_max_comp")
            row.prop(hc, "chapa_max_larg")
            box.prop(hc, "bloquear_extrapolacao")

            box = layout.box()
            box.label(text="Dimensões Gerais (mm)", icon='CUBE')
            col = box.column(align=True)
            col.prop(p, "largura")
            col.prop(p, "altura")
            col.prop(p, "profundidade")
            col.prop(p, "tipo_montagem")
            col.prop(p, "orient_contra_frente")
            col.prop(p, "orient_traseira")

            box = layout.box()
            box.label(text="Componentes Estruturais", icon='OUTLINER_OB_MESH')
            for prop_b, prop_t in (
                ("lateral_esq", "esp_lateral_esq"),
                ("lateral_dir", "esp_lateral_dir"),
                ("base_inf", "esp_base_inf"),
                ("base_sup", "esp_base_sup"),
                ("fundo", "esp_fundo"),
            ):
                row = box.row(align=True)
                row.prop(p, prop_b)
                row.prop(hc, prop_t, text="")
            row = box.row(align=True)
            row.prop(p, "contra_frente")
            row.prop(p, "travessa_traseira")
            row = box.row(align=True)
            row.prop(p, "rodape")
            if p.rodape:
                row.prop(p, "rodape_altura", text="Alt.")

        elif p.aba == 'DIVISOES':
            box = layout.box()
            box.label(text="Divisões Internas", icon='MOD_SOLIDIFY')
            box.prop(p, "div_verticais")
            box.prop(hc, "esp_divisoria")
            box.prop(p, "prateleiras")
            box.prop(hc, "esp_prateleira")
            box.prop(p, "passo_mm")
            box.operator("caff.duplicar_divisoria", icon='DUPLICATE')

        elif p.aba == 'GAVETAS':
            box = layout.box()
            box.label(text="Editor de Gavetas & Corrediça 3D", icon='MODIFIER')
            box.prop(p, "gavetas_vao")
            box.prop(p, "gavetas_qtd")
            box.prop(p, "gavetas_altura_bloco")
            box.prop(p, "gaveta_modelo_padrao")
            box.prop(p, "gaveta_usar_corredica_3d")
            box.prop(p, "gaveta_separador")
            if p.gaveta_separador:
                row = box.row(align=True)
                row.prop(p, "gaveta_sep_cols", text="Cols")
                row.prop(p, "gaveta_sep_rows", text="Lins")
            if len(p.gavetas_lista) > 0:
                sub = box.box()
                sub.label(text="Frente Individual por Gaveta:")
                for i, item in enumerate(p.gavetas_lista):
                    sub.prop(item, "modelo_frente", text=f"Gaveta {i+1}")

        elif p.aba == 'INTERNOS':
            box = layout.box()
            box.label(text="Componentes Internos", icon='MESH_CYLINDER')
            box.prop(p, "cabideiro")

        elif p.aba == 'PORTAS':
            box = layout.box()
            box.label(text="Portas de Abrir", icon='MESH_PLANE')
            box.prop(p, "portas_abrir")
            if p.portas_abrir:
                box.prop(p, "portas_abrir_qtd")
            box.prop(p, "acabamento")

        elif p.aba == 'DESLIZANTES':
            box = layout.box()
            box.label(text="Porta Deslizante", icon='ARROW_LEFTRIGHT')
            box.prop(p, "deslizante_ativa")
            box.prop(p, "deslizante_pos_base")
            box.prop(p, "deslizante_esp_base")
            box.prop(p, "deslizante_prof_trilho")
            box.prop(p, "deslizante_material")
            box.prop(p, "deslizante_folhas")
            box.prop(p, "deslizante_sobreposicao")

        elif p.aba == 'FUNDOS':
            box = layout.box()
            box.label(text="Painel Traseiro", icon='MESH_GRID')
            box.prop(p, "fundo")
            box.prop(hc, "esp_fundo")
            box.prop(p, "fundo_fixacao")
            box.prop(p, "fundo_recuo")

        layout.separator()
        row = layout.row(align=True)
        row.operator("caff.montar_caixa_padrao", icon='CUBE')
        row.operator("caff.limpar_armario", icon='TRASH')

        row = layout.row()
        row.scale_y = 1.4
        row.operator("caff.gerar_armario", icon='FILE_REFRESH')


classes = (
    CAFF_HostContractProps,
    CAFF_DrawerItemProps,
    CAFF_ArmarioProps,
    CAFF_OT_gerar,
    CAFF_OT_montar_caixa,
    CAFF_OT_limpar,
    CAFF_OT_toggle_abrir_fechar,
    CAFF_OT_duplicar_divisoria,
    CAFF_PT_main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.caff_host_contract = PointerProperty(type=CAFF_HostContractProps)
    bpy.types.Scene.caff_armario = PointerProperty(type=CAFF_ArmarioProps)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_viewport_context_menu)


def unregister():
    try:
        bpy.types.VIEW3D_MT_object_context_menu.remove(draw_viewport_context_menu)
    except Exception:
        pass
    if hasattr(bpy.types.Scene, "caff_armario"):
        del bpy.types.Scene.caff_armario
    if hasattr(bpy.types.Scene, "caff_host_contract"):
        del bpy.types.Scene.caff_host_contract
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
