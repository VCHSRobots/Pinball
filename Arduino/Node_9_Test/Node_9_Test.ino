/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Test Node 
 * 
 * *** Address = 9
 * 
 * This module is for the Testing.  It is a dummy node that
 * only implements NOP and ECHO.
 * 
 * This module is commanded and controlled by the Raspberry Pi via
 * the RS-485 bus.
 * 
* Commands and arguments:   
 * 00      NOP            No operation, just getting status.
 * 100     ECHO           args: one byte to put in the echo registor
 * 
 * Output Message:
 *   Byte 0:   Count of received cmds, rolls over at 255.
 *   Byte 1:   Count of errors, rolls over at 255.
 *   Byte 2:   Echo Registor -- returns argument given on a ECHO command.
 * 
 */

#define NODE_ADDRESS 9

#include "comm_bus.h"

// Define the commands
#define CMD_NOP               0 
#define CMD_ECHO            100

// Comm Bus Stuff
void on_receive(byte *, int);
CommBus bus(NODE_ADDRESS, on_receive);
bool cmd_pending = false;
uint8_t cmd_bytes[16];
int cmd_bytes_len = 0;
uint16_t cmd_count = 0;
uint16_t err_count = 0;
uint8_t echo_reg = 0;

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
    bus.set_response(response, 3);
}

// --------------------------------------------------------------------
// Main setup
void setup() {
    load_response();
    bus.begin();
}

// --------------------------------------------------------------------
// Here is the main loop function that is repeatedly called by the
// "os".  See comments at top to see how this should work.
void loop() {
    bus.update();   
    process_command();
    if (!bus.is_busy()) load_response();
}

