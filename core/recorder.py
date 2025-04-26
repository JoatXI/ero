import threading, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ffmpeg import FFmpeg, Progress, FFmpegError
from core.settings import FFmpegSettings
import pyautogui

class Encoder:
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
                .input(self.video_input, f=self.f_video, framerate=self.fps, offset_x=0, offset_y=0, video_size=f"{self.width}x{self.height}")
                .input(f"audio={self.audio_device}", rtbufsize="1024M", f=self.input_format, ac=2, ar=22050, channel_layout="stereo", audio_buffer_size="80m", itsoffset=0.5)
                .output(self.file_name, acodec="libmp3lame", vcodec="libx264", crf=23, preset="ultrafast", pix_fmt="yuv420p")
            )
            
            @ffmpeg.on("progress")
            def time_to_terminate(progress: Progress):
                if not self.running:
                    ffmpeg.terminate()
                    
            ffmpeg.execute()
        except FFmpegError as exception:
            print("Error occured:", exception)
            sys.exit(1)

    def start_windows_recording(self):
        self.running = True
        self.encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        self.encoding_thread.start()
    
    def stop_windows_recording(self):
        self.running = False
        if self.encoding_thread:
            self.encoding_thread.join()

if __name__ == '__main__':
    recorder = Encoder()
    recorder.start_windows_recording()