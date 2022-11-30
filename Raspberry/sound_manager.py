# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# sound_manager.py -- manages the sounds for the game
#

import pygame as pyg
import common
from pb_log import log
import time

if common.platform == "real":
    sound_path = "/home/pi/pb/sounds/"
else:
    sound_path = "C:\\Users\\dalbr\\Documents\\Projects\\Epic_Robots_2023\\PinballMachine\\Software\\Pinball\\Raspberry\\sounds\\"

S_DING_KICKER = 1
S_DING_LANE = 2
S_DING_JET_BUMPERS = 3
S_DING_TARGET = 4
S_MATCH_START = 5
S_MATCH_END = 6
S_BUILD_0 = 7
S_BUILD_1 = 8
S_BUILD_2 = 9
S_BUILD_3 = 10
S_BUILD_4 = 11
S_BUILD_5 = 12
S_BUILD_6 = 13
S_FOUL_1 = 14
S_FOUL_2 = 15
S_FOUL_3 = 16
S_FOUL_4 = 17
S_HINT_0 = 18
S_HINT_1 = 19
S_HINT_2 = 20
S_HINT_3 = 21
S_HINT_4 = 22
S_PANIC_0 = 23
S_PANIC_1 = 24
S_PANIC_2 = 25
S_PANIC_3 = 26
S_PANIC_4 = 27
S_PANIC_5 = 28
S_REDCARD = 29
S_NOT_SELECTED = 30
S_SEEDED_1 = 31
S_SEEDED_47 = 32
S_SEEDED_8 = 33
S_COMPETITION = 34
S_PLAYOFFS = 35

builds = [S_BUILD_0, S_BUILD_1, S_BUILD_2, S_BUILD_3, S_BUILD_4, S_BUILD_5]
fouls = [S_FOUL_1, S_FOUL_2, S_FOUL_3, S_FOUL_4]
panics = [S_PANIC_0, S_PANIC_1, S_PANIC_2, S_PANIC_3, S_PANIC_4, S_PANIC_5]

sounds = [
        (S_DING_KICKER, "Ding_1.wav"),
        (S_DING_LANE, "Ding_2.wav"),
        (S_DING_JET_BUMPERS, "Ding_JetBumper.wav"),
        (S_DING_TARGET, "Target_Hit.wav"),
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
        (S_PLAYOFFS, "You_Made_It_To_Playoffs.wav")]


def get_all_sounds():
    '''Returns a list of ids for all sounds in the system.'''
    ids = []
    for i, f in sounds: ids.append(i)
    return ids

def get_sound_file(id):
    '''Given a id, returns a sound file name, with path,
    or None if no matching file.'''
    for i, f in sounds:
        if i == id:
            return sound_path + f
    return None
    
class SoundManager():
    def __init__(self):
        self._load_sounds() 

    def _load_sounds(self):
        log("Loading Sounds")
        self._sounds = {} 
        for id in get_all_sounds():
            f = get_sound_file(id) 
            if f is None: continue 
            try:
                s = pyg.mixer.Sound(f) 
                self._sounds[id] = s
            except Exception as err:
                log(f"Error: Sound for id={id}, file={f} not loaded. Reason: {err}")
                self._sounds[id] = None 
        
    def play_sound(self, id):
        if id in self._sounds:
            if self._sounds[id] is not None:
                self._sounds[id].play() 
        else:
            log(f"Warning: Attempt to play non-existing sound.  id={id}.")
    

            
if __name__ == "__main__" :
    pyg.init() 
    sm = SoundManager()
    for id in get_all_sounds():
        file = get_sound_file(id)
        print(f"Playing {file}.")
        sm.play_sound(id)
        time.sleep(5)



                






