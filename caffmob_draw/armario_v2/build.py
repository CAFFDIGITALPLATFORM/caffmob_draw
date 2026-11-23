"""Geração das malhas do armário v2 (feature 017, T020; RN-19, RN-24, D-02, RF-17).

`pecas` monta a lista de chapas em **milímetros** sem tocar no Blender: cada item traz papel, componente do Padrão de
Dimensões, nome, a caixa no referencial do armário, espessura, veio, fitas, `movel`, `curso` e eixo. `gerar` converte a
caixa para metros (divisão por 1000 num único ponto, `MM`) e cria uma malha por chapa na coleção do armário, filha da
raiz vazia, com `btm_armario_parte` preenchido — a fonte do corte (RN-24) e do alvo da animação (RN-10).

Referencial, o mesmo de `cabinet_editor.structure.layout`: X centrado na largura, Y de `−profundidade` (frente) a 0
(trás), Z de 0 (piso) a `altura`.

O `bpy`, o `bmesh` e o `mathutils` entram por import tardio, só nas funções que criam dados na cena: `pecas` — e o
módulo — continuam importáveis fora do Blender, e o teste puro da lista de chapas roda sem simular nada.

O fundo segue a fixação (RN-15): em canal fica entre as chapas da caixa e recua da face de trás sem consumir
profundidade; sobreposto usa as medidas externas. Os quatro acabamentos viram materiais próprios, com vidro e alumínio
em materiais separados (RF-17).
"""

from . import gavetas as gavetas_mod
from . import portas as portas_mod
from . import spec as spec_mod
from . import vaos as vaos_mod

MM = 0.001

COLECAO = "CAFFMob Armário v2"
RAIZ = "Armário v2"

# Componente do Padrão de Dimensões de cada papel (`data/dimension_schema.py`), para casar com o corte.
COMPONENTES = {
    'LATERAL': 'LAT',
    'BASE_INF': 'BAS',
    'BASE_SUP': 'BAS',
    'DIVISORIA': 'DIV',
    'PRATELEIRA': 'PRAT',
    'FUNDO': 'FUN_INF',
    'FRENTE_GAVETA': 'FRE_GAV_INT',
    'PORTA': 'POR',
    'FOLHA': 'POR',
}
FITA_FRENTE = (True, False, False, False)
SEM_FITA = (False, False, False, False)

ACABAMENTOS = {
    'MADEIRADO': (0.72, 0.53, 0.34, 1.0),
    'BRANCO': (0.92, 0.92, 0.90, 1.0),
    'CINZA': (0.52, 0.54, 0.56, 1.0),
    'PRETO': (0.05, 0.05, 0.06, 1.0),
}


def _peca(papel, nome, box, espessura, *, veio='NONE', fitas=SEM_FITA, material='CHAPA',
          movel=False, curso=0.0, eixo='Y'):
    return {'papel': papel, 'componente': COMPONENTES.get(papel, 'ESP'), 'nome': nome, 'box': box,
            'espessura': espessura, 'veio': veio, 'fitas': fitas, 'material': material,
            'movel': movel, 'curso': curso, 'eixo': eixo}


def _caixa(x0, x1, y0, y1, z0, z1):
    return ((x0, y0, z0), (x1, y1, z1))


