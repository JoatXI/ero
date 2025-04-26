import threading, sys, os
from ffmpeg import FFmpeg, Progress, FFmpegError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.settings import FFmpegSettings
import pyautogui

class LinuxEncoder:
    def __init__(self):
        self.audio_device, self.input_format = FFmpegSettings().set_audio_inputs()
        self.video_input, self.f_video = FFmpegSettings().set_video_inputs()
        self.file_name, self.fps = FFmpegSettings().set_output()
        self.width, self.height = pyautogui.size()
        self.encoding_thread = None
        self.running = False
        
    def ffmpeg_encoder(self):
        try:
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(self.video_input, video_size=f"{self.width}x{self.height}", framerate=self.fps, f=self.f_video)
                .input(self.audio_device, f=self.input_format, ac=2, sample_rate=44100, channels=2, itsoffset=0.5)
                .output(self.file_name, acodec="libmp3lame", vcodec="libx264", crf=28, preset="ultrafast")
            )
            
            @ffmpeg.on("progress")
            def time_to_terminate(progress: Progress):
                if not self.running:
                    ffmpeg.terminate()
                    
            ffmpeg.execute()
        except FFmpegError as exception:
            print("Error occured:", exception)
            sys.exit(1)

    def start_linux_recording(self):
        self.running = True
        self.encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        self.encoding_thread.start()

    def stop_linux_recording(self):
        self.running = False
        if self.encoding_thread:
            self.encoding_thread.join()

if __name__ == '__main__':
    recorder = LinuxEncoder()
    recorder.start_linux_recording()