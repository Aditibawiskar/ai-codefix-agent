# tests/test_main.py
def test_app_importable():
    """
    Simple smoke test: ensure `app.main` module imports and exposes `app`.
    Avoids TestClient/httpx compatibility issues for now.
    """
    import importlib

    mod = importlib.import_module("app.main")
    assert hasattr(mod, "app")
    # Optionally verify the app is a FastAPI instance without importing FastAPI here
    # (keeps test minimal and avoids extra deps).
