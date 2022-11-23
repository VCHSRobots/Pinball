/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Light Control Unit 
 * 
 * *** Configured for the Playfield
 * *** Address = 3
 * 
 * This module is for the Light Control Unit in the score box.  The hardware is
 * set up to control six 12v lamps, and one neostrip, 104 LEDs long. 
 * 
 * This module is commanded and controlled by the Raspberry Pi via
 * the RS-485 bus.
 * 
 * Theory of Operation:
 * The main loop is a multiplexer between monitoring the comm bus and keeping
 * the anaimations of the lights going.  The anaimations updated once every
 * 25 milliseconds -- but with some jitter depending on comm bus activity. 
 * 
 * It is known that any update to the Neopixels takes about 2 msec.  Therefore, 
 * if the comm bus is busy, updates to the Neopixels are held off.  Updates
 * to the lamps are much faster -- in the 10s of usecs.  
 * 
 * The time slicing works as follows:  A frame is defined as a 25 msec span of time.
 * A frame counter is advanced once every 25 msec.  Within a frame, the main loop
 * runs many subframes, which are also counted but these are not timed.  On a new 
 * frame, the subframe counter is set to zero.  If the comm bus is not busy 
 * on frame zero, then the neo-pixel strip is shown (which takes as much as 2 msec).
 * If the comm-bus is busy, the sub-frame counter is not advanceded, and work is delayed
 * until the comm-bus is free.  Normally, at least 50 (if not over 1000) subframes will
 * run in a frame.  Work for updating the various components and systems can schedule
 * to do their work on different subframes.  This keeps the time to execute a subframe
 * well under 300 usecs, except for subframe zero which might take 2 msecs.
 * 
 * Commands and arguments:   
 * 00 (0)  NOP           No operation, just getting status.
 * 01 (3)  NEO_RESET     NeoPixel Reset Args: Color(3)
 * 02 (9)  NEO_SINGLE    NeoPixel Single: C1(3), C2(3), Index(1), C1-Wait(1), C2-Wait(1)
 * 03 (3)  NEO_SOLID     NeoPixel Solid Args: Color(3)
 * 04 (7)  NEO_WIPE      NeoPixel Wipe Args: C1(3), C2(3), Wait(1)
 * 05 (8)  NEO_CHASE     NeoPixel Chase Args: C1(3), C2(3), N(1), Wait(1)
 * 06 (9)  NEO_BLINK     NepPixel Blink Args: C1(3), C2(3), N1(1), N2(1), Wait(1)
 * 07 (2)  LAMP_SOLID    Lamp Solid Args: LampMask(1), Brightness(1)
 * 08 (3)  LAMP_FLASH    Lamp Flash Args: LampMask(1), Brightness(1), Wait(1)
 * 09 (4)  LAMP_MODULATE Lamp Modulate Args: LampMask(1), B1(1), B2(1), Steps(1)
 * 
 * The above arguments are defined as follows:
 *   Color, C1, and C2: Three bytes: R, G, B
 *   Wait: wait time between updates, in units of 25 msecs
 *   N: Number of pixels in moving window
 *   N1: Number of pixels on left side of blink
 *   N2: Number of pixels on right side of blink
 *   C1-Wait: wait time, in units of 25 msecs, the neo pixel is showing C1 Color
 *   C2-Wait: wait time, in units of 25 msecs, the neo pixel is showing C2 Color
 *   Index: The index of the neopixel being set
 *   Brightness: 0 (off) to 255 (fully on) to set brightness
 *   B1: The brightness at the first limit of the modulation
 *   B2: The brightness as the second limit of the modulation
 *   Steps: The number of 25 msec steps to move between limits of the modulation
 *   LampMask: Bits 0-5 indicate which lamps perticipate in the command.
 * 
 * The entire neo pixel strip is either in an animation mode or a single's mode.
 * The anamiation modes are: NEO_SOLID, NEO_WIPE, NEO_CHASE, NEO_BLINK.  If any
 * of these commands are issued, the entire strip is taken over by the command.
 * However, if NEO_SINGLE is issued, then the strip reverts to the single's mode,
 * and what ever settings for the previous single's mode comes back into effect.
 * That is, the conditions of the single's mode is persistant during the animation
 * mdoes.  All the pixels in the single's mode can be set at once with NEO_RESET.
 * 
 * The lamps are in one of two conditions: background mode, or flash.  The backgound
 * modes are LAMP_SOLID and LAMP_MODULATE.  If LAMP_FLASH is issued, the lamp is set
 * to the Brightness level for the duration of the flash, then is returns to the 
 * background mode it was in before the flash.
 * 
 * Status Return:
 *  
 * This node returns a count of processed commands.  This count is
 * a byte, so it rolls over every 256 commands.  A second byte returns 
 * a count of command errors, that also rolls over every 256 errors.
 * 
 * NOTE about Memory:
 * This code can be used for both the score box and the playfield with a small
 * modifications:
 *   1. The Node Address must be different.  Score box is address 2,
 *   and the Playfield address is 3.
 *   2. There is not enough memory in the NANO for over about 80 pixels and
 *   the "singles" mode.  Therefore, the NEO_SINGLE command and its associated
 *   code must be commented out for use in the score box.
 *  
 */

