// QA Commerce Lab — lógica del cliente web. Todas las operaciones usan la API REST (/api).

const TOKEN_KEY = "qacl_token";
const USER_KEY = "qacl_user";
const FLASH_KEY = "qacl_flash";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function getUser() { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); }
function saveSession(data) {
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
}
function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function money(n) {
  return "$" + Number(n).toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function flash(message, type = "ok") {
  const box = $("#flash");
  box.className = `flash ${type}`;
  box.textContent = message;
}

function flashNext(message) { sessionStorage.setItem(FLASH_KEY, message); }

function goToLogin() {
  location.href = `/login?next=${encodeURIComponent(location.pathname)}`;
}

async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (res.status === 401 && token) {
    clearSession();
    flashNext((data && data.detail) || "Debes iniciar sesión");
    goToLogin();
  }
  if (!res.ok) {
    const err = new Error((data && data.detail) || "Ocurrió un error");
    err.status = res.status;
    err.errors = (data && data.errors) || {};
    throw err;
  }
  return data;
}

function requireAuth() {
  if (!getToken()) { goToLogin(); return false; }
  return true;
}

function showFieldErrors(form, errors) {
  $$("[data-error-for]", form).forEach((p) => { p.textContent = errors[p.dataset.errorFor] || ""; });
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

// ---------- Encabezado ----------
async function refreshCartCount() {
  if (!getToken()) return;
  try {
    const cart = await api("/cart");
    $("#cart-count").textContent = cart.item_count;
  } catch (_) { /* sin carrito */ }
}

function renderHeader() {
  const user = getUser();
  $$(".auth-only").forEach((el) => { el.hidden = !user; });
  $$(".guest-only").forEach((el) => { el.hidden = !!user; });
  if (user) $("#user-name").textContent = user.name;
  $("#logout").addEventListener("click", async () => {
    try { await api("/auth/logout", { method: "POST" }); } catch (_) { /* ya expiró */ }
    clearSession();
    location.href = "/";
  });
  refreshCartCount();
  const pending = sessionStorage.getItem(FLASH_KEY);
  if (pending) { flash(pending); sessionStorage.removeItem(FLASH_KEY); }
}

// ---------- Catálogo ----------
async function addToCart(productId, quantity) {
  if (!getToken()) { goToLogin(); return; }
  try {
    const cart = await api("/cart/items", { method: "POST", body: { product_id: productId, quantity } });
    $("#cart-count").textContent = cart.item_count;
    flash("Producto agregado al carrito");
  } catch (e) {
    flash(e.message, "error");
  }
}

function productCard(p) {
  return `
    <article class="card product" data-testid="product-card">
      <img src="${p.image}" alt="" width="64" height="64">
      <h2><a href="/productos/${p.id}">${escapeHtml(p.name)}</a></h2>
      <p class="muted">${escapeHtml(p.category)}</p>
      <p class="price">${money(p.price)}</p>
      ${p.available ? "" : '<p class="tag out">Agotado</p>'}
      <button type="button" data-add="${p.id}" ${p.available ? "" : "disabled"}
        aria-label="Agregar ${escapeHtml(p.name)} al carrito">Agregar al carrito</button>
    </article>`;
}

async function initCatalog() {
  const params = new URLSearchParams(location.search);
  const page = Number(params.get("page") || 1);
  const cats = await api("/categories");
  $("#category").insertAdjacentHTML("beforeend",
    cats.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join(""));
  $("#search").value = params.get("search") || "";
  $("#category").value = params.get("category") || "";
  $("#sort").value = params.get("sort") || "";

  const query = new URLSearchParams();
  for (const k of ["search", "category", "sort"]) if (params.get(k)) query.set(k, params.get(k));
  query.set("page", page);
  const data = await api(`/products?${query}`);

  const list = $("#product-list");
  list.innerHTML = data.items.map(productCard).join("");
  $("#results-info").textContent = data.total
    ? `${data.total} productos`
    : "No encontramos productos para tu búsqueda";
  const pages = Math.max(1, Math.ceil(data.total / data.page_size));
  $("#page-info").textContent = `Página ${page} de ${pages}`;
  $("#prev-page").disabled = page <= 1;
  $("#next-page").disabled = page >= pages;

  const goTo = (p) => { params.set("page", p); location.search = params.toString(); };
  $("#prev-page").addEventListener("click", () => goTo(page - 1));
  $("#next-page").addEventListener("click", () => goTo(page + 1));
  $("#filters").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const next = new URLSearchParams();
    for (const [k, v] of Object.entries(formData(ev.target))) if (v) next.set(k, v);
    location.search = next.toString();
  });
  list.addEventListener("click", (ev) => {
    const btn = ev.target.closest("[data-add]");
    if (btn) addToCart(Number(btn.dataset.add), 1);
  });
}

