# random_choice.py -- class to provide a random choice 
# Fall 2022, dlb

import random
import time

class RandomChoice():
    '''Returns a random choice from a list.  De-weights the same choice twice in a row.'''
    def __init__(self, lst):
        self.lst = lst 
        self.last_choice = None
        random.seed(int(time.time()))

    def get(self):
        ''' Returns one element from the list given when this class was initicated.  On
        successive called, trys not to return the same element twice in a row.'''
        nrow = 0
        while True:
            c = random.choice(self.lst) 
            if c != self.last_choice: 
                self.last_choice = c 
                return c 
            nrow += 1 
            if nrow >= 3: return c