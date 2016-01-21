"""Contains supplementary classes needed for dvd-slideshow generation."""

from enum import Enum


class TransitionName(Enum):
    FadeIn = 'fadein'
    FadeOut = 'fadeout'
    CrossFade = 'crossfade'
    Wipe = 'wipe'


class TransitionDirection(Enum):
    Left = 'left'
    Right = 'right'
    Up = 'up'
    Down = 'down'


class TransitionEntry:
    """Wraps transition effect config entry.

    Used to generate transition effect string from specified transition name,
    duration, subtitle and (for 'wipe' effect only) direction.
    """

    def __init__(self, name: TransitionName, duration: int,
                 subtitle: str='', direction: TransitionDirection=None):
        self.name = name
        self.subtitle = subtitle
        self.duration = duration
        self.direction = direction

    def __str__(self):
        d = self.direction.value if self.direction else ''
        duration = str(self.duration)

        items = [self.name.value, duration, d]

        if self.subtitle:
            items.insert(2, self.subtitle)

        return ':'.join(items).strip(':').strip()


class ImageEntry:
    """Wraps image config entry."""

    def __init__(self, path: str, duration: int, subtitle: str=''):
        self.path = path
        self.duration = duration
        self.subtitle = subtitle

    def __str__(self):
        s = ':'.join([self.path, str(self.duration), self.subtitle])
        return s.strip(':').strip()
