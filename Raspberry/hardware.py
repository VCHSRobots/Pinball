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
import config

NODE_BLIGHTS  = 2
NODE_PLIGHTS  = 3
NODE_FLIPPERS = 4
NODE_BUMPERS  = 5
NODE_KICKERS  = 6
NODE_LANES    = 7
NODE_TARGETS  = 8
NODE_TEST     = 9

nodes = {NODE_BLIGHTS:  {'name': "S Lts",  "nsw":  0, "ibs": 0, "designator":'S'},
         NODE_PLIGHTS:  {'name': "P Lts",  "nsw":  0, "ibs": 0, "designator":'P'},
         NODE_FLIPPERS: {'name': "Flprs",  "nsw":  8, "ibs": 1, "designator":'F'}, 
         NODE_BUMPERS:  {'name': "Bmprs",  "nsw":  3, "ibs": 1, "designator":'B'},
         NODE_KICKERS:  {'name': "Kckrs",  "nsw":  3, "ibs": 1, "designator":'K'},
         NODE_LANES:    {'name': "Lanes",  "nsw": 11, "ibs": 2, "designator":'L'},
         NODE_TARGETS:  {'name': "Targs",  "nsw":  8, "ibs": 2, "designator":'T'} }
    #    NODE_TEST:     {'name': "Test ",  "nsw":  0, "ibs": 1} }

completed_cmds = []
dropped_cmds = []
last_cmd_id = 0

class Node():
    def __init__(self, node_addr):
        self._node_addr = node_addr
        self._name = nodes[node_addr]['name']
        self._nsw = nodes[node_addr]['nsw']
        self._ibs = nodes[node_addr]['ibs']
        self._designator = nodes[node_addr]['designator']
        self._active = True 
        self._reported_cmd_cnt = 0 
        self._reported_err_cnt = 0 
        self._response_errs = 0
        self._have_init_counts = False 
        self._sw_counts = []
        self._sw_state = 0
        self._last_comm_attemp_time = 0
        self._last_comm_success_time = time.monotonic()
        self._cmd_queue = [] 
        for i in range(self._nsw): self._sw_counts.append(0)

    def _split_bytes(self, dat):
        idat = [] 
        for x in dat:
            idat.append(x & 0x000F) 
            idat.append((x >> 4) & 0x000F)
        return idat

    def get_switch_state(self):
        return self._sw_state

    def queue_command(self, dat): 
        global last_cmd_id
        last_cmd_id += 1
        self._cmd_queue.insert(0, (last_cmd_id, dat))
        return last_cmd_id

    def _attempt_comm(self, dat):
        events = []
        if not self._node_addr in config.get_active_nodes(): return events
        if dat is None and self._node_addr in [2, 3]: return events
        rsp = comm.node_io(self._node_addr, dat) 
        self._last_comm_attemp_time = time.monotonic()
        if rsp == None: 
            telp = time.monotonic() - self._last_comm_success_time
            if telp > 5.00 and not self._node_addr in [2, 3]:
                if self._active: log(f"Node {self._name} going inactive.")
                self._active = False
            return None
        self._last_comm_success_time = time.monotonic() 
        if not self._active: log(f"Node {self._name} going active.") 
        self._active = True
        if self._ibs == 0: return events
        nb, ib0, ib1 = 1, 3, 4
        if self._ibs == 2: 
            nb, ib0, ib1 = 2, 3, 5
        nswb = int(self._nsw / 2) 
        if self._nsw % 2 != 0: nswb += 1  
        if len(rsp) < 3 + nb + nswb:
            self._response_errs += 1      
            return events
        if self._ibs > 1: 
            self._sw_state = (rsp[ib0 + 1] << 8) | rsp[ib0]
        else:
            self._sw_state = rsp[ib0]
        temp_cnts = self._split_bytes(rsp[ib1:ib1+nswb])
        if not self._have_init_counts:
            self._have_init_counts = True 
            for i in range(self._nsw):
                self._sw_counts[i] = temp_cnts[i]
            return events 
        # Generate new events, save the counts.
        for i in range(self._nsw):
            cnt = (temp_cnts[i] & 0x000F) - (self._sw_counts[i] & 0x000F) 
            self._sw_counts[i] = temp_cnts[i] 
            if cnt < 0: cnt += 16
            for j in range(cnt):
                event_name = self._designator + f"{i+1}"
                events.append(event_name)
        return events
       
    def update(self):
        ''' Update the node, and return any new events.'''
        global completed_cmds, dropped_cmds
        events = [] 
        if comm is None: return events
        if not self._active:
            if len(self._cmd_queue) > 0:
                log(f"Node {self._name} is not active, {len(self._cmd_queue)} commands dropped.")
                for id, _ in self._cmd_queue:
                    dropped_cmds.append(id)
                self._cmd_queue = [] 
            if self._last_comm_success_time == 0: twait = 5 
            else: twait = 1.5 
            telp = time.monotonic() - self._last_comm_attemp_time
            if telp < twait: return events
        while(True):
            dat = None 
            id = -1
            if len(self._cmd_queue) > 0: id, dat = self._cmd_queue.pop()
            temp_events = self._attempt_comm(dat)
            if temp_events is None: 
                # Try again, one time
                temp_events = self._attempt_comm(dat)
                if temp_events is None:
                    if dat is not None: self._cmd_queue.append((id, dat))
                    return events 
            if id != -1:
                completed_cmds.append(id)
            events.extend(temp_events)
            if len(self._cmd_queue) == 0: return events
 
