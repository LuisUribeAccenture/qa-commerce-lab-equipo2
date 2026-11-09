"""Verifica que el entorno está listo para los laboratorios del curso.

Uso (desde la carpeta del repositorio, con el entorno virtual activado):
    python tools/check_env.py

Al final imprime un resumen para copiar y pegar en Cypher.
"""
import importlib
import logging
import platform
import re
import shutil
import socket
import subprocess
import sys
import urllib.request
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
logging.disable(logging.INFO)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OK, FAIL, WARN, SKIP = "OK", "FALTA", "AVISO", "OPCIONAL"
results = []


def check(name, status, detail="", fix=""):
    results.append((name, status, detail, fix))


def run(cmd):
    exe = shutil.which(cmd[0])
    if exe is None:
        return None
    try:
        out = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=20)
        return (out.stdout + out.stderr).strip()
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


def version_tuple(text):
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text or "")
    return tuple(int(g or 0) for g in m.groups()) if m else None


def url_ok(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=8):
            return True
    except urllib.error.HTTPError:
        return True  # el servidor respondió: hay conexión
    except Exception:  # noqa: BLE001
        return False


# ---------- Herramientas base (necesarias desde la sesión 3) ----------
py = sys.version_info
check("Python 3.10 o superior", OK if py >= (3, 10) else FAIL, platform.python_version(),
      "Instala Python 3.10+ (guía, paso 2)")

in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
check("Entorno virtual activado", OK if in_venv else WARN, sys.prefix,
      "Activa .venv antes de trabajar (guía, paso 7)")

git = run(["git", "--version"])
check("Git", OK if git else FAIL, git or "no encontrado", "Instala Git (guía, paso 1)")

node = run(["node", "--version"])
nv = version_tuple(node)
check("Node.js 18 o superior", OK if nv and nv >= (18,) else FAIL, node or "no encontrado",
      "Instala Node.js LTS (guía, paso 4)")

codex = run(["codex", "--version"])
check("Codex CLI", OK if codex and not codex.startswith("error") else FAIL, codex or "no encontrado",
      "npm install -g @openai/codex (guía, paso 5)")

code = run(["code", "--version"])
check("VS Code (comando code)", OK if code else WARN, (code or "no encontrado").splitlines()[0],
      "Instala VS Code o agrégalo al PATH; puedes usar otro editor")

# ---------- Dependencias de Python del laboratorio ----------
for module, label in [("fastapi", "FastAPI"), ("uvicorn", "Uvicorn"), ("pytest", "pytest"),
                      ("requests", "requests"), ("playwright", "Playwright para Python")]:
    try:
        importlib.import_module(module)
        check(f"Paquete {label}", OK)
    except ImportError:
        check(f"Paquete {label}", FAIL, "no instalado", "pip install -r requirements-dev.txt (guía, paso 7)")

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.close()
    check("Navegador de Playwright (Chromium)", OK)
except ImportError:
    pass
except Exception as exc:  # noqa: BLE001
    check("Navegador de Playwright (Chromium)", FAIL, str(exc).splitlines()[0][:80],
          "python -m playwright install chromium (guía, paso 7)")

# ---------- La aplicación arranca ----------
try:
    sys.path.insert(0, str(ROOT))
    import os
    import tempfile

    os.environ.setdefault("QACL_DB", str(Path(tempfile.gettempdir()) / "qa_commerce_check.db"))
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        ok = client.get("/api/health").status_code == 200 and client.get("/api/products").json()["total"] > 0
    check("QA Commerce Lab arranca", OK if ok else FAIL, "", "Revisa los mensajes de error")
except Exception as exc:  # noqa: BLE001
    check("QA Commerce Lab arranca", FAIL, str(exc).splitlines()[0][:80], "pip install -r requirements-dev.txt")

with socket.socket() as s:
    port_free = s.connect_ex(("127.0.0.1", 8000)) != 0
check("Puerto 8000", OK if port_free else WARN, "libre" if port_free else "en uso",
      "Si no es QA Commerce Lab, usa otro puerto: uvicorn app.main:app --port 8010")

# ---------- Red ----------
for url, label in [("https://github.com", "Acceso a GitHub"), ("https://pypi.org/simple/", "Acceso a PyPI (pip)"),
                   ("https://registry.npmjs.org/", "Acceso a npm"), ("https://api.openai.com", "Acceso a la API de OpenAI")]:
    check(label, OK if url_ok(url) else FAIL, "", "Posible proxy o firewall: avisa al instructor")

# ---------- Para sesiones posteriores ----------
docker = run(["docker", "--version"])
check("Docker (opcional)", OK if docker else SKIP, docker or "no instalado", "Opcional")
adb = run(["adb", "version"])
check("Android SDK / adb (sesión 6)", OK if adb else SKIP, (adb or "no instalado").splitlines()[0],
      "Se instala con la guía de mobile, antes de la sesión 6")
appium = run(["appium", "--version"])
check("Appium (sesión 6)", OK if appium else SKIP, appium or "no instalado", "Se instala antes de la sesión 6")
k6 = run(["k6", "version"])
check("k6 (sesión 9)", OK if k6 else SKIP, (k6 or "no instalado").splitlines()[0], "Se instala antes de la sesión 9")

# ---------- Reporte ----------
symbols = {OK: "[OK]    ", FAIL: "[FALTA] ", WARN: "[AVISO] ", SKIP: "[--]    "}
print("\nVerificación del entorno · Gen AI aplicada a Testing & QA\n")
for name, status, detail, fix in results:
    line = f"{symbols[status]}{name}"
    if detail:
        line += f"  ({detail})"
    print(line)
    if status in (FAIL, WARN) and fix:
        print(f"         -> {fix}")

fails = [r for r in results if r[1] == FAIL]
warns = [r for r in results if r[1] == WARN]
print("\n" + "-" * 60)
if fails:
    print(f"Faltan {len(fails)} elementos. Revisa las indicaciones de arriba y la guía de instalación.")
else:
    print("Todo listo para la sesión 3." + (f" Hay {len(warns)} avisos." if warns else ""))
print("\nResumen para Cypher (copia esta línea):")
print(f"check_env | {platform.system()} {platform.release()} | Python {platform.python_version()} | "
      f"OK={sum(r[1] == OK for r in results)} FALTA={len(fails)} AVISO={len(warns)} | "
      f"faltan: {', '.join(r[0] for r in fails) or 'nada'}")
sys.exit(1 if fails else 0)
