"""Lab 6.1 · Casos aprobados de pruebas negativas y de seguridad de la API."""

import json
import logging
from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest

from app import security
from app.routes import auth, orders


ANA = {"email": "ana.garcia@example.com", "password": "Password123"}
LUIS = {"email": "luis.perez@example.com", "password": "Password123"}
REGISTRO = {
    "name": "Cliente Sintético",
    "email": "seguridad@example.com",
    "password": "Prueba123",
    "password_confirm": "Prueba123",
    "birth_date": "1990-01-01",
}
DIRECCION = {
    "street": "Calle Sintética 734",
    "neighborhood": "Colonia de Pruebas",
    "city": "Monterrey",
    "state": "Nuevo León",
    "postal_code": "64000",
    "phone": "8100573186",
}
AHORA = datetime(2026, 11, 18, 12)
PAGO = {
    "card_holder": "Titular Sintético",
    "card_number": "4111111111111111",
    "expiry": "11/26",
    "cvv": "321",
}
LOGIN = "/api/auth/login"
REGISTRAR = "/api/auth/register"
ORDENES = "/api/orders"
CARRITO = "/api/cart"
AGREGAR = f"{CARRITO}/items"
CREDENCIALES_INVALIDAS = "Correo o contraseña incorrectos"


def _sesion(client, credenciales):
    res = client.post(LOGIN, json=credenciales)
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['token']}"}


@pytest.fixture
def api(client):
    """Adapta la fixture compartida a la interfaz de la prueba de ejemplo."""
    return SimpleNamespace(session=client, get=client.get)


@pytest.fixture
def api_ana(client):
    return _sesion(client, ANA)


@pytest.fixture
def api_luis(client):
    return _sesion(client, LUIS)


@pytest.fixture
def fijar_reloj(monkeypatch):
    def fijar(fecha):
        class FechaRegistro(date):
            @classmethod
            def today(cls):
                return fecha.date()

        monkeypatch.setattr(security, "now", lambda: fecha)
        monkeypatch.setattr(auth, "now", lambda: fecha)
        monkeypatch.setattr(auth, "date", FechaRegistro)

    return fijar


def _error(res, codigo, mensaje):
    assert res.status_code == codigo
    datos = res.json()
    assert datos["detail"] == mensaje
    return datos


def _error_de_campo(res, campo):
    assert res.status_code == 400
    datos = res.json()
    assert isinstance(datos["detail"], str) and datos["detail"].strip()
    assert set(datos["errors"]) == {campo}
    assert isinstance(datos["errors"][campo], str) and datos["errors"][campo].strip()
    return datos


def _agregar_valido(client, sesion, producto_id=1, cantidad=1):
    res = client.post(AGREGAR, headers=sesion, json={"product_id": producto_id, "quantity": cantidad})
    assert res.status_code == 200
    assert [(p["product_id"], p["quantity"]) for p in res.json()["items"]] == [(producto_id, cantidad)]


def _carrito(client, sesion):
    res = client.get(CARRITO, headers=sesion)
    assert res.status_code == 200
    return res.json()["items"]


def _orden_pendiente(client, sesion):
    _agregar_valido(client, sesion)
    res = client.post(ORDENES, headers=sesion, json={"address": DIRECCION})
    assert res.status_code == 201
    assert res.json()["status"] == "Pendiente de pago"
    return f"{ORDENES}/{res.json()['id']}"


def _existencias(client, producto_id):
    res = client.get(f"/api/products/{producto_id}")
    assert res.status_code == 200
    return res.json()["stock"]


# CA-06.1 · Prueba de ejemplo
def test_token_invalido(api):  # ejemplo
    api.session.headers["Authorization"] = "Bearer token-inventado"
    res = api.get("/api/cart")
    assert res.status_code == 401


def test_listado_excluye_orden_ajena(client, api_ana, api_luis):
    # CA-12.1, CA-12.5 · El listado devuelve únicamente órdenes del cliente.
    orden_de_ana = int(_orden_pendiente(client, api_ana).rsplit("/", 1)[1])
    ana = client.get(ORDENES, headers=api_ana)
    luis = client.get(ORDENES, headers=api_luis)
    assert ana.status_code == luis.status_code == 200
    assert {orden["id"] for orden in ana.json()} == {orden_de_ana}
    assert {orden["id"] for orden in luis.json()} == {1}


@pytest.mark.xfail(strict=True, reason="BUG-02: el detalle permite ver una orden ajena (CA-12.5)")
def test_detalle_ajeno_no_expone_orden(client, api_ana, api_luis):
    # CA-12.2, CA-12.5, RNF-04 · Solo el titular puede consultar el detalle.
    ruta = f"{ORDENES}/1"
    titular = client.get(ruta, headers=api_luis)
    assert titular.status_code == 200
    assert titular.json()["id"] == 1

    datos = _error(client.get(ruta, headers=api_ana), 404, "Orden no encontrada")
    assert set(datos) == {"detail"}


