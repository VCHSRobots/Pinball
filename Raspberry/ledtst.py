#! /usr/bin/python
# led.tst -- exercises the lights node.
# 
# # Pinball Machine Project, EPIC Robotz, Fall 2022
# Epic Robotz, Fall 2020
# dlb

import time
import sys
import pb_log
pb_log.disable()
import time
import common 
if common.platform() == "real":
    import comm_bus
    comm = comm_bus.CommBus()
else:
    comm = None

CMD_NEO_RESET     =   1
CMD_NEO_SINGLE    =   2
CMD_NEO_SOLID     =   3
CMD_NEO_WIPE      =   4
CMD_NEO_CHASE     =   5
CMD_NEO_BLINK     =   6
CMD_NEO_DEMO      =   7
CMD_LAMP_SOLID    =   8
CMD_LAMP_FLASH    =   9
CMD_LAMP_MODULATE =  10

def submit(cmd):
    rsp = comm.node_io(3, cmd)
    if rsp is None:
        print("No response from light node.")
    return

def run(args):
    comm.begin()
    iloop = 0 
    nbus, nerr = 0, 0
    while True:
        #cmd = [CMD_NEO_BLINK, 255, 0, 0, 255, 255, 255, 1, 1, 4]
        cmd = [CMD_NEO_CHASE, 255, 0, 0, 255, 255, 255, 2, 4]
        #cmd = [CMD_NEO_DEMO, 255, 0, 0, 255, 255, 255, 2, 4]
        #rsp = comm.node_io(3, cmd)
        #rsp = comm.node_io(3)
        # nbus += 1
        # if rsp == None:
        #     nerr += 1
        #     print(f"No response from light node. bus={nbus}, nerr={nerr}")
        # time.sleep(0.01)
        if iloop == 0: c = (255, 0, 0)
        if iloop == 1: c = (0, 255, 0)
        if iloop == 2: c = (0, 0, 255)
        iloop += 1 
        if iloop >= 3: iloop = 0
        ipx = 0
        while True:
            r1, g1, b1 = c 
            cmd = [CMD_NEO_SINGLE, r1, g1, b1, r1, g1, b1, ipx, 30, 30]
            rsp = comm.node_io(3, cmd)
            nbus += 1
            if rsp == None:
                nerr += 1
                print(f"No response from light node. bus={nbus}, nerr={nerr}")
            ipx += 1
            if ipx >= 31: break 
            time.sleep(0.05)
        #time.sleep(0.2)


if __name__ == "__main__":
    run(sys.argv)