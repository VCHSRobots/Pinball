# Pinball Machine Project, EPIX Robotz, Fall 2022
#
# Screen Demo

import tkinter as tk 
import tkinter.font as tkFont
import os
import time
import pygame
import random

sound_files = (
    ('MatchStart.wav', 3), 
    ('welcome_debut.m4a',4),
    ('build_season_starts.m4a',4),
    ('hit_all_epic_targets.m4a',4),
    ('1_week.m4a',4),
    ('dont_hit_the_panic_button.m4a',4),
    ('2_weeks.m4a',4),
    ('canangibu.wav',4),
    ('panic_cad_not_ready.m4a',4),
    ('3_weeks.m4a',4),
    ('panic_cnc_not_finished.m4a',4),
    ('4_weeks.m4a',4),
    ('panic_parts_out_of_stock.m4a',4),
    ('5_weeks.m4a',4),
    ('panic_programmers_sick.m4a',4),
    ('welcome_to_competition.m4a'  ,4),
    ('foul_overweight.m4a',4),
    ('MatchStart.wav', 3), 
    ('hit_targets_to_get_ranked.m4a',4),
    ('use_scouting_data.m4a',4),
    ('foul_human_player_violation.m4a',4),
    ('foul_illegal_contact.m4a',4),
    ('climb_the_ramp.m4a',4),
    ('panic_robot_is_trash.m4a',4),
    ('foul_frame_out_of_bounds.m4a',4),
    ('red_card.m4a',4),
    ('EndMatch.wav',4),
    ('get_selected_at_the_jet_bumpers.m4a',4),
    ('lv2.wav',4),
    ('made_it_to_playoffs.m4a',4),
    ('not_selected.m4a',4),
    ('seeded_47.m4a',4),
    ('foul_frame_out_of_bounds.wav',4),
    ('sonnette.wav',4),
    ('seeded_8.m4a',4),
    ('seeded_1.m4a',4) )

# ('bert.wav',4),
# ('BuildSeasonStarts.wav',4),
# ('DontHitPanicButton.wav',4),
# ('edge.wav',4),
# ('Foul_FrameOutOfBounds.wav',4),
# ('Foul_HumanPlayerViolation.wav',4),
# ('foul_human_player_voliation.wav',4),
# ('Foul_IllegalContact.wav',4),
# ('Foul_Overweight.wav',4),
# ('MatchAbort.wav',4),
# ('MatchStart.wav',4),
# ('RedCard.wav',4),

# check if 
if os.environ.get('DISPLAY','') == '':
    print('No display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

pygame.init()
sounds = []
for sname, pt in sound_files:
    s = pygame.mixer.Sound('/home/pi/pb/sounds/' + sname)
    sounds.append((s, pt))

win = tk.Tk()
win["background"] = "black"
win.config(cursor="none")
l3 = tk.Label(win, text = "57302", font=("Times New Roman bold", 400))
l3["fg"] = "white"
l3["bg"] = "black"
l3.pack();
win.attributes("-fullscreen", True)

tlast = time.monotonic()
current_sound = sounds[0]
tsound0 = tlast 
s, _ = current_sound
s.play()

cnt = 53703 
isounds = 0
while True:
    tnow = time.monotonic()
    if tnow - tlast > 1.0:
        cnt += 1
        l3["text"] = "%d" % cnt 
        tlast = tnow 
    s, pt = current_sound 
    if tnow - tsound0 > pt + 2.0:
        isounds += 1 
        if isounds >= len(sounds):
            isounds = 0;
        current_sound = sounds[isounds]
        s, _ = current_sound
        tsound0 = tnow
        s.play() 
    win.update_idletasks()
    win.update()


