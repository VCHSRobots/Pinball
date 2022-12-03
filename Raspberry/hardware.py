# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# hardward.py -- interface to the pinball machine hardware
#
# Events:
# Events are mostly only switch closures.  These are nameed as follows
#  L1 - L16 : Lane swiches
#  T1 - T16 : Target switches
#  F1 - F8  : Flipper switches
#  B1 - B3  : Jet Bummpers
#  K1 - K3  : Kickers  
# 
# States:
# Switch states can also be returned.  These are simply bitmaps, where each
# bit coresponds to a single switch.
# 

import time
import threading 
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

nodes = {2: {'name': "S Lts",  "nsw":  0, "ibs": 0, "designator":'S'},
         3: {'name': "P Lts",  "nsw":  0, "ibs": 0, "designator":'P'},
         4: {'name': "Flprs",  "nsw":  8, "ibs": 1, "designator":'F'}, 
         5: {'name': "Bmprs",  "nsw":  3, "ibs": 1, "designator":'B'},
         6: {'name': "Kckrs",  "nsw":  3, "ibs": 1, "designator":'K'},
         7: {'name': "Lanes",  "nsw": 11, "ibs": 2, "designator":'L'},
         8: {'name': "Targs",  "nsw":  8, "ibs": 2, "designator":'T'} }
    #    9: {'name': "Test ",  "nsw":  0, "ibs": 1} }

class Node():
    def __init__(self, node_addr):
        self._node_addr = node_addr
        self._name = nodes[node_addr]['name']
        self._nsw = nodes[node_addr]['nsw']
        self._ibs = nodes[node_addr]['ibs']
        self._designator = nodes[node_addr]['designator']
        self._active = False 
        self._reported_cmd_cnt = 0 
        self._reported_err_cnt = 0 
        self._response_errs = 0
        self._have_init_counts = False 
        self._sw_counts = []
        self._sw_state = 0
        self._last_comm_attemp_time = 0
        self._last_comm_success_time = 0
        for i in range(self._nsw): self._sw_counts.append(0)

    def _split_bytes(self, dat):
        idat = [] 
        for x in dat:
            idat.append(x & 0x000F) 
            idat.append((x >> 4) & 0x000F)
        return idat

    def get_switch_state(self):
        return self._sw_state

    def update(self):
        ''' Update the node, and return any new events.'''
        if comm is None: return []
        if not self._active:
            if self._last_comm_success_time == 0: twait = 5 
            else: twait = 1.5 
            telp = time.monotonic() - self._last_comm_attemp_time
            if telp < twait: return [] 
        rsp = comm.node_io(self._node_addr)
        self._last_comm_attemp_time = time.monotonic()
        if rsp == None: 
            telp = time.monotonic() - self._last_comm_success_time
            if telp > 3.00:
                self._active = False 
            return []
        self._last_comm_success = time.monotonic() 
        self._active = True
        if self._ibs == 0: return []
        nb, ib0, ib1 = 1, 3, 4
        if self._ibs == 2: 
            nb, ib0, ib1 = 2, 3, 5
        nswb = int(self._nsw / 2) 
        if self._nsw % 2 != 0: nswb += 1  
        if len(rsp) < 3 + nb + nswb:
            self._response_errs += 1      
            return []
        if self._ibs > 1: 
            self._sw_state = (rsp[ib0 + 1] << 8) | rsp[ib0]
        else:
            self._sw_state = rsp[ib0]
        temp_cnts = self._split_bytes(rsp[ib1:ib1+nswb])
        if not self._have_init_counts:
            self._have_init_counts = True 
            for i in range(self._nsw):
                self._sw_counts[i] = temp_cnts[i]
            return [] 
        # Generate new events, save the counts.
        events = [] 
        for i in range(self._nsw):
            cnt = (temp_cnts[i] & 0x000F) - (self._sw_counts[i] & 0x000F) 
            self._sw_counts[i] = temp_cnts[i] 
            if cnt < 0: cnt += 16
            for j in range(cnt):
                event_name = self._designator + f"{i+1}"
                events.append(event_name)
        return events

class Hardware():
    def __init__(self):
        if comm is not None: comm.begin()
        self._event_lock = threading.Lock() 
        self._cmd_queue_lock = threading.Lock()
        self._nodes = {}
        for node_adr in nodes:
            self._nodes[node_adr] = Node(node_adr)
        self._events = [] 

    def update(self):
        events = [] 
        for node_adr in self._nodes:
            temp_events = self._nodes[node_adr].update()
            events.extend(temp_events)
        self._event_lock.acquire() 
        self._events.extend(events)
        self._event_lock.release() 

    def get_events(self):
        '''Returns a list of new events since last call.'''
        self._event_lock.acquire() 
        xout = self._events
        self._events = []
        self._event_lock.release() 
        return xout

    def get_switch_state(self, node_addr):
        '''Returns a bitmap of the switches for a given node'''
        if node_addr in self._nodes:
            return self._nodes[node_addr].get_switch_state()
        else: return 0
        
if __name__ == "__main__":
    pb_log.disable_debug()
    pb_log.disable_terminal()
    hw = Hardware() 
    while(True):
        hw.update() 
        events = hw.get_events()
        for e in events:
            print(e)
        

