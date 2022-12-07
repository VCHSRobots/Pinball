# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Bumpers Node handler

from pb_log import log
import hardware 
import event_manager

class Kickers():
    ''' Takes care of stuff with the kickers's node'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_KICKERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the kickers'''
        pass

    def update(self):
        '''Processes internal events pertaining to the kickers.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            self._hw.send_command(self._nodeadr, ev['cmd'])
            if "cmd_name" in ev: name = ev['cmd_name']
            else: name = ""
            log(f"Sending Queued Command from Bumpers: {name}")

    def disable(self):
        cmd = [21, 0xFF, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Disabling all Coils")
        cmd = [23, 0xFF, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Disabling all Lamps")

    def enable(self):
        cmd = [21, 0xFF, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Enabling all Coils")
        cmd = [23, 0xFF, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Kickers: Enabling all Lamps")