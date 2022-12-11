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

# Pixel Index for Lights on Play Field
PI_LANE_1_TOP   = ("lane_1_top", 0) 
PI_LANE_2_TOP   = ("lane_2_top", 1) 
PI_LANE_3_TOP   = ("lane_3_top", 2)
PI_LANE_1_BOT   = ("lane_1_bot", 3)
PI_LANE_2_BOT   = ("lane_2_bot", 4)
PI_LANE_3_BOT   = ("lane_3_bot", 5)
PI_TARG_X       = ("target_X", 6)
PI_DROP_HOLE    = ("drop_hole", 7)
PI_RAMP_1       = ("ramp_1", 8)
PI_RAMP_2       = ("ramp_2", 9)
PI_PATH_1       = ("path_1", 10)
PI_PATH_2       = ("path_2", 11)
PI_TARG_PANIC_1 = ("target_panic_1", 12)
PI_TARG_PANIC_2 = ("target_panic_2", 13)
PI_TARG_E       = ("target_E", 14)
PI_TARG_P       = ("target_P", 15)
PI_TARG_I       = ("target_I", 16)
PI_TARG_C       = ("target_C", 17)
PI_COL_RT       = ("column_right", (18, 19, 20, 21))
PI_COL_MID      = ("column_middle", (22, 23, 24, 25))
PI_COL_LEFT     = ("column_left", (26, 27, 28, 29))
PI_FAKE         = ("fake", 31)

# Lamp constants
LAMP_PANIC      = ("panic_lamp", 0b0001)
LAMP_LANES      = ("lane_lamps", 0b0010)

pixels = [PI_LANE_1_TOP, PI_LANE_1_BOT, PI_LANE_2_TOP, PI_LANE_2_BOT, PI_LANE_3_TOP, PI_LANE_3_BOT, 
          PI_TARG_X, PI_DROP_HOLE, PI_RAMP_1, PI_RAMP_2, PI_PATH_1, PI_PATH_2, PI_TARG_PANIC_1, 
          PI_TARG_PANIC_2, PI_TARG_E, PI_TARG_P, PI_TARG_I, PI_TARG_C, PI_COL_RT, PI_COL_MID, PI_COL_LEFT, PI_FAKE ]

def reverse_lookup_name(px):
    for name, pix in pixels:
        if type(pix) is list:
            for i, pp in enumerate(pix):
                if pp == px: return name + f"_({i})"
        else:
            if px == pix: return name
    return "<unknown pixel>"

def tell_log(cmd):
    ''' Dissambles the cmd into human readable. To tell log.'''
    if len(cmd) <= 0: return 
    c = cmd[0] 
    if c == CMD_NEO_RESET: 
        c1 = cmd[1:4]
        log(f"Playfield Lights: Reseting all individule pixels to {c1}")
    elif c == CMD_NEO_SINGLE:
        c1, c2, ipx, w1, w2 = cmd[1:4], cmd[4:7], cmd[7], cmd[8], cmd[9]
        pname = reverse_lookup_name(ipx)
        log(f"Playfield Lights: Setting pixel {pname} ({ipx}) to colors {c1} {c2} with times {w1} {w2}")
    elif c == CMD_NEO_SOLID:
        c1 = cmd[1:4]
        log(f"Playfield lights: Setting all pixels to {c1}")
    elif c == CMD_NEO_WIPE:
        c1, c2, w1 = cmd[1:4], cmd[4:7], cmd[7]
        log(f"Playfield Lights: Setting a WIPE with colors {c1} and {c2} with wait time of {w1}")
    elif c == CMD_NEO_CHASE:    
        c1, c2, n, w1 = cmd[1:4], cmd[4:7], cmd[7], cmd[8]
        log(f"Playfield Lights: Setting a CHASE with colors {c1} and {c2}, window size of {n} and wait time {w1}")
    elif c == CMD_NEO_BLINK:     
        c1, c2, n1, n2, w1 = cmd[1:4], cmd[4:7], cmd[7], cmd[8], cmd[9]
        log(f"Playfield Lights: Setting a BLINK with colors {c1} and {c2}, sizes of {n1} and {n2} and wait {w1}")
    elif c == CMD_NEO_DEMO:      
        log(f"Playfield Lights: Setting NEO DEMO on all pixels")
    elif c == CMD_LAMP_SOLID:    
        mask, brightness = cmd[1], cmd[2]
        log(f"Playfield Lights: Setting lamps to SOLID with mask={mask:04b} and brightness={brightness}")
    elif c == CMD_LAMP_FLASH:    
        mask, brightness, time_on = cmd[1], cmd[2], cmd[3]
        log(f"Playfield Lights: Setting Lamp Flash, mask={mask:04b}, brightness={brightness}, flash_on_time={time_on}")
    elif c == CMD_LAMP_MODULATE:
        mask, b1, b2, steps = cmd[1], cmd[2], cmd[3], cmd[4]
        log(f"Playfield Lights: Setting lamps to Modulate, mask={mask:04b}, brightness levels = {b1} and {b2}, steps = {steps}")
    else: log(f"Playfield Lights: Sending unknown cmd {cmd}") 

