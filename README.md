Pre-Installation Requirements
-----------------------------

Simple Media Player Software external dependencies:

1. dvd-slideshow utility
2. vlc and/or mpv
3. upstart-sysv
3. python3


Installation
------------

Steps to install and launch Simple Media Player Software 
using virtualenv (Ubuntu)

0. sudo apt-get upstart-sysv ( **if needed** )

1. sudo apt-get install virtualenv

2. virtualenv --python=/usr/bin/python3.4 ~/venv

3. git clone https://gitlab.com/devforfu/simple_media_player_software.git smp

4. cd smp 

5. git checkout xwin && sudo ~/venv/bin/python3 setup.py install

6. sudo chmod +x /opt/player.sh 

7. ~/venv/bin/pip3 install -r requirements.txt

8. ~/venv/bin/python3 -m simple_media_player


Kiosk example
-------------

There is exapmle of setting up informational kiosk showing slide show in 
specified periods of time. 

1. install Ubuntu Server or use virtual machine

2. install Google Chrome to show something on boot (you can use anything else) 
and X server

    + sudo add-apt-repository 'deb http://dl.google.com/linux/chrome/deb stable main'
    
    + wget -q -O - *https://dl-ssl.google.com/linux/linux_signing_key.pub* | sudo apt-key add -
    
    + sudo apt update
    
    + sudo apt install --no-install-recommends xorg openbox google-chrome-stable pulseaudio
    
3. add user to audio group: sudo usermode -a -G audio $USER_NAME
            
4. install VLC (or MPV) player: sudo apt-get vlc ( **warning: vlc is not working under root** )

5. install Simple Media Player Software (previous TODO list)

6. edit /etc/init/simple-media-player.conf to set correct user name

7. edit /opt/player.sh to set correct user name and correct GUI application

8. reboot server - you will see loaded Google Chrome and each 20 minutes slide 
show will be shown (you may change config or pass **-f** key to media player 
to see immediate results)