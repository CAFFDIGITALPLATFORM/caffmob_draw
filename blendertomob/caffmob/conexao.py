"""
Cliente do MOBI para o addon (061 RF-36 a RF-38): autorização de aparelho (RFC 8628) e API /api/draw/v1.

Python puro (urllib), sem bpy: o operador do Blender chama estas funções num timer, e o teste de ida e
volta as chama contra o MOBI de ensaio. Os tokens ficam num arquivo do próprio usuário, nunca a senha.
O token de renovação gira a cada uso: o arquivo é regravado na hora, senão o próximo uso revoga o
aparelho por reuso.

Texturas de fábrica (062 D-15): só a miniatura e a versão de trabalho saem do MOBI. O arquivo baixado fica num
cache local com o sha256 no nome; a mesma textura nunca é baixada duas vezes, e o conteúdo é conferido pelo hash.
"""

import hashlib
import json
import os
import platform
import time
import urllib.error
import urllib.parse
import urllib.request

CLIENT_ID = "caffmob-draw"
BASE_PADRAO = "https://mobi.caff.digital"
TEMPO_LIMITE_S = 10
# O Cloudflare na frente do MOBI recusa o User-Agent padrão do urllib (403, "error code: 1010",
# medido em produção em 2026-10-14). O addon se identifica pelo nome.
USER_AGENT = f"CAFF-MOB-DRAW/1.0 ({platform.system() or 'desconhecido'}; Python {platform.python_version()})"


class ErroDoMobi(Exception):
    def __init__(self, status, corpo):
        super().__init__(f"{status}: {corpo}")
        self.status = status
        self.corpo = corpo


def _pedir(metodo, url, corpo=None, cabecalhos=None, formulario=False):
    dados = None
    cabecalhos = {"User-Agent": USER_AGENT, "Accept": "application/json", **(cabecalhos or {})}
    if corpo is not None:
        if formulario:
            dados = urllib.parse.urlencode(corpo).encode()
            cabecalhos["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            dados = json.dumps(corpo, ensure_ascii=False).encode()
            cabecalhos["Content-Type"] = "application/json"
    pedido = urllib.request.Request(url, data=dados, method=metodo, headers=cabecalhos)
    try:
        with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE_S) as resposta:
            texto = resposta.read().decode()
            return resposta.status, (json.loads(texto) if texto else None), dict(resposta.headers)
    except urllib.error.HTTPError as erro:
        texto = erro.read().decode()
        try:
            corpo_erro = json.loads(texto) if texto else None
        except ValueError:
            corpo_erro = texto
        return erro.code, corpo_erro, dict(erro.headers or {})


def _pedir_bytes(url, cabecalhos=None):
    """GET de arquivo: (status, bytes, cabeçalhos). 304 volta com bytes vazios."""
    pedido = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, **(cabecalhos or {})})
    try:
        with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE_TEXTURA_S) as resposta:
            return resposta.status, resposta.read(), dict(resposta.headers)
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read(), dict(erro.headers or {})


TEMPO_LIMITE_TEXTURA_S = 60
EXTENSOES = {"image/jpeg": "jpg", "image/png": "png"}


def _gravar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    temporario = f"{caminho}.{os.getpid()}.tmp"
    with open(temporario, "wb") as arquivo:
        arquivo.write(dados)
    os.replace(temporario, caminho)


def pedir_codigo(base, nome, plataforma="blender"):
    status, corpo, _ = _pedir("POST", f"{base}/api/draw/aparelho/codigo", {"client_id": CLIENT_ID, "nome": nome, "plataforma": plataforma}, formulario=True)
    if status != 200:
        raise ErroDoMobi(status, corpo)
    return corpo


