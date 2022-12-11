# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Game logic for the lanes

from pb_log import log
import playfield_lights as pl 
import sound_manager as sm

class LogicLanes():
    def __init__(self, app, hw, sound, lights):
        self._app = app
        self._hw = hw 
        self._sound = sound 
        self._lights = lights
        self._hot_lane = 0
        self._lanehits = [0, 0, 0]
        self._toplights = [pl.PI_LANE_1_TOP, pl.PI_LANE_2_TOP, pl.PI_LANE_3_TOP]
        self._botlights = [pl.PI_LANE_1_BOT, pl.PI_LANE_2_BOT, pl.PI_LANE_3_BOT]

    def set_hot_lights(self):
        for i in range(3):
            toplight = self._toplights[i]
            if self._hot_lane == i:
                self._lights.set_pixel_blink(toplight, (0, 255, 0), (0, 0, 128), 3, 2)
            else:
                self._lights.set_pixel(toplight, (0, 80, 0))

    def set_score_lights(self):
        for i in range(3):
            light = self._botlights[i]
            hits = self._lanehits[i]
            if hits == 0: self._lights.set_pixel(light, (40, 40, 40))   # Barely on 
            if hits == 1: self._lights.set_pixel(light, (140, 140, 0))  # dull yellow
            if hits == 2: self._lights.set_pixel(light, (200, 0, 0))    # mildly bright red
            if hits == 3: self._lights.set_pixel_blink(light, (255, 0, 0), (0, 0, 255), 40, 5)
            if hits == 4: self._lights.set_pixel_blink(light, (255, 0, 0), (0, 0, 255), 20, 5)
            if hits > 4 and hits <= 6:  self._lights.set_pixel_blink(light, (255, 0, 0), (0, 0, 255), 10, 5)
            if hits > 6 and hits <= 9:  self._lights.set_pixel_blink(light, (255, 0, 0), (0, 0, 255), 5, 20)
            if hits > 9: self._lights.set_pixel(light, (0, 0, 255)) 

    def on_new_game(self):
        self._lanehits = [0, 0, 0]
        self._hot_lane = 1
        self.set_hot_lights()
        self.set_score_lights()

    def award_top_lane(self, indx):
        mult = self._lanehits[indx]
        if mult == 0: mult = 1
        if self._hot_lane == indx: 
            self._lanehits[indx] += 4
            points = 250 * mult
        else:
            self._lanehits[indx] += 1
            points = 100 * mult
        self._app.add_to_score(points)
        self._sound.play(sm.S_LANE_AWARD)
        self.set_score_lights()                    

    def process_hw_event(self, ev):
        ''' Process hardware events that might impact lanes.'''
        if ev == "F1":
            self._hot_lane += 1 
            if self._hot_lane >= 3: self._hot_lane = 0 
            self.set_hot_lights()
        if ev == "F2":
            self._hot_lane -= 1 
            if self._hot_lane < 0: self._hot_lane = 2 
            self.set_hot_lights()
        if ev == "L1":
            self.award_top_lane(0) 
        if ev == "L2":
            self.award_top_lane(1) 
        if ev == "L3":
            self.award_top_lane(2) 
        if ev in ["L4", "L5", "L6", "L7", "L8", "L9", "L10"]:
            self._sound.play(sm.S_LANE_AWARD)
            self._app.add_to_score(100)
