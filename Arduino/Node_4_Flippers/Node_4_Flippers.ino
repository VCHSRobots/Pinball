/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Flipper Control Unit 
 * 
 * *** Address = 4
 * 
 * This module is for the Flipper Control.  The hardward is set up to
 * control 3 flippers, and 3 other devices, called "coils".  Inputs are
 * 6 switch contacts.  
 * 
 * The first two switches are called "buttons" and have direct control
 * over the flippers.  The condition of the other four switches are
 * monitored and reported to the host.
 * 
 * This module is commanded and controlled by the Raspberry Pi via
 * the RS-485 bus.
 * 
 * Theory of Operation:
 * The main loop is a multiplexer between monitoring the comm bus, monitoring
 * the input switches, and firing the coils.  Since all operations can 
 * take place in the 10s of microseconds, no framing is done.
 * 
 * Commands and arguments:   
 * 00      NOP            No operation, just getting status.
 * 100     ECHO           args: one byte to put in the echo registor
 * 10      FLIPPER_PWM    args: mask(1), pwm_0(1), pwm_1(1), delay(1)
 * 11      FLIPPER_CTRL   args: mask(1), ctrl(1), energized(1), delay(1)
 * 12      FLIPPER_ENABLE args: mask(1), enable/disable(1)
 * 13      COILS_PWM      args: mask(1), pwm_on(1)
 * 14      COILS_CTRL     args: mask(1), enable/disable(1), delay(1)
 * 15      BALL_CYCLE     args: enable(1)
 * 16      DEBOUNCE       args: mask(1), tunit_low(1), tunit_high(1) 
 * 
 * FLIPPER_PWM
 * Sets the PWM values to use when the flipper is energized.  Two values are given, 'pwm_0' and 
 * 'pwm_1'.  The first is used for the initial jolt of power that lasts 'delay' msecs.
 * Then pwm_1 is applied for as long as the button is held.  The first three bits in 'mask'
 * controls which flippers these parameters are applied to.  These can be used to control
 * the stenght of the flipper, and have it change dynamically throughout the game.  
 * 
 * FLIPPER_CTRL
 * Provides direct control over the flippers by the host, bypassing the buttons.  The
 * first three bits in mask control which flippers this command applies to.  A non-zero
 * 'ctrl' byte means to "take" control, whereas zero means to return control to the player.
 * If control is to be taken, a non-zero 'energized' means to energize the flipper. 
 * Once energized, the power profile follows the same curve as would 
 * a button press. 'delay' controls the how long the flippers are enetergized.  Zero
 * delay means indefinate.
 * 
 * FLIPPER_ENABLE
 * Sets wheither or not the flipplers are connected to the external buttons. Switch input one
 * controls flipper 1, and switch input 2 controls flippers 2 and 3.  The first three bits
 * in mask controls which flippers are effected by this command.  To enable, the
 * enable/disable byte must be non-zero.   
 * 
 * COILS_PWM
 * Sets the pwm values to use when the coils are on. The first three bits of
 * mask controls which coils these parameters are applied to.
 * 
 * COILS_CTRL
 * Sets the actual condition of the coil to engertized or deengergized. The first three
 * bis in mask control which coils this command applies to.  The enable/disable byte
 * should be non-zero to turn the coils on, and zero to turn them off.  If the coils are
 * to be turned on, then delay will control for how long, in msec.  A zero delay means
 * indefinate.
 * 
 * BALL_CYCLE
 * Sets the condition of the ball cycle servo.  It takes about a second to change servo
 * positions.  To release a ball into the game, the ball cycle should be enabled (non-zero) for
 * one second, and then returned to disabled (zero).  Timing of BALL_CYCLE is entirelly 
 * left up to the host.
 * 
 * DEBOUNCE
 * Sets the debounce filter for each switch input.  tuints_low is the number of
 * milliseconds that the input must be in the low state to be consideres a valid input.
 * tunits_high is the number of millisconds that the input must be in the high state before
 * a new trigger is allowed. Mask is six bits that controls to which switches this
 * parameter is applied.
 * 
 * Typical Power Profile for Flippers
 * The wiring of the flippers is tricky.  In our machine the flippera are controlled by
 * two coils and a End-Of-Swing (EOS) switch.  The first coil is a low resistance/high
 * current coil, and the second is a high resistance/low current coil.  The coils are
 * connected in series, and the EOS swich shorts out the second coil 
 * when the flipper is in it's non-energized state.  When voltage is applied, high
 * current flows through the first coil causing the flipper to move and the EOS switch to open.
 * When the switch opens, the combined coils move to a low current condition to 
 * hold the flipper in an energized state without using high current.
 * 
 * The FLIPPER_PWM can be used to limit the current in both conditions... Note that after
 * a delay for movement of the flipper, the second PWM value should probably be higher
 * than the first because the circult characteristics have changed to be a low current
 * condition.
 * 
 * Output Message:
 *   Byte 0:   Count of received cmds, rolls over at 255.
 *   Byte 1:   Count of errors, rolls over at 255.
 *   Byte 2:   Echo Registor -- returns argument given on a ECHO command.
 *   Byte 3:   Bit pattern of current switch conditions.
 *   Byte 4:   Switch counts for inputs 0 and 1
 *   Byte 5:   Switch counts for inputs 2 and 3
 *   Byte 6:   Switch counts for inputs 4 and 5
 *   Byte 7:   Switch counts for inputs 6 and 7
 * 
 * A switch count byte has the following bit pattern:  bbbb-aaaa were "bbbb" is the
 * count for the highered number switch, and "aaaa" is the switch count for the lowered
 * numnbered switch.  The counts run from zero to 15, and then roll over.
 * 
 * Special Note regarding Switches:
 * Switches 1-3 are assumed to be connected to the flipper buttons and the start button.
 * These are pulled low to activate.
 * Switch 4, 5, 6, and 7 are connected to the ball trough to sense presents of balls
 * in their respective position.  These are active high.
 * Switch 8 is a spare -- active low.
 * 
 * This code accounts for the way the switch is wired, and presents a logical "one" if
 * the switch is activated.
 * 
 */

