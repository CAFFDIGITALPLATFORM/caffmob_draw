"""
Contrato caffmob v1 dentro do Blender (feature 061, T095 e T097, parte local; 062 T032, texturas pela rede).

Para cada caso-ouro de ambiente válido: monta a cena parede a parede e lê a cena de volta para o
contrato; o documento tem de sair idêntico (fora version, atualizado_em e origem). Confere também as
malhas, as peças dos módulos pelo contrato e a edição de um segmento.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_caffmob.py
"""
import json
import sys
from pathlib import Path

import bpy

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import blendertomob as addon  # noqa: E402
from blendertomob.caffmob.chapas import pecas_do_modulo  # noqa: E402
from blendertomob.caffmob.contrato import ler_documento, sem_envelope_do_servidor, serializar  # noqa: E402
from blendertomob.caffmob.geometria import trechos_da_parede  # noqa: E402
from blendertomob.cutting.part_extractor import extract_parts_from_scene  # noqa: E402
from blendertomob.operators.caffmob_sync import construir_cena, documento_da_cena  # noqa: E402

addon.register()
addon.load_file_post(None)
contexto = bpy.context
casos = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "tests" / "casos_ouro").rglob("*.json"))]
ambientes = [c for c in casos if c["tipo"] == "ambiente" and "erros" not in c["esperado"]]
ambientes.append(next(c for c in casos if c["caso"] == "carga-200-segmentos-30-modulos"))
falhas = []

for caso in ambientes:
    documento = caso["entrada"]
    construir_cena(contexto, documento)
    paredes = [o for o in contexto.scene.objects if o.get("caffmob_tipo") == "parede"]
    pisos = [o for o in contexto.scene.objects if o.get("caffmob_tipo") == "piso"]
    if len(paredes) != len(documento["paredes"]) or any(len(o.data.vertices) == 0 for o in paredes):
        falhas.append(f"{caso['caso']}: paredes sem malha")
    if len(pisos) != sum(1 for p in documento["paredes"] if p["fechada"]):
        falhas.append(f"{caso['caso']}: {len(pisos)} pisos para {sum(1 for p in documento['paredes'] if p['fechada'])} paredes fechadas")
    volta = documento_da_cena(contexto)
    if serializar(sem_envelope_do_servidor(volta)) != serializar(sem_envelope_do_servidor(documento)):
        falhas.append(f"{caso['caso']}: a cena não volta igual ao contrato")
print(f"ida e volta pela cena: {len(ambientes)} ambientes", flush=True)

# Peças dos 30 módulos pelo contrato, com id pelo uuid do módulo (T092).
carga = next(c for c in casos if c["caso"] == "carga-200-segmentos-30-modulos")["entrada"]
construir_cena(contexto, carga)
pecas = extract_parts_from_scene(contexto)
esperadas = [p["id"] for m in carga["modulos"] for p in pecas_do_modulo(m)]
if sorted(p.id for p in pecas) != sorted(esperadas):
    falhas.append(f"peças: {len(pecas)} extraídas, {len(esperadas)} esperadas pelo contrato")
if {p.module_ref for p in pecas} != {m["id"] for m in carga["modulos"]}:
    falhas.append("module_ref das peças não é o uuid do módulo")

# Edição de segmento: mudar o 2º lado da polilinha aberta desloca o vértice seguinte (RF-13).
aberta = next(c for c in casos if c["caso"] == "parede-polilinha-aberta")["entrada"]
construir_cena(contexto, aberta)
parede_obj = next(o for o in contexto.scene.objects if o.get("caffmob_tipo") == "parede")
contexto.view_layer.objects.active = parede_obj
antes = trechos_da_parede(ler_documento(parede_obj["caffmob_parede"]))
segmento = ler_documento(parede_obj["caffmob_parede"])["segmentos"][1]
resultado = bpy.ops.btm.caffmob_editar_segmento(indice=1, comprimento=segmento["comprimento"] + 200, espessura=segmento["espessura"],
                                                 pe_direito_inicial=segmento["pe_direito_inicial"], pe_direito_final=segmento["pe_direito_final"],
                                                 afastamento=0, flecha=0, sentido=segmento["sentido"], tipo=segmento["tipo"])
depois = trechos_da_parede(ler_documento(parede_obj["caffmob_parede"]))
if resultado != {'FINISHED'} or abs((depois[2][1][1] - antes[2][1][1]) - 200) > 1e-6:
    falhas.append(f"editar segmento: {resultado}, último vértice foi de {antes[2][1]} para {depois[2][1]}")
# Sem tela, o Blender transforma o report({'ERROR'}) do operador em RuntimeError: é a recusa.
try:
    bpy.ops.btm.caffmob_editar_segmento(indice=0, comprimento=1000, espessura=150, pe_direito_inicial=2700, pe_direito_final=2700,
                                        afastamento=0, flecha=900, sentido='LEFT', tipo='NORMAL')
    falhas.append("flecha maior que meia corda deveria ser recusada")
except RuntimeError as erro:
    if "FLECHA_FORA" not in str(erro):
        falhas.append(f"recusa com motivo errado: {erro}")

