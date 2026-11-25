from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Busca local seletiva na documentação Markdown do Blender.")
    ap.add_argument("query", nargs="+", help="termo ou expressão a procurar")
    ap.add_argument("--docs", type=Path, default=Path.cwd() / "blender-docs-agent")
    ap.add_argument("--version", choices=["5.2", "5.3", "5.4", "api-5.4"])
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--context", type=int, default=420)
    args = ap.parse_args()
    query = " ".join(args.query).casefold()
    index = args.docs / "search_index.jsonl"
    if not index.exists():
        raise SystemExit(f"Índice não encontrado: {index}. Execute convert_blender_docs.py primeiro.")
    hits = []
    with index.open(encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if args.version and item["version"] != args.version:
                continue
            haystack = " ".join([item["title"], *item.get("headings", []), item.get("summary", "")]).casefold()
            if query in haystack:
                hits.append(item)
            if len(hits) >= args.limit:
                break
    for i, item in enumerate(hits, 1):
        page = args.docs / item["path"]
        text = page.read_text(encoding="utf-8", errors="replace")
        pos = text.casefold().find(query)
        if pos < 0:
            snippet = item.get("summary", "")
        else:
            snippet = re.sub(r"\s+", " ", text[max(0, pos - args.context):pos + len(query) + args.context])
        print(f"\n[{i}] Blender {item['version']} — {item['title']}\n{item['path']}\n{snippet}")
    print(f"\nResultados: {len(hits)}")


if __name__ == "__main__":
    main()
