import unittest
from simple_media_player.slideshow.builder import SlideShowBuilder
from simple_media_player.slideshow.config import TransitionDirection


class TestSlideShowBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = SlideShowBuilder()

    def test_entries_add(self):
        expected_result = '\n'.join([
            "img1.png:5:sub1",
            "crossfade:10",
            "img2.png:10:sub2",
            "wipe:10:left"
        ])

        self.builder.image('img1.png', 5, 'sub1')
        self.builder.cross_fade(10)
        self.builder.image('img2.png', 10, 'sub2')
        self.builder.wipe(10, d=TransitionDirection.Left)

        result = self.builder.build()

        self.assertEqual(len(self.builder.entries), 4,
                         'unexpected entities count')

        self.assertEqual(result, expected_result, 'unexpected config result')


if __name__ == '__main__':
    unittest.main()
