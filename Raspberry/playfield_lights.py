# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Playfield Lights Handler

from pb_log import log
import hardware 
import event_manager


CMD_NEO_RESET     =   1
CMD_NEO_SINGLE    =   2
CMD_NEO_SOLID     =   3
CMD_NEO_WIPE      =   4
CMD_NEO_CHASE     =   5
CMD_NEO_BLINK     =   6
CMD_NEO_DEMO      =   7
CMD_LAMP_SOLID    =   8
CMD_LAMP_FLASH    =   9
CMD_LAMP_MODULATE =  10

class PlayfieldLights():
    ''' Takes care of play field lights.'''
   
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_PLIGHTS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        pass

    def update(self):
        pass
        # '''Processes internal events pertaining to the score box lights.'''
        # events = self._queue.get_fired_events() 
        # for ev in events:
        #     if ev['cmd'] == "game_mode":
        #         name = ev["cmd_name"]
        #         log("Executing queued command in ScoreBox Lights: {name}") 
        #         self.on_game_mode()
        #     if ev['cmd'] == "wait_mode":
        #         name = ev["cmd_name"]
        #         log("Executing queued command in ScoreBox Lights: {name}") 
        #         self.on_wait_mode()

    def on_game_mode(self):
        pass

    def on_wait_mode(self):
        pass

    def on_game_over(self):
        pass
   
    def on_new_game(self):
        pass

    def on_new_ball(self):
        pass

    def on_drop_hole(self):
        pass

    def on_panic(self):
        pass
