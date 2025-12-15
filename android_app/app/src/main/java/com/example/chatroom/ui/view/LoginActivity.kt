package com.example.chatroom.ui.view

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.example.chatroom.R
import com.example.chatroom.ui.viewmodel.LoginViewModel

class LoginActivity : AppCompatActivity() {

    private lateinit var viewModel: LoginViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val sessionManager = SessionManager(this)
        viewModel = ViewModelProvider(this, LoginViewModelFactory(sessionManager)).get(LoginViewModel::class.java)

        val usernameInput = findViewById<EditText>(R.id.usernameInput)
        val passwordInput = findViewById<EditText>(R.id.passwordInput)
        val loginButton = findViewById<Button>(R.id.loginButton)

        loginButton.setOnClickListener {
            val username = usernameInput.text.toString()
            val password = passwordInput.text.toString()
            if (username.isNotEmpty() && password.isNotEmpty()) {
                viewModel.login(username, password)
            } else {
                Toast.makeText(this, "Please enter username and password", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loginResult.observe(this) { success ->
            if (success) {
                startActivity(Intent(this, ChatActivity::class.java))
                finish()
            } else {
                Toast.makeText(this, "Login failed", Toast.LENGTH_SHORT).show()
            }
        }
    }
}