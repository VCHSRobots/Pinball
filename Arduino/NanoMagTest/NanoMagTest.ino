// Here, we are doing an experiment to test if the NANO can
// respond fast enough to trigger the bumper.  That is,
// we want the solenoid fully under computer control -- not
// just subject to the contact switch.

#define PIN_TRIG   3 // Input Trigger
#define PIN_BUMPER 4 // Output to bumper
#define PIN_LED    5 // Feedback LED 

#define SHOT_TIME  100  // Milliseconds to feed the soleniod
#define REST_TIME  80   // Required Rest time before new trigger allowed
#define SHUTOFF_COUNT 40 // Max number of shots in 10 sec window
#define SHUTOFF_SECS  10 // Number of secs to wait before resert after shut down.

#define STATE_READY    0    // Waiting for a new trigger
#define STATE_FIRED    1    // Giving a pulse of energy
#define STATE_RESTING  2    // Waiting for a given time before allowing new trigger
#define STATE_STUCK    3    // Waiting for the trigger input to reset.

int state = STATE_READY;  
unsigned long event_time = 0;     // Time condition changed
long score = 0;

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(PIN_TRIG, INPUT_PULLUP);
  pinMode(PIN_BUMPER, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  digitalWrite(PIN_BUMPER, 0);
  state = STATE_READY;
  event_time = millis();
}

bool trigger_active() {
  if (digitalRead(PIN_TRIG) == LOW) return true;
  else return false;
}

bool trigger_passive() {
  if (digitalRead(PIN_TRIG) == HIGH) return true;
  else return false; 
}

void fire_soleniod() {
  digitalWrite(PIN_BUMPER, HIGH);
}

void soleniod_off() {
  digitalWrite(PIN_BUMPER, LOW);
}

void led_on() {
  digitalWrite(PIN_LED, HIGH);
}

void led_off() {
  digitalWrite(PIN_LED, LOW);
}

void service_bumper() {
  unsigned long time_now = millis();
  unsigned long elp = time_now - event_time;
  switch(state) {
    case STATE_READY:
      if (trigger_active()) {
        fire_soleniod();
        event_time = time_now;
        state = STATE_FIRED;
        led_on();
        score++;
      }
      return;
    case STATE_FIRED:
      if (elp > SHOT_TIME) {
        event_time = time_now;
        soleniod_off();
        if (trigger_active()) state = STATE_STUCK;
        else state = STATE_RESTING;
      }
      return;
    case STATE_STUCK:
      if (trigger_passive()) state= STATE_RESTING;
      return;
    case STATE_RESTING:
      if (elp > REST_TIME) {
        state = STATE_READY;
        event_time = time_now;
        led_off();
      }
      return;
  }
}

char lineout[100];
long last_score = 0;

void loop() {
    service_bumper();
    if (last_score != score) {
      last_score = score;
      sprintf(lineout, "HIT! Score=%ld", last_score);
      Serial.println(lineout);
    }
}
