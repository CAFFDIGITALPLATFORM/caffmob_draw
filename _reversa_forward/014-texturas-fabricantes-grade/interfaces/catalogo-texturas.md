# Contrato: pasta de texturas do titular → catálogo do pacote

> Identificador: `014-texturas-fabricantes-grade`
> Tipo: arquivo (entrada local, lida por `tools/texturas_importar.py` no ambiente do desenvolvedor)
> Data: `2026-10-12`

## Entrada (request)

Uma pasta raiz no layout da biblioteca de texturas do Promob:

```
<raiz>/fabrica/<Fabricante>/<Coleção>[/<Subcoleção>]/<arquivo>.<jpg|jpeg|png>
<raiz>/fabrica/<Fabricante>/<arquivo>.<jpg|jpeg|png>            → coleção "Geral"
<raiz>/fabrica/<Fabricante>/.../<arquivo>.<ext>.bump            → relevo de <arquivo>.<ext>
<raiz>/fabrica/<Fabricante>/Bumps/...                          → ignorado como textura
```

- Fabricantes aceitos (RN-01, comparação sem caixa no nome da pasta): `arauco`, `berneck`, `duratex`, `eucatex`,
  `fibraplac`, `floraplac`, `formica`, `greenplac`, `guararapes`, `lopar`, `placas_do_brasil`, `sudati`. A lista é
  dado do script, não regra escondida no código (princípio III).
- Extensões aceitas: `.jpg`, `.jpeg`, `.png`, em qualquer caixa.
- Ignorados: `.bump`, `.bump2`, `.resources`, `.specular`, `.txt`, pastas `Bumps`, arquivos ocultos.

## Saída (response)

- `caffmob_draw/textures/<fabricante>/...`: cópia das imagens aceitas, com o caminho relativo preservado.
- `caffmob_draw/textures/thumbs/<id>.png`: miniatura com 256 px no maior lado.
- `caffmob_draw/textures/catalog.json`: formato em `data-delta.md` §1.
- Relatório no terminal: total por fabricante, avisos e itens ignorados.

## Erros

| Situação | Comportamento |
|----------|---------------|
| Raiz inexistente ou sem `fabrica/` | Sai com código 1 e a mensagem "Pasta de texturas não encontrada: <caminho>"; nada é escrito |
| Fabricante aceito ausente na raiz | Aviso; os demais seguem |
| Imagem ilegível ou corrompida | Aviso com o caminho; fica fora do catálogo |
| Colisão de id na mesma coleção | Sufixo `-2`, `-3`…, e aviso |

## Idempotência

Rodar de novo com a mesma raiz gera o mesmo `catalog.json`, com os mesmos ids e a mesma ordem (fabricante, coleção e
nome, sem caixa), e não recopia imagens iguais (mesmo tamanho e mesma data). Imagens removidas da raiz saem do
catálogo e do pacote.

## Timeouts

Não há rede. A primeira execução copia cerca de 576 MB e gera 1.209 miniaturas; o script mostra o progresso por
fabricante e pode ser interrompido e retomado (idempotente).

## Leitura em tempo de uso (`texture_library/catalog.py`)

- Lê `catalog.json` uma vez por sessão (cache, invalidado só ao recarregar a extensão).
- Arquivo ausente: catálogo vazio e o aviso "Texturas não instaladas" na área Texturas.
- Item cujo `file` não existe no pacote: fica fora da grade, com aviso único por sessão.
