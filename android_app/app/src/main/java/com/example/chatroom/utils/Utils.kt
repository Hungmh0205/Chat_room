package com.example.chatroom.utils

object Constants {
    const val SERVER_URL = "http://10.0.2.2:5000"  // Adjust for your server
}

class SessionManager(private val context: android.content.Context) {
    private val prefs = context.getSharedPreferences("chat_prefs", android.content.Context.MODE_PRIVATE)

    fun saveUsername(username: String) {
        prefs.edit().putString("username", username).apply()
    }

    fun getUsername(): String? {
        return prefs.getString("username", null)
    }

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}