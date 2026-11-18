"""Regenera as views de todos os contextos de _reversa_bugs e o espelho das specs.

Uso:
    py -3 _reversa_bugs/editor-de-paredes/generated/regenerate.py
    py -3 _reversa_bugs/editor-de-paredes/generated/regenerate.py editor-de-paredes walls2d

Projeção pura: o bug.md é a única fonte de verdade. Nada aqui escreve em bug.md, em evidência ou em fix. O script lê o
front matter de cada bug, valida as invariantes do README do registro e reescreve apenas as views em
<_reversa_bugs/contexto>/generated/ e o espelho _reversa_sdd/traceability/bugs.md.
"""

import glob
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone

RAIZ = "_reversa_bugs"
ESPELHO = os.path.join("_reversa_sdd", "traceability", "bugs.md")
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
HDR = f"<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em {TS} a partir de {{}} bugs -->"
CINZA, AMARELO, VERDE, VERMELHO = "#30363d", "#f5d90a", "#30a46c", "#e5484d"


# ---------------------------------------------------------------------------------------------------------------
# Leitura do front matter (subconjunto de YAML usado pelo schema dos bugs, sem dependência externa)
# ---------------------------------------------------------------------------------------------------------------


def _sem_aspas(txt):
    txt = txt.strip()
    if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in "\"'":
        return txt[1:-1]
    return txt


def _dividir(txt):
    """Separa itens de uma lista inline respeitando aspas, chaves e colchetes."""
    itens, atual, profundidade, aspas = [], [], 0, None
    for c in txt:
        if aspas:
            atual.append(c)
            if c == aspas:
                aspas = None
            continue
        if c in "\"'":
            aspas = c
        elif c in "[{":
            profundidade += 1
        elif c in "]}":
            profundidade -= 1
        elif c == "," and profundidade == 0:
            itens.append("".join(atual))
            atual = []
            continue
        atual.append(c)
    if "".join(atual).strip():
        itens.append("".join(atual))
    return [i.strip() for i in itens if i.strip()]


def _valor(txt):
    txt = txt.strip()
    if txt.startswith("[") and txt.endswith("]"):
        return [_sem_aspas(i) for i in _dividir(txt[1:-1])]
    if txt.startswith("{") and txt.endswith("}"):
        mapa = {}
        for item in _dividir(txt[1:-1]):
            chave, _, resto = item.partition(":")
            mapa[_sem_aspas(chave)] = _valor(resto)
        return mapa
    return _sem_aspas(txt)


def _recuo(linha):
    return len(linha) - len(linha.lstrip(" "))


def _filho(linhas, i, prof):
    """Valor aninhado de uma chave sem valor na linha: lista, bloco ou nulo."""
    j = i
    while j < len(linhas) and not linhas[j].strip():
        j += 1
    if j >= len(linhas) or _recuo(linhas[j]) <= prof:
        return None, i
    if linhas[j].strip().startswith("- "):
        return _lista(linhas, j, _recuo(linhas[j]))
    return _bloco(linhas, j, _recuo(linhas[j]))


def _bloco(linhas, i, prof):
    mapa = {}
    while i < len(linhas):
        linha = linhas[i]
        if not linha.strip():
            i += 1
            continue
        if _recuo(linha) < prof:
            break
        if _recuo(linha) > prof:
            i += 1
            continue
        chave, _, resto = linha.strip().partition(":")
        chave, resto = chave.strip(), resto.strip()
        i += 1
        if resto:
            mapa[chave] = _valor(resto)
        else:
            mapa[chave], i = _filho(linhas, i, prof)
    return mapa, i


def _lista(linhas, i, prof):
    itens = []
    while i < len(linhas):
        linha = linhas[i]
        if not linha.strip():
            i += 1
            continue
        if _recuo(linha) < prof:
            break
        if _recuo(linha) > prof:
            i += 1
            continue
        texto = linha.strip()
        if not texto.startswith("- "):
            break
        conteudo = texto[2:].strip()
        i += 1
        if conteudo.startswith("{"):
            itens.append(_valor(conteudo))
            continue
        chave, separador, resto = conteudo.partition(":")
        if not separador:
            itens.append(_sem_aspas(conteudo))
            continue
        item = {}
        chave, resto = chave.strip(), resto.strip()
        if resto:
            item[chave] = _valor(resto)
        else:
            item[chave], i = _filho(linhas, i, prof)
        while i < len(linhas) and linhas[i].strip() and _recuo(linhas[i]) == prof + 2:
            k2, _, r2 = linhas[i].strip().partition(":")
            k2, r2 = k2.strip(), r2.strip()
            i += 1
            if r2:
                item[k2] = _valor(r2)
            else:
                item[k2], i = _filho(linhas, i, prof + 2)
        itens.append(item)
    return itens, i


