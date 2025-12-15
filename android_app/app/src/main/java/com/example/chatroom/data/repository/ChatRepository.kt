package com.example.chatroom.data.repository

import com.example.chatroom.data.api.ApiService
import com.example.chatroom.data.api.SocketService
import com.example.chatroom.data.model.Message

class ChatRepository(private val apiService: ApiService, private val socketService: SocketService) {

    fun connectSocket(onConnected: () -> Unit, onMessage: (String) -> Unit, onDisconnected: () -> Unit) {
        socketService.connect(onConnected, onMessage, onDisconnected)
    }

    fun sendMessage(msg: String) {
        socketService.sendMessage(msg)
    }

    fun sendPrivateMessage(toUser: String, message: String) {
        socketService.sendPrivateMessage(toUser, message)
    }

    fun disconnectSocket() {
        socketService.disconnect()
    }

    suspend fun login(username: String, password: String): Result<String> {
        return try {
            val response = apiService.login(com.example.chatroom.data.api.LoginRequest(username, password))
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Success")
            } else {
                Result.failure(Exception("Login failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Add more methods for history, etc., if needed
}