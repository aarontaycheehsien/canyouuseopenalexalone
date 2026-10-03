"""Load the local OpenAlex credential without logging it."""
import os
from pathlib import Path

def load_key():
    if os.environ.get('OPENALEX_API_KEY'):
        return
    raw = (Path(__file__).resolve().parent / '.env.txt').read_text(encoding='utf-8-sig').strip()
    lines = [x.strip() for x in raw.splitlines() if x.strip() and not x.lstrip().startswith('#')]
    if len(lines) == 1 and '=' not in lines[0]:
        value = lines[0]
    else:
        values = {k.strip().lower(): v for k,v in (x.split('=', 1) for x in lines if '=' in x)}
        value = values.get('openalex_api_key', values.get('api_key', values.get('openalex', '')))
    value = value.strip().strip('\"\'')
    if not value or any(c.isspace() for c in value):
        raise ValueError('Local OpenAlex credential has an unrecognized format')
    os.environ['OPENALEX_API_KEY'] = value
