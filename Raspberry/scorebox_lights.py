# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Score Box Lights Handler

from pb_log import log
import hardware 
import event_manager

class ScoreBoxLights():
    ''' Takes care of score box lights'''

    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_PLIGHTS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def update(self):
        '''Processes internal events pertaining to the score box lights.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            if ev['cmd'] == "game_mode":
                name = ev["cmd_name"]
                log("Executing queued command in ScoreBox Lights: {name}") 
                self.on_game_mode()
            if ev['cmd'] == "wait_mode":
                name = ev["cmd_name"]
                log("Executing queued command in ScoreBox Lights: {name}") 
                self.on_wait_mode()

    def on_game_mode(self):
        '''Normal name mode: Fast Wipe'''
        cmd = [4, 0, 255, 0, 0, 0, 0, 1] # NEO_WIPE green/black 25ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoWipe green/black 25ms.")
        cmd = [10, 0b00101010, 0, 200, 50]
        self._hw.send_command(self._nodeadr, cmd) 
        cmd = [10, 0b00010101, 0, 200, 60]
        self._hw.send_command(self._nodeadr, cmd) 
        log("SBox Lamps: modulate quickly")

    def on_wait_mode(self):
        '''Normal name mode: Fast Wipe'''
        cmd = [7] # NEO_DEMO 
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox NeoPixels: NeoDemo")
        cmd = [10, 0b00101010, 0, 200, 255]
        self._hw.send_command(self._nodeadr, cmd) 
        cmd = [10, 0b00010101, 0, 200, 235]
        self._hw.send_command(self._nodeadr, cmd) 
        log("SBox Lamps: modulate slowly")  

    def on_game_over(self):
        '''All Red for 15 seconds, Lamps off.'''
        cmd = [3, 255, 0, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: all red.")
        ev = {'cmd': "wait_mode", 'cmd_name': "Wait Mode Lights"}
        self._queue.add_event(ev, 15.0)

    def on_new_game(self):
        '''Twinkle white for 5 second, then demo'''
        self._queue.clear_events()
        cmd = [6, 255, 255, 255, 0, 0, 0, 2, 2, 2]  # NEO_BLINK white/black 2-piels, 50ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoBlink white/black, 2px/2px, 50ms")
        cmd = [8, 0x3F, 255] 
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Lamps: all on")
        ev = {'cmd': "game_mode", 'cmd_name': "Game Mode Lights"}
        self._queue.add_event(ev, 5.0)

    def on_new_ball(self):
        '''Twinkle blue for 5 seconds, Flash Lamps'''
        self._queue.clear_events()
        cmd = [6, 0, 0, 255, 255, 0, 0, 3, 3, 2]  # NEO_BLINK blue/red 3-piels, 50ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoBlink blue/red, 3px/3px, 50ms")
        cmd = [8, 0x3F, 255] 
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Lamps: all on")
        ev = {'cmd': "game_mode", 'cmd_name': "Game Mode Lights"}
        self._queue.add_event(ev, 5.0)

    def on_drop_hole(self):
        ''' Flash Lamps, wwenkle green'''
        pass

    def on_panic(self):
        ''' Twenkle Red/White for 10 seconds'''
        pass
