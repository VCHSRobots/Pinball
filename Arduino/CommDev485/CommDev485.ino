// CommDev485 -- comm development work for Pinball Machine
// dlb, Fall 2022

#define PIN_TX_ENABLE 2 // Pin to enable/disable RS-485 transmitter.
#define PIN_DB1 3  // Debug LEDs.
#define PIN_DB2 4 
#define PIN_DB3 5
#define PIN_DB4 6
#define NODE_ADDR 2  // Define our node address
#define DATA_LEN  3  // Length of our data payload to host
#define MSGLEN DATA_LEN+3 // Length of entire message to host

// Communication states...
#define COMM_DIRTY     0 // The channel is dirty.  Waiting for reset
#define COMM_READY     1 // The channel is clean. Waiting for any msg.
#define COMM_MSG_ADR   2 // Waiting for Message Address byte
#define COMM_MSG_DATA  3 // Waiting for Message Data bytes
#define COMM_MSG_CKSUM 4 // Waiting for Message Checksum byte

char msg_data[20];            // The message data. Max is 15 data bytes + 3 header bytes
volatile int imsg_ptr = 0;                // Location of next byte in msg data
volatile int node_addr = 0;               // Node address of current message being received
volatile int data_len = 0;                // Data Length of current message being received
volatile bool new_msg_waiting = false;    // If a new message is avaliable.
volatile int comm_state = COMM_DIRTY;     // Current state of the communication channel
volatile unsigned long last_byte_time = millis(); // Time of last byte received
bool tx_pending = false;                  // If there is a transmit pending
bool tx_waiting = false;                  // If we are waiting for the transmitter to finish
unsigned long tx_t0;                      // The time that a pending transmit was declared
unsigned long tx_wait_t0;                 // The time we started waiting on the transmitter
unsigned long tx_wtime = (87*6);          // Time for one outgoing msg, in usec. 

volatile char output_data[MSGLEN + 5];

int leds[4] = {PIN_DB1, PIN_DB2, PIN_DB3, PIN_DB4};
unsigned long ledtms[4] = {0, 0, 0, 0};
int ledstate[4] = {0, 0, 0, 0};   // States: 0=off, 1=on, 2=flash, 3=bink

void debug(int z) {
  if (z & 0x0001) digitalWrite(PIN_DB1, LOW);
  else digitalWrite(PIN_DB1, HIGH);
  if (z & 0x0002) digitalWrite(PIN_DB2, LOW);
  else digitalWrite(PIN_DB2, HIGH);
  if (z & 0x0004) digitalWrite(PIN_DB3, LOW);
  else digitalWrite(PIN_DB3, HIGH);
  if (z & 0x0008) digitalWrite(PIN_DB4, LOW);
  else digitalWrite(PIN_DB4, HIGH); 
}

void manage_leds() {
  unsigned long tnow = millis();
  for(int i = 0; i < 4; i++) {
    if (ledstate[i] == 0) digitalWrite(leds[i], HIGH);
    if (ledstate[i] == 1) digitalWrite(leds[i], LOW);
    if (ledstate[i] == 2) {
      if (tnow - ledtms[i] > 140) {
        ledstate[i] = 0;
        digitalWrite(leds[i], HIGH);
        return;
      }
      if (tnow - ledtms[i] > 70) digitalWrite(leds[i], HIGH);
      else digitalWrite(leds[i], LOW);
    }
    if (ledstate[i] == 3) {
      unsigned long telp = tnow - ledtms[i];
      if (telp > 100) { 
        digitalWrite(leds[i], LOW);
        ledtms[i] = tnow;
      } else {
        if (telp < 50) digitalWrite(leds[i], LOW);
        else digitalWrite(leds[i], HIGH);
      }
    }
  }
}

void led_on(int iled) {
  digitalWrite(leds[iled], LOW);
  ledstate[iled] = 1;
}

void led_off(int iled) {
  digitalWrite(leds[iled], HIGH);
  ledstate[iled] = 0;
}

void flash_led(int iled) {
  if(ledstate[iled] == 2) return;
  digitalWrite(leds[iled], LOW);
  ledtms[iled] = millis();
  ledstate[iled] = 2;
}

void blink_led(int iled) {
  if(ledstate[iled] == 3) return;
  digitalWrite(leds[iled], LOW);
  ledtms[iled] = millis();
  ledstate[iled] = 3;
}

void lightshow() {
  debug(0x0F);
  delay(100);
  debug(0x01);
  delay(100);
  debug(0x02);
  delay(100);
  debug(0x04);
  delay(100);
  debug(0x08);
  delay(100);
  debug(0x00);
}

