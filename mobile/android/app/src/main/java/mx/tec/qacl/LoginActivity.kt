package mx.tec.qacl

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView

/** HU-02 · Inicio de sesión. */
class LoginActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        val server = findViewById<EditText>(R.id.login_server)
        val email = findViewById<EditText>(R.id.login_email)
        val password = findViewById<EditText>(R.id.login_password)
        val error = findViewById<TextView>(R.id.login_error)
        val button = findViewById<Button>(R.id.login_button)

        button.setOnClickListener {
            error.text = ""
            button.isEnabled = false
            Api.baseUrl = server.text.toString()
            val correo = email.text.toString().trim()
            val clave = password.text.toString()
            Thread {
                try {
                    Api.login(correo, clave)
                    runOnUiThread {
                        startActivity(Intent(this, CatalogActivity::class.java))
                        button.isEnabled = true
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        error.text = if (e is Api.ApiError) e.message else "No se pudo conectar con el servidor"
                        button.isEnabled = true
                    }
                }
            }.start()
        }
    }
}
