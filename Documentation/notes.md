### Notes For Pinball Software Development

## Now to set up the I2C bus for the pi.

To turn on the I2C bus, and set it's speed, do:
  1. From the Raspberry Desktop, run the system configuration, "Raspberry Pi Configuration",
  and enable I2C under "interfaces".
  2. Edit the boot configuration file:
      
      sudo nano /boot/config.txt

  3. In the boot configuration file, find the line that starts with "dtparam=i2c_arm=on", and
  change it to:

      dtparam=i2c_arm=on,i2c_arm_baudrate=50000

  The "50000" can be any speed between about 10,000 and 400,000.  Try 50,000 to start.

  4. Reboot the Pi.

## Tools useful for checking things out:

      i2cdetect


## How to AutoStart the Pinball Program in the pi.

We want the pinball machine to automatically run on power-up or reboot. 
The pinball program runs on the desktop, since it outputs a graphical display.
Therefore, we want the desktop fully running before starting the pinball program.
This is done as follows:

Make a shell scrip, called "launcher.sh".  It is stored in /home/pi/pb.

Its contents are:

        #!/bin/sh
        # launcher.sh -- used to start up the pinball manager program

        cd /
        sudo python /home/pi/pb/demo_screen.py 

The shell needs to be executed in a terminal window.  THis is accomplished by
runing an lxterminal, and telling lxterminal to run a program inside it, upon startup, like so:
    
        lxterminal -e /home/pi/pb/launcher.sh

The '-e' option exectues the launcher.sh script, which, in turn executes our  python program.

Now, the lxterminal must be put in the autostart file for the windows desktop.  On the pi,
the windows desktop is really X-Windows, or, known as LXDE, or "lightweight X11 Desktop Environment".
LXDE uses /etc/xdg/lxsession/LXDE-pi/autostart for a list of programs to automatically run on startup.
That file looks like:

            @lxpanel --profile LXDE-pi
            @pcmanfm --desktop --profile LXDE-pi
            @xscreensaver -no-splash
            @lxterminal -e /home/pi/pb/launcher.sh

Note the last line.


## Decoding Serial Line Data from Oscilliscope

Transmitted "yes".  Got the following

yes + CR/LF                      = 0x79,        0x65,        0x73,        0x0D,        0x0A

Raw Bits:                        0111 1001    0110 0101    0111 0011    0000 1101    0000 1010  

Reverse bits for each byte:      1001 1110    1010 0110    1100 1110    1011 0000    0101 0000       

Add Stop bits:      ...11111  10 1001 1110 10 1010 0110 10 1100 1110 10 1011 0000 10 0101 0000  11111...

This last line was observed on my scope.  Logical one was +3.3 volts, Logical zero was 0 volts.

Other observation:  Request sent as an "a" char.  Response started about 20usec after last bit
of the "a" was transmitted.  Entire response was done in 440 usecs after the "a" was received.

## Address and Protocol for RS-485 bus

1.  Pi starts the exchange.  A Pi Message is at least three bytes long, and can be up to 18 bytes long.
    It is composed as follows:
       Sync Byte              -- an "E", or 0x45
       Addree and Len Byte    -- In the form: "aaaa nnnn", where "aaaa" is address, and "nnnn" is length
       Data Bytes             -- Zero to 15 bytes
       Checksum               -- Explained Below

2. The node with the address of "aaaa", always responds with:
       Sync Byte              -- an "e"
       Node Address, Len:     -- In the form "aaaa nnnn"
       Data Bytes             -- Zero to 15 bytes
       Checksum               -- Explained Below

Rules:  
1. The Bus operates at 115200 baud.  2 start/stop bits per byte.
2. The slave node must respond within 4 microseconds.  
3. If the checksum indicates an error, no response is made (at all!).

Design parameters:
* At 115200 baud with 2 start/stop bits, one byte can be transmitted in about 87 usecs.
* The worst case msg excange is 18+18 bytes or  about 3 msec. 
* Allowing for a 4 msec delay in a node, one node can be interigated in under 10ms.
* However, typical sized messages will be 6 bytes, both ways, with maybe 1 ms delay or about 2ms.
* Therefore, for the pinball machine with, 8 nodes, a update cycle will be under 20 ms.

CheckSum:
* Calculate by adding all bytes in the message together and then only keeping the least significant byte.
* The checksum itself is not part of the calculation.

## Timming Tests and Measurements
1. To transmit a 0-byte payload, and receive a 3 byte payload requries about 1.7 ms.  Therefore, assume about 3-5 ms per message.  7 nodes, is about 40ms. 
2. To do a show() on 200 neo pixels takes somewhere between 0.9 and 2.2 ms.   For 10 neo pixels,
it still takes as much as a millisecond, but average time is around 0.5 ms.
3. To sense 3 inputs, in a counting loop and do something simple with the data takes 16 usecs.




