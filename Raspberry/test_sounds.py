# Pinball Machine Project, EPIC Robotz, Fall 2022
#
# Screen Demo

import os
import time
import pygame
import common

sound_files = [
        "Build_1.wav",
        "Build_2.wav",
        "Build_3.wav",
        "Build_4.wav",
        "Build_5.wav",
        "Build_6.wav",
        "Climb_the_Ramp.wav",
        "Ding_1.wav",
        "Ding_2.wav",
        "Ding_JetBumper.wav",
        "Dont_Hit_Panic.wav",
        "Foul_Frame_Out_Of_Bounds.wav",
        "Foul_Human_Player_Violation.wav",
        "Foul_Illegal_Contact.wav",
        "Foul_Overweight.wav",
        "Game_Debut.wav",
        "Get_Selected_With_Jet_Bumpers.wav",
        "Hit_All_EPIC_Targets.wav",
        "Hit_Targes_To_Get_Ranked.wav",
        "Match_Start.wav",
        "Match_End.wav",
        "Not_Selected.wav",
        "Painc_Parts_Out_Of_Stock.wav",
        "Panic_CAD_Not_Ready.wav",
        "Panic_NoCNC.wav",
        "Panic_Programmers_Sick.wav",
        "Panic_Robot_Is_Trash.wav",
        "Redcard.wav",
        "Seeded_1.wav",
        "Seeded_47.wav",
        "Seeded_8.wav",
        "Target_Hit.wav",
        "Use_Scouting.wav",
        "Welcome_to_Competition.wav",
        "You_Made_It_To_Playoffs.wav"]

if common.platform() == "real": sound_path = "/home/pi/pb/sounds/"
else: sound_path = "sounds\\"

pygame.init()
sounds = []
for sname in sound_files:
    fn = sound_path + sname 
    print(fn)
    s = pygame.mixer.Sound(sound_path + sname)
    s.play() 
    time.sleep(5)



