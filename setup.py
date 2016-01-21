"""
Simple Information Kiosk Daemon
-------------------------------

python3 setup.py install

Links
`````
* `development <https://github.com/devforfu/kiosk>`_`

"""

import os
from distutils.core import setup
from itertools import product

from simple_media_player.constants import DefaultParams
from simple_media_player.constants import SCHEDULE_PATH, PLAYER_CONFIG_PATH


# create log folder
log_path = "/var/log/smp/"

if not os.path.exists(log_path):
    os.makedirs(log_path, exist_ok=True)

# demo schedule calling media player each 5 minutes
if os.path.exists(SCHEDULE_PATH):
    SCHEDULE_PATH += ".new"

    if os.path.exists(SCHEDULE_PATH):
        os.remove(SCHEDULE_PATH)

folder, _ = os.path.split(SCHEDULE_PATH)
try:
    os.makedirs(folder, exist_ok=True)
except FileExistsError:
    pass

with open(SCHEDULE_PATH, 'w') as fp:
    for h, m in product(range(0, 24), range(0, 60, 10)):
        fp.write("%s:%s\n" % (h, m))

# default configuration
if os.path.exists(PLAYER_CONFIG_PATH):
    PLAYER_CONFIG_PATH += ".new"

    if os.path.exists(PLAYER_CONFIG_PATH):
        os.remove(PLAYER_CONFIG_PATH)

folder, _ = os.path.split(PLAYER_CONFIG_PATH)
try:
    os.makedirs(folder, exist_ok=True)
except FileExistsError:
    pass

with open(PLAYER_CONFIG_PATH, 'w') as fp:
    fp.write("[simple_media_player]\n")
    for param in DefaultParams:
        fp.write(param.name.lower() + "=" + str(param.value) + '\n')


classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Operating system :: POSIX :: Linux',
    'Intended Audience :: System Administrators',
    'Topic :: Utilities'
]

setup(name='simple_media_player',
      version='0.1',
      description='',
      long_description=__doc__,
      author='',
      author_email='',
      url='https://github.com/devforfu/kiosk',
      packages=['simple_media_player',
                'simple_media_player.api',
                'simple_media_player.mockup',
                'simple_media_player.slideshow'],
      data_files=[('/etc/init', ['simple-media-player.conf']),
                  ('/opt', ['player.sh'])],
      classifiers=classifiers)
