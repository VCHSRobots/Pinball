import keyboard
import time

is_done = False

def on_spacepress(key):
    is_done = True
keyboard.add_hotkey("space", on_spacepress)

tlast = time.monotonic()

while True:
    if is_done: 
        break
    tnow = time.monotonic() 
    if tnow - tlast > 1.0:
        print("Still Waiting.")
        tlast = tnow

print("All done.")
