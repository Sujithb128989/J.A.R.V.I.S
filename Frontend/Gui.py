import sys
import os
import requests
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtGui import QIcon, QPainter, QColor, QTextCharFormat, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer, QTime
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ASSISTANT_NAME = os.getenv("Assistantname", "J.A.R.V.I.S")
CURRENT_DIR = os.getcwd()
TEMP_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Files")
GRAPHICS_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Graphics")
DEFAULT_CITY = "New York" # You can change this to your city

# --- Helper Functions ---

def get_file_path(directory, filename):
    return os.path.join(directory, filename)

def read_from_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def write_to_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

def get_weather(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
        geo_response = requests.get(geo_url).json()
        if "results" not in geo_response:
            return None

        location = geo_response["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url).json()

        if "current_weather" in weather_response:
            return {
                "location": location.get("name", city),
                "country": location.get("country", ""),
                "temperature": weather_response["current_weather"].get("temperature"),
                "humidity": "N/A", # Open-Meteo does not provide humidity directly in current_weather
                "condition_code": weather_response["current_weather"].get("weathercode"),
            }
    except Exception as e:
        print(f"Error getting weather: {e}")
        return None

def get_weather_condition(code):
    conditions = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast"}
    return conditions.get(code, "N/A")

# --- Centralized Stylesheet ---

STYLESHEET = """
QWidget#MainWidget {
    background-color: #0D0D0D;
    color: #E0E0E0;
    font-family: 'Orbitron', sans-serif;
}
QLabel {
    color: #00AACC;
    font-size: 16px;
}
QLabel#TitleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #00FFFF;
    padding-bottom: 10px;
}
QLabel#StatusLabel {
    font-size: 18px;
    color: #FFFFFF;
}
QTextEdit {
    background-color: rgba(0, 0, 0, 0.5);
    border: 1px solid #00FFFF;
    border-radius: 4px;
    font-size: 14px;
    color: #E0E0E0;
    padding: 10px;
}
QPushButton#MicButton {
    background-color: transparent;
    border: 2px solid #00FFFF;
    border-radius: 40px;
}
"""

class JarvisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mic_is_on = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"{ASSISTANT_NAME} AI")
        self.setGeometry(100, 100, 800, 900)

        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        main_widget.setStyleSheet(STYLESHEET)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)

        # --- Top Grid for Data Widgets ---
        top_grid = QGridLayout()

        self.time_label = QLabel("00:00:00")
        self.date_label = QLabel("Date")
        self.location_label = QLabel("Location")
        self.weather_label = QLabel("Weather")

        top_grid.addWidget(self.time_label, 0, 0, Qt.AlignLeft)
        top_grid.addWidget(self.date_label, 1, 0, Qt.AlignLeft)
        top_grid.addWidget(self.location_label, 0, 1, Qt.AlignRight)
        top_grid.addWidget(self.weather_label, 1, 1, Qt.AlignRight)

        main_layout.addLayout(top_grid)
        main_layout.addWidget(QFrame(self)) # Spacer

        # --- Title ---
        title_label = QLabel(ASSISTANT_NAME, self)
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Chat Display ---
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display, 1)

        # --- Status Label ---
        self.status_label = QLabel("Initializing...", self)
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # --- Mic Button ---
        self.mic_button = QPushButton(self)
        self.mic_button.setObjectName("MicButton")
        self.mic_button.setFixedSize(80, 80)
        self.mic_button.setIconSize(QSize(50, 50))
        self.mic_button.clicked.connect(self.toggle_microphone)
        self.update_mic_icon()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.mic_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # --- Timers ---
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui_from_files)
        self.ui_timer.start(200)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_data_widgets)
        self.data_timer.start(1000) # Update every second for the clock
        self.update_data_widgets(initial=True) # Initial call

    def update_data_widgets(self, initial=False):
        # Update Time
        current_time = QTime.currentTime()
        self.time_label.setText(current_time.toString('hh:mm:ss'))

        # Update Date, Location, and Weather less frequently
        if initial or current_time.second() == 0:
            self.date_label.setText(datetime.now().strftime("%A, %B %d, %Y"))
            weather_data = get_weather(DEFAULT_CITY)
            if weather_data:
                self.location_label.setText(f"{weather_data['location']}, {weather_data['country']}")
                self.weather_label.setText(f"{weather_data['temperature']}°C, {get_weather_condition(weather_data['condition_code'])}")

    def toggle_microphone(self):
        self.mic_is_on = not self.mic_is_on
        write_to_file(get_file_path(TEMP_DIR_PATH, "Mic.data"), str(self.mic_is_on))
        self.update_mic_icon()

    def update_mic_icon(self):
        icon_path = "MicOn.png" if self.mic_is_on else "MicOff.png"
        self.mic_button.setIcon(QIcon(get_file_path(GRAPHICS_DIR_PATH, icon_path)))

    def update_ui_from_files(self):
        chat_message = read_from_file(get_file_path(TEMP_DIR_PATH, "Responses.data"))
        if chat_message:
            self.chat_display.append(chat_message)
            write_to_file(get_file_path(TEMP_DIR_PATH, "Responses.data"), "") # Clear after reading

        status_message = read_from_file(get_file_path(TEMP_DIR_PATH, "Status.data"))
        if status_message:
            self.status_label.setText(status_message)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    # You might need to install this font if it's not on your system
    QFont.insertDatabase('https://fonts.google.com/specimen/Orbitron')
    window = JarvisUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()