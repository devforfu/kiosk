import os
import glob
import json
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer


PORT = 8000
MIN_IMAGES = 3
MAX_IMAGES = 15


class ImagesRequestHandler(SimpleHTTPRequestHandler):
    """Mockup requests handler to be used for testing images downloading.

    Handler allows to setup localhost server able to handle following requests:

        1) retrieve dummy playlist:

            http://localhost:PORT/playlist


        2) get path to random image from local folder:

            http://localhost:PORT/random_image


        3) retrieve specified image from local folder:

            http://localhost:PORT/img/image_name.png
    """

    SAMPLE_IMAGES_FOLDER = os.path.join(os.environ['HOME'], 'Pictures/Samples')

    def do_GET(self):
        response = None
        content_type = None

        if self.path.endswith('/playlist'):
            address = 'http://localhost:%d/random_image' % PORT
            frames = random.randint(MIN_IMAGES, MAX_IMAGES)
            images = [address for _ in range(frames)]
            response = json.dumps({'playlist': images})
            content_type = 'application/json'
            response = response.encode('utf-8')

        elif self.path.endswith('/random_image'):
            images = [p for p in glob.glob1(self.SAMPLE_IMAGES_FOLDER, "*.png")]
            img = images[random.randint(0, len(images) - 1)]
            url = 'http://localhost:%d/img/%s' % (PORT, img)
            response = json.dumps({'url': url})
            content_type = 'application/json'
            response = response.encode('utf-8')

        elif self.path.startswith('/img'):
            image_name = self.path.split('/')[-1]
            image_path = os.path.join(self.SAMPLE_IMAGES_FOLDER, image_name)
            with open(image_path, 'rb') as img:
                response = img.read()
            content_type = 'application/image'

        if response is None:
            response = ''
            content_type = ''

        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)


def run_server(host='', port=PORT):
    address = (host, port)
    images_server = HTTPServer(address, ImagesRequestHandler)
    images_server.serve_forever()


if __name__ == '__main__':
    run_server()
