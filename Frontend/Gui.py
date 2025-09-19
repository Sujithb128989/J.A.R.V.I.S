import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame
from PyQt5.QtGui import QIcon, QPainter, QColor, QTextCharFormat, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import load_dotenv

load_dotenv()

ASSISTANT_NAME = os.getenv("Assistantname", "J.A.R.V.I.S")
CURRENT_DIR = os.getcwd()
TEMP_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Files")
GRAPHICS_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Graphics")

# --- Helper Functions (re-added for compatibility) ---

def get_file_path(directory, filename):
    """Constructs a full path to a file."""
    return os.path.join(directory, filename)

def read_from_file(filepath):
    """Reads content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def write_to_file(filepath, content):
    """Writes content to a file."""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

def SetAssistantStatus(Status):
    write_to_file(get_file_path(TEMP_DIR_PATH, "Status.data"), Status)

def GetAssistantStatus():
    return read_from_file(get_file_path(TEMP_DIR_PATH, "Status.data"))

def ShowTextToScreen(Text):
    write_to_file(get_file_path(TEMP_DIR_PATH, "Responses.data"), Text)

def SetMicrophoneStatus(Command):
    write_to_file(get_file_path(TEMP_DIR_PATH, "Mic.data"), Command)

def GetMicrophoneStatus():
    return read_from_file(get_file_path(TEMP_DIR_PATH, "Mic.data"))

def TempDirectoryPath(Filename):
    return get_file_path(TEMP_DIR_PATH, Filename)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how"]

    if any(word in new_query for word in question_words):
        if query_words and query_words[-1][-1] in ['.', '?', '1']:
            new_query = new_query[:-1]
        else:
            new_query = new_query + "?"
    else:
        if query_words and query_words[-1][-1] in ['.', '?', '1']:
            new_query = new_query[:-1] + "."
        else:
            new_query = new_query + ","
    return new_query.capitalize()

# --- Centralized Stylesheet ---

STYLESHEET = """
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QMainWindow {
    border: 1px solid #333;
}

QTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #333;
    border-radius: 4px;
    font-size: 14px;
    padding: 10px;
}

QScrollBar:vertical {
    border: none;
    background: #1E1E1E;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QPushButton#MicButton {
    background-color: #1E1E1E;
    border: 2px solid #555;
    border-radius: 35px; /* Makes it circular */
    padding: 10px;
}

QPushButton#MicButton:hover {
    border-color: #007ACC;
}

QLabel#StatusLabel {
    font-size: 18px;
    font-weight: bold;
    color: #00AACC;
}

QLabel#TitleLabel {
    font-size: 12px;
    color: #888;
}
"""

class JarvisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mic_is_on = False
        self.old_chat_message = ""
        self.old_status_message = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"{ASSISTANT_NAME} AI")
        self.setGeometry(100, 100, 600, 800)
        self.setStyleSheet(STYLESHEET)

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title Label
        title_label = QLabel(f"{ASSISTANT_NAME} AI", self)
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)

        # Chat Display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)

        # Status Label
        self.status_label = QLabel("Initializing...", self)
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Microphone Button
        self.mic_button = QPushButton(self)
        self.mic_button.setObjectName("MicButton")
        self.mic_button.setFixedSize(70, 70)
        self.mic_button.setIconSize(QSize(40, 40))
        self.mic_button.clicked.connect(self.toggle_microphone)
        self.update_mic_icon()

        # Layout Assembly
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.chat_display, 1) # Give chat display more stretch
        main_layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.mic_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Timer to update UI from files
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_from_files)
        self.timer.start(200) # Update every 200ms

    def toggle_microphone(self):
        self.mic_is_on = not self.mic_is_on
        SetMicrophoneStatus(str(self.mic_is_on))
        self.update_mic_icon()

    def update_mic_icon(self):
        icon_path = "MicOn.png" if self.mic_is_on else "MicOff.png"
        self.mic_button.setIcon(QIcon(get_file_path(GRAPHICS_DIR_PATH, icon_path)))

    def update_ui_from_files(self):
        # Update chat display
        chat_message = read_from_file(get_file_path(TEMP_DIR_PATH, "Responses.data"))
        if chat_message and chat_message != self.old_chat_message:
            self.chat_display.append(chat_message)
            self.old_chat_message = chat_message

        # Update status label
        status_message = read_from_file(get_file_path(TEMP_DIR_PATH, "Status.data"))
        if status_message and status_message != self.old_status_message:
            self.status_label.setText(status_message)
            self.old_status_message = status_message

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = JarvisUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Initialize status files
    SetMicrophoneStatus("False")
    SetAssistantStatus("Ready")
    ShowTextToScreen("")
    GraphicalUserInterface()