def front_matter(texto):
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return {}
    try:
        fim = next(k for k in range(1, len(linhas)) if linhas[k].strip() == "---")
    except StopIteration:
        return {}
    mapa, _ = _bloco(linhas[1:fim], 0, 0)
    return mapa


# ---------------------------------------------------------------------------------------------------------------
# Carga e validação globais
# ---------------------------------------------------------------------------------------------------------------


def contextos():
    if not os.path.isdir(RAIZ):
        return []
    return sorted(d for d in os.listdir(RAIZ) if os.path.isdir(os.path.join(RAIZ, d, "bugs")))


def carregar():
    bugs = []
    for ctx in contextos():
        for pasta in sorted(glob.glob(os.path.join(RAIZ, ctx, "bugs", "*"))):
            caminho = os.path.join(pasta, "bug.md")
            if not os.path.isfile(caminho):
                continue
            with open(caminho, encoding="utf-8") as f:
                fm = front_matter(f.read())
            fm["id"] = fm.get("id") or os.path.basename(pasta).split("-")[:3]
            for chave in ("display_number", "schema_version"):
                if str(fm.get(chave) or "").isdigit():
                    fm[chave] = int(fm[chave])
            if isinstance(fm.get("closure"), dict):
                fm["closure"]["satisfied"] = str(fm["closure"].get("satisfied")).lower() == "true"
            fm["path"] = pasta.replace("\\", "/")
            fm["context"] = ctx
            fm["locked"] = os.path.isfile(os.path.join(pasta, "DONE.md"))
            fm["_data"] = fm.get("updated") or ""
            if fm["locked"]:
                with open(os.path.join(pasta, "DONE.md"), encoding="utf-8") as f:
                    m = re.search(r"Encerrado em (\d{4}-\d{2}-\d{2})", f.read())
                if m:
                    fm["_data"] = m.group(1)
            bugs.append(fm)
    return bugs


def _specs(b):
    return (b.get("traceability") or {}).get("specs") or []


def validar(bugs):
    """Invariantes do README do registro, sempre globais (cruzando contextos)."""
    achados, por_id = [], defaultdict(list)
    for b in bugs:
        por_id[b["id"]].append(b)
    for bid, lista in por_id.items():
        if len(lista) > 1:
            achados.append(f"{bid}: ID duplicado em " + ", ".join(b["context"] for b in lista))
    for b in bugs:
        bid, tr = b["id"], b.get("traceability") or {}
        if b.get("schema_version") not in (1, "1"):
            achados.append(f"{bid}: schema_version {b.get('schema_version')} desconhecida")
        resolvido = b.get("status") == "resolved"
        if resolvido and not b.get("resolution_kind"):
            achados.append(f"{bid}: resolved sem resolution_kind")
        if resolvido and (b.get("closure") or {}).get("satisfied") not in (True, "true"):
            achados.append(f"{bid}: resolved com closure.satisfied diferente de true")
        if b.get("resolution_kind") == "fixed":
            if not b.get("spec_verdict"):
                achados.append(f"{bid}: fixed sem veredito de spec")
            estado = (tr.get("root_cause") or {}).get("state")
            if not estado:
                achados.append(f"{bid}: fixed sem causa raiz registrada")
            elif estado != "confirmed":
                achados.append(f"{bid}: fixed com causa em {estado}, exige confirmed")
            if not tr.get("regression_tests"):
                achados.append(f"{bid}: fixed sem teste de regressão")
        if resolvido and not b["locked"]:
            achados.append(f"{bid}: resolved sem DONE.md")
        if not resolvido and b["locked"]:
            achados.append(f"{bid}: DONE.md com status {b.get('status')}")
        for r in b.get("relationships") or []:
            alvo = r.get("bug") if isinstance(r, dict) else None
            if not alvo:
                achados.append(f"{bid}: relação sem bug de destino")
            elif alvo == bid:
                achados.append(f"{bid}: autorrelação {r.get('type')}")
            elif alvo not in por_id:
                achados.append(f"{bid}: relação {r.get('type')} aponta para {alvo}, inexistente")
    # ciclos de duplicate-of
    duplicatas = {b["id"]: [r["bug"] for r in (b.get("relationships") or [])
                            if isinstance(r, dict) and r.get("type") == "duplicate-of"] for b in bugs}
    for inicio in duplicatas:
        vistos, atual = [], inicio
        while atual in duplicatas:
            if atual in vistos:
                achados.append(f"{inicio}: ciclo de duplicate-of ({' -> '.join(vistos + [atual])})")
                break
            vistos.append(atual)
            atual = duplicatas[atual][0] if duplicatas[atual] else None
    return achados


