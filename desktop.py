from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGraphicsDropShadowEffect, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import requests
import sys
from datetime import datetime

class RobloxInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Roblox Account Info Retriever")
        self.setStyleSheet("background-color: #1E1E1E;")

        label_font = QFont("JetBrains Mono", 16, QFont.Weight.Bold)
        input_font = QFont("JetBrains Mono", 14)
        result_font = QFont("JetBrains Mono", 14)

        main_layout = QVBoxLayout()

        title_label = QLabel("Roblox Account Info Retriever")
        title_label.setFont(label_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setFont(input_font)
        self.username_input.setPlaceholderText("Enter Roblox Username")
        self.username_input.setStyleSheet("padding: 8px; margin: 10px; border: 1px solid #aaa; border-radius: 5px; color: white; background-color: #2D2D2D;")
        main_layout.addWidget(self.username_input)

        self.retrieve_button = QPushButton("Retrieve Info", self)
        self.retrieve_button.setFont(label_font)
        self.retrieve_button.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 10px;
            margin: 10px;
            border: none;
            border-radius: 5px;
        """)
        self.retrieve_button.clicked.connect(self.get_roblox_user_info)
        main_layout.addWidget(self.retrieve_button)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setFont(label_font)
        self.clear_button.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 10px;
            margin: 10px;
            border: none;
            border-radius: 5px;
        """)
        self.clear_button.clicked.connect(self.clear_info)
        main_layout.addWidget(self.clear_button)

        self.result_display = QTextEdit(self)
        self.result_display.setFont(result_font)
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("padding: 10px; margin: 10px; border: 1px solid #aaa; border-radius: 5px; background-color: #2D2D2D; color: white;")
        main_layout.addWidget(self.result_display)

        self.setLayout(main_layout)

    def get_roblox_user_info(self):
        username = self.username_input.text().strip()
        if not username:
            self.result_display.setText("Please enter a username.")
            return

        try:
            url = "https://users.roblox.com/v1/usernames/users"
            data = {"usernames": [username]}
            response = requests.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            if not result["data"]:
                self.result_display.setText("User not found.")
                return

            user_id = result["data"][0]["id"]
            user_info_url = f"https://users.roblox.com/v1/users/{user_id}"
            user_info_response = requests.get(user_info_url)
            user_info_response.raise_for_status()

            user_info = user_info_response.json()

            created_date = user_info.get("created")
            formatted_date = "N/A"
            years_on_platform = "N/A"
            if created_date:
                try:
                    created_datetime = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                    formatted_date = created_datetime.strftime("%d %b %Y")
                    years_on_platform = datetime.now().year - created_datetime.year
                except ValueError:
                    formatted_date = "Invalid date format"

            friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
            friends_response = requests.get(friends_url)
            friends_response.raise_for_status()
            friend_count = friends_response.json().get("count", "N/A")

            presence_url = "https://presence.roblox.com/v1/presence/users"
            presence_data = {"userIds": [user_id]}
            presence_response = requests.post(presence_url, json=presence_data)
            presence_response.raise_for_status()
            presence_info = presence_response.json()

            last_online = "N/A"
            is_online = "Offline"
            if presence_info["userPresences"]:
                presence = presence_info["userPresences"][0]
                is_online = "Online" if presence["userPresenceType"] == 2 else "Offline"
                last_online = presence.get("lastLocation", "N/A") if is_online == "Offline" else "Currently Online"

            info_text = (
                f"Username: {user_info.get('name')}\n"
                f"Display Name: {user_info.get('displayName')}\n"
                f"User ID: {user_info.get('id')}\n"
                f"Description: {user_info.get('description')}\n"
                f"Friend Count: {friend_count}\n"
                f"Years on Roblox: {years_on_platform} years\n"
                f"Created Date: {formatted_date}\n"
                f"Is Banned: {'Yes' if user_info.get('isBanned') else 'No'}\n"
                f"Online Status: {is_online}\n"
                f"Last Online: {last_online}"
            )
            self.result_display.setText(info_text)

        except requests.RequestException as e:
            self.result_display.setText(f"An error occurred: {str(e)}")

    def clear_info(self):
        self.username_input.clear()
        self.result_display.clear()

app = QApplication(sys.argv)
window = RobloxInfoApp()
window.showMaximized()
sys.exit(app.exec())