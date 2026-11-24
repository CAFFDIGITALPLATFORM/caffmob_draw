#!/usr/bin/env python3
"""Reversa Debugger executável deste projeto.

Roda a suíte pura e a suíte Blender arquivo a arquivo, guarda a saída de cada ensaio, classifica
cada falha (defeito, ambiente/rede, performance ou obsoleto) e grava um relatório no repositório.

Uso:
    python3 _reversa_bugs/tools/reversa_debugger.py
    python3 _reversa_bugs/tools/reversa_debugger.py --suite pure
    python3 _reversa_bugs/tools/reversa_debugger.py --blender /opt/blender/blender --json

Saída:
    _reversa_bugs/plugin-caffmob-draw/inspections/<data>-debugger/
        report.md, results.json, pure/<teste>.log, blender/<teste>.log

Código de saída: 0 sem defeito candidato; 1 com defeito candidato; 2 erro de configuração.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
DEFAULT_BLENDER = shutil.which("blender") or "/opt/blender/blender"
DEFAULT_OUT = ROOT / "_reversa_bugs" / "plugin-caffmob-draw" / "inspections"

ENV_PATTERNS = (
    "online_access", "127.0.0.1", "moBI de ensaio", "mobi de ensaio", "connection refused",
    "network is unreachable", "urlopen", "does not name an extension", "extension_path_user",
    "sem rede", "sem conta", "nome de extensão", "servidor de ensaio",
)
PERF_TESTS = {"blender_066_cladding_bench.py", "blender_067_proto_snapshot.py"}
PERF_PATTERNS = ("p95", "confirmation_target", "preview_target", "performance", "demorou")
OBSOLETE_PATTERNS = ("obsoleto", "removido pela feature", "não é mais registrad")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean(text: str, limit: int = 500) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", text or "")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return " | ".join(lines[:3])[:limit]


def _diagnostic(output: str) -> str:
    """Primeira linha que parece causa, não ruído de Blender."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", output or "")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for needle in ("Traceback", "AssertionError", "Error:", "FALHA", "FAILED", "FAIL:", "ERROR:"):
        for i, line in enumerate(lines):
            if needle in line:
                return " \n".join(lines[i:i + 3])[:800]
    return _clean(output, 800)


def _classify(name: str, code: int, output: str) -> tuple[str, str]:
    low = (output or "").lower()
    if any(p in low for p in OBSOLETE_PATTERNS):
        return "obsoleto", "ensaio declara a funcionalidade removida"
    if any(p in low for p in ENV_PATTERNS):
        return "ambiente", "dependência externa indisponível (rede, MOBI ou extensão instalada)"
    if name in PERF_TESTS or any(p in low for p in PERF_PATTERNS):
        return "performance", "limite de tempo/percentil não atingido neste ambiente"
    if code == 124 or code < 0:
        return "defeito", "timeout ou sinal inesperado"
    return "defeito", "falha sem bloqueio externo identificado"


def _evidence_line(log_path: Path, classification: str) -> str:
    """Linha do log que sustenta a classificação (online_access, 127.0.0.1, p95...)."""
    if not log_path.is_file():
        return ""
    patterns = ENV_PATTERNS if classification == "ambiente" else PERF_PATTERNS
    text = log_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        low = line.lower()
        if any(p in low for p in patterns):
            return _clean(line, 800)
    return ""


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


