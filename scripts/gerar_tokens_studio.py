"""Gera a cópia Python dos tokens, sem alterar o MOBI nem depender de pacotes."""
import hashlib
import json
from pathlib import Path
from pprint import pformat

import sys

# Uso: python3 scripts/gerar_tokens_studio.py <apps/caff-mobi/shared/studio/tokens.json>
ADDON = Path(__file__).resolve().parents[1]
fonte = Path(sys.argv[1]) if len(sys.argv) > 1 else ADDON.parent / 'caff-mobi/shared/studio/tokens.json'
destino = ADDON / 'caffmob_draw/walls2d/tokens_studio.py'
dados = fonte.read_bytes()
destino.write_text('"""Gerado por scripts/gerar_tokens_studio.py; fonte: shared/studio/tokens.json."""\n'
                   + 'SHA256 = ' + repr(hashlib.sha256(dados).hexdigest()) + '\n'
                   + 'TOKENS = ' + pformat(json.loads(dados), sort_dicts=False, width=110) + '\n', encoding='utf-8')
