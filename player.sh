#!/bin/bash

export USER_NAME=ubuntu

xset -dpms
xset s off
openbox-session &

echo "running mockup server..." > /tmp/image_server_beacon
/home/$USER_NAME/venv/bin/python3 -m simple_media_player.mockup.imageserver &

echo "running download-create-playback cycle..." >> /tmp/cycle_beacon

#while true; do
    /home/$USER_NAME/venv/bin/python3 -m simple_media_player &
    google-chrome --kiosk --no-first-start 'http://python.org'
#done