class Runner:
    def __init__(self, suite: str, blender: str, pure_timeout: float, blender_timeout: float, out: Path,
                 keep_going: bool):
        self.suite, self.blender = suite, blender
        self.pure_timeout, self.blender_timeout = pure_timeout, blender_timeout
        self.out, self.keep_going = out, keep_going
        self.results: list[dict] = []

    def _tests(self, prefix: str) -> list[Path]:
        return sorted(p for p in TESTS.glob(prefix) if p.is_file() and p.suffix == ".py")

    def _run(self, path: Path, suite: str, timeout: float) -> dict:
        if suite == "pure":
            command = [sys.executable, str(path)]
        else:
            command = [self.blender, "--background", "--factory-startup", "--python-exit-code", "1",
                       "--python", str(path)]
        log = self.out / suite / (path.stem + ".log")
        log.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        code, output = 124, ""
        try:
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
            code, output = completed.returncode, (completed.stdout or "") + (completed.stderr or "")
        except subprocess.TimeoutExpired as exc:
            output = ((exc.stdout or "") + (exc.stderr or "")) if isinstance(exc.stdout, str) else ""
            output += f"\nTIMEOUT após {timeout:.0f} s\n"
        except FileNotFoundError:
            output = f"COMANDO NÃO ENCONTRADO: {command[0]}\n"
            code = 127
        log.write_text(output, encoding="utf-8", errors="replace")
        elapsed = time.monotonic() - started
        passed = code == 0
        classification, reason = ("passou", "") if passed else _classify(path.name, code, output)
        return {"suite": suite, "file": str(path.relative_to(ROOT)), "name": path.name, "exit": code,
                "passed": passed, "seconds": round(elapsed, 2), "classification": classification,
                "reason": reason, "diagnostic": "" if passed else _diagnostic(output),
                "log": _rel(log)}

    def run(self) -> None:
        if self.suite in ("pure", "all"):
            for path in self._tests("test_*.py"):
                result = self._run(path, "pure", self.pure_timeout)
                self._record(result)
        if self.suite in ("blender", "all"):
            if not Path(self.blender).exists():
                raise SystemExit(f"Blender não encontrado: {self.blender}")
            for path in self._tests("blender_*.py"):
                result = self._run(path, "blender", self.blender_timeout)
                self._record(result)

    def _record(self, result: dict) -> None:
        self.results.append(result)
        status = "OK" if result["passed"] else result["classification"].upper()
        print(f"[{status}] {result['file']} ({result['seconds']:.1f}s)", flush=True)
        if not result["passed"] and not self.keep_going:
            raise SystemExit(1)


