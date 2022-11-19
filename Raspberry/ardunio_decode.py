# arduino_decode.py -- Translate raw data from the arduino
# EPIC Robotz, dlb, Nov 2022

import arduino_reg_map as reg
from utils import * 

def data_to_dict(strdata):
    ''' Converts the input list of bytes from the arduino's registers
    to a dictionary containing  parameter values.  The Key names
    mostly follow the register names.  See code below for actual
    key names. '''
    data = []
    words = strdata.split()
    for w in words:
        try:
            v = int(w)
        except ValueError:
            v = 0
        data.append(v)
    dout = {}
    if len(data) >= reg.REG_SIGV:
        dout["SIGV"] = "%c" % data[reg.SIGV]
    if len(data) > reg.REG_DTME4:
        u0, u1, u2, u3 = data[reg.DTME1], data[reg.DTME2], data[reg.DTME3], data[reg.DTME4]
        dout["DTME"] = fourbytestolong(u3, u2, u1, u0)


    if len(data) > reg.REG_E0:
        dout["E0"] = data[reg.REG_E0]
    if len(data) > reg.REG_E1:
        dout["E1"] = data[reg.REG_E1] 
    if len(data) > reg.REG_E2:
        dout["E2"] = data[reg.REG_E2]
    return dout