# ---------------------------------------------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------------------------------------------


def curto(texto, limite):
    texto = texto or ""
    return texto if len(texto) <= limite else texto[:limite].rstrip() + "…"


def celula(ids):
    return ", ".join(sorted(ids)) if ids else "nenhum"


def escrever(caminho, linhas):
    pasta = os.path.dirname(caminho) or "."
    os.makedirs(pasta, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=pasta, prefix=".tmp-")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas) + "\n")
    os.replace(tmp, caminho)


def index(ctx, todos, abertos, resolvidos, achados):
    linhas = [HDR.format(len(todos)), "", f"# Bugs · {ctx}", "", "## Resumo", "", "| status | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in sorted(Counter(b.get("status") for b in todos).items())]
    linhas += ["", "| phase | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in sorted(Counter(b.get("phase") for b in todos).items())]
    linhas += ["", "## Abertos / ativos", "",
               "| # | ID | prioridade | severidade | area/module/feature | título | caminho | bloqueado |",
               "|---|---|---|---|---|---|---|---|"]
    for b in abertos:
        bloqueio = ", ".join(x.get("target") or x.get("bug") or "?" for x in (b.get("blocking") or []))
        linhas.append(f'| {b.get("display_number")} | {b["id"]} | {b.get("priority")} | {b.get("severity")} | '
                      f'{b.get("area")}/{b.get("module")}/{b.get("feature")} | {b.get("title")} | `{b["path"]}` | '
                      f'{"sim (" + bloqueio + ")" if bloqueio else "não"} |')
    linhas += ["", "## Resolvidos", "", "| resolution_kind | qtd |", "|---|---|"]
    linhas += [f"| {s} | {n} |" for s, n in
               sorted(Counter(b.get("resolution_kind") or "null" for b in resolvidos).items())]
    linhas.append("")
    for b in resolvidos:
        trava = "travado: " if b["locked"] else "sem trava: "
        linhas.append(f'- #{b.get("display_number")} {b["id"]} ({b.get("resolution_kind")}) · {trava}{b.get("title")}')
    if achados:
        linhas += ["", "## Inconsistências", "",
                   "Invariantes do registro violadas no front matter. O gerador não conserta: a decisão é humana.", ""]
        linhas += [f"- {x}" for x in achados]
    escrever(os.path.join(RAIZ, ctx, "generated", "index.md"), linhas)


def matrix(ctx, todos, bugs):
    linhas = [HDR.format(len(todos)), "", f"# Relações · {ctx}", "",
              "| origem | tipo | destino | state | evidência? |", "|---|---|---|---|---|"]
    for b in todos:
        for r in b.get("relationships") or []:
            alvo = r.get("bug")
            if alvo in bugs:
                rotulo = f'{alvo} ({bugs[alvo].get("module")})'
                if bugs[alvo].get("context") != ctx:
                    rotulo = f'{alvo} ({bugs[alvo].get("context")}/{bugs[alvo].get("module")})'
            else:
                rotulo = f"{alvo} (externo)"
            linhas.append(f'| {b["id"]} | {r.get("type")} | {rotulo} | {r.get("state")} | '
                          f'{"sim" if r.get("evidence") else "não"} |')
    escrever(os.path.join(RAIZ, ctx, "generated", "matrix.md"), linhas)


def spec_matrix(ctx, todos, addendos, bugs):
    por_spec = defaultdict(lambda: defaultdict(list))
    for b in todos:
        for spec in _specs(b):
            por_spec[spec][b.get("status")].append(b["id"])
    gap = defaultdict(list)
    for b in todos:                      # o veredito manda; sem ele, o label de triagem ainda marca a lacuna
        if b.get("spec_verdict") == "spec-gap" or "spec-gap" in (b.get("labels") or []):
            gap[b.get("status")].append(b["id"])
    linhas = [HDR.format(len(todos)), "", f"# Bugs × specs · {ctx}", "",
              "| spec | open | active | resolved |", "|---|---|---|---|"]
    for spec in sorted(por_spec):
        d = por_spec[spec]
        linhas.append(f'| `{spec}` | {celula(d["open"])} | {celula(d["active"])} | {celula(d["resolved"])} |')
    if any(gap.values()):
        linhas.append(f'| **spec-gap** | {celula(gap["open"])} | {celula(gap["active"])} | {celula(gap["resolved"])} |')
    linhas += ["", "## Adendos de bug vigentes", ""]
    linhas += [f"- `_reversa_sdd/addenda/{a}`" for a in addendos]
    escrever(os.path.join(RAIZ, ctx, "generated", "spec-matrix.md"), linhas)


PESO = {"caused-by": 3, "blocked-by": 2, "regression-of": 4}


def impactos(todos):
    """Impacto de cada bug sobre os outros: só arestas supported/confirmed, related-to limitado a 3 no total."""
    score, relacionados = Counter(), Counter()
    for b in todos:
        for r in b.get("relationships") or []:
            if (r.get("state") or "") not in ("supported", "confirmed"):
                continue
            alvo, tipo = r.get("bug"), r.get("type")
            if tipo in PESO:
                score[alvo] += PESO[tipo]
            elif tipo == "related-to" and relacionados[alvo] < 3:
                score[alvo] += 1
                relacionados[alvo] += 1
    return {bid: s for bid, s in score.items() if s}


def graph_md(ctx, todos, abertos, arestas, score):
    linhas = [HDR.format(len(todos)), "", f"# Grafo · {ctx}", "", "```mermaid", "graph LR"]
    for b in todos:
        linhas.append(f'  {b["id"].replace("-", "_")}["#{b.get("display_number")} {curto(b.get("title"), 40)}"]')
    for b, r in arestas:
        seta = "-.->|" if r.get("state") == "proposed" else "-->|"
        linhas.append(f'  {b["id"].replace("-", "_")} {seta}{r.get("type")}| {r.get("bug").replace("-", "_")}')
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
        if abertos:
            fecho = f"Dos {len(abertos)} abertos, {no_aberto} apontam para esse arquivo."
        else:
            fecho = "Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam."
        linhas += ["", f"Leitura: {len(ids)} bugs convergem em `{arq}`, o maior ponto de convergência do contexto. {fecho}"]
    linhas += ["", "## Impact score", "",
               "Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, "
               "relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.", "",
               "| # | ID | score |", "|---|---|---|"]
    for bid, valor in sorted(score.items(), key=lambda kv: (-kv[1], kv[0])):
        bug = next((b for b in todos if b["id"] == bid), None)
        if bug:
            linhas.append(f'| {bug.get("display_number")} | {bid} | {valor} |')
    escrever(os.path.join(RAIZ, ctx, "generated", "graph.md"), linhas)


def graph_html(ctx, todos, abertos, resolvidos, arestas, addendos, inconsist, score):
    cols, x0, y0, passo_x, passo_y, w, h = 4, 40, 40, 290, 150, 250, 100
    linhas = math.ceil(len(todos) / cols) if todos else 1
    largura, altura = 1200, y0 + (linhas - 1) * passo_y + h + 40
    pos = {b["id"]: (x0 + (i % cols) * passo_x, y0 + (i // cols) * passo_y) for i, b in enumerate(todos)}
    pecas = ['<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto"><path d="M0 0L10 5L0 10z" fill="#8aa"/></marker></defs>']
    for b, r in arestas:
        if r.get("bug") not in pos:
            continue
        ax, ay = pos[b["id"]]
        bx, by = pos[r["bug"]]
        x1, y1, x2, y2 = ax + w / 2, ay + h / 2, bx + w / 2, by + h / 2
        tracejado = ' stroke-dasharray="6 4"' if r.get("state") == "proposed" else ""
        pecas.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#8aa"{tracejado} '
                     f'marker-end="url(#a)" opacity=".7"/><text x="{(x1 + x2) / 2:.0f}" '
                     f'y="{(y1 + y2) / 2 - 6:.0f}" fill="#9bb" font-size="11" text-anchor="middle">{r.get("type")}'
                     f'</text>')
    for b in todos:
        x, y = pos[b["id"]]
        severidade = b.get("severity")
        contorno = VERMELHO if severidade in ("critical", "high") else AMARELO if severidade == "medium" else CINZA
        status = b.get("status")
        tinta = VERDE if status == "resolved" else VERMELHO if status == "open" else AMARELO
        pecas.append(f'<a href="../bugs/{os.path.basename(b["path"])}/bug.md">'
                     f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#1c2128" stroke="{contorno}" '
                     f'stroke-width="2"/><text x="{x + 12}" y="{y + 24}" fill="#e6edf3" font-size="13" '
                     f'font-weight="600">#{b.get("display_number")} {b["id"].split("-")[-1]} · {b.get("priority")}'
                     f'</text><text x="{x + 12}" y="{y + 46}" fill="#c9d1d9" font-size="12">'
                     f'{curto(b.get("title"), 31)}</text>'
                     f'<text x="{x + 12}" y="{y + 66}" fill="#8b949e" font-size="11">{severidade} · {b.get("area")}'
                     f'</text><text x="{x + 12}" y="{y + 86}" fill="{tinta}" font-size="11">{status} · '
                     f'{b.get("phase")}</text></a>')
    tabela = ""
    for b in abertos:
        bloqueio = ", ".join(x.get("target") or x.get("bug") or "?" for x in (b.get("blocking") or []))
        estado = f'{b.get("status")} · {b.get("phase")}' + (f" (bloqueado por {bloqueio})" if bloqueio else "")
        tabela += (f'<tr><td>{b.get("display_number")}</td><td><a href="../bugs/{os.path.basename(b["path"])}/bug.md">'
                   f'{b["id"]}</a></td><td>{b.get("severity")}</td><td>{b.get("priority")}</td>'
                   f'<td>{b.get("title")}</td><td>{b.get("area")}/{b.get("module")}/{b.get("feature")}</td>'
                   f'<td>{estado}</td></tr>')
    travados = "".join(f'<li><a href="../bugs/{os.path.basename(b["path"])}/bug.md">#{b.get("display_number")} '
                       f'{b["id"]}</a> · {b["_data"]} · {b.get("resolution_kind")} · {b.get("title")}</li>'
                       for b in resolvidos)
    grau = Counter()
    for b, r in arestas:
        grau[b["id"]] += 1
        grau[r.get("bug")] += 1
    maximo = max(grau.values()) if grau else 0
    topo = ", ".join("#" + str(b.get("display_number")) for b in todos if grau.get(b["id"]) == maximo) if maximo else ""
    confirmadas = sum(1 for _b, r in arestas if r.get("state") in ("supported", "confirmed"))
    narrativa = (f"Os nós com mais ligações são {topo} ({maximo} ligações cada). Há {confirmadas} relação(ões) "
                 f"supported/confirmed; as demais são hipóteses de triagem e não pesam no impact score."
                 if maximo else "Nenhuma relação registrada neste contexto.")
    if score:
        principal = max(score.items(), key=lambda kv: kv[1])[0]
        narrativa += f" Maior impact score: {principal}."
    css = ("body{background:#0d1117;color:#e6edf3;font:14px system-ui,sans-serif;margin:0;padding:16px}\n"
           ".meta{color:#8b949e;font-size:12px}.cards{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}\n"
           ".card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 16px;min-width:120px}\n"
           ".card b{font-size:22px;display:block}svg{max-width:100%;height:auto;background:#0d1117}\n"
           "table{border-collapse:collapse;width:100%;margin-top:8px}\n"
           "td,th{border-bottom:1px solid #30363d;padding:6px;text-align:left;font-size:13px}\n"
           "a{color:#58a6ff}.wrap{overflow-x:auto}")
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>Grafo de Bugs · {ctx}</title><style>\n{css}</style></head><body>\n'
            f'<h1>Grafo de Bugs · {ctx}</h1>\n'
            f'<p class="meta">Gerado por /reversa-debugger-graph em {TS} · {len(todos)} bugs · '
            f'{len(inconsist)} inconsistências · arestas tracejadas = relação proposed (hipótese)</p>\n'
            f'<div class="cards"><div class="card"><b>{len(todos)}</b>bugs</div>'
            f'<div class="card"><b>{sum(1 for b in resolvidos if b.get("resolution_kind") == "fixed")}'
            f'</b>resolved · fixed</div>\n'
            f'<div class="card"><b>{len(abertos)}</b>abertos/ativos</div>'
            f'<div class="card"><b>{len(addendos)}</b>adendos de spec</div>\n'
            f'<div class="card"><b>{len(inconsist)}</b>inconsistências</div></div>\n'
            f'<div class="wrap"><svg viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}" '
            f'role="img" aria-label="Grafo de bugs">\n' + "\n".join(pecas) + "\n</svg></div>\n"
            f'<p>{narrativa}</p>\n'
            f'<h2>Bugs abertos / ativos</h2><div class="wrap"><table><tr><th>#</th><th>ID</th>'
            f'<th>severidade</th><th>prioridade</th><th>título</th><th>area/module/feature</th><th>status</th></tr>\n'
            f'{tabela}\n</table></div>')
    if inconsist:
        html += "<h2>Inconsistências</h2><ul>" + "".join(f"<li>{x}</li>" for x in inconsist) + "</ul>"
    html += f'<h2>Concluídos (travados)</h2><ul>\n{travados}\n</ul></body></html>'
    escrever(os.path.join(RAIZ, ctx, "generated", "graph.html"), [html])


def espelho(bugs):
    por_spec = defaultdict(list)
    for b in bugs:
        if b.get("visibility") == "restricted":
            continue
        for spec in _specs(b):
            por_spec[spec].append(b)
    linhas = [HDR.format(len(bugs)), "", "# Bugs que atingem as specs", ""]
    for spec in sorted(por_spec):
        linhas += [f"## `{spec}`", ""]
        for b in sorted(por_spec[spec], key=lambda x: (x.get("display_number") or 0, x["id"])):
            rotulo = b.get("status")
            if b.get("resolution_kind"):
                rotulo += f'/{b.get("resolution_kind")}'
            linhas.append(f'- {b["id"]} ({rotulo}, {b.get("priority")}): {b.get("title")} — `{b["path"]}`')
        linhas.append("")
    escrever(ESPELHO, linhas)


def main():
    pedidos = sys.argv[1:]
    todos = carregar()
    achados = validar(todos)
    disponiveis = sorted({b["context"] for b in todos})
    alvos = pedidos or disponiveis
    desconhecidos = [c for c in alvos if c not in disponiveis]
    if desconhecidos:
        print("contexto sem bugs registrados:", ", ".join(desconhecidos))
        alvos = [c for c in alvos if c in disponiveis]
    if not alvos:
        print(f"Nenhum bug registrado em {RAIZ}. Registre com /reversa-debugger.")
        return 0
    por_id = {b["id"]: b for b in todos}
    addendos = sorted(os.path.basename(p) for p in glob.glob(os.path.join("_reversa_sdd", "addenda", "*.md")))
    for ctx in alvos:
        do_contexto = [b for b in todos if b["context"] == ctx and b.get("visibility") != "restricted"]
        if not do_contexto:
            continue
        do_contexto.sort(key=lambda b: (b.get("display_number") or 0, b["id"]))
        abertos = [b for b in do_contexto if b.get("status") in ("open", "active")]
        resolvidos = [b for b in do_contexto if b.get("status") == "resolved"]
        arestas = [(b, r) for b in do_contexto for r in (b.get("relationships") or [])
                   if isinstance(r, dict) and r.get("bug")]
        ids_locais = {b["id"] for b in do_contexto}
        locais = [x for x in achados if x.split(":")[0] in ids_locais]
        score = impactos(do_contexto)
        escrever(os.path.join(RAIZ, ctx, "generated", "catalog.jsonl"),
                 [json.dumps({k: v for k, v in b.items() if not k.startswith("_")}, ensure_ascii=False,
                             sort_keys=True) for b in do_contexto])
        index(ctx, do_contexto, abertos, resolvidos, locais)
        matrix(ctx, do_contexto, por_id)
        spec_matrix(ctx, do_contexto, addendos, por_id)
        graph_md(ctx, do_contexto, abertos, arestas, score)
        graph_html(ctx, do_contexto, abertos, resolvidos, arestas, addendos, locais, score)
        print(f'{ctx}: {len(do_contexto)} bugs · {len(abertos)} abertos · {len(resolvidos)} resolvidos · '
              f'{len(arestas)} arestas · {len(locais)} inconsistências')
    espelho([b for b in todos if b.get("visibility") != "restricted"])
    print(f"espelho: {ESPELHO} · {len(todos)} bugs · {len(achados)} inconsistências globais")
    for x in achados:
        print("  -", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
