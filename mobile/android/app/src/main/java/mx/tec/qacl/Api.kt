package mx.tec.qacl

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.NumberFormat
import java.util.Locale

/** Cliente mínimo de la API REST de QA Commerce Lab (mismas reglas que la web). */
object Api {
    var baseUrl = "http://10.0.2.2:8000"
    var token: String? = null
    var userName: String = ""

    class ApiError(val status: Int, message: String) : Exception(message)

    private fun request(method: String, path: String, body: JSONObject? = null): JSONObject {
        val conn = URL(baseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection
        conn.requestMethod = method
        conn.connectTimeout = 8000
        conn.readTimeout = 8000
        conn.setRequestProperty("Content-Type", "application/json")
        token?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
        if (body != null) {
            conn.doOutput = true
            conn.outputStream.use { it.write(body.toString().toByteArray()) }
        }
        val status = conn.responseCode
        val stream = if (status in 200..299) conn.inputStream else conn.errorStream
        val text = stream?.bufferedReader()?.use { it.readText() } ?: "{}"
        val json = if (text.isBlank()) JSONObject() else JSONObject(text)
        if (status !in 200..299) throw ApiError(status, json.optString("detail", "Error $status"))
        return json
    }

    fun login(email: String, password: String) {
        val res = request("POST", "/api/auth/login", JSONObject().put("email", email).put("password", password))
        token = res.getString("token")
        userName = res.getJSONObject("user").getString("name")
    }

    fun products(search: String): JSONObject {
        val q = if (search.isBlank()) "" else "?search=" + java.net.URLEncoder.encode(search, "UTF-8")
        return request("GET", "/api/products$q")
    }

    fun cart(): JSONObject = request("GET", "/api/cart")

    fun addToCart(productId: Int, quantity: Int = 1): JSONObject =
        request("POST", "/api/cart/items", JSONObject().put("product_id", productId).put("quantity", quantity))

    fun setQuantity(productId: Int, quantity: Int): JSONObject =
        request("PATCH", "/api/cart/items/$productId", JSONObject().put("quantity", quantity))

    fun logout() {
        try { request("POST", "/api/auth/logout") } catch (_: Exception) { }
        token = null
    }

    private val formato = NumberFormat.getCurrencyInstance(Locale.US)
    fun money(value: Double): String = formato.format(value)
}
