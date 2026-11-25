from __future__ import annotations

import argparse
import re
from pathlib import Path

ANCHOR_RE = re.compile(r"\s*\[�\]\(#[^)]+\)")
SKIP_RE = re.compile(r"^\s*\[(?:Skip to content|Back to top)\]\([^)]*\)\s*$", re.I)
EDIT_RE = re.compile(r"^\s*\[Edit this page\]\([^)]*\)\s*$", re.I)
INLINE_NAV_RE = re.compile(r"\[(?:Skip to content|Back to top|Edit this page)\]\([^)]*\)", re.I)
ON_PAGE_RE = re.compile(r"^\s*On this page\s*$", re.I)


def format_markdown(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace")
    text = original.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    in_fence = False
    for line in text.split("\n"):
        line = line.rstrip()
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            line = ANCHOR_RE.sub("", line)
            line = INLINE_NAV_RE.sub("", line)
            if SKIP_RE.match(line) or EDIT_RE.match(line):
                continue
            line = re.sub(r"\[([^\]]+)\]\(#[^)]+\)", r"\1", line) if line.strip().startswith("#") else line
            line = re.sub(r"[ \t]+", " ", line)
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?m)^(#{1,6} .+)\n(?!\n)", r"\1\n\n", text)
    text = text.strip() + "\n"
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Padroniza Markdown gerado da documentação Blender para leitura por agentes.")
    ap.add_argument("--docs", type=Path, default=Path.cwd() / "blender-docs-agent")
    args = ap.parse_args()
    files = sorted(args.docs.glob("**/*.md"))
    changed = sum(format_markdown(p) for p in files)
    print({"files": len(files), "changed": changed, "docs": str(args.docs)})


if __name__ == "__main__":
    main()
