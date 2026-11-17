"""Regenera as views do contexto editor-de-paredes a partir dos bug.md e do catalog.jsonl.

Uso: py -3 _reversa_bugs/editor-de-paredes/generated/regenerate.py

Projeção pura: nada aqui escreve em bug.md, em evidência ou em fix. As contagens saem do front matter de cada bug e a
regra de fechamento é a do README do registro (resolved exige DONE.md; fixed exige veredito, causa raiz e regressão).
"""

import glob
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

CTX = "editor-de-paredes"
OUT = os.path.join("_reversa_bugs", CTX, "generated")
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
HDR = f"<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em {TS} a partir de {{}} bugs -->"
CINZA, AMARELO, VERDE = "#30363d", "#f5d90a", "#30a46c"
VERMELHO = "#e5484d"


def escalar(fm, chave):
    m = re.search(rf"^{chave}: (.+)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v in ("null", "~", "") else v


def lista(fm, chave):
    m = re.search(rf"^  {chave}:(.*)$", fm, re.M)
    if not m:
        return []
    resto = m.group(1).strip()
    if resto.startswith("["):
        return [x.strip().strip('"').strip("'") for x in resto.strip("[]").split(",") if x.strip()]
    itens = []
    for linha in fm[m.end():].splitlines():
        mm = re.match(r"^    - (.+)$", linha)
        if not mm:
            break
        itens.append(mm.group(1).strip().strip('"').strip("'"))
    return itens


def carregar():
    caminho = os.path.join(OUT, "catalog.jsonl")
    cat = [json.loads(l) for l in open(caminho, encoding="utf-8") if l.strip()]
    for b in cat:
        p = os.path.join(b["path"], "bug.md")
        if os.path.isfile(p):
            t = open(p, encoding="utf-8").read()
            fm = t.split("---")[1]
            for chave in ("status", "phase", "severity", "priority", "resolution_kind", "spec_verdict", "title"):
                valor = escalar(fm, chave)
                if valor is not None:
                    b[chave] = valor
            m = re.search(r"^closure:\n  policy: (\S+)\n  satisfied: (\w+)", fm, re.M)
            if m:
                b["closure"] = {"policy": m.group(1), "satisfied": m.group(2) == "true"}
            tr = dict(b.get("traceability") or {})
            for chave in ("specs", "affected_code", "reproduction_tests", "regression_tests"):
                tr[chave] = lista(fm, chave)
            m = re.search(r"^  root_cause:\n    state: (\S+)", fm, re.M)
            tr["root_cause"] = None if not m else {"state": m.group(1)}
            b["traceability"] = tr
        b["_done"] = os.path.isfile(os.path.join(b["path"], "DONE.md"))
        b["_data"] = b.get("updated") or ""
        if b["_done"]:
            m = re.search(r"Encerrado em (\d{4}-\d{2}-\d{2})",
                          open(os.path.join(b["path"], "DONE.md"), encoding="utf-8").read())
            if m:
                b["_data"] = m.group(1)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        for b in cat:
            f.write(json.dumps({k: v for k, v in b.items() if not k.startswith("_")}, ensure_ascii=False) + "\n")
    return cat


def curto(texto, limite):
    return texto if len(texto) <= limite else texto[:limite].rstrip() + "…"


def celula(ids):
    return ", ".join(sorted(ids)) if ids else "nenhum"


def escrever(nome, linhas):
    with open(os.path.join(OUT, nome), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas) + "\n")


