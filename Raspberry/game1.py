# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# "Game1" -- First program to conduct a complete game.

import time
import pygame as pyg
import common 
if common.platform() == "real":
    import comm_bus
    comm = comm_bus.CommBus()
else:
    comm = None
import pb_log
from pb_log import log, logd 
import screen 

class PinballMachine():
    '''This class manages the entire pinball machine.'''
    def __init__(self):
        pyg.init() 
        self._screen = screen.Screen()
        self._screen.reset_score()
        if comm is not None:
            comm.begin()

    def get_game_phase_text(self, day):
        if (day < 3): return ("Debut", "Learn the Game", "at the top Lanes", "")
        if (day < 14): return ("Build Week 1", "Design your robot", "at the Jet Bumpers!", "")
        if (day < 21): return ("Build Week 2", "Build your robot", "by hitting the EPIC", "targets!")
        if (day < 28): return ("Build Week 3", "Build your robot", "by using the ramp!", "Hurry!")
        if (day < 35): return ("Build Week 4", "Make a better bot", "by hitting EPIC", "targets in order!")
        if (day < 42): return ("Build Week 5", "Continue to build", "by hitting targets!", "Hurry, Hurry!")
        if (day < 49): return ("Build Week 6", "Finsh your Robot", "by using the Jet Bumpers!", "")
        if (day < 56): return ("Build Week 7", "Test your Robot", "at the drop hole.", "")
        if (day < 63): return ("Competition!", "Use the Ramp", "to get to competition!", "")
        if (day < 70): return ("Scouting!", "Go Scouting at", "the Jet Bumpers!", "")
        if (day < 75): return ("Get Ranked!", "Get ranked by", "using the lanes", "and hitting targets!")
        if (day < 80): return ("Finals!", "Hit all Targets", "to win finals match", "and go to CHAMPS!")
        return ("CHAMPS!", "Do all you can!", "Smash everything!", "Push, push!")

    def run(self):
        cntr = 0  
        while(True):   # This is the Main Loop for the Game
            time.sleep(0.1)
            pyg.event.pump()
            for e in pyg.event.get():
                if e.type == pyg.QUIT or (e.type == pyg.KEYUP and e.key == pyg.K_ESCAPE): 
                    pyg.quit()
                    return 
            cntr += 1
            self._screen.score().main_score = cntr
            if cntr % 10 == 0:
                self._screen.score().day += 1
                if self._screen.score().day > 90:  self._screen.score().day = -6
                self._screen.score().number_of_balls = 2
                gp, g1, g2, g3 = self.get_game_phase_text(self._screen.score().day)
                self._screen.score().game_phase = gp
                self._screen.score().game_hint1 = g1
                self._screen.score().game_hint2 = g2
                self._screen.score().game_hint3 = g3
                self._screen.score().robot_parts += 1 
                if self._screen.score().robot_parts > 8: self._screen.score().robot_parts = 0
            self._screen.update()

if __name__ == "__main__":
    pb_log.log_init() 
    # For production code, remove the comments below.
    # pb_log.disable_terminal();
    # pb_log.disable_debug();
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
