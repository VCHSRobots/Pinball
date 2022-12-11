# pb_log.py -- Log processing 
# Pinball Machine Project, EPIC Robotz, Fall 2022
# dlb

import os 
import time
import common 

if common.platform() == "real":
    log_file_path = "/home/pi/pb/logs"
    log_separator = "/"
else:
    log_file_path = "C:\\Users\\dalbr\\Documents\\Projects\\Epic_Robots_2023\\PinballMachine\\Software\\logs"
    log_separator = "\\"

logfile = None
log_current_date = ""
logdebug = True  # if should be logging debug messages
logterminal = True  # if should be sending to the terminal
logging_enabled = True   # if not logging at all.

def _formatted_time():
    ''' Returns a tuple of the formatted time, and the formatted date for file name'''
    tme = time.time()
    t = time.localtime(tme)
    msec = int((tme - int(tme)) * 1000) 
    tm = f'{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}.{msec:03}'
    tdate = f'{t.tm_year:04}-{t.tm_mon:02}-{t.tm_mday:02}'
    return tdate, tm

def disable():
    global logging_enabled
    logging_enabled = False 

def enable():
    global logging_enabled 
    logging_enabled = True

# def get_last_log_file():
#     flist = os.listdir(log_file_path)
#     maxnum = 0
#     last_file = None
#     for f in flist:
#         if not f.startswith("pb_"): continue
#         if not f.endswith(".log"): continue
#         try:
#             num = int(f[3:8])
#         except:
#             continue
#         if num > maxnum: 
#             maxnum = num
#             last_file = f
#     if last_file is None: return None
#     return log_file_path + log_separator + last_file

def _reopen(td, tm):
    global logfile, log_current_date
    if td == log_current_date: return
    try:
        if logfile: logfile.close() 
        fname = f'{log_file_path}{log_separator}pb_{td}.log'
        logfile = open(fname, "a")
        logfile.write("\n")
        logfile.write(f"New logfile created at: {td} {tm}\n")
        logfile.write(f"Log File Name = {fname}\n")
        logfile.write(f"\n")
        logfile.write(f"Session continues from previous logfile.\n")
        logfile.write(f"\n")
        logfile.flush()
        log_current_date = td
    except Exception as err:
        print(f"!!! Unable to Open Log File.  Reason: {err}")
        logfile = None

def log_init():
    '''Initialize the logger. Must be called at least once to enable logging to file.'''
    try:
        global logfile, log_current_date
        td, tm = _formatted_time()
        fname = f'{log_file_path}{log_separator}pb_{td}.log'
        logfile = open(fname, "a")
        logfile.write(f"\n")
        logfile.write(f"New Session started at: {td} {tm}\n")
        logfile.write(f"Log File Name = {fname}\n")
        logfile.write("\n")
        logfile.flush()
        log_current_date = td
        return
    except Exception as err:
        print(f"!!! Unable to Open Log File.  Reason: {err}")
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
    '''Close logging to file. Call log_init() to
    reopen and continue logging to a file.'''
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
    td, tm = _formatted_time()
    _reopen(td, tm)
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
    td, tm = _formatted_time()
    _reopen(td, tm)
    line = tm + " DEBUG> " + msg
    if logfile: 
        logfile.write(line + "\n")
        logfile.flush()
    if logterminal: print(line)


