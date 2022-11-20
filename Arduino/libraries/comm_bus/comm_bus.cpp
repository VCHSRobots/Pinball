// Epic Robotz, Pinball Machine Project, Fall 2022
// dlb
// 

#include "comm_bus.h"

#define PIN_LED 13               // Led to flash on msg received/sent
#define BAUD_RATE 115200         // Baud rate of the transmitter
#define BYTE_USEC 87             // Number of usecs per byte at BAUD_RATE
#define TX_TIME_PAD 100          // Number of usecs to pad TX enable

// Constructs the CommBus object. Provide the node address and the
// callback to be called when a message is received.
CommBus::CommBus(int node_address, void (*on_receive)(uint8_t *msg, int n)) {
  _our_node_address = node_address;
  _on_receive = on_receive;
  // blink_led(3);
}

// Call this to set the data that will be sent when a 
// response is needed.  The data is buffered, so 
// syncing it with comm activity is not necessary,
// but there is no guarantee that any specific data
// is sent back to the host.  That is, the caller may change
// the data multiple times before the host makes a request to see it.
void CommBus::set_response(uint8_t *data, int n) {
  for (int i = 0; i < n; i++) {
    _response_data[i] = data[i];
  }
  _response_data_len = n;
  _new_response_pending = true;
}

// Call this to enable communications with the host.
void CommBus::begin() {
  pinMode(PIN_DB1, OUTPUT);
  pinMode(PIN_DB2, OUTPUT);
  pinMode(PIN_DB3, OUTPUT);
  pinMode(PIN_DB4, OUTPUT);
  lightshow();
  pinMode(PIN_TX_ENABLE, OUTPUT);
  digitalWrite(PIN_TX_ENABLE, LOW);
  Serial.begin(BAUD_RATE);
  prepare_outmsg();
  for(int i = 0; i < 4; i++) led_off(i);
}

// Prepares the current output message.
void CommBus::prepare_outmsg() {
  _output_data[0] = 'e';
  _output_data[1] = ((_our_node_address & 0x000F) << 4) | _response_data_len;
  for(int i = 0; i < _response_data_len; i++) {
    _output_data[i + 2] = _response_data[i];
  }
  _output_data[_response_data_len + 2] = checksum(_output_data, _response_data_len + 2);
  _output_data_len = _response_data_len + 3;
  _new_response_pending = false;
}

// Call this as often as possible -- at least once per msec.
void CommBus::update() {
  manage_leds();   // Debugging, may be removed.
  if (_tx_waiting) {
    if (micros() - _tx_wait_t0 < _tx_wtime) return;
    digitalWrite(PIN_TX_ENABLE, LOW);
    _tx_waiting = false;
  }
  if (_tx_pending) {
    if (_new_response_pending) prepare_outmsg();
    if (micros() - _tx_t0 < 750) return;  // Must wait at least 0.5ms to start response.
    digitalWrite(PIN_TX_ENABLE, HIGH);
    for(int i = 0; i < _output_data_len; i++) Serial.write(_output_data[i]);
    // Kludge... Here we should be able to do a Serial.flush(), but 
    // that takes too long (over 2.5ms).  Instead, we calculate how
    // long to keep the transmitter enabled, and then shut it down 
    _tx_pending = false;
    _tx_waiting = true;
    _tx_wait_t0 = micros();
    _tx_wtime = (BYTE_USEC * _output_data_len) + TX_TIME_PAD;
    return;
  }
 
  read_serial_bus();
  if (_new_msg_waiting) {
    led_on(3);
    _new_msg_waiting = false;
    if (_rec_msg[0] == 'E' && _node_addr == _our_node_address) {
      // The message is for us!
      _tx_pending = true;
      _tx_t0 = micros();
      _on_receive(_rec_msg + 2, _data_len);
    }
  }
}

// Calculate checksum for message
uint8_t CommBus::checksum(uint8_t *buf, int nbuf) {
  uint16_t sum = 0;
  for(int i = 0; i < nbuf; i++) {
    sum += buf[i];
  }
  return (sum & 0x00FF);
}

// Reads one byte from serial stream and returns it.
// If no input avaliable, returns -1. Should not block.
int CommBus::read_serial_byte() {
  if(Serial.available() > 0) {
    int b = Serial.read();
    if (b >= 0) _last_byte_time = micros();
    return b;
  }
  return -1;
}

void CommBus::show_data(int d) {
  if (d & 0x08) led_on(0);
  else led_off(0);
  if (d & 0x04) led_on(1);
  else led_off(1);
  if (d & 0x02) led_on(2);
  else led_off(2);
  if (d & 0x01) led_on(3);
  else led_off(3);
}