# Pela rede, com os operadores do painel, contra o MOBI de ensaio (scripts/mobi/servidor-de-ensaio-061.sh).
URL = __import__("os").environ.get("CAFFMOB_ENSAIO_URL")
if URL:
    import os
    from blendertomob.caffmob import conexao
    from blendertomob.operators import caffmob_sync
    os.environ["CAFFMOB_BASE"] = URL
    sessao = caffmob_sync.sessao()
    sessao.guardar(conexao.esperar_token(URL, conexao.pedir_codigo(URL, "Blender de ensaio")))
    original = dict(next(c for c in casos if c["caso"] == "carga-200-segmentos-30-modulos")["entrada"], id="7d0e0000-0000-4000-8000-000000000061")
    sessao.criar_ambiente(original)
    bpy.ops.btm.caffmob_listar()
    wm = contexto.window_manager
    if original["id"] not in [item.ambiente_id for item in wm.caffmob_ambientes]:
        falhas.append("Listar não trouxe o ambiente criado")
    bpy.ops.btm.caffmob_baixar(ambiente_id=original["id"])
    if len([o for o in contexto.scene.objects if o.get("caffmob_tipo") == "modulo"]) != 30:
        falhas.append("Baixar não reproduziu os 30 módulos")
    bpy.ops.btm.caffmob_enviar()
    no_mobi = sessao.baixar_ambiente(original["id"])
    if no_mobi["version"] != 2 or no_mobi["origem"] != "blender" or serializar(sem_envelope_do_servidor(no_mobi)) != serializar(sem_envelope_do_servidor(original)):
        falhas.append(f"Enviar sem mudança deveria gravar a versão 2 igual ao original (versão {no_mobi['version']})")
    # Alguém muda na web; o Blender, ainda na 2, move um módulo e envia: 409, e a escolha fica com a do MOBI.
    na_web = dict(no_mobi, nome="Mudado na web")
    sessao.enviar_ambiente(na_web, 2)
    modulo = next(o for o in contexto.scene.objects if o.get("caffmob_tipo") == "modulo")
    modulo.location.x += 0.5
    bpy.ops.btm.caffmob_enviar()
    if not contexto.scene.get("caffmob_conflito"):
        falhas.append("Enviar com versão velha deveria guardar o conflito")
    bpy.ops.btm.caffmob_resolver_conflito(escolha='DO_MOBI')
    if ler_documento(contexto.scene["caffmob_ambiente"])["nome"] != "Mudado na web" or contexto.scene["caffmob_versao"] != 3:
        falhas.append("Ficar com a do MOBI deveria trazer a versão 3")
    # De novo, agora ficando com a minha.
    sessao.enviar_ambiente(dict(sessao.baixar_ambiente(original["id"]), nome="Mudado de novo"), 3)
    modulo = next(o for o in contexto.scene.objects if o.get("caffmob_tipo") == "modulo")
    modulo.location.x += 0.25
    bpy.ops.btm.caffmob_enviar()
    bpy.ops.btm.caffmob_resolver_conflito(escolha='MINHA')
    final = sessao.baixar_ambiente(original["id"])
    if final["version"] != 5 or final["nome"] != "Mudado na web":
        falhas.append(f"Ficar com a minha deveria gravar a versão 5 com o nome da cena (veio {final['version']}, {final['nome']})")
    # 062: textura de fábrica. Baixar traz só o que o módulo usa e monta o material; o painel aplica e o Enviar leva.
    from blendertomob.caffmob.chapas import aplicar_textura
    achadas = sessao.listar_texturas(busca="japandi")["itens"]
    if len(achadas) != 1:
        falhas.append(f"a busca por japandi deveria achar 1 textura (achou {len(achadas)})")
    else:
        tid = achadas[0]["id"]
        com_textura = dict(original, id="7d0e0000-0000-4000-8000-000000000062", nome="Com textura",
                           modulos=[aplicar_textura(original["modulos"][0], "CAIXA", tid), *original["modulos"][1:]])
        sessao.criar_ambiente(com_textura)
        bpy.ops.btm.caffmob_baixar(ambiente_id=com_textura["id"])
        texturizado = next(o for o in contexto.scene.objects if o.get("caffmob_tipo") == "modulo" and json.loads(o["caffmob_modulo"])["id"] == com_textura["modulos"][0]["id"])
        material = next((m for m in texturizado.data.materials if m.name == f"CAFFMOB {tid}"), None)
        imagem = material and next((no.image for no in material.node_tree.nodes if no.type == 'TEX_IMAGE'), None)
        if not imagem or imagem.size[0] == 0:
            falhas.append("o módulo com textura deveria ter o material com a imagem carregada")
        elif not Path(imagem.filepath).name.startswith(achadas[0]["sha256_trabalho"]):
            falhas.append(f"a imagem deveria vir do cache com o sha256 no nome ({imagem.filepath})")
        contexto.view_layer.objects.active = texturizado
        contexto.window_manager.caffmob_grupo_textura = "TODAS"
        bpy.ops.btm.caffmob_aplicar_textura(textura_id=tid)
        if any(not c.get("textura_id") for c in __import__("blendertomob.caffmob.chapas", fromlist=["x"]).chapas_do_modulo(json.loads(texturizado["caffmob_modulo"]))):
            falhas.append("Aplicar a todas deveria pôr a textura em toda chapa do módulo")
        bpy.ops.btm.caffmob_enviar()
        voltou = next(m for m in sessao.baixar_ambiente(com_textura["id"])["modulos"] if m["id"] == com_textura["modulos"][0]["id"])
        if {e.get("textura_id") for e in voltou["chapas_editadas"]} != {tid}:
            falhas.append(f"o textura_id deveria voltar ao MOBI em todas as chapas (veio {voltou['chapas_editadas']})")
    sessao.esquecer()
    print("pela rede com os operadores: ok" if not falhas else "pela rede com os operadores: falhou", flush=True)

addon.unregister()
addon.register()
addon.unregister()
if falhas:
    print("\n".join(f"FALHOU {f}" for f in falhas), flush=True)
    sys.exit(1)
print("BLENDER_CAFFMOB_OK", flush=True)
