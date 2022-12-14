# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Panic logic

import time
from pb_log import log
import playfield_lights as pl 
import sound_manager as sm
import config
import random_choice as rc
import neo_colors as cc

possible_panics = rc.RandomChoice([
        (13, sm.S_PANIC_2),    # "Panic_CAD_Not_Ready.wav"),
        (23, sm.S_PANIC_3),    # "Panic_NoCNC.wav"),
        (30, sm.S_PANIC_1),    # "Painc_Parts_Out_Of_Stock.wav"),
        (37, sm.S_PANIC_4),    # "Panic_Programmers_Sick.wav"),
        (44, sm.S_PANIC_5) ])   # "Panic_Robot_Is_Trash.wav")

MODE_PANIC_OFF = 0
MODE_ANOUNCE = 1
MODE_STARTUP_ANAIMATION = 2
MODE_ACCUMULATION = 3
MODE_ADDING_POINTS = 4

class LogicPanic():
    def __init__(self, app, hw, sound, lights):
        self._app = app
        self._hw = hw 
        self._sound = sound 
        self._lights = lights
        self._inpanic = False 
        self._mode = MODE_PANIC_OFF
        self._panic_t0 = time.monotonic() 
        self._istage = 0 
        self._stage_t0 = time.monotonic()
        self._nbonus  = 0 
        self._panic_choice = None
        self._hits = 0

    def in_panic(self):
        return self._inpanic

    def on_new_game(self):
        ''' Should be called on a new game.'''
        self._panic_choice = possible_panics.get()
        log(f"Panic time will be = {self._panic_choice}")
        self._nbonus = 0 
        self._inpanic = False
        self._mode = MODE_PANIC_OFF
        self._hits = 0
        self.set_target_lights()
        self.set_bonus_lights()

    def set_bonus_lights(self):
        self._lights.set_pixel(pl.PI_COL_RT, cc.DULL_GREEN)
        self._lights.set_pixel(pl.PI_COL_MID, cc.YELLOW)
        self._lights.set_pixel(pl.PI_COL_LEFT, cc.DULL_GREEN)

    def on_drop_hole(self):
        ''' Should be called when a ball goes into the drop hole.'''
        pass 

    def on_final_drain(self):
        ''' Should be called when no more balls on the playing field.'''
        if self.in_panic:
            if self._mode == MODE_ADDING_POINTS: return 
            log("Panic ending due to ball draining.")
            self.end_panic()

    def on_game_over(self):
        ''' Should be called when the game is over.'''
        self._inpanic = False
    
    def on_new_day(self, iday):
        ''' Should be called when the day counter is increased.'''
        id, sn = self._panic_choice
        if id != iday: return
        log(f"Starting panic on day {iday}.")
        self._inpanic = True
        self._mode = MODE_ANOUNCE
        log("Panic mode changed to ANOUNCE.")
        self._nbonus = 0
        self._sound.play(sn)
        self.set_target_lights()
        self._lights.set_lamp_modulate(pl.LAMP_PANIC, 0, 255, 4)  
        self._lights.set_all_chase(cc.GREEN, cc.WHITE, 1, 3)  
        self._panic_t0 = time.monotonic()
        self._stage_t0 = time.monotonic()
        self._istage = 0

    def manage_startup_lights(self):
        tnow = time.monotonic() 
        if tnow - self._stage_t0 < 0.100: return
        self._stage_t0 = tnow 
        self._istage += 1
        if self._istage < 20: return
        if self._istage <= 30:
            i = self._istage - 20
            ncyc = int(i / 5)
            if ncyc == 0: c = (255, 0, 0)
            if ncyc > 0: c = (0, 0, 255)
            cyc = i % 5
            if cyc == 0: 
                self._lights.set_pixel(pl.PI_ROW_0, cc.OFF)
                self._lights.set_pixel(pl.PI_ROW_1, cc.OFF)
                self._lights.set_pixel(pl.PI_ROW_2, cc.OFF)
                self._lights.set_pixel(pl.PI_ROW_3, cc.OFF)
            if cyc == 1: self._lights.set_pixel(pl.PI_ROW_0, c)
            if cyc == 2: self._lights.set_pixel(pl.PI_ROW_1, c)
            if cyc == 3: self._lights.set_pixel(pl.PI_ROW_2, c)
            if cyc == 4: self._lights.set_pixel(pl.PI_ROW_3, c)
        else:
            # Show number of bonus points.
            self._mode = MODE_ACCUMULATION 
            log("Panic mode changed to ACCUMULATION.")
            n = self._nbonus
            if n >= 24: n = 24 
            for i in range(n):
                if i <= 12: self._lights.set_pixel(pl.BONUS_LEDS[i], cc.RED)
                else:      self._lights.set_pixel(pl.BONUS_LEDS[i - 12], cc.BLUE)
    
    def manage_adding_points(self):
        tnow = time.monotonic() 
        if tnow - self._stage_t0 < 0.200: return 
        self._stage_t0 = tnow 
        self._istage += 1 
        if self._istage < 3: return 
        if self._istage == 3:
            self._sound.play_bonus(self._nbonus) 
            if self._nbonus > 24: 
                extra = self._nbonus - 24 
                points = config.get_points("panic_bonus")
                self._app.add_to_score(extra * points)
                self._nbonus = 24
        if self._nbonus <= 0:
            self.end_panic()
            return
        if self._nbonus > 12:
            ipx = self._nbonus - 12 
            if ipx >= 12: ipx = 12
            if ipx > 0: self._lights.set_pixel(pl.BONUS_LEDS[ipx - 1], cc.RED)
        else:
            ipx = self._nbonus 
            if ipx >= 12: ipx = 12 
            if ipx > 0: self._lights.set_pixel(pl.BONUS_LEDS[ipx - 1], cc.DULL_YELLOW)
        points = config.get_points("panic_bonus")
        self._app.add_to_score(points)
        self._nbonus -= 1

    def add_bonus(self):
        if not self._inpanic: return
        if self._mode != MODE_ACCUMULATION: return
        self._nbonus += 1 
        if self._nbonus > 24: return
        if self._nbonus > 12:
            ipx = self._nbonus - 12 
            if ipx >= 12: ipx = 12
            if ipx > 0: self._lights.set_pixel(pl.BONUS_LEDS[ipx - 1], cc.BLUE)
        else:
            ipx = self._nbonus 
            if ipx >= 12: ipx = 12 
            if ipx > 0: self._lights.set_pixel(pl.BONUS_LEDS[ipx - 1], cc.RED)

    def end_panic(self):
        self._inpanic = False
        self._mode = MODE_PANIC_OFF
        log("Panic mode changed to PANIC_OFF.")
        self._lights.set_lamp_solid(pl.LAMP_PANIC, 0)
        self.set_target_lights()
        self.set_bonus_lights()

    def set_target_lights(self):
        if not self._inpanic: 
            if self._hits == 0: 
                self._lights.set_pixel_blink(pl.PI_TARG_PANIC_1, cc.GREEN, cc.OFF, 8, 8)
                self._lights.set_pixel(pl.PI_TARG_PANIC_2, cc.DULL_GREEN)
            if self._hits == 1:
                 self._lights.set_pixel_blink(pl.PI_TARG_PANIC_1, cc.GREEN, cc.OFF, 8, 8)
                 self._lights.set_pixel(pl.PI_TARG_PANIC_2, cc.RED)
            if self._hits == 2:
                self._lights.set_pixel(pl.PI_TARG_PANIC_1, cc.RED)
                self._lights.set_pixel(pl.PI_TARG_PANIC_2, cc.RED)
            if self._hits == 3:
                self._lights.set_pixel(pl.PI_TARG_PANIC_1, cc.RED)
                self._lights.set_pixel(pl.PI_TARG_PANIC_2, cc.BLUE)
            if self._hits > 3:
                self._lights.set_pixel(pl.PI_TARG_PANIC_1, cc.BLUE)
                self._lights.set_pixel(pl.PI_TARG_PANIC_2, cc.BLUE)
            return
        self._lights.set_pixel_blink(pl.PI_TARG_PANIC_1, cc.GREEN, cc.OFF, 4, 3)
        self._lights.set_pixel_blink(pl.PI_TARG_PANIC_2, cc.WHITE, cc.OFF, 4, 2)

    def panic_hit(self): 
        if not self._inpanic:
            self._hits += 1 
            points = config.get_points("target_panic", 500)
            self._app.add_to_score(points * self._hits)
            self._sound.play(sm.S_DING_TARGET)
            self.set_target_lights()
            return
        log("Panic Target hit durring Panic.")
        self._sound.play(sm.S_WIN_TRUMPET_2)
        self._nbonus += 1
        self._istage = 0 
        self._stage_t0 = time.monotonic()
        self._panic_t0 = time.monotonic() 
        self._mode = MODE_ADDING_POINTS
        log("Panic Mode changed to ADDING_POINTS.")

    def update(self):
        if not self._inpanic: return
        if time.monotonic() - self._panic_t0 > config.get_game_param("panic_time", 20):
            if self._mode != MODE_ADDING_POINTS: 
                log("Panic timed out.")
                self.end_panic()
        if self._mode == MODE_ANOUNCE:
            if time.monotonic() - self._stage_t0 < 1.0: return
            self._mode = MODE_STARTUP_ANAIMATION 
            self._stage_t0 = time.monotonic() - 1 
            self._istage = 0 
            self.manage_startup_lights() 
            return
        if self._mode == MODE_STARTUP_ANAIMATION:
            self.manage_startup_lights() 
            return
        if self._mode == MODE_ACCUMULATION:
            return
        if self._mode == MODE_ADDING_POINTS:
            self.manage_adding_points()
        
    def process_hw_event(self, ev):
        ''' Process hardware events that might impact lanes.'''
        if not self._app.game_active(): return
        if ev == "T5":
            self.panic_hit()
            return
        if not self._inpanic: return
        if ev in ["T1", "T2", "T3", "T4", "T6"]:
            self.add_bonus()
            return
        if ev in ["K1", "K2", "K3", "B1", "B2", "B3"]:
            self.add_bonus()
            return
        if ev in ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10"]:
            self.add_bonus()
            return
            
    

