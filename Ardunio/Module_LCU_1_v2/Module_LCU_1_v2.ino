/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Light Control Unit (in Score Box)
 * 
 * This module is for the Light Control Unit in the
 * score box.  The hardware is set up to control six 
 * 12v lamps, and one neostrip, 104 LEDs long. 
 * 
 * This module is commanded and controlled by the 
 * Raspberry Pi voer a I2C connection.
 * 
 * I2C Particulars
 * ---------------
 * This program response to the I2C bus like a typical device with a set of registors that
 * can be read or writen to by a master.  The arduino is the slave.  The set of registors
 * are defined in a table below.  Each address has a name according to its function.
 *
 * Table of I2C Registers  
 * ----------------------
 *      Name      Addr    R/W?  Purpose/Usage
 *      --------  ----    ----  -------------   */
#define REG_SIGV     0   // RO  Device Signature/Version.  Currently: 'e'
#define REG_DTME1    1   // RO  Device Time, Milliseconds, Byte 0, MSB
#define REG_DTME2    2   // RO  Device Time, Milliseconds, Byte 1
#define REG_DTME3    3   // RO  Device Time, Milliseconds, Byte 2
#define REG_DTME4    4   // RO  Device Time, Milliseconds, Byte 3, LSB
#define REG_NEO      5   // RW  Neo Pattern to use
#define REG_LAMPS    6   // RW  Lamps on/off status, by bits 0-5
#define REG_FLASH    7   // RW  Lamps Flash, by bits 0-5
#define RED_FT       8   // RW  Number of milliseconds for flash
#define REG_L1       9   // RW  Lamp 1 brightness 
#define REG_L2      10   // RW  Lamp 2 brightness 
#define REG_L3      11   // RW  Lamp 3 brightness 
#define REG_L4      12   // RW  Lamp 4 brightness 
#define REG_L5      13   // RW  Lamp 5 brightness 
#define REG_L6      14   // RW  Lamp 6 brightness 
#define REG_EXTRA   15   // RW  Extra Regs for any purpose (testing)
#define REG_LAST    24   // ** Last Registor
#define REG_RW0      5   // ** First Registor where writing is allowed.

// Define the I2C Address that this module will respond to:
#define I2C_ADDRESS 8

#include <Wire.h>
#include <Adafruit_NeoPixel.h>

// Define the pins...
#define PIN_LAMP_1 3
#define PIN_LAMP_2 5
#define PIN_LAMP_3 6
#define PIN_LAMP_4 9
#define PIN_LAMP_5 10
#define PIN_LAMP_6 11
#define PIN_NEO 12

// Define other important parameters...
#define VERSION 'e'
#define NLAMPS 6
#define NPIXELS 104

volatile unsigned long timenext;
volatile unsigned long timenow;
volatile unsigned long timelastcomm;
volatile unsigned long timereset;
volatile byte regs[REG_LAST + 1];
volatile int regaddr = 0;
volatile long sendcnt = 0;
volatile long reccnt = 0;
volatile long badmsgcount = 0;

char lamps[] = {PIN_LAMP_1, PIN_LAMP_2, PIN_LAMP_3, PIN_LAMP_4, PIN_LAMP_5, PIN_LAMP_6};
uint32_t color_red;
uint32_t color_blue;
uint32_t color_green;
uint32_t color_white;
uint32_t color_black;

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(NPIXELS, PIN_NEO, NEO_GRB + NEO_KHZ800);


// --------------------------------------------------------------------
// Main setup
void setup() {
  //neo_setup();
  //lamp_setup();
  i2c_setup();
  //Serial.begin(115200);
  //Serial.println("");
  //Serial.println("Starting UP! ");
  //Serial.println("");
}

// --------------------------------------------------------------------
// Setup the I2C Bus
void i2c_setup() {
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receivePiCmd);
  Wire.onRequest(sendPiData);
  timereset = millis();      // Time that we restarted
  timenext = timereset;  // Time to run next loop
}

// --------------------------------------------------------------------
// Setup the NeoPixel Strip
void neo_setup() {
  strip.begin();  
  strip.clear();          
  strip.show();       // Causes           
  strip.setBrightness(255); 
  color_red = strip.Color(255, 0, 0);
  color_blue = strip.Color(0, 255, 0);
  color_green = strip.Color(0, 0, 255);
  color_white = strip.Color(255, 255, 255);
  color_black = strip.Color(0, 0, 0);
}

