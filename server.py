import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, send, emit
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename


# Khởi tạo Flask & SocketIO
app = Flask(__name__)
app.secret_key = "secret_key"
socketio = SocketIO(app, cors_allowed_origins="*")
bcrypt = Bcrypt(app)

# Cấu hình thư mục upload file
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = None  # Cho phép tất cả các loại file
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Kiểm tra định dạng file hợp lệ
def allowed_file(filename):
    return True

# Khởi tạo database SQLite
def init_db():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Danh sách người dùng online
users_online = set()

# Trang chủ
@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")
    return render_template("chat.html", username=session["username"])

# Đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        try:
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": "Đăng ký thành công!"})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Tên người dùng đã tồn tại!"})
    return render_template("register.html")

# Đăng nhập
@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user[0], password):
            session["username"] = username
            return redirect("/")
        else:
            return "Sai tài khoản hoặc mật khẩu!"
    return render_template("login.html")

# Đăng xuất
@app.route("/logout")
def logout():
    username = session.get("username")
    if username in users_online:
        users_online.remove(username)
        emit("update_users", list(users_online), broadcast=True)
    session.pop("username", None)
    return redirect("/login")

#tải file lên
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Không có file!"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Chưa chọn file!"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        file_url = f"/static/uploads/{filename}"
        username = session.get("username", "Ẩn danh")

        # Xác định loại file để hiển thị phù hợp
        if filename.lower().endswith(("png", "jpg", "jpeg", "gif")):
            message_content = f"{username} đã gửi ảnh: <br><a href='{file_url}' target='_blank'><img src='{file_url}' width='200px' onclick='openImage(this)'></a>"
        elif filename.lower().endswith(("mp4", "webm", "ogg")):
            message_content = f"{username} đã gửi video: <br><video width='320' height='240' controls><source src='{file_url}' type='video/mp4'>Trình duyệt không hỗ trợ video.</video>"
        elif filename.lower().endswith(("mp3", "wav", "ogg")):
            message_content = f"{username} đã gửi âm thanh: <br><audio controls><source src='{file_url}' type='audio/mpeg'>Trình duyệt không hỗ trợ âm thanh.</audio>"
        else:
            message_content = f"{username} đã gửi file: <a href='{file_url}' target='_blank'>{filename}</a>"

        # Lưu vào database
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message_content))
        conn.commit()
        conn.close()

        # Gửi tin nhắn đến mọi người
        socketio.emit("message", message_content)
        return jsonify({"status": "success", "message": "Tải file thành công!", "url": file_url})

    return jsonify({"status": "error", "message": "Định dạng file không hợp lệ!"})

# Lịch sử chat
@app.route("/history")
def chat_history():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM messages ORDER BY timestamp ASC")
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)

# Gửi tin nhắn real-time
@socketio.on("message")
def handle_message(msg):
    if "username" not in session:
        return  # Chặn tin nhắn từ user chưa đăng nhập
    
    username = session["username"]
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, msg))
    conn.commit()
    conn.close()
    
    send(f"{username}: {msg}", broadcast=True)


# Xử lý người dùng online
@socketio.on("connect")
def handle_connect():
    username = session.get("username", "Ẩn danh")
    if username not in users_online:
        users_online.add(username)
    emit("update_users", list(users_online), broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    username = session.get("username", "Ẩn danh")
    if username in users_online:
        users_online.remove(username)
    emit("update_users", list(users_online), broadcast=True)

# Khởi động server với ngrok
if __name__ == "__main__":
    from pyngrok import ngrok
    public_url = ngrok.connect(5000).public_url
    print(f"🔥 Server đang chạy tại: {public_url}")
    socketio.run(app, host="0.0.0.0", port=5000)
    
