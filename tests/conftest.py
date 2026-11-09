"""Fixtures compartidas por todas las pruebas.

- client / auth_client: cliente en proceso (TestClient), sin servidor. Pruebas rápidas de la API.
- servidor: QA Commerce Lab corriendo de verdad en un puerto libre, con su propia base de datos.
  Lo usan las pruebas web (tests/web) y las de API con requests (tests/api).
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

# Base de datos aislada para las pruebas en proceso: se define antes de importar la app
os.environ["QACL_DB"] = str(Path(tempfile.gettempdir()) / "qa_commerce_test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    init_db(reset=True)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(client):
    """Cliente autenticado como Ana García (usuaria de ejemplo)."""
    res = client.post("/api/auth/login", json={"email": "ana.garcia@example.com", "password": "Password123"})
    client.headers["Authorization"] = f"Bearer {res.json()['token']}"
    return client


# ---------- Servidor real ----------
def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _post(url: str, data: dict | None = None) -> dict:
    req = urllib.request.Request(url, method="POST", data=json.dumps(data or {}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read())


@pytest.fixture(scope="session")
def servidor():
    puerto = _puerto_libre()
    env = {**os.environ, "QACL_DB": str(Path(tempfile.gettempdir()) / f"qa_commerce_srv_{puerto}.db")}
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(puerto)],
                            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{puerto}"
    for _ in range(50):
        try:
            urllib.request.urlopen(f"{url}/api/health", timeout=1)
            break
        except OSError:
            time.sleep(0.2)
    else:
        proc.terminate()
        pytest.fail("La aplicación no arrancó")
    yield url
    proc.terminate()
    proc.wait(timeout=10)