// ---------- Detalle de producto ----------
async function initProduct() {
  const box = $("#product");
  let p;
  try {
    p = await api(`/products/${box.dataset.productId}`);
  } catch (e) {
    box.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
    return;
  }
  box.innerHTML = `
    <img src="${p.image}" alt="" width="160" height="160">
    <div>
      <h1>${escapeHtml(p.name)}</h1>
      <p class="muted">${escapeHtml(p.category)}</p>
      <p>${escapeHtml(p.description)}</p>
      <p class="price big">${money(p.price)}</p>
      <p id="stock">${p.available ? `Disponibles: ${p.stock}` : '<span class="tag out">Agotado</span>'}</p>
      ${p.low_stock ? '<p class="tag warn">¡Últimas unidades!</p>' : ""}
      <form id="add-form" class="row" novalidate>
        <label for="qty">Cantidad</label>
        <input id="qty" type="number" min="1" max="10" value="1" ${p.available ? "" : "disabled"}>
        <button type="submit" ${p.available ? "" : "disabled"}>Agregar al carrito</button>
      </form>
      <p class="error" id="qty-error" role="alert"></p>
    </div>`;
  $("#add-form").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const qty = Number($("#qty").value);
    if (!Number.isInteger(qty) || qty < 1 || qty > 10) {
      $("#qty-error").textContent = "La cantidad debe estar entre 1 y 10";
      return;
    }
    $("#qty-error").textContent = "";
    addToCart(p.id, qty);
  });
}

// ---------- Login y registro ----------
function initLogin() {
  $("#login-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    $("#login-error").textContent = "";
    try {
      saveSession(await api("/auth/login", { method: "POST", body: formData(ev.target) }));
      location.href = new URLSearchParams(location.search).get("next") || "/";
    } catch (e) {
      $("#login-error").textContent = e.message;
    }
  });
}

function initRegister() {
  const form = $("#register-form");
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    showFieldErrors(form, {});
    $("#register-error").textContent = "";
    try {
      const data = await api("/auth/register", { method: "POST", body: formData(form) });
      saveSession(data);
      flashNext(`Bienvenido, ${data.user.name}`);
      location.href = "/";
    } catch (e) {
      showFieldErrors(form, e.errors);
      $("#register-error").textContent = e.message;
      form.password.value = "";
      form.password_confirm.value = "";
    }
  });
}

// ---------- Carrito ----------
const SHIPPING_COST = 99;
const FREE_SHIPPING_FROM = 999;

function renderCartSummary(cart) {
  const subtotal = cart.items.reduce((acc, i) => acc + i.line_total, 0);
  const discount = Number(cart.discount);
  let shipping = cart.items.length ? SHIPPING_COST : 0;
  if (subtotal > FREE_SHIPPING_FROM || cart.coupon_code === "ENVIOGRATIS") shipping = 0;
  const total = subtotal - discount + shipping;

  $("#sum-subtotal").textContent = money(subtotal);
  $("#sum-discount").textContent = discount ? `-${money(discount)}` : money(0);
  $("#sum-shipping").textContent = shipping ? money(shipping) : "Gratis";
  $("#sum-total").textContent = money(total);
}

function scheduleSummary(cart) {
  // Espera a que el usuario termine de editar antes de recalcular el resumen
  setTimeout(() => renderCartSummary(cart), 300 + Math.random() * 1200);
}

