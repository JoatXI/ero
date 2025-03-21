import platform
import cpuinfo
import GPUtil

class FFmpegSettings:
    def __init__(self):
        self.nvidia_gpu = GPUtil.getGPUs()
        self.info = cpuinfo.get_cpu_info()
        self.os = platform.system()
        self.amd_gpu = False
        
    def __repr__(self):
        return f"\nSettings(os={self.os}, CPU={self.info}, Nvidia GPU={self.nvidia_gpu}, AMD GPU?={self.amd_gpu})"
    
    def set_audio_inputs(self):
        if self.os == "Windows":
            audio_device = "Stereo Mix (Realtek(R) Audio)"
            input_format = "dshow"
            return audio_device, input_format
        elif self.os == "Linux":
            audio_device = "default"
            input_format = "pulse"
            return audio_device, input_format
        raise Exception("Unknown Operating System")

    def set_video_inputs(self):
        print(self.os)

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
            print("Error setting encoder:", e)