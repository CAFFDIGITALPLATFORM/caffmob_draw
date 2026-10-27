#!/usr/bin/env python3
"""Texturas PBR do pacote a partir do ambientCG (073, D-05; RF-01, RF-02, RF-12). Fora do Blender.

    python3 tools/baixar_pbr.py folha <candidatas.json> <saida.html>
    python3 tools/baixar_pbr.py baixar <candidatas.json> [caffmob_draw/pbr]

- `folha`: página de aprovação com as miniaturas de cada candidata (embutidas, a página não busca nada fora) e a
  escolha por vaga, gravada no banco do artefato publicado;
- `baixar`: para cada vaga com `escolhida`, baixa o zip 1K-JPG do ambientCG, tira só `Color`, `NormalGL`,
  `Roughness` e (nos metais) `Metalness`, grava `cor`, `normal`, `rugosidade`, `metalico` e a `miniatura` de 256 px
  em `pbr/<slug>/` e regrava o `manifest.json` com origem, licença e sha256.

O zip vem de fora: só os membros esperados são lidos, pelo nome, sem extrair o resto. Precisa do Pillow.
"""
import base64
import datetime
import hashlib
import html
import importlib.util
import io
import json
import os
import sys
import urllib.request
import zipfile

UA = 'caffmob-draw-pbr/1.0 (+https://mobi.caff.digital)'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, 'caffmob_draw', 'pbr')
SUFIXOS = {'cor': '_Color.jpg', 'normal': '_NormalGL.jpg', 'rugosidade': '_Roughness.jpg', 'metalico': '_Metalness.jpg'}
MINIATURA_PX = 256


def _core():
    caminho = os.path.join(RAIZ, 'caffmob_draw', 'texture_library', 'pbr_core.py')
    spec = importlib.util.spec_from_file_location('pbr_core', caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=180) as r:
        return r.read()


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def _miniatura(origem, destino, px=MINIATURA_PX, qualidade=85):
    from PIL import Image
    with Image.open(origem) as im:
        im = im.convert('RGB')
        im.thumbnail((px, px))
        im.save(destino, 'JPEG', quality=qualidade)


def baixar_textura(asset_id, slug, metal, pasta=PASTA):
    """Mapas de uma textura em `pasta/<slug>/`; devolve {mapa: {arquivo, sha256[, px]}}."""
    dados = _get(f'https://ambientcg.com/get?file={asset_id}_1K-JPG.zip')
    destino = os.path.join(pasta, slug)
    os.makedirs(destino, exist_ok=True)
    mapas = {}
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        nomes = {os.path.basename(n): n for n in z.namelist()}
        for mapa, sufixo in SUFIXOS.items():
            if mapa == 'metalico' and not metal:
                continue
            membro = nomes.get(asset_id + '_1K-JPG' + sufixo) or nomes.get(asset_id + sufixo)
            if membro is None:
                raise SystemExit(f'{asset_id}: o zip não tem {sufixo}')
            caminho = os.path.join(destino, mapa + '.jpg')
            with z.open(membro) as src, open(caminho + '.tmp', 'wb') as dst:
                dst.write(src.read())
            os.replace(caminho + '.tmp', caminho)
            mapas[mapa] = {'arquivo': f'{slug}/{mapa}.jpg', 'sha256': sha256(caminho)}
    from PIL import Image
    with Image.open(os.path.join(destino, 'cor.jpg')) as im:
        mapas['cor']['px'] = list(im.size)
    mini = os.path.join(destino, 'miniatura.jpg')
    _miniatura(os.path.join(destino, 'cor.jpg'), mini)
    mapas['miniatura'] = {'arquivo': f'{slug}/miniatura.jpg', 'sha256': sha256(mini)}
    return mapas


