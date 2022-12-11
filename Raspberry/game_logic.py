# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# game_logic -- Game conductor.  
#
# This is where the game state is conducted. D
# Decisions about rewarding points, bounces, 
# are made here.

import time 
import sound_manager as sm

class GameLogic():

    def __init__(self, app, hw, sound):
        self._app = app
        self._hw = hw 
        self._sound = sound

    def start_game(self):
        pass

    def ball_drained(self):
        pass

    def ball_released(self):
        pass

    def move_lane_light(self, dir):
        pass




