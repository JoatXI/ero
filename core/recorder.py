from ffmpeg import FFmpeg, Progress, FFmpegError
from settings import FFmpegSettings
import subprocess
import threading
import pyautogui
import keyboard
import datetime

class Encoder:
    def __init__(self, fps=30):
        self.file_name = f"{datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')}.mkv"
        self.audio_device, self.input_format = FFmpegSettings().set_audio_inputs()
        self.encoder = FFmpegSettings().set_encoder()
        self.width, self.height = pyautogui.size()
        self.running = False
        self.fps = fps
        
    def ffmpeg_encoder(self):
        try:
            mss_stream = subprocess.Popen(
                'python core/frame_capture.py',
                stdout=subprocess.PIPE
            )
            
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input("pipe:0", f="rawvideo", s=f"{self.width}x{self.height}", pix_fmt="bgra", r=self.fps)
                .input(f"audio={self.audio_device}", rtbufsize="1024M", f=self.input_format, ac=2, ar=44100, channel_layout="stereo", audio_buffer_size="80m")
                .output(self.file_name, acodec="copy", vcodec=self.encoder, pix_fmt="yuv420p", preset="slow", crf=22, shortest=None)
            )
            
            @ffmpeg.on("progress")
            def time_to_terminate(progress: Progress):
                print(progress)
                if not self.running:
                    print('\nterminating recording...')
                    ffmpeg.terminate()
                    
            print('\nencoding video...\n')
            ffmpeg.execute(mss_stream.stdout)
        
        except FFmpegError as exception:
            print("An exception has occurred!")
            print("- Message from ffmpeg:", exception.message)
            print("- Arguments to execute ffmpeg:", exception.arguments)

    def start_recording(self):
        self.running = True
        
        encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        encoding_thread.start()
        
        if keyboard.read_key() == "esc":
            print("\nStopping Recording...")
            self.running = False
            
            encoding_thread.join()
            print('\nVideo saved.')

if __name__ == '__main__':
    recorder = Encoder()
    recorder.start_recording()