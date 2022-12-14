# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Game logic for the lanes

from pb_log import log
import playfield_lights as pl 
import sound_manager as sm
import config
import random_choice as rc
import neo_colors as cc

class LogicLanes():
    def __init__(self, app, hw, sound, lights):
        self._app = app
        self._hw = hw 
        self._sound = sound 
        self._lights = lights
        self._hot_lane = 0
        self._side_hits = 0
        self._lanehits = [0, 0, 0]
        self._toplights = [pl.PI_LANE_1_TOP, pl.PI_LANE_2_TOP, pl.PI_LANE_3_TOP]
        self._botlights = [pl.PI_LANE_1_BOT, pl.PI_LANE_2_BOT, pl.PI_LANE_3_BOT]
        self._fouls = rc.RandomChoice([sm.S_FOUL_1, sm.S_FOUL_2, sm.S_FOUL_3, sm.S_FOUL_4, sm.S_REDCARD])

    def set_hot_lights(self):
        for i in range(3):
            toplight = self._toplights[i]
            if self._hot_lane == i:
                self._lights.set_pixel_blink(toplight, cc.GREEN, cc.OFF, 3, 2)
            else:
                self._lights.set_pixel(toplight, cc.DULL_GREEN)

    def set_side_lane_lights(self):
        if self._side_hits == 0:
            self._lights.set_pixel_blink(pl.PI_PATH_1, cc.GREEN, cc.OFF, 4, 3)
            self._lights.set_pixel(pl.PI_PATH_2, cc.GREEN)
        if self._side_hits == 1:
            self._lights.set_pixel(pl.PI_PATH_2, cc.RED)
        if self._side_hits == 2:
            self._lights.set_pixel(pl.PI_PATH_1, cc.RED)
        if self._side_hits == 3:
            self._lights.set_pixel(pl.PI_PATH_2, cc.BLUE)
        if self._side_hits > 3:
            self._lights.set_pixel(pl.PI_PATH_2, cc.BLUE)

    def set_score_lights(self):
        for i in range(3):
            light = self._botlights[i]
            hits = self._lanehits[i]
            if hits == 0: self._lights.set_pixel(light, cc.FAINT_WHITE)   # Barely on 
            if hits == 1: self._lights.set_pixel(light, cc.DULL_YELLOW)  # dull yellow
            if hits == 2: self._lights.set_pixel(light, cc.MILD_RED)    # mildly bright red
            if hits == 3: self._lights.set_pixel_blink(light, cc.RED, cc.BLUE, 40, 5)
            if hits == 4: self._lights.set_pixel_blink(light, cc.RED, cc.BLUE, 20, 5)
            if hits > 4 and hits <= 6:  self._lights.set_pixel_blink(light, cc.RED, cc.BLUE, 10, 5)
            if hits > 6 and hits <= 9:  self._lights.set_pixel_blink(light, cc.RED, cc.BLUE, 5, 20)
            if hits > 9: self._lights.set_pixel(light, cc.BLUE) 

    def on_new_game(self):
        self._side_hits = 0
        self._lanehits = [0, 0, 0]
        self._hot_lane = 1
        self.set_hot_lights()
        self.set_score_lights()
        self.set_side_lane_lights()
        self._lights.set_pixel(pl.PI_DROP_HOLE, cc.FAINT_WHITE) 

    def process_top_lane(self, indx):
        mult = self._lanehits[indx]
        if mult == 0: mult = 1
        if self._hot_lane == indx: 
            self._lanehits[indx] += 4
            base_points = config.get_points("top_lane_with_hot_light", 400)
        else:
            self._lanehits[indx] += 1
            base_points = config.get_points("top_lane", 100)
        points = base_points * mult
        self._app.add_to_score(points)
        self._sound.play(sm.S_LANE_AWARD)
        self.set_score_lights()                    

    def process_hw_event(self, ev):
        ''' Process hardware events that might impact lanes.'''
        if not self._app.game_active(): return
        if ev == "F1":  # Right Flipper Button
            self._hot_lane += 1 
            if self._hot_lane >= 3: self._hot_lane = 0 
            self.set_hot_lights()
        if ev == "F2":  # Left Flipper Button
            self._hot_lane -= 1 
            if self._hot_lane < 0: self._hot_lane = 2 
            self.set_hot_lights()
        if ev == "L1":  # Easy Lane
            points = config.get_points("easy_lane", 25)
            self._sound.play(sm.S_DING_LANE)
            self._app.add_to_score(points)
        if ev == "L5":  # Side Lane
            self._side_hits += 1
            points = config.get_points("side_lane", 500)
            self._app.add_to_score(points * self._side_hits)
            self._sound.play(sm.S_WIN_TRUMPET_2)
            self.set_side_lane_lights()
        if ev == "L4": # Upper lane left
            self.process_top_lane(0) 
        if ev == "L3": # Upper lane middle
            self.process_top_lane(1) 
        if ev == "L2": # Upper Lane right
            self.process_top_lane(2)
        if ev in ["L7", "L10"]: # Flipper Lanes
            points = config.get_points("flipper_lanes", 50)
            self._sound.play(sm.S_DING_LANE)
        if ev in ["L8", "L9"]:  # Drain Lanes
            isc  = self._fouls.get()
            self._sound.play(isc)
            points = config.get_points("drain_lanes", 25)
            self._app.add_to_score(points)





