import os
import abc
import json
import urllib3
from datetime import datetime
from urllib3.exceptions import MaxRetryError, RequestError, HTTPError


class ImagesReceiver(metaclass=abc.ABCMeta):
    """Abstract image receiver.

    Each receiver should specify path that will be used to store downloaded
    files and a method for images receiving.
    """

    @abc.abstractproperty
    def path(self):
        pass

    @abc.abstractmethod
    def receive_images(self):
        pass


class RemoteImagesReceiver(ImagesReceiver):
    """Implements remote images receiver.

    Class instances download using API call images into local folder.
    """

    def __init__(self, api, storing_folder,
                 download_attempts=10, infinite_retry=True):
        self._api = api
        self._downloads = storing_folder
        self._infinite_retry = infinite_retry
        self._download_attempts = download_attempts

    @property
    def path(self):
        return self._downloads

    def _create_attempts_gen(self):
        attempt = 0
        while self._infinite_retry:
            yield attempt
            attempt += 1
        for i in range(self._download_attempts):
            yield i

    def _get_request(self, http, url, preload=True):
        """Helper function for HTTP requests."""

        def make_request():
            try:
                return http.request('GET', url, preload_content=preload)
            except HTTPError:
                return None

        gen = self._create_attempts_gen()

        for _ in gen:
            r = make_request()
            if r is not None:
                return r

        raise HTTPError("cannot retrieve url: %s" % url)

    def receive_images(self, timeout=20.0):
        """Downloads images via provided API."""
        http = urllib3.PoolManager(timeout=timeout)
        chunk_size = 4096
        downloaded_images = []

        timestamp = datetime.today().strftime("%Y-%m%d-%H%M-%S")
        images_folder = os.path.join(self._downloads, timestamp)
        os.makedirs(images_folder, exist_ok=True)

        r = self._get_request(http, self._api)
        decoded = r.data.decode('utf8')
        playlist = json.loads(decoded)['playlist']

        for url in playlist:
            r = self._get_request(http, url)
            decoded = r.data.decode('utf8')
            image_url = json.loads(decoded)['url']

            # actual image retrieving
            for _ in self._create_attempts_gen():
                r = self._get_request(http, image_url, preload=False)

                if not r:
                    continue

                image_name = image_url.split('/')[-1]
                local_path = os.path.join(images_folder, image_name)

                with open(local_path, 'wb') as img:
                    while True:
                        data = r.read(chunk_size)
                        if not data:
                            break
                        img.write(data)

                downloaded_images.append(local_path)
                r.release_conn()
                break

        if not downloaded_images:
            import shutil
            shutil.rmtree(images_folder, ignore_errors=True)
            raise HTTPError("cannot retrieve images from url: %s" % self._api)

        return downloaded_images
