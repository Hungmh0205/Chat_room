# DHT Chat Room

DHT Chat Room là một ứng dụng chat thời gian thực với nhiều tính năng như chat nhóm, chat riêng tư, quản lý tin nhắn, quản lý người dùng, và tích hợp video call. Ứng dụng được xây dựng bằng Flask, Flask-SocketIO, và PyQt6.

## **Tính năng**
- **Chat thời gian thực:** Gửi và nhận tin nhắn ngay lập tức.
- **Chat riêng tư:** Nhắn tin riêng tư giữa các người dùng.
- **Quản lý tin nhắn:** Lưu trữ và quản lý lịch sử tin nhắn.
- **Quản lý người dùng:** Đăng ký, đăng nhập, và quản lý tài khoản.
- **Video call:** Tích hợp video call với ZegoUIKitPrebuilt.
- **Tải lên file:** Hỗ trợ tải lên và chia sẻ file (hình ảnh, video, âm thanh).
- **Nhạc nền:** Phát nhạc nền từ file tải lên hoặc YouTube

---

## **Yêu cầu hệ thống**
- Python 3.8 trở lên
- Các thư viện Python:
  - Flask
  - Flask-SocketIO
  - Flask-Bcrypt
  - PyQt6
  - pyngrok
  - werkzeug

---

## **Hướng dẫn cài đặt**
1. **Clone dự án:**
   ```bash
   git clone <repository-url>
   cd Chat_room

2. **Cài thư viện cần thiết**
- Chạy file install.bat
  hoặc 
   ```bash
   pip install Flask Flask-SocketIO Flask-Bcrypt pyngrok werkzeug

3. **Khởi tạo cơ sở dữ liệu**
- Cơ sở dữ liệu SQLite sẽ được tự động tạo khi chạy ứng dụng lần đầu.

4. **Chạy ứng dụng**
   ```bash
   python server.py

Hướng dẫn sử dụng
1. Đăng ký và đăng nhập
- Truy cập trang /register để tạo tài khoản.
- Đăng nhập tại trang /login.
2. Chat nhóm
- Sau khi đăng nhập, bạn sẽ được chuyển đến trang chat nhóm.
3. Chat riêng tư
- Nhấp vào tên người dùng trong danh sách online để bắt đầu chat riêng tư.
4. Video call
- Truy cập /dashboard để tạo hoặc tham gia cuộc gọi video.
5. Quản lý tin nhắn và người dùng
- Chạy manager.py để mở giao diện quản lý tin nhắn và người dùng.

Đóng góp
Nếu bạn muốn đóng góp cho dự án, hãy tạo một pull request hoặc mở issue trên GitHub.
