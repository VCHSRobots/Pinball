# test_comm_bus.py -- test comm bus over many cycles.

import comm_bus as bus 
import pb_log
from pb_log import log


pb_log.log_init()
pb_log.disable_debug()
pb_log.disable_terminal()
log('Testing comm bus.')
b = bus.CommBus()
b.begin()

# assume there are three nodes, addresses 2,3 and 4, and that
# they always return "abc".
try:
    nfails = 0
    ncycles = 0
    iside = 0
    while True:
        iside += 1
        if iside >= 3: iside = 0
        adr = 0
        if iside == 0: adr = 2
        if iside == 1: adr = 3
        if iside == 2: adr = 4
        ans = b.node_io(adr)
        if ans is None: 
            nfails += 1
        else:
            if len(ans) != 3: nfails += 1
            else:
                if ans[0] != 97 or ans[1] != 98 or ans[2] != 99: nfails += 1
        ncycles += 1
        if ncycles % 100 == 0:
            msg = f"{ncycles:06d} cycles.  {nfails:6d}  fails. "
            log(msg) 
            print(msg)
except KeyboardInterrupt:
    pb_log.close()
