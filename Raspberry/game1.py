# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# "Game1" -- First program to conduct a complete game.

import tkinter as tk 
import tkinter.font as tkFont
import os
import time
import pygame
import comm_bus




class PinballMachine():
    '''This class manages all the hardware for the pinball machine. This does not
    include the LCD screen, speakers, WiFi, or web server. It does include all nodes
    under the playing surface and in the score box area.  Its main job is
    to communicate with the nodes and provide an in-memory model of the status
    of the machine.  It also provides for simulated input for missing nodes.'''
    def __init__(self):
        pass
    def run(self):
        pass


if __name__ == "__main__":
    pbmachine = PinballMachine()
    pbmachine.run()
