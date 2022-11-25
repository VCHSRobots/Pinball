# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# screen.py -- manages the screen for the game
# 
# This file/package is only concerned with 
# the display on the screen.  All game logic
# is done elsewhere.
# 

import pygame as pyg
import time
import sys
import os
from pb_log import log
import common

class Score():
    ''' Keeps track of the current score. '''
    main_score = 3409
    high_score = 12043
    number_of_balls = 2
    err_msg = "Node 5 (kickers) not responding." 
    game_phase = " Build Week 1" 
    game_hint1 = "Design your robot"
    game_hint2 = "at the Jet Bumpers!"
    game_hint3 = "Try Hard!"
    robot_parts = 3
    day = 0

class ScreenCalendar():
    '''Draws a calendar to represent time passage.'''
    def __init__(self):
        self._font  = pyg.font.SysFont("freemono", 20)
        c = (255, 255, 0)
        cback = (31, 61, 122)
        self._months = []
        for month, ndays in [("January", 31), ("Feburary", 28)]:
            s = pyg.Surface((310, 278))
            s.fill(cback) 
            ss = self._font.render(month, True, c, cback)
            s.blit(ss, (70, 10))
            for ix in range(8):
                x = ix * 38
                pyg.draw.lines(s, c, False, [(x, 66), (x, 256)])
            for iy in range(6):
                y = iy * 38 + 66
                pyg.draw.lines(s, c, False, [(0, y), (266, y)]) 
            for i, t in enumerate(["S", "M", "T", "W", "T", "F", "S"]):
                ix = i * 38 + 16
                ss = self._font.render(t, True, c, cback)
                s.blit(ss, (ix, 40))
            for i in range(ndays):
                iyc = int(i / 7)
                ixc = i - (iyc * 7)
                t = f"{i+1:2}"
                x, y = ixc*38 + 5, iyc*38 + 68
                ss = self._font.render(t, True, c, cback)
                s.blit(ss, (x, y))
            self._months.append(s)

    def render(self, surface, day):
        ss = None
        if day <= 0: 
            surface.blit(self._months[0], (220, 730)) 
            return
        if day >= 1 and day <= 31: 
            ss = self._months[0].copy() 
            iday = day
        if day >= 32 and day <= 59:
            ss = self._months[1].copy() 
            iday = day - 31
        if ss is None: 
            ss = self._months[1].copy()
            iday = 28
        for i in range(iday):
            iyc = int(i / 7)
            ixc = i - (iyc * 7)
            x, y = ixc*38, iyc*38 + 68
            pyg.draw.line(ss, (255, 255, 0), (x, y), (x + 38, y + 38), 3)
            pyg.draw.line(ss, (255, 255, 0), (x + 38, y), (x, y + 38), 3)
        surface.blit(ss, (220, 730)) 

class ScreenBox():
    '''Manages one box'''
    def __init__(self, loc, size, nchars, border = True, fg_color=(255, 255, 255),
                 bg_color = (0, 0, 0)):
        '''Initializes a ScreenBox. loc is an x,y tuple of
        the upper left corner of the box, size is the height
        of the chars, in pixels. nchars is the number of
        characters the box should hold, and border is used
        to draw a rect around the box area.'''
        self._text = ""
        self._loc = loc 
        self._size = size 
        self._boarder = border
        self._fg_color = fg_color
        self._bg_color = bg_color
        self._padx = 10
        self._pady =  8
        self._myfont = pyg.font.SysFont("freemono", size, bold=True)
        tmpstr = ""
        for i in range(nchars): tmpstr += "9"
        fs = self._myfont.render(tmpstr, True, self._fg_color, self._bg_color)
        self._boxsize = fs.get_width() + self._padx, fs.get_height() + self._pady 
        self._backbox = None

    def set_colors(self, fg_color, bg_color = None):
        self._fgcolor = fg_color
        if bg_color is not None: self._bg_color = bg_color
        self._backbox = None

    def set_text(self, text):
        self._text = text
    
    def render(self, surface):
        if self._backbox is None:
            self._backbox = pyg.Surface(self._boxsize, 0, surface)
            self._backbox.fill(self._bg_color)
            w, h = self._boxsize
            if self._boarder:
                r1 = pyg.Rect(1, 1, w-2, h-2)
                pyg.draw.rect(self._backbox, self._fg_color, r1, 2)
        surface.blit(self._backbox, self._loc) 
        x, y = self._loc 
        loc2 = int(x + self._padx/2), int(y + self._pady/2) 
        fs = self._myfont.render(self._text, True, self._fg_color, self._bg_color)
        surface.blit(fs, loc2)

class ScreenRobotParts():
    '''Class to manage drawing the robot animation.'''
    def __init__(self):
        self._partsurfaces = []
        if common.platform() == "real": self._partpath = "/home/pi/pb/assets/"
        else: self._partpath = "assets"
        self._partfiles = ["RobotParts_1.gif", "RobotParts_2.gif", "RobotParts_3.gif", "RobotParts_4.gif",
                           "RobotParts_5.gif", "RobotParts_6.gif", "RobotParts_7.gif"]
        try:
            for f in self._partfiles:
                ff = os.path.join(self._partpath, f) 
                s = pyg.image.load(ff)
                self._partsurfaces.append(s)
        except:
            self._partsurfaces = None 
            log("Unable to load Robot Part Anaimation files.") 
        
    def render(self, surface, partnum):
        r = pyg.Rect(566, 757, 360, 280)
        pyg.draw.rect(surface, (21, 61, 122), r)
        if self._partsurfaces is None: return
        if partnum <= 0: return 
        if partnum >= 7: partnum = 6 
        surface.blit(self._partsurfaces[partnum], (566, 757))
        
