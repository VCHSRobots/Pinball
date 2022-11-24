# arduino_reg_map.py -- Map of Arduino Registers for modules in the pinball machine
# EPIC Robotz, dlb, Nov 2022

# This table should match the code in the arduino.
REG_SIGV    =  0   # RO  Device Signature/Version.  Currently: 'e'
REG_DTME1   =  1   # RO  Device Time, Milliseconds, Byte 0, MSB
REG_DTME2   =  2   # RO  Device Time, Milliseconds, Byte 1
REG_DTME3   =  3   # RO  Device Time, Milliseconds, Byte 2
REG_DTME4   =  4   # RO  Device Time, Milliseconds, Byte 3, LSB
REG_NEO     =  5   # RW  Neo Pattern to use
REG_LAMPS   =  6   # RW  Lamps on/off status, by bits 0-5
REG_FLASH   =  7   # RW  Lamps Flash, by bits 0-5
RED_FT      =  8   # RW  Number of milliseconds for flash
REG_L1      =  9   # RW  Lamp 1 brightness 
REG_L2      = 10   # RW  Lamp 2 brightness 
REG_L3      = 11   # RW  Lamp 3 brightness 
REG_L4      = 12   # RW  Lamp 4 brightness 
REG_L5      = 13   # RW  Lamp 5 brightness 
REG_L6      = 14   # RW  Lamp 6 brightness 
REG_EXTRA   = 15   # RW  Extra Regs for any purpose (testing)
REG_E0      = 15   # RW  Extra Reg 0
REG_E1      = 16   # RW  Extra Reg 1
REG_E2      = 17   # RW  Extra Reg 2
REG_LAST    = 24   # ** Last Registor
REG_RW0     =  5   # ** First Registor where writing is allowed.

reg_table = (
    (REG_SIGV,  "SIGV" ),
    (REG_DTME1, "DTME1"),
    (REG_DTME2, "DTME2"),
    (REG_DTME3, "DTME3"),
    (REG_DTME4, "DTME4"),
    (REG_NEO,   "NEO"  ),
    (REG_LAMPS, "LAMPS"),
    (REG_FLASH, "FLASH"),
    (RED_FT,    "FT"   ),
    (REG_L1,    "L1"   ),
    (REG_L2,    "L2"   ),
    (REG_L3,    "L3"   ),
    (REG_L4,    "L4"   ),
    (REG_L5,    "L5"   ),
    (REG_L6,    "L6"   ),
    (REG_EXTRA, "EXTRA"),
    (REG_E0,    "E0"   ),
    (REG_E1,    "E1"   ),
    (REG_E2,    "E2"   ),
    (REG_LAST,  "LAST" ),
    (REG_RW0,   "RW0"  ) )

def get_reg_names():
    '''Provides a list of registor names. '''
    names = []
    for r in reg_table:
        _ , n = r 
        names.append(n)
    return names

def adr2name(i):
    '''Returns a registor's name when given it's number.'''
    for r in reg_table:
        ii, n = r
        if ii == i: return n
    return "?" 

def name2adr(n):
    '''Returns a registor's number when given it's name.'''
    i = 0
    for r in reg_table:
        i, nn = r 
        if n == nn: return i 
    return -1