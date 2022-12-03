# pb_log.py -- Log processing 
# Pinball Machine Project, EPIC Robotz, Fall 2022
# dlb

import os 
import time
import common 

if common.platform() == "real":
    log_file_path = "/home/pi/pb/logs"
else:
    log_file_path = "C:\\Users\\dalbr\\Documents\\Projects\\Epic_Robots_2023\\PinballMachine\\Software\\logs"

logfile = None
logdebug = True  # if should be logging debug messages
logterminal = True  # if should be sending to the terminal
logging_enabled = True   # if not logging at all.

def _formatted_time():
    t = time.localtime() 
    tstr = f'{t.tm_year:04}-{t.tm_mon:02}-{t.tm_mday:02} {t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}'
    return tstr

def disable():
    global logging_enabled
    logging_enabled = False 

def enable():
    global logging_enabled 
    logging_enabled = True

def log_init():
    '''Initialize the logger. Must be called at least once to enable logging to file.'''
    try:
        global logfile
        flist = os.listdir(log_file_path)
        maxnum = 0
        for f in flist:
            if not f.startswith("pb_"): continue
            if not f.endswith(".log"): continue
            try:
                num = int(f[3:8])
            except:
                continue
            if num > maxnum: maxnum = num
        maxnum += 1 
        fname = f'{log_file_path}/pb_{maxnum:05}.log'
        logfile = open(fname, "a")
        tm = _formatted_time() 
        logfile.write(f"New Sesstion started at: {tm}\n")
        logfile.write(f"File Number = {maxnum}\n")
        logfile.write("\n")
        logfile.flush()
        return
    except:
        print("!!! Unable to Open Log File.")
        logfile = None

def disable_debug():
    '''Disable logging of debug messages.'''
    global logdebug
    logdebug = False 

def enable_debug():
    '''Enable logging of debug messages.'''
    global logdebug
    logdebug = True

def disable_terminal():
    '''Disable sending log messages to terminal.'''
    global logterminal
    logterminal = False 

def enable_terminal():
    '''Enable sending log messages to terminal.'''
    global logterminal
    logterminal = True

def close():
    '''Close logging to file.  Call begin() to
    start a new file.'''
    global logfile
    if logfile is None: return
    logfile.flush()
    logfile.close()
    logfile = None
    return

def log(msg):
    '''Logs any message'''
    global logterminal, logfile, logging_enabled
    if not logging_enabled: return
    tm = _formatted_time()
    line = tm + "> " + msg
    if logfile: 
        logfile.write(line + "\n")
        logfile.flush()
    if logterminal: print(line)

def logd(msg):
    '''Logs debug msg, only if debug logging is enabled.'''
    global logterminal, logfile, logdebug, logging_enabled
    if not logging_enabled: return
    if not logdebug: return
    tm = _formatted_time()
    line = tm + " DEBUG> " + msg
    if logfile: 
        logfile.write(line + "\n")
        logfile.flush()
    if logterminal: print(line)