class Screen():
    '''This class manages the screen for the pinball machine.  It contains
    functions for doing all drawing on the screen.  It does not do any 
    game logic.  Use score() to change the score, then use update()
    to draw the score onto the screen.'''

    def __init__(self):
        pyg.init()
        if common.platform() == "real":
            self._size = (0, 0)
            self._screen = pyg.display.set_mode(self._size, pyg.HWSURFACE | pyg.FULLSCREEN | pyg.NOFRAME)
        else:
            self._size = (1920, 1080)
            self._screen = pyg.display.set_mode(self._size, 0)

        # print("Screen Size: ", pyg.display.Info())

        self._robotparts = ScreenRobotParts()
        self._calendar = ScreenCalendar()
        self._running = True
        self._score = Score() 
        self._elements = {} 
        self._elements["MainScore"] = ScreenBox((200, 40), 400, 6)
        self._elements["NBalls_Label"] = ScreenBox((1500, 550), 50, 5, border=False, fg_color=(200, 200, 200), bg_color=(21, 61, 122))
        self._elements["NBalls"]    = ScreenBox((1500, 610), 120, 2)
        self._elements["HighScore_Label"] = ScreenBox((200, 550), 50, 10, border=False, fg_color=(200, 200, 200), bg_color=(21, 61, 122))
        self._elements["HighScore"] = ScreenBox((200, 610), 90, 6)
        self._elements["GamePhase"] = ScreenBox((570, 612), 100, 15, border=False, fg_color=(255, 255, 0), bg_color=(21, 61, 122))
        self._elements["GameHint1"] = ScreenBox((1000, 820), 60, 25, border=False, fg_color=(255, 255, 0), bg_color=(21, 61, 122))
        self._elements["GameHint2"] = ScreenBox((1000, 890), 60, 25, border=False, fg_color=(255, 255, 0), bg_color=(21, 61, 122))
        self._elements["GameHint3"] = ScreenBox((1000, 960), 60, 25, border=False, fg_color=(255, 255, 0), bg_color=(21, 61, 122))
        self._elements["ErrMsg"] = ScreenBox((200, 1030), 30, 80, border=False, fg_color=(255, 0, 0), bg_color=(21, 61, 122))

    def score(self):
        return self._score

    def reset_score(self):
        self._score.main_score = 0 
        self._score.number_of_balls = 0 
        self._score.high_score = 0 
        self._score.game_phase = ""
        self._score.game_hint1 = ""
        self._score.game_hint2 = ""
        self._score.game_hint3 = ""
        self._score.err_msg = ""
        self._score.robot_parts = 0 
        self._score.day = 0

    def report_score(self):
        print(f"Main Score: {self._score.main_score}")
        print(f"High Score: {self._score.high_score}")
        print(f"Number of Balls: {self._score.number_of_balls}")
        print(f"Error Message {self._score.err_msg}")
        print(f"Game Phase: {self._score.game_phase}")

    def _set_text(self):
        for k in self._elements:
            sb = self._elements[k];
            if k == "MainScore": sb.set_text(f"{self._score.main_score:06}")
            if k == "NBalls_Label": sb.set_text("Balls")
            if k == "NBalls": sb.set_text(f"{self._score.number_of_balls:02}")
            if k == "HighScore_Label": sb.set_text("High Score")
            if k == "HighScore": sb.set_text(f"{self._score.high_score:06}")
            if k == "GamePhase": sb.set_text(self._score.game_phase)
            if k == "GameHint1": sb.set_text(self._score.game_hint1)
            if k == "GameHint2": sb.set_text(self._score.game_hint2)
            if k == "GameHint3": sb.set_text(self._score.game_hint3)
            if k == "ErrMsg": sb.set_text(self._score.err_msg)
      
    def update(self):
        '''Updates the screen.'''
        self._set_text()
        self._screen.fill((21, 61, 122))
        for ename in self._elements:
            eval = self._elements[ename] 
            eval.render(self._screen)
        self._robotparts.render(self._screen, self._score.robot_parts)
        self._calendar.render(self._screen, self._score.day)
        pyg.display.update()
        return True

if __name__ == "__main__" :
    scrn = Screen() 
    tlast = time.monotonic()
    cntr = 0  
    ipart_cntr = 0
    while(True):
        time.sleep(0.1)
        pyg.event.pump()
        for e in pyg.event.get():
            if e.type == pyg.QUIT or (e.type == pyg.KEYUP and e.key == pyg.K_ESCAPE): 
                pyg.quit()
                sys.exit() 
        cntr += 1
        scrn.score().main_score = cntr
        scrn.score().number_of_balls = 7
        scrn.score().day += 1
        if scrn.score().day > 70: scrn.score().day = -4
        ipart_cntr += 1 
        if ipart_cntr >= 0:
            scrn.score().robot_parts += 1 
            if scrn.score().robot_parts > 8: scrn.score().robot_parts = 0
        scrn.update()
    