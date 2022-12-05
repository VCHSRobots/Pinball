# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Bumpers Node handler

from pb_log import log
import hardware 
import event_manager

class Bumpers():
    ''' Takes care of stuff with the bumpers's node'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_BUMPERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the bumpers'''
        pass

    def update(self):
        '''Processes internal events pertaining to the bumpers.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            self._hw.send_command(self._nodeadr, ev['cmd'])

    def disable(self):
        cmd = [21, 0xFF, 0]
        self._hw.send_command(self._nodeadr, cmd)
        cmd = [23, 0xFF, 0]
        self._hw.send_command(self._nodeadr, cmd)

    def enable(self):
        cmd = [21, 0xFF, 1]
        self._hw.send_command(self._nodeadr, cmd)
        cmd = [23, 0xFF, 1]
        self._hw.send_command(self._nodeadr, cmd)
       
