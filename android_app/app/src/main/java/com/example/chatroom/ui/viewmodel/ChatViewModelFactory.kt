package com.example.chatroom.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.chatroom.utils.SessionManager

class ChatViewModelFactory(private val sessionManager: SessionManager) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ChatViewModel::class.java)) {
            return ChatViewModel(sessionManager) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}