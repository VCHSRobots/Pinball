/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Lane Switches Control Unit 
 * 
 * *** Address = 7
 * 
 * This module is for the lane switches. The hardware is set up to
 * monitor 15 switches.   
 * 
 * This module is commanded and controlled by the Raspberry Pi via
 * the RS-485 bus.
 * 
 * Theory of Operation:
 * The main loop is a multiplexer between monitoring the comm bus and monitoring
 * the input switches.  Since all operations can take place in the 10s of
 * microseconds, no framing is done.
 * 
 * Commands and arguments:   
 * 00      NOP            No operation, just getting status.
 * 100     ECHO           args: one byte to put in the echo registor
 * 30      DEBOUNCE       args: tunit_low(1), tunit_high(1) 
 * 31      DB_BANK        args: bank(1), mask(1), tunit_low(1), tunit_high(1)
 * 32      CLEAR_COUNTS   args: none
 * 
 * DEBOUNCE
 * Sets the debounce filter for all switch inputs.  tuints_low is the number of
 * milliseconds that the input must be in the low state to be consideres a valid input.
 * tunits_high is the number of millisconds that the input must be in the high state before
 * a new trigger is allowed.
 * 
 * DB_BANK
 * Similar to DEBOUNCE, but allows setting the parameters for individule switches
 * by spectifing a bank (0 or 1) and a mask.  
 * 
 * CLEAR_COUNTS
 * Clears the counts for all inputs. 
 * 
 * Output Message:
 *   Byte  0:   Count of received cmds, rolls over at 255.
 *   Byte  1:   Count of errors, rolls over at 255.
 *   Byte  2:   Echo Registor -- returns argument given on a ECHO command.
 *   Byte  3:   Bit pattern of current switch conditions, bank 0 (Switches 0-7)
 *   Byte  4:   Bit pattern of current switch conditions, bank 1 (Switches 8-15)
 *   Byte  5:   Switch counts for inputs  0 and  1
 *   Byte  6:   Switch counts for inputs  2 and  3
 *   Byte  7:   Switch counts for inputs  4 and  5
 *   Byte  8:   Switch counts for inputs  6 and  7
 *   Byte  9:   Switch counts for inputs  8 and  9
 *   Byte 10:   Switch counts for inputs 10 and 11
 *   Byte 11:   Switch counts for inputs 12 and 13
 *   Byte 12:   Switch counts for inputs 14 and 15
 * 
 * A switch count byte has the following bit pattern:  bbbb-aaaa were "bbbb" is the
 * count for the highered number switch, and "aaaa" is the switch count for the lowered
 * numnbered switch.  The counts run from zero to 15, and then roll over.
 * 
 */

#define NODE_ADDRESS 7
#define NINPUTS 15

#include "comm_bus.h"

// Define the pins...
#define PIN_S1      14   // Input 0
#define PIN_S2      11   // Input 1
#define PIN_S3      10   // Input 2
#define PIN_S4       9   // Input 3
#define PIN_S5       8   // Input 4
#define PIN_S6       7   // Input 5
#define PIN_S7       6   // Input 6
#define PIN_S8       5   // Input 7
#define PIN_S9       4   // Input 8
#define PIN_S10      3   // Input 9
#define PIN_S11     15   // Input 10
#define PIN_S12     16   // Input 11
#define PIN_S13     17   // Input 12
#define PIN_S14     18   // Input 13
#define PIN_S15     19   // Input 14

// Debug pin  
#define PIN_DB1     12   // (Usually this is the Neo Pixel Pin...)

// Define the commands
#define CMD_NOP               0
#define CMD_ECHO            100 
#define CMD_DEBOUNCE         30
#define CMD_DB_BANK          31
#define CMD_CLEAR_COUNTS     32

// Switch Input States
#define SW_READY        0  // We are waiting for a trigger
#define SW_DB_ON        1  // Waiting for debounce on closing of the switch
#define SW_ACTIVE       2  // The switch is active -- a pulse is counted here.
#define SW_DB_OFF       3  // Waiting for debounce on opening of the switch

// Setup the pins
uint8_t input_pins[] = {PIN_S1, PIN_S2, PIN_S3, PIN_S4, PIN_S5, PIN_S6, PIN_S7, PIN_S8,
                        PIN_S9, PIN_S10, PIN_S11, PIN_S12, PIN_S13, PIN_S14, PIN_S15};

// Parameters and states for input switches.
// Note: these arrays are 16 elements instead of 15.  Last element is ignored.
// This makes some processing easier.
uint32_t debounce_on[] =  {3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000,
                           3000, 3000, 3000, 3000, 3000, 3000};
uint32_t debounce_off[] = {5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000,
                           5000, 5000, 5000, 5000, 5000, 5000};