#define NODE_ADDRESS 4
#define NFLIPPERS 3
#define NCOILS 3
#define NINPUTS 8

#include "comm_bus.h"

// Define the pins...
#define PIN_FLIPPER_1   6
#define PIN_FLIPPER_2   5
#define PIN_FLIPPER_3   3
#define PIN_COIL_1     11 
#define PIN_COIL_2     10
#define PIN_COIL_3      9
#define PIN_SW_1        8   // Assumed to be right hand flipper button
#define PIN_SW_2        7   // Assumed to be left hand flipper button
#define PIN_SW_3        4   // Assumed to be start button
#define PIN_SW_4       14   // Also A0 -- active high -- ball sensor 1
#define PIN_SW_5       15   // Also A1 -- active high -- ball sensor 2
#define PIN_SW_6       16   // Also A2 -- active high -- ball sensor 3
#define PIN_SW_7       17   // Also A3 -- active high -- ball sensor 4
#define PIN_SW_8       18   // Also A4 
#define PIN_BALL_CYCLE 12   // Controls the ball cycle servo

// Set the active value for the switch
#define SWA_1 LOW  
#define SWA_2 LOW
#define SWA_3 LOW
#define SWA_4 HIGH
#define SWA_5 HIGH
#define SWA_6 HIGH
#define SWA_7 HIGH
#define SWA_8 LOW


// Debugging Pins...
#define PIN_DB1 17
#define PIN_DB2 18
#define PIN_DB3 19

// Define the commands
#define CMD_NOP               0 
#define CMD_ECHO            100
#define CMD_FLIPPER_PWM      10
#define CMD_FLIPPER_CTRL     11
#define CMD_FLIPPER_ENABLE   12
#define CMD_COILS_PWM        13
#define CMD_COILS_CTRL       14
#define CMD_BALL_CYCLE       15
#define CMD_DEBOUNCE         16

