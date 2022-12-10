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
        # Trough Status
        self._current_bits = 0b00000111  
        self._last_bits = 0 
        self._last_bits_change_t0 = time.monotonic()
        self._bit_change_pending = False
        # Drop Hole Status
        self._current_drop = False 
        self._last_drop = False 
        self._last_drop_change_t0 = time.monotonic() 
        self._drop_change_pending = False 

    def monitor_ball_trough(self):
        ''' Monitors the ball trough.  Adds events to the main queue.'''
        bits = self._flippers.get_ball_bits() 
        if not self._bit_change_pending: 
            if bits == self._current_bits: return
            self._bit_change_pending = True 
            self._last_bits = bits
            self._last_bits_change_t0 = time.monotonic()
            return
        if bits != self._last_bits:
            self._last_bits = bits
            self._last_bits_change_t0 = time.monotonic()
            return
        if time.monotonic() - self._last_bits_change_t0 < 1.5: return
        # Trough bits have been stable 
        self._bit_change_pending = False
        bold = self._current_bits 
        bnew = self._last_bits
        self._current_bits = self._last_bits 
        if bold == bnew:
            # The change didn't actually take place 
            return 
        # Something changed.  What was it?
        if bold == 0b00000111:   # All balls were in trough 
            if bnew == 0b00000011:  
                self._game.add_game_event("Ball Released")
            elif bnew == 0b00000001:
                self._game.add_game_event("Ball Released")
                self._game.add_game_event("Ball Released")
            else:
                self._game.add_game_event("Balls Jammed")
            return
        if bold == 0b00000011:  # Two balls were in trough
            if bnew == 0b00000001:
                self._game.add_game_event("Ball Released")
            elif bnew == 0b00000111:
                self._game.add_game_event("Ball Drained")
            else:
                self._game.add_game_event("Balls Jammed")
        if bold == 0b00000001: # One ball was in trough
            if bnew == 0b00000011:
                self._game.add_game_event("Ball Drained")
            elif bnew == 0b00000111:
                self._game.add_game_event("Ball Drained")
                self._game.add_game_event("Ball Drained")
            else:
                self._game.add_event("Ball Jammed")
        else:  # Trough Was Jammed
            if bnew == 0b00000111 or bnew == 0b00000011 or bnew == 0b00000001:
                self._game.add_game_event("Jam Cleared")

        self._current_drop = False 
        self._last_drop = False 
        self._last_drop_change_t0 = time.monotonic() 
        self._drop_change_pending = False

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
        n = -1
        if self._current_bits == 0b00000000: n = 3 # 3  # Invalid Condition
        if self._current_bits == 0b00000001: n = 2 
        if self._current_bits == 0b00000010: n = 2  # Invalid Condition
        if self._current_bits == 0b00000100: n = 2  # Invalid Condition
        if self._current_bits == 0b00001000: n = 2  # Invalid Condition
        if self._current_bits == 0b00000011: n = 1 
        if self._current_bits == 0b00000110: n = 1  # Invalid Condition
        if self._current_bits == 0b00000101: n = 1  # Invalid Condition
        if self._current_bits == 0b00001001: n = 1  # Invalid Condition 
        if self._current_bits == 0b00001010: n = 1  # Invalid Condition
        if self._current_bits == 0b00001100: n = 1  # Invalid Condition
        if self._current_bits == 0b00000111: n = 0  
        if self._current_bits == 0b00001011: n = 0  # Invalid Condition
        if self._current_bits == 0b00001101: n = 0  # Invalid Condition
        if self._current_bits == 0b00001110: n = 0  # Invalid Condition
        if self._current_bits == 0b00001111: n = 0  # Invalid Condition
        return n

    def update(self):
        self.monitor_ball_trough() 
        self.monitor_drop_hole()
