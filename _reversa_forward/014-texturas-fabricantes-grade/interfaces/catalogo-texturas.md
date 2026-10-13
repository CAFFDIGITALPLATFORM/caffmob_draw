# Contrato: pasta de texturas do titular → catálogo do pacote e pacote do servidor

> Identificador: `014-texturas-fabricantes-grade`
> Tipo: arquivo (entrada local, lida por `tools/texturas_importar.py` no ambiente do desenvolvedor)
> Data: `2026-10-12` (revisão 2: modelo híbrido)

## Entrada (request)

Uma pasta raiz no layout da biblioteca de texturas do Promob:

```
<raiz>/fabrica/<Fabricante>/<Coleção>[/<Subcoleção>]/<arquivo>.<jpg|jpeg|png>
<raiz>/fabrica/<Fabricante>/<arquivo>.<jpg|jpeg|png>            → coleção "Geral"
<raiz>/fabrica/<Fabricante>/.../<arquivo>.<ext>.bump            → relevo de <arquivo>.<ext>
<raiz>/fabrica/<Fabricante>/Bumps/...                          → ignorado como textura
```

- Fabricantes aceitos (RN-01, comparação sem caixa no nome da pasta): `arauco`, `berneck`, `duratex`, `eucatex`,
  `fibraplac`, `floraplac`, `formica`, `greenplac`, `guararapes`, `lopar`, `placas_do_brasil`, `sudati`.
- Extensões aceitas: `.jpg`, `.jpeg`, `.png`, em qualquer caixa.
- Ignorados: `.bump`, `.bump2`, `.resources`, `.specular`, `.txt`, pastas `Bumps`, arquivos ocultos.

## Saída (response)

**No pacote e no git** (`caffmob_draw/textures/`):
- `catalog.json`: formato em `data-delta.md` §1, com `sha256` e `bytes` de cada imagem;
- `thumbs/<id>.png`: miniatura com 256 px no maior lado.

**Para o servidor, fora do pacote e do git** (`dist/texturas-servidor/`):
- `files/<id>.<ext>`: imagens em tamanho real;
- `manifest.json`: `{"version": 1, "items": {"<id>": {"sha256": "…", "bytes": …, "file": "files/<id>.<ext>"}}}`.

O manifesto é o que o servidor publica em `GET /v1/textures/catalog` (`interfaces/servidor-texturas.md` §3).

Ao fim, o script imprime um relatório no terminal: total por fabricante, avisos e itens ignorados.

## Erros

| Situação | Comportamento |
|----------|---------------|
| Raiz inexistente ou sem `fabrica/` | Sai com código 1 e "Pasta de texturas não encontrada: <caminho>"; nada é escrito |
| Fabricante aceito ausente | Aviso; os demais seguem |
| Imagem ilegível ou corrompida | Aviso com o caminho; fica fora do catálogo |
| Colisão de id na mesma coleção | Sufixo `-2`, `-3`…, e aviso |

## Idempotência

Rodar de novo com a mesma raiz gera os mesmos ids, a mesma ordem e os mesmos sha256. Imagens iguais não são
copiadas nem reprocessadas.

## Timeouts

Não há rede. A primeira execução copia cerca de 576 MB e gera 1.209 miniaturas, com progresso por fabricante. Pode ser
interrompida e retomada.