#define NODE_ADDRESS 3
#define NPIXELS 30
#define NLAMPS 6

#include <Adafruit_NeoPixel.h>
#include "comm_bus.h"

// Define the pins...
#define PIN_LAMP_1 6
#define PIN_LAMP_2 5
#define PIN_LAMP_3 3
#define PIN_LAMP_4 11
#define PIN_LAMP_5 10
#define PIN_LAMP_6 9
#define PIN_NEO 12

// Debugging Pins...
#define PIN_DB1 14
#define PIN_DB2 15
#define PIN_DB3 16
#define PIN_DB4 17

// Define the commands
#define CMD_NOP           0x00 
#define CMD_NEO_RESET     0x01
#define CMD_NEO_SINGLE    0x02
#define CMD_NEO_SOLID     0x03
#define CMD_NEO_WIPE      0x04
#define CMD_NEO_CHASE     0x05
#define CMD_NEO_BLINK     0x06
#define CMD_LAMP_SOLID    0x07
#define CMD_LAMP_FLASH    0x08
#define CMD_LAMP_MODULATE 0x09

// Define Modes for Neo Pixels
#define NEO_SINGLE 0
#define NEO_SOLID  1
#define NEO_WIPE   2
#define NEO_CHASE  3
#define NEO_BLINK  4

// Define Modes for the Lamps
#define LAMP_SOLID 0
#define LAMP_FLASH 1
#define LAMP_MODULATE 2

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(NPIXELS, PIN_NEO, NEO_GRB + NEO_KHZ800);

// Setup the Lamps
uint8_t lamp_pins[] = { PIN_LAMP_1, PIN_LAMP_2, PIN_LAMP_3, PIN_LAMP_4, PIN_LAMP_5, PIN_LAMP_6 };

// Status keepers for the Lamps
uint8_t lamp_modes[] = {LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID};
uint8_t lamp_brightness_0[] = {0, 0, 0, 0, 0, 0};
uint8_t lamp_brightness_1[] = {0, 0, 0, 0, 0, 0};
uint8_t lamp_wait[] = {0, 0, 0, 0, 0, 0};
uint8_t lamp_istep[] = {0, 0, 0, 0, 0, 0};  // Contains step and direction for modulation.
uint8_t lamp_previous[] = {LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID, LAMP_SOLID};
uint8_t lamp_flash_brightness[] = {0, 0, 0, 0, 0, 0};
uint8_t lamp_flash_wait[] = {0, 0, 0, 0, 0, 0};
uint8_t lamp_flash_istep[] = {0, 0, 0, 0, 0, 0};

// Inputs to the Neo Pixel Operations
uint32_t neo_c1[NPIXELS];
uint32_t neo_c2[NPIXELS];
uint8_t neo_c1steps[NPIXELS];
uint8_t neo_c2steps[NPIXELS];
uint32_t neo_c1_animation = 0x0000ff;
uint32_t neo_c2_animation = 0x00ff00;
uint8_t neo_n1 = 1;
uint8_t neo_n2 = 1;
uint8_t neo_wait = 8;

