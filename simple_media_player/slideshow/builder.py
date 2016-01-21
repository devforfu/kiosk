from .config import TransitionName, TransitionDirection, TransitionEntry
from .config import ImageEntry


class SlideShowBuilder:
    """Builds config file for dvd-slideshow utility in step-by-step manner."""

    def __init__(self):
        self.entries = []

    def image(self, path: str, duration: int, subtitle: str=''):
        """Adds image entry into config file."""
        e = ImageEntry(path, duration, subtitle)
        self.entries.append(e)
        return self

    def fade_in(self, duration: int, subtitle: str=''):
        """Adds fade-in transition into config file."""
        e = TransitionEntry(TransitionName.FadeIn, duration, subtitle)
        self.entries.append(e)
        return self

    def fade_out(self, duration: int, subtitle: str=''):
        """Adds fade-out transition into config file."""
        e = TransitionEntry(TransitionName.FadeOut, duration, subtitle)
        self.entries.append(e)
        return self

    def cross_fade(self, duration: int, subtitle: str=''):
        """Adds crossfade transition into config file."""
        e = TransitionEntry(TransitionName.CrossFade, duration, subtitle)
        self.entries.append(e)
        return self

    def wipe(self, duration: int, subtitle: str='',
             d: TransitionDirection=None):
        """Adds wipe transition into config file."""
        e = TransitionEntry(TransitionName.Wipe, duration, subtitle, d)
        self.entries.append(e)
        return self

    def build(self):
        """Concatenates all specified effects and images into single string."""
        return '\n'.join([str(e) for e in self.entries]) + '\n'

    @staticmethod
    def create_slide_show(images: list, image_duration: int):
        """Creates slide show from provided images.

        Transitions between images are selected in a random manner.

        Arguments:
            images(list): a list of images paths to be used in slide show
            image_duration(int): duration of each image showing
        """
        import random
        builder = SlideShowBuilder()
        transition_duration = 2

        for image in images[:-1]:
            builder.image(image, image_duration)
            choice = random.randint(0, 2)
            make_transition = {
                0: lambda d, s: builder.fade_out(d//2, s).fade_in(d//2, s),
                1: lambda d, s: builder.cross_fade(d, s),
                2: lambda d, s: builder.wipe(d, s)
            }[choice]

            make_transition(transition_duration, '')

        builder.image(images[-1], image_duration)
        builder.fade_out(transition_duration)

        return builder.build()