// --------------------------------------------------------------------
// Setup the Lamps
void lamp_setup() {
    for(int i = 0; i < NLAMPS; i++) {
      pinMode(lamps[i], OUTPUT);
      digitalWrite(lamps[i], 0);
    }
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the "os".  Here, we use 
// a time-share approach to run each task.  This loop calls each task once every 10msec.
// This means there cannot be any "blocking", and each task must return as fast as possible.
void loop() {
  timenow = millis();
  if (timenow < timenext) return;
  timenext += 10;
  //manage_neo();
  //manage_lamps();
  //report_status();
}

// --------------------------------------------------------------------
void manage_neo() {
  neo_slow_mover();
}

// --------------------------------------------------------------------
void manage_lamps() {
  // TODO: write lamp management.
}

// --------------------------------------------------------------------
// receivePiCmd() 
// This is a callback from the I2C lib when the arduino receives data from the RPi.
void receivePiCmd(int msglen) {
  timelastcomm = millis();
  reccnt++;
  if (msglen == 1) {
    regaddr = Wire.read();
    if (regaddr < 0 || regaddr > REG_LAST) {
      // Register out of range, bad message.
      badmsgcount++;
      regaddr = 0;
    }
    return;
  }
  if (msglen != 2) {
    badmsgcount++;
    return;
  }
  regaddr = Wire.read();
  int dat = Wire.read();
  if (regaddr < 0 || regaddr > REG_LAST) {
    // Register out of range, bad message.
    badmsgcount++;
    return;
  }
  if (regaddr < REG_RW0) {
    // Trying to write into a read only reg.  Ignore this.
    return;
  }
  regs[regaddr] = dat;
}

// --------------------------------------------------------------------
// sendPiData()  
// This is a callback from the I2C lib when the arduino has been commanded
// by the RPi to send data back.  The register number of the data to send was
// previously communicated on a receive command, and is stored in regaddr.
volatile byte timesend[4];
void sendPiData() {
  sendcnt++;
  if (regaddr == REG_SIGV) {Wire.write(VERSION); return; }
  if (regaddr == REG_DTME1) {
    long ttfix = millis();
    timesend[0] = ((byte *)&ttfix)[0];
    timesend[1] = ((byte *)&ttfix)[1];
    timesend[2] = ((byte *)&ttfix)[2];
    timesend[3] = ((byte *)&ttfix)[3];
  }
  if (regaddr >= REG_DTME1 && regaddr <= REG_DTME4) {
    Wire.write(timesend[regaddr - REG_DTME1]);
    delayMicroseconds(10);  // For some reason, this makes it work reliably.
    return;
  }
  Wire.write(regs[regaddr]);
  delayMicroseconds(10); // For some reason, this makes it work reliably.
}

// --------------------------------------------------------------------
// report_status()
// Reports the status to the monitor terminal, once every 5 secs.
// This is a debugging aid.
void report_status() {
  static unsigned long lastreporttime = 0;
  static long status_count = 0;
  char strbuf[100], buf2[30];
  if (timenow - lastreporttime > 5000) {
    status_count += 1;
    lastreporttime = timenow;

    unsigned long t0 = millis();
    Serial.println("");

    sprintf(strbuf, "Time = %ld", timenow);
    Serial.println(strbuf);

    sprintf(strbuf, "Last Time Report = %02x %02x %02x %02x (hex)", timesend[0], timesend[1], timesend[2], timesend[3]);
    Serial.println(strbuf);

    sprintf(strbuf, "NEO Pattern = %02x", regs[REG_NEO]);
    Serial.println(strbuf);

    sprintf(strbuf, "Lamps = %3d, %3d, %3d, %3d, %3d, %3d", regs[REG_L1], regs[REG_L2], regs[REG_L3], 
      regs[REG_L4], regs[REG_L5], regs[REG_L6]);
    Serial.println(strbuf);
  
    sprintf(strbuf, "Spare Regs (%d) = %3d %3d %3d", REG_EXTRA, regs[REG_EXTRA], regs[REG_EXTRA+1], regs[REG_EXTRA+2]);
    Serial.println(strbuf);

    sprintf(strbuf, "Receive/Send counts = %ld, %ld", reccnt, sendcnt);
    Serial.println(strbuf);

    sprintf(strbuf, "Bad Message count = %ld", badmsgcount);
    Serial.println(strbuf);

    unsigned long tdelta = millis() - t0;
    sprintf(strbuf, "Status Report Time = %ld msec", tdelta);
    Serial.println(strbuf);
  }
}

// -------------------------------------------------------------------------------
// Neo Patterns

unsigned long timeneolast = 0;

// Marches one red light around the circle at a slow rate
void neo_slow_mover() {
  static int pos = 0;
  if (timenow - timeneolast > 200) {
    timeneolast = timenow;
    for (int i = 0; i < NPIXELS; i++) strip.setPixelColor(i, color_black);
    pos++;
    if(pos >= NPIXELS) pos = 0;
    strip.setPixelColor(pos, color_red);
    strip.show(); 
  }
}