def baixar(candidatas, pasta=PASTA):
    core = _core()
    vagas = json.load(open(candidatas, encoding='utf-8'))['vagas']
    hoje = datetime.date.today().isoformat()
    texturas = []
    for v in vagas:
        escolha = v.get('escolhida')
        if not escolha:
            print('sem escolha:', v['slug'])
            continue
        cand = next(c for c in v['candidatas'] if c['id'] == escolha)
        print('baixando', v['slug'], escolha)
        mapas = baixar_textura(escolha, v['slug'], v['metal'], pasta)
        texturas.append(dict(slug=v['slug'], uuid=core.uuid_de(v['slug']), nome=v['nome'], categoria=v['categoria'],
                             palavras=v['palavras'], tom=v['tom'], padrao=bool(v['padrao']), metal=bool(v['metal']),
                             origem=dict(fonte='ambientCG', id=escolha, url=cand['url'], licenca=core.LICENCA,
                                         copiado_em=hoje),
                             tamanho_mm=v['tamanho_mm'], mapas=mapas))
    manifesto = {'schema-version': 1, 'namespace': str(core.NAMESPACE_PBR), 'licenca': core.LICENCA,
                 'texturas': texturas}
    problemas = core.validar_manifesto(manifesto, pasta, sha256)
    destino = os.path.join(pasta, core.MANIFESTO)
    with open(destino + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(destino + '.tmp', destino)
    for p in problemas:
        print('PROBLEMA:', p)
    return 1 if problemas else 0


def _data_uri(url):
    from PIL import Image
    with Image.open(io.BytesIO(_get(url))) as im:
        im = im.convert('RGB')
        im.thumbnail((176, 176))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=78)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def folha(candidatas, saida):
    dados = json.load(open(candidatas, encoding='utf-8'))
    for v in dados['vagas']:
        for c in v['candidatas']:
            c['img'] = _data_uri(c['miniatura'])
    vagas = json.dumps([{k: v[k] for k in ('slug', 'nome', 'categoria', 'palavras', 'tom', 'tamanho_mm')} |
                        {'candidatas': [{k: c[k] for k in ('id', 'nome', 'url', 'img')} for c in v['candidatas']]}
                        for v in dados['vagas']], ensure_ascii=False)
    pagina = MODELO.replace('/*VAGAS*/[]', vagas.replace('</', '<\\/'))
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(pagina)
    print(saida, f'{len(pagina) / 1e6:.1f} MB')


