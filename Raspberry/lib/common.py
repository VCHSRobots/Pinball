#  common.py -- common varialbes and globals 
#  Pinball Machine Project, EPIC Robotz, Fall 2022
#  dlb
#

import sys 

def platform():
    '''Returns either "sim" or "real" depending on where
    the code is being run from.  That is, if the code
    is being run on the real pinball machine, "real" will
    be returned.'''
    if sys.platform == "linux": return "real"
    else: return "sim"
