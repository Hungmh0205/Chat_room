package com.example.chatroom.ui.view

import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.ListView
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.chatroom.R
import com.example.chatroom.ui.adapter.MessageAdapter
import com.example.chatroom.ui.viewmodel.ChatViewModel
import com.google.android.material.navigation.NavigationView

class ChatActivity : AppCompatActivity() {

    private lateinit var viewModel: ChatViewModel
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var messageList: RecyclerView
    private lateinit var messageInput: EditText
    private val messages = mutableListOf<String>()
    private lateinit var adapter: MessageAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        val sessionManager = SessionManager(this)
        viewModel = ViewModelProvider(this, ChatViewModelFactory(sessionManager)).get(ChatViewModel::class.java)

        drawerLayout = findViewById(R.id.drawerLayout)
        messageList = findViewById(R.id.messageList)
        messageInput = findViewById(R.id.messageInput)
        val sendButton = findViewById<android.widget.Button>(R.id.sendButton)
        val toolbar = findViewById<androidx.appcompat.widget.Toolbar>(R.id.toolbar)

        setSupportActionBar(toolbar)
        val toggle = ActionBarDrawerToggle(this, drawerLayout, toolbar, R.string.open, R.string.close)
        drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        adapter = MessageAdapter(messages)
        messageList.layoutManager = LinearLayoutManager(this)
        messageList.adapter = adapter

        viewModel.connectSocket()
        viewModel.messages.observe(this) { msg ->
            messages.add(msg)
            adapter.notifyDataSetChanged()
            messageList.scrollToPosition(messages.size - 1)
        }

        sendButton.setOnClickListener {
            val msg = messageInput.text.toString()
            if (msg.isNotEmpty()) {
                viewModel.sendMessage(msg)
                messageInput.text.clear()
            }
        }

        val navView = findViewById<NavigationView>(R.id.navView)
        navView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_online_users -> {
                    viewModel.loadOnlineUsers()
                    viewModel.onlineUsers.observe(this) { users ->
                        android.widget.Toast.makeText(this, "Online: ${users.joinToString()}", android.widget.Toast.LENGTH_SHORT).show()
                    }
                }
                R.id.nav_settings -> {
                    android.widget.Toast.makeText(this, "Settings coming soon", android.widget.Toast.LENGTH_SHORT).show()
                }
                R.id.nav_logout -> {
                    viewModel.logout()
                    finish()
                }
            }
            drawerLayout.closeDrawer(GravityCompat.START)
            true
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        viewModel.disconnectSocket()
    }
}