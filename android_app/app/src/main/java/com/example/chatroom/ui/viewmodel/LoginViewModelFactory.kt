package com.example.chatroom.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.chatroom.utils.SessionManager

class LoginViewModelFactory(private val sessionManager: SessionManager) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(LoginViewModel::class.java)) {
            return LoginViewModel(sessionManager) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}