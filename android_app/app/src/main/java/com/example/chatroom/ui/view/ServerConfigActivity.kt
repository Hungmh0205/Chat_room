package com.example.chatroom.ui.view

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.chatroom.R
import com.example.chatroom.utils.SessionManager

class ServerConfigActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_config)

        sessionManager = SessionManager(this)

        val urlInput = findViewById<EditText>(R.id.urlInput)
        val connectButton = findViewById<Button>(R.id.connectButton)

        // Pre-fill nếu đã có
        urlInput.setText(sessionManager.getServerUrl() ?: "")

        connectButton.setOnClickListener {
            val url = urlInput.text.toString().trim()
            if (url.isNotEmpty()) {
                sessionManager.saveServerUrl(url)
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
            } else {
                Toast.makeText(this, "Please enter server URL", Toast.LENGTH_SHORT).show()
            }
        }
    }
}