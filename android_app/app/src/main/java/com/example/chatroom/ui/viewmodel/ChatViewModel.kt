package com.example.chatroom.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.example.chatroom.data.api.RetrofitClient
import com.example.chatroom.data.api.SocketService
import com.example.chatroom.data.repository.ChatRepository
import com.example.chatroom.utils.SessionManager

class ChatViewModel(private val sessionManager: SessionManager) : ViewModel() {
    private val _messages = MutableLiveData<String>()
    val messages: LiveData<String> get() = _messages

    private val _onlineUsers = MutableLiveData<List<String>>()
    val onlineUsers: LiveData<List<String>> get() = _onlineUsers

    private lateinit var repository: ChatRepository

    init {
        val serverUrl = sessionManager.getServerUrl() ?: return
        val apiService = RetrofitClient.getApiService(serverUrl)
        repository = ChatRepository(apiService, SocketService(serverUrl))
    }

    fun connectSocket() {
        repository.connectSocket(
            onConnected = { /* Handle connected */ },
            onMessage = { msg -> _messages.value = msg },
            onDisconnected = { /* Handle disconnected */ }
        )
    }

    fun sendMessage(msg: String) {
        repository.sendMessage(msg)
    }

    fun loadOnlineUsers() {
        viewModelScope.launch {
            val response = repository.getOnlineUsers()
            if (response.isSuccessful) {
                _onlineUsers.value = response.body()?.users ?: emptyList()
            }
        }
    }

    fun disconnectSocket() {
        repository.disconnectSocket()
    }

    fun logout() {
        sessionManager.clearSession()
    }
}