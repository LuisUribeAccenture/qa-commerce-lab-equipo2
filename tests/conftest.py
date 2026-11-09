import os
import tempfile
from pathlib import Path

import pytest

# Base de datos aislada para las pruebas: se define antes de importar la app
os.environ["QACL_DB"] = str(Path(tempfile.gettempdir()) / "qa_commerce_test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402


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