// // Constants to help Switch Processing
// #define SW_BIT_1 0x0001
// #define SW_BIT_2 0x0002
// #define SW_BIT_3 0x0004
// #define SW_BIT_4 0x0008
// #define SW_BIT_5 0x0010
// #define SW_BIT_6 0x0020

// Switch Input States
#define SW_READY        0  // We are waiting for a trigger
#define SW_DB_ON        1  // Waiting for debounce on closing of the switch
#define SW_ACTIVE       2  // The switch is active -- a pulse is counted here.
#define SW_DB_OFF       3  // Waiting for debounce on opening of the switch

// Setup the pins
uint8_t input_pins[] = {PIN_SW_1, PIN_SW_2, PIN_SW_3, PIN_SW_4, PIN_SW_5, PIN_SW_6, PIN_SW_7, PIN_SW_8};
uint8_t flipper_pins[] = {PIN_FLIPPER_1, PIN_FLIPPER_2, PIN_FLIPPER_3};
uint8_t coil_pins[] = {PIN_COIL_1, PIN_COIL_2, PIN_COIL_3};

// Input Parameters and states for flippers
uint8_t flipper_pwm_0[] = {255, 255, 255};
uint8_t flipper_pwm_1[]  = {255, 255, 255};
uint32_t flipper_pwm_delay[] = {50, 50, 50};
uint32_t flipper_start_t0[] = {0, 0, 0};
bool flipper_energized[] = {false, false, false};
bool flipper_enable[] = {true, true, true};  // CHANGE BACK!!!
bool flipper_controled[] = {false, false, false};
bool flipper_ctrl_energized[] = {false, false, false};
uint32_t flipper_ctrl_delay[] = {0, 0, 0};
uint32_t flipper_ctrl_t0[] = {0, 0, 0};

// Input Parameters and states for coils
bool coil_energized[] = {false, false, false};
uint32_t coil_t0[] = {0, 0, 0};
uint32_t coil_delay[] = {0, 0, 0};
uint8_t coil_pwm[] = {255, 255, 255}; 

// Parameters and states for input switches.
uint32_t debounce_on[] = {1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000};
uint32_t debounce_off[] = {10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000};
uint32_t debounce_t0[] = {0, 0, 0, 0, 0, 0, 0, 0};
uint8_t switch_counts[] = {0, 0, 0, 0, 0, 0, 0, 0};
uint8_t switch_active_type[] = {SWA_1, SWA_2, SWA_3, SWA_4, SWA_5, SWA_6, SWA_7, SWA_8};
uint8_t switch_states[] = {SW_READY, SW_READY, SW_READY, SW_READY, SW_READY, SW_READY, SW_READY, SW_READY};
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

