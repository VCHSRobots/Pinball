# arduino_pb.py -- low level access to Arduino Modules on Pinball machine
# EPIC Robotz, dlb, Nov 2022

import sys
from smbus import SMBus
import time
import arduino_reg_map as reg
import utils
import random

default_addr = 0x8 # default bus address of ardunio
default_bus = 1 # indicates /dev/ic2-1

class Arduino_pb():
    ''' Manages arduino for pinball modules (units) '''
    def __init__(self, address=default_addr, bus_number=default_bus, bus_monitor=None):
        self._addr = address
        self._bus_number = bus_number
        print("Initing the SMBus().")
        self._bus = SMBus(bus_number)
        print("Done initing the SMBus.")
        self._bus_monitor = bus_monitor

    def writereg(self, regadr, dat):
        ''' Reads a register from the arduino. '''
        try:
            self._bus.write_byte_data(self._addr, regadr, dat)
            if self._bus_monitor: self._bus_monitor.on_success()
        except IOError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise
        except OSError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise
    
    def readreg(self, regadr):
        ''' Writes to a register on the arduino. '''
        try:
            dat = self._bus.read_byte_data(self._addr, regadr)
            if self._bus_monitor: self._bus_monitor.on_success()
            return dat
        except IOError:    
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise
        except OSError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise

    def test_health(self):
        ''' Tests the health of the i2c bus and the arduino by writing
        to the spare register and reading it back.  If all okay,
        True is returned. '''
        v = random.randint(0,255)
        try:
            self.writereg(reg.REG_EXTRA, v)
            time.sleep(0.00025)
            vgot = self.readreg(reg.REG_EXTRA)
            if vgot != v: return False
            return True
        except OSError:
            return False

    def get_reg_names(self):
        '''Provides a list of registor names. '''
        return reg.get_reg_names()

    def adr2name(self, i):
        '''Returns a registor's name when given it's number.'''
        return reg.adr2name(i)

    def name2adr(self, n):
        '''Returns a registor's number when given it's name.'''
        return reg.name2adr(n)

    def get_version(self):
        ''' Returns the signature byte on the arduino as (okayflag, char)
        where okayflag is True if all is okay, and char is the signature byte.'''
        try:
            id = self.readreg(reg.REG_SIGV)
        except IOError:
            return False, 0
        return True, id

    def get_timestamp_bytes(self):
        ''' Returns the individule bytes that make up the timestamp, 
        and returns (okayflag, tuple_of_bytes), where okayflag is True
        if all is okay, and tuple_of_bytes contains 4 bytes, with the
        LSB first. '''
        try:
            u0 = self.readreg(reg.REG_DTME1)
            u1 = self.readreg(reg.REG_DTME2)
            u2 = self.readreg(reg.REG_DTME3)
            u3 = self.readreg(reg.REG_DTME4)
        except IOError:
            return False, (0, 0, 0, 0)
        return True, (u0, u1, u2, u3)

    def get_timestamp(self):
        ''' Returns the time count (ms since power up) from the arduino
        as (okayflag, tme), where okayflag is True if all is okay, and
        tme is the timestamp from the arduino in milliseconds since 
        arduino powerup or reset.  '''
        okay, blist = self.get_timestamp_bytes()
        if not okay: return False, 0
        u0, u1, u2, u3 = blist
        tt = utils.fourbytestolong(u3, u2, u1, u0)
        return True, tt

    def get_all(self):
        ''' Reads all the registers in the arduino and returns them as
        (okayflag, bytes) where okayflag is True if nothing goes wrong,
        and bytes is a list of byte values. '''
        d = []
        try:
            for i in range(reg.REG_LAST + 1):
                v = self.readreg(i)
                d.append(v)
        except:
            return (False, [0 for _ in range(reg.REG_LAST + 1)])
        return True, d