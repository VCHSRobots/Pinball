// Simple Echo Test
// dlb, Fall 2022

#define PIN_LED 14
#define BAUD_RATE 115200

unsigned long last_byte_time = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);
}

// Reads one byte from serial stream and returns it.
// If no input avaliable, returns -1. Should not block.
int read_serial_byte() {
  if(Serial.available() > 0) {
    int b = Serial.read();
    if (b >= 0) last_byte_time = micros();
    return b;
  }
  return -1;
}

void loop() {
  int b = read_serial_byte();
  if(b >= 0) {
    digitalWrite(PIN_LED, LOW);
    delay(500);
    Serial.write(b);
    digitalWrite(PIN_LED, HIGH);
  }
}
