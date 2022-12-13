# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Game logic for the targets

from pb_log import log
import playfield_lights as pl 
import sound_manager as sm
import config

EPIC_TARGETS_POINTS = [250, 300, 350, 500]

class LogicTargets():
    def __init__(self, app, hw, sound, lights):
        self._app = app
        self._hw = hw 
        self._sound = sound 
        self._lights = lights
        self._epic_targets_hits = [0, 0, 0, 0]    # Target counds
        self._epic_order_next = 0            # Next Target to hit in order
        self._epic_order_achieved = False    # If the target order has been achived. 
        self._panic_hits = 0
        self._xtarg_hits = 0

        self._epic_lights = [pl.PI_TARG_E, pl.PI_TARG_P, pl.PI_TARG_I, pl.PI_TARG_C]

    def set_epic_target_lights(self):
        for i in range(4):
            light = self._epic_lights[i]
            hits = self._epic_targets_hits[i]
            c = (0, 0, 0)
            if hits <= 0: c = (5, 5, 5)      # Barely on 
            if hits == 1: c = (100, 100, 0)  # dull yellow
            if hits == 2: c = (255, 0, 0)    # Bright red
            if hits  > 2: c = (0, 0, 255)    # Bright blue 
            if self._epic_order_next == i: 
                self._lights.set_pixel_blink(light, c, (0, 255, 0), 3, 2)  
            else:
                self._lights.set_pixel(light, c)

    def on_new_game(self):
        self._epic_targets_hits = [0, 0, 0, 0]
        self._epic_order_next = 0 
        self._epic_order_achieved = False
        self.set_epic_target_lights() 
        self._panic_hits = 0
        self._xtarg_hits = 0
        self._lights.set_pixel(pl.PI_TARG_PANIC_1, (5,5,5))
        self._lights.set_pixel(pl.PI_TARG_PANIC_2, (5,5,5))
        self._lights.set_pixel(pl.PI_TARG_X, (5,5,5))
                
    def process_epic_hit(self, itarg):
        point_table = config.get_points("epic_targets", [250, 300, 350, 500])
        self._app.add_to_robot_parts()
        self._epic_targets_hits[itarg] += 1 
        points = self._epic_targets_hits[itarg] * point_table[itarg]
        self._app.add_to_score(points)
        tn = ["E", "P", "I", "C"]
        log(f"EPIC target '{tn[itarg]}' hit. {points} awarded.")
        if itarg == self._epic_order_next:
            self._epic_order_next += 1
            if self._epic_order_next > 3:
                self._epic_order_achieved = True
                self._epic_order_next = 0
                self._sound.play(sm.S_WIN_TRUMPET_1)
                points = config.get_points("epic_target_inorder_points", 5000)
                self._app.add_to_score(points) 
                log(f"EPIC targets hit in order. {points} awarded.")
            else:
                self._sound.play(sm.S_DING_TARGET)
        else:
            self._epic_order_next = 0
            self._sound.play(sm.S_DING_TARGET)
        self.set_epic_target_lights()

    def process_hw_event(self, ev):
        ''' Process hardware events pretainting to targets.'''
        if not self._app.game_active(): return
        if ev == "T1":  # Target E 
            self.process_epic_hit(0)
        if ev == "T2":  # Target P 
            self.process_epic_hit(1)
        if ev == "T3":  # Target I 
            self.process_epic_hit(2)
        if ev == "T4":  # Target C 
            self.process_epic_hit(3)
        if ev == "T5":  # Panic Target
            self._panic_hits += 1
            if self._panic_hits == 1: self._lights.set_pixel(pl.PI_TARG_PANIC_1, (255, 0, 0))
            if self._panic_hits > 1: self._lights.set_pixel(pl.PI_TARG_PANIC_2, (255, 0, 0))
            base_points = config.get_points("target_panic", 500)
            points = base_points * self._panic_hits
            self._app.add_to_score(points) 
            log(f"Panic target hit. {points} awarded.")
            self._sound.play(sm.S_DING_TARGET)
        if ev == "T6":  # X Target
            self._xtarg_hits += 1
            self._lights.set_pixel(pl.PI_TARG_X, (255, 0, 0))
            base_points = config.get_points("target_x", 750)
            points = base_points * self._xtarg_hits
            self._app.add_to_score(points) 
            log(f"X target hit. {points} awarded.")
            self._sound.play(sm.S_DING_TARGET)
        
        





