# send_patch.py
import sys
from pathlib import Path

import requests

BASE = "http://127.0.0.1:8000"
URL_VALIDATE = f"{BASE}/validate_patch"
URL_APPLY = f"{BASE}/apply_patch"

PATCH_FILE = Path("patch.diff")
if not PATCH_FILE.exists():
    print("patch.diff not found", file=sys.stderr)
    sys.exit(1)

PATCH = PATCH_FILE.read_text(encoding="utf-8")

payload = {"patch": PATCH}

try:
    resp = requests.post(URL_VALIDATE, json=payload, timeout=10)
    print("VALIDATE status:", resp.status_code)
    print(resp.text)
except requests.exceptions.RequestException as e:
    print("Validate request failed:", e)
    # continue to attempt apply for debugging (optional)

try:
    resp = requests.post(URL_APPLY, json=payload, timeout=20)
    print("APPLY status:", resp.status_code)
    print(resp.text)
except requests.exceptions.RequestException as e:
    print("Apply request failed:", e)
