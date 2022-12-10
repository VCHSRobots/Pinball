# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Score Box Lights Handler

from pb_log import log
import hardware 
import event_manager

CMD_NEO_RESET     =  1
CMD_NEO_SINGLE    =  2
CMD_NEO_SOLID     =  3
CMD_NEO_WIPE      =  4
CMD_NEO_CHASE     =  5
CMD_NEO_BLINK     =  6
CMD_NEO_DEMO      =  7
CMD_LAMP_SOLID    =  8
CMD_LAMP_FLASH    =  9
CMD_LAMP_MODULATE = 10

class ScoreBoxLights():
    ''' Takes care of score box lights'''

    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_BLIGHTS 
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        pass

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
        cmd = [CMD_NEO_WIPE, 0, 255, 0, 0, 0, 0, 1] # NEO_WIPE green/black 25ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoWipe green/black 25ms.")
        cmd = [CMD_LAMP_MODULATE, 0b00101010, 0, 200, 50]
        self._hw.send_command(self._nodeadr, cmd) 
        cmd = [CMD_LAMP_MODULATE, 0b00010101, 0, 200, 60]
        self._hw.send_command(self._nodeadr, cmd) 
        log("SBox Lamps: modulate quickly")

    def on_wait_mode(self):
        '''Normal name mode: Fast Wipe'''
        cmd = [CMD_NEO_DEMO] 
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox NeoPixels: NeoDemo")
        cmd = [CMD_LAMP_MODULATE, 0b00101010, 0, 200, 255]
        self._hw.send_command(self._nodeadr, cmd) 
        cmd = [CMD_LAMP_MODULATE, 0b00010101, 0, 200, 235]
        self._hw.send_command(self._nodeadr, cmd) 
        log("SBox Lamps: modulate slowly")  

    def on_game_over(self):
        '''All Red for 15 seconds, Lamps off.'''
        cmd = [CMD_NEO_SOLID, 255, 0, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: all red.")
        ev = {'cmd': "wait_mode", 'cmd_name': "Wait Mode Lights"}
        self._queue.add_event(ev, 15.0)

    def on_new_game(self):
        '''Twinkle white for 5 second, then demo'''
        self._queue.clear_events()
        cmd = [CMD_NEO_BLINK, 255, 255, 255, 0, 0, 0, 2, 2, 2]  # NEO_BLINK white/black 2-piels, 50ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoBlink white/black, 2px/2px, 50ms")
        cmd = [CMD_LAMP_SOLID, 0x3F, 255] 
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Lamps: all on")
        ev = {'cmd': "game_mode", 'cmd_name': "Game Mode Lights"}
        self._queue.add_event(ev, 5.0)

    def on_new_ball(self):
        '''Twinkle blue for 5 seconds, Flash Lamps'''
        self._queue.clear_events()
        cmd = [CMD_NEO_BLINK, 0, 0, 255, 255, 0, 0, 3, 3, 2]  # NEO_BLINK blue/red 3-piels, 50ms period
        self._hw.send_command(self._nodeadr, cmd)
        log("SBox Ligths: NeoBlink blue/red, 3px/3px, 50ms")
        cmd = [CMD_LAMP_SOLID, 0x3F, 255] 
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
