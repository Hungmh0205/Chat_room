package com.example.chatroom.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.example.chatroom.data.api.RetrofitClient
import com.example.chatroom.data.api.SocketService
import com.example.chatroom.data.repository.ChatRepository
import com.example.chatroom.utils.Constants

class ChatViewModel : ViewModel() {
    private val repository = ChatRepository(RetrofitClient.apiService, SocketService(Constants.SERVER_URL))
    private val _messages = MutableLiveData<String>()
    val messages: LiveData<String> get() = _messages

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

    fun disconnectSocket() {
        repository.disconnectSocket()
    }

    fun logout() {
        // Clear session, etc.
    }
}