class Hardware():
    def __init__(self):
        if comm is not None: comm.begin()
        self._event_lock = threading.Lock() 
        self._cmd_queue_lock = threading.Lock()
        self._nodes = {}
        for node_adr in nodes:
            self._nodes[node_adr] = Node(node_adr)
        self._events = [] 
        self._simulated_events = [] 
        self._last_key = None
        self._key_digits = (pyg.K_1, pyg.K_2, pyg.K_3, pyg.K_4, pyg.K_5, pyg.K_6, pyg.K_7, pyg.K_8, pyg.K_9)
        self._major_keys = (pyg.K_t, pyg.K_l, pyg.K_f, pyg.K_b, pyg.K_k)
        self._major_key_map = {pyg.K_t: "T", pyg.K_l: "L", pyg.K_f: "F", pyg.K_b: "B", pyg.K_k: "K" }
        self._startup_cmds = []

    def send_command(self, addr, dat):
        '''Queue's a command to be sent to a node on the next update.  Does not block. 
        Returns an id for the command so that the caller can check if it was successfully 
        sent at a later time by polling command_done(). '''
        id = self._nodes[addr].queue_command(dat)
        return id

    def send_startup_cmd(self, addr, cmd, name=""):
        '''Queues a command that MUST be executed at startup before regular games can
        be played.  This is suitable for configuration commands that must be executed
        for safe play.  After all the startup commands are queued, call conduct_startup(). '''
        self._startup_cmds.append((addr, cmd, name))

    def conduct_startup(self):
        '''Issues all the startup commands.  Will block until entire queue is empty.  If
        the queue cannot be competed, due to some hardware failure -- will return 
        a displayable error.  Otherwise None is returned. '''
        ncnt = 0
        t0 = time.monotonic()
        errtxt = None
        active_nodes = config.get_active_nodes()
        broken_nodes = []
        for addr, cmd, name in self._startup_cmds:
            if not addr in active_nodes: continue
            if addr in broken_nodes: continue
            tstart = time.monotonic()
            while True:
                if comm is None: rsp = []
                else: rsp = comm.node_io(addr, cmd)
                if rsp is not None:
                    if addr in nodes: node_name = nodes[addr]['name']
                    else: node_name = f"<Unknown>"
                    log(f"Startup Command Issued on node {node_name}: {name}")
                    break 
                if time.monotonic() - tstart > 2.0:
                    if addr in nodes: node_name = nodes[addr]['name']
                    else: node_name = f"<Unknown>"
                    log(f"Startup Command FAILED on node {node_name}: {name} ")
                    errtxt = f"Node {addr} ({node_name}) not responding."
                    broken_nodes.append(addr)
                    break  # we try to issue all commands to other nodes, even on errors
            ncnt += 1
        telp = time.monotonic() - t0
        log(f"{ncnt} startup commands successfully issued in {telp:.2f} seconds.")
        return errtxt

    def command_done(id):
        '''Returns true if the command was successfully sent.  If so, thereafter the same
        id will return false.  If the command has not been successfully sent thus far, false is 
        returned.''' 
        global completed_cmds
        if id in completed_cmds:
            completed_cmds.remove(id) 
            return True
        return False

    def command_dropped(id):
        '''Returns true if the command was dropped.  If so, thereafter the same id will return
        false.  If the command was not dropped thus far, false is returned.'''
        global dropped_cmds
        if id in dropped_cmds:
            dropped_cmds.remove(id)
            return True 
        return False

    def report_to_log(self):
        if comm is None: return None
        cmap = comm.report()
        s = "" 
        for k in cmap:
            s += f"{k}: {cmap[k]}   "
        log(s)
    
    def update(self):
        events = [] 
        # Start by adding simulated events.
        if self._simulated_events is not None:
            events.extend(self._simulated_events)
            self._simulated_events = []
        # Now, talk to real nodes...
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
            bits = self._nodes[node_addr].get_switch_state()
            return bits 
        else: return 0

    def simulate(self, key):
        '''Allows keyboard input to simulate game play.  Used
        for testing.  See comments above for key meanings.'''
        if key in self._major_keys:
            self._last_key = key 
            return 
        if self._last_key is not None:
            for i, k in enumerate(self._key_digits):
                if k == key: 
                    self._simulated_events.append(self._major_key_map[self._last_key] + f"{i+1:1}")
                    return 
        
if __name__ == "__main__":
    pb_log.disable_debug()
    pb_log.disable_terminal()
    hw = Hardware() 
    while(True):
        hw.update() 
        events = hw.get_events()
        for e in events:
            print(e)
        