MODELO = r'''<title>Folha de Texturas PBR</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap">
<style>
/* Layout: uma faixa por categoria; cada vaga é uma linha com o nome à esquerda e as três candidatas lado a lado. */
:root{
  --bg:#f3f2ee; --surface:#ffffff; --fg:#1f2421; --muted:#5d6661; --line:#d9d8d1;
  --accent:#2f6b57; --accent-soft:#dcebe4; --warn:#9a5b13;
  --display:"Archivo",system-ui,sans-serif; --body:"Source Sans 3",system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#161a18; --surface:#1f2421; --fg:#e8ebe8; --muted:#a2aba6; --line:#353c38;
  --accent:#7cc4a8; --accent-soft:#24382f; --warn:#e0a35a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#161a18; --surface:#1f2421; --fg:#e8ebe8; --muted:#a2aba6; --line:#353c38;
  --accent:#7cc4a8; --accent-soft:#24382f; --warn:#e0a35a; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:16px/1.5 var(--body);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 64px}
main{max-width:1080px;margin:0 auto;display:grid;gap:32px}
h1,h2{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:1.9rem;font-weight:700}
h2{font-size:1.15rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding-bottom:8px;border-bottom:1px solid var(--line)}
header{display:grid;gap:8px}
header p{margin:0;max-width:68ch;color:var(--muted)}
.estado{display:flex;flex-wrap:wrap;gap:12px;align-items:center;font-size:.95rem}
.pill{font-family:var(--mono);font-size:.85rem;padding:2px 10px;border-radius:999px;background:var(--accent-soft);color:var(--accent);font-variant-numeric:tabular-nums}
.aviso{color:var(--warn)}
section{display:grid;gap:12px}
.vaga{display:grid;grid-template-columns:minmax(0,220px) minmax(0,1fr);gap:16px;padding:16px 0;border-bottom:1px solid var(--line)}
.info{display:grid;gap:6px;align-content:start;min-width:0}
.info strong{font-family:var(--display);font-size:1.05rem}
.meta{font-size:.85rem;color:var(--muted)}
.medida{display:flex;gap:6px;align-items:center;font-size:.85rem;color:var(--muted)}
.medida input{width:5.2em;font:inherit;font-family:var(--mono);padding:2px 4px;border:1px solid var(--line);border-radius:4px;background:var(--surface);color:var(--fg)}
.cands{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.cand{position:relative;display:grid;gap:4px;padding:6px;border:2px solid transparent;border-radius:8px;background:var(--surface);cursor:pointer}
.cand input{position:absolute;opacity:0;pointer-events:none}
.cand img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:4px;display:block}
.cand span{font-family:var(--mono);font-size:.8rem;overflow-wrap:anywhere}
.cand a{font-size:.8rem;color:var(--accent)}
.cand:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}
.cand:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
.nota{font:inherit;font-size:.85rem;width:100%;padding:4px 6px;border:1px solid var(--line);border-radius:4px;background:var(--surface);color:var(--fg)}
@media (max-width:640px){.vaga{grid-template-columns:1fr}}
</style>
<main>
  <header>
    <h1>Folha de Texturas PBR</h1>
    <p>Escolha uma imagem por vaga. A medida é o tamanho real que a imagem cobre na parede ou no piso: confira pela contagem (tijolo com cerca de 230 mm, tábua com cerca de 190 mm, placa de porcelanato com 600 mm). Se nenhuma servir, escreva na nota o que procurar. Todas são do ambientCG, licença CC0.</p>
    <div class="estado"><span class="pill" id="contagem">0 de 0 escolhidas</span><span id="salvo" class="meta">Carregando escolhas…</span></div>
  </header>
  <div id="lista"></div>
</main>
<script>
const VAGAS = /*VAGAS*/[];
const CATS = {parede: 'Parede', piso: 'Piso', metal: 'Metal'};
const TOM = {claro: 'tom claro', medio: 'tom médio', cinza: 'tom cinza', escuro: 'tom escuro'};
const escolhas = {};
let db = null;
const el = (t, a = {}, ...f) => { const e = document.createElement(t); for (const [k, v] of Object.entries(a)) { if (k === 'text') e.textContent = v; else e.setAttribute(k, v); } e.append(...f); return e; };

function contar() {
  const n = VAGAS.filter(v => escolhas[v.slug]?.candidata).length;
  document.getElementById('contagem').textContent = n + ' de ' + VAGAS.length + ' escolhidas';
}

function render() {
  const lista = document.getElementById('lista');
  lista.replaceChildren();
  for (const cat of Object.keys(CATS)) {
    const sec = el('section', {}, el('h2', {text: CATS[cat]}));
    for (const v of VAGAS.filter(x => x.categoria === cat)) {
      const e = escolhas[v.slug] || {};
      const larg = el('input', {type: 'number', min: '1', max: '10000', id: 'l-' + v.slug, 'aria-label': 'Largura em mm'});
      const alt = el('input', {type: 'number', min: '1', max: '10000', id: 'a-' + v.slug, 'aria-label': 'Altura em mm'});
      larg.value = e.largura || v.tamanho_mm.largura; alt.value = e.altura || v.tamanho_mm.altura;
      const nota = el('input', {type: 'text', class: 'nota', id: 'n-' + v.slug, placeholder: 'Nota (opcional)'});
      nota.value = e.nota || '';
      const salvar = () => gravar(v.slug, {largura: +larg.value, altura: +alt.value, nota: nota.value});
      larg.addEventListener('change', salvar); alt.addEventListener('change', salvar); nota.addEventListener('change', salvar);
      const cands = el('div', {class: 'cands', role: 'radiogroup', 'aria-label': v.nome});
      for (const c of v.candidatas) {
        const r = el('input', {type: 'radio', name: 'r-' + v.slug, value: c.id, id: 'r-' + v.slug + '-' + c.id});
        r.checked = e.candidata === c.id;
        r.addEventListener('change', () => gravar(v.slug, {candidata: c.id, largura: +larg.value, altura: +alt.value, nota: nota.value}));
        cands.append(el('label', {class: 'cand', for: r.id}, r, el('img', {src: c.img, alt: c.nome, loading: 'lazy'}),
          el('span', {text: c.id}), el('a', {href: c.url, target: '_blank', rel: 'noopener', text: 'ver no ambientCG'})));
      }
      sec.append(el('div', {class: 'vaga'},
        el('div', {class: 'info'}, el('strong', {text: v.nome}),
          el('span', {class: 'meta', text: TOM[v.tom] + ' · casa com: ' + v.palavras.join(', ')}),
          el('div', {class: 'medida'}, larg, el('span', {text: '×'}), alt, el('span', {text: 'mm'})), nota),
        cands));
    }
    lista.append(sec);
  }
  contar();
}

async function gravar(slug, campos) {
  escolhas[slug] = Object.assign({}, escolhas[slug], campos);
  contar();
  const salvo = document.getElementById('salvo');
  if (!db) { salvo.textContent = 'Sem conexão com o banco: a escolha não fica gravada.'; salvo.className = 'aviso'; return; }
  try { await db.doc('escolhas/' + slug).set(escolhas[slug]); salvo.textContent = 'Escolha gravada.'; salvo.className = 'meta'; }
  catch (err) { salvo.textContent = 'Não foi possível gravar (' + (err && err.code || 'erro') + '). Tente de novo.'; salvo.className = 'aviso'; }
}

render();
(async () => {
  const salvo = document.getElementById('salvo');
  db = window.claude ? await window.claude.use('db') : null;
  if (!db) { salvo.textContent = 'Abra pelo claude.ai, com sua conta, para gravar as escolhas.'; salvo.className = 'aviso'; return; }
  try {
    const snap = await db.collection('escolhas').get();
    for (const d of snap.docs) escolhas[d.id] = d.data();
    salvo.textContent = snap.empty ? 'Nenhuma escolha gravada ainda.' : 'Escolhas carregadas.';
    render();
  } catch (err) { salvo.textContent = 'Não foi possível ler as escolhas (' + (err && err.code || 'erro') + ').'; salvo.className = 'aviso'; }
})();
</script>
'''


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'folha':
        folha(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'baixar':
        sys.exit(baixar(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else PASTA))
    else:
        raise SystemExit(__doc__)
