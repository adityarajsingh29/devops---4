"""Lab 4 sample app used for blue-green, canary, GitOps, secrets and disaster-recovery demos."""
import os
import random
import socket

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "1.0")
COLOR = os.getenv("APP_COLOR", "blue")
ERROR_RATE = float(os.getenv("ERROR_RATE", "0"))  # >0 simulates a bad release (canary rollback demo)
REDIS_HOST = os.getenv("REDIS_HOST", "")
store = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True) if REDIS_HOST else None


@app.route("/")
def index():
    if ERROR_RATE and random.random() < ERROR_RATE:  # nosec B311 - demo only
        return jsonify(error="simulated failure", version=VERSION), 500
    return jsonify(app="lab4-app", version=VERSION, color=COLOR, pod=socket.gethostname())


@app.route("/health")
def health():
    return jsonify(status="ok", version=VERSION)


@app.route("/secret-check")
def secret_check():
    # Never return the secret itself - only whether it was injected and a masked hint
    value = os.getenv("DB_PASSWORD", "")
    return jsonify(db_password_loaded=bool(value), masked=(value[:2] + "****") if value else None)


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if store is None:
        return jsonify(error="no storage configured"), 503
    if request.method == "POST":
        text = (request.get_json(silent=True) or {}).get("text", "").strip()
        if not text:
            return jsonify(error="text is required"), 400
        store.rpush("notes", text)
        return jsonify(saved=text), 201
    return jsonify(notes=store.lrange("notes", 0, -1))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104
