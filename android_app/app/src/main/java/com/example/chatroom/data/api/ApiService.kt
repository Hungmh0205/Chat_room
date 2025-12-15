package com.example.chatroom.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

// API Service for HTTP requests (login, etc.)
interface ApiService {
    @POST("login")
    suspend fun login(@Body request: LoginRequest): retrofit2.Response<LoginResponse>

    @POST("register")
    suspend fun register(@Body request: RegisterRequest): retrofit2.Response<ApiResponse>
}

data class LoginRequest(val username: String, val password: String)
data class LoginResponse(val status: String, val message: String)
data class RegisterRequest(val username: String, val password: String)
data class ApiResponse(val status: String, val message: String)

object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:5000/"  // Adjust for your server

    private val logging = HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY)

    private val client = OkHttpClient.Builder()
        .addInterceptor(logging)
        .build()

    val apiService: ApiService = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(ApiService::class.java)
}