// Status keepers for Neo Pixels
uint8_t neo_mode = NEO_SINGLE;
bool neo_show_pending = false;
uint8_t neo_istep[NPIXELS];   // Where we are in the loop for each pixel.
int neo_anim_iprog = 0;       // Progress on the anaimation
int neo_anim_steps = 0;       // Number of steps for anaimations
int neo_anim_iside = 0; 

// Comm Bus Stuff
void on_receive(byte *, int);
CommBus bus(NODE_ADDRESS, on_receive);
bool cmd_pending = false;
uint8_t cmd_bytes[16];
int cmd_bytes_len = 0;
uint16_t cmd_count = 0;
uint16_t err_count = 0;

// Time keeping, and main loop stuff
uint32_t last_frame_time = millis();  // The time at that last frame started
uint32_t frame_count = 0;             // The current frame we are on (one frame = 25 msec)
uint32_t sub_frame = 0;               // The current sub frame we are on (at least 20 per frame)
uint32_t max_sub_frame = 0;
// Timmer Fucntions...
uint32_t t0_timmer;
uint32_t elp_timmer = 0;       
int debug_counter = 0;        

// --------------------------------------------------------------------
// Declaration to measure ram usaage:
int freeRam() {
    extern int __heap_start, *__brkval;
    int v;
    return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}

// --------------------------------------------------------------------
// Timmer Functions for Debugging.
void start_timmer() {
    t0_timmer = micros();
    digitalWrite(PIN_DB1, LOW);
}

void stop_timmer() {
    digitalWrite(PIN_DB1, HIGH);
    uint32_t elp = micros() - t0_timmer;
    if (elp > elp_timmer) elp_timmer = elp;
}

// --------------------------------------------------------------------
// Called when a message is received.
// Save it for later processing.
void on_receive(byte *msg, int n) {
    cmd_count++;
    if(n <= 0) return;
    cmd_pending = true;
    for(int i = 0; i < n; i++) cmd_bytes[i] = msg[i];
    cmd_bytes_len = n;
    return;
}

// --------------------------------------------------------------------
// Converts input arguments (bytes) into a 32 bit color value usable
// by the neo pixel strip.
uint32_t convert_to_rgb(uint8_t *p) {
    uint8_t r = p[0];
    uint8_t g = p[1];
    uint8_t b = p[2];
    uint32_t color = strip.Color(r, g, b);
    return color;
}

