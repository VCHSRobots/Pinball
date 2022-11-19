// This is for the NANO that is sending a square wave
// This tests the highest frequence squre wave

#define PIN_SQ 3

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(PIN_SQ, OUTPUT);
  //Serial.begin(115200);
}
int counter = 0;
// the loop function runs over and over again forever
void loop() {
  while(1) {
    digitalWrite(PIN_SQ, HIGH);   // turn the LED on (HIGH is the voltage level)
    delayMicroseconds(500);
    //delay(100);                       // wait for a second
    digitalWrite(PIN_SQ, LOW);    // turn the LED off by making the voltage LOW
    delayMicroseconds(500);
    //delay(50);                       // wait for a second
    //counter += 1;
    //if (counter % 10 == 0) {
    //  Serial.println(counter);
    //}
  }
}
