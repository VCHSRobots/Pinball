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
import lanes 
import targets
import highscore
import ball_manager
import event_manager
import config
import game_logic
import logic_lanes 

secs_per_day = 2.0  # Controls the speed of the build timer

class PinballMachine():
    '''This class manages the entire pinball machine.'''
    def __init__(self):
        pyg.init() 
        self._screen = screen.Screen()
        self._hw = hardware.Hardware() 
        self._sound = sm.SoundManager() 
        self._gl = game_logic.GameLogic(self, self._hw, self._sound)
        self._slights = slights.ScoreBoxLights(self, self._hw, self._sound) 
        self._plights = plights.PlayfieldLights(self, self._hw, self._sound)
        self._flippers = flippers.Flippers(self, self._hw, self._sound)
        self._bumpers = bumpers.Bumpers(self, self._hw, self._sound)
        self._kickers = kickers.Kickers(self, self._hw, self._sound)
        self._lanes = lanes.Lanes(self, self._hw, self._sound)
        self._targets = targets.Targets(self, self._hw, self._sound)
        self._ballmanager = ball_manager.BallManager(self, self._hw, self._flippers)
        self._lane_logic = logic_lanes.LogicLanes(self, self._hw, self._sound, self._plights)
        self._game_events = event_manager.EventManager()
        self._highscore = highscore.get_highscore()
        self._nballs = 0   # Number of balls remaining in game, including ball in play.
        self._game_active = False
        self._prevent_new_game = True
        self._prevent_game_t0 = time.monotonic()
        self._machine_broken = False
        self._errmsg = ""
        self.reset_score()
        self._screen.reset_score()

    def game_active(self):
        return self._game_active

    def prevent_new_game(self):
        self._prevent_game = True
        self.add_game_event("Allow Game", 3.0)

    def add_repeating_game_event(self, event, period, delay=0):
        if type(event) is str: ev = {'name': event}
        else: ev = event 
        self._game_events.add_repeating_event(ev, period, delay)
        log(f"Repeating Game Event Added: {ev['name']} with peiod = {period:0.2f} and delay = {delay:0.2f} secs.")

    def add_game_event(self, event, delay=0):
        ''' Adds a game event to the queue for future processing. 
        The event can be a string, or a map with a name.'''
        if type(event) is str: ev = {'name': event}
        else: ev = event
        self._game_events.add_event(ev, delay) 
        log(f"Game Event Added: {ev['name']} with delay = {delay:0.2f} secs.")

    def process_game_events(self):
        evlist = self._game_events.get_fired_events() 
        for ev in evlist:
            log(f"Game Event Processed: {ev['name']}.")
            if ev["name"] == "Ball Drained": self.on_ball_drained() 
            elif ev["name"] == "Drop Hole Full": self.on_ball_dropped() 
            elif ev["name"] == "Balls Jammed": self.show_warning("Balls Jammed.")
            elif ev["name"] == "Balls Unjammed": pass
            elif ev["name"] == "Clear Warning": self._errmsg = ""
            elif ev["name"] == "Make Report": self.make_reports()
            elif ev["name"] == "Check Highscore": self._highscore = highscore.get_highscore()
            elif ev["name"] == "Allow Game": self._prevent_game = False
            elif ev["name"] == "Eject Drop Ball": self._flippers.eject_drop_ball()
            else: log(f"Game Event {ev['name']} not handled.")

    def make_reports(self):
        self._hw.report_to_log() 

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
        if self._iday == 43: self._sound.play(sm.S_COMPETITION)
        if self._iday == 47: self._sound.play(sm.S_MATCH_START)
        if self._iday == 51: self._sound.play(sm.S_HINT_1)
        if self._iday == 56: self._sound.play(sm.S_HINT_2)
        if self._iday == 60: self._sound.play(sm.S_HINT_3)
        if self._iday == 64: self._sound.play(sm.S_HINT_4)
        if self._iday == 70: 
            if self._score > 2000: self._sound.play(sm.S_SEEDED_1)
            elif self._score > 1000: self._sound.play(sm.S_SEEDED_8)
            elif self._score > 400: self._sound.play(sm.S_SEEDED_47)
            else: self._sound.play(sm.S_NOT_SELECTED)
        if self._iday == 74 and self._score > 5000:
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
        self.reset_score()
        self.show_score("<Initializing>", "Reading Config", "", "")
        config.init_config()
        self.show_score("<Initializing>", "Configuring Hardware", "", "")
        self._slights.queue_startup_cmds()
        self._plights.queue_startup_cmds()
        self._flippers.queue_startup_cmds() 
        self._kickers.queue_startup_cmds()
        self._bumpers.queue_startup_cmds()
        self._lanes.queue_startup_cmds()
        self._targets.queue_startup_cmds()
        t0 = time.monotonic()
        errmsg = self._hw.conduct_startup()
        if errmsg is not None:
            self._machine_broken = True 
            self._errmsg = errmsg
        else:
            self._errmsg = "" 
            self._machine_broken = False
            self._flippers.eject_drop_ball() 
            self._flippers.lift_motor_cycle(4.0)
            self._flippers.disable_flippers() 
            self._bumpers.disable()
            self._kickers.disable()
            for i in range(5): 
                self._hw.update()
                time.sleep(0.1) 
            self.show_score("<Initializing>", "Loading Sounds", "", "")
            self._sound.load_sounds()
            self.show_score("<Initializing>", "Draining Balls", "", "")
            while True:
                self._hw.update()
                telp = time.monotonic() - t0 
                if telp > 6.0: break
        self.reset_score() 
        self.set_game_over(EndingSound=False)
        tperiod = config.get_game_param("report_period", 10)
        self.add_repeating_game_event("Make Report", tperiod)
        tperiod = config.get_game_param("check_highscore_period", 10)
        self.add_repeating_game_event("Check Highscore", tperiod)

    def show_warning(self, txt):
        self._errmsg = txt 
        self._game_events.remove_name("Clear Warning")
        self.add_game_event("Clear Warning", 3.0)
        log(f"Showing Warning: {txt}")

    def reset_score(self):
        self._last_day_change_time = time.monotonic()
        self._score = 0
        self._nballs = 0 
        self._iday = -1
        self._robot_parts = 0 
        self._game_active = False 
        self._highscore = highscore.get_highscore()

    def start_new_game(self):
        log("** Starting New Game.")
        self.reset_score()
        self._slights.on_new_game()
        self._flippers.enable_main_flippers()
        self._flippers.disable_thrid_flipper()
        self._bumpers.enable()
        self._kickers.enable()
        self._plights.on_new_game()
        self._lane_logic.on_new_game()
        self._game_active = True
        self._sound.play(sm.S_MATCH_START)
        self._last_day_change_time = time.monotonic()
        self._flippers.new_ball()
        self._nballs = 3

    def set_game_over(self, EndingSound=True):
        log("** Game Over.")
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

    def monitor_game_start(self):
        ''' Come here to monitor ball situation for starting game.'''
        if self._game_active: return
        okay_to_go = self._ballmanager.balls_ready_to_play() 
        if okay_to_go == True: 
            self._prevent_new_game = False
            self._start_game_warning = False
            return
        telp = time.monotonic() - self._prevent_game_t0 
        if telp > 4.0: 
            # Okay, we have waited over 4 seconds for the old game balls to
            # appear correctly in the trough.  Display warning.
            self.show_warning(okay_to_go)

    def on_ball_drained(self):
        '''Come here when a ball has been detected in the drain hole.'''
        if not self._game_active: return 
        if self._ballmanager.balls_in_play() > 0:
            if self._ballmanager.drop_hole_full(): self._flippers.eject_drop_ball()
            self._game_events.remove_name('Eject Drop Ball')
            return 
        self._nballs -= 1 
        if self._nballs <= 0: 
            self._nballs = 0
            self.set_game_over() 
            return
        self.sound(sm.S_BALL_LOST)
        if not self._machine_broken:
            self._plights.on_ball_drain()
            self._flippers.new_ball() 
            self._slights.on_new_ball()
            self._plights.on_new_ball()

    def on_ball_dropped(self):
        ''' Come here to process when a ball has been detected in the drop hole.'''
        if not self._game_active:
            self._flippers.eject_drop_ball()
            return
        self.sound(sm.S_DING_DROPHOLE)
        hold_time = config.get_game_param("drop_ball_hold", 15)
        self.add_game_event({'name': 'Eject Drop Ball'}, hold_time)
        self.add_to_score(1000)
        self._flippers.new_ball()
        self._slights.on_drop_hole()
        self._plights.on_drop_hole()

    def sound(self, id):
        if self._game_active:
            self._sound.play(id)

    def process_hardware_events(self):
        ''' Process hardware events -- mostly switch closures.  Note that events
        associated with the ball trough and drop hole (F4-F8) are handled in
        ball_manager.py instead of here.'''
        events = self._hw.get_events()
        for e in events:
            log(f"Event: {e}")
            self._lane_logic.process_hw_event(e)
            if e == "F1": # Right Flipper Button
                self.add_to_score(1) 
            if e == "F2": # Left Flipper Button
                self.add_to_score(1)
            if e == "F3": # Start Button
                if self._game_active: 
                    # Shortcut to spinning the lift motor some more.
                    self._flippers.lift_motor_cycle(1.5)
                    continue
                if self._prevent_new_game: 
                    log("Rejecting new game request.")
                    continue 
                self.start_new_game()
                return 
            if e in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]: 
                self.add_to_robot_parts()
                self.add_to_score(100) 
                self.sound(sm.S_DING_TARGET)
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
                    
    def show_score(self, gp=None, g1=None, g2=None, g3=None):
        self._screen.score().main_score = self._score
        self._screen.score().high_score = self._highscore
        self._screen.score().day = self._iday
        self._screen.score().number_of_balls = self._nballs
        if gp is None: gp, g1, g2, g3 = self.get_game_phase_text()
        self._screen.score().game_phase = gp
        self._screen.score().game_hint1 = g1
        self._screen.score().game_hint2 = g2
        self._screen.score().game_hint3 = g3
        self._screen.score().robot_parts = self._robot_parts
        self._screen.score().err_msg = self._errmsg
        self._screen.score().out_of_order = False
        if self._machine_broken:
            self._screen.score().out_of_order = True 
            self._screen.score().game_phase = "Out of Order"
            self._screen.score().game_hint1 = "Machine needs"
            self._screen.score().game_hint2 = "service."
            self._screen.score().game_hint3 = ""
        self._screen.update()

    def run(self):
        self.reset_machine()
        while(True):   # This is the Main Loop for the Game
            pyg.event.pump()
            for e in pyg.event.get():
                if e.type == pyg.QUIT or (e.type == pyg.KEYUP and e.key == pyg.K_ESCAPE): 
                    pyg.quit()
                    return 
                if e.type == pyg.KEYUP:
                    self._hw.simulate(e.key)
            if not self._machine_broken:
                self._hw.update()
                self._slights.update()
                self._plights.update()
                self._flippers.update()
                self._kickers.update()
                self._bumpers.update()
                self._lanes.update()
                self._targets.update()
                self.advance_calendar()
                self._ballmanager.update()
                self.process_hardware_events()
                self.monitor_game_start()
            self.process_game_events()
            self.show_score()

if __name__ == "__main__":
    pb_log.log_init() 
    # For production code, remove the comments below.
    pb_log.disable_terminal()
    pb_log.disable_debug()
    log("")
    log("Starting Pinball Game ONE.")
    log("")
    if common.platform() == "real":
        log("Running on the actual pinball machine hardware.")
        log(f"Active Nodes = {config.get_active_nodes()}")
    else:
        log("Running in simulation mode.")
    pbmachine = PinballMachine()
    pbmachine.run()
    log("Exiting Without Error.")
