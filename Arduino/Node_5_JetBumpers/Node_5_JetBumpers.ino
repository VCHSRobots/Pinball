/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Jet Bumper Control Unit 
 * 
 * *** Address = 5
 * 
 * This module is for the Jet Bumpers.  The hardward is set up to
 * control 3 coils, 3 lamps, and 3 inputs.
 * 
 * There is specail logic to tie the outputs to the inputs.  That is,
 * the inputs can cause the coils to fire and lights to flash.
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
 * 20      COILS_PWM      args: mask(1), pwm(1), ontime(1), resttime(1)
 * 21      COILS_ENABLE   args: mask(1), enabled(1)
 * 22      COILS_TRIGGER  args: mask(1), energized(1)
 * 23      LAMP_ENABLE    args: mask(1), enabled(1)
 * 24      LAMP_PWM       args: mask(1), pwm_on(1), ontime(1)
 * 25      LAMP_SOLID     args: mask(1), Brightness(1)
 * 26      LAMP_FLASH     args: mask(1), Brightness(1), onttime(1)
 * 27      LAMP_MODULATE  args: mask(1), B1(1), B2(1), steps(1)
 * 28      DEBOUNCE       args: mask(1), tunit_low(1), tunit_high(1) 
 * 
 * Note, in all following commands, 'mask' is a bit map that controls which
 * coils and lamps to which the command is applied.
 * 
 * COILS_PWM
 * Sets the pwm values to use when the coil is energized.  Also sets how long to 
 * energize the coil upon a trigger, and how lone to wait between triggers. 'ontime'
 * and 'resttime' are given in milliseconds.  
 * 
 * COILS_ENABLE
 * Controls whether or not the coils will repond to the switch inputs. If enabled,
 * the switch inputs override computer control.  'enabled' is non-zero to enable
 * the coils.
 * 
 * COILS_TRIGGER
 * Allows computer to fire the coils. 'enabled' is non-zero to fire the coil,
 * whereas zero causes the coil to return to the ready state.
 * 
 * LAMPS_ENABLE
 * Controls whether or not the lamps will respond to the switch inputs.  If enabled,
 * the switch inputs override computer control.  'enabled' is non-zero to enable 
 * the lamps.
 * 
 * LAMP_PWM
 * Sets the pwm value and delay values to use when under switch inputs.  'ontime' is
 * in milliseconds.
 * 
 * LAMP_SOLID
 * Allows the computer to set the lamp to a solid value.  To return control exclusively
 * to the switches, this value should be set to zero.
 * 
 * LAMP_FLASH
 * Allows the computer to flash the lamp.  After the lamp is flashed, it is returned
 * to the mode it was previously in.  'onttime' is given in milliseconds
 * 
 * LAMP_MODULAE
 * Sets the lamp in a modulation mode.  B1 and B2 are the pwm values to use at the
 * edges of the modulation window, and 'steps' is the time span of the window in 25 msec
 * units.  For example, steps=40 is a one second window.
 * 
 * DEBOUNCE
 * Sets the debounce filter for each switch input.  tuints_low is the number of
 * milliseconds that the input must be in the low state to be consideres a valid input.
 * tunits_high is the number of millisconds that the input must be in the high state before
 * a new trigger is allowed.
 * 
 * Output Message:
 *   Byte 0:   Count of received cmds, rolls over at 255.
 *   Byte 1:   Count of errors, rolls over at 255.
 *   Byte 2:   Echo Registor -- returns argument given on a ECHO command.
 *   Byte 3:   Bit pattern of current switch conditions.
 *   Byte 4:   Switch counts for input 0
 *   Byte 5:   Switch counds for input 1
 *   Byte 5:   Switch counts for input 2
 * 
 * The switch counts are a full byte, and roll over after 255 hits.
 * 
 */

#define NODE_ADDRESS 5
#define NCOILS 3
#define NLAMPS 3
#define NINPUTS 3

#include "comm_bus.h"

// Define the pins...
#define PIN_LAMP_1  11
#define PIN_LAMP_2  10
#define PIN_LAMP_3   9
#define PIN_COIL_1   6 
#define PIN_COIL_2   5
#define PIN_COIL_3   3
#define PIN_SW_1     4
#define PIN_SW_2     7 
#define PIN_SW_3     8

