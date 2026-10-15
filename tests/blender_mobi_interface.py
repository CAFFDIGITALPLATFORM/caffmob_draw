"""Interface MOBI: grupos, conta, listas, cancelamento e preferências, sem rede (063 T053–T055)."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env
import bpy
import caffmob_draw as addon
from caffmob_draw.ui import sidebar_project, layout_probe
from caffmob_draw.texture_library import auth, downloads

context = bpy.context
state = context.window_manager.btm_caffmob
assert hasattr(context.window_manager.btm_sidebar, 'open_group_mobi')
assert not context.window_manager.btm_sidebar.open_group_mobi
state.ambientes.add().id = 'ambiente-teste'
state.ambientes[0].nome = 'Ambiente de teste'
state.proximo_ambiente = 'pagina-2'
for scope in ('titular', 'pessoal'):
    item = state.modelos.add()
    item.id, item.nome, item.escopo = scope, scope, scope

with patch.object(downloads, 'unavailable_reason', return_value=''), patch.object(auth, 'signed_in', return_value=True), patch.object(auth, 'titular_nome', return_value='Oficina'), patch.object(auth, 'login_state', return_value=(None, '', '')):
    records = []
    for scope in ('titular', 'pessoal'):
        state.biblioteca = scope
        probe = layout_probe.Probe()
        sidebar_project.draw_mobi(probe, context)
        ops = probe.recorder.operators()
        insert = next(r for r in ops if r['name'] == 'caffmob.mobi_baixar_modelo')
        assert insert['args']['modelo_id'] == scope
        assert next(r for r in ops if r['name'] == 'caffmob.mobi_baixar_ambiente')['args']['ambiente_id'] == 'ambiente-teste'
        assert any(r['args'].get('novo') and r['args'].get('escopo') == scope for r in ops)
        records = ops
    state.ocupado = True
    probe = layout_probe.Probe()
    sidebar_project.draw_mobi(probe, context)
    assert any(r['name'] == 'caffmob.mobi_cancelar' for r in probe.recorder.operators())
    state.ocupado = False
with patch.object(auth, 'signed_in', return_value=False), patch.object(auth, 'login_state', return_value=('WAITING', 'TEST-CODE', 'http://127.0.0.1')), patch.object(downloads, 'unavailable_reason', return_value=''):
    probe = layout_probe.Probe()
    sidebar_project.draw_mobi(probe, context)
    assert any(r['name'] == 'caffmob.mobi_cancelar' for r in probe.recorder.operators())

pref = addon.BTM_AddonPreferences.bl_rna.properties
assert pref['mobi_url'].default == 'https://mobi.caff.digital'
assert 'textures_server_url' not in pref
with patch.object(downloads, '_prefs', return_value=type('Prefs', (), {'mobi_url':'https://exemplo.test'})()), patch.dict(os.environ, {'CAFFMOB_BASE':'http://127.0.0.1:3210'}):
    assert downloads.server_url() == 'http://127.0.0.1:3210'
with patch.object(downloads, 'shutdown') as stop, patch.object(auth, 'reload') as reload, patch.object(auth, 'cancel_login') as cancel:
    addon._update_mobi_url(None, context)
    stop.assert_called_once()
    reload.assert_called_once()
    cancel.assert_called_once()

# Acrescenta só as novas capacidades: preserva os caminhos legados da linha de base.
if '--baseline' in sys.argv:
    path = Path(__file__).resolve().parent / 'fixtures/sidebar_inventory_baseline.json'
    data = json.loads(path.read_text())
    for rows in data['sidebar'].values():
        for record in records:
            current = dict(record, section='CAFFMob Draw › Produção/Projeto › CAFF MOBI')
            if current not in rows:
                rows.append(current)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
addon.unregister()
addon.register()
assert hasattr(bpy.context.window_manager, 'btm_caffmob')
addon.unregister()
print('BLENDER_MOBI_INTERFACE_OK', flush=True)
