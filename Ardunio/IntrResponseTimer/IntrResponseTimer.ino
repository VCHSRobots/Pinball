// This is for the NANO reciving the square wave.  Checking response timing.

#define PIN_SQ 3  // Input Square Wave
#define PIN_OUT 4 // Output flasher

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(PIN_SQ, INPUT_PULLUP);
  pinMode(PIN_OUT, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_SQ), sq_ISR, FALLING);
  Serial.begin(115200);
}
long volatile counter = 0;
long last_counter = 0;
int volatile iled = 0;

void sq_ISR() {
    counter++;
    iled++;
    if (iled > 1) iled = 0;
    if (iled == 0) digitalWrite(PIN_OUT, LOW);
    else digitalWrite(PIN_OUT, HIGH);
}

void loop() {
  char lineout[100];
  long counter_now = counter;
  long delta = counter_now - last_counter;
  if (delta > 2000) {
    last_counter =  counter_now;
    sprintf(lineout, "Another 2000. Counter_now = %ld", counter_now);
    Serial.println(lineout);
  }
}
