"""Archived HTTP GET/POST (standard library). Every response is stored with its request and UTC time;
a request already archived is replayed from disk, so reruns are offline and identical."""
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFLINE = os.environ.get("SMART_OFFLINE") == "1"
RETRIES = int(os.environ.get("SMART_RETRIES", "8"))


def _path(kind, key):
    return ROOT / "archives" / kind / (hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")


def get(kind, url, params):
    full = url + "?" + urllib.parse.urlencode(params)
    return _call(kind, full, None)


def post(kind, url, body):
    return _call(kind, url, body)


def _call(kind, url, body):
    key = url + "\n" + json.dumps(body, sort_keys=True)
    p = _path(kind, key)
    if p.exists():
        d = json.loads(p.read_text())
        return d["status"], d["response"]
    if OFFLINE:
        raise SystemExit(f"not archived (offline): {url}")
    started = datetime.now(timezone.utc).isoformat()
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if "api.openalex.org" in url:
        headers["Authorization"] = "Bearer proxy-injected"   # replaced by the session proxy; never stored
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=180) as r:
                status, resp = r.status, json.loads(r.read() or b"null")
            break
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                resp = json.loads(e.read() or b"null")
            except ValueError:
                resp = None
            if status in (429, 500, 502, 503, 504):
                if attempt < RETRIES - 1:
                    time.sleep(min(60, 2 ** (attempt + 1)))
                    continue
                raise SystemExit(f"giving up after retries: HTTP {status} {url}")   # never archived
            break
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            if attempt == RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"request": {"method": "POST" if body is not None else "GET", "url": url, "body": body},
                             "status": status, "requested_utc": started, "response": resp}, indent=1))
    time.sleep(0.15)
    return status, resp
