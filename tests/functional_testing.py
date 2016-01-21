import unittest
import threading
from http.server import HTTPServer
from simple_media_player.__main__ import SimpleMediaPlayer
from simple_media_player.mockup.imageserver import ImagesRequestHandler, PORT


class TestDownloadCreatePlayback(unittest.TestCase):

    def setUp(self):
        self.server = HTTPServer(('', PORT), ImagesRequestHandler)
        threading.Thread(target=self.serve).start()

    def serve(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            pass
        finally:
            self.server.server_close()

    def tearDown(self):
        self.server.shutdown()

    def test_download_create_playback(self):
        player = SimpleMediaPlayer()
        player.run(no_wait=True)
        print(player.created_slide_show_path)
        print(player.estimated_slide_show_duration)
        print(player.actual_slide_show_duration)


if __name__ == '__main__':
    unittest.main()
