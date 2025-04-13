import platform
import datetime
import sys

class FFmpegSettings:
    os = platform.system()
    fps = 30

    @classmethod
    def get_operating_system(cls):
        """
        Sets the video inputs based on users operating system
        """
        return cls.os

    @classmethod
    def set_audio_inputs(cls):
        """
        Sets the audio inputs based on users operating system
        Returns the audio device and format as two-string tuple
        """
        if cls.os == "Windows":
            audio_device = "Stereo Mix (Realtek(R) Audio)"
            input_format = "dshow"
            return audio_device, input_format
        elif cls.os == "Linux":
            audio_device = "alsa_output.pci-0000_00_1b.0.analog-stereo"
            input_format = "pulse"
            return audio_device, input_format
        else:
            raise Exception("Unknown Operating System")

    @classmethod
    def set_video_inputs(cls):
        """
        Sets the video inputs based on users operating system.
        Returns the video input and format as two-string tuple
        """
        try:
            if cls.os == "Windows":
                video_input = "desktop"
                f_video = "gdigrab"
                return video_input, f_video
            elif cls.os == "Linux":
                video_input = ":0.0"
                f_video = "x11grab"
                return video_input, f_video
            else:
                raise Exception("Unsupported Operating System")
        except Exception as e:
            print("Error occurred while setting video inputs:", e)
            sys.exit(1)

    @classmethod
    def set_fps(cls, fps_value):
        """
        Set the framerate value.
        Allowed values are only 30 or 60.
        """
        if fps_value in (30, 60):
            cls.fps = fps_value
        else:
            raise ValueError("Invalid FPS value")

    @classmethod
    def set_output(cls):
        """
        Gets the current framerate setting
        and sets the output file name.
        Returns the output file name and 
        framerate as string and integer tuple
        """
        file_name = f"{datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')}.mp4"
        return file_name, cls.fps
