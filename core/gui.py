from linux_recorder import LinuxEncoder
from settings import FFmpegSettings
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from recorder import Encoder
from PyQt5.QtWidgets import *
from PyQt5 import uic
import platform, sys
import mss

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
        
        # QTimer for live preview updates (every 1ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(1)
        
    def initUI(self):
        self.live_preview = self.findChild(QLabel, "livePreview")
        self.fps_options = self.findChild(QComboBox, "fpsOptions")
        self.start_button = self.findChild(QPushButton, "startButton")
        self.stop_button = self.findChild(QPushButton, "stopButton")
        
        self.fps_options.addItems(["30", "60"])
        self.fps_options.setCurrentText("30")
        
        self.live_preview.setScaledContents(False)
        self.live_preview.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        self.live_preview.setAlignment(Qt.AlignCenter)
        self.live_preview.setMaximumSize(self.original_screen_width, self.original_screen_height)
        
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        
    def update_preview(self):
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)

        # Calculate bytes per line (width * 4 because each pixel has 4 bytes)
        bytes_per_line = sct_img.width * 4

        image = QImage(sct_img.bgra, sct_img.width, sct_img.height, bytes_per_line, QImage.Format_RGB32)
        
        scaled_image = image.scaled(self.live_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        pixmap = QPixmap.fromImage(scaled_image)
        self.live_preview.setPixmap(pixmap)

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