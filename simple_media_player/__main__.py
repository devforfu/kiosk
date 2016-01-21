"""Simple Media Player entry point."""

import os
import glob
import time
import uuid
import random
import logging
import urllib3
import tempfile
import subprocess
import configparser
from itertools import chain
from datetime import datetime, timedelta

import schedule

from .slideshow.builder import SlideShowBuilder
from .wrapper import SlideShowPlayer, avprobe
from .api.images import RemoteImagesReceiver
from .constants import SCHEDULE_PATH, PLAYER_CONFIG_PATH


# logging functionality
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
log.addHandler(sh)

suffix = str(datetime.now()).replace(' ', '_').replace(':', '_')
fh = logging.FileHandler('/var/log/smp/smp_%s' % suffix)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)


def pick_random_music(path: str):
    """Picks random audio file from provided folder.

    Arguments:
        path(str): path to folder with music
    """
    patterns = ('*.mp3', '*.mid', '*.wav', '*.ogg', '*.aac')
    seq = list(chain.from_iterable(glob.glob1(path, p) for p in patterns))
    return os.path.join(path, seq[random.randint(0, len(seq) - 1)])


class SimpleMediaPlayer:

    def __init__(self):
        self.cfg = None
        self.player = None
        self.created_slide_show_path = ''
        self.estimated_slide_show_duration = 0
        self.actual_slide_show_duration = 0
        self.video_encoding_timeout = 900

    def read_config(self, path):
        """Reads media player configuration.

        Arguments:
            path(str): path to config file
        """
        if not os.path.exists(path):
            raise ValueError('config path "%s" not exists' % path)

        config = configparser.ConfigParser()
        config.read(path)
        self.cfg = config['simple_media_player']

    def download_images(self):
        """Downloads images from server specified in configuration."""
        receiver = RemoteImagesReceiver(
            self.cfg['images_api'],
            os.path.expandvars(self.cfg['downloaded_images_path']))

        while True:
            try:
                images = receiver.receive_images()
                return images

            except urllib3.exceptions.HTTPError as e:
                log.warn('[smp][!] Images retrieving error: %s' % str(e))
                log.warn('[smp][!] Trying again...')

    def create_slide_show(self, image_paths: list):
        """Creates slide show with from provided images and random audio track.
        """
        self.player = SlideShowPlayer(
            os.path.expandvars(self.cfg['created_slide_shows_path']))

        single_image_duration = int(self.cfg['image_display_duration'])

        slide_show_params = tempfile.mktemp()
        with open(slide_show_params, 'w') as fp:
            slide_show_config = SlideShowBuilder.create_slide_show(
                image_paths, single_image_duration)
            fp.write(slide_show_config)

        video_file_name = str(uuid.uuid4())

        try:
            audio = pick_random_music(
                os.path.expandvars(self.cfg['background_music_path']))
            log.debug('[smp][.] Picked music: %s' % audio)
            log.debug('[smp][.] Start video creation...\n')

        except Exception as e:
            audio = None
            log.warn('[smp][!] Cannot pick music: ' + str(e))
            log.warn('[smp][!] Slide show will be padded with silence')

        self.player.mp4()
        self.player.resolution = self.cfg['slide_show_resolution']

        video_duration = single_image_duration * len(image_paths)
        proc = self.player.create_slide_show(
            video_file_name, slide_show_params, audio, video_duration)

        try:
            bin_name = "[dvd-slideshow]"
            for line in proc.stdout:
                line = line.decode().strip()
                line = line.replace(bin_name, "")
                line = bin_name + " " + line
                log.debug(line)
            proc.stdout.close()
            proc.wait(timeout=self.video_encoding_timeout)

        except subprocess.TimeoutExpired:
            log.error('[smp][-] Slide show creation timeout expired!')
            return None

        result_path = os.path.join(
            os.path.expandvars(self.cfg['created_slide_shows_path']),
            video_file_name + '.mp4')

        return video_duration, result_path

    def playback_with_delay(self, path, duration, end_playback):
        """Tries to guarantee accurate timing using kind of spin waiting."""
        while True:

            now = datetime.fromtimestamp(time.time())
            if now < (end_playback - timedelta(seconds=duration)):
                log.debug("[smp][.] Current time: %s" % now)
                time.sleep(1)
                continue

            log.debug("[smp][.] Start playback!")
            proc = self.player.playback(path)
            for line in proc.stdout:
                line = line.decode().strip()
                line = "[%s] %s" % (self.player.player_bin, line)
                log.debug(line)
            proc.wait(duration)
            break

    def run(self, end_playback=None, no_wait: bool=False):
        """Starts download-create-playback cycle.

        Arguments:
            end_playback(datetime): time point when playback should be ended
            no_wait(bool): start playback immediately (without spin-waiting)
        """
        log.debug("[smp][.] Read configuration file: '%s'" % PLAYER_CONFIG_PATH)
        self.read_config(PLAYER_CONFIG_PATH)

        log.debug("[smp][.] Try to retrieve images from %s" % self.cfg['images_api'])
        image_paths = self.download_images()

        if image_paths is None:
            log.error('[smp][-] Cannot retrieve images. Terminating...')
            return

        result = self.create_slide_show(image_paths)

        if result is None:
            log.error('[smp][-] Cannot create slide show. Terminating...')
            return

        estimated_duration, slide_show_path = result
        actual_duration = avprobe(slide_show_path)

        self.created_slide_show_path = slide_show_path
        self.estimated_slide_show_duration = estimated_duration
        self.actual_slide_show_duration = actual_duration

        log.debug('[smp][+] Slide show had been created: %s' % slide_show_path)
        log.debug('[smp][.] Estimated slide show duration: %s' % estimated_duration)
        log.debug('[smp][.] Actual slide show duration: %s' % actual_duration)

        if estimated_duration != actual_duration:
            log.debug('[smp][!] Actual duration not equal to estimated value')
            duration = actual_duration
        else:
            duration = estimated_duration

        self.player.fullscreen()
        self.player.mpv()
        # self.player.vlc()

        try:
            now = datetime.now()

            if end_playback is not None:
                if now + timedelta(seconds=duration) > end_playback:
                    log.warn("[smp][!] Attention: created slide show is too "
                             "long to be finished on time and will be "
                             "terminated earlier. It seems that created "
                             "schedule is to dense.")
                    adjusted_wait_time = end_playback - now
                    duration = adjusted_wait_time.total_seconds()

            if no_wait:
                proc = self.player.playback(slide_show_path)
                for line in proc.stdout:
                    log.debug(line.decode().strip())
                proc.stdout.close()
                proc.wait(duration)

            else:
                log.debug('[smp][.] Playback should end at: %s'
                          % str(end_playback))
                self.playback_with_delay(
                    slide_show_path, duration, end_playback)

        except subprocess.TimeoutExpired:
            log.debug("[smp][.] Playback stop...")

        finally:
            now = datetime.now()

            if end_playback is not None:
                if (end_playback.hour != now.hour or
                    end_playback.minute != now.minute or
                        end_playback.second != now.second):

                    log.warn("[smp][!] Playback has not been "
                             "ended at specified time!")

            log.debug('[smp][.] Ended at: %s' % str(now))

        log.debug('[smp][+] Download-create-playback cycle ended!')