def test_cancelacion_ajena_no_modifica_orden_ni_stock(client, api_ana, api_luis):
    # CA-12.3–CA-12.5, RN-09 · El control usa una orden pagada y apta para cancelación.
    preparar = client.post("/api/test/orders/1/status", json={
        "status": "Pagada", "paid_at": (datetime.now() - timedelta(minutes=1)).isoformat(),
    })
    assert preparar.status_code == 200
    ruta = f"{ORDENES}/1"
    titular = client.get(ruta, headers=api_luis)
    assert titular.status_code == 200
    assert titular.json()["status"] == "Pagada"
    cantidades = {item["product_id"]: item["quantity"] for item in titular.json()["items"]}
    assert cantidades
    stock = {producto: _existencias(client, producto) for producto in cantidades}

    _error(client.post(f"{ruta}/cancel", headers=api_ana), 404, "Orden no encontrada")
    anterior = client.get(ruta, headers=api_luis)
    assert anterior.status_code == 200
    assert anterior.json() == titular.json()
    for producto, cantidad in stock.items():
        assert _existencias(client, producto) == cantidad

    control = client.post(f"{ruta}/cancel", headers=api_luis)
    assert control.status_code == 200
    assert control.json()["status"] == "Cancelada"
    for producto, cantidad in stock.items():
        assert _existencias(client, producto) == cantidad + cantidades[producto]


@pytest.mark.parametrize("token", [None, "token-sintetico-invalido"], ids=["ausente", "invalido"])
def test_alta_carrito_requiere_token_valido(client, api_ana, token):
    # CA-06.1 · Agregar al carrito requiere una sesión autenticada.
    encabezados = {"Authorization": f"Bearer {token}"} if token else {}
    res = client.post(AGREGAR, headers=encabezados, json={"product_id": 1, "quantity": 1})
    _error(res, 401, "Debes iniciar sesión")
    assert _carrito(client, api_ana) == []
    _agregar_valido(client, api_ana)


def test_alta_carrito_rechaza_sesion_expirada(client, fijar_reloj):
    # CA-02.5, CA-06.1 · La inactividad superior a 30 minutos invalida la sesión.
    fijar_reloj(AHORA)
    expirada = _sesion(client, ANA)
    vigente = _sesion(client, ANA)
    fijar_reloj(AHORA + timedelta(minutes=2))
    assert _carrito(client, vigente) == []
    fijar_reloj(AHORA + timedelta(minutes=31))

    res = client.post(AGREGAR, headers=expirada, json={"product_id": 1, "quantity": 1})
    _error(res, 401, "Tu sesión expiró")
    assert _carrito(client, vigente) == []
    _agregar_valido(client, vigente)


@pytest.mark.xfail(strict=True, reason="BUG-03: el código del login distingue cuentas existentes (CA-02.2)")
def test_login_devuelve_error_generico(client):
    # CA-02.1, CA-02.2 · El contrato de login usa 401 para credenciales inválidas.
    clave_erronea = {**ANA, "password": "Incorrecta123"}
    inexistente = client.post(LOGIN, json={**clave_erronea, "email": "inexistente@example.com"})
    incorrecta = client.post(LOGIN, json=clave_erronea)
    _sesion(client, ANA)
    assert inexistente.json() == incorrecta.json() == {"detail": CREDENCIALES_INVALIDAS}
    assert (inexistente.status_code, incorrecta.status_code) == (401, 401)


@pytest.mark.parametrize("fallos", [4, 5])
def test_login_bloquea_tras_cinco_fallos(client, fijar_reloj, fallos):
    # CA-02.1, CA-02.3, CA-02.4, RN-04 · Bloqueo de 15 minutos a partir del quinto fallo.
    fijar_reloj(AHORA)
    for _ in range(fallos):
        res = client.post(LOGIN, json={**ANA, "password": "Incorrecta123"})
        _error(res, 401, CREDENCIALES_INVALIDAS)

    if fallos == 4:
        _sesion(client, ANA)
        return

    fijar_reloj(AHORA + timedelta(minutes=14, seconds=59))
    _error(client.post(LOGIN, json=ANA), 423, "Cuenta bloqueada temporalmente. Intenta más tarde.")
    fijar_reloj(AHORA + timedelta(minutes=15, seconds=1))
    _sesion(client, ANA)


