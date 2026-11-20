"""Unit tests - run against the Flask app in-process (no network)."""
import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def load_app(**env):
    for k in ("APP_VERSION", "APP_COLOR", "ERROR_RATE", "DB_PASSWORD", "REDIS_HOST"):
        os.environ.pop(k, None)
    os.environ.update(env)
    import app as module
    importlib.reload(module)
    return module.app.test_client()


def test_index_returns_version_and_color():
    client = load_app(APP_VERSION="2.0", APP_COLOR="green")
    data = client.get("/").get_json()
    assert data["version"] == "2.0"
    assert data["color"] == "green"


def test_health_ok():
    client = load_app()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_secret_is_never_returned_in_clear():
    client = load_app(DB_PASSWORD="SuperSecret123")
    data = client.get("/secret-check").get_json()
    assert data["db_password_loaded"] is True
    assert "SuperSecret123" not in str(data)


def test_error_rate_simulates_failures():
    client = load_app(ERROR_RATE="1")
    assert client.get("/").status_code == 500


def test_notes_without_storage_returns_503():
    client = load_app()
    assert client.get("/notes").status_code == 503