// ball trough stuff
bool ball_cycle = false;

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
        case CMD_FLIPPER_PWM: {
                int mask = cmd_bytes[1];
                int pwm_0 = cmd_bytes[2];
                int pwm_1 = cmd_bytes[3];
                uint32_t delay = ((uint32_t) cmd_bytes[4]) * 1000;
                for(int i = 0; i < 3; i++) {
                    if( (1 << i) & mask) {
                        flipper_pwm_0[i] = pwm_0;
                        flipper_pwm_1[i]  = pwm_1;
                        flipper_pwm_delay[i] = delay; 
                    }
                }
            }
            return true;
        case CMD_FLIPPER_CTRL: {
                int mask = cmd_bytes[1];
                bool ctrl = false;
                if (cmd_bytes[2]) ctrl = true;
                bool energize = false;
                if(cmd_bytes[3]) energize = true;
                uint32_t delay = ((uint32_t) cmd_bytes[4]) * 1000; 
                uint32_t tnow = micros();
                for(int i = 0; i < 3; i++) {
                    if( (1 << i) & mask) {
                        flipper_controled[i] = ctrl;
                        flipper_ctrl_energized[i] = energize;
                        flipper_ctrl_delay[i] = delay;
                        flipper_ctrl_t0[i] = tnow;
                    }
                }
            }
            return true;
        case CMD_FLIPPER_ENABLE: {
                int mask = cmd_bytes[1];
                bool enable = false;
                if (cmd_bytes[2]) enable = true;
                for(int i = 0; i < 3; i++) {
                    if( (1 << i) & mask) {
                        flipper_enable[i] = enable;
                    }
                }
            }
            return true;
        case CMD_COILS_PWM: {
                int mask = cmd_bytes[1];
                int pwm = cmd_bytes[2]; 
                for(int i = 0; i < 3; i++) {
                    if( (1 << i) & mask) {
                        coil_pwm[i] = pwm;
                    }
                }
            }
            return true;
        case CMD_COILS_CTRL:  {
                int mask = cmd_bytes[1];
                bool energize = false;
                if (cmd_bytes[2]) energize = true;
                uint32_t delay = ((uint32_t) cmd_bytes[3]) * 1000; 
                uint32_t tnow = micros();
                for(int i = 0; i < 3; i++) {
                    if ((1 << i) & mask) {
                        coil_energized[i] = energize;
                        coil_t0[i] = tnow;
                        coil_delay[i] = delay;
                    }
                }
            }  
            return true;
        case CMD_BALL_CYCLE: {
                if(cmd_bytes[1]) ball_cycle = true;
                else ball_cycle = false;
            }
            return true;
        case CMD_DEBOUNCE: {
                int mask = cmd_bytes[1];
                uint32_t tunit_on = cmd_bytes[2];
                uint32_t tunit_off = cmd_bytes[3];   
                tunit_on *= 1000;
                tunit_off *= 1000;
                for(int i = 0; i < 6; i++) {
                    if ( (1 << i) & mask) {
                        debounce_on[i] = tunit_on;
                        debounce_off[i] = tunit_off;
                    }
                }  
            }
            return true;
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
    response[2] = echo_reg;

    response[3] = switch_bits & 0x00FF;

    response[4] = ((switch_counts[1] << 4) & 0x00F0) | (switch_counts[0] & 0x000F);
    response[5] = ((switch_counts[3] << 4) & 0x00F0) | (switch_counts[2] & 0x000F);
    response[6] = ((switch_counts[5] << 4) & 0x00F0) | (switch_counts[4] & 0x000F);
    response[7] = ((switch_counts[7] << 4) & 0x00F0) | (switch_counts[6] & 0x000F);

    bus.set_response(response, 8);
}


// --------------------------------------------------------------------
// Setup the Flippers
void setup_flippers() {
    for(int i= 0; i < NFLIPPERS; i++) {
        pinMode(flipper_pins[i], OUTPUT);
        digitalWrite(flipper_pins[i], LOW);
    }
}

// --------------------------------------------------------------------
// Setup the coils
void setup_coils() {
    for(int i= 0; i < NCOILS; i++) {
        pinMode(coil_pins[i], OUTPUT);
        digitalWrite(coil_pins[i], LOW);
    }
}

// --------------------------------------------------------------------
// Setup the input switches
void setup_inputs() {
    for(int i= 0; i < NINPUTS; i++) {
        pinMode(input_pins[i], INPUT_PULLUP);
    }
}


// --------------------------------------------------------------------
// Setup the debugging pins
void setup_debug() {
    pinMode(PIN_DB1, OUTPUT);
    pinMode(PIN_DB2, OUTPUT);
    pinMode(PIN_DB3, OUTPUT);
    digitalWrite(PIN_DB1, HIGH);
    digitalWrite(PIN_DB2, HIGH);
    digitalWrite(PIN_DB3, HIGH);
}

// --------------------------------------------------------------------
// Main setup
void setup() {
    setup_debug();
    setup_flippers();
    setup_coils();
    setup_inputs();
    load_response();
    pinMode(PIN_BALL_CYCLE, OUTPUT);
    bus.begin();
}

// --------------------------------------------------------------------
// Sets the ball cycle condition
void send_ball_cycle() {
    if(ball_cycle) digitalWrite(PIN_BALL_CYCLE, HIGH);
    else digitalWrite(PIN_BALL_CYCLE, LOW);
}

