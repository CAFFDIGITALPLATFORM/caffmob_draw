# Contrato: servidor de texturas da CAF Mob

> Identificador: `014-texturas-fabricantes-grade`
> Tipo: HTTP (JSON), versão `v1`
> Data: `2026-10-12`
> Consumidor: plugin CAFFMob Draw (`texture_library/`). Provedor: site da CAF Mob (ou servidor provisório).

## Convenções

- **Base:** `<textures_server_url>/v1`, configurável nas preferências do plugin. Só HTTPS; servidor falso local com
  `http://127.0.0.1` só nos testes.
- **Autenticação:** `Authorization: Bearer <access_token>` em tudo que não for `/auth/*`.
- **Cabeçalhos do plugin:** `User-Agent: CAFFMobDraw/<versão> Blender/<versão>` e `Accept: application/json`.
- **Erros:** corpo `{"error": "<código>", "message": "<texto para o usuário, pt-BR>"}`.

| HTTP | `error` | O que o plugin faz |
|------|---------|--------------------|
| 400 | `invalid_request` | Aviso com `message`; não repete |
| 401 | `invalid_token` / `expired_token` | Renova a sessão uma vez (`/auth/refresh`); se falhar, pede login |
| 403 | `forbidden` / `not_entitled` | Aviso "Sua conta não tem acesso a esta textura" (ou ao "Baixar tudo") |
| 404 | `not_found` | Aviso "Textura não disponível no servidor"; marca o item |
| 429 | `rate_limited` | Espera `Retry-After` (ou 2, 4, 8… até 60 s) e repete |
| 5xx | `server_error` | Recuo 2, 4, 8 s, até 3 tentativas; depois, aviso |

- **Tempos:** conexão em 10 s; leitura em 30 s sem receber bytes; nenhuma chamada bloqueia a interface (D-11).

## 1. Login por código de dispositivo (RFC 8628)

### `POST /v1/auth/device`

- **Request:** `{"client_id": "caffmob-draw"}`
- **Response 200:**
  ```json
  {"device_code": "…", "user_code": "WDJB-MJHT",
   "verification_uri": "https://cafmob…/ativar",
   "verification_uri_complete": "https://cafmob…/ativar?code=WDJB-MJHT",
   "expires_in": 600, "interval": 5}
  ```
- **Plugin:** mostra `user_code`, abre `verification_uri_complete` no navegador e passa a consultar `/auth/token` a
  cada `interval` segundos.

### `POST /v1/auth/token`

- **Request:** `{"client_id": "caffmob-draw", "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
  "device_code": "…"}`
- **Response 200:**
  `{"access_token": "…", "expires_in": 900, "refresh_token": "…", "account": {"email": "…", "name": "…"}}`
- **Response 400:** com `error` igual a:
  - `authorization_pending`: continua consultando;
  - `slow_down`: soma 5 s ao intervalo;
  - `access_denied` ou `expired_token`: para e avisa.

### `POST /v1/auth/refresh`

- **Request:** `{"client_id": "caffmob-draw", "refresh_token": "…"}`
- **Response 200:** igual à de `/auth/token`. O servidor pode girar o `refresh_token`, e o plugin grava o novo.
- **Response 401:** sessão encerrada; o plugin apaga `session.json` e pede login.

### `POST /v1/auth/logout`

- **Request:** `{"refresh_token": "…"}`
- **Response:** 204. É idempotente: token já revogado também responde 204.

## 2. Permissões da conta

### `GET /v1/me/entitlements`

- **Response 200:** `{"textures": true, "download_all": true, "catalog_versions": [1]}`
- `textures: false`: nenhum download; a grade mostra as miniaturas e o aviso de acesso.
- `download_all`: habilita o "Baixar tudo" (RN-12, RF-19).

## 3. Catálogo

### `GET /v1/textures/catalog?version=<catalog_version>`

- **Response 200:**
  `{"version": 1, "items": {"<id>": {"sha256": "…", "bytes": 1234567, "url": "/v1/textures/<id>/file"}}}`
- **Cache:** com `ETag`; o plugin manda `If-None-Match` e aceita 304.
- O plugin usa as miniaturas e os nomes do `catalog.json` do pacote, e só pega aqui sha256, bytes e endereço. Um id do
  pacote ausente da resposta vira "não disponível no servidor".

## 4. Download

### `GET /v1/textures/<id>/file`

- **Response 200:** bytes da imagem, com `Content-Type` `image/jpeg` ou `image/png`, `Content-Length` e `ETag`
  (sha256).
- **Response 302:** para um endereço assinado e temporário de armazenamento. O plugin segue o redirecionamento sem
  mandar o `Authorization` para outro domínio.
- **Retomada:** `Range: bytes=<n>-`, resposta 206. Sem suporte a `Range`, a resposta 200 recomeça do zero.
- **Idempotência:** baixar duas vezes dá o mesmo arquivo; o plugin confere o sha256 e só então renomeia o `.part`.
- **Integridade:** sha256 diferente do catálogo descarta o arquivo, tenta uma vez de novo e depois avisa.

### Relevo (`<id>.bump`)

Quinze texturas trazem o relevo do fabricante (um JPEG de altura). Ele é um item próprio do catálogo do servidor,
com o id da textura mais `.bump` (por exemplo `eucatex/chapas-mdf-eucafibra/bp-raizes-carbono.bump`), e segue as
mesmas regras de download. O `tools/texturas_importar.py` já o coloca no `manifest.json`. Servidor sem o relevo:
o plugin aplica só a cor, sem aviso.

## 5. Servidor falso dos testes (`tests/fake_texture_server.py`)