def index(todos, abertos, resolvidos, achados):
    linhas = [HDR.format(len(todos)), "", f"# Bugs · {CTX}", "", "## Resumo", "", "| status | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in sorted(Counter(b["status"] for b in todos).items())]
    linhas += ["", "| phase | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in sorted(Counter(b["phase"] for b in todos).items())]
    linhas += ["", "## Abertos / ativos", "",
               "| # | ID | prioridade | severidade | area/module/feature | título | caminho | bloqueado |",
               "|---|---|---|---|---|---|---|---|"]
    for b in abertos:
        bloqueio = ", ".join(x["target"] for x in (b.get("blocking") or []))
        linhas.append(f'| {b["display_number"]} | {b["id"]} | {b["priority"]} | {b["severity"]} | '
                      f'{b["area"]}/{b["module"]}/{b["feature"]} | {b["title"]} | `{b["path"]}` | '
                      f'{"sim (" + bloqueio + ")" if bloqueio else "não"} |')
    linhas += ["", "## Resolvidos", "", "| resolution_kind | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in sorted(Counter(b.get("resolution_kind") or "null" for b in resolvidos).items())]
    linhas.append("")
    for b in resolvidos:
        trava = "travado: " if b["_done"] else "sem trava: "
        linhas.append(f'- #{b["display_number"]} {b["id"]} ({b.get("resolution_kind")}) · {trava}{b["title"]}')
    if achados:
        linhas += ["", "## Inconsistências", "",
                   "Invariantes do registro violadas no front matter. O gerador não conserta: a decisão é humana.", ""]
        linhas += [f"- {x}" for x in achados]
    escrever("index.md", linhas)


def matrix(todos, bugs):
    linhas = [HDR.format(len(todos)), "", f"# Relações · {CTX}", "",
              "| origem | tipo | destino | state | evidência? |", "|---|---|---|---|---|"]
    for b in todos:
        for r in b.get("relationships") or []:
            alvo = f'{r["bug"]} ({bugs[r["bug"]]["module"]})' if r["bug"] in bugs else f'{r["bug"]} (externo)'
            linhas.append(f'| {b["id"]} | {r["type"]} | {alvo} | {r["state"]} | '
                          f'{"sim" if r.get("evidence") else "não"} |')
    escrever("matrix.md", linhas)


def spec_matrix(todos, addendos):
    por_spec = defaultdict(lambda: {"open": [], "active": [], "resolved": []})
    for b in todos:
        for spec in (b.get("traceability") or {}).get("specs") or []:
            por_spec[spec][b["status"]].append(b["id"])
    gap = {"open": [], "active": [], "resolved": []}
    for b in todos:                      # o veredito manda; sem ele, o label de triagem ainda marca a lacuna
        if b.get("spec_verdict") == "spec-gap" or "spec-gap" in (b.get("labels") or []):
            gap[b["status"]].append(b["id"])
    linhas = [HDR.format(len(todos)), "", f"# Bugs × specs · {CTX}", "",
              "| spec | open | active | resolved |", "|---|---|---|---|"]
    for spec in sorted(por_spec):
        d = por_spec[spec]
        linhas.append(f'| `{spec}` | {celula(d["open"])} | {celula(d["active"])} | {celula(d["resolved"])} |')
    if any(gap.values()):
        linhas.append(f'| **spec-gap** | {celula(gap["open"])} | {celula(gap["active"])} | {celula(gap["resolved"])} |')
    linhas += ["", "## Adendos de bug vigentes", ""]
    linhas += [f"- `_reversa_sdd/addenda/{a}`" for a in addendos]
    escrever("spec-matrix.md", linhas)


def graph_md(todos, abertos, arestas):
    linhas = [HDR.format(len(todos)), "", f"# Grafo · {CTX}", "", "```mermaid", "graph LR"]
    for b in todos:
        linhas.append(f'  {b["id"].replace("-", "_")}["#{b["display_number"]} {curto(b["title"], 40)}"]')
    for b, r in arestas:
        seta = "-.->|" if r["state"] == "proposed" else "-->|"
        linhas.append(f'  {b["id"].replace("-", "_")} {seta}{r["type"]}| {r["bug"].replace("-", "_")}')
    linhas += ["```", "", "## Clusters", ""]
    clusters = defaultdict(list)
    for b in todos:
        for arq in (b.get("traceability") or {}).get("affected_code") or []:
            clusters[arq].append(b["id"])
    ordem = sorted(clusters.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for arq, ids in ordem:
        if len(ids) > 1:
            linhas.append(f'- `{arq}`: {len(ids)} bugs ({", ".join(ids)})')
    if ordem:
        arq, ids = ordem[0]
        no_aberto = sum(1 for b in abertos if arq in ((b.get("traceability") or {}).get("affected_code") or []))
        linhas += ["", f"Leitura: {len(ids)} bugs convergem em `{arq}`, o maior ponto de convergência do contexto. "
                       f"Dos {len(abertos)} abertos, {no_aberto} apontam para esse arquivo."]
    score = Counter()
    for b, r in arestas:
        if r["state"] in ("supported", "confirmed"):
            score[b["id"]] += 1
            score[r["bug"]] += 1
    linhas += ["", "## Impact score", "",
               "Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.", "",
               "| # | ID | score |", "|---|---|---|"]
    for i, v in sorted(score.items(), key=lambda kv: (-kv[1], kv[0])):
        if i in {b["id"] for b in todos}:
            linhas.append(f'| {next(b["display_number"] for b in todos if b["id"] == i)} | {i} | {v} |')
    escrever("graph.md", linhas)


def graph_html(todos, abertos, resolvidos, arestas, addendos, inconsist):
    cols, x0, y0, passo_x, passo_y, w, h = 4, 40, 40, 290, 150, 250, 100
    linhas = math.ceil(len(todos) / cols)
    largura, altura = 1200, y0 + (linhas - 1) * passo_y + h + 40
    pos = {b["id"]: (x0 + (i % cols) * passo_x, y0 + (i // cols) * passo_y) for i, b in enumerate(todos)}
    pecas = ['<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto"><path d="M0 0L10 5L0 10z" fill="#8aa"/></marker></defs>']
    for b, r in arestas:
        if r["bug"] not in pos:
            continue
        ax, ay = pos[b["id"]]
        bx, by = pos[r["bug"]]
        x1, y1, x2, y2 = ax + w / 2, ay + h / 2, bx + w / 2, by + h / 2
        tracejado = ' stroke-dasharray="6 4"' if r["state"] == "proposed" else ""
        pecas.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#8aa"{tracejado} '
                     f'marker-end="url(#a)" opacity=".7"/><text x="{(x1 + x2) / 2:.0f}" y="{(y1 + y2) / 2 - 6:.0f}" '
                     f'fill="#9bb" font-size="11" text-anchor="middle">{r["type"]}</text>')
    for b in todos:
        x, y = pos[b["id"]]
        contorno = VERMELHO if b["severity"] in ("critical", "high") else AMARELO if b["severity"] == "medium" else CINZA
        tinta = VERDE if b["status"] == "resolved" else VERMELHO
        pecas.append(f'<a href="../bugs/{os.path.basename(b["path"])}/bug.md">'
                     f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#1c2128" stroke="{contorno}" '
                     f'stroke-width="2"/><text x="{x + 12}" y="{y + 24}" fill="#e6edf3" font-size="13" '
                     f'font-weight="600">#{b["display_number"]} {b["id"].split("-")[-1]} · {b["priority"]}</text>'
                     f'<text x="{x + 12}" y="{y + 46}" fill="#c9d1d9" font-size="12">{curto(b["title"], 31)}</text>'
                     f'<text x="{x + 12}" y="{y + 66}" fill="#8b949e" font-size="11">{b["severity"]} · {b["area"]}'
                     f'</text><text x="{x + 12}" y="{y + 86}" fill="{tinta}" font-size="11">{b["status"]} · '
                     f'{b["phase"]}</text></a>')
    tabela = ""
    for b in abertos:
        bloqueio = ", ".join(x["target"] for x in (b.get("blocking") or []))
        status = f'{b["status"]} · {b["phase"]}' + (f" (bloqueado por {bloqueio})" if bloqueio else "")
        tabela += (f'<tr><td>{b["display_number"]}</td><td><a href="../bugs/{os.path.basename(b["path"])}/bug.md">'
                   f'{b["id"]}</a></td><td>{b["severity"]}</td><td>{b["priority"]}</td><td>{b["title"]}</td>'
                   f'<td>{b["area"]}/{b["module"]}/{b["feature"]}</td><td>{status}</td></tr>')
    travados = "".join(f'<li><a href="../bugs/{os.path.basename(b["path"])}/bug.md">#{b["display_number"]} {b["id"]}'
                       f'</a> · {b["_data"]} · {b.get("resolution_kind")} · {b["title"]}</li>' for b in resolvidos)
    grau = Counter()
    for b, r in arestas:
        grau[b["id"]] += 1
        grau[r["bug"]] += 1
    maximo = max(grau.values()) if grau else 0
    topo = ", ".join("#" + str(b["display_number"]) for b in todos if grau.get(b["id"]) == maximo)
    confirmadas = sum(1 for _b, r in arestas if r["state"] in ("supported", "confirmed"))
    css = ("body{background:#0d1117;color:#e6edf3;font:14px system-ui,sans-serif;margin:0;padding:16px}\n"
           ".meta{color:#8b949e;font-size:12px}.cards{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}\n"
           ".card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 16px;min-width:120px}\n"
           ".card b{font-size:22px;display:block}svg{max-width:100%;height:auto;background:#0d1117}\n"
           "table{border-collapse:collapse;width:100%;margin-top:8px}"
           "td,th{border-bottom:1px solid #30363d;padding:6px;text-align:left;font-size:13px}\n"
           "a{color:#58a6ff}.wrap{overflow-x:auto}")
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>Grafo de Bugs · {CTX}</title><style>\n{css}</style></head><body>\n'
            f'<h1>Grafo de Bugs · {CTX}</h1>\n'
            f'<p class="meta">Gerado por /reversa-debugger-graph em {TS} · {len(todos)} bugs · '
            f'{len(inconsist)} inconsistências · arestas tracejadas = relação proposed (hipótese)</p>\n'
            f'<div class="cards"><div class="card"><b>{len(todos)}</b>bugs</div>'
            f'<div class="card"><b>{len(resolvidos)}</b>resolved · fixed</div>\n'
            f'<div class="card"><b>{len(abertos)}</b>abertos/ativos</div>'
            f'<div class="card"><b>{len(addendos)}</b>adendos de spec</div>\n'
            f'<div class="card"><b>{len(inconsist)}</b>inconsistências</div></div>\n'
            f'<div class="wrap"><svg viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}" '
            f'role="img" aria-label="Grafo de bugs">\n' + "\n".join(pecas) + "\n</svg></div>\n"
            f'<p>Os nós com mais ligações são {topo} ({maximo} ligações cada). Há {confirmadas} relação(ões) '
            f'supported/confirmed; as demais são hipóteses de triagem e não pesam no impact score.</p>\n'
            f'<h2>Bugs abertos / ativos</h2><div class="wrap"><table><tr><th>#</th><th>ID</th>'
            f'<th>severidade</th><th>prioridade</th><th>título</th><th>area/module/feature</th><th>status</th></tr>\n'
            f'{tabela}\n</table></div>')
    if inconsist:
        html += "<h2>Inconsistências</h2><ul>" + "".join(f"<li>{x}</li>" for x in inconsist) + "</ul>"
    html += f'<h2>Concluídos (travados)</h2><ul>\n{travados}\n</ul></body></html>'
    with open(os.path.join(OUT, "graph.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html + "\n")


def inconsistencias(todos):
    achados = []
    for b in todos:
        tr = b.get("traceability") or {}
        if b["status"] == "resolved" and not b["_done"]:
            achados.append(f'{b["id"]}: resolved sem DONE.md')
        if b["status"] != "resolved" and b["_done"]:
            achados.append(f'{b["id"]}: DONE.md com status {b["status"]}')
        if b.get("resolution_kind") == "fixed":
            if not b.get("spec_verdict"):
                achados.append(f'{b["id"]}: fixed sem veredito de spec')
            if not (tr.get("root_cause") or {}).get("state"):
                achados.append(f'{b["id"]}: fixed sem causa raiz registrada')
            elif (tr.get("root_cause") or {}).get("state") != "confirmed":
                achados.append(f'{b["id"]}: fixed com causa em {(tr.get("root_cause") or {}).get("state")}, '
                               f'exige confirmed')
            if not tr.get("regression_tests"):
                achados.append(f'{b["id"]}: fixed sem teste de regressão')
    return achados


def main():
    cat = carregar()
    todos = sorted(cat, key=lambda b: b["display_number"])
    bugs = {b["id"]: b for b in todos}
    abertos = [b for b in todos if b["status"] in ("open", "active")]
    resolvidos = [b for b in todos if b["status"] == "resolved"]
    arestas = [(b, r) for b in todos for r in (b.get("relationships") or [])]
    addendos = sorted(os.path.basename(p) for p in glob.glob(os.path.join("_reversa_sdd", "addenda", "*.md")))
    achados = inconsistencias(todos)
    index(todos, abertos, resolvidos, achados)
    matrix(todos, bugs)
    spec_matrix(todos, addendos)
    graph_md(todos, abertos, arestas)
    graph_html(todos, abertos, resolvidos, arestas, addendos, achados)
    print(f"bugs {len(todos)} · abertos {len(abertos)} · resolvidos {len(resolvidos)} · "
          f"addendos {len(addendos)} · arestas {len(arestas)}")
    print("inconsistências:", achados or "nenhuma")


if __name__ == "__main__":
    main()