def consultar_token(base, device_code):
    """Uma consulta: devolve os tokens, ou {'error': ...} (authorization_pending, slow_down, access_denied, expired_token)."""
    status, corpo, _ = _pedir("POST", f"{base}/api/draw/aparelho/token", {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code", "device_code": device_code, "client_id": CLIENT_ID}, formulario=True)
    if status == 200:
        return corpo
    return corpo if isinstance(corpo, dict) and "error" in corpo else {"error": f"http_{status}"}


def esperar_token(base, codigo, dormir=time.sleep, agora=time.monotonic):
    """Consulta até aprovar, recusar ou vencer, respeitando interval e slow_down (RFC 8628 §3.5)."""
    intervalo = codigo.get("interval", 5)
    limite = agora() + codigo.get("expires_in", 600)
    while agora() < limite:
        resposta = consultar_token(base, codigo["device_code"])
        if "access_token" in resposta:
            return resposta
        erro = resposta.get("error", "")
        if erro == "slow_down":
            intervalo += 5
        elif erro.startswith("http_5"):
            pass  # MOBI reiniciando (deploy) ou borda fora: tenta de novo dentro do prazo do código
        elif erro != "authorization_pending":
            raise ErroDoMobi(400, resposta)
        dormir(intervalo)
    raise ErroDoMobi(400, {"error": "expired_token"})


class Sessao:
    """Tokens do aparelho num arquivo JSON; renova uma vez ao receber 401."""

    def __init__(self, arquivo, base=BASE_PADRAO):
        self.arquivo = arquivo
        self.base = base
        self.tokens = None
        if arquivo and os.path.exists(arquivo):
            with open(arquivo, encoding="utf-8") as entrada:
                gravado = json.load(entrada)
            self.base = gravado.get("base", base)
            self.tokens = gravado.get("tokens")

    @property
    def conectado(self):
        return bool(self.tokens and self.tokens.get("access_token"))

    @property
    def titular(self):
        return (self.tokens or {}).get("titular", {}).get("nome", "")

    def guardar(self, tokens):
        self.tokens = tokens
        if not self.arquivo:
            return
        temporario = f"{self.arquivo}.tmp"
        with open(temporario, "w", encoding="utf-8") as saida:
            json.dump({"base": self.base, "tokens": tokens}, saida)
        os.chmod(temporario, 0o600)
        os.replace(temporario, self.arquivo)

    def esquecer(self):
        self.tokens = None
        if self.arquivo and os.path.exists(self.arquivo):
            os.remove(self.arquivo)

    def _renovar(self):
        status, corpo, _ = _pedir("POST", f"{self.base}/api/draw/aparelho/token", {
            "grant_type": "refresh_token", "refresh_token": self.tokens["refresh_token"], "client_id": CLIENT_ID}, formulario=True)
        if status != 200:
            self.esquecer()
            raise ErroDoMobi(401, {"erro": "DESCONECTADO", "detalhe": corpo})
        self.guardar(corpo)

    def chamar(self, metodo, caminho, corpo=None, if_match=None):
        if not self.conectado:
            raise ErroDoMobi(401, {"erro": "DESCONECTADO"})
        for tentativa in (1, 2):
            cabecalhos = {"Authorization": f"Bearer {self.tokens['access_token']}"}
            if if_match is not None:
                cabecalhos["If-Match"] = f'"{if_match}"'
            status, resposta, headers = _pedir(metodo, f"{self.base}/api/draw/v1{caminho}", corpo, cabecalhos)
            if status == 401 and tentativa == 1:
                self._renovar()
                continue
            return status, resposta, headers
        return status, resposta, headers

    def listar_ambientes(self):
        itens, depois = [], "0"
        while depois is not None:
            status, corpo, _ = self.chamar("GET", f"/ambientes?depois={depois}")
            if status != 200:
                raise ErroDoMobi(status, corpo)
            itens.extend(corpo["itens"])
            depois = corpo["proximo"]
        return itens

    def baixar_ambiente(self, ambiente_id):
        status, corpo, _ = self.chamar("GET", f"/ambientes/{ambiente_id}")
        if status != 200:
            raise ErroDoMobi(status, corpo)
        return corpo

    def enviar_ambiente(self, documento, versao_lida):
        """200 → {'version', ...}; 409 → {'erro': 'VERSAO_DIVERGENTE', 'versao_atual', 'documento_atual'}."""
        status, corpo, _ = self.chamar("PUT", f"/ambientes/{documento['id']}", documento, if_match=versao_lida)
        if status not in (200, 409):
            raise ErroDoMobi(status, corpo)
        return status, corpo

    def chamar_bytes(self, caminho, cabecalhos=None):
        if not self.conectado:
            raise ErroDoMobi(401, {"erro": "DESCONECTADO"})
        for tentativa in (1, 2):
            status, dados, headers = _pedir_bytes(f"{self.base}/api/draw/v1{caminho}", {"Authorization": f"Bearer {self.tokens['access_token']}", **(cabecalhos or {})})
            if status == 401 and tentativa == 1:
                self._renovar()
                continue
            return status, dados, headers
        return status, dados, headers

    def listar_texturas(self, busca=None, fabricante=None, linha=None, cursor=None):
        """Uma página de 60: {'itens': [...], 'proximo': cursor ou None}."""
        filtros = {chave: valor for chave, valor in (("busca", busca), ("fabricante", fabricante), ("linha", linha), ("cursor", cursor)) if valor}
        status, corpo, _ = self.chamar("GET", "/texturas" + (f"?{urllib.parse.urlencode(filtros)}" if filtros else ""))
        if status != 200:
            raise ErroDoMobi(status, corpo)
        return corpo

    def ler_textura(self, textura_id):
        status, corpo, _ = self.chamar("GET", f"/texturas/{textura_id}")
        if status != 200:
            raise ErroDoMobi(status, corpo)
        return corpo

    def baixar_textura(self, textura, pasta, tamanho="trabalho"):
        """Caminho do arquivo no cache. Baixa só se o sha256 ainda não está lá, e confere o hash do que chegou."""
        sha = textura["sha256_trabalho" if tamanho == "trabalho" else "sha256_miniatura"]
        for extensao in ("jpg", "png"):
            existente = os.path.join(pasta, f"{sha}.{extensao}")
            if os.path.exists(existente):
                return existente
        status, dados, headers = self.chamar_bytes(f"/texturas/{textura['id']}/imagem?tamanho={tamanho}")
        if status != 200:
            raise ErroDoMobi(status, dados[:200].decode(errors="replace"))
        if hashlib.sha256(dados).hexdigest() != sha:
            raise ErroDoMobi(502, {"erro": "HASH_DIVERGENTE", "textura": textura["id"]})
        caminho = os.path.join(pasta, f"{sha}.{EXTENSOES.get(headers.get('Content-Type', '').split(';')[0], 'jpg')}")
        _gravar(caminho, dados)
        return caminho

    def baixar_mapa(self, textura_id, tipo, pasta):
        """Mapa (bump, bump2, specular) no cache, revalidado pelo ETag: o catálogo não traz o hash do mapa."""
        caminho = os.path.join(pasta, f"{textura_id}-{tipo}.jpg")
        etag = None
        if os.path.exists(caminho) and os.path.exists(f"{caminho}.etag"):
            with open(f"{caminho}.etag", encoding="utf-8") as arquivo:
                etag = arquivo.read().strip()
        status, dados, headers = self.chamar_bytes(f"/texturas/{textura_id}/mapas/{tipo}", {"If-None-Match": etag} if etag else None)
        if status == 304:
            return caminho
        if status != 200:
            raise ErroDoMobi(status, dados[:200].decode(errors="replace"))
        _gravar(caminho, dados)
        _gravar(f"{caminho}.etag", (headers.get("ETag") or "").encode())
        return caminho

    def criar_ambiente(self, documento):
        status, corpo, _ = self.chamar("POST", "/ambientes", documento)
        if status != 201:
            raise ErroDoMobi(status, corpo)
        return corpo