Implementa este contrato com `http.server`, com contas e permissões configuráveis e respostas injetáveis: 401
depois de N chamadas, 403, 404, 429 com `Retry-After`, corte da conexão no meio do download e `Range`. É a referência
executável do contrato para o time do site.

## 6. Exemplos reais

Capturados do servidor falso em 2026-10-12. Os tokens são aleatórios a cada execução.

```http
POST /v1/auth/device            {"client_id": "caffmob-draw"}
200 {"device_code": "HTRttULsSdFC4r2VJO_oHw", "user_code": "B460-E229",
     "verification_uri": "http://127.0.0.1:35255/ativar",
     "verification_uri_complete": "http://127.0.0.1:35255/ativar?code=B460-E229", "expires_in": 600, "interval": 1}

POST /v1/auth/token             {"client_id": "caffmob-draw", "device_code": "HTRttULsSdFC4r2VJO_oHw",
                                 "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}
400 {"error": "authorization_pending", "message": "Aguardando a confirmação no navegador."}
200 {"access_token": "mFLlV27NfWp1IAD7yj4ZRFwMSX2dL6-Y", "expires_in": 900,
     "refresh_token": "H2ipmWyns113q4oUl2P6e-AjuYtXhEJks_J63_h9Ofk",
     "account": {"email": "teste@cafmob.local", "name": "teste"}}

GET /v1/me/entitlements         Authorization: Bearer mFLl…
200 {"textures": true, "download_all": true, "catalog_versions": [1]}

GET /v1/textures/catalog?version=1
200 ETag: "cbb4d7ee71734c20"
    {"version": 1, "items": {"demo/geral/carvalho": {"sha256": "a2ea5f9a…aad4c", "bytes": 179,
                                                     "url": "/v1/textures/demo/geral/carvalho/file"}, …}}
GET /v1/textures/catalog?version=1   If-None-Match: "cbb4d7ee71734c20"
304

GET /v1/textures/demo/geral/carvalho/file   Range: bytes=100-
206 Content-Type: image/png  Content-Length: 79  Content-Range: bytes 100-178/179
    ETag: "a2ea5f9a…aad4c"

GET /v1/textures/nada/file
404 {"error": "not_found", "message": "Textura não disponível no servidor."}
GET /v1/me/entitlements         Authorization: Bearer errado
401 {"error": "invalid_token", "message": "Sessão inválida. Entre de novo com a sua conta CAF Mob."}

POST /v1/auth/refresh           {"client_id": "caffmob-draw", "refresh_token": "H2ip…"}
200 {"access_token": "kk18…", "expires_in": 900, "refresh_token": "C7iB…", "account": {…}}
POST /v1/auth/refresh           (o token antigo, depois da rotação)
401 {"error": "invalid_token", "message": "Sessão encerrada. Entre de novo."}

POST /v1/auth/logout            {"refresh_token": "C7iB…"}
204
```

## 7. O que o plugin faz (fixado pelos testes)

Testes: `tests/test_texture_downloader.py` (subprocesso, sem Blender) e `tests/blender_014_textures_net.py` (no
Blender).

- O download e as chamadas JSON rodam num subprocesso (`texture_library/downloader.py`), com
  `User-Agent: CAFFMobDraw/<versão> Blender/<versão>`. A interface não trava.
- O `Authorization` vai como cabeçalho que não segue redirecionamento. Num 302 para o mesmo servidor, o plugin o
  manda de novo; para outro domínio, não manda.
- **Queda no meio:** a conexão pode fechar sem erro antes do fim. O plugin confere o tamanho recebido com `bytes` do
  catálogo e retoma com `Range` a partir do `.part`. Resposta 200 a um `Range` recomeça do zero. Um 416 apaga o
  `.part` e recomeça.
- **401 durante o download:** o plugin renova a sessão (`/auth/refresh`), manda o token novo ao subprocesso e
  continua o mesmo download.
- **429:** espera `Retry-After` (ou 2, 4, 8… até 60 s), até 6 vezes. **5xx e falha de rede:** 2, 4 e 8 s; depois,
  avisa.
- **Até 4 downloads ao mesmo tempo.** O "Baixar tudo" usa a mesma fila, mostra o total no rodapé da biblioteca e pode
  ser cancelado. O que já baixou fica.
- **Sessão:** `session.json` em 0600, com o token de renovação, a conta e o servidor; nunca o token de acesso nem a
  senha. Trocar o servidor nas preferências invalida a sessão.

## 8. Como o time do site valida a implementação

1. Suba o servidor real num endereço de teste com uma conta de teste e algumas texturas do `manifest.json`
   (`dist/texturas-servidor/`, gerado por `tools/texturas_importar.py`).
2. Compare as rotas com a referência executável: rode
   `python3 tests/fake_texture_server.py --root dist/texturas-servidor --port 8765 --download-all` e faça as mesmas
   chamadas da seção 6 nos dois servidores. Os formatos de corpo, os códigos HTTP e os cabeçalhos (`ETag`,
   `Content-Range`, `Retry-After`) precisam bater.
3. Rode a bateria do plugin contra o servidor real, trocando o servidor falso pelo endereço de teste:
   - em `tests/test_texture_downloader.py`, troque `Server(...)` pelo endereço;
   - em `tests/blender_014_textures_net.py`, use `downloads.set_server("<endereço>")`.
   Os cenários de falha (corte, 429, 401) dependem de o servidor real permitir provocá-los. Sem isso, valem os
   cenários felizes e o 403 com uma conta sem permissão.
4. No Blender, em Preferências › Complementos › CAFFMob Draw › Conta CAF Mob:
   - ponha o endereço;
   - entre (o navegador abre na página de ativação);
   - arraste uma textura para uma peça: ela baixa e aplica.
5. Com a conta de teste sem `download_all`, o "Baixar tudo" precisa ser recusado com o aviso de permissão.
