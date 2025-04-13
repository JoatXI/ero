from linux_recorder import LinuxEncoder
from PyQt5.QtGui import QPixmap, QImage
from settings import FFmpegSettings
from PyQt5.QtCore import QTimer, Qt
import platform, json, sys, os
from PyQt5.QtWidgets import *
from recorder import Encoder
from PyQt5 import uic
import mss

CONFIG_FILE = "config.json"
PATH_FILE = "path.json"

def load_app_config():
    if not os.path.exists(CONFIG_FILE):
        return {"app_1": "", "app_2": "", "app_3": ""}
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def path_loader():
    if not os.path.exists(PATH_FILE):
        return {"chosen_dir": os.path.expanduser("~/Videos")}
    with open(PATH_FILE, "r") as file:
        return json.load(file)

def save_app_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
        
def set_output_path(dir):
    with open(PATH_FILE, "w") as file:
        json.dump(dir, file, indent=4)

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
        self.path_text = self.findChild(QLineEdit, "pathText")
        self.path_btn = self.findChild(QPushButton, "savePath")
        self.save_button = self.findChild(QPushButton, "saveButton")
        self.cancel_button = self.findChild(QPushButton, "cancelButton")
        
        config = load_app_config()
        save_directory = path_loader()
        
        self.app_text_1.setText(config.get("app_1", ""))
        self.app_text_2.setText(config.get("app_2", ""))
        self.app_text_3.setText(config.get("app_3", ""))
        
        checked_path = save_directory.get("chosen_dir", "")
        if checked_path:
            self.path_text.setText(checked_path)
        else:
            self.path_text.setText(os.path.expanduser("~/Videos"))
        
        self.browse_button1.clicked.connect(lambda: self.browse_app(self.app_text_1))
        self.browse_button2.clicked.connect(lambda: self.browse_app(self.app_text_2))
        self.browse_button3.clicked.connect(lambda: self.browse_app(self.app_text_3))
        self.path_btn.clicked.connect(lambda: self.path_browse(self.path_text))
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
    def browse_app(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Application Executable")
        if file_path:
            app_name = os.path.basename(file_path)
            line_edit.setText(app_name)
    
    def path_browse(self, line_text):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory", "")
        if directory:
            line_text.setText(directory)
    
    def save_settings(self):
        config = {
            "app_1": self.app_text_1.text(),
            "app_2": self.app_text_2.text(),
            "app_3": self.app_text_3.text()
        }
        path = {
            "chosen_dir": self.path_text.text().strip()
        }
        
        save_app_config(config)
        if path:
            set_output_path(path)
        self.close()

class MyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("assets/design.ui", self)
        self.settings = FFmpegSettings()
        self.os = platform.system()
        self.recording = False
        self.sct = mss.mss()
        
        self.counter = 0
        self.display_counter = QTimer()
        self.display_counter.timeout.connect(self.update_time_label)
        
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
        self.settings_button = self.findChild(QAction, "settingsButton")
        self.time_label = self.findChild(QLabel, "timeLabel")
        
        self.fps_options.addItems(["30", "60"])
        self.fps_options.setCurrentText("30")
        
        self.live_preview.setAlignment(Qt.AlignCenter)
        self.live_preview.setMaximumSize(self.original_screen_width, self.original_screen_height)
        
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
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

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def update_time_label(self):
        self.counter += 1
        hours = self.counter // 3600
        minutes = (self.counter % 3600) // 60
        seconds = self.counter % 60
        self.time_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def start_recording(self):
        if not self.recording:
            selected_fps = int(self.fps_options.currentText())
            self.settings.set_fps(selected_fps)
            
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
            
            self.counter = 0
            self.time_label.setText("00:00:00")
            self.display_counter.start(1000)
            
    def stop_recording(self):
        if self.recording:
            if self.os == "Windows":
                self.windows_encoder.stop_windows_recording()
                self.recording = False
            elif self.os == "Linux":
                self.linux_encoder.stop_linux_recording()
                self.recording = False
    
            self.display_counter.stop()
            self.counter = 0
            self.time_label.setText("00:00:00")

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        if self.recording:
            reply = QMessageBox.question(self,
                "Recording in Progress",
                "A recording is currently in progress."
                "Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self.os == "Windows":
                    self.windows_encoder.stop_windows_recording()
                elif self.os == "Linux":
                    self.linux_encoder.stop_linux_recording()

                self.display_counter.stop()
                self.recording = False
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyGUI()
    window.show()
    app.exec_()