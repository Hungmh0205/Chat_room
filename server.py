import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, send, emit
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename


# Khởi tạo Flask & SocketIO
app = Flask(__name__)
app.secret_key = "secret_key"
socketio = SocketIO(app, 
    cors_allowed_origins="*",
    ping_timeout=10,
    ping_interval=5,
    reconnection=True,
    reconnection_attempts=5,
    logger=True,
    engineio_logger=True
)
bcrypt = Bcrypt(app)

# Cấu hình thư mục upload file
UPLOAD_FOLDER = "static/uploads"
MUSIC_FOLDER = "static/music"  # Thêm thư mục cho nhạc
ALLOWED_EXTENSIONS = None  # Cho phép tất cả các loại file
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MUSIC_FOLDER, exist_ok=True)  # Tạo thư mục music nếu chưa có
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MUSIC_FOLDER"] = MUSIC_FOLDER

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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user TEXT,
        to_user TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()


# Danh sách người dùng online
users_online = set()

# Lưu trữ thông tin socket của người dùng
user_sockets = {}



# Trang chủ
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect("/login")  # Nếu chưa đăng nhập thì quay về trang đăng nhập
    return render_template("chat.html")

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
            print(f"🔥 Session khi login: {session}")  # In ra để debug
            return redirect("/chat")
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
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", first_name=session["username"])  # Chỉnh lại biến


@app.route("/meeting")
def meeting():
    return render_template("meeting.html", username=session["username"])


@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/meeting?roomID={room_id}")

    return render_template("join.html")


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
        return

    username = session["username"]
    
    # Lưu tin nhắn vào database
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, msg))
    conn.commit()
    conn.close()
    
    # Gửi tin nhắn đến tất cả người dùng
    send(f"{username}: {msg}", broadcast=True)


# Xử lý người dùng online
@socketio.on("connect")
def handle_connect():
    username = session.get("username", "Ẩn danh")
    if username not in users_online:
        users_online.add(username)
    user_sockets[username] = request.sid
    emit("update_users", list(users_online), broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    try:
        username = session.get("username", "Ẩn danh")
        if username in users_online:
            users_online.remove(username)
        if username in user_sockets:
            del user_sockets[username]
        emit("update_users", list(users_online), broadcast=True)
    except Exception as e:
        print(f"Error in disconnect handler: {str(e)}")

@app.route("/upload_music", methods=["POST"])
def upload_music():
    if "music" not in request.files:
        return jsonify({"status": "error", "message": "Không có file nhạc!"})

    file = request.files["music"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Chưa chọn file nhạc!"})

    if file and file.filename.lower().endswith(('mp3', 'wav', 'ogg')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["MUSIC_FOLDER"], filename)
        file.save(filepath)
        return jsonify({
            "status": "success", 
            "message": "Tải nhạc thành công!",
            "url": f"/static/music/{filename}"
        })

    return jsonify({"status": "error", "message": "Chỉ chấp nhận file nhạc (MP3, WAV, OGG)!"})

@app.route("/get_music_list")
def get_music_list():
    music_files = []
    for file in os.listdir(app.config["MUSIC_FOLDER"]):
        if file.lower().endswith(('mp3', 'wav', 'ogg')):
            music_files.append({
                "name": file,
                "url": f"/static/music/{file}"
            })
    return jsonify(music_files)

# Xử lý lỗi kết nối
@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO error: {str(e)}")
    return False

@socketio.on_error
def error_handler(e):
    print(f"SocketIO event error: {str(e)}")
    return False

# Xử lý tin nhắn riêng tư
@socketio.on("private_message")
def handle_private_message(data):
    if "username" not in session:
        return
    
    from_user = session["username"]
    to_user = data.get("to_user")
    message = data.get("message")
    
    if not to_user or not message:
        return
    
    # Lưu tin nhắn vào database
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO private_messages (from_user, to_user, message) 
        VALUES (?, ?, ?)
    """, (from_user, to_user, message))
    conn.commit()
    conn.close()
    
    # Gửi tin nhắn đến người nhận nếu họ online
    if to_user in user_sockets:
        emit("private_message", {
            "from": from_user,
            "message": message
        }, to=user_sockets[to_user])

    
    # Gửi tin nhắn về cho người gửi
    emit("private_message", {
        "from": from_user,
        "message": message
    }, room=request.sid)

# Upload file riêng tư
@app.route("/upload_private_file", methods=["POST"])
def upload_private_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Không có file!"})
    
    file = request.files["file"]
    to_user = request.form.get("to_user")
    
    if file.filename == "":
        return jsonify({"status": "error", "message": "Chưa chọn file!"})
    
    if not to_user:
        return jsonify({"status": "error", "message": "Thiếu thông tin người nhận!"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        file_url = f"/static/uploads/{filename}"
        from_user = session.get("username", "Ẩn danh")
        
        # Xác định loại file để hiển thị phù hợp
        if filename.lower().endswith(("png", "jpg", "jpeg", "gif")):
            message_content = f"{from_user} đã gửi ảnh: <br><a href='{file_url}' target='_blank'><img src='{file_url}' width='200px'></a>"
        elif filename.lower().endswith(("mp4", "webm", "ogg")):
            message_content = f"{from_user} đã gửi video: <br><video width='320' height='240' controls><source src='{file_url}' type='video/mp4'>Trình duyệt không hỗ trợ video.</video>"
        elif filename.lower().endswith(("mp3", "wav", "ogg")):
            message_content = f"{from_user} đã gửi âm thanh: <br><audio controls><source src='{file_url}' type='audio/mpeg'>Trình duyệt không hỗ trợ âm thanh.</audio>"
        else:
            message_content = f"{from_user} đã gửi file: <a href='{file_url}' target='_blank'>{filename}</a>"
        
        # Lưu vào database
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO private_messages (from_user, to_user, message) 
            VALUES (?, ?, ?)
        """, (from_user, to_user, message_content))
        conn.commit()
        conn.close()
        
        # Gửi tin nhắn đến người nhận nếu họ online
        if to_user in user_sockets:
            socketio.emit("private_message", {
                "from": from_user,
                "message": message_content
            }, room=user_sockets[to_user])
        
        return jsonify({
            "status": "success", 
            "message": "Tải file thành công!", 
            "url": file_url
        })
    
    return jsonify({"status": "error", "message": "Định dạng file không hợp lệ!"})

@app.route("/private_history")
def private_chat_history():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    username = session["username"]
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    
    # Lấy tin nhắn riêng tư của người dùng (cả gửi và nhận)
    cursor.execute("""
        SELECT from_user, to_user, message, timestamp 
        FROM private_messages 
        WHERE from_user = ? OR to_user = ?
        ORDER BY timestamp DESC
    """, (username, username))
    
    messages = cursor.fetchall()
    conn.close()
    
    # Chuyển đổi kết quả thành danh sách dict
    history = []
    for msg in messages:
        history.append({
            "from_user": msg[0],
            "to_user": msg[1],
            "message": msg[2],
            "timestamp": msg[3]
        })
    
    return jsonify(history)

# Thêm route để lấy tên người dùng hiện tại
@app.route("/get_username")
def get_username():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"username": session["username"]})

# Khởi động server với ngrok
if __name__ == "__main__":
    try:
        from pyngrok import ngrok
        public_url = ngrok.connect(5000).public_url
        print(f"🔥 Server đang chạy tại: {public_url}")
        socketio.run(app, 
            host="0.0.0.0", 
            port=5000,
            debug=True,
            use_reloader=False,
            log_output=True
        )
    except Exception as e:
        print(f"Server error: {str(e)}")
    