class PlayfieldLights():
    ''' Takes care of play field lights.'''
   
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_PLIGHTS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def issue_cmd(self, *cmd):
        ''' Send a command for this node.  Log the command as well'''
        self._hw.send_command(self._nodeadr, cmd)
        tell_log(cmd)

    def queue_startup_cmds(self):
        pass

    def update(self):
        '''Processes internal events pertaining to the score box lights.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            if ev['name'] == "set_single_mode":
                name, ipx = PI_FAKE
                self.issue_cmd(CMD_NEO_SINGLE, 0,0,0, 0,0,0, ipx, 2, 2)
            if ev['name'] == "cmd":
                cmd = ev['cmd']
                self.issue_cmd(*cmd)

    def set_pixel_blink(self, px, c1, c2, w1, w2, delay=0):
        ''' Sets an individule pixel or pixel group to blink between two colors
        and wait times.  Colors are 3-tuples. Wait times are in units of 25msec.
        If delay is given, the command is queued for later.'''
        name, ipx = px
        r1, g1, b1 = c1 
        r2, g2, b2 = c2
        if type(ipx) is list: ipx_list = ipx 
        else:                 ipx_list = [ipx]
        for ipx in ipx_list:
            cmd = [CMD_NEO_SINGLE, r1, g1, b1, r2, g2, b2, ipx, w1, w2]
            if delay == 0:
                self.issue_cmd(*cmd)
            else:
                ev = {'name': "cmd", 'cmd': cmd, 'category': 'neo'}
                self._queue.add_event(ev, delay)

    def set_pixel(self, px, c, delay=0):
        ''' Sets an individule pixel or pixel group to a solid color. 
        Color is a 3-tuple. If delay is given, the command is queued for later.'''
        self.set_pixel_blink(px, c, c, 50, 50, delay)

    def set_lamp_solid(self, lamp, brightness, delay=0):
        ''' Sets the lamp to solid brightness.  If delay is given
        the command is queued for later. '''
        name, mask = lamp
        cmd = [CMD_LAMP_SOLID, mask, brightness]
        if delay == 0: self.issue_cmd(*cmd)
        else:
            ev = {'name': "cmd", "cmd": cmd, 'category': 'lamp'}
            self._queue.add_event(ev, delay)

    def set_lamp_flash(self, lamp, brightness, time_on, delay=0):
        ''' Sets the lamp to flash, at the given brightness, for the
        time_on duration, given in 25ms units.  After the flash,
        the lamp will return to it's previous mode.  If delay is
        given, the command is queued for later.'''
        name, mask = lamp
        cmd = [CMD_LAMP_SOLID, mask, brightness, time_on]
        if delay == 0: self.issue_cmd(*cmd)
        else:
            ev = {'name': "cmd", "cmd": cmd, 'category': 'lamp'}
            self._queue.add_event(ev, delay)

    def set_lamp_modulate(self, lamp, b1, b2, steps, delay=0):
        ''' Sets the lamp to modulate between two brightnesses.  Steps
        is the period in 25 msec units, to go between the two brightnesses.
        if delay is given, the command is queued for later.'''
        name, mask = lamp
        cmd = [CMD_LAMP_SOLID, mask, b1, b2, steps]
        if delay == 0: self.issue_cmd(*cmd)
        else:
            ev = {'name': "cmd", "cmd": cmd, 'category': 'lamp'}
            self._queue.add_event(ev, delay)

    def on_new_game(self):
        ''' Indicate the start of a new geam. '''
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_RESET, 0, 0, 0)
        self.issue_cmd(CMD_NEO_BLINK, 200, 200, 200,  255, 0, 0,   1, 1, 3)  # White/red blink 75ms
        ev ={'name': "set_single_mode", 'category': 'neo'}
        self._queue.add_event(ev, 3.5)
        self.set_lamp_modulate(LAMP_LANES, 0, 255, 50)
        self.set_lamp_modulate(LAMP_PANIC, 0, 25, 40)

    def on_ball_drain(self):
        ''' Indicate the end of a turn due to ball draining. '''
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_WIPE, 0,0,0, 0,0,0, 6)   # Slow wipe to black, 150ms step period
        ev ={'name': "set_single_mode", 'category': 'neo'}
        self._queue.add_event(ev, 3.5)
    
    def on_new_ball(self):
        ''' Indicates a new ball being put into play'''
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_BLINK, 255, 0, 0,  0, 0, 255,   1, 1, 3)  # Blink, red/blue blink 75 ms
        ev ={'name': "set_single_mode", 'category': 'neo'}
        self._queue.add_event(ev, 3.5)
        self.set_lamp_flash(LAMP_PANIC, 200, 10)

    def on_drop_hole(self):
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_SOLID, 0, 0, 255)  # Solid bright blue 
        ev ={'name': "set_single_mode", 'category': 'neo'}
        self._queue.add_event(ev, 2.0)

    def on_panic(self):
        ''' Indicates a panic situation.'''
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_CHASE, 255, 0, 0, 0, 255, 0, 2, 2) # Chase, red/green, 2 pixel window, 50ms
        ev ={'name': "set_single_mode", 'category': 'neo'}
        self._queue.add_event(ev, 3.5)
        self.set_lamp_solid(LAMP_PANIC, 255)

    def on_no_panic(self):
        self.set_lamp_modulate(LAMP_PANIC, 0, 25, 40)

    def on_game_over(self):
        ''' Indicate game over. '''
        self._queue.remove_category('neo')
        self.issue_cmd(CMD_NEO_SOLID, 128, 0, 0) # Solid dull red
        cmd = [CMD_NEO_DEMO]
        ev = {'name': 'cmd', 'cmd': cmd, 'category': 'neo'}
        self._queue.add_event(ev, 10)