def pecas(spec, divisoes=(), lista_gavetas=(), lista_internos=()):
    """[dict] das chapas do armário em milímetros, na ordem em que entram na cena e no corte."""
    largura, altura, profundidade = spec.largura, spec.altura, spec.profundidade
    x0, x1 = -largura / 2.0, largura / 2.0
    y_frente, y_tras = -profundidade, 0.0
    esq = spec.espessura_lateral if spec.lateral_esq_ativa else 0.0
    dir_ = spec.espessura_lateral if spec.lateral_dir_ativa else 0.0
    inf = spec.espessura_base_inferior if spec.base_inf_ativa else 0.0
    sup = spec.espessura_base_superior if spec.base_sup_ativa else 0.0
    base_passante = spec.tipo_montagem == spec_mod.BASE_PASSANTE
    comprimentos = spec_mod.carcass_lengths(spec)
    z_lateral = spec_mod.lateral_offset_z(spec)
    x_interno0 = x0 + esq
    z_interno0 = inf
    # RN-06: com a deslizante apoiada por dentro, o trilho come a profundidade — divisórias, prateleiras, gavetas e
    # internos recuam e encurtam nesse tanto, e as chapas da caixa ficam como estão.
    recuo = portas_mod.recuo_por_papel(spec.deslizante_ativa, spec.deslizante_base, spec.trilho_profundidade)
    itens = []

    # Caixa (RN-04): laterais na altura da montagem; bases entre elas ou por cima, conforme a montagem.
    if spec.lateral_esq_ativa:
        itens.append(_peca('LATERAL', "Lateral esquerda",
                           _caixa(x0, x0 + esq, y_frente, y_tras, z_lateral, z_lateral + comprimentos['LEFT']),
                           esq, veio='VERTICAL', fitas=FITA_FRENTE))
    if spec.lateral_dir_ativa:
        itens.append(_peca('LATERAL', "Lateral direita",
                           _caixa(x1 - dir_, x1, y_frente, y_tras, z_lateral, z_lateral + comprimentos['RIGHT']),
                           dir_, veio='VERTICAL', fitas=FITA_FRENTE))
    if spec.base_inf_ativa:
        bx0, bx1 = (x0, x1) if base_passante else (x_interno0, x1 - dir_)
        itens.append(_peca('BASE_INF', "Base inferior", _caixa(bx0, bx1, y_frente, y_tras, 0.0, inf), inf,
                           veio='HORIZONTAL', fitas=FITA_FRENTE))
    if spec.base_sup_ativa:
        tx0, tx1 = (x0, x1) if base_passante else (x_interno0, x1 - dir_)
        itens.append(_peca('BASE_SUP', "Base superior", _caixa(tx0, tx1, y_frente, y_tras, altura - sup, altura), sup,
                           veio='HORIZONTAL', fitas=FITA_FRENTE))

    # Fundo (RN-15): em canal entre as chapas da caixa; sobreposto nas medidas externas. O recuo afasta da face de trás.
    if spec.fundo_ativo:
        medidas = spec_mod.fundo(spec)
        t_fundo = spec.espessura_fundo
        if spec.fundo_fixacao == spec_mod.SOBREPOSTO:
            fx0, fx1, fz0, fz1 = x0, x1, 0.0, altura
        else:
            fx0, fx1, fz0, fz1 = x_interno0, x1 - dir_, inf, altura - sup
        fy1 = -medidas['recuo']
        itens.append(_peca('FUNDO', "Fundo", _caixa(fx0, fx1, fy1 - t_fundo, fy1, fz0, fz1), t_fundo))

    # Divisórias e prateleiras: o caminho do vão diz onde a peça começa (RN-12).
    regioes = vaos_mod.regioes(divisoes, spec)
    for divisao in divisoes:
        regiao = regioes.get(divisao.vao)
        if regiao is None:
            continue
        reg_x, reg_z, reg_largura, reg_altura = regiao
        py0 = y_frente + divisao.recuo_frente + recuo['DIVISORIA']
        py1 = y_tras - divisao.recuo_tras
        if divisao.eixo == vaos_mod.VERTICAL:
            px = x_interno0 + reg_x + divisao.posicao
            itens.append(_peca('DIVISORIA', "Divisória" if divisao.tipo != vaos_mod.ESPACADOR else "Distanciador",
                               _caixa(px, px + divisao.espessura, py0, py1,
                                      z_interno0 + reg_z, z_interno0 + reg_z + reg_altura),
                               divisao.espessura, veio='VERTICAL', fitas=FITA_FRENTE))
        else:
            pz = z_interno0 + reg_z + divisao.posicao
            itens.append(_peca('PRATELEIRA', "Prateleira",
                               _caixa(x_interno0 + reg_x, x_interno0 + reg_x + reg_largura, py0, py1,
                                      pz, pz + divisao.espessura),
                               divisao.espessura, veio='HORIZONTAL', fitas=FITA_FRENTE))

    # Internos: prateleira na altura escolhida dentro do vão (RN-13).
    for interno in lista_internos:
        regiao = regioes.get(interno.vao)
        if regiao is None:
            continue
        reg_x, reg_z, reg_largura, _reg_altura = regiao
        pz = z_interno0 + reg_z + interno.altura
        t_interno = spec.espessura_prateleira
        itens.append(_peca('PRATELEIRA', interno.tipo.capitalize(),
                           _caixa(x_interno0 + reg_x, x_interno0 + reg_x + reg_largura,
                                  y_frente + recuo['INTERNO'], y_tras, pz, pz + t_interno),
                           t_interno, veio='HORIZONTAL', fitas=FITA_FRENTE))

    # Frentes e caixa das gavetas: empilhadas no vão com a folga de 3 mm nas pontas e entre elas (RN-07, RN-09).
    topo = altura - sup
    preenchido = {}
    for gaveta in lista_gavetas:
        regiao = regioes.get(gaveta.vao)
        if regiao is None:
            continue
        reg_x, reg_z, reg_largura, _reg_altura = regiao
        base = preenchido.get(gaveta.vao, 0.0)
        pz = z_interno0 + reg_z + gavetas_mod.FOLGA + base
        preenchido[gaveta.vao] = base + gaveta.altura + gavetas_mod.FOLGA
        t_frente = spec.espessura_porta
        px0 = x_interno0 + reg_x
        itens.append(_peca('FRENTE_GAVETA', f"Frente da gaveta {gaveta.indice + 1}",
                           _caixa(px0, px0 + reg_largura, y_frente - t_frente + recuo['GAVETA'],
                                  y_frente + recuo['GAVETA'], pz, min(pz + gaveta.altura, topo)),
                           t_frente, veio='HORIZONTAL', fitas=FITA_FRENTE, movel=True,
                           curso=profundidade * 0.72, eixo='Y'))
        itens.extend(_caixa_da_gaveta(gaveta, spec, px0, pz, reg_largura, profundidade - recuo['GAVETA']))

    # Portas de abrir e folhas deslizantes são exclusivas (RN-14).
    comprimento_frente = x1 - dir_ - x_interno0
    if spec.porta_ativa and not spec.deslizante_ativa:
        folhas = portas_mod.portas_de_abrir(comprimento_frente, spec.porta_folhas,
                                            dobradica=spec.porta_dobradica,
                                            espessura=spec.espessura_porta, material='MDF')
        cursor = x_interno0
        for folha in folhas:
            itens.append(_peca('PORTA', f"Porta {folha.indice + 1}",
                               _caixa(cursor, cursor + folha.largura, y_frente - folha.espessura, y_frente,
                                      z_interno0, topo),
                               folha.espessura, veio='VERTICAL', fitas=SEM_FITA, movel=True,
                               curso=folha.graus, eixo='GIRO'))
            cursor += folha.largura
    elif spec.deslizante_ativa:
        folhas = portas_mod.folhas_deslizantes(comprimento_frente, spec.deslizante_folhas,
                                               sobreposicao=spec.deslizante_sobreposicao,
                                               material=spec.deslizante_material,
                                               espessura=spec.espessura_folha)
        material = 'VIDRO' if spec.deslizante_material == 'VIDRO' else (
            'ALUMINIO' if spec.deslizante_material == 'ALUMINIO' else 'CHAPA')
        for folha in folhas:
            px = x_interno0 + folha.indice * (folha.largura - spec.deslizante_sobreposicao)
            py1 = y_frente - folha.indice * (folha.espessura + 2.0)
            itens.append(_peca('FOLHA', f"Folha {folha.indice + 1}",
                               _caixa(px, px + folha.largura, py1 - folha.espessura, py1, z_interno0, topo),
                               folha.espessura, veio='VERTICAL', fitas=SEM_FITA, material=material,
                               movel=True, curso=folha.largura * 0.8, eixo='X'))
    return itens


