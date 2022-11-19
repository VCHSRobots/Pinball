// Header file for comm_buss
// Epic Robotz, Pinball Machine Project, Fall 2022
// dlb
//

#ifndef Comm_Bus_h
#define Comm_Bus_h

#include <Arduino.h>

#define PIN_TX_ENABLE 2 // Pin to enable/disable RS-485 transmitter.
#define PIN_DB1 14      // Debug LED, Labeled as A0
#define PIN_DB2 15      // Debug LED, Labeled as A1
#define PIN_DB3 16      // Debug LED, Labeled as A2
#define PIN_DB4 17      // Debug LED, labeled as A3

// Communication states...
#define COMM_DIRTY     0 // The channel is dirty.  Waiting for reset
#define COMM_READY     1 // The channel is clean. Waiting for any msg.
#define COMM_MSG_ADR   2 // Waiting for Message Address byte
#define COMM_MSG_DATA  3 // Waiting for Message Data bytes
#define COMM_MSG_CKSUM 4 // Waiting for Message Checksum byte

class CommBus {
  public:
    CommBus(int node_address, void (*on_receive)(uint8_t *msg, int n));
    void begin();
    void update();
    void set_response(uint8_t *msg, int n);

  private:
    int _our_node_address;                     // The address of our node
    void (*_on_receive)(uint8_t *msg, int n);  // Callback on receive
    uint8_t _response_data[16];                // Pending response msg
    int _response_data_len = 0;                // Pending response msg len
    bool _new_response_pending = false;        // If the response data is new
    uint8_t _output_data[20];                   // The message being sent back to the host

    int _comm_state = COMM_DIRTY;              // Current state of the communication channel
    uint8_t _rec_msg[20];                      // The input message.
    int _imsg_ptr = 0;                         // Location of next byte in msg data
    int _node_addr = 0;                        // Node address of current message being received
    int _data_len = 0;                         // Data Length of current message being received
    bool _new_msg_waiting = false;             // If a new message is available.
    unsigned long _last_byte_time = micros();  // Time of last byte received -- usecs
    bool _tx_pending = false;                  // If there is a transmit pending
    bool _tx_waiting = false;                  // If we are waiting for the transmitter to finish
    unsigned long _tx_t0;                      // The time that a pending transmit was declared
    unsigned long _tx_wait_t0;                 // The time we started waiting on the transmitter
    unsigned long _tx_wtime = (87*6);          // Time for one outgoing msg, in usec. 
              

    uint8_t checksum(uint8_t *buf, int nbuf);
    void prepare_outmsg();
    int read_serial_byte();
    bool read_serial_bus();
    void manage_serial_bus();

    // Debugging Stuff
    int _leds[4] = {PIN_DB1, PIN_DB2, PIN_DB3, PIN_DB4};
    unsigned long _ledtms[4] = {0, 0, 0, 0};
    int _ledstate[4] = {0, 0, 0, 0};   // States: 0=off, 1=on, 2=flash, 3=bink
    void debug(int z);
    void manage_leds();
    void led_on(int iled);
    void led_off(int iled);
    void flash_led(int iled);
    void blink_led(int iled);
    void lightshow();
};

#endif