uint32_t debounce_t0[]  = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t switch_counts[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t switch_states[] = {SW_READY, SW_READY, SW_READY, SW_READY, SW_READY, SW_READY,
                           SW_READY, SW_READY, SW_READY, SW_READY, SW_READY, SW_READY,
                           SW_READY, SW_READY, SW_READY, SW_READY};
uint16_t switch_bits = 0;

// Comm Bus Stuff
void on_receive(byte *, int);
CommBus bus(NODE_ADDRESS, on_receive);
bool cmd_pending = false;
uint8_t cmd_bytes[16];
int cmd_bytes_len = 0;
uint16_t cmd_count = 0;
uint16_t err_count = 0;
uint8_t echo_reg = 0;

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
// Process input command.  Returns true if a new command was processed.
bool process_command() {
    if (!cmd_pending) return false;
    cmd_pending = false;
    if (cmd_bytes_len <= 0) return false;
    int cmd = cmd_bytes[0];
    switch(cmd) {
        case CMD_NOP:  
            return true; 
        case CMD_ECHO: {
                echo_reg = cmd_bytes[1];
            }
            return true;
        case CMD_DEBOUNCE: {
                uint32_t tunit_on = cmd_bytes[1];
                uint32_t tunit_off = cmd_bytes[2];   
                tunit_on *= 1000;
                tunit_off *= 1000;
                for(int i = 0; i < NINPUTS; i++) {
                    debounce_on[i] = tunit_on;
                    debounce_off[i] = tunit_off;
                }  
            }
            return true;
        case CMD_DB_BANK: {
                uint8_t ibank = cmd_bytes[1];
                uint8_t mask  = cmd_bytes[2];
                uint32_t tunit_on = cmd_bytes[1];
                uint32_t tunit_off = cmd_bytes[2];   
                tunit_on *= 1000;
                tunit_off *= 1000;
                if(ibank >= 2) return true;
                int n = 8;
                int ioffset = 0;
                if (ibank == 1) { n = 7; ioffset = 8; }
                for(int i = 0; i < n; i++) {
                    if ((1 << i) & mask) {
                        debounce_on[i + ioffset] = tunit_on;
                        debounce_off[i + ioffset] = tunit_off;
                    }
                }
            }
            return true;
        case CMD_CLEAR_COUNTS: {
                for(int i = 0; i < NINPUTS; i++) {
                    switch_counts[i] = 0;
                }
            }
            return true;
    }
    return false;
}

// --------------------------------------------------------------------
// Loads the response for the next command.
void load_response() {
    uint8_t response[16];

    response[0] = cmd_count & 0x00FF;
    response[1] = err_count & 0x00FF;
    response[2] = echo_reg;

    response[3] = switch_bits & 0x00FF;
    response[4] = (switch_bits >> 8) & 0x007F;
    for (int i = 0; i < 8; i++) {
        uint8_t b = ((switch_counts[i * 2 + 1] << 4) & 0x00F0);
        b |= (switch_counts[i * 2]) & 0x000F;
        response[5 + i] = b;
    }
    bus.set_response(response, 13);
}

// --------------------------------------------------------------------
// Setup the input switches
void setup_inputs() {
    for(int i = 0; i < NINPUTS; i++) {
        pinMode(input_pins[i], INPUT_PULLUP);
    }
}

// --------------------------------------------------------------------
// Setup the debugging pins
void setup_debug() {
    pinMode(PIN_DB1, OUTPUT);
    digitalWrite(PIN_DB1, HIGH);
}

// --------------------------------------------------------------------
// Main setup
void setup() {
    setup_debug();
    setup_inputs();
    load_response();
    bus.begin();
}

// --------------------------------------------------------------------
// Reads the inputs and applies filtering. 
void get_inputs() {
    uint16_t x = 0;
    for(int i = 0; i < NINPUTS; i++) {
        uint32_t tnow = micros();
        uint16_t ibit = (1 << i);
        bool bval = false;
        if (digitalRead(input_pins[i]) == LOW) bval = true;
        switch(switch_states[i]) {
            case SW_READY:
                if (bval) {
                    switch_states[i] = SW_DB_ON;
                    debounce_t0[i] = tnow;
                }
                break;
            case SW_DB_ON:
                if (!bval) {
                    switch_states[i] = SW_READY;
                } else {
                    if (tnow - debounce_t0[i] > debounce_on[i]) {
                        switch_states[i] = SW_ACTIVE;
                        x = x | ibit;
                        switch_counts[i]++;
                    }
                }
                break;
            case SW_ACTIVE:
                x = x | ibit;
                if (!bval) {
                    switch_states[i] = SW_DB_OFF;
                    debounce_t0[i] = tnow;
                }
                break;
            case SW_DB_OFF:
                x = x | ibit;
                if (bval) {
                    switch_states[i] = SW_ACTIVE;
                }
                if (tnow - debounce_t0[i] > debounce_off[i]) {
                    switch_states[i] = SW_READY;
                }
                break;
        }
    }
    switch_bits = x;
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the
// "os".  See comments at top to see how this should work.
void loop() {
    bus.update();   
    process_command();
    start_timmer();
    get_inputs();
    stop_timmer();
    if (!bus.is_busy()) load_response();
}