// Debugging Pins...
#define PIN_DB1 16
#define PIN_DB2 17
#define PIN_DB3 18
#define PIN_DB4 19

// Define the commands
#define CMD_NOP               0 
#define CMD_ECHO            100
#define CMD_COILS_PWM        20
#define CMD_COILS_ENABLE     21
#define CMD_COILS_TRIGGER    22
#define CMD_LAMP_ENABLE      23
#define CMD_LAMP_PWM         24
#define CMD_LAMP_SOLID       25
#define CMD_LAMP_FLASH       26
#define CMD_LAMP_MODULATE    27
#define CMD_DEBOUNCE         28

// Switch Input States
#define SW_READY        0  // We are waiting for a trigger
#define SW_DB_ON        1  // Waiting for debounce on closing of the switch
#define SW_ACTIVE       2  // The switch is active -- a pulse is counted here.
#define SW_DB_OFF       3  // Waiting for debounce on opening of the switch

// Coil States
#define COIL_READY      0 // Coil is off, ready to be triggers
#define COIL_FIRED      1 // Coil is energized
#define COIL_RESTING    2 // Coil is de-energized, resting for next trigger.

// Lamp modes
#define LAMP_READY      0 // Lamp is not being controls by computer
#define LAMP_SOLID      2 // Lamp is on soild, and Computer given pwm.
#define LAMP_FLASH      3 // Lamp is being flashed by the computer
#define LAMP_MODULATE   4 // Lamp is being modulated by the computer

// Setup the pins
uint8_t input_pins[] = {PIN_SW_1, PIN_SW_2, PIN_SW_3};
uint8_t lamp_pins[] = {PIN_LAMP_1, PIN_LAMP_2, PIN_LAMP_3};
uint8_t coil_pins[] = {PIN_COIL_1, PIN_COIL_2, PIN_COIL_3};

// Input Parameters and states for coils
bool coil_trig_pending[] = {false, false, false};
uint8_t coil_pwm[] = {255, 255, 255};
uint8_t coil_ontime[] = {50, 50, 50};
uint8_t coil_resttime[] = {10, 10, 10};
uint32_t coil_start_t0[] = {0, 0, 0};
uint8_t coil_state[] = {COIL_READY, COIL_READY, COIL_READY};
bool coil_enable[] = {false, false, false};

// Parameters and states for input switches.
uint32_t debounce_on[] = {1000, 1000, 1000};
uint32_t debounce_off[] = {2000, 2000, 2000};
uint32_t debounce_t0[] = {0, 0, 0};
uint8_t switch_counts[] = {0, 0, 0};
uint8_t switch_states[] = {SW_READY, SW_READY, SW_READY};
uint8_t switch_bits = 0;

// Parameters and states for the lamps
bool lamp_enable[] = {false, false, false};
bool lamp_triggered[] = {false, false, false};
bool lamp_trig_pending[] = {false, false, false};
uint8_t lamp_pwm[] = {255, 255, 255};
uint8_t lamp_ontime[] = {50, 50, 50};

