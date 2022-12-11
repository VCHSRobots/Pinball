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
        '''Adds an event to the quene.  The event should be a dict. Delay is in seconds.'''
        if type(ev) is str: ev = {'name': ev}
        tfire = time.monotonic() + delay 
        ev["tfire"] = tfire
        self._cmd_queue.insert(0, ev)

    def add_repeating_event(self, ev, period=1, delay=0):
        '''Adds a repeating event to the queue.  The event should be a dict. Period and
        Delay are in seconds.  Delay is how long before the first time the event is fired,
        and then it is fired every period afterwards.'''
        tfire = time.monotonic() + delay 
        ev['tfire'] = tfire
        ev['tperiod'] = period 
        self._cmd_queue.insert(0, ev)

    def get_fired_events(self):
        ''' Returns a list of events that have fired (i.e., are ready to be processed).'''
        evout = [] 
        saved_events = []
        tnow = time.monotonic()
        while(len(self._cmd_queue) > 0):
            ev = self._cmd_queue.pop()
            if tnow > ev["tfire"]: 
                evout.insert(0, ev)
                if 'tperiod' in ev:
                    ev['tfire'] = time.monotonic() + ev['tperiod']
                    saved_events.insert(0, ev)
            else: saved_events.insert(0, ev) 
        self._cmd_queue = saved_events 
        return evout

    def clear_events(self):
        ''' Clears entire queue.'''
        self._cmd_queue = [] 

    def remove_name(self, name):
        ''' Removes all events with the given name.'''
        new_list = []
        for ev in self._cmd_queue:
            if 'name' in ev:
                if ev['name'] == name: continue
            new_list.insert(0, ev) 
        self._cmd_queue = new_list

    def remove_category(self, category):
        ''' Remvoves all events with a given category. '''
        new_list = []
        for ev in self._cmd_queue:
            if 'category' in ev:
                if ev['category'] == category: continue
            new_list.insert(0, ev) 
        self._cmd_queue = new_list     

    