function renderCart(cart, { deferSummary = false } = {}) {
  const box = $("#cart-items");
  const checkout = $("#go-checkout");
  $("#cart-count").textContent = cart.item_count;
  if (!cart.items.length) {
    box.innerHTML = '<p class="empty">Tu carrito está vacío</p>';
    checkout.classList.add("disabled");
    checkout.setAttribute("aria-disabled", "true");
    checkout.removeAttribute("href");
  } else {
    checkout.classList.remove("disabled");
    checkout.removeAttribute("aria-disabled");
    checkout.setAttribute("href", "/checkout");
    box.innerHTML = cart.items.map((i) => `
      <div class="card cart-item" data-product-id="${i.product_id}">
        <img src="${i.image}" alt="" width="48" height="48">
        <a href="/productos/${i.product_id}">${escapeHtml(i.name)}</a>
        <span class="muted">${money(i.price)} c/u</span>
        <input type="number" min="0" max="10" value="${i.quantity}" aria-label="Cantidad de ${escapeHtml(i.name)}">
        <span class="line-total">${money(i.line_total)}</span>
        <button type="button" class="link" data-remove aria-label="Eliminar ${escapeHtml(i.name)}">Eliminar</button>
      </div>`).join("");
  }
  $("#coupon-applied").hidden = !cart.coupon_code;
  $("#coupon-name").textContent = cart.coupon_code || "";
  if (deferSummary) scheduleSummary(cart); else renderCartSummary(cart);
}

async function initCart() {
  if (!requireAuth()) return;
  renderCart(await api("/cart"));

  $("#cart-items").addEventListener("change", async (ev) => {
    if (!ev.target.matches("input[type=number]")) return;
    const row = ev.target.closest("[data-product-id]");
    const qty = Number(ev.target.value);
    if (!Number.isInteger(qty) || qty < 0 || qty > 10) {
      flash("La cantidad debe estar entre 1 y 10", "error");
      renderCart(await api("/cart"));
      return;
    }
    try {
      const cart = await api(`/cart/items/${row.dataset.productId}`, { method: "PATCH", body: { quantity: qty } });
      renderCart(cart, { deferSummary: true });
    } catch (e) {
      flash(e.message, "error");
      renderCart(await api("/cart"));
    }
  });
  $("#cart-items").addEventListener("click", async (ev) => {
    if (!ev.target.matches("[data-remove]")) return;
    const row = ev.target.closest("[data-product-id]");
    renderCart(await api(`/cart/items/${row.dataset.productId}`, { method: "DELETE" }), { deferSummary: true });
  });
  $("#coupon-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    $("#coupon-error").textContent = "";
    try {
      const cart = await api("/cart/coupon", { method: "POST", body: { code: $("#coupon-code").value } });
      $("#coupon-code").value = "";
      renderCart(cart, { deferSummary: true });
    } catch (e) {
      $("#coupon-error").textContent = e.message;
    }
  });
  $("#remove-coupon").addEventListener("click", async () => {
    renderCart(await api("/cart/coupon", { method: "DELETE" }), { deferSummary: true });
  });
}

// ---------- Checkout ----------
async function initCheckout() {
  if (!requireAuth()) return;
  const [cart, me] = await Promise.all([api("/cart"), api("/me")]);
  if (!cart.items.length) { location.href = "/carrito"; return; }

  $("#checkout-items").innerHTML = cart.items
    .map((i) => `<li>${i.quantity} × ${escapeHtml(i.name)} <span>${money(i.line_total)}</span></li>`).join("");
  $("#co-subtotal").textContent = money(cart.subtotal);
  $("#co-discount").textContent = Number(cart.discount) ? `-${money(cart.discount)}` : money(0);
  $("#co-shipping").textContent = cart.shipping ? money(cart.shipping) : "Gratis";
  $("#co-total").textContent = money(cart.total);

  const form = $("#address-form");
  if (me.saved_address) {
    for (const [k, v] of Object.entries(me.saved_address)) if (form.elements[k]) form.elements[k].value = v;
  }
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    showFieldErrors(form, {});
    $("#checkout-error").textContent = "";
    const data = formData(form);
    const body = { address: { ...data }, save_address: $("#addr-save").checked };
    delete body.address.save_address;
    try {
      const order = await api("/orders", { method: "POST", body });
      location.href = `/pago/${order.id}`;
    } catch (e) {
      showFieldErrors(form, e.errors);
      $("#checkout-error").textContent = e.message;
    }
  });
}

