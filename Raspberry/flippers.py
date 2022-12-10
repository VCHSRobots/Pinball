# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Flipper Node handler

import time
from pb_log import log
import hardware 
import event_manager
import config 

CMD_FLIPPER_PWM    =  10
CMD_FLIPPER_CTRL   =  11
CMD_FLIPPER_ENABLE =  12
CMD_COILS_PWM      =  13
CMD_COILS_CTRL     =  14
CMD_BALL_CYCLE     =  15
CMD_DEBOUNCE       =  16

MASK_FLIPPER_RIGHT  = 0b00000001
MASK_FLIPPER_LEFT   = 0b00000010
MASK_FLIPPER_THIRD  = 0b00000100
MASK_LIFT_MOTOR     = 0b00000001
MASK_DROP_HOLE      = 0b00000100
MASK_MAIN_FLIPPERS  = 0b00000011
MASK_ALL_FLIPPERS   = 0b00000111

MASK_RIGHT_FLIPPER_SW = 0b00000001
MASK_LEFT_FLIPPER_SW  = 0b00000010
MASK_START_SW         = 0b00000100
MASK_BALL_1_READY     = 0b00001000
MASK_BALL_2_READY     = 0b00010000
MASK_BALL_3_READY     = 0b00100000
MASK_BALL_4_READY     = 0b01000000
MASK_HOLE_SWITCH      = 0b10000000

BALL_1_BIT_POS        = 3

