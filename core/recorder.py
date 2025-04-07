from ffmpeg import FFmpeg, Progress, FFmpegError
from settings import FFmpegSettings
from pynput import keyboard
import threading
import pyautogui
import sys

class Encoder:
    def __init__(self):
        self.audio_device, self.input_format = FFmpegSettings().set_audio_inputs()
        self.video_input, self.f_video = FFmpegSettings().set_video_inputs()
        self.file_name, self.fps = FFmpegSettings().set_output()
        self.width, self.height = pyautogui.size()
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
                print(progress)
                if not self.running:
                    print('\nterminating recording...')
                    ffmpeg.terminate()
                    
            print('\nencoding video...\n')
            ffmpeg.execute()
        
        except FFmpegError as exception:
            print("An exception has occurred!")
            print("- Message from ffmpeg:", exception.message)
            print("- Arguments to execute ffmpeg:", exception.arguments)
            sys.exit(1)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            print("\nStopping Recording...")
            self.running = False
            return False

    def start_recording(self):
        self.running = True
        
        encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        encoding_thread.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            encoding_thread.join()
            print('\nVideo saved.')

if __name__ == '__main__':
    recorder = Encoder()
    recorder.start_recording()