// Light Flasher.
//
// This is a test to see if we can control the car light.

#define PIN_LIGHT 5 // Input Trigger

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(PIN_LIGHT, OUTPUT);
  digitalWrite(PIN_LIGHT, 0);
  Serial.begin(115200);
}

bool light_on(float brightness) {
  int ib = brightness * 255;
  if (ib < 0) ib = 0;
  if (ib > 255) ib = 255;
  analogWrite(PIN_LIGHT, ib);
}

bool light_off() {
  digitalWrite(PIN_LIGHT, 0);
}

void flash() {
  light_on(1.0);
  delay(50);
  light_off();
}

void ramp_up() {
  int i;
  for(i = 0; i < 100; i++) {
    float b = i / 100.0;
    light_on(b);
    delay(40);
  }
  light_off();
}

void loop() {
    ramp_up();
    delay(1000);
    flash();
    delay(1000);
    for(int i = 0; i < 5; i++) {
      flash();
      delay(100);
    }
    delay(1000);
    light_on(0.05);
    delay(2000);
    light_off();
    delay(1000);
}
 
