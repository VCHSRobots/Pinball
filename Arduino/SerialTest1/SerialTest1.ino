
#define NODE_ADDR 2  // Define our node address
#define DATA_LEN  3  // Length of our data payload to host
#define MSGLEN DATA_LEN+3 // Length of entire message to host

// Communication states...
#define COMM_DIRTY     0 // The channel is dirty.  Waiting for reset
#define COMM_READY     1 // The channel is clean. Waiting for any msg.
#define COMM_MSG_ADR   2 // Waiting for Message Address byte
#define COMM_MSG_DATA  3 // Waiting for Message Data bytes
#define COMM_MSG_CKSUM 4 // Waiting for Message Checksum byte

volatile char msgdata[20];                // The message data. Max is 15 data bytes + 3 header bytes
volatile int imsg_ptr = 0;                // Location of next byte in msg data
volatile int node_addr = 0;               // Node address of current message being received
volatile int data_len = 0;                // Data Length of current message being received
volatile bool new_msg_waiting = false;    // If a new message is avaliable.
volatile int comm_state = COMM_DIRTY;     // Current state of the communication channel
volatile unsigned long last_byte_time = millis(); // Time of last byte received 

volatile char output_data[MSGLEN + 5];

void setup() {
  Serial.begin(115200);
  output_data[0] = 'e' 
  output_data[1] = ((NODE_ADDR << 4) | MSGLEN) & 0x00FF;
  output_data[2] = 'a';
  output_data[3] = 'b';
  output_data[4] = 'c';
  output_data[5] = checksum(databuf, 5);
}

// Calculate checksum for message
int checksum(char *buf, int nc) {
  int sum = 0;
  for(int i = 0; i < nc; i++) {
    sum += buf[i];
  }
  sum = sum & 0x00FF;
  return sum
}

// Reads one byte from serial stream and returns it.
// If no input avaliable, returns -1. Should not block.
int read_serial_byte() {
  if(Serial.avaliable() > 0) {
    int b = Serial.read();
    if (b > 0) last_byte_time = millis();
    return b;
  }
  return -1;
}

// Reads data off the serial bus. 
bool read_serial_bus() {
  unsigned long tnow = millis();
  switch(comm_state) {
    case COMM_DIRTY:
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
    case COM_READY:
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
    case COMM_MSG_ADR:
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
    case COMM_MSG_DATA:
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
    case COMM_MSG_CKSUM:
      if(tnow - last_byte_time > 2) {
        comm_state = COMM_DIRTY;
        return;
      }
      int b = read_serial_byte();
      if (b < 0) return;
      cksum = checksum(msg_data, imsg_ptr);
      if (cksum != b) {
        comm_state = COMM_DIRTY;
        return;
      }
      new_msg_waiting = true;
      comm_state = COMM_READY;
      return;
   }
}

// Manages the serial bus.  Should be called on every loop cycle.
// Will not block.  You should have reply message queued up
// in case the input is from the host.
void manage_serial_bus() {
  read_serial_bus();
  if (new_msg_waiting) {
    new_msg_waiting = false;
    if (msg_data[0] == 'E' && node_addr == NODE_ADDR) {
      // Its from the host for us!
      // TODO: remove payload.
      // Respond quickly:
      digitalWrite(PIN_TX_ENABLE, HIGH);
      Serial.write(output_data, DATA_LEN + 3);
      // TODO: Figure out a way to disable the transmitter without blocking.
      Serial.flush();  // This should block until all is written, at most 2 ms.
      digitalWrite(PIN_TX_ENABLE, LOW);
    }
}


      
      
    
        

      
      
      
      
      while(true) {
        int b = read_serial
      }
      if (tnow 
      
  }
  
  char databuf[16];
  int iptr = 0;
  if (!clean_channel) {
      bool gotone = false;
      while (Serial.available()) {
        b1 = Serial.read();
        last_byte_time = tnow;
        gotone = true;
      }
      if (gotone) return;
      if (tnow - last_byte_time > 10) clean_channelhannel = true;
      if (!clean_channel) return;
  }
  if 
  // Add chars to our input buf, keep track of state.
  while (Serial.avaliable()) {
    if in_buf
  }

  
}


void loop() {
  if ( Serial.available()) 
  {
    char ch = Serial.read();
    if (ch == 'a') Serial.println("yes");
    if (ch == 'b') Serial.println("no");
    if (ch == 'c') Serial.println("maybe");
  }
}