uint32_t lamp_t0[] = {0, 0, 0};
uint8_t lamp_mode[] = {LAMP_READY, LAMP_READY, LAMP_READY};
uint8_t lamp_brightness_0[] = {0, 0, 0};
uint8_t lamp_brightness_1[] = {0, 0, 0};
uint8_t lamp_modpwm[] = {0, 0, 0};
uint8_t lamp_steps[] = {0, 0, 0};
uint8_t lamp_istep[] = {0, 0, 0};  // Contains step and direction for modulation.
uint8_t lamp_previous[] = {LAMP_READY, LAMP_READY, LAMP_READY};
uint8_t lamp_flash_brightness[] = {0, 0, 0};
uint8_t lamp_flash_ontime[] = {0, 0, 0};
uint32_t lamp_flash_t0[] = {0, 0, 0};

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
        case CMD_COILS_PWM: {
                int mask = cmd_bytes[1];
                int pwm = cmd_bytes[2];
                int ontime = cmd_bytes[3];
                int resttime = cmd_bytes[4];
                for(int i = 0; i < NCOILS; i++) {
                    if ( (1 << i) & mask) {
                        coil_pwm[i] = pwm;
                        coil_ontime[i] = ontime;
                        coil_resttime[i] = resttime;
                    }
                } 
            }
            return true;
        case CMD_COILS_ENABLE: {
                int mask = cmd_bytes[1];
                bool enable = false;
                if (cmd_bytes[2]) enable = true;
                for(int i = 0; i < NCOILS; i++) {
                    if ( (1 << i) & mask) {
                        coil_enable[i] = enable;
                    }
                } 
            }
            return true;
        case CMD_COILS_TRIGGER: {
                int mask = cmd_bytes[1];
                bool trigger = false;
                if (cmd_bytes[2]) trigger = true;
                uint32_t tnow = millis();
                for(int i = 0; i < NCOILS; i++) {
                    if ( (1 << i) & mask) {
                        if(trigger) coil_state[i] = COIL_FIRED;
                        else coil_state[i] = COIL_READY;
                        coil_start_t0[i] = tnow;
                    }
                } 
            }
            return true;
        case CMD_LAMP_ENABLE: {
                int mask = cmd_bytes[1];
                bool enabled = false;
                if (cmd_bytes[2]) enabled = true;
                for(int i = 0; i < NLAMPS; i++) {
                    if ( (1 << i) & mask) {
                        lamp_enable[i] = enabled;
                    }
                } 
            }
            return true;
        case CMD_LAMP_PWM: {
                int mask = cmd_bytes[1];
                uint8_t pwm = cmd_bytes[2];
                uint8_t ontime = cmd_bytes[3];
                for(int i = 0; i < NLAMPS; i++) {
                    if ( (1 << i) & mask) {
                        lamp_pwm[i] = pwm;
                        lamp_ontime[i] = ontime;
                    }
                }
            }
            return true;
        case CMD_LAMP_SOLID: {
                int mask = cmd_bytes[1];
                uint8_t pwm = cmd_bytes[2];
                uint8_t mode = LAMP_READY;
                if (pwm > 0) mode = LAMP_SOLID;
                for(int i = 0; i < NLAMPS; i++) {
                    if ( (1 << i) & mask) {
                        lamp_mode[i] = mode;
                        lamp_brightness_0[i] = pwm;
                    }
                }
            }
            return true;
        case CMD_LAMP_FLASH: {
                int mask = cmd_bytes[1];
                uint8_t pwm = cmd_bytes[2];
                uint8_t ontime = cmd_bytes[3];
                uint32_t tnow = millis();
                for(int i = 0; i < NLAMPS; i++) {
                    if ( (1 << i) & mask) {
                        if (lamp_mode[i] != LAMP_FLASH) lamp_previous[i] = lamp_mode[i];
                        lamp_mode[i] = LAMP_FLASH;
                        lamp_flash_brightness[i] = pwm;
                        lamp_flash_ontime[i] = ontime;
                        lamp_flash_t0[i] = tnow;
                    }
                }
            }
            return true;
        case CMD_LAMP_MODULATE: {
                int mask = cmd_bytes[1];
                uint8_t b0 = cmd_bytes[2];
                uint8_t b1 = cmd_bytes[3];
                if (b0 > b1) {
                    uint8_t btemp = b0;
                    b0 = b1;
                    b1 = btemp;
                }
                uint8_t nsteps = cmd_bytes[4];
                if (nsteps > 127) nsteps = 127;
                for(int i = 0; i < NLAMPS; i++) {
                    if ( (1 << i) & mask) {
                        lamp_mode[i] = LAMP_MODULATE;
                        lamp_brightness_0[i] = b0;
                        lamp_brightness_1[i] = b1;
                        lamp_steps[i] = nsteps;
                        lamp_istep[i] = 0;
                    }
                }
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
    uint8_t response[10];

    response[0] = cmd_count & 0x00FF;
    response[1] = err_count & 0x00FF;
    response[2] = echo_reg;

    response[3] = switch_bits;

    response[4] = switch_counts[0] & 0x00FF;
    response[5] = switch_counts[1] & 0x00FF;
    response[6] = switch_counts[2] & 0x00FF;

    bus.set_response(response, 7);
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
// Setup the lamps
void setup_lamps() {
    for(int i= 0; i < NLAMPS; i++) {
        pinMode(input_pins[i], OUTPUT);
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
    setup_coils();
    setup_lamps();
    setup_inputs();
    load_response();
    bus.begin();
}

// --------------------------------------------------------------------
// Sets the actual lamp output.
void set_lamp(int ilamp, int pwm) {
    int pin = lamp_pins[ilamp];
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
    uint8_t x = 0;
    for(int i = 0; i < NINPUTS; i++) {
        uint32_t tnow = micros();
        int ibit = (1 << i);
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
                        lamp_trig_pending[i] = true;
                        coil_trig_pending[i] = true;
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
// Manage coils -- should be called very often for each coil.
void manage_coils(int i) {
    uint32_t tnow = millis();
    switch(coil_state[i]) {
        case COIL_READY: {
                set_coil(i, 0);  
                if (coil_enable[i]) {
                    if (coil_trig_pending[i]) {
                        coil_trig_pending[i] = false;
                        set_coil(i, coil_pwm[i]);
                        coil_state[i] = COIL_FIRED;
                        coil_start_t0[i] = tnow;
                        return;
                    }
                }
            }
            return;
        case COIL_FIRED: {
                set_coil(i, coil_pwm[i]);
                if(tnow - coil_start_t0[i] > coil_ontime[i]) {
                    set_coil(i, 0);
                    coil_state[i] = COIL_RESTING;
                    coil_start_t0[i] = tnow;
                    return;
                }
            }
            return;
        case COIL_RESTING: {
                set_coil(i, 0);
                if(tnow - coil_start_t0[i] > coil_resttime[i]) {
                    coil_state[i] = COIL_READY;
                    coil_trig_pending[i] = false;
                    return;
                }
            }
            return;
    }
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
    int nsteps = lamp_steps[ilamp];
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
// Manage the lamps.  Once every 25 milliseconds, set newstep to true
// for each lamp.
void manage_lamps(int i, bool newstep) {
    uint32_t tnow = millis();
    if (lamp_triggered[i]) {
        set_lamp(i, lamp_pwm[i]);
        if (tnow - lamp_t0[i] > lamp_ontime[i]) {
            lamp_triggered[i] = false;
            set_lamp(i, 0);
        } else {
            return;
        }
    }
    if (lamp_enable[i]) {
        if (lamp_trig_pending[i]) {
            lamp_trig_pending[i] = false;
            lamp_triggered[i] = true;
            lamp_t0[i] = tnow;
            set_lamp(i, lamp_pwm[i]);
            return;
        }
    }
    lamp_trig_pending[i] = false;
    if (lamp_mode[i] == LAMP_READY) {
        set_lamp(i, 0); 
        return;
    }
    if (lamp_mode[i] == LAMP_SOLID) {
        set_lamp(i, lamp_brightness_0[i]);
        return;
    }
    if (lamp_mode[i] == LAMP_FLASH) {
        set_lamp(i, lamp_flash_brightness[i]);
        if(tnow - lamp_flash_t0[i] > lamp_flash_ontime[i]) {
            lamp_mode[i] = lamp_previous[i];
            set_lamp(i, lamp_brightness_0[i]);
            return;
        }
    }
    if (lamp_mode[i] == LAMP_MODULATE) {
        if(newstep) lamp_modpwm[i] = cal_brightness(i);
        set_lamp(i, lamp_modpwm[i]);
    }
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the
// "os".  See comments at top to see how this should work.
void loop() {
    static int icnt = 0;
    static uint32_t last_25frame = millis();
    static bool newframe = false;

    uint32_t tnow = millis();
    if (tnow - last_25frame >= 25) {
        newframe = true;
        last_25frame = tnow;
    }

    bus.update();   
    process_command();
    start_timmer();
    get_inputs();
    if (!bus.is_busy()) load_response();
    icnt++;
    if(icnt >= 6) icnt = 0;
    switch(icnt) {
        case 0: manage_coils(0); break;
        case 1: manage_coils(1); break;
        case 2: manage_coils(2); break;
        case 3: manage_lamps(0, newframe); break;
        case 4: manage_lamps(1, newframe); break;
        case 5: manage_lamps(2, newframe);  newframe = false; break;
    }
    stop_timmer();
}

