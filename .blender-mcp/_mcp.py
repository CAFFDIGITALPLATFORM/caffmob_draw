"""Cliente mínimo do servidor MCP do Blender (127.0.0.1:9877, JSON terminado em NUL)."""

import json
import socket
import sys

PORT = 9877


def call(code, timeout=90):
    sock = socket.create_connection(("127.0.0.1", PORT), timeout=timeout)
    sock.settimeout(timeout)
    sock.sendall(json.dumps({"type": "execute", "code": code, "strict_json": True}).encode() + b"\0")
    buf = b""
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf += chunk
        if buf.endswith(b"\0"):
            break
    sock.close()
    return json.loads(buf.rstrip(b"\0").decode("utf-8", "replace"))


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        resposta = call(fh.read())
    texto = json.dumps(resposta, ensure_ascii=False, indent=2)
    print(texto[:8000])