def _caixa_da_gaveta(gaveta, spec, x0, z0, largura, profundidade):
    """Chapas da caixa da gaveta, com as medidas de `gavetas.chapas` (RN-09).

    A caixa fica atrás da frente e recua `FOLGA` de cada lateral. Separadores verticais ficam nas divisas das colunas
    e os horizontais nas das linhas; os quatro afastadores vão no topo das faces, cada um no seu lado. Tudo é
    aproximação de posicionamento — a medida de corte sai de `gavetas.chapas`, não daqui.
    """
    t_frente = spec.espessura_porta
    espessura = spec.espessura_gaveta
    largura_caixa = largura - 2.0 * gavetas_mod.FOLGA
    profundidade_caixa = profundidade - t_frente
    if largura_caixa <= 0.0 or profundidade_caixa <= 0.0:
        return []
    x0, x1 = x0 + gavetas_mod.FOLGA, x0 + largura - gavetas_mod.FOLGA
    y1 = -profundidade - t_frente
    y0 = y1 - profundidade_caixa
    z0, z1 = z0, z0 + gaveta.altura
    curso = profundidade * 0.72
    pecas_caixa = gavetas_mod.chapas(gaveta, largura_caixa, profundidade_caixa, espessura)
    verticais = [p for p in pecas_caixa if p['papel'] == 'SEPARADOR' and p['nome'].startswith('Separador vertical')]
    horizontais = [p for p in pecas_caixa if p['papel'] == 'SEPARADOR' and p['nome'].startswith('Separador horizontal')]
    colunas = max(1, int(gaveta.separador_colunas))
    linhas = max(1, int(gaveta.separador_linhas))
    saida = []
    for indice, separador in enumerate(verticais):
        px = x0 + (indice + 1) * largura_caixa / colunas
        esp = separador['espessura']
        saida.append(_peca('SEPARADOR', f"{separador['nome']} da gaveta {gaveta.indice + 1}",
                           _caixa(px - esp / 2.0, px + esp / 2.0, y0, y1,
                                  z0 + gavetas_mod.FOLGA, z0 + gavetas_mod.FOLGA + separador['comprimento']),
                           esp, movel=True, curso=curso, eixo='Y'))
    for indice, separador in enumerate(horizontais):
        pz = z0 + (indice + 1) * gaveta.altura / linhas
        esp = separador['espessura']
        saida.append(_peca('SEPARADOR', f"{separador['nome']} da gaveta {gaveta.indice + 1}",
                           _caixa(x0, x1, y0, y1, pz - esp / 2.0, pz + esp / 2.0),
                           esp, movel=True, curso=curso, eixo='Y'))
    for afastador in pecas_caixa:
        if afastador['papel'] != 'AFASTADOR':
            continue
        comprimento, largura_ta = afastador['comprimento'], afastador['largura']
        esp = afastador['espessura']
        if afastador['lado'] == 'frente':
            caixa = _caixa(x0, x0 + comprimento, y1 - esp, y1, z1 - largura_ta, z1)
        elif afastador['lado'] == 'tras':
            caixa = _caixa(x0, x0 + comprimento, y0, y0 + esp, z1 - largura_ta, z1)
        elif afastador['lado'] == 'esq':
            caixa = _caixa(x0, x0 + esp, y0, y0 + comprimento, z1 - largura_ta, z1)
        else:
            caixa = _caixa(x1 - esp, x1, y0, y0 + comprimento, z1 - largura_ta, z1)
        saida.append(_peca('AFASTADOR', f"{afastador['nome']} da gaveta {gaveta.indice + 1}", caixa, esp,
                           movel=True, curso=curso, eixo='Y'))
    return saida


