package com.example.chatroom.utils

object Constants {
    // Không hardcode, dùng từ SessionManager
}

class SessionManager(private val context: android.content.Context) {
    private val prefs = context.getSharedPreferences("chat_prefs", android.content.Context.MODE_PRIVATE)

    fun saveUsername(username: String) {
        prefs.edit().putString("username", username).apply()
    }

    fun getUsername(): String? {
        return prefs.getString("username", null)
    }

    fun saveServerUrl(url: String) {
        prefs.edit().putString("server_url", url).apply()
    }

    fun getServerUrl(): String? {
        return prefs.getString("server_url", null)
    }

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}