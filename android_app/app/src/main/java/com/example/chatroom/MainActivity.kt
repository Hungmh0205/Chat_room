package com.example.chatroom

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.chatroom.ui.view.ChatActivity
import com.example.chatroom.ui.view.ServerConfigActivity
import com.example.chatroom.utils.SessionManager

class MainActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sessionManager = SessionManager(this)

        if (sessionManager.getServerUrl() == null) {
            // Chưa có URL, đi config server
            startActivity(Intent(this, ServerConfigActivity::class.java))
        } else if (sessionManager.getUsername() != null) {
            // Đã login, đi chat
            startActivity(Intent(this, ChatActivity::class.java))
        } else {
            // Có URL nhưng chưa login, đi login
            startActivity(Intent(this, LoginActivity::class.java))
        }
        finish()
    }
}