def medidas_de_corte(item):
    """(comprimento, largura) de corte da chapa: os dois eixos que não são a espessura da caixa."""
    (px0, py0, pz0), (px1, py1, pz1) = item['box']
    vao = [px1 - px0, py1 - py0, pz1 - pz0]
    fino = min(range(3), key=lambda i: vao[i])
    return tuple(vao[i] for i in range(3) if i != fino)


def _material(nome, cor, roughness=0.45, metallic=0.0):
    import bpy  # type: ignore

    material = bpy.data.materials.get(nome)
    if material is None:
        material = bpy.data.materials.new(nome)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF') if material.node_tree else None
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = cor
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs and cor[3] < 1.0:
            bsdf.inputs['Transmission Weight'].default_value = 1.0 - cor[3]
    material.diffuse_color = cor
    return material


def materiais(acabamento):
    """{'CHAPA', 'VIDRO', 'ALUMINIO'} do acabamento escolhido (RF-17)."""
    cor = ACABAMENTOS.get(acabamento, ACABAMENTOS['MADEIRADO'])
    return {
        'CHAPA': _material(f"Armário v2 {acabamento.lower()}", cor),
        'VIDRO': _material("Armário v2 vidro", (0.82, 0.88, 0.90, 0.25), roughness=0.05),
        'ALUMINIO': _material("Armário v2 alumínio", (0.72, 0.73, 0.75, 1.0), roughness=0.3, metallic=1.0),
    }


def colecao(scene):
    """Coleção do armário v2 na cena, criada na primeira geração."""
    import bpy  # type: ignore

    existente = bpy.data.collections.get(COLECAO)
    if existente is None:
        existente = bpy.data.collections.new(COLECAO)
    if existente.name not in scene.collection.children:
        scene.collection.children.link(existente)
    return existente


