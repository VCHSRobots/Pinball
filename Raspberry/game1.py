# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# "Game1" -- First program to conduct a complete game.

import time
import pygame as pyg
import common 
import pb_log
from pb_log import log, logd 
import screen 
import hardware 
import sound_manager as sm
import scorebox_lights as slights 
import playfield_lights as plights
import flippers
import bumpers
import kickers
import highscore

secs_per_day = 2.5  # Controls the speed of the build timer

class PinballMachine():
    '''This class manages the entire pinball machine.'''
    def __init__(self):
        pyg.init() 
        self._screen = screen.Screen()
        self._hw = hardware.Hardware() 
        self._sound = sm.SoundManager() 
        self._slights = slights.ScoreBoxLights(self, self._hw, self._sound) 
        self._plights = plights.PlayfieldLights(self, self._hw, self._sound)
        self._flippers = flippers.Flippers(self, self._hw, self._sound)
        self._bumpers = bumpers.Bumpers(self, self._hw, self._sound)
        self._kickers = kickers.Kickers(self, self._hw, self._sound)
        self._highscore = highscore.get_highscore()
        self._nballs = 0   # Number of balls remaining in game, including ball in play.
        self._nballs_on_field = 0  # Number of balls on the playing field.
        self._game_active = False
        self._drop_ball_pending = False
        self._drop_ball_t0 = time.monotonic()
        self._prevent_new_game = True
        self._prevent_game_t0 = time.monotonic()
        self._last_report_t0 = time.monotonic()
        self.reset_score()
        self._screen.reset_score()

    def get_game_phase_text(self):
        if not self._game_active: return("<Game Over>", "Press Start for", "a new game", "")
        if (self._iday <  3): return ("Debut", "Learn the Game", "with Jet Bumpers!", "")
        if (self._iday < 10): return ("6 Build Weeks", "Design your robot", "at the top lanes", "")
        if (self._iday < 17): return ("5 Build Weeks", "Build your robot", "by hitting the EPIC", "targets!")
        if (self._iday < 24): return ("4 Build Weeks", "Build your robot", "by using the ramp!", "Hurry!")
        if (self._iday < 31): return ("3 Build Weeks", "Make a better bot", "by hitting EPIC", "targets in order!")
        if (self._iday < 38): return ("2 Build Weeks", "Continue to build", "by hitting targets!", "Hurry, Hurry!")
        if (self._iday < 45): return ("1 Build Weeks", "Finsh your Robot", "by using the Jet Bumpers!", "")
        if (self._iday < 52): return ("Building Done", "Test your Robot", "at the drop hole.", "")
        if (self._iday < 59): return ("Competition!", "Use the Ramp", "to get to competition!", "")
        if (self._iday < 66): return ("Scouting!", "Go Scouting at", "the Jet Bumpers!", "")
        if (self._iday < 73): return ("Get Ranked!", "Get ranked by", "using the lanes", "and hitting targets!")
        if (self._iday < 80): return ("Finals!", "Hit all Targets", "to win finals match", "and go to CHAMPS!")
        return ("CHAMPS!", "Do all you can!", "Smash everything!", "Push, push!")
    
    def play_day_sound(self):
        if self._iday ==  1: self._sound.play(sm.S_BUILD_0)
        if self._iday ==  3: self._sound.play(sm.S_BUILD_6)
        if self._iday ==  6: self._sound.play(sm.S_HINT_0)
        if self._iday == 10: self._sound.play(sm.S_BUILD_5)
        if self._iday == 17: self._sound.play(sm.S_BUILD_4)
        if self._iday == 24: self._sound.play(sm.S_BUILD_3)
        if self._iday == 31: self._sound.play(sm.S_BUILD_2)
        if self._iday == 38: self._sound.play(sm.S_BUILD_1)
        if self._iday == 39 and self._score < 200: self._sound.play(sm.S_PANIC_5)
        if self._iday == 40: self._sound.play(sm.S_COMPETITION)
        if self._iday == 43: self._sound.play(sm.S_MATCH_START)
        if self._iday == 46: self._sound.play(sm.S_HINT_1)
        if self._iday == 49: self._sound.play(sm.S_HINT_2)
        if self._iday == 51: self._sound.play(sm.S_HINT_3)
        if self._iday == 54: self._sound.play(sm.S_HINT_4)
        if self._iday == 57: 
            if self._score > 2000: self._sound.play(sm.S_SEEDED_1)
            elif self._score > 1000: self._sound.play(sm.S_SEEDED_8)
            elif self._score > 400: self._sound.play(sm.S_SEEDED_47)
            else: self._sound.play(sm.S_NOT_SELECTED)
        if self._iday == 60 and self._score > 5000:
            self._sound.play(sm.S_PLAYOFFS)

    def advance_calendar(self):
        if not self._game_active: return
        tnow = time.monotonic() 
        telp = tnow - self._last_day_change_time
        if(telp > secs_per_day):
            self._last_day_change_time = tnow 
            self._iday += 1 
            if self._iday > 90: self._iday = 90
            self.play_day_sound()

    def reset_machine(self):
        self._flippers.eject_drop_ball() 
        self._flippers.disable_flippers() 
        self._bumpers.disable()
        self._kickers.disable()
        time.sleep(5) # wait for ball to drain

    def reset_score(self):
        self._last_day_change_time = time.monotonic()
        self._score = 0
        self._nballs = 0 
        self._nballs_on_field = 0
        self._iday = -1
        self._robot_parts = 0 
        self._game_active = False 
        self._highscore = highscore.get_highscore()

    def start_new_game(self):
        log("Setting State to New Game.")
        self.reset_score()
        self._slights.on_new_game()
        self._flippers.enable_main_flippers()
        self._flippers.disable_thrid_flipper()
        self._bumpers.enable()
        self._kickers.enable()
        self._game_active = True
        self._sound.play(sm.S_MATCH_START)
        self._last_day_change_time = time.monotonic()
        self._flippers.new_ball()
        self._nballs = 3
        self._nballs_on_field = 1

    def set_game_over(self, EndingSound=True):
        log("Setting State to Game Over.")
        self._highscore = highscore.get_highscore()
        if self._score > self._highscore: 
            log(f"Setting new highscore: {self._highscore} -> {self._score}")
            self._highscore = self._score 
            okay = highscore.save_highscore(self._score) 
            if not okay: log(f"Unable to save highscore.")
        if EndingSound: self.sound(sm.S_MATCH_END)
        self._game_active = False
        self._slights.on_game_over()
        self._plights.on_game_over()
        self._flippers.eject_drop_ball()
        self._flippers.disable_flippers()
        self._bumpers.disable()
        self._kickers.disable()
        self._prevent_new_game = True 
        self._prevent_game_t0 = time.monotonic()

    def add_to_score(self, val):
        if self._nballs > 0 and self._game_active:
            self._score += val

    def add_to_robot_parts(self):
        if self._nballs > 0 and self._game_active:
            self._robot_parts += 1 
            log(f"Adding to Robot Parts. Current count: {self._robot_parts}")

    def eject_dropball(self):
        self._flippers.eject_drop_ball() 
        self._drop_ball_pending = False

    def manage_dropball(self):
        if self._drop_ball_pending:
            tnow = time.monotonic()
            if tnow - self._drop_ball_t0 < 20: return 
            self.eject_dropball()

    def ball_drained(self):
        '''Come here when a ball has been detected in the drain hole.'''
        if not self._game_active: return 
        self._nballs_on_field -= 1 
        if self._nballs_on_field > 0:
            if self._flippers.ball_in_hole():
                self.eject_dropball() 
            return 
        if self._nballs_on_field < 0: self._nballs_on_field = 0
        self._nballs -= 1 
        if self._nballs <= 0:
            self._nballs = 0 
            self.set_game_over() 
            return
        self.sound(sm.S_REDCARD)
        self._flippers.new_ball() 
        self._nballs_on_field += 1
        self._slights.on_new_ball()
        self._plights.on_new_ball()

    def sound(self, id):
        if self._game_active:
            self._sound.play(id)

    def process_hardware_events(self):
        events = self._hw.get_events()
        for e in events:
            log(f"Event: {e}")
            if e == "F3": # restart
                if self._game_active: 
                    # Shortcut to spinning the lift motor some more.
                    self._flippers.lift_motor_cycle(1.5)
                    continue
                if self._prevent_new_game and time.monotonic() - self._prevent_game_t0 < 2.0: continue 
                self._prevent_new_game = False
                self.start_new_game()
                return 
            if e in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]: 
                self.add_to_robot_parts()
                self.add_to_score(100) 
                self.sound(sm.S_DING_TARGET)
            if e in ["F1", "F2"]:
                self.add_to_score(1) 
            if e in ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"]:
                self.sound(sm.S_DING_LANE)
            if e in ["L1"]:
                self.add_to_score(10) 
            if e in ["L2", "L3", "L4"]:
                self.add_to_score(50) 
            if e in ["L5"]:
                self.add_to_score(150) 
                self._flippers.enable_thrid_flipper()
            if e in ["L8", "L9"]:
                self.add_to_score(25) 
            if e in ["K1", "K2", "K3"]:
                self.add_to_score(25) 
                self.sound(sm.S_DING_KICKER)
            if e in ["B1", "B2", "B3"]:
                self.add_to_score(50) 
                self.sound(sm.S_DING_JET_BUMPERS)
            if e in ["F7"]:
                self.ball_drained()
            if e in ["F8"]:
                self.sound(sm.S_DING_TARGET)
                self._drop_ball_pending = True 
                self._drop_ball_t0 = time.monotonic()
                self.add_to_score(1000)
                self._nballs_on_field += 1
                self._flippers.new_ball()
                self._slights.on_drop_hole()
                self._plights.on_drop_hole()
                    
    def show_score(self):
        self._screen.score().main_score = self._score
        self._screen.score().high_score = self._highscore
        self._screen.score().day = self._iday
        self._screen.score().number_of_balls = self._nballs
        gp, g1, g2, g3 = self.get_game_phase_text()
        self._screen.score().game_phase = gp
        self._screen.score().game_hint1 = g1
        self._screen.score().game_hint2 = g2
        self._screen.score().game_hint3 = g3
        self._screen.score().robot_parts = self._robot_parts
        self._screen.update()

    def make_reports(self):
        tnow = time.monotonic()
        if tnow - self._last_report_t0 < 10.0: return
        self._highscore = highscore.get_highscore()  # Kluge -- change this to somesore of notification sys
        self._last_report_t0 = tnow 
        self._hw.report_to_log() 

    def run(self):
        self.reset_score() 
        self.set_game_over(EndingSound=False)
        while(True):   # This is the Main Loop for the Game
            #time.sleep(0.1)
            self._hw.update() 
            pyg.event.pump()
            self._slights.update()
            self._plights.update()
            self._flippers.update()
            self._kickers.update()
            self._bumpers.update()
            for e in pyg.event.get():
                if e.type == pyg.QUIT or (e.type == pyg.KEYUP and e.key == pyg.K_ESCAPE): 
                    pyg.quit()
                    return 
                if e.type == pyg.KEYUP:
                    self._hw.simulate(e.key)
            self.advance_calendar()
            self.process_hardware_events()
            self.manage_dropball()
            self.show_score()
            self.make_reports()

if __name__ == "__main__":
    pb_log.log_init() 
    # For production code, remove the comments below.
    pb_log.disable_terminal()
    pb_log.disable_debug()
    log("")
    log("Starting Game One.")
    log("")
    if common.platform() == "real":
        log("Running on the actual pinball machine hardware.")
    else:
        log("Running in simulation mode.")
    pbmachine = PinballMachine()
    pbmachine.run()
    log("Exiting Without Error.")