// --------------------------------------------------------------------
// Sets the actual flipper output.
void set_flipper(int icoil, int pwm) {
    int pin = flipper_pins[icoil];
    if (pwm <= 0) digitalWrite(pin, LOW);
    else if (pwm >= 255) digitalWrite(pin, HIGH);
    else analogWrite(pin, pwm);
}

// --------------------------------------------------------------------
// Sets the actual coil output.
void set_coil(int icoil, int pwm) {
    int pin = coil_pins[icoil];
    if (pwm <= 0) digitalWrite(pin, LOW);
    else if (pwm >= 255) digitalWrite(pin, HIGH);
    else analogWrite(pin, pwm);
}

// --------------------------------------------------------------------
// Reads the inputs and applies filtering. 
void get_inputs() {
    uint16_t x = 0;
    for(int i = 0; i < NINPUTS; i++) {
        uint32_t tnow = micros();
        uint16_t ibit = (1 << i);
        bool bval = false;
        if (digitalRead(input_pins[i]) == switch_active_type[i]) bval = true;
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
// Manage flippers -- should be called very often for each flipper.
void manage_flippers(int i) {
    uint32_t tnow = micros();
    bool fon = false;
    if(flipper_controled[i]) {
        // Flipper is being controlled by the computer.
        if (flipper_ctrl_energized[i]) {
            // The computer wants to energize the flipper.
            if(flipper_ctrl_delay[i] == 0) {
                // The flipper should be held down forever
                fon = true;
            } else {
                // The flipper should be held down for a given time.
                if (tnow - flipper_ctrl_t0[i] > flipper_ctrl_delay[i]) {
                    fon = false;
                    flipper_ctrl_energized[i] = false;
                } else {
                    fon = true;
                }
            }
        }
    } else {
        // Flipper is being controlled by the human.
        if (flipper_enable[i]) {
            // The computer has allowed the human to be in control.
            // Here, apply logic to connect switches to the flippers
            fon = false;
            if (i == 0 && switch_states[0] == SW_ACTIVE) fon = true;
            if ((i == 1 || i == 2) && switch_states[1] == SW_ACTIVE) fon = true;
        }
    }
    // At this point we know if the flipper should be triggered or not,
    // by either the computer or the human.
    if (fon) {
        // We want to turn on the flipper.
        if(flipper_energized[i]) {
            // Its already on, follow the profile.
            if(tnow - flipper_start_t0[i] <= flipper_pwm_delay[i]) {
                set_flipper(i, flipper_pwm_0[i]);
            } else {
                set_flipper(i, flipper_pwm_1[i]);
            }
        } else {
            // Its not on, start it up.
            flipper_start_t0[i] = tnow;
            flipper_energized[i] = true;
            set_flipper(i, flipper_pwm_0[i]);
        }
    } else {
        // Turn it off
        flipper_energized[i] = false;
        set_flipper(i, 0);
    }
}

// --------------------------------------------------------------------
// Manage the coils
void manage_coils() {
    for(int i = 0; i < NCOILS; i++) {
        if (coil_energized[i]) {
            set_coil(i, coil_pwm[i]);
            if (coil_delay[i] > 0) {
                uint32_t tnow = micros();
                if(tnow - coil_t0[i] > coil_delay[i]) {
                    coil_energized[i] = false;
                    set_coil(i, 0);
                }
            }
        } else {
            set_coil(i, 0);
        }
    }
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the
// "os".  See comments at top to see how this should work.
void loop() {
    static int iflipper = 0;
    bus.update();   
    process_command();
    get_inputs();
    if (!bus.is_busy()) load_response();
    start_timmer(); 
    iflipper++;
    if(iflipper >= NFLIPPERS) iflipper = 0;
    manage_flippers(iflipper);
    if(iflipper == 0 && !bus.is_busy()) manage_coils(); 
    stop_timmer();
    send_ball_cycle();
}
