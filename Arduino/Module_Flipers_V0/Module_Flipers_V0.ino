// EPIC Pinball Machine, Fall 2022
// Module for the Kickers
// 
// Controls 3 Coils and their associated Lights
// Demo Version -- Just to see the hardware work.
//
// This version assumes that the coils are fired
// with buttons one and two, and that it is safe
// to leave the coils on for an extended period.

#define PIN_COIL_1 6
#define PIN_COIL_2 5
#define PIN_COIL_3 3

#define PIN_SW_1 8
#define PIN_SW_2 7
#define PIN_SW_3 4

#define PIN_LED 13

char switches[] = {PIN_SW_1, PIN_SW_2, PIN_SW_3};
char coils[] = {PIN_COIL_1, PIN_COIL_2, PIN_COIL_3};
bool led_is_on = false;

void setup() {
  pinMode(PIN_COIL_1, OUTPUT);
  pinMode(PIN_COIL_2, OUTPUT);
  pinMode(PIN_COIL_3, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_SW_1, INPUT_PULLUP);
  pinMode(PIN_SW_2, INPUT_PULLUP);
  pinMode(PIN_SW_3, INPUT_PULLUP);
  digitalWrite(PIN_COIL_1, LOW);
  digitalWrite(PIN_COIL_2, LOW);
  digitalWrite(PIN_COIL_3, LOW);
  digitalWrite(PIN_LED, HIGH);
}

void led_on() {
  digitalWrite(PIN_LED, LOW);
  led_is_on = true;
}

void led_off() {
  digitalWrite(PIN_LED, HIGH);
  led_is_on = false;
}

// Use set_coil to turn it on or off with a strength arg.
// The strength arg should be between 0 and 255, where 0
// is off, and 255 is full strength.
void set_coil(int icoil, int strength) {
  int pin = coils[icoil];
  if (strength <= 0) {digitalWrite(pin, LOW); return; }
  if (strength >= 255) {digitalWrite(pin, HIGH); return; }
  analogWrite(pin, strength);
}

// Returns true if switch is closed, false otherwise.
bool get_switch(int iswitch) {
  int pin = switches[iswitch];
  if (digitalRead(pin) == LOW) return true;
  return false;
}

void loop() {
  if (get_switch(0)) {
    set_coil(0, 255);
  } else {
    set_coil(0, 0);
  }
  if (get_switch(1)) {
    set_coil(1, 255);
    set_coil(2, 255);
  } else {
    set_coil(1, 0);
    set_coil(2, 0);
  }
}
