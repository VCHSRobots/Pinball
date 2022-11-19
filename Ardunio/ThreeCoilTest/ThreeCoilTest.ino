// This is for a test board, to control 3 coils with
// 3 switch inputs.  The coils are all independent.

#define PIN_COIL_1 3
#define PIN_COIL_2 5
#define PIN_COIL_3 6

#define PIN_SW_1 4
#define PIN_SW_2 7
#define PIN_SW_3 8

#define PIN_LED 13

#define STATE_READY    0    // Waiting for a new trigger
#define STATE_FIRED    1    // Giving a pulse of energy
#define STATE_RESTING  2    // Waiting for a given time before allowing new trigger
#define STATE_STUCK    3    // Waiting for the trigger input to reset.
#define STATE_DEBOUNCE 4    // In Debouce condition

#define SHOT_TIME  50   // Milliseconds to feed the soleniod
#define REST_TIME  60   // Required Rest time before new trigger allowed

char switches[] = {PIN_SW_1, PIN_SW_2, PIN_SW_3};
char coils[] = {PIN_COIL_1, PIN_COIL_2, PIN_COIL_3};
char states[] = {STATE_READY, STATE_READY, STATE_READY };
unsigned long tnow = 0;
unsigned long event_times[] = { 0, 0, 0 };
unsigned long ledtime = 0;
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

// Must be called repeatedly from main loop to update the led.
void manage_led() {
  if (led_is_on) {
    if (tnow - ledtime > 50) {
        led_off();
        return;
    }
  }
}

// Call this to flash the led.
void fire_led() {
  led_on();
  ledtime = tnow;
}

// Call this repeatedly from the main loop to manage each coil.
void service_coil(int icoil) {
  unsigned long elp = tnow - event_times[icoil];
  switch(states[icoil]) {
    case STATE_READY:
      if (get_switch(icoil)) {
        set_coil(icoil, 255);
        event_times[icoil] = tnow;
        states[icoil] = STATE_FIRED;
        fire_led();
      }
      return;
    case STATE_FIRED:
      if (elp > SHOT_TIME) {
        event_times[icoil] = tnow;
        set_coil(icoil, 0);
        if (get_switch(icoil)) states[icoil] = STATE_STUCK;
        else states[icoil] = STATE_DEBOUNCE;
      }
      return;
    case STATE_STUCK:
      if (!get_switch(icoil)) {
        states[icoil] = STATE_DEBOUNCE;
        event_times[icoil] = tnow;
      }
      return;
    case STATE_DEBOUNCE:
      if (get_switch(icoil)) {
        states[icoil] = STATE_STUCK;
        return;
      }
      if (elp > 20) {
        states[icoil] = STATE_RESTING;
        event_times[icoil] = tnow;
        return;
      }
      return;
    case STATE_RESTING:
      if (elp > REST_TIME) {
        states[icoil] = STATE_READY;
        event_times[icoil] = tnow;
      }
      return;
  }
}


void loop() {
  tnow = millis();
  manage_led();
  for(int icoil = 0; icoil < 3; icoil++) {
    tnow = millis();
    service_coil(icoil);
  }
}
