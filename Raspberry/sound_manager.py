# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# sound_manager.py -- manages the sounds for the game
#

import pygame as pyg
import common
from pb_log import log
import time


if common.platform() == "real":
    sound_path = "/home/pi/pb/sounds/"
else:
    sound_path = "C:\\Users\\dalbr\\Documents\\Projects\\Epic_Robots_2023\\PinballMachine\\Software\\Pinball\\Raspberry\\sounds\\"

S_DING_KICKER = 1
S_DING_LANE = 2
S_DING_JET_BUMPERS = 3
S_DING_TARGET = 4
S_DING_DROPHOLE = 5
S_MATCH_START = 6
S_MATCH_END = 7
S_BUILD_0 = 8
S_BUILD_1 = 9
S_BUILD_2 = 10
S_BUILD_3 = 11
S_BUILD_4 = 12
S_BUILD_5 = 13
S_BUILD_6 = 14
S_FOUL_1 = 15
S_FOUL_2 = 16
S_FOUL_3 = 17
S_FOUL_4 = 18
S_HINT_0 = 19
S_HINT_1 = 20
S_HINT_2 = 21
S_HINT_3 = 22
S_HINT_4 = 23
S_PANIC_0 = 24
S_PANIC_1 = 25
S_PANIC_2 = 26
S_PANIC_3 = 27
S_PANIC_4 = 28
S_PANIC_5 = 29
S_REDCARD = 30
S_NOT_SELECTED = 31
S_SEEDED_1 = 32
S_SEEDED_47 = 33
S_SEEDED_8 = 34
S_COMPETITION = 35
S_PLAYOFFS = 36
S_BALL_LOST = 37
S_LANE_AWARD = 38
S_WIN_TRUMPET_1 = 39
S_WIN_TRUMPET_2 = 40

builds = [S_BUILD_0, S_BUILD_1, S_BUILD_2, S_BUILD_3, S_BUILD_4, S_BUILD_5]
fouls = [S_FOUL_1, S_FOUL_2, S_FOUL_3, S_FOUL_4]
panics = [S_PANIC_0, S_PANIC_1, S_PANIC_2, S_PANIC_3, S_PANIC_4, S_PANIC_5]

sounds = [
        (S_DING_KICKER, "Ding_1.wav"),
        (S_DING_LANE, "Ding_2.wav"),
        (S_DING_JET_BUMPERS, "Ding_JetBumper.wav"),
        (S_DING_TARGET, "Target_Hit.wav"),
        (S_DING_DROPHOLE, "Happy_Horn.wav"),
        (S_MATCH_START, "Match_Start.wav"),
        (S_MATCH_END, "Match_End.wav"),
        (S_BUILD_0, "Game_Debut.wav"),
        (S_BUILD_1, "Build_1.wav"),
        (S_BUILD_2, "Build_2.wav"),
        (S_BUILD_3, "Build_3.wav"),
        (S_BUILD_4, "Build_4.wav"),
        (S_BUILD_5, "Build_5.wav"),
        (S_BUILD_6, "Build_6.wav"),
        (S_HINT_0, "Hit_All_EPIC_Targets.wav"),
        (S_HINT_1, "Hit_Targets_To_Get_Ranked.wav"),
        (S_HINT_2, "Get_Selected_With_Jet_Bumpers.wav"),
        (S_HINT_3, "Climb_the_Ramp.wav"),    # "for more ranking points"
        (S_HINT_4, "Use_Scouting.wav"),
        (S_FOUL_1, "Foul_Frame_Out_Of_Bounds.wav"),
        (S_FOUL_2, "Foul_Human_Player_Violation.wav"),
        (S_FOUL_3, "Foul_Illegal_Contact.wav"),
        (S_FOUL_4, "Foul_Overweight.wav"),
        (S_PANIC_0, "Dont_Hit_Panic.wav"),
        (S_PANIC_1, "Painc_Parts_Out_Of_Stock.wav"),
        (S_PANIC_2, "Panic_CAD_Not_Ready.wav"),
        (S_PANIC_3, "Panic_NoCNC.wav"),
        (S_PANIC_4, "Panic_Programmers_Sick.wav"),
        (S_PANIC_5, "Panic_Robot_Is_Trash.wav"),
        (S_REDCARD, "Redcard.wav"),
        (S_NOT_SELECTED, "Not_Selected.wav"),
        (S_SEEDED_1, "Seeded_1.wav"),
        (S_SEEDED_47, "Seeded_47.wav"),
        (S_SEEDED_8, "Seeded_8.wav"),
        (S_COMPETITION, "Welcome_to_Competition.wav"),
        (S_PLAYOFFS, "You_Made_It_To_Playoffs.wav"),
        (S_BALL_LOST, "Beep.wav"),
        (S_LANE_AWARD, "Chime_1.wav"),
        (S_WIN_TRUMPET_1, "WinTrumpet_1.wav"),
        (S_WIN_TRUMPET_2, "WinTrumpet_2.wav")]

def get_all_sounds():
    '''Returns a list of ids for all sounds in the system.'''
    ids = []
    for i, f in sounds: ids.append(i)
    return ids

def get_sound_file(id):
    '''Given a id, returns a sound file name, with path,
    or None if no matching file.'''
    for i, f in sounds:
        if i == id: return f
    return None
    
class SoundManager():
    def __init__(self):
        self._sounds = {}

    def load_sounds(self):
        log("Loading Sounds")
        self._sounds = {} 
        for id in get_all_sounds():
            f = get_sound_file(id) 
            if f is None: continue
            fpath = sound_path + f 
            try:
                s = pyg.mixer.Sound(fpath) 
                self._sounds[id] = (s, f)
            except Exception as err:
                log(f"Error: Sound for id={id}, file={fpath} not loaded. Reason: {err}")
                self._sounds[id] = None 
        
    def play(self, id):
        if id in self._sounds:
            if self._sounds[id] is not None:
                s, n = self._sounds[id]
                s.play()
                log(f"Playing Sound id ({id}): {n}") 
        else:
            log(f"Warning: Attempt to play non-existing sound.  id={id}.")
    
if __name__ == "__main__" :
    pyg.init() 
    sm = SoundManager()
    # for id in get_all_sounds():
    #     file = get_sound_file(id)
    #     print(f"Playing {file}.")
    #     sm.play(id)
    #     time.sleep(5)
    sm.play(S_BUILD_6)
    time.sleep(5)



                






