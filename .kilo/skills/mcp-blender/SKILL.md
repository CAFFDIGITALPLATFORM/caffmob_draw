---
name: mcp-blender
description: Use this skill whenever the user wants to interact with Blender via MCP (Model Context Protocol) server, draw/create 3D objects, modify scenes, apply materials, lighting, UV maps, or any Blender-related operation through the MCP server. Make sure to use this skill whenever the user mentions Blender, MCP, port 9877, drawing in Blender, 3D modeling, or any Blender automation task, even if they don't explicitly ask for a "skill". This skill manages user preferences (port, name) stored in .blender-mcp/settings.md.
---

# mcp-blender Skill

## Purpose

This skill provides a standardized way to interact with Blender through an MCP (Model Context Protocol) server running on a configurable port. It manages user preferences (port number, user name) stored in `.blender-mcp/settings.md` and uses them on every invocation.

## Preferences Management

### Settings File Location

Preferences are stored in `.blender-mcp/settings.md` relative to the current working directory (or project root).

### Settings File Format

```markdown
# Blender MCP Settings

- **Port**: <port_number>
- **User Name**: <user_name>
```

### On Every Invocation

1. **Check for settings file**: Look for `.blender-mcp/settings.md` in the working directory.
2. **If settings exist**: Read and parse them. Use the configured port and user name for all operations.
3. **If settings don't exist**: Prompt the user in the chat for:
   - Their name
   - The port they want to use for the Blender MCP server (default: 9877)
   Then create the `.blender-mcp/` directory and `settings.md` file with these values.

### Prompting for Missing Settings

When settings are missing, ask the user:
- "Qual é o seu nome?" (What is your name?)
- "Qual porta deseja usar para o servidor MCP do Blender? (padrão: 9877)" (Which port do you want to use for the Blender MCP server? default: 9877)

Create the settings file after receiving answers.

## MCP Communication Protocol

### Connection Details

- **Protocol**: TCP socket
- **Host**: 127.0.0.1 (localhost)
- **Port**: From settings (default: 9877)
- **Format**: JSON message terminated by null byte (`\0`)

### Message Format

```json
{"type":"execute","code":"<python_code>","strict_json":true}\0
```

### Python Code Execution

The `code` field contains Python code that runs inside Blender's Python environment (bpy module available). Use this to:
- Create/modify 3D objects
- Apply materials, textures, lighting
- Modify UV maps
- Render scenes
- Execute any Blender operation

### Response Format

Blender responds with JSON:
```json
{"status": "ok", "result": {}, "stdout": "<output>"}
```

## Common Operations

### Creating Objects

```python
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "MyCube"
```

### Applying Materials

```python
import bpy
mat = bpy.data.materials.new(name="MyMaterial")
mat.use_nodes = True
obj.data.materials.append(mat)
```

### UV Unwrapping

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Separating Loose Parts

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
```

### Splitting Mesh Edges

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.split()
bpy.ops.object.mode_set(mode='OBJECT')
```

### Adding Lighting

```python
import bpy
bpy.ops.object.light_add(type='AREA', location=(1200, -800, 900))
light = bpy.context.active_object
light.name = "Key_Light"
light.data.energy = 800
light.data.size = 600
```

## Workflow

1. **Load preferences** from `.blender-mcp/settings.md`
2. **If missing**: Prompt user and create settings
3. **Connect** to Blender MCP server on configured port
4. **Execute** requested Blender operations via Python code
5. **Report** results to user

## Notes

- Always verify the port is reachable before sending commands
- Use `bpy.context.active_object` to reference the currently selected object
- For complex operations, send multiple sequential commands
- The Blender instance must be running with the MCP server addon enabled on the configured port