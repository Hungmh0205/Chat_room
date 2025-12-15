package com.example.chatroom

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.chatroom.ui.view.ChatActivity
import com.example.chatroom.ui.view.LoginActivity
import com.example.chatroom.utils.SessionManager

class MainActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sessionManager = SessionManager(this)

        if (sessionManager.getUsername() != null) {
            // Already logged in, go to chat
            startActivity(Intent(this, ChatActivity::class.java))
        } else {
            // Go to login
            startActivity(Intent(this, LoginActivity::class.java))
        }
        finish()
    }
}