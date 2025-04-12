import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QTabWidget, QHBoxLayout, QInputDialog
)
from PyQt6.QtGui import QFont
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class ChatManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Manager")
        self.setGeometry(100, 100, 900, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.init_messages_tab()
        self.init_users_tab()
        self.init_private_messages_tab()
    
    def init_messages_tab(self):
        self.messages_tab = QWidget()
        self.tabs.addTab(self.messages_tab, "Quản lý Tin nhắn")
        layout = QVBoxLayout()
        self.messages_tab.setLayout(layout)
        
        self.load_messages_button = QPushButton("📜 Tải lịch sử tin nhắn")
        self.load_messages_button.clicked.connect(self.load_messages)
        layout.addWidget(self.load_messages_button)
        
        self.message_table = QTableWidget()
        layout.addWidget(self.message_table)
        
        button_layout = QHBoxLayout()
        
        self.delete_message_button = QPushButton("🗑️ Xóa tin nhắn được chọn")
        self.delete_message_button.clicked.connect(self.delete_message)
        button_layout.addWidget(self.delete_message_button)
        
        self.delete_all_messages_button = QPushButton("🧹 Xóa toàn bộ tin nhắn")
        self.delete_all_messages_button.clicked.connect(self.delete_all_messages)
        button_layout.addWidget(self.delete_all_messages_button)
        
        layout.addLayout(button_layout)
    
    def init_users_tab(self):
        self.users_tab = QWidget()
        self.tabs.addTab(self.users_tab, "Quản lý Người dùng")
        layout = QVBoxLayout()
        self.users_tab.setLayout(layout)
        
        self.load_users_button = QPushButton("👥 Tải danh sách tài khoản")
        self.load_users_button.clicked.connect(self.load_users)
        layout.addWidget(self.load_users_button)
        
        self.user_table = QTableWidget()
        layout.addWidget(self.user_table)
        
        button_layout = QHBoxLayout()
        
        self.delete_user_button = QPushButton("❌ Xóa tài khoản được chọn")
        self.delete_user_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.delete_user_button)
        
        self.change_password_button = QPushButton("🔑 Đổi mật khẩu tài khoản")
        self.change_password_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.change_password_button)
        
        layout.addLayout(button_layout)
        
        self.search_user_input = QLineEdit()
        self.search_user_input.setPlaceholderText("🔍 Nhập tên người dùng...")
        layout.addWidget(self.search_user_input)
        
        self.search_user_button = QPushButton("Tìm kiếm")
        self.search_user_button.clicked.connect(self.search_user)
        layout.addWidget(self.search_user_button)
    
    def init_private_messages_tab(self):
        self.private_messages_tab = QWidget()
        self.tabs.addTab(self.private_messages_tab, "Quản lý Tin nhắn Riêng")
        layout = QVBoxLayout()
        self.private_messages_tab.setLayout(layout)
        
        self.load_private_messages_button = QPushButton("📜 Tải lịch sử tin nhắn riêng")
        self.load_private_messages_button.clicked.connect(self.load_private_messages)
        layout.addWidget(self.load_private_messages_button)
        
        self.private_message_table = QTableWidget()
        layout.addWidget(self.private_message_table)
        
        button_layout = QHBoxLayout()
        
        self.delete_private_message_button = QPushButton("🗑️ Xóa tin nhắn riêng được chọn")
        self.delete_private_message_button.clicked.connect(self.delete_private_message)
        button_layout.addWidget(self.delete_private_message_button)
        
        self.delete_all_private_messages_button = QPushButton("🧹 Xóa toàn bộ tin nhắn riêng")
        self.delete_all_private_messages_button.clicked.connect(self.delete_all_private_messages)
        button_layout.addWidget(self.delete_all_private_messages_button)
        
        layout.addLayout(button_layout)
    
    def load_messages(self):
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, message, timestamp FROM messages ORDER BY timestamp DESC")
        messages = cursor.fetchall()
        conn.close()
        
        self.message_table.setRowCount(len(messages))
        self.message_table.setColumnCount(4)
        self.message_table.setHorizontalHeaderLabels(["ID", "Người gửi", "Tin nhắn", "Thời gian"])
        
        for row_idx, row_data in enumerate(messages):
            for col_idx, col_data in enumerate(row_data):
                self.message_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
    
    def delete_message(self):
        selected_row = self.message_table.currentRow()
        if selected_row >= 0:
            msg_id = self.message_table.item(selected_row, 0).text()
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE id=?", (msg_id,))
            conn.commit()
            conn.close()
            self.load_messages()
            QMessageBox.information(self, "Thành công", "Đã xóa tin nhắn!")
            
    def delete_all_messages(self):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ tin nhắn?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            conn.commit()
            conn.close()
            self.load_messages()
            QMessageBox.information(self, "Thành công", "Đã xóa toàn bộ tin nhắn!")
    
    def load_users(self):
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        conn.close()
        
        self.user_table.setRowCount(len(users))
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên đăng nhập"])
        
        for row_idx, row_data in enumerate(users):
            for col_idx, col_data in enumerate(row_data):
                self.user_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
    
    def delete_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row >= 0:
            user_id = self.user_table.item(selected_row, 0).text()
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            self.load_users()
            QMessageBox.information(self, "Thành công", "Đã xóa tài khoản!")
    
    def search_user(self):
        search_text = self.search_user_input.text()
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username LIKE ?", (f"%{search_text}%",))
        users = cursor.fetchall()
        conn.close()
        
        self.user_table.setRowCount(len(users))
        for row_idx, row_data in enumerate(users):
            for col_idx, col_data in enumerate(row_data):
                self.user_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
    
    def change_password(self):
        selected_row = self.user_table.currentRow()
        if selected_row >= 0:
            user_id = self.user_table.item(selected_row, 0).text()
            new_password, ok = QInputDialog.getText(self, "Đổi mật khẩu", "Nhập mật khẩu mới:")
            if ok and new_password:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                conn = sqlite3.connect("chat.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu!")
    
    def load_private_messages(self):
        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, from_user, to_user, message, timestamp 
            FROM private_messages 
            ORDER BY timestamp DESC
        """)
        private_messages = cursor.fetchall()
        conn.close()
        
        self.private_message_table.setRowCount(len(private_messages))
        self.private_message_table.setColumnCount(5)
        self.private_message_table.setHorizontalHeaderLabels(["ID", "Người gửi", "Người nhận", "Tin nhắn", "Thời gian"])
        
        for row_idx, row_data in enumerate(private_messages):
            for col_idx, col_data in enumerate(row_data):
                self.private_message_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def delete_private_message(self):
        selected_row = self.private_message_table.currentRow()
        if selected_row >= 0:
            msg_id = self.private_message_table.item(selected_row, 0).text()
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM private_messages WHERE id=?", (msg_id,))
            conn.commit()
            conn.close()
            self.load_private_messages()
            QMessageBox.information(self, "Thành công", "Đã xóa tin nhắn riêng!")

    def delete_all_private_messages(self):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ tin nhắn riêng?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("chat.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM private_messages")
            conn.commit()
            conn.close()
            self.load_private_messages()
            QMessageBox.information(self, "Thành công", "Đã xóa toàn bộ tin nhắn riêng!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatManager()
    window.show()
    sys.exit(app.exec())