def sched():
    """Makes scheduling of download-create-playback cycles."""
    log.debug("[smp][.] Read schedule file: %s" % SCHEDULE_PATH)

    with open(SCHEDULE_PATH) as fp:
        time_table = fp.read().split()

    config = configparser.ConfigParser()
    config.read(PLAYER_CONFIG_PATH)

    minutes_offset = int(config['simple_media_player']['launch_time_offset'])

    now = str(datetime.now().date())

    smp = SimpleMediaPlayer()

    for entry in time_table:
        tp = datetime.strptime(now + ' ' + entry, '%Y-%m-%d %H:%M')
        shifted_time = tp - timedelta(minutes=minutes_offset)

        # start earlier to have time create video and handle issues
        actual_start = ':'.join(str(shifted_time.time()).split(':')[:2])

        schedule.every().day.at(actual_start).do(smp.run, tp)
        log.debug("[smp][.] Job scheduled on %s to be ended at %s"
                  % (actual_start, entry))

    log.debug("[smp][.] Start scheduling loop...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fast', action='store_true')

    args = vars(parser.parse_args())

    while True:
        try:
            if args['fast']:
                player = SimpleMediaPlayer()
                player.run(no_wait=True)

            else:
                sched()

        except KeyboardInterrupt:
            log.info("[smp][!] Keyboard interrupt. Terminating...")

        except Exception as e:
            log.error("[smp][-] Exception occurred: %s" % str(e))