// --------------------------------------------------------------------
// Process input command.  Returns true if a new command was processed.
bool process_command() {
    if (!cmd_pending) return false;
    cmd_pending = false;
    if (cmd_bytes_len <= 0) return false;
    int cmd = cmd_bytes[0];
    switch(cmd) {
        case CMD_NOP:  break; 
        case CMD_NEO_RESET: {
                // Arguments:
                // cmd, c-r, c-b, c-b
                //   0,   1,   2,   3
                uint32_t color = convert_to_rgb(cmd_bytes + 1);
                neo_mode = NEO_SINGLE;
                for(int i = 0; i < NPIXELS; i++) {
                    neo_c1[i] = color;
                    neo_c2[i] = color;
                    neo_c1steps[i] = 0;
                    neo_c2steps[i] = 0;
                    neo_istep[i] = 0;
                    strip.setPixelColor(i, color);
                }
                neo_show_pending = true;
            }
            return true;
        case CMD_NEO_SINGLE: {
                // Arguments:
                // cmd, c1-r, c1-g, c1-b, c2-r, c2-g, c2-b, indx, c1-steps, c2-steps
                //   0,    1,    2,    3,    4,    5,    6,    7,        8,        9
                neo_mode = NEO_SINGLE;
                int indx = cmd_bytes[7]; 
                if (indx < 0 || indx >= NPIXELS) {
                    // err_count++;  No longer an error. Indicates desire to return to single's mode.
                    return true;
                }
                neo_c1[indx] = convert_to_rgb(cmd_bytes + 1);
                neo_c2[indx] = convert_to_rgb(cmd_bytes + 4);
                neo_c1steps[indx] = cmd_bytes[8] & 0x007F;
                neo_c2steps[indx] = cmd_bytes[9] & 0x007F;
                neo_istep[indx] = 0;
            }
            return true;
        case CMD_NEO_SOLID: {
                // Arguments:
                // cmd, c-r, c-g, c-b
                //   0,   1,   2,   3
                neo_mode = NEO_SOLID;
                uint32_t color = convert_to_rgb(cmd_bytes + 1);
                for(int i = 0; i < NPIXELS; i++) {
                    strip.setPixelColor(i, color);
                } 
                neo_show_pending = true;
            }
            return true;
        case CMD_NEO_WIPE: { 
                // Arguments:
                // cmd, c1-r, c1-g, c1-b, c2-r, c2-g, c2-b, wait
                //   0,    1,    2,    3,    4,    5,    6,    7
                neo_mode = NEO_WIPE;
                neo_c1_animation = convert_to_rgb(cmd_bytes + 1);
                neo_c2_animation = convert_to_rgb(cmd_bytes + 4);
                neo_wait = cmd_bytes[7] & 0x007F;;
                neo_anim_iprog = 0;       // Progress on the anaimation
                neo_anim_steps = 0;       // Number of steps for anaimations
                neo_anim_iside = 0;       // Which color we are doing
            }
            return true; 
        case CMD_NEO_CHASE: {
                // Arguments:
                // cmd, c1-r, c1-g, c1-b, c2-r, c2-g, c2-b, n, wait
                //   0,    1,    2,    3,    4,    5,    6, 7,    8
                neo_mode = NEO_CHASE;
                neo_c1_animation = convert_to_rgb(cmd_bytes + 1);
                neo_c2_animation = convert_to_rgb(cmd_bytes + 4);
                neo_n1 = cmd_bytes[7];
                neo_wait = cmd_bytes[8] & 0x007F;;
                neo_anim_iprog = 0;       // Progress on the anaimation
                neo_anim_steps = 0;       // Number of steps for anaimations
            }
            return true;
        case CMD_NEO_BLINK: {
                // Arguments:
                // cmd, c1-r, c1-g, c1-b,  c2-r, c2-g, c2-b, n1, n2, wait
                //   0,    1,    2,    3,     4,    5,    6,  7,  8,    9
                neo_mode = NEO_BLINK;
                neo_c1_animation = convert_to_rgb(cmd_bytes + 1);
                neo_c2_animation = convert_to_rgb(cmd_bytes + 4);
                neo_n1 = cmd_bytes[7];
                neo_n2 = cmd_bytes[8];
                neo_wait = cmd_bytes[9] & 0x007F;;
            }
            return true;
        case CMD_LAMP_SOLID: {
                // Arguments:
                // cmd, mask , brighness
                //   0,    1,          2
                uint8_t mask = cmd_bytes[1];
                uint8_t brightness = cmd_bytes[2];
                for (int i = 0; i < 6; i++) {
                    if ((1 << i) & mask) {
                        lamp_modes[i] = LAMP_SOLID;
                        lamp_brightness_0[i] = brightness;
                    }
                }
            }
            return true;
        case CMD_LAMP_FLASH: {
                // Arguments:
                // cmd, mask , brighness, wait
                //   0,    1,          2,    3
                uint8_t mask = cmd_bytes[1];
                for (int i = 0; i < 6; i++) {
                    if ((1 << i) & mask) {
                        if (lamp_modes[i] != LAMP_FLASH) {
                            lamp_previous[i] = lamp_modes[i];
                        }
                        lamp_modes[i] = LAMP_FLASH;
                        lamp_flash_brightness[i] = cmd_bytes[2];
                        lamp_flash_wait[i] = cmd_bytes[3] & 0x007F;
                        lamp_flash_istep[i] = 0;
                    }
                }
            }
            return true;
        case CMD_LAMP_MODULATE: {
                // Arguments:
                // cmd, mask , b1, b2, wait
                //   0,    1,   2,  3,    4
                uint8_t mask = cmd_bytes[1];
                for (int i = 0; i < 6; i++) {
                    if ((1 << i) & mask) {
                        lamp_modes[i] = LAMP_MODULATE;
                        if (cmd_bytes[3] >= cmd_bytes[2]) {
                            lamp_brightness_0[i] = cmd_bytes[2];
                            lamp_brightness_1[i] = cmd_bytes[3];
                        } else {
                            lamp_brightness_0[i] = cmd_bytes[3];
                            lamp_brightness_1[i] = cmd_bytes[2];
                        }
                        lamp_wait[i] = cmd_bytes[4] & 0x007F; 
                        lamp_istep[0] = 0;
                    }
                }
            }
            return true;
        default:
      err_count++;
  }
  return false;
}

