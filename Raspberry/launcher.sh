#!/bin/sh
# launcher.sh -- used to start up the pinball manager program

cd /
export PYTHONPATH="/home/pi/.local/lib/python3.9/site-packages;/home/pi/pb/lib"
sudo python /home/pi/pb/game1.py 