from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

DEFAULT_ZIPS = {
    "5.2": "blender_manual_html_5_2.zip",
    "5.3": "blender_manual_html_5_3.zip",
    "5.4": "blender_manual_html_5_4.zip",
}
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "aside"}
BLOCK_TAGS = {"p", "div", "section", "article", "main", "blockquote", "figure", "figcaption", "dl", "dt", "dd"}


def clean_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("._")
    return value or "page"


def normalize_url(href: str) -> str:
    href = html.unescape(href or "").strip()
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return href
    return href.replace("\\", "/")


class MarkdownParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.stack: list[str] = []
        self.skip_depth = 0
        self.pre_depth = 0
        self.code_depth = 0
        self.link_stack: list[str] = []
        self.list_stack: list[str] = []
        self.table_row: list[str] = []
        self.in_heading = False
        self.headings: list[str] = []

    def emit(self, text: str):
        if self.skip_depth or not text:
            return
        self.out.append(text)

    def newline(self, count=1):
        if self.skip_depth:
            return
        self.out.append("\n" * count)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attr = dict(attrs)
        self.stack.append(tag)
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if tag == "main":
            return
        if tag == "pre":
            self.pre_depth += 1
            self.newline(2)
            self.emit("```text\n")
        elif tag == "code" and not self.pre_depth:
            self.code_depth += 1
            self.emit("`")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = True
            self.newline(2)
            self.emit("#" * int(tag[1]) + " ")
        elif tag in BLOCK_TAGS:
            self.newline(2)
        elif tag == "br":
            self.newline()
        elif tag == "a":
            self.link_stack.append(normalize_url(attr.get("href", "")))
            self.emit("[")
        elif tag == "ul":
            self.list_stack.append("-")
            self.newline(2)
        elif tag == "ol":
            self.list_stack.append("1.")
            self.newline(2)
        elif tag == "li":
            marker = self.list_stack[-1] if self.list_stack else "-"
            self.newline()
            self.emit(marker + " ")
        elif tag == "strong" or tag == "b":
            self.emit("**")
        elif tag == "em" or tag == "i":
            self.emit("*")
        elif tag == "table":
            self.newline(2)
        elif tag == "tr":
            self.table_row = []
        elif tag in {"th", "td"}:
            self.table_row.append("")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            if self.stack:
                self.stack.pop()
            return
        if tag == "pre":
            self.emit("\n```")
            self.pre_depth = max(0, self.pre_depth - 1)
        elif tag == "code" and not self.pre_depth:
            self.emit("`")
            self.code_depth = max(0, self.code_depth - 1)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = False
            self.newline(2)
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            self.emit("](" + href + ")" if href else "]")
        elif tag == "ul" or tag == "ol":
            if self.list_stack:
                self.list_stack.pop()
            self.newline()
        elif tag == "li":
            self.newline()
        elif tag == "strong" or tag == "b":
            self.emit("**")
        elif tag == "em" or tag == "i":
            self.emit("*")
        elif tag == "tr" and self.table_row:
            row = [re.sub(r"\s+", " ", x).strip() for x in self.table_row]
            self.newline()
            self.emit("| " + " | ".join(row) + " |")
            self.table_row = []
        elif tag in BLOCK_TAGS:
            self.newline()
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.pre_depth:
            self.emit(data)
            return
        text = re.sub(r"\s+", " ", data)
        if not text.strip():
            return
        text = text.replace("|", "\\|")
        self.emit(text)
        if self.in_heading:
            self.headings.append(text.strip())

    def result(self) -> tuple[str, list[str]]:
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip() + "\n", list(dict.fromkeys(self.headings))


def convert_html(raw: bytes) -> tuple[str, list[str]]:
    parser = MarkdownParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return parser.result()


def find_html(zf: zipfile.ZipFile):
    for name in zf.namelist():
        low = name.lower()
        if low.endswith(".html") and "/_" not in low and not low.endswith("/index.html"):
            yield name
        elif low.endswith("/index.html"):
            yield name


def safe_output_path(root: Path, name: str) -> Path:
    rel = PurePosixPath(name).with_suffix(".md")
    rel = Path(*[clean_name(p) for p in rel.parts])
    return root / rel


def convert_version(zip_path: Path, version: str, out_root: Path, index_file, manifest: dict):
    version_root = out_root / f"manual-{version}"
    version_root.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = list(find_html(zf))
        for name in names:
            raw = zf.read(name)
            markdown, headings = convert_html(raw)
            if len(markdown.strip()) < 80:
                continue
            dest = safe_output_path(version_root, name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            title = headings[0] if headings else PurePosixPath(name).stem
            header = f"---\nversion: '{version}'\nsource_html: '{name}'\ntitle: {json.dumps(title, ensure_ascii=False)}\n---\n\n"
            dest.write_text(header + markdown, encoding="utf-8")
            summary = re.sub(r"\s+", " ", markdown)[:700]
            index_file.write(json.dumps({"version": version, "title": title, "path": str(dest.relative_to(out_root)).replace("\\", "/"), "headings": headings[:30], "summary": summary}, ensure_ascii=False) + "\n")
            count += 1
    manifest[version] = {"zip": str(zip_path), "pages": count}
    return count


def main():
    ap = argparse.ArgumentParser(description="Converter local dos manuais HTML do Blender para Markdown pesquisável.")
    ap.add_argument("--input", type=Path, default=Path.cwd())
    ap.add_argument("--output", type=Path, default=Path.cwd() / "blender-docs-agent")
    ap.add_argument("--versions", nargs="+", default=["5.2", "5.3", "5.4"])
    ap.add_argument("--api-zip", type=Path, help="ZIP oficial da Blender Python API a incluir no índice")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    out = args.output.resolve()
    source_paths = [args.input / DEFAULT_ZIPS[version] for version in args.versions]
    for source_path in source_paths:
        if not source_path.exists():
            raise FileNotFoundError(source_path)
    if args.api_zip and not args.api_zip.exists():
        raise FileNotFoundError(args.api_zip)
    if out.exists() and args.force:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"tool": "convert_blender_docs.py", "format": "markdown", "versions": {}, "files": {}}
    index_path = out / "search_index.jsonl"
    with index_path.open("w", encoding="utf-8") as idx:
        total = 0
        for version in args.versions:
            zip_path = args.input / DEFAULT_ZIPS[version]
            total += convert_version(zip_path, version, out, idx, manifest["versions"])
        if args.api_zip:
            total += convert_version(args.api_zip, "api-5.4", out, idx, manifest["versions"])
    manifest["files"] = {"pages_markdown": total, "search_index": "search_index.jsonl"}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "README.md").write_text("# Blender Manual Markdown\n\nDocumentação convertida para uso local por agentes. Use `search_index.jsonl` para localizar páginas sem carregar tudo no contexto.\n\nVersões: 5.2, 5.3 e 5.4.\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise
