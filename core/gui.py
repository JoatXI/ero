from linux_recorder import LinuxEncoder
from settings import FFmpegSettings
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
import platform, json, sys, os
from PyQt5.QtWidgets import *
from recorder import Encoder
from PyQt5 import uic
import mss

CONFIG_FILE = "config.json"

def load_app_config():
    if not os.path.exists(CONFIG_FILE):
        return {"app_1": "", "app_2": "", "app_3": ""}
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def save_app_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        uic.loadUi("assets/settings.ui", self)
        
        self.browse_button1 = self.findChild(QPushButton, "trackApp_1")
        self.browse_button2 = self.findChild(QPushButton, "trackApp_2")
        self.browse_button3 = self.findChild(QPushButton, "trackApp_3")
        self.app_text_1 = self.findChild(QLineEdit, "appText_1")
        self.app_text_2 = self.findChild(QLineEdit, "appText_2")
        self.app_text_3 = self.findChild(QLineEdit, "appText_3")
        self.save_button = self.findChild(QPushButton, "saveButton")
        self.cancel_button = self.findChild(QPushButton, "cancelButton")
        
        config = load_app_config()
        self.app_text_1.setText(config.get("app_1", ""))
        self.app_text_2.setText(config.get("app_2", ""))
        self.app_text_3.setText(config.get("app_3", ""))
        
        self.browse_button1.clicked.connect(lambda: self.browse_app(self.app_text_1))
        self.browse_button2.clicked.connect(lambda: self.browse_app(self.app_text_2))
        self.browse_button3.clicked.connect(lambda: self.browse_app(self.app_text_3))
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
    def browse_app(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Application Executable")
        if file_path:
            app_name = os.path.basename(file_path)
            line_edit.setText(app_name)
        
    def save_settings(self):
        config = {
            "app_1": self.app_text_1.text(),
            "app_2": self.app_text_2.text(),
            "app_3": self.app_text_3.text()
        }
        save_app_config(config)
        self.close()

class MyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("assets/design.ui", self)
        self.settings = FFmpegSettings()
        self.os = platform.system()
        self.recording = False
        self.sct = mss.mss()
        
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.original_screen_width = size.width()
        self.original_screen_height = size.height()
        
        self.initUI()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(1)
        
    def initUI(self):
        self.live_preview = self.findChild(QLabel, "livePreview")
        self.fps_options = self.findChild(QComboBox, "fpsOptions")
        self.start_button = self.findChild(QPushButton, "startButton")
        self.stop_button = self.findChild(QPushButton, "stopButton")
        self.save_path_btn = self.findChild(QPushButton, "savePath")
        self.path_text = self.findChild(QLineEdit, "pathText")
        self.settings_button = self.findChild(QAction, "settingsButton")
        
        self.fps_options.addItems(["30", "60"])
        self.fps_options.setCurrentText("30")
        
        self.live_preview.setScaledContents(False)
        self.live_preview.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        self.live_preview.setAlignment(Qt.AlignCenter)
        self.live_preview.setMaximumSize(self.original_screen_width, self.original_screen_height)
        
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.save_path_btn.clicked.connect(self.browse_for_path)
        if self.settings_button:
            self.settings_button.triggered.connect(self.open_settings_dialog)
        
    def update_preview(self):
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)
        bytes_per_line = sct_img.width * 4

        image = QImage(sct_img.bgra, sct_img.width, sct_img.height, bytes_per_line, QImage.Format_RGB32)
        scaled_image = image.scaled(self.live_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        pixmap = QPixmap.fromImage(scaled_image)
        self.live_preview.setPixmap(pixmap)

    def browse_for_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory", "")
        if directory:
            self.path_text.setText(directory)

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def start_recording(self):
        if not self.recording:
            selected_fps = int(self.fps_options.currentText())
            self.settings.set_fps(selected_fps)
            
            chosen_directory = self.path_text.text().strip()
            if chosen_directory:
                self.settings.set_output_directory(chosen_directory)
            
            if self.os == "Windows":
                self.windows_encoder = Encoder()
                self.windows_encoder.start_windows_recording()
                self.recording = True
            elif self.os == "Linux":
                self.linux_encoder = LinuxEncoder()
                self.linux_encoder.start_linux_recording()
                self.recording = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
    def stop_recording(self):
        if self.recording:
            if self.os == "Windows":
                self.windows_encoder.stop_windows_recording()
                self.recording = False
            elif self.os == "Linux":
                self.linux_encoder.stop_linux_recording()
                self.recording = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyGUI()
    window.show()
    app.exec_()