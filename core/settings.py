import platform

class FFmpegSettings:
    def __init__(self):
        self.os = platform.system()

    def get_operating_system(self):
        return self.os
    
    def set_audio_inputs(self):
        if self.os == "Windows":
            audio_device = "Stereo Mix (Realtek(R) Audio)"
            input_format = "dshow"
            return audio_device, input_format
        elif self.os == "Linux":
            audio_device = "alsa_output.pci-0000_00_1b.0.analog-stereo"
            input_format = "pulse"
            return audio_device, input_format
        raise Exception("Unknown Operating System")

    def set_video_inputs(self):
        print(f'\n{self.os}')

        try:
            if self.os == "Windows":
                video_input = "desktop"
                f_video = "gdigrab"
                return video_input, f_video
            elif self.os == "Linux":
                video_input = ":0.0"
                f_video = "x11grab"
                return video_input, f_video
        except Exception as e:
            print("Error occured while setting video inputs:", e)
            SystemExit