def e_raiz(obj):
    """O objeto é a raiz vazia do armário v2 (vazio na coleção própria criada por `colecao`)."""
    if obj is None or obj.type != 'EMPTY':
        return False
    return any(colecao.name == COLECAO for colecao in obj.users_collection)


def raiz_de(obj):
    """Raiz do armário v2 acima de `obj` (ela inclusive), ou `None`.

    Todo `Object` carrega o grupo `btm_armario` — o `PointerProperty` existe em todos e devolve uma instância vazia —,
    então testar se ele está preenchido parava na primeira peça (a fumaça de T033 pegou isso no Abrir/Fechar e no
    menu). A raiz é o vazio da coleção do construtor, o mesmo critério em todo o pacote.
    """
    while obj is not None:
        if e_raiz(obj):
            return obj
        obj = obj.parent
    return None


def criar_raiz(scene, nome=RAIZ):
    """Raiz vazia do armário, na coleção própria; as peças nascem filhas dela."""
    import bpy  # type: ignore

    vazio = bpy.data.objects.new(nome, None)
    vazio.empty_display_type = 'PLAIN_AXES'
    vazio.empty_display_size = 0.05
    colecao(scene).objects.link(vazio)
    if getattr(vazio, 'btm_armario', None) is not None:
        vazio.btm_armario.gerado = False
    return vazio


def limpar(root):
    """Remove as peças geradas (filhas com `btm_armario_parte`), sem tocar no resto da cena."""
    import bpy  # type: ignore

    for filho in list(root.children):
        if getattr(filho, 'btm_armario_parte', None) is None:
            continue
        malha = filho.data if filho.type == 'MESH' else None
        bpy.data.objects.remove(filho, do_unlink=True)
        if malha is not None and malha.users == 0:
            bpy.data.meshes.remove(malha)


def _malha(nome, box):
    """Malha de caixa em metros, com normais recalculadas (RAG: seção BMesh do guia do projeto)."""
    import bmesh  # type: ignore
    import bpy  # type: ignore

    (px0, py0, pz0), (px1, py1, pz1) = box
    tamanho = [max(px1 - px0, 1e-5), max(py1 - py0, 1e-5), max(pz1 - pz0, 1e-5)]
    centro = [((px0 + px1) / 2.0) * MM, ((py0 + py1) / 2.0) * MM, ((pz0 + pz1) / 2.0) * MM]
    malha = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    try:
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=[tamanho[i] * MM for i in range(3)], verts=bm.verts)
        bmesh.ops.translate(bm, vec=centro, verts=bm.verts)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(malha)
    finally:
        bm.free()
    malha.update()
    return malha


def gerar(root, spec, divisoes=(), lista_gavetas=(), lista_internos=()):
    """Refaz as chapas do armário a partir do spec e devolve [objetos] na cena."""
    import bpy  # type: ignore
    from mathutils import Matrix  # type: ignore

    destino = (root.users_collection or (bpy.context.scene.collection,))[0]
    limpar(root)
    mapa = materiais(spec.acabamento)
    objetos = []
    for indice, dados in enumerate(pecas(spec, divisoes, lista_gavetas, lista_internos)):
        objeto = bpy.data.objects.new(dados['nome'], _malha(dados['nome'], dados['box']))
        destino.objects.link(objeto)
        objeto.parent = root
        objeto.matrix_parent_inverse = Matrix.Identity(4)
        material = mapa.get(dados['material'], mapa['CHAPA'])
        objeto.data.materials.append(material)
        parte = objeto.btm_armario_parte
        parte.papel = dados['papel']
        parte.componente = dados['componente']
        parte.comprimento_mm, parte.largura_mm = medidas_de_corte(dados)
        parte.espessura_mm = dados['espessura']
        parte.material = dados['material']
        parte.veio = dados['veio']
        parte.fita_l1, parte.fita_l2, parte.fita_w1, parte.fita_w2 = dados['fitas']
        parte.uid = f"{root.name}/{dados['papel']}/{indice}"
        parte.movel = dados['movel']
        parte.curso_mm = dados['curso']
        parte.eixo = dados['eixo']
        objetos.append(objeto)
    if getattr(root, 'btm_armario', None) is not None:
        root.btm_armario.gerado = True
    return objetos
