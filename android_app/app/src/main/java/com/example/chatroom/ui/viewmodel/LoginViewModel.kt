package com.example.chatroom.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chatroom.data.api.RetrofitClient
import com.example.chatroom.data.api.SocketService
import com.example.chatroom.data.repository.ChatRepository
import com.example.chatroom.utils.Constants
import com.example.chatroom.utils.SessionManager
import kotlinx.coroutines.launch

class LoginViewModel(private val sessionManager: SessionManager) : ViewModel() {
    private val _loginResult = MutableLiveData<Boolean>()
    val loginResult: LiveData<Boolean> get() = _loginResult

    fun login(username: String, password: String) {
        val serverUrl = sessionManager.getServerUrl() ?: return
        val apiService = RetrofitClient.getApiService(serverUrl)
        val repository = ChatRepository(apiService, SocketService(serverUrl))
        viewModelScope.launch {
            val result = repository.login(username, password)
            _loginResult.value = result.isSuccess
        }
    }
}