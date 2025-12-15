package com.example.chatroom.data.api

import io.socket.client.IO
import io.socket.client.Socket

class SocketService(private val serverUrl: String) {
    private lateinit var socket: Socket

    fun connect(onConnected: () -> Unit, onMessage: (String) -> Unit, onDisconnected: () -> Unit) {
        try {
            socket = IO.socket(serverUrl)
            socket.connect()

            socket.on(Socket.EVENT_CONNECT) {
                onConnected()
            }

            socket.on(Socket.EVENT_DISCONNECT) {
                onDisconnected()
            }

            socket.on("message") { args ->
                val data = args[0] as String
                onMessage(data)
            }

            // Add private_message if needed
            socket.on("private_message") { args ->
                val data = args[0] as JSONObject
                val message = data.getString("message")
                onMessage("Private: $message")
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun sendMessage(msg: String) {
        socket.emit("message", msg)
    }

    fun sendPrivateMessage(toUser: String, message: String) {
        val data = JSONObject().apply {
            put("to_user", toUser)
            put("message", message)
        }
        socket.emit("private_message", data)
    }

    fun disconnect() {
        socket.disconnect()
    }
}