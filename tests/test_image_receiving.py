import os
import json
import urllib3
import tempfile
import unittest
import threading
from http.server import HTTPServer

from simple_media_player.api.images import RemoteImagesReceiver
from simple_media_player.mockup.imageserver import ImagesRequestHandler, PORT


class TestImageServer(unittest.TestCase):

    def setUp(self):
        self.playlist_url = "http://localhost:%d/playlist" % PORT
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

    def test_image_requests(self):
        http = urllib3.PoolManager()
        r = http.request('GET', self.playlist_url)
        result = json.loads(r.data.decode('utf-8'))

        self.assertIn('playlist', result, "playlist key not found in response")
        self.assertGreater(len(result['playlist']), 0)

        url = result['playlist'][0]
        r = http.request('GET', url)
        result = json.loads(r.data.decode('utf-8'))

        self.assertIn('url', result, "image url not found in response")

    def test_image_receiver(self):
        receiver = RemoteImagesReceiver(
            self.playlist_url, tempfile.gettempdir(), infinite_retry=False)
        image_paths = receiver.receive_images()

        for path in image_paths:
            self.assertTrue(os.path.exists(path))

    def test_wrong_playlist_url_request(self):
        receiver = RemoteImagesReceiver(
            "http://wrong_url/playlist",
            tempfile.gettempdir(), infinite_retry=False)
        self.assertRaises(urllib3.exceptions.HTTPError, receiver.receive_images)


if __name__ == '__main__':
    unittest.main()