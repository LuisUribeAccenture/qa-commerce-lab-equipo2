"""Fixtures para las pruebas web con Playwright.

- servidor: levanta QA Commerce Lab en un puerto libre, con su propia base de datos.
- base_url: lo usa Playwright para que page.goto("/login") vaya al servidor de pruebas.
- reiniciar_app (automático): deja los datos base antes de CADA prueba (aislamiento).
- cliente_sintetico: crea un cliente y productos con el generador del Lab 3.

Ejecutar:  pytest tests/web            (agrega --headed para ver el navegador)
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

from data.generador import generar_dataset

ROOT = Path(__file__).resolve().parents[2]


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
    env = {**os.environ, "QACL_DB": str(Path(tempfile.gettempdir()) / f"qa_commerce_web_{puerto}.db")}
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


@pytest.fixture(scope="session")
def base_url(servidor):
    return servidor


@pytest.fixture(autouse=True)
def reiniciar_app(servidor):
    _post(f"{servidor}/api/test/reset")


@pytest.fixture
def cliente_sintetico(servidor):
    """Un cliente nuevo (y 3 productos) creados con el generador de datos sintéticos."""
    dataset = generar_dataset(seed=19, clientes=1, productos=3)
    creados = _post(f"{servidor}/api/test/seed", dataset)
    cliente = dataset["users"][0]
    return {**cliente, "product_ids": creados["products"]}


def iniciar_sesion(page, email: str, password: str) -> None:
    """Inicia sesión por la interfaz y espera a volver al catálogo."""
    page.goto("/login")
    page.get_by_label("Correo electrónico").fill(email)
    page.get_by_label("Contraseña").fill(password)
    page.get_by_role("button", name="Entrar").click()
    page.wait_for_url("**/")