def scan_bugs() -> list[dict]:
    bugs = []
    for path in sorted((ROOT / "_reversa_bugs").glob("*/bugs/*/bug.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        head = text.split("---", 2)[1] if text.startswith("---") else ""

        def field(name: str) -> str:
            match = re.search(rf"^{name}:\s*(.+)$", head, re.M)
            return match.group(1).strip().strip('"') if match else ""

        bugs.append({"id": field("id"), "display": field("display_number"), "status": field("status"),
                     "severity": field("severity"), "title": field("title"),
                     "context": path.parents[2].name, "locked": (path.parent / "DONE.md").exists()})
    return bugs


def summarize(results: list[dict]) -> dict:
    suites = {}
    for result in results:
        data = suites.setdefault(result["suite"], {"total": 0, "passed": 0, "failed": 0, "timeouts": 0,
                                                   "classifications": {}})
        data["total"] += 1
        if result["passed"]:
            data["passed"] += 1
        else:
            data["failed"] += 1
            if result["exit"] == 124:
                data["timeouts"] += 1
            data["classifications"][result["classification"]] = \
                data["classifications"].get(result["classification"], 0) + 1
    return suites


def write_report(out: Path, results: list[dict], bugs: list[dict], args: argparse.Namespace,
                 command: list[str] | None = None) -> None:
    suites = summarize(results)
    failures = [r for r in results if not r["passed"]]
    defects = [r for r in failures if r["classification"] == "defeito"]
    open_bugs = [b for b in bugs if b["status"] != "resolved"]
    now = _now()
    lines = [
        f"<!-- GENERATED by _reversa_bugs/tools/reversa_debugger.py em {now} -->",
        "# Reversa Debugger · execução real", "",
        "- Comando: `" + " ".join(command or sys.argv) + "`",
        f"- Executado em: {now}",
        f"- Saída: `{_rel(out)}/` (um log por ensaio)", "",
        "## Placar", "",
        "| Suíte | Arquivos | Passaram | Falharam | Timeouts | Classificação das falhas |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name in ("pure", "blender"):
        if name not in suites:
            continue
        data = suites[name]
        classes = ", ".join(f"{k}: {v}" for k, v in sorted(data["classifications"].items())) or "nenhuma"
        lines.append(f"| {name} | {data['total']} | {data['passed']} | {data['failed']} | {data['timeouts']} | {classes} |")
    lines += ["", "## Falhas restantes", ""]
    if not failures:
        lines.append("Nenhuma falha: as duas suítes passaram por inteiro.")
    else:
        lines += ["| Ensaio | Exit | Tempo | Classificação | Evidência |", "|---|---:|---:|---|---|"]
        for result in failures:
            lines.append(f"| `{result['file']}` | {result['exit']} | {result['seconds']:.1f}s | "
                         f"**{result['classification']}** | `{result['log']}` |")
        lines += ["", "### Diagnóstico por ensaio", ""]
        for result in failures:
            evidence = _evidence_line(ROOT / result["log"], result["classification"]) or result["diagnostic"]
            lines += [f"#### `{result['file']}` · {result['classification']}", "",
                      f"- Motivo: {result['reason']}",
                      f"- Log: `{result['log']}`",
                      f"- Trecho: `{evidence}`", ""]
    lines += ["## Registro Reversa", "",
              f"- Bugs registrados: {len(bugs)} · abertos: {len(open_bugs)} · "
              f"resolvidos: {len(bugs) - len(open_bugs)}", ""]
    if open_bugs:
        lines += ["| ID | # | Status | Contexto | Título |", "|---|---:|---|---|---|"]
        for bug in open_bugs:
            lines.append(f"| {bug['id']} | {bug['display']} | {bug['status']} | {bug['context']} | {bug['title']} |")
        lines.append("")
    lines += ["## Ações de debugger fix indicadas", ""]
    if defects:
        lines += ["1. Abrir os defeitos abaixo, reproduzir e corrigir com teste de regressão:", ""]
        lines += [f"   - `{r['file']}`: {r['diagnostic']}" for r in defects]
    else:
        lines.append("Nenhum defeito candidato. As falhas restantes estão bloqueadas por ambiente ou "
                     "por limite de performance, e não por lógica de produto.")
    report = out / "report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "results.json").write_text(json.dumps({"generated_at": now, "command": sys.argv,
                                                 "suites": suites, "results": results, "bugs": bugs,
                                                 "bugs_open": open_bugs}, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    print(f"\nRelatório: {_rel(report)}")
    print(f"Resumo: " + " · ".join(f"{k} {v['passed']}/{v['total']}" for k, v in suites.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reversa Debugger: roda as suítes e classifica as falhas.")
    parser.add_argument("--suite", choices=("all", "pure", "blender"), default="all")
    parser.add_argument("--blender", default=DEFAULT_BLENDER)
    parser.add_argument("--pure-timeout", type=float, default=45.0)
    parser.add_argument("--blender-timeout", type=float, default=360.0)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--keep-going", action="store_true", default=True,
                        help="continua depois de uma falha (padrão; use --fail-fast para parar)")
    parser.add_argument("--fail-fast", dest="keep_going", action="store_false")
    parser.add_argument("--json", action="store_true", help="imprime o results.json no stdout")
    parser.add_argument("--report-only", action="store_true",
                        help="regenera o report.md a partir do results.json e dos logs já gravados")
    args = parser.parse_args()
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    out = args.out or (DEFAULT_OUT / f"{stamp}-debugger")
    out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    previous = {}
    if (out / "results.json").is_file():
        try:
            previous = json.loads((out / "results.json").read_text(encoding="utf-8"))
        except ValueError:
            previous = {}
    if args.report_only:
        if not previous.get("results"):
            print(f"Sem results.json em {out} para regenerar o relatório.", file=sys.stderr)
            return 2
        write_report(out, previous["results"], scan_bugs(), args, previous.get("command"))
        return 1 if any(r["classification"] == "defeito" for r in previous["results"]) else 0
    try:
        runner = Runner(args.suite, args.blender, args.pure_timeout, args.blender_timeout, out, args.keep_going)
        runner.run()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.", file=sys.stderr)
        return 130
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return int(exc.code) if isinstance(exc.code, int) else 2
    bugs = scan_bugs()
    write_report(out, runner.results, bugs, args, sys.argv)
    print(f"Tempo total: {time.monotonic() - started:.1f}s")
    if args.json:
        print((out / "results.json").read_text(encoding="utf-8"))
    return 1 if any(r["classification"] == "defeito" for r in runner.results) else 0


if __name__ == "__main__":
    sys.exit(main())
