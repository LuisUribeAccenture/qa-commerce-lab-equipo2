package mx.tec.qacl

import android.app.Activity
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject

/** HU-07, HU-09 · Carrito: cantidades y totales (calculados por la API). */
class CartActivity : Activity() {
    private val items = mutableListOf<JSONObject>()
    private lateinit var adapter: CartAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_cart)
        adapter = CartAdapter()
        findViewById<ListView>(R.id.cart_list).adapter = adapter
        findViewById<Button>(R.id.cart_back).setOnClickListener { finish() }
        ejecutar { Api.cart() }
    }

    private fun ejecutar(accion: () -> JSONObject) {
        Thread {
            try {
                val cart = accion()
                runOnUiThread { mostrar(cart) }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(this, e.message, Toast.LENGTH_LONG).show() }
            }
        }.start()
    }

    private fun mostrar(cart: JSONObject) {
        val lista = cart.getJSONArray("items")
        items.clear()
        for (i in 0 until lista.length()) items.add(lista.getJSONObject(i))
        adapter.notifyDataSetChanged()
        findViewById<TextView>(R.id.cart_empty).visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
        val envio = cart.getDouble("shipping")
        findViewById<TextView>(R.id.cart_subtotal).text = "Subtotal: ${Api.money(cart.getDouble("subtotal"))}"
        findViewById<TextView>(R.id.cart_discount).text = "Descuento: ${Api.money(cart.getDouble("discount"))}"
        findViewById<TextView>(R.id.cart_shipping).text = "Envío: " + if (envio == 0.0) "Gratis" else Api.money(envio)
        findViewById<TextView>(R.id.cart_total).text = "Total: ${Api.money(cart.getDouble("total"))}"
    }

    inner class CartAdapter : BaseAdapter() {
        override fun getCount() = items.size
        override fun getItem(position: Int) = items[position]
        override fun getItemId(position: Int) = items[position].getLong("product_id")

        override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
            val view = convertView ?: LayoutInflater.from(parent.context).inflate(R.layout.item_cart, parent, false)
            val item = items[position]
            val id = item.getInt("product_id")
            val qty = item.getInt("quantity")
            val nombre = item.getString("name")
            view.findViewById<TextView>(R.id.cart_item_name).text = nombre
            view.findViewById<TextView>(R.id.cart_item_qty).text = qty.toString()
            view.findViewById<Button>(R.id.cart_item_plus).apply {
                contentDescription = "Aumentar $nombre"
                setOnClickListener { ejecutar { Api.setQuantity(id, qty + 1) } }
            }
            view.findViewById<Button>(R.id.cart_item_minus).apply {
                contentDescription = "Disminuir $nombre"
                setOnClickListener { ejecutar { Api.setQuantity(id, qty - 1) } }
            }
            return view
        }
    }
}
