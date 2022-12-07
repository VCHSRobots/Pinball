# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Flipper Node handler

from pb_log import log
import hardware 
import event_manager

class Flippers():
    ''' Takes care of stuff with the flipper's node, including
    game start, and ball cycling.'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_FLIPPERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()
    
    def new_ball(self):
        '''Puts a new ball into the game.'''
        bits = self._hw.get_switch_state(self._nodeadr)
        sbits = ""
        for i in range(8):
            if 1 << (7 - i) & bits != 0: sbits += "X"
            else: sbits += "-"
        log(f"Putting a new ball into play.  Filpper Bits: {sbits}")
        if not self.ball_ready_to_cycle():
            log("Trying to put a non-existant ball into play.")
        cmd = [15, 1]  # Turn on the cycle servo      
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Ball Servo Assert")
        cmd = [14, 0b00000001, 1, 0, 0]  # Turn on the lift motor, to run indefinate.
        self._hw.send_command(self._nodeadr, cmd) 
        log("Sending Command from Flippers: Lift Motor ON")
        # Queue up an event to return the servo to normal
        ev = {'cmd': [15, 0], 'cmd_name': "Set Servo to Normal"}
        self._queue.add_event(ev, 2.0)
        # Queue up an event to stop the lift motor
        ev = {'cmd': [14, 0b00000001, 0, 0, 0], 'cmd_name': "Stop Lift Motor"}
        self._queue.add_event(ev, 3.0)

    def lift_motor_cycle(self, time_on = 1.5):
        '''Cycles the lift motor for the given amount of time.'''
        cmd = [14, 0b00000001, 1, 0, 0]  # Turn on the lift motor, to run indefinate.
        self._hw.send_command(self._nodeadr, cmd) 
        log("Sending Command from Flippers: Lift Motor ON")
        # Queue up an event to stop the lift motor
        ev = {'cmd': [14, 0b00000001, 0, 0, 0], 'cmd_name': "Stop Lift Motor"}
        self._queue.add_event(ev, time_on)

    def process_hardware_events(self, events):
        ''' Processes hardware events that pertain to the flippers'''
        pass

    def update(self):
        '''Processes internal events pertaining to the flippers.'''
        events = self._queue.get_fired_events() 
        for ev in events:
            self._hw.send_command(self._nodeadr, ev['cmd'])
            if "cmd_name" in ev: name = ev['cmd_name']
            else: name = ""
            log(f"Sending Queued Command from Flippers: {name}")

    def disable_flippers(self):
        cmd = [12, 0xFF, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Disable All Flippers.")

    def enable_main_flippers(self):
        cmd = [12, 0x03, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Enable Main Flippers.")
        
    def enable_thrid_flipper(self):
        cmd = [12, 0x07, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Enable Third Flipper.")

    def disable_thrid_flipper(self):
        cmd = [12, 0x04, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Disable Third Flipper.")

    def balls_in_trough(self):
        '''Returns the number of balls in the trough.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        nballs = 0
        if bits & 0b00001000 != 0: nballs += 1    # Ball next to release gate
        if bits & 0b00010000 != 0: nballs += 1    # Next Ball
        if bits & 0b00100000 != 0: nballs += 1    # Next Ball
        if bits & 0b01000000 != 0: nballs += 1    # Ball under drain hole
        return nballs

    def ball_ready_to_cycle(self):
        '''Returns true if a ball is ready to cycle.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        if bits & 0b00001000 != 0: return True
        return False

    def ball_in_hole(self):
        ''' Returns true if a ball is in the hole.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        if bits & 0b10000000 != 0: return True
        return False 

    def eject_drop_ball(self):
        # Set the hole ejector to a reasonable pwm
        cmd = [13, 0b00000100, 100]
        self._hw.send_command(self._nodeadr, cmd)
        cmd = [14, 0b00000100, 1, 100]  # turns on  coil #3 for 100 ms.
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Eject Drop Ball")