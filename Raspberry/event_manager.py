# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# game_even_manager.py
#
# Manages a queue of events that can be delayed.
#

import time 

class EventManager():

    def __init__(self):
        self._cmd_queue = []

    def add_event(self, ev, delay=0):
        '''Adds an event to the quene.  The event should be a map. Delay is in seconds.'''
        tfire = time.monotonic() + delay 
        ev["tfire"] = tfire
        self._cmd_queue.insert(0, ev)

    def get_fired_events(self):
        evout = [] 
        saved_events = []
        tnow = time.monotonic()
        while(len(self._cmd_queue) > 0):
            ev = self._cmd_queue.pop()
            if tnow > ev["tfire"]: evout.insert(0, ev)
            else: saved_events.insert(0, ev) 
        self._cmd_queue = saved_events 
        return evout

    def clear_events(self):
        self._cmd_queue = [] 

