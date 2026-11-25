from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.request
from pathlib import Path

URLS = {
    "5.3": "https://docs.blender.org/api/5.3/blender_python_reference_5_3.zip",
    "5.4": "https://docs.blender.org/api/5.4/blender_python_reference_5_4.zip",
}


def main():
    ap = argparse.ArgumentParser(description="Baixa a Blender Python API oficial com retomada por Range.")
    ap.add_argument("--version", choices=URLS, default="5.4")
    ap.add_argument("--output", type=Path, default=Path.cwd() / "blender-docs-agent" / "api-source")
    ap.add_argument("--chunk-mib", type=int, default=4)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / f"blender_python_api_{args.version}.zip"
    part = target.with_suffix(".zip.part")
    url = URLS[args.version]

    if target.exists() and target.stat().st_size > 0:
        print(f"Já existe: {target}")
        return
    head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(head, timeout=60) as r:
            total = int(r.headers.get("Content-Length", "0"))
    except Exception:
        total = 0
    if not total:
        raise RuntimeError("Não foi possível obter o tamanho do ZIP da API.")
    chunk = args.chunk_mib * 1024 * 1024
    while (part.stat().st_size if part.exists() else 0) < total:
        start = part.stat().st_size if part.exists() else 0
        end = min(total - 1, start + chunk - 1)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*", "Range": f"bytes={start}-{end}"})
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    if start and r.status != 206:
                        raise IOError(f"servidor não aceitou Range: HTTP {r.status}")
                    data = r.read()
                if not data:
                    raise IOError("resposta vazia")
                with part.open("ab") as f:
                    f.write(data)
                print(f"{part.stat().st_size:,}/{total:,} bytes ({part.stat().st_size/total:.1%})", flush=True)
                break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt == 7:
                    raise
                print(f"tentativa {attempt + 1}/8: {exc}", flush=True)
                time.sleep(2 ** min(attempt, 4))
    if part.stat().st_size != total:
        raise IOError(f"download incompleto: {part.stat().st_size}/{total}")
    part.replace(target)
    print(f"Concluído: {target}")


if __name__ == "__main__":
    main()
