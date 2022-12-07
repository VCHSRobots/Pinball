#  commbus.py -- Communications Bus Manager for Pi
#  Pinball Machine Project, EPIC Robotz, Fall 2022
#  dlb
#
#  Here, we try to manage all interaction with the
#  nodes.

import serial
import time
import RPi.GPIO as gpio
from pb_log import log, logd

_tx_enable_pin = 12  # This is pin 12 on the header, labeld as GPIO18

class CommBus():
    ''' Manages comm bus for all nodes in pinball machine. '''
    def __init__(self):
        self._ser = None
        self._txon = False
        self._tm_last_msg = time.monotonic() - 1.0
        self._logging = False       # Turn off most common log outputs
        self.clear_counts()

    def clear_counts(self):
        self._bus_cycles = 0        # Total number of bus IO operations attempted
        self._no_response_errs = 0  # Number of non-responsive queries
        self._checksum_errs = 0     # Number of rejected msg due to checksum mismatch
        self._write_errs = 0        # Errors during writing to bus (serious, should not happen)
        self._protocol_errs = 0     # Errors due to bad fist byte

    def begin(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        gpio.setup(_tx_enable_pin, gpio.OUT, initial=gpio.LOW)
        self._ser = serial.Serial("/dev/ttyAMA0", baudrate=115200, write_timeout=0.060, timeout=0, parity='N', stopbits=1)

    def enable_logging(self):
        self._logging = True

    def disable_logging(self):
        self._logging = False

    def report(self):
        ''' Returns a map of stats.'''
        rp = {} 
        rp["Bus Cycles"] = self._bus_cycles
        rp["Response Errors"] = self._no_response_errs
        rp["Checksum Errors"] = self._checksum_errs
        rp["Write Errors"] = self._write_errs
        rp["Protocall Errors"] = self._protocol_errs
        return rp

    def _enable_tx(self):
        gpio.output(_tx_enable_pin, gpio.HIGH)

    def _disable_tx(self):
        gpio.output(_tx_enable_pin, gpio.LOW)

    def _checksum(self, msg, nmsg):
        sum = 0
        for i, v in enumerate(msg):
            if i >= nmsg: 
                break
            sum += v
        sum = sum & 0x00FF
        return sum

    def close(self):
        ''' Shuts down the Serial port.  Must use begin() to restart
        after this call.'''
        if (self._ser):
            self._ser.close()
            self._ser = None

    def _bytes_to_str(self, data):
        n = len(data) 
        if n > 10: n = 10
        sout = ""
        for i in range(n):
            if sout != "": sout += ", "
            sout = sout + f'{data[i]:02x}'
        return sout

    def t_us(self):
        return int(time.monotonic_ns() / 1000)

    def node_io(self, addr, data=None):
        ''' Executes an IO cycle on the given node, with the given data.
        The data should not be more than 15 bytes.  The data can be None.
        It returns a bytearray of the received data (not the entire msg),
        or None on error. This call can block for up to about 10 ms.'''

        # First, prepare the out-going message...
        if data is None: data = bytearray(0)
        ndat = len(data)
        if ndat > 15: raise ValueError
        nmsg = ndat + 3
        out_bytes = bytearray(nmsg)
        out_bytes[0] = ord('E')
        out_bytes[1] = (addr << 4 | ndat) & 0x00FF
        for i, v in enumerate(data):
            if i > 15: break
            out_bytes[i + 2] = v & 0x00FF
        cksum = self._checksum(out_bytes, nmsg - 1)
        out_bytes[nmsg - 1] = cksum

        # If not enough time has elapsed since our last msg,
        # delay here.
        tnow = time.monotonic()
        elp = tnow - self._tm_last_msg
        if elp < 0.010:
            twait = 0.010 - elp
            time.sleep(twait)
        
        # Now, clear out any crud on the receive line.
        self._ser.reset_input_buffer()

        trecord = []
        tr0 = self.t_us()
        self._bus_cycles += 1
        # Send the message.  Do this by first enabling the transmitter.
        try:
            self._enable_tx() 
            trecord.append(self.t_us() - tr0)
            self._txon = True 
            nw = self._ser.write(out_bytes)  # does not block!
            trecord.append(self.t_us() - tr0)
            # self.ser.flush()  # This should have worked, but
            # flush takes way too long, over 27 ms!
            # So, here we do a kludge...  Cal time it should have
            # taken, add about .25ms, and wait.
            twait = (len(out_bytes) * 10 / 115200.0) + 0.0001
            time.sleep(twait)
            trecord.append(self.t_us() - tr0)
        except Exception as err:
            # This is probably some sort of write timeout.  It
            # should never happen.
            log(f'Serious error with com port. Write fail.')
            log(f'Error {type(err)}: {str(err)}')
            self._disable_tx()
            self._write_errs += 1
            return None
        trecord.append(self.t_us() - tr0)
        self._disable_tx()
        trecord.append(self.t_us() - tr0)
        logd(f'times = {trecord}')
        if nw != nmsg:
            log("Serious error with com port. Write fail.")
            log(f'All bytes not written.  Tried to send {nmsg} bytes, but {nw} bytes reported.')
            self._write_errs += 1
            return None

        # Go into receive mode.  When real RS-485 is used, we should see two
        # messages: the one we wrote, and the one from the node we want to talk to.
        # Our msg starts with big "E", and the node msg starts with "e".
        # Note, at 115200 baud, two 18 byte msg should take about 3ms. The node should respond in 4ms.
        # If this takes more than 10ms, something is wrong.
        tsent = time.monotonic()  # the time we delivered the command message
        self._tm_last_msg = tsent
        imsgptr = 0  # the location in the current message
        datlen = 0   # the indicated message len
        in_msgbuf = bytearray(60)  # the accumulated input
        ncnt = 0;
        while(True):
            ncnt += 1
            tnow = time.monotonic()
            if tnow - tsent > 0.01:
                # No response.  
                if self._logging: log(f'No response from slave node. Node={addr}  {ncnt}' )
                self._no_response_errs += 1
                return None
            # We set the mode to not-blocking!  We might not get anything back
            # on the read, but stay in this loop till the slave node has had
            # every chance to respond.
            buf = self._ser.read(50)
            if len(buf) <= 0:
                if self._logging: logd(f'No bytes on serial port. {ncnt}')
            if len(buf) > 0:
                if self._logging: logd(f'{len(buf)} bytes read on serial port. {ncnt}')
                if self._logging: logd("Bytes = " + self._bytes_to_str(buf))
                # process the input bytes here.
                for c in buf:
                    if imsgptr == 0: 
                        # process the sync byte
                        if c != ord('e') and c != ord('E'):
                            if self._logging: log(f"Message protocol fail.  Illegal first byte ({c})")
                            self._protocol_errs += 1
                            return None
                        in_msgbuf[0] = c
                        imsgptr = 1
                        continue
                    if imsgptr == 1:
                        # process the address/len byte
                        in_msgbuf[1] = c
                        addr_temp = (c >> 4) & 0x000F
                        datlen = c & 0x000F
                        if addr_temp != addr:
                            if self._logging: log(f"Message fail. Returned address from slave incorrect. ({addr} != {addr_temp}).")
                            self._protocol_errs += 1
                            return
                        imsgptr = 2
                        continue
                    if (imsgptr  >= datlen + 2):
                            # this should be the check sum byte.
                            cksum = self._checksum(in_msgbuf, imsgptr)
                            if c != cksum:
                                if self._logging: log(f"Checksum fail on receive. Found {c}. Should be {cksum}.")
                                if self._logging: log(f"Message payload size = {datlen}")
                                if self._logging: log(f"Bytes in msg = {self._bytes_to_str(in_msgbuf)}")
                                self._checksum_errs += 1
                                return None
                            # We have a completed message... check if it is an Echo or really from
                            # the slave node.
                            if in_msgbuf[0] == ord('E'):
                                # it was just an echo.  Need to get the next msg.
                                imsgptr = 0
                                continue
                            # This is success!
                            payload = []
                            for c in in_msgbuf[2:imsgptr]: payload.append(c)
                            return payload
                    in_msgbuf[imsgptr] = c 
                    imsgptr += 1
                    continue

    # def _checksum(self, msg, nmsg):
    #     sum = 0
    #     for i, v in enumerate(msg):
    #         if i >= nmsg: 
    #             break
    #         sum += v & 0x00FF
    #     sum = sum & 0x00FF
    #     return sum 

    # def writereg(self, regadr, dat):
    #     ''' Reads a register from the arduino. '''
    #     try:
    #         self._bus.write_byte_data(self._addr, regadr, dat)
    #         if self._bus_monitor: self._bus_monitor.on_success()
    #     except IOError:
    #         if self._bus_monitor: self._bus_monitor.on_fail()
    #         raise
    #     except OSError:
    #         if self._bus_monitor: self._bus_monitor.on_fail()
    #         raise