@pytest.mark.parametrize("operacion", [
    "registro",
    pytest.param("direccion", marks=pytest.mark.xfail(
        strict=True, reason="BUG-04: el error de dirección expone datos personales (RNF-04)",
    )),
    "pago",
])
def test_errores_y_logs_omiten_datos_personales(client, api_ana, caplog, monkeypatch, operacion):
    # RNF-04 · Las respuestas de error y los logs omiten los valores personales enviados.
    monkeypatch.setattr(orders, "now", lambda: AHORA)
    datos_personales = {}
    if operacion == "registro":
        ruta = REGISTRAR
        campo = "password"
        cuerpo = {**REGISTRO, "password": "SinNumeros", "password_confirm": "SinNumeros"}
        encabezados = {}
        datos_personales["correo"] = cuerpo["email"]
    elif operacion == "direccion":
        _agregar_valido(client, api_ana)
        ruta = ORDENES
        campo = "postal_code"
        cuerpo = {"address": {**DIRECCION, "postal_code": "6400"}}
        encabezados = api_ana
        datos_personales.update(correo=ANA["email"], **cuerpo["address"])
    else:
        ruta = f"{_orden_pendiente(client, api_ana)}/pay"
        campo = "cvv"
        cuerpo = {**PAGO, "cvv": "8742"}
        encabezados = api_ana
        datos_personales.update(tarjeta=cuerpo["card_number"], cvv=cuerpo["cvv"], vencimiento=cuerpo["expiry"])

    caplog.clear()
    with caplog.at_level("INFO"):
        marcador = "Control de captura RNF-04"
        logging.getLogger(__name__).info(marcador)
        res = client.post(ruta, headers=encabezados, json=cuerpo)
    assert marcador in caplog.messages
    respuesta = json.dumps(_error_de_campo(res, campo), ensure_ascii=False)
    en_respuesta = [nombre for nombre, valor in datos_personales.items() if valor in respuesta]
    en_logs = [nombre for nombre, valor in datos_personales.items() if valor in caplog.text]
    assert (en_respuesta, en_logs) == ([], []), "Campos expuestos en la respuesta y en los logs"


@pytest.mark.parametrize("campo", ["quantity", "address"])
def test_rechaza_tipos_incompatibles(client, api_ana, campo):
    # Esquemas CartItemIn.quantity y OrderIn.address · 422 para tipos incompatibles.
    if campo == "quantity":
        ruta, cuerpo = AGREGAR, {"product_id": 1, "quantity": {}}
    else:
        _agregar_valido(client, api_ana)
        ruta, cuerpo = ORDENES, {"address": []}

    res = client.post(ruta, headers=api_ana, json=cuerpo)
    assert res.status_code == 422
    errores = res.json()["detail"]
    assert [error["loc"] for error in errores] == [["body", campo]]
    assert isinstance(errores[0]["msg"], str) and errores[0]["msg"].strip()

    if campo == "quantity":
        _agregar_valido(client, api_ana)
    else:
        control = client.post(ORDENES, headers=api_ana, json={"address": DIRECCION})
        assert control.status_code == 201
        assert control.json()["status"] == "Pendiente de pago"


@pytest.mark.parametrize("campo", list(REGISTRO))
def test_registro_rechaza_campos_omitidos(client, campo):
    # CA-01.1, CA-01.2, CA-01.7 · Cada campo requerido tiene un mensaje de error.
    cuerpo = {nombre: valor for nombre, valor in REGISTRO.items() if nombre != campo}
    mensaje = _error_de_campo(client.post(REGISTRAR, json=cuerpo), campo)["errors"][campo].casefold()
    assert "obligatori" in mensaje or (campo == "password_confirm" and "coincid" in mensaje)
    control = client.post(REGISTRAR, json=REGISTRO)
    assert control.status_code == 201
    assert control.json()["token"]


@pytest.mark.parametrize(("campo", "invalido", "valido"), [
    ("email", "correo-invalido.example.com", "seguridad@example.com"),
    ("password", "abc1234", "abcd1234"),
    ("password", "a1" * 32 + "b", "a1" * 32),
    ("birth_date", "2009-11-18", "2008-11-18"),
], ids=["correo", "clave-7", "clave-65", "menor"])
def test_registro_rechaza_valores_invalidos(client, fijar_reloj, campo, invalido, valido):
    # CA-01.3–CA-01.5, CA-01.7, RN-02, RN-03 · Un campo inválido por solicitud.
    fijar_reloj(AHORA)
    cuerpo = {**REGISTRO, campo: invalido}
    if campo == "password":
        cuerpo["password_confirm"] = invalido
    mensaje = _error_de_campo(client.post(REGISTRAR, json=cuerpo), campo)["errors"][campo].casefold()
    if campo == "email":
        assert "formato" in mensaje
    elif campo == "password":
        assert all(fragmento in mensaje for fragmento in ("8", "64", "letra", "número"))
    else:
        assert "mayor de edad" in mensaje or "18" in mensaje

    cuerpo[campo] = valido
    if campo == "password":
        cuerpo["password_confirm"] = valido
    control = client.post(REGISTRAR, json=cuerpo)
    assert control.status_code == 201
    assert control.json()["token"]


@pytest.mark.parametrize(("cantidad", "stock", "valida", "codigo", "mensaje"), [
    (0, 20, 1, 400, "La cantidad debe estar entre 1 y 10"),
    pytest.param(11, 20, 10, 400, "La cantidad debe estar entre 1 y 10", marks=pytest.mark.xfail(
        strict=True, reason="BUG-05: el carrito admite 11 unidades (CA-06.2, RN-05)",
    )),
    (6, 5, 5, 409, "Solo hay 5 unidades disponibles"),
], ids=["cero", "once", "supera-stock"])
def test_carrito_rechaza_cantidad_fuera_de_rango(client, api_ana, cantidad, stock, valida, codigo, mensaje):
    # CA-06.2, RN-05 · El alta admite de 1 a 10 unidades y hasta el stock disponible.
    origen = client.post("/api/test/seed", json={"products": [
        {"name": "Producto de prueba", "price": 100, "stock": stock},
    ]})
    assert origen.status_code == 200
    producto = origen.json()["products"][0]
    res = client.post(AGREGAR, headers=api_ana, json={"product_id": producto, "quantity": cantidad})
    _error(res, codigo, mensaje)
    assert _carrito(client, api_ana) == []
    _agregar_valido(client, api_ana, producto, valida)


@pytest.mark.parametrize(("campo", "valor", "mensaje"), [
    ("postal_code", "6400", "El código postal debe tener 5 dígitos"),
    ("postal_code", "640001", "El código postal debe tener 5 dígitos"),
    ("phone", "810057318", "El teléfono debe tener 10 dígitos"),
    ("phone", "81005731863", "El teléfono debe tener 10 dígitos"),
], ids=["cp-4", "cp-6", "telefono-9", "telefono-11"])
def test_checkout_rechaza_direccion_invalida(client, api_ana, campo, valor, mensaje):
    # CA-10.2, CA-10.5 · Una dirección inválida no crea una orden.
    _agregar_valido(client, api_ana)
    antes = client.get(ORDENES, headers=api_ana)
    assert antes.status_code == 200
    res = client.post(ORDENES, headers=api_ana, json={"address": {**DIRECCION, campo: valor}})
    assert _error_de_campo(res, campo)["errors"][campo] == mensaje
    despues = client.get(ORDENES, headers=api_ana)
    assert despues.status_code == 200
    assert despues.json() == antes.json()

    control = client.post(ORDENES, headers=api_ana, json={"address": DIRECCION})
    assert control.status_code == 201
    assert control.json()["status"] == "Pendiente de pago"


@pytest.mark.parametrize(("campo", "valor", "mensaje"), [
    ("card_number", "411111111111111", "El número de tarjeta debe tener 16 dígitos"),
    ("card_number", "41111111111111111", "El número de tarjeta debe tener 16 dígitos"),
    ("expiry", "10/26", "La tarjeta está vencida"),
    ("cvv", "32", "El CVV debe tener 3 dígitos"),
    ("cvv", "3210", "El CVV debe tener 3 dígitos"),
], ids=["tarjeta-15", "tarjeta-17", "mes-anterior", "cvv-2", "cvv-4"])
def test_pago_rechaza_datos_invalidos(client, api_ana, monkeypatch, campo, valor, mensaje):
    # CA-11.2, CA-11.4 · Un pago inválido no cambia el estado de la orden.
    monkeypatch.setattr(orders, "now", lambda: AHORA)
    ruta = _orden_pendiente(client, api_ana)
    carrito = _carrito(client, api_ana)
    stock = {item["product_id"]: _existencias(client, item["product_id"]) for item in carrito}
    res = client.post(f"{ruta}/pay", headers=api_ana, json={**PAGO, campo: valor})
    datos = _error_de_campo(res, campo)
    assert datos["detail"] == "Revisa los datos de la tarjeta"
    assert datos["errors"][campo] == mensaje
    pendiente = client.get(ruta, headers=api_ana)
    assert pendiente.status_code == 200
    assert pendiente.json()["status"] == "Pendiente de pago"
    assert _carrito(client, api_ana) == carrito
    for producto, cantidad in stock.items():
        assert _existencias(client, producto) == cantidad

    control = client.post(f"{ruta}/pay", headers=api_ana, json=PAGO)
    assert control.status_code == 200
    assert control.json()["status"] == "Pagada"
