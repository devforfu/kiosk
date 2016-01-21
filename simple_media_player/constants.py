"""
Default configuration parameters for media player.
"""
import os
from enum import Enum


SCHEDULE_PATH = "/etc/simple_media_player/schedule.cfg"

PLAYER_CONFIG_PATH = "/etc/simple_media_player/parameters.cfg"

HOME = os.environ['HOME']


class DefaultParams(Enum):
    """Simple Media Player Software parameters."""

    # paths to directories with content for slide-show
    DOWNLOADED_IMAGES_PATH = \
        os.path.join(HOME, "Pictures/media_player_images")

    CREATED_SLIDE_SHOWS_PATH = \
        os.path.join(HOME, "Videos/media_player_slide_shows")

    BACKGROUND_MUSIC_PATH = \
        os.path.join(HOME, "Music/media_player_music")

    # URL for images retrieving
    IMAGES_API = "http://localhost:8000/playlist"

    # offset in minutes before time point specified in schedule file
    LAUNCH_TIME_OFFSET = 7

    IMAGE_DISPLAY_DURATION = 15

    SLIDE_SHOW_RESOLUTION = '1920x1080'
