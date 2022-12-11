# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# ball_manager.py
#
# Monitors and manages the balls on the field.

import time
from pb_log import log

class BallManager():

    def __init__(self, game, hw, flippers):
        self._game = game 
        self._hw = hw 
        self._flippers = flippers
        # Trough Bit Status
        self._current_bits = 0b0000111
        self._last_bits    = 0b0000111
        self._bit_change_pending = False 
        self._bit_change_pending_t0 = time.monotonic() 
        self._bit_stable = True
        # Trough Status
        self._balls_in_trough = 3
        self._trough_change_pending = False
        self._trough_invalid = False
        # Drop Hole Status
        self._current_drop = False 
        self._last_drop = False 
        self._last_drop_change_t0 = time.monotonic() 
        self._drop_change_pending = False 

    def monitor_ball_trough_bits(self):
        ''' Monitors the bits in the ball trough.  If the
        bits haven't changed in a while, declare them stable.'''
        bits = self._flippers.get_ball_bits()
        if bits == self._last_bits:
            if not self._bit_change_pending: 
                self._bits_stable = True 
                return 
            telp = time.monotonic() - self._bit_change_pending_t0 
            if telp > 0.5: 
                log("New bits stable.")
                self._bit_change_pending = False 
                self._bits_stable = True 
            return
        log("Bit change detected.")
        self._last_bits = bits
        self._bit_change_pending = True
        self._bit_change_pending_t0 = time.monotonic()
        self._bits_stable = False

    def count_balls_in_trough(self):
        ''' Returns a raw count of the number of balls in the
        trough -- no matter what their position. '''
        n = 0
        for i in range(4):
            if (1 << i) & self._current_bits != 0: n += 1 
        return n

    def trough_is_valid(self, bits):
        ''' Returns true if we thing the trough is in a 
        stable (non-jammed) condition '''
        if bits == 0b00000001: return True
        if bits == 0b00000011: return True
        if bits == 0b00000111: return True
        return False

    def monitor_ball_trough(self):
        ''' Monitors the ball trought.  Waits for valid configurations.'''
        self.monitor_ball_trough_bits() 
        if not self._bits_stable:
            if self._trough_change_pending:
                # decide if we are in a jammed condition
                pass
            self._trough_change_pending = True
            log("Trough Change Pending")
            return
        if not self._trough_change_pending: return
        self._trough_change_pending = False
        self._current_bits = self._last_bits 
        if not self.trough_is_valid(self._current_bits):
            # The bits are stable, but not in a valid config.  
            if self._trough_invalid:
                # it was invalid before.  Don't do anything
                return
            self._trough_invalid = True
            self._game.add_game_event("Balls Jammed")
            return
        if self._trough_invalid:
            self._game.add_game_event("Balls Unjammed")
        self._trough_invalid = False
        new_ball_count = self.count_balls_in_trough()
        log(f"New ball count: {new_ball_count}   Old count: {self._balls_in_trough}")
        if new_ball_count > self._balls_in_trough:
            n = new_ball_count - self._balls_in_trough
            for i in range(n):
                self._game.add_game_event("Ball Drained")
            self._balls_in_trough = new_ball_count 
            return
        if new_ball_count < self._balls_in_trough:
            n = self._balls_in_trough - new_ball_count 
            for i in range(n):
                self._game.add_game_event("Ball Released")
            self._balls_in_trough = new_ball_count 
            return

    def monitor_drop_hole(self):
        ''' Monitors the drop hole. Adds events to the main queue.'''
        inhole = self._flippers.ball_in_hole() 
        if not self._drop_change_pending: 
            if inhole == self._current_drop: return
            self._drop_change_pending = True 
            self._last_drop = inhole
            self._last_drop_change_t0 = time.monotonic()
            return
        if inhole != self._last_drop:
            self._last_drop = inhole
            self._last_drop_change_t0 = time.monotonic()
            return
        if time.monotonic() - self._last_drop_change_t0 < 1.5: return
        # Drop hole has been stable
        self._drop_change_pending = False
        bold = self._current_drop 
        bnew = self._last_drop
        self._current_drop = self._last_drop 
        if bold == bnew:
            # The change didn't actually take place 
            return 
        # Something changed.  What was it?
        if bold == False:   # There was no ball in the hole
            self._game.add_game_event("Drop Hole Full")
        else:
            self._game.add_game_event("Drop Hole Empty")
        
    def drop_hole_full(self):
        return self._current_drop

    def balls_in_play(self):
        ''' Returns the number of balls we think are in play. 
        A ball is considered "in play" if it is not in the
        trough. -1 is returned when we think there is something wrong.
        This assumes the game starts with 3 balls.'''
        n = 3 - self._balls_in_trough 
        if n < 0: n = 0
        if n > 3: n = 3
        return n 

    def balls_ready_to_play(self):
        ''' Returns True if 3 balls in proper position for game start. Otherwise
        returns an error message indicating the problem. '''
        if self._current_bits == 0b00000111: return True
        if self._current_bits == 0b00001111: return "Too many balls!  Must be 3."
        if not self.trough_is_valid(self._current_bits):
            return f"Balls out of position. ({self._current_bits:>04b})"
        nballs = self.balls_in_trough()
        if nballs < 3: return f"Only {nballs} found. Need 3."
        elif nballs == 3: return True
        else: return f"Unknown Err. NBalls={nballs}"

    def update(self):
        self.monitor_ball_trough() 
        self.monitor_drop_hole()
