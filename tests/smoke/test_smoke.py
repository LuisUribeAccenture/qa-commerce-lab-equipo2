"""Pruebas smoke: verifican que la aplicación arranca y que el flujo principal responde."""


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_catalog_lists_active_products(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert data["page_size"] == 20
    assert len(data["items"]) == 20
    assert all("Descontinuado" not in p["description"] for p in data["items"])


def test_login_with_valid_credentials(client):
    res = client.post("/api/auth/login", json={"email": "ana.garcia@example.com", "password": "Password123"})
    assert res.status_code == 200
    assert res.json()["user"]["name"] == "Ana García"


def test_login_with_wrong_password(client):
    res = client.post("/api/auth/login", json={"email": "ana.garcia@example.com", "password": "incorrecta1"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Correo o contraseña incorrectos"


def test_add_product_to_cart(auth_client):
    res = auth_client.post("/api/cart/items", json={"product_id": 4, "quantity": 2})
    assert res.status_code == 200
    assert res.json()["item_count"] == 2


def test_purchase_happy_path(auth_client):
    auth_client.post("/api/cart/items", json={"product_id": 9, "quantity": 1})
    address = {"street": "Calle Falsa 123", "neighborhood": "Centro", "city": "Monterrey",
               "state": "Nuevo León", "postal_code": "64000", "phone": "8100000000"}
    order = auth_client.post("/api/orders", json={"address": address}).json()
    assert order["status"] == "Pendiente de pago"

    paid = auth_client.post(f"/api/orders/{order['id']}/pay", json={
        "card_holder": "Ana García", "card_number": "4111 1111 1111 1111", "expiry": "12/30", "cvv": "123"})
    assert paid.status_code == 200
    assert paid.json()["status"] == "Pagada"
    assert paid.json()["card_last4"] == "1111"


def test_web_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "QA Commerce Lab" in res.text