// ---------- Pago ----------
async function initPayment() {
  if (!requireAuth()) return;
  const id = $("#payment").dataset.orderId;
  const order = await api(`/orders/${id}`);
  $("#pay-total").textContent = money(order.total);
  const form = $("#payment-form");
  if (order.status !== "Pendiente de pago") {
    form.innerHTML = `<p>Esta orden ya fue procesada (estado: ${escapeHtml(order.status)}).</p>`;
    return;
  }
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    showFieldErrors(form, {});
    $("#payment-error").textContent = "";
    try {
      const paid = await api(`/orders/${id}/pay`, { method: "POST", body: formData(form) });
      $("#payment").hidden = true;
      $("#confirmation").hidden = false;
      $("#confirm-order").textContent = `#${paid.id}`;
      $("#confirm-last4").textContent = paid.card_last4;
      $("#cart-count").textContent = "0";
    } catch (e) {
      if (e.status === 400) showFieldErrors(form, e.errors);
      $("#payment-error").textContent = e.message;
    }
  });
}

// ---------- Órdenes ----------
function formatDate(iso) {
  return new Date(iso).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" });
}

async function initOrders() {
  if (!requireAuth()) return;
  const orders = await api("/orders");
  $("#orders-empty").hidden = orders.length > 0;
  $("#orders-table").hidden = orders.length === 0;
  $("#orders-table tbody").innerHTML = orders.map((o) => `
    <tr>
      <td><a href="/ordenes/${o.id}">#${o.id}</a></td>
      <td>${formatDate(o.created_at)}</td>
      <td>${money(o.total)}</td>
      <td><span class="status">${escapeHtml(o.status)}</span></td>
    </tr>`).join("");
}

function renderOrder(o) {
  const a = o.address;
  $("#order").innerHTML = `
    <p>Estado: <strong id="order-status">${escapeHtml(o.status)}</strong></p>
    <p class="muted">Creada: ${formatDate(o.created_at)}${o.paid_at ? ` · Pagada: ${formatDate(o.paid_at)}` : ""}</p>
    <table class="table">
      <thead><tr><th scope="col">Producto</th><th scope="col">Cantidad</th><th scope="col">Precio</th></tr></thead>
      <tbody>${o.items.map((i) => `<tr><td>${escapeHtml(i.name)}</td><td>${i.quantity}</td><td>${money(i.unit_price)}</td></tr>`).join("")}</tbody>
    </table>
    <dl>
      <dt>Subtotal</dt><dd>${money(o.subtotal)}</dd>
      <dt>Descuento</dt><dd>${o.discount ? `-${money(o.discount)}` : money(0)}</dd>
      <dt>Envío</dt><dd>${o.shipping ? money(o.shipping) : "Gratis"}</dd>
      <dt class="total">Total</dt><dd class="total">${money(o.total)}</dd>
    </dl>
    <p>Envío a: ${escapeHtml(`${a.street}, ${a.neighborhood}, ${a.city}, ${a.state}, C.P. ${a.postal_code}`)}</p>
    ${o.card_last4 ? `<p>Tarjeta terminada en ${escapeHtml(o.card_last4)}</p>` : ""}
    ${o.status === "Pendiente de pago" ? `<a class="button" href="/pago/${o.id}">Pagar</a>` : ""}
    ${o.status === "Pagada" ? '<button type="button" id="cancel-order">Cancelar orden</button>' : ""}`;
  const cancel = $("#cancel-order");
  if (cancel) cancel.addEventListener("click", async () => {
    if (!confirm("¿Seguro que quieres cancelar esta orden?")) return;
    try {
      renderOrder(await api(`/orders/${o.id}/cancel`, { method: "POST" }));
      flash("La orden fue cancelada");
    } catch (e) {
      flash(e.message, "error");
    }
  });
}

async function initOrder() {
  if (!requireAuth()) return;
  try {
    renderOrder(await api(`/orders/${$("#order").dataset.orderId}`));
  } catch (e) {
    $("#order").innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
  }
}

// ---------- Arranque ----------
const PAGES = {
  catalog: initCatalog, product: initProduct, login: initLogin, register: initRegister, cart: initCart,
  checkout: initCheckout, payment: initPayment, orders: initOrders, order: initOrder,
};

document.addEventListener("DOMContentLoaded", () => {
  renderHeader();
  const init = PAGES[document.body.dataset.page];
  if (init) Promise.resolve().then(init).catch((e) => flash(e.message, "error"));
});
