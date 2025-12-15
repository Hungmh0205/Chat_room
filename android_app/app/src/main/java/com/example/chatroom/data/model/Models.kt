package com.example.chatroom.data.model

data class User(val username: String)

data class Message(val username: String, val message: String, val timestamp: String)

data class PrivateMessage(val fromUser: String, val toUser: String, val message: String, val timestamp: String)