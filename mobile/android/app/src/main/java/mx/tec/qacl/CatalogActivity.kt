package mx.tec.qacl

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject

/** HU-03, HU-04, HU-06 · Catálogo, búsqueda y agregar al carrito. */
class CatalogActivity : Activity() {
    private val productos = mutableListOf<JSONObject>()
    private lateinit var adapter: ProductAdapter
    private lateinit var cartButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_catalog)
        findViewById<TextView>(R.id.catalog_user).text = Api.userName
        cartButton = findViewById(R.id.catalog_cart_button)
        adapter = ProductAdapter()
        findViewById<ListView>(R.id.catalog_list).adapter = adapter

        val search = findViewById<EditText>(R.id.catalog_search)
        findViewById<Button>(R.id.catalog_search_button).setOnClickListener { cargar(search.text.toString()) }
        cartButton.setOnClickListener { startActivity(Intent(this, CartActivity::class.java)) }
        findViewById<Button>(R.id.catalog_logout).setOnClickListener {
            Thread { Api.logout() }.start()
            finish()
        }
        cargar("")
    }

    override fun onResume() {
        super.onResume()
        actualizarContador()
    }

    private fun cargar(texto: String) {
        Thread {
            try {
                val data = Api.products(texto)
                val items = data.getJSONArray("items")
                runOnUiThread {
                    productos.clear()
                    for (i in 0 until items.length()) productos.add(items.getJSONObject(i))
                    adapter.notifyDataSetChanged()
                    val total = data.getInt("total")
                    findViewById<TextView>(R.id.catalog_info).text =
                        if (total == 0) "No encontramos productos para tu búsqueda" else "$total productos"
                }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(this, e.message, Toast.LENGTH_LONG).show() }
            }
        }.start()
    }

    private fun actualizarContador() {
        Thread {
            try {
                val count = Api.cart().getInt("item_count")
                runOnUiThread { cartButton.text = "Carrito ($count)" }
            } catch (_: Exception) { }
        }.start()
    }

    private fun agregar(producto: JSONObject) {
        Thread {
            try {
                val cart = Api.addToCart(producto.getInt("id"))
                runOnUiThread {
                    cartButton.text = "Carrito (${cart.getInt("item_count")})"
                    Toast.makeText(this, "Producto agregado al carrito", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(this, e.message, Toast.LENGTH_LONG).show() }
            }
        }.start()
    }

    inner class ProductAdapter : BaseAdapter() {
        override fun getCount() = productos.size
        override fun getItem(position: Int) = productos[position]
        override fun getItemId(position: Int) = productos[position].getLong("id")

        override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
            val view = convertView ?: LayoutInflater.from(parent.context).inflate(R.layout.item_product, parent, false)
            val p = productos[position]
            val disponible = p.getBoolean("available")
            view.findViewById<TextView>(R.id.item_name).text = p.getString("name")
            view.findViewById<TextView>(R.id.item_price).text = Api.money(p.getDouble("price"))
            view.findViewById<TextView>(R.id.item_status).text = if (disponible) "" else getString(R.string.out_of_stock)
            val add = view.findViewById<Button>(R.id.item_add)
            add.contentDescription = "Agregar ${p.getString("name")} al carrito"
            add.setOnClickListener { agregar(p) }
            return view
        }
    }
}
