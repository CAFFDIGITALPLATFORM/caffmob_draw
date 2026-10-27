"""073 (T030; RF-05 a RF-09, RN-07, RN-08, RN-10, RN-12): texturas PBR do pacote no Blender.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_073_pbr.py

Usa um pacote PBR sintético (as imagens são geradas aqui, nada do ambientCG) no lugar de `caffmob_draw/pbr/`:
- o material da biblioteca e o da cena v2 ligam normal, rugosidade e, no metal, metálico; o mesmo uso reaproveita
  o material;
- sem internet, a textura do pacote resolve e aplica sem nenhuma requisição;
- o `.promob` sintético com parede de tijolo e puxador de inox entra com as texturas PBR;
- a biblioteca lista "Revestimentos e metais" e a textura aparece como à mão; soltar aplica na hora.
"""
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _pbr_sintetico as ps_pbr  # noqa: E402
import _promob_sintetico as ps  # noqa: E402
from caffmob_draw.library_panel import draw as library_draw  # noqa: E402
from caffmob_draw.object_library import retexture  # noqa: E402
from caffmob_draw.promob import ops, para_v2  # noqa: E402
from caffmob_draw.texture_library import apply, catalog, downloads, ops_finish_drop, pbr, pbr_core  # noqa: E402

FAILURES = []
PASTA = tempfile.mkdtemp(prefix='caffmob_073_')
PBR_DIR = os.path.join(PASTA, 'pbr')
TIJOLO, INOX = pbr_core.uuid_de('tijolo-aparente'), pbr_core.uuid_de('inox-escovado')


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def pacote_sintetico():
    """Manifesto sintético com imagens 8 × 8 de verdade (o Blender precisa abri-las)."""
    dados = ps_pbr.gravar(PBR_DIR)
    for caminho in pbr_core.arquivos(dados):
        img = bpy.data.images.new('tmp', 8, 8)
        img.filepath_raw = os.path.join(PBR_DIR, *caminho.split('/'))
        img.file_format = 'JPEG'
        img.save()
        bpy.data.images.remove(img)
    catalog.PBR_DIR = PBR_DIR
    catalog._local.clear()
    manifesto = pbr_core.carregar(PBR_DIR)
    para_v2._pbr_do_addon = lambda: manifesto
    return manifesto


def ligado(mat, nome, entrada):
    no = mat.node_tree.nodes.get(nome)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if no is None:
        return False
    alvo = no.outputs['Color'].links[0].to_node if no.outputs['Color'].links else None
    if alvo is not None and alvo.type == 'NORMAL_MAP':
        alvo = alvo.outputs['Normal'].links[0].to_node if alvo.outputs['Normal'].links else None
    return alvo == bsdf and any(lk.to_socket.name == entrada for lk in mat.node_tree.links
                                if lk.to_node == bsdf and lk.from_node in (no, *[n for n in mat.node_tree.nodes
                                                                                 if n.type == 'NORMAL_MAP']))


def biblioteca():
    entrada = catalog.item(TIJOLO)
    check(entrada is not None and entrada.get('pbr'), "o UUID do tijolo acha a textura do pacote")
    caminho = downloads.cached(TIJOLO)
    check(caminho == os.path.join(PBR_DIR, 'tijolo-aparente', 'cor.jpg'), "a imagem vem do pacote, sem cache", caminho)
    mat = retexture.image_material(caminho, 1200, 1200, texture_id=TIJOLO)
    check(ligado(mat, pbr.NORMAL, 'Normal') and ligado(mat, pbr.ROUGHNESS, 'Roughness'),
          "material da biblioteca com normal e rugosidade")
    check(mat.node_tree.nodes.get(pbr.METALLIC) is None, "tijolo não tem metálico")
    mapping = next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')
    check(all(mapping == n.inputs['Vector'].links[0].from_node for n in mat.node_tree.nodes
              if n.type == 'TEX_IMAGE'), "os mapas usam o mesmo mapeamento da cor")
    again = retexture.image_material(caminho, 1200, 1200, texture_id=TIJOLO)
    check(again == mat and len([n for n in mat.node_tree.nodes if n.name == pbr.NORMAL]) == 1,
          "o mesmo uso reaproveita o material, sem duplicar nós")
    inox = retexture.image_material(downloads.cached(INOX), 500, 500, texture_id=INOX)
    check(ligado(inox, pbr.METALLIC, 'Metallic'), "inox com o mapa metálico")


