# i2ctest.py -- test the i2c connection
# EPIC Robotz, dlb, Feb 2021

import time
import sys
import ardunio_pb
import arduino_reg_map as reg
import random

print("Initing communication.")
arduino = ardunio_pb.Arduino_pb()

data_errcnt = 0
bus_errcnt = 0
ncnt = 0

wregs = [reg.REG_E0, reg.REG_E1, reg.REG_E2]
wdat  = [0, 0, 0]
datok = [True, True, True]
for r in wregs:
  try:
    arduino.writereg(r, 0)
  except IOError as err:
    print("Unable to init.  \nErr= ", err)
    sys.exit()
print("Init of regs successful.")

nreaderrs = 0
nwriteerrs = 0
ndataerrs = 0


while True:
  ncnt += 1
  # time.sleep(0.100)
  ipath = random.randint(0,2)
  r = wregs[ipath]
  wdat[ipath] = d = random.randint(0, 255)
  # print("writing. [%d] = %d" % (r, d))
  try:
    arduino.writereg(r, d)
  except IOError as err:
    print("!! Got IOError while writing on cycle %d." % ncnt)
    print("  Err= ", err)
    nwriteerrs += 1
    datok[ipath] = False
    continue
  datok[ipath] = True
  ipath = random.randint(0, 2)
  r, d = wregs[ipath], wdat[ipath]
  # print("reading [%d]" % r)
  try:
    d0 = arduino.readreg(r)
  except IOError as err:
    print("!! Got IOError while reading on cycle %d." % ncnt)
    print("  Err= ", err)
    nreaderrs += 1
    continue
  if d != d0 and datok[ipath]:
      data_errcnt += 1
      print("!! Got data error on cycle %d.\n  Wrote 0x%02x Read 0x%02x ." % (ncnt, d, d0))
      ndataerrs += 1
      continue
  if ncnt % 100 == 0:
    ntotal = nwriteerrs + nreaderrs + ndataerrs
    print("%6d cycles. %4d total errors, %4d read errors, %4d write errors, %4d data errors." % (ncnt, ntotal, nreaderrs, nwriteerrs, ndataerrs))
  
#    bus_errcnt += 1
#    if bus_errcnt < 10: print("Bus error found!")
#  time.sleep(0.010)
#  if ncnt % 50 == 0:
#    print("Loop Count: %d,  Bus Errors: %d,  Data Errors: %d" % (ncnt, bus_errcnt, data_errcnt))