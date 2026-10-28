"""078 (T029): Teste de integração em Blender headless para os 30 modelos de aberturas, contrato v2 e 'Substituir pelo selecionado'."""

import json
import os
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_TMP_STANDARDS = tempfile.TemporaryDirectory()
os.environ.setdefault("CAFFMOB_DRAW_STANDARDS_DB", os.path.join(_TMP_STANDARDS.name, "padroes.sqlite3"))

import caffmob_draw as addon
from caffmob_draw.caffmob.v2.contrato import (
    MATERIAIS_DE_ABERTURA,
    MODELOS_DE_JANELA,
    MODELOS_DE_PORTA,
)
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.mobi import cena_v2, enviar_v2
from caffmob_draw.mobi.enviar_v2_core import novo_documento

addon.register()
addon.load_file_post(None)


def _limpar_objetos_extras():
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def _selecionar_unico(obj):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    if obj is not None:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def testar_30_modelos_contrato_v2_e_roundtrip():
    """Constroi os 30 modelos (10 portas + 20 janelas) nos 3 acabamentos via `cena_v2` e verifica `enviar_v2`."""
    _limpar_objetos_extras()
    doc = novo_documento("Ambiente 078 — 30 Aberturas")
    pav_id = doc["pavimentos"][0]["id"]
    doc["pavimentos"][0]["pe_direito"] = 3000

    # Parede com 6 segmentos (5 aberturas por segmento, respeitando LIMITES_STUDIO['aberturas_por_segmento'] == 8)
    seg_ids = [f"11111111-1111-4111-8111-11111111110{k}" for k in range(1, 7)]
    angulos = [0, 90, 0, 90, 0, 90]
    segmentos = []
    for k, (sid, ang) in enumerate(zip(seg_ids, angulos)):
        rel = 0 if k == 0 else (ang - angulos[k - 1])
        segmentos.append(
            {
                "id": sid,
                "comprimento": 10000,
                "angulo_absoluto": ang,
                "angulo_relativo": rel,
                "espessura": 150,
                "pe_direito_inicial": 3000,
                "pe_direito_final": 3000,
                "afastamento": 0,
                "flecha": 0,
                "sentido": "LEFT",
                "tipo": "NORMAL",
                "estado": "ativo",
            }
        )
    doc["paredes"] = [
        {
            "id": "22222222-2222-4222-8222-222222222201",
            "pavimento_id": pav_id,
            "camada_id": None,
            "origem": {"x": 0, "y": 0},
            "fechada": False,
            "visivel": True,
            "perfil": "studio/1",
            "segmentos": segmentos,
        }
    ]

    aberturas = []
    for i, modelo in enumerate(MODELOS_DE_PORTA):
        material = MATERIAIS_DE_ABERTURA[i % len(MATERIAIS_DE_ABERTURA)]
        seg_id = seg_ids[i // 5]
        idx_local = i % 5
        aberturas.append(
            {
                "id": f"33333333-3333-4333-8333-3333333333{i + 1:02d}",
                "segmento_id": seg_id,
                "tipo": "DOOR",
                "posicao": 300 + idx_local * 1800,
                "largura": 1200,
                "altura": 2100,
                "peitoril": 0,
                "modelo": modelo,
                "material": material,
            }
        )

    for j, modelo in enumerate(MODELOS_DE_JANELA):
        material = MATERIAIS_DE_ABERTURA[j % len(MATERIAIS_DE_ABERTURA)]
        seg_id = seg_ids[2 + (j // 5)]
        idx_local = j % 5
        aberturas.append(
            {
                "id": f"44444444-4444-4444-8444-4444444444{j + 1:02d}",
                "segmento_id": seg_id,
                "tipo": "WINDOW",
                "posicao": 300 + idx_local * 1800,
                "largura": 1200,
                "altura": 1100,
                "peitoril": 950,
                "modelo": modelo,
                "material": material,
            }
        )

    assert len(aberturas) == 30
    doc["aberturas"] = aberturas
    erros_doc = validar_documento(doc)
    assert erros_doc == [], f"Erros de validação: {erros_doc}"

    cena_v2.construir_cena(bpy.context, doc)

    raizes = [o for o in bpy.context.scene.objects if o.get("caffmob_tipo") == "abertura"]
    assert len(raizes) == 30, f"Esperava 30 raízes de abertura, obteve {len(raizes)}"

    for raiz in raizes:
        pecas = [c for c in raiz.children if c.get("caffmob_tipo") == "abertura_peca"]
        assert len(pecas) >= 2, f"Abertura {raiz.name} deveria ter batente + folhas, obteve {len(pecas)}"
        assert raiz.btm_opening_real.opening_model != ""

    # Round-trip de volta para o documento v2
    doc_lido, avisos = enviar_v2.documento_da_cena(bpy.context)
    assert avisos == []
    assert len(doc_lido["aberturas"]) == 30
    por_id = {a["id"]: a for a in doc_lido["aberturas"]}
    for esp in aberturas:
        atual = por_id[esp["id"]]
        assert atual["modelo"] == esp["modelo"]
        assert atual["material"] == esp["material"]
        assert atual["largura"] == esp["largura"]
        assert atual["altura"] == esp["altura"]


def testar_substituir_abertura_v2_e_promob():
    """Substitui uma abertura v2 com grupo Promob (`btm_promob_abertura`) por outro modelo preservando o vão."""
    porta_raiz = next(
        o
        for o in bpy.context.scene.objects
        if o.get("caffmob_tipo") == "abertura"
        and json.loads(o["caffmob_abertura"])["tipo"] == "DOOR"
    )
    abertura_id = porta_raiz["caffmob_id"]
    dados_antes = json.loads(porta_raiz["caffmob_abertura"])

    # Simula grupo órfão vindo do `.promob` (`btm_promob_abertura`) + `btm_promob_aberturas_sem_folha`
    grupo_promob = bpy.data.objects.new("Promob_Porta_Original", None)
    bpy.context.scene.collection.objects.link(grupo_promob)
    grupo_promob["btm_promob_abertura"] = abertura_id

    folha_promob = bpy.data.objects.new("Promob_Folha_Filha", bpy.data.meshes.new("Promob_Folha_Mesh"))
    bpy.context.scene.collection.objects.link(folha_promob)
    folha_promob.parent = grupo_promob

    bpy.context.scene[cena_v2.SEM_FOLHA_PROP] = json.dumps([abertura_id])
    cena_v2.esconder_folhas_substituidas(bpy.context.scene)
    assert all(c.hide_viewport for c in porta_raiz.children)

    # Seleciona a folha do Promob e substitui por `porta_correr_4f` em `blindex`
    _selecionar_unico(folha_promob)
    bpy.context.window_manager.btm_library.opening_material = "blindex"
    res = bpy.ops.caffmob.library_replace_selected(
        model_id="porta_correr_4f",
        material="blindex",
    )
    assert res == {"FINISHED"}

    # O grupo Promob foi removido e o ID saiu de `SEM_FOLHA_PROP`
    assert not any(o.get("btm_promob_abertura") == abertura_id for o in bpy.context.scene.objects)
    assert abertura_id not in json.loads(bpy.context.scene.get(cena_v2.SEM_FOLHA_PROP) or "[]")

    # As dimensões do vão foram preservadas e o modelo/material atualizados
    dados_depois = json.loads(porta_raiz["caffmob_abertura"])
    assert dados_depois["largura"] == dados_antes["largura"]
    assert dados_depois["altura"] == dados_antes["altura"]
    assert dados_depois["peitoril"] == dados_antes["peitoril"]
    assert dados_depois["posicao"] == dados_antes["posicao"]
    assert dados_depois["modelo"] == "porta_correr_4f"
    assert dados_depois["material"] == "blindex"
    assert any(not c.hide_viewport for c in porta_raiz.children)

    # E `enviar_v2.documento_da_cena` enxerga a substituição
    doc_lido, _ = enviar_v2.documento_da_cena(bpy.context)
    abertura_doc = next(a for a in doc_lido["aberturas"] if a["id"] == abertura_id)
    assert abertura_doc["modelo"] == "porta_correr_4f"
    assert abertura_doc["material"] == "blindex"


def testar_recusa_entre_familias_diferentes():
    """Recusa substituição quando a família do candidato difere do alvo selecionado ou seleção inválida."""
    porta_raiz = next(
        o
        for o in bpy.context.scene.objects
        if o.get("caffmob_tipo") == "abertura"
        and json.loads(o["caffmob_abertura"])["tipo"] == "DOOR"
    )
    _selecionar_unico(porta_raiz)

    # Porta selecionada + candidato janela -> CANCELLED
    assert bpy.ops.caffmob.library_replace_selected(model_id="janela_correr_2f") == {"CANCELLED"}

    # Porta selecionada + candidato módulo -> CANCELLED
    assert bpy.ops.caffmob.library_replace_selected(model_id="balcao_2p") == {"CANCELLED"}

    # Seleção vazia -> CANCELLED
    _selecionar_unico(None)
    assert bpy.ops.caffmob.library_replace_selected(model_id="porta_giro_lisa") == {"CANCELLED"}


def testar_substituir_modulos_balcao_gaveteiro_e_cantos():
    """Insere balcão e substitui em cadeia: balcão -> gaveteiro -> canto L -> canto oblíquo -> balcão reto."""
    _selecionar_unico(None)
    res = bpy.ops.caffmob.library_insert_model(model_id="balcao_1p")
    assert res == {"FINISHED"}

    root = bpy.context.view_layer.objects.active
    assert root is not None and root.btm_plane.object_kind == "MODULE"
    # Ajusta dimensões customizadas para provar preservação (920 × 560 × 870 mm)
    root.btm_cabinet.width = 0.92
    root.btm_cabinet.depth = 0.56
    root.btm_cabinet.height = 0.87
    root.location = (1.25, -0.80, 0.10)
    root.rotation_euler.z = 0.5

    # 1. Balcão 1P -> Gaveteiro 4G (mantém 920 × 560 × 870 mm e pose)
    _selecionar_unico(root)
    assert bpy.ops.caffmob.library_replace_selected(model_id="gaveteiro_4g") == {"FINISHED"}
    gav = bpy.context.view_layer.objects.active
    assert gav is not None and gav.btm_plane.object_kind == "MODULE"
    assert abs(gav.btm_cabinet.width - 0.92) < 1e-4
    assert abs(gav.btm_cabinet.depth - 0.56) < 1e-4
    assert abs(gav.btm_cabinet.height - 0.87) < 1e-4
    assert abs(gav.location.x - 1.25) < 1e-4
    assert abs(gav.location.y - (-0.80)) < 1e-4
    assert abs(gav.rotation_euler.z - 0.5) < 1e-4
    assert int(gav.get("btm_drawers") or 0) == 4

    # 2. Gaveteiro 4G (reto) -> Canto L Balcão (inicializa 2º braço com o Padrão de Dimensões da linha = 800 mm)
    _selecionar_unico(gav)
    assert bpy.ops.caffmob.library_replace_selected(model_id="canto_l_balcao") == {"FINISHED"}
    canto_l = bpy.context.view_layer.objects.active
    assert canto_l is not None and canto_l.btm_plane.object_kind == "MODULE"
    assert canto_l.get("btm_corner_kind") == "L"
    assert abs(canto_l.btm_cabinet.width - 0.92) < 1e-4
    assert abs(float(canto_l.get("btm_right_width_mm") or 0.0) - 800.0) < 1e-4

    # Customiza o 2º braço do canto L para 1050 mm e substitui por Canto Oblíquo (preserva 1050 mm)
    canto_l["btm_right_width_mm"] = 1050.0
    _selecionar_unico(canto_l)
    assert bpy.ops.caffmob.library_replace_selected(model_id="canto_obliquo_balcao") == {"FINISHED"}
    canto_ob = bpy.context.view_layer.objects.active
    assert canto_ob is not None and canto_ob.btm_plane.object_kind == "MODULE"
    assert canto_ob.get("btm_corner_kind") == "OBLIQUE"
    assert abs(float(canto_ob.get("btm_right_width_mm") or 0.0) - 1050.0) < 1e-4

    # 3. Canto Oblíquo -> Balcão 2P reto (zera btm_right_width_mm e preserva largura principal 920 mm)
    _selecionar_unico(canto_ob)
    assert bpy.ops.caffmob.library_replace_selected(model_id="balcao_2p") == {"FINISHED"}
    balcao_2p = bpy.context.view_layer.objects.active
    assert balcao_2p is not None and balcao_2p.btm_plane.object_kind == "MODULE"
    assert abs(balcao_2p.btm_cabinet.width - 0.92) < 1e-4
    assert balcao_2p.get("btm_corner_kind") == "NONE"
    assert abs(float(balcao_2p.get("btm_right_width_mm") or 0.0)) < 1e-4


testar_30_modelos_contrato_v2_e_roundtrip()
testar_substituir_abertura_v2_e_promob()
testar_recusa_entre_familias_diferentes()
testar_substituir_modulos_balcao_gaveteiro_e_cantos()
print("blender_078_openings_and_replace: OK")