// --------------------------------------------------------------------
// Loads the response for the next command.
void load_response() {
    //static int max_ram = 0;
    uint8_t response[10];

    response[0] = cmd_count & 0x00FF;
    response[1] = err_count & 0x00FF;

    // int ram = freeRam();
    // if(ram > max_ram) max_ram = ram;
    // response[2] = (max_ram >> 8) & 0x00FF;
    // response[3] = max_ram & 0x00FF;

    // response[4] = (elp_timmer >> 24) & 0x00FF;
    // response[5] = (elp_timmer >> 16) & 0x00FF;
    // response[6] = (elp_timmer >> 8) & 0x00FF;
    // response[7] = elp_timmer & 0x00FF;

    // response[8] = (debug_counter >> 8) & 0x00FF;
    // response[9] = debug_counter & 0x00FF;

    bus.set_response(response, 2);
}

// --------------------------------------------------------------------
// Setup the NeoPixel Strip
void neo_setup() {   
  for(int i = 0; i < NPIXELS; i++) {
    neo_c1[i] = 0x000000;
    neo_c2[i] = 0x000000;
    neo_c1steps[i] = 0;
    neo_c2steps[i] = 0;
    neo_istep[i] = 0;
  }
  strip.begin();  
  strip.setBrightness(255);          
  strip.clear(); 
  strip.show();  
}

// --------------------------------------------------------------------
// Setup the Lamps
void lamp_setup() {
    for(int i= 0; i < NLAMPS; i++) {
        pinMode(lamp_pins[i], OUTPUT);
        digitalWrite(lamp_pins[i], LOW);
    }
}

// --------------------------------------------------------------------
// Setup the debugging pins
void debug_setup() {
    pinMode(PIN_DB1, OUTPUT);
    pinMode(PIN_DB2, OUTPUT);
    pinMode(PIN_DB3, OUTPUT);
    pinMode(PIN_DB4, OUTPUT);
    digitalWrite(PIN_DB1, HIGH);
    digitalWrite(PIN_DB2, HIGH);
    digitalWrite(PIN_DB3, HIGH);
    digitalWrite(PIN_DB4, HIGH);
}

// --------------------------------------------------------------------
// Main setup
void setup() {
    neo_setup();
    lamp_setup();
    debug_setup();
    load_response();
    bus.begin();
}

// --------------------------------------------------------------------
// Use this to process the neo-singles mode.  For time-slicing,
// parts of the strip can be processed separately.
void neo_set_singles(int indx0, int np) {
    for(int i = 0; i < np; i++) {
        int ip = indx0 + i;
        uint8_t bstep = neo_istep[ip];
        int istep = bstep & 0x007F;
        int idir  = (bstep >> 7) & 0x0001;
        istep++;
        if (idir == 0) {
            if(istep >= neo_c1steps[ip]) {
                idir = 1;
                istep = 0;
                strip.setPixelColor(ip, neo_c2[ip]);
            }
        } else {
            if(istep >= neo_c2steps[ip]) {
                idir = 0;
                istep = 0;
                strip.setPixelColor(ip, neo_c1[ip]);
            }  
        }
        neo_istep[ip] = ((idir << 7) & 0x0080) | (istep & 0x007F);
    }
    neo_show_pending = true;
}

