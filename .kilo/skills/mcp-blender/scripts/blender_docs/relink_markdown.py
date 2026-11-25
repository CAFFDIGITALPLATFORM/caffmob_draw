from __future__ import annotations

import argparse
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_RE = re.compile(r"(?P<open>\]\()(?P<href>[^)\s]+)(?P<close>\))")
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".zip", ".epub", ".pdf"}


def rel_from_source(current: str, href_path: str) -> str:
    current_dir = posixpath.dirname(current.replace("\\", "/"))
    return posixpath.normpath(posixpath.join(current_dir, href_path.replace("\\", "/")))


def candidate_paths(target: str):
    target = target.lstrip("./")
    if target.lower().endswith(".html"):
        yield target[:-5] + ".md"
    elif target.endswith("/"):
        yield target + "index.md"
    else:
        yield target


def rewrite_file(path: Path, root: Path, known: set[str], stats: dict):
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")

    def replace(match: re.Match) -> str:
        href = match.group("href")
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or href.startswith(("#", "//", "mailto:")):
            stats["external_or_anchor"] += 1
            return match.group(0)
        decoded = unquote(parsed.path)
        if Path(decoded).suffix.lower() in SKIP_EXTENSIONS:
            stats["asset_links"] += 1
            return match.group(0)
        if not decoded.lower().endswith(".html") and not decoded.endswith("/"):
            stats["other_links"] += 1
            return match.group(0)
        source_target = rel_from_source(relative, decoded)
        destination = None
        for candidate in candidate_paths(source_target):
            if candidate in known:
                destination = candidate
                break
        if not destination:
            stats["missing_html_targets"] += 1
            stats["missing_examples"].setdefault(href, relative)
            return match.group(0)
        link_path = posixpath.relpath(destination, posixpath.dirname(relative) or ".")
        if not link_path.startswith("."):
            link_path = "./" + link_path
        rewritten = link_path
        if parsed.query:
            rewritten += "?" + parsed.query
        if parsed.fragment:
            rewritten += "#" + parsed.fragment
        stats["rewritten"] += 1
        return match.group("open") + rewritten + match.group("close")

    updated = LINK_RE.sub(replace, text)
    if updated != text:
        path.write_text(updated, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Religa links internos .html para .md em uma base Markdown.")
    ap.add_argument("--docs", type=Path, default=Path.cwd() / "blender-docs-agent")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    root = args.docs.resolve()
    files = sorted(root.glob("manual-*/**/*.md"))
    known = {p.relative_to(root).as_posix() for p in files}
    stats = {"files": len(files), "files_changed": 0, "rewritten": 0, "missing_html_targets": 0, "missing_examples": {}, "external_or_anchor": 0, "asset_links": 0, "other_links": 0}
    for path in files:
        if rewrite_file(path, root, known, stats):
            stats["files_changed"] += 1
    stats["missing_examples"] = dict(list(stats["missing_examples"].items())[:100])
    report = args.report or root / "LINK_REPORT.json"
    report.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