def sem_internet():
    pedidos = []
    original = downloads.fetch
    downloads.fetch = lambda *a, **k: pedidos.append(a)
    try:
        bpy.ops.mesh.primitive_cube_add()
        cubo = bpy.context.active_object
        estado, n = apply.apply([cubo], TIJOLO)
        check(estado == apply.APPLIED and n == 1, "aplicar a textura do pacote funciona na hora", f"{estado} {n}")
        check(not pedidos, "nenhuma requisição de download")
        caminhos = []
        ops_finish_drop.fetch(INOX, lambda p, e, imediato: caminhos.append((p, e, imediato)))
        check(caminhos and caminhos[0][0].endswith('inox-escovado/cor.jpg') and caminhos[0][2],
              "soltar a textura do pacote não espera download")
        mat, _largura = ops_finish_drop.material_for(INOX, caminhos[0][0])
        check(ligado(mat, pbr.METALLIC, 'Metallic'), "o material do soltar também é PBR")
    finally:
        downloads.fetch = original


def painel():
    arvore = library_draw.texture_tree()
    check(arvore and arvore[0][0] == catalog.PBR_MANUFACTURER and [c[0] for c in arvore[0][3]] == ['parede', 'piso',
                                                                                                    'metal'],
          "a biblioteca abre com Revestimentos e metais (Parede, Piso, Metal)", str(arvore[:1]))
    check(library_draw.texture_state(catalog.item(TIJOLO)) == ('DOWNLOADED', 1.0), "a textura do pacote aparece à mão")
    check(catalog.thumb_path(catalog.item(TIJOLO)).endswith('tijolo-aparente/miniatura.jpg'), "miniatura do pacote")


def importacao():
    parede = ps._parede([(0, 0, 150), (3000, 0, 150), (3000, 2500, 150)], 2700)
    faces = ''.join(f'<REGION ID="PAREDE_FACE_PERFIL_MOVIMENTACAO_INDICEFORMA_{i}"><MATERIAL ID="{m}" /></REGION>'
                    for i, m in ((0, 'reboco'), (1, 'par_tijolos_tijolos 003')))
    parede = parede.replace('</REGION></REGIONS>', '</REGION>' + faces + '</REGIONS>', 1)
    puxador = ps._item('MODULO', 'pux', base=(500, 0, 900), dim=(160, 20, 30), rot=0, nome='Puxador',
                       camada='Default', material='inox escovado')
    principal = ps._ambiente([parede, puxador], nome='Texturas')
    caminho = os.path.join(PASTA, 'Texturas.promob')
    with open(caminho, 'wb') as f:
        f.write(ps.zip_de(ps.entradas(principal=principal)))
    online = bpy.app.online_access
    erro = ops.importar(caminho, None)
    check(erro is None, "a importação não dá erro", str(erro))
    if bpy.app.timers.is_registered(ops._montar):
        bpy.app.timers.unregister(ops._montar)
    ops._montar()
    doc = json.loads(bpy.context.scene['caffmob_ambiente'])
    tijolo = [m for m in doc['materiais'] if m.get('textura_id') == TIJOLO]
    check(tijolo and tijolo[0]['tipo'] == 'textura' and tijolo[0]['escala_mm'] == {'largura': 1200, 'altura': 1200},
          "o documento grava a parede de tijolo como textura, em escala real", str(tijolo))
    na_parede = [m for m in bpy.data.materials if m.get(pbr.MARK) == TIJOLO and m.get('caffmob_material')]
    check(na_parede and ligado(na_parede[0], pbr.NORMAL, 'Normal'), "a parede na cena tem o tijolo com relevo",
          str([m.name for m in bpy.data.materials if m.get(pbr.MARK)]))
    check(not na_parede or na_parede[0].get('caffmob_textura_pendente') == '', "nada fica pendente de download")
    puxadores = [m for m in bpy.data.materials if m.get(pbr.MARK) == INOX and 'inox escovado' in
                 str(m.get('btm_promob_origem', ''))]
    check(puxadores and ligado(puxadores[0], pbr.METALLIC, 'Metallic'), "o puxador de inox entra metálico")
    check(online == bpy.app.online_access, "a importação não mexe no acesso online")


def main():
    pacote_sintetico()
    for etapa in (biblioteca, sem_internet, painel, importacao):
        try:
            etapa()
        except Exception:
            traceback.print_exc()
            FAILURES.append(etapa.__name__)
    if FAILURES:
        print("FALHAS:", FAILURES)
        sys.exit(1)


main()