// --------------------------------------------------------------------
// Sets the pixels for wiping.
void neo_wipe() {
    neo_anim_steps++;
    if (neo_anim_steps >= neo_wait) {
        neo_anim_steps = 0;
        if (neo_anim_iside == 0) strip.setPixelColor(neo_anim_iprog, neo_c1_animation);
        else                     strip.setPixelColor(neo_anim_iprog, neo_c2_animation);
        neo_show_pending = true;
        neo_anim_iprog++;
        if (neo_anim_iprog >= NPIXELS) {
            neo_anim_iprog = 0;
            neo_anim_iside++;
            if(neo_anim_iside > 1) neo_anim_iside = 0;
        }
    }
}

// --------------------------------------------------------------------
// Sets a segment in the neo pixel strip, while accounting for
// running off the end.
void neo_set_segment(int ip, int n, uint32_t color) {
    for(int i = 0; i < n; i++) {
        int indx = ip + i;
        if (indx >= NPIXELS) indx = indx - NPIXELS;
        if (indx < 0) ip = 0;
        if (indx >= NPIXELS) indx = NPIXELS - 1;
        strip.setPixelColor(indx, color);
    }
}

// --------------------------------------------------------------------
// Sets the pixels for chasing.  
void neo_chase() {
    neo_anim_steps++;
    if (neo_anim_steps >= neo_wait) {
        neo_anim_steps = 0;  
        // First reset the old pixels.
        neo_set_segment(neo_anim_iprog, neo_n1, neo_c2_animation);
        // Advance the position of the chase
        neo_anim_iprog++;
        if(neo_anim_iprog >= NPIXELS) neo_anim_iprog = 0;
        // Set the current pixels.
        neo_set_segment(neo_anim_iprog, neo_n1, neo_c1_animation);
        neo_show_pending = true;
    }
}

// --------------------------------------------------------------------
// Sets the pixels for blinking.  For time-slicing,
// parts of the strip can be processed separately.
void neo_blink(int indx0, int n) {
    static bool neo_blink_go = false;
    static int counter;
    static uint32_t c1, c2;
    if(indx0 == 0) {
        neo_blink_go = false;
        neo_anim_steps++;
        if (neo_anim_steps < neo_wait) return;
        neo_anim_steps = 0;
        neo_anim_iside++;
        if (neo_anim_iside > 1) {
            neo_anim_iside = 0;
            c1 = neo_c1_animation;
            c2 = neo_c2_animation;
        } else {
            c1 = neo_c2_animation;
            c2 = neo_c1_animation;
        }
        neo_blink_go = true;
        neo_show_pending = true;
        counter = 0;
    }
    if (!neo_blink_go) return;
    for(int i = 0; i < n; i++) {
        int ip = indx0 + i;
        if (ip >= NPIXELS) return;
        if (counter < neo_n1) strip.setPixelColor(ip, c1);
        else strip.setPixelColor(ip, c2);
        counter++;
        if (counter >= neo_n1 + neo_n2) counter = 0;
    }
}

// --------------------------------------------------------------------
// Responsible for time-slicing the work to update the neo pixels.
// Does the work in batches, of 15 pixels each.  The batches
// must be numbered from 0 to NPIXELS/15 + 1.  That is call this 
// funciton repeateally during a frame for all batches need, numbered
// 0 though about 10.  Its okay to request processing of batches out
// of range.  For example, for 104 pixels, 10 batches will be okay.
// Measured max time for a call is 180 usecs.
void manage_neo(int ibatch) {
    if (ibatch < 0) return;
    switch(neo_mode) {
        case NEO_SINGLE: {
                int np = 15;
                int indx = ibatch * np;
                if (indx + np >= NPIXELS) {
                    np = NPIXELS - indx;
                }
                if (np <= 0) return;
                neo_set_singles(indx, np);
                neo_show_pending = true;
            }
            return;
        case NEO_SOLID: 
            return;
        case NEO_WIPE: {
                if (ibatch == 0) neo_wipe();
            }
            return;
        case NEO_CHASE: {
                if (ibatch == 0) neo_chase();
            }
            return;
        case NEO_BLINK: {
                int np = 15;
                int indx = ibatch * np;
                if (indx + np >= NPIXELS) {
                    np = NPIXELS - indx;
                }
                if (np <= 0) return;
                neo_blink(indx, np);
            }
            return;
    }
}

