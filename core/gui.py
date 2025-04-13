from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
)
from pynput.keyboard import Controller, Key
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from settings import FFmpegSettings
from recorder import Encoder
import threading
import mss
import sys

class RecorderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ẹro")
        self.is_recording = False
        self.encoder_instance = None
        self.encoder_thread = None
        self.keyboard_controller = Controller()
        self.sct = mss.mss()

        screen = QApplication.primaryScreen()
        size = screen.size()
        self.original_screen_width = size.width()
        self.original_screen_height = size.height()

        self.preview_min_width = 640
        self.preview_min_height = 480
        self.preview_max_width = self.original_screen_width
        self.preview_max_height = self.original_screen_height

        self.initUI()

        # QTimer for live preview updates (every 1ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(1)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.preview_label = QLabel("Live Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(self.preview_min_width, self.preview_min_height)
        self.preview_label.setMaximumSize(self.preview_max_width, self.preview_max_height)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.fps_combo.setCurrentText("30")

        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)

        # Layout setup
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_label)
        vbox.addWidget(self.fps_combo)
        hbox = QHBoxLayout()
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        central_widget.setLayout(vbox)

    def update_preview(self):
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)

        # Calculate bytes per line (width * 4 because each pixel has 4 bytes)
        bytes_per_line = sct_img.width * 4

        image = QImage(sct_img.bgra, sct_img.width, sct_img.height, bytes_per_line, QImage.Format_ARGB32)
        
        preview_size = self.preview_label.size()
        scaled_image = image.scaled(preview_size.width(), preview_size.height(), Qt.KeepAspectRatio)

        pixmap = QPixmap.fromImage(scaled_image)
        self.preview_label.setPixmap(pixmap)

    def start_recording(self):
        if not self.is_recording:
            selected_fps = int(self.fps_combo.currentText())
            FFmpegSettings().set_fps(selected_fps)
            print(f"Starting recording at {selected_fps} FPS...")
            self.encoder_instance = Encoder()
            self.encoder_thread = threading.Thread(target=self.encoder_instance.start_recording)
            self.encoder_thread.start()
            self.is_recording = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_recording(self):
        if self.is_recording:
            print("Stopping recording...")
            self.keyboard_controller.press(Key.esc)
            self.keyboard_controller.release(Key.esc)
            if self.encoder_thread:
                self.encoder_thread.join()
            self.is_recording = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecorderGUI()
    window.show()
    sys.exit(app.exec_())
