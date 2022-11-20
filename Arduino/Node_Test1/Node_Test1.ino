// Tests the communication between one node and the Pi.
// dlb, Fall 2022

#include "comm_bus.h"

#define NODE_ADDRESS 4
#define PIN_LED1 13

void on_receive(byte *, int);
CommBus bus(NODE_ADDRESS, on_receive);
uint8_t msg[16];
int msg_len  = 0;

void setup() {
  pinMode(PIN_LED1, OUTPUT);
  digitalWrite(PIN_LED1, HIGH);
  msg[0] = 'a';
  msg[1] = 'b';
  msg[2] = 'c';
  msg_len = 3;
  bus.set_response(msg, msg_len);
  bus.begin();
}

// Called when a message is received.
void on_receive(byte *msg, int n) {
  if(n <= 0) return;
  if(msg[0] == '1') digitalWrite(PIN_LED1, LOW);
  else digitalWrite(PIN_LED1, HIGH);
}

unsigned long tlast = millis();
int cnt;

void loop() {
  unsigned long tnow = millis();
  if (tnow - tlast > 1000) {
    cnt++;
    msg[0] = (cnt >> 8) & 0x00FF;
    msg[1] = cnt & 0x00FF;
    //bus.set_response(msg, 2);
    tlast = tnow;
  }
  bus.update();
}