// --------------------------------------------------------------------
// Sets the lamp's brightness.
void set_lamp(int ilamp, int brightness) {
    int pin = lamp_pins[ilamp];
    if (brightness <= 0) digitalWrite(pin, LOW);
    else if (brightness >= 255) digitalWrite(pin, HIGH);
    else analogWrite(pin, brightness);
}

// --------------------------------------------------------------------
// Calculate brightness 
uint8_t cal_brightness(int ilamp) {
    int bout = 0;
    int b0 = lamp_brightness_0[ilamp];
    int b1 = lamp_brightness_1[ilamp];
    int istep = lamp_istep[ilamp] & 0x007F;
    int idir = 0;
    if (lamp_istep[ilamp] & 0x0080) idir = 1;
    int nsteps = lamp_wait[ilamp];
    int span = b1 - b0;
    float slice = (float) span / (float) nsteps;
    if (idir == 0) {
        istep++;
        if (istep >= nsteps) {
            istep = nsteps;
            idir = 1;
        }
        bout = b0 + (int) (istep * slice);
    } else {
        istep--;
        if (istep <= 0) {
            istep = 0;
            idir = 0;
        }
        int iistep = nsteps - istep;
        bout = b1 - (int) (iistep * slice);
    }
    if (bout >= b1) bout = b1;
    if (bout <= b0) bout = b0;
    lamp_istep[ilamp] = ((idir << 7) & 0x0080) | istep;
    return bout;
}

// --------------------------------------------------------------------
// Manage a lamp.  Should be called once on each frame for each lamp
// and no more.
void manage_lamps(int ilamp) {
    if (ilamp < 0 || ilamp >= NLAMPS) return;
    int mode = lamp_modes[ilamp];
    switch(mode) {
        case LAMP_SOLID: {
            int b = lamp_brightness_0[ilamp];
            set_lamp(ilamp, b);
            return;
        }
        case LAMP_FLASH: {
            if (lamp_flash_istep[ilamp] >= lamp_flash_wait[ilamp]) {
                lamp_modes[ilamp] = lamp_previous[ilamp];
                int b = lamp_brightness_0[ilamp];
                set_lamp(ilamp, b);
                    return;
                }
            int b = lamp_flash_brightness[ilamp];
            set_lamp(ilamp, b);
            lamp_flash_istep[ilamp]++;
            return;
        }
        case LAMP_MODULATE: {
            int b = cal_brightness(ilamp);
            set_lamp(ilamp, b);
        }
    }
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the
// "os".  See comments at top to see how this should work.
void loop() {
    static bool inhibit_strip = false;
    bus.update();   // Highest priority, called every time.
    uint32_t tnow = millis();
    if (tnow - last_frame_time >= 25) {
        // New frame start
        frame_count++;
        sub_frame = 0;
        last_frame_time = tnow;
    }
    if (bus.is_busy()) return;
    if (process_command()) {
        load_response();
        // A new command was processed.  This means any
        // work done so far in this frame is probably invalid.
        // Therefore, if there is plenty of time left in 
        // this frame, reset the sub_frame counter which will
        // cause the work to be done from the beginning.  Otherwise
        // set the sub frame counter to a large number to 
        // avoid doing work till the next frame, and disable
        // the updating of the strip in the next frame.
        if (tnow - last_frame_time < 10) sub_frame = 0;
        else sub_frame = 1000000;
        inhibit_strip = true;
    }
    if (sub_frame == 0) {
        if (bus.is_busy()) return;
        if(neo_show_pending & !inhibit_strip) {
            strip.show();  // Blocks for 1-2 msec!
            neo_show_pending = false;
        }
        inhibit_strip = false;
    }
    sub_frame++;
    if (sub_frame < 1) return;
    if (sub_frame >= 10 && sub_frame < 30) {
        //start_timmer();
        manage_neo(sub_frame - 10);
        //stop_timmer();
    }
    if (sub_frame >= 40 && sub_frame < 50) {
        //start_timmer();
        manage_lamps(sub_frame - 40);
        //stop_timmer();
    }
}
 