class Flippers():
    ''' Takes care of stuff with the flipper's node, including
    game start, and ball cycling.'''
    def __init__(self, gameapp, hw, sm):
        self._nodeadr = hardware.NODE_FLIPPERS
        self._game = gameapp
        self._hw = hw
        self._sound = sm
        self._queue = event_manager.EventManager()

    def queue_startup_cmds(self):
        cmd = [CMD_FLIPPER_ENABLE, MASK_ALL_FLIPPERS, 0]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "disable all flippers")

        pwm1 = config.get_param('flipper_right', 'pwm1', 255)
        pwm2 = config.get_param('flipper_right', 'pwm2', 255)
        delay = config.get_param('flipper_right', 'delay', 50)
        cmd = [CMD_FLIPPER_PWM, MASK_FLIPPER_RIGHT, pwm1, pwm2, delay]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "flipper_right pwm")
        
        pwm1 = config.get_param('flipper_left', 'pwm1', 255)
        pwm2 = config.get_param('flipper_left', 'pwm2', 255)
        delay = config.get_param('flipper_left', 'delay', 50)
        cmd = [CMD_FLIPPER_PWM, MASK_FLIPPER_LEFT, pwm1, pwm2, delay]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "flipper_left pwm")
        
        pwm1 = config.get_param('flipper_third', 'pwm1', 255)
        pwm2 = config.get_param('flipper_third', 'pwm2', 255)
        delay = config.get_param('flipper_third', 'delay', 50)
        cmd = [CMD_FLIPPER_PWM, MASK_FLIPPER_THIRD, pwm1, pwm2, delay]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "flipper_third pwm")
        
        pwm = config.get_param('lift_motor', 'pwm', 255)
        cmd = [CMD_COILS_PWM, MASK_LIFT_MOTOR, pwm]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "lift_motor pwm")

        pwm = config.get_param('drop_hole_coil', 'pwm', 100)
        cmd = [CMD_COILS_PWM, MASK_DROP_HOLE, pwm]
        self._hw.send_startup_cmd(self._nodeadr, cmd, "drop_hole_coil pwm")
 
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
        cmd = [CMD_BALL_CYCLE, 1]  # Turn on the cycle servo      
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Ball Servo Assert")
        cmd = [CMD_COILS_CTRL, MASK_LIFT_MOTOR, 1, 0, 0]  # Turn on the lift motor, to run indefinate.
        self._hw.send_command(self._nodeadr, cmd) 
        log("Sending Command from Flippers: Lift Motor ON")
        # Queue up an event to return the servo to normal
        cycle_time = config.get_param('ball_gate_servo', 'cycle_time', 1.5)
        ev = {'cmd': [CMD_BALL_CYCLE, 0], 'cmd_name': "Set Servo to Normal"}
        self._queue.add_event(ev, cycle_time)
        # Queue up an event to stop the lift motor
        run_time = config.get_param('lift_motor', 'run_time', 4.0)
        ev = {'cmd': [CMD_COILS_CTRL, MASK_LIFT_MOTOR, 0, 0, 0], 'cmd_name': "Stop Lift Motor"}
        self._queue.add_event(ev, run_time)

    def lift_motor_cycle(self, time_on = 1.5):
        '''Cycles the lift motor for the given amount of time.'''
        cmd = [CMD_COILS_CTRL, MASK_LIFT_MOTOR, 1, 0, 0]  # Turn on the lift motor, to run indefinate.
        self._hw.send_command(self._nodeadr, cmd) 
        log("Sending Command from Flippers: Lift Motor ON")
        # Queue up an event to stop the lift motor
        ev = {'cmd': [CMD_COILS_CTRL, MASK_LIFT_MOTOR, 0, 0, 0], 'cmd_name': "Stop Lift Motor"}
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
        cmd = [CMD_FLIPPER_ENABLE, MASK_ALL_FLIPPERS, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Disable All Flippers.")

    def enable_main_flippers(self):
        cmd = [CMD_FLIPPER_ENABLE, MASK_MAIN_FLIPPERS, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Enable Main Flippers.")
        
    def enable_thrid_flipper(self):
        cmd = [CMD_FLIPPER_ENABLE, MASK_FLIPPER_THIRD, 1]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Enable Third Flipper.")

    def disable_thrid_flipper(self):
        cmd = [CMD_FLIPPER_ENABLE, MASK_FLIPPER_THIRD, 0]
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Disable Third Flipper.")

    def balls_in_trough(self):
        '''Returns the number of balls in the trough.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        nballs = 0
        if bits & MASK_BALL_1_READY != 0: nballs += 1    # Ball next to release gate
        if bits & MASK_BALL_2_READY != 0: nballs += 1    # Next Ball
        if bits & MASK_BALL_3_READY != 0: nballs += 1    # Next Ball
        if bits & MASK_BALL_4_READY != 0: nballs += 1    # Ball under drain hole
        return nballs

    def balls_ready_to_play(self):
        ''' Returns True if 3 balls in proper position for game start. Otherwise
        returns an error message indicating the problem. '''
        nballs = self.balls_in_trough()
        if nballs != 3:
            if nballs > 3: return f"Too many balls! ({nballs})"
            return f"Too few balls ({nballs}). Need 3."
        mask_desired = MASK_BALL_1_READY | MASK_BALL_2_READY | MASK_BALL_3_READY
        mask_allballs = MASK_BALL_1_READY | MASK_BALL_2_READY | MASK_BALL_3_READY | MASK_BALL_4_READY
        ball_bits = self._hw.get_switch_state(self._nodeadr) & mask_allballs
        if ball_bits != mask_desired: 
            return f"Balls out of position. ({ball_bits:>08b})"
        return True

    def ball_ready_to_cycle(self):
        '''Returns true if a ball is ready to cycle.  This means
        that there are two balls against the gate.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        if bits & MASK_BALL_1_READY != 0 and bits & MASK_BALL_2_READY != 0: return True
        return False

    def get_ball_bits(self):
        ''' Returns the four ball bits (shifted to the LSB) that represent
        the position of balls in the trough. '''
        bits = self._hw.get_switch_state(self._nodeadr)
        ball_bits = (bits >> BALL_1_BIT_POS) & 0x0F
        return ball_bits

    def ball_in_hole(self):
        ''' Returns true if a ball is in the hole.'''
        bits = self._hw.get_switch_state(self._nodeadr) 
        if bits & MASK_HOLE_SWITCH != 0: return True
        return False 

    def eject_drop_ball(self):
        # Assume that the pwm is properly set up.
        time_on = config.get_param("drop_hole_coil", "time_on", 100)
        cmd = [CMD_COILS_CTRL, MASK_DROP_HOLE, 1, time_on] 
        self._hw.send_command(self._nodeadr, cmd)
        log("Sending Command from Flippers: Eject Drop Ball")