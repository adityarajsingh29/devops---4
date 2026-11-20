"""Integration tests - run against the built container over HTTP (BASE_URL)."""
import os
import urllib.request
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def get(path):
    with urllib.request.urlopen(BASE_URL + path, timeout=5) as resp:
        return resp.status, json.loads(resp.read())


def test_container_health():
    status, body = get("/health")
    assert status == 200 and body["status"] == "ok"


def test_container_serves_expected_version():
    status, body = get("/")
    assert status == 200
    assert body["version"] == os.getenv("EXPECTED_VERSION", body["version"])


def test_container_hides_secret():
    status, body = get("/secret-check")
    assert status == 200
    assert set(body) == {"db_password_loaded", "masked"}
    assert body["masked"] is None or body["masked"].endswith("****")