void setup() {
  pinMode(PIN_DB1, OUTPUT);
  pinMode(PIN_DB2, OUTPUT);
  pinMode(PIN_DB3, OUTPUT);
  pinMode(PIN_DB4, OUTPUT);
  lightshow();
  pinMode(PIN_TX_ENABLE, OUTPUT);
  digitalWrite(PIN_TX_ENABLE, LOW);
  Serial.begin(115200);
  output_data[0] = 'e';
  output_data[1] = ((NODE_ADDR << 4) | DATA_LEN) & 0x00FF;
  output_data[2] = 'a';
  output_data[3] = 'b';
  output_data[4] = 'c';
  output_data[5] = checksum(output_data, 5);
}

// Calculate checksum for message
int checksum(char *buf, int nc) {
  int sum = 0;
  for(int i = 0; i < nc; i++) {
    sum += buf[i];
  }
  sum = sum & 0x00FF;
  return sum;
}

// Reads one byte from serial stream and returns it.
// If no input avaliable, returns -1. Should not block.
int read_serial_byte() {
  if(Serial.available() > 0) {
    int b = Serial.read();
    if (b >= 0) last_byte_time = millis();
    return b;
  }
  return -1;
}

// Reads data off the serial bus. 
bool read_serial_bus() {
  unsigned long tnow = millis();
  switch(comm_state) {
     case COMM_DIRTY: {
      flash_led(0);
      led_off(1);
      bool gotone = false;
      while (Serial.available()) {
        int b = Serial.read();
        last_byte_time = tnow;
        gotone = true;
      }
      if (gotone) return;
      if (tnow - last_byte_time > 10) {
        comm_state = COMM_READY;
      }
      return;
    }
    case COMM_READY: {
      led_on(1);
      int b = read_serial_byte();
      if (b < 0) return;
      // It should be an 'E' or an 'e'.
      if (b != 'E' && b != 'e') {
        comm_state = COMM_DIRTY;
        return;  
      }
      msg_data[0] = b;
      imsg_ptr = 1;
      comm_state = COMM_MSG_ADR;
    }
    case COMM_MSG_ADR: {
      if(tnow - last_byte_time > 2) {
        comm_state = COMM_DIRTY;
        return;
      }
      int b = read_serial_byte();
      if (b < 0) return;
      msg_data[imsg_ptr] = b;
      imsg_ptr++;
      node_addr = (b >> 4) & 0x000F;
      data_len = b & 0x000F;
      comm_state = COMM_MSG_DATA;
    }
    case COMM_MSG_DATA: {
      if(tnow - last_byte_time > 2) {
        comm_state = COMM_DIRTY;
        return;
      }
      while(true) {
        if (imsg_ptr >= data_len + 2) {
          comm_state = COMM_MSG_CKSUM;
          break;
        }
        int b = read_serial_byte();
        if (b < 0) return;
        msg_data[imsg_ptr] = b;
        imsg_ptr++;
      }
    }
    case COMM_MSG_CKSUM: {
      if(tnow - last_byte_time > 2) {
        comm_state = COMM_DIRTY;
        return;
      }
      int b = read_serial_byte();
      if (b < 0) return;
      int cksum = checksum(msg_data, imsg_ptr);
      if (cksum != b) {
        comm_state = COMM_DIRTY;
        return;
      }
      new_msg_waiting = true;
      comm_state = COMM_READY;
      return;
    }
  }
}

// Manages the serial bus.  Should be called on every loop cycle.
// Will not block.  You should have reply message queued up
// in case the host has a request.
void manage_serial_bus() {
  if (tx_waiting) {
    if (micros() - tx_wait_t0 < tx_wtime) return;
    digitalWrite(PIN_TX_ENABLE, LOW);
    tx_waiting = false;
  }
  if (tx_pending) {
    if (micros() - tx_t0 < 750) return;  // Must wait at least 0.5ms to start response.
    digitalWrite(PIN_TX_ENABLE, HIGH);
    for(int i = 0; i < DATA_LEN + 3; i++) Serial.write(output_data[i]);
    // Kludge... Here we should be able to do a Serial.flush(), but 
    // that takes too long (over 2.5ms).  Instead, we calculate how
    // long to keep the transmitter enabled, and then shut it down 
    tx_pending = false;
    tx_waiting = true;
    tx_wait_t0 = micros();
    return;
  }
 
  read_serial_bus();
  if (new_msg_waiting) {
    new_msg_waiting = false;
    if (msg_data[0] == 'E' && node_addr == NODE_ADDR) {
      flash_led(2);
      // TODO remove payload.
      tx_pending = true;
      tx_t0 = micros();
    }
  }
}      
      
void loop() {
  blink_led(3);
  manage_serial_bus();
  manage_leds();
}
