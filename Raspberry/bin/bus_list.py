#! /usr/bin/python3
# bus_list.py -- Scans the bus and lists devices
#
# Pinball Machine Project, EPIC Robotz, Fall 2022
# Epic Robotz, Fall 2020
# dlb
#
#
import comm_bus
import pb_log
import time

pb_log.log_init()
pb_log.disable_debug()
pb_log.disable_terminal()

bus = comm_bus.CommBus() 
bus.begin()

nodes = [(2, "Light Node in Score Box"),
         (3, "Light Node in Play Field"),
         (4, "Flipper Node"), 
         (5, "Jet Bumpers Node"),
         (6, "Kicker Node"),
         (7, "Lane Sensor Node"),
         (8, "Target Node"),
         (9, "Test Node")]

print("")
print("Node Addr  Found  Description")
print("---------  -----  -----------")

for addr, desc in nodes:
    cmd = [100, 20]  # echo command
    ans = bus.node_io(addr, cmd)
    found = False  
    if ans is None:
        # Failed.  Try again in 0.5 secs
        time.sleep(0.5)
        ans = bus.node_io(addr, cmd) 
    if ans is None: 
        print(f"{addr:6}            {desc}")
    else:
        print(f"{addr:6}      Yes   {desc}")

print("")
bus.close() 

