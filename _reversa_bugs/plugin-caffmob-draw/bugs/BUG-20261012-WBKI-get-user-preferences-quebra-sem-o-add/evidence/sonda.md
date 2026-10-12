# Reprodução de BUG-20261012-WBKI

- Commit: master em 2026-10-12
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`)

`cd tests && blender --background --factory-startup --python blender_inspection_smoke.py` (passa: `BLENDER_INSPECTION_SMOKE_OK`):

```
     17 KeyError: 'bpy_prop_collection[key]: key "caffmob_draw" not found'
  File ".../face_frame/props_hb_face_frame.py", line 3829, in _update_cabinet_dim
  File ".../face_frame/types_face_frame.py", line 8775, in recalculate_face_frame_cabinet
  File ".../face_frame/types_face_frame.py", line 8841, in apply
  File ".../frameless/operators/ops_placement.py", line 34, in toggle_cabinet_color
  File ".../hb_props.py", line 824, in get_user_preferences
    add_on_prefs = preferences.addons[__package__].preferences
```
