# tests/test_integration.py
from fastapi.testclient import TestClient

from app.main import app

PATCH = """diff --git a/example.py b/example.py
index 0000000..0000000 100644
--- a/example.py
+++ b/example.py
@@ -1,2 +1,2 @@
-def add(a,b):
-    return a+b
+def add(a, b):
+    return a + b
"""

client = TestClient(app)


def test_validate_and_apply():
    # Validate patch
    resp = client.post("/validate_patch", json={"patch": PATCH})
    assert resp.status_code in (
        200,
        400,
        422,
    )  # service may validate or return structure
    # Try apply_patch and assert JSON shape
    resp2 = client.post("/apply_patch", json={"patch": PATCH})
    assert resp2.status_code == 200
    j = resp2.json()
    assert "applied" in j
    assert isinstance(j.get("applied"), bool)
    # checks key should exist
    assert "checks" in j