// Reads data off the serial bus. 
bool CommBus::read_serial_bus() {
  unsigned long tnow = micros();
  switch(_comm_state) {
     case COMM_DIRTY: {
      //led_on(0);
      led_off(1);
      bool gotone = false;
      while (Serial.available()) {
        int b = Serial.read();
        _last_byte_time = tnow;
        gotone = true;
      }
      if (gotone) return;
      if (tnow - _last_byte_time > 5000) {
        _comm_state = COMM_READY;
      }
      return;
    }
    case COMM_READY: {
      //led_off(0);
      led_on(1);
      int b = read_serial_byte();
      if (b < 0) return;
      // It should be an 'E' or an 'e'.
      if (b != 'E' && b != 'e') {
        _comm_state = COMM_DIRTY;
        //led_on(2);
        return;  
      }
      _rec_msg[0] = b;
      _imsg_ptr = 1;
      _comm_state = COMM_MSG_ADR;
    } // Note: we WANT to fall through here...
    case COMM_MSG_ADR: {
      // if(tnow - _last_byte_time > 8000) {
      //   _comm_state = COMM_DIRTY;
      //   led_on(3);
      //   return;
      // }
      int b = read_serial_byte();
      if (b < 0) {
        led_on(0);
        return;
      }
      _rec_msg[_imsg_ptr] = b;
      _imsg_ptr++;
      _node_addr = (b >> 4) & 0x000F;
      _data_len = b & 0x000F;
      _comm_state = COMM_MSG_DATA;
    }  // Note: we WANT to fall through here...
    case COMM_MSG_DATA: {
      led_on(2);
      // if(tnow - _last_byte_time > 8000) {
      //   _comm_state = COMM_DIRTY;
      //   return;
      // }
      while(true) {
        if (_imsg_ptr >= _data_len + 2) {
          _comm_state = COMM_MSG_CKSUM;
          break;
        }
        int b = read_serial_byte();
        if (b < 0) return;
        _rec_msg[_imsg_ptr] = b;
        _imsg_ptr++;
      }
    } // Note: we WANT to fall through here...
    case COMM_MSG_CKSUM: {
      //led_on(3);
      //if(tnow - _last_byte_time > 1500) {
      // _comm_state = COMM_DIRTY;
      //  return;
      //}
      int b = read_serial_byte();
      if (b < 0) return;
      int cksum = checksum(_rec_msg, _imsg_ptr);
      if (cksum != b) {
        _comm_state = COMM_DIRTY;
        led_on(3);
        return;
      }
      //flash_led(3);
      _new_msg_waiting = true;
      _comm_state = COMM_READY;
      return;
    }
  }
}

// Debug Help

void CommBus::debug(int z) {
  if (z & 0x0001) digitalWrite(PIN_DB1, LOW);
  else digitalWrite(PIN_DB1, HIGH);
  if (z & 0x0002) digitalWrite(PIN_DB2, LOW);
  else digitalWrite(PIN_DB2, HIGH);
  if (z & 0x0004) digitalWrite(PIN_DB3, LOW);
  else digitalWrite(PIN_DB3, HIGH);
  if (z & 0x0008) digitalWrite(PIN_DB4, LOW);
  else digitalWrite(PIN_DB4, HIGH); 
}

void CommBus::manage_leds() {
  unsigned long tnow = millis();
  for(int i = 0; i < 4; i++) {
    if (_ledstate[i] == 0) digitalWrite(_leds[i], HIGH);
    if (_ledstate[i] == 1) digitalWrite(_leds[i], LOW);
    if (_ledstate[i] == 2) {
      if (tnow - _ledtms[i] > 140) {
        _ledstate[i] = 0;
        digitalWrite(_leds[i], HIGH);
        return;
      }
      if (tnow - _ledtms[i] > 70) digitalWrite(_leds[i], HIGH);
      else digitalWrite(_leds[i], LOW);
    }
    if (_ledstate[i] == 3) {
      unsigned long telp = tnow - _ledtms[i];
      if (telp > 200) { 
        digitalWrite(_leds[i], LOW);
        _ledtms[i] = tnow;
      } else {
        if (telp < 100) digitalWrite(_leds[i], LOW);
        else digitalWrite(_leds[i], HIGH);
      }
    }
  }
}

void CommBus::led_on(int iled) {
  digitalWrite(_leds[iled], LOW);
  _ledstate[iled] = 1;
}

void CommBus::led_off(int iled) {
  digitalWrite(_leds[iled], HIGH);
  _ledstate[iled] = 0;
}

void CommBus::flash_led(int iled) {
  if(_ledstate[iled] == 2) return;
  digitalWrite(_leds[iled], LOW);
  _ledtms[iled] = millis();
_ledstate[iled] = 2;
}

void CommBus::blink_led(int iled) {
  if(_ledstate[iled] == 3) return;
  digitalWrite(_leds[iled], LOW);
  _ledtms[iled] = millis();
  _ledstate[iled] = 3;
}

void CommBus::lightshow() {
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


