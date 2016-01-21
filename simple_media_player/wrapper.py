"""
Contains thin wrappers for different Linux utilities. Uses subprocess.Popen
function to spawn child processes.
"""
import math
import subprocess
from datetime import datetime


def avprobe(path: str):
    """Simple wrapper over avprobe utility. Returns actual duration of
    created slide show.
    """
    p = subprocess.Popen(['avprobe', path], stderr=subprocess.PIPE)
    p.wait()
    data = p.stderr.read()
    p.stderr.close()
    d = data.decode().split('Duration:')[-1].split(',')[0].strip()
    d = datetime.strptime(d, '%H:%M:%S.%f')

    to_seconds = lambda t: t / 1e6

    total_seconds = d.hour*3600 + d.minute*60 \
                    + d.second + to_seconds(d.microsecond)

    return total_seconds


class SlideShowPlayer:
    """Thin wrapper over dvd-slideshow utility and media player. Creates slide
    show from specified config file and plays it back.
    """

    DVD_SLIDE_SHOW_BIN = 'dvd-slideshow'

    def __init__(self, output_folder: str):
        self.resolution = '1920x1080'
        self._output = output_folder
        self._mp4 = False
        self._fullscreen = False
        self._player_launch = None

    def mp4(self):
        """Create slide show using MP4 format."""
        self._mp4 = True

    def fullscreen(self):
        """Enable fullscreen playback."""
        self._fullscreen = True

    @property
    def player_bin(self):
        """Returns name of selected player."""
        return self._player_launch[0]

    def create_slide_show(self, name: str, config: str, music_path: str=None,
                          estimated_video_duration: int=None):
        """Creates slide show using dvd-sliedeshow utility.

        Arguments:
            name(str): created video file name
            config(str): path to dvd-slideshow configuration file
            music_path(str): path to background music file
        """
        args = [
            self.DVD_SLIDE_SHOW_BIN,
            '-n', name,
            '-f', config,
            '-o', self._output,
            '-s', self.resolution
        ]

        if music_path is not None:

            if estimated_video_duration is None:
                args.append('-a', music_path)

            else:
                music_duration = avprobe(music_path)
                repeats = math.ceil(estimated_video_duration / music_duration)

                for i in range(repeats):
                    args.append('-a')
                    args.append(music_path)

        if self._mp4:
            args.append('-mp4')

        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return proc


    def vlc(self):
        """Use VLC player for slide show playback."""
        self._player_launch = ['cvlc', '--no-video-title-show']
        if self._fullscreen:
            self._player_launch.append('-f')

    def mpv(self):
        """User mpv player for slide show playback."""
        self._player_launch = ['mpv']
        if self._fullscreen:
            self._player_launch.append('-fs')

    def playback(self, slide_show_path: str):
        """Starts video playback using specified media player

        Arguments:
            slide_show_path(str): path to slide show video file
        """
        args = list(self._player_launch)
        args.append(slide_show_path)
        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return proc
