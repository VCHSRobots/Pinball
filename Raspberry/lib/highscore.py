# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# highscore.py -- Keeps track of high score
#

import os 
import time
import common 

if common.platform() == "real":
    highscore_file_path = "/home/pi/pb/logs/highscore.txt"
else:
    highscore_file_path = "C:\\Users\\dalbr\\Documents\\Projects\\Epic_Robots_2023\\PinballMachine\\Software\\logs\\highscore.txt"

def get_highscore():
    try:
        f = open(highscore_file_path, "r")
        s = f.read()
        score = int(s) 
        f.close()
        return score
    except Exception:
        return 0 

def save_highscore(score):
    try:
        f = open(highscore_file_path, "w")
        f.write(f"{score}")
        f.close() 
        return True
    except Exception:
        return False
