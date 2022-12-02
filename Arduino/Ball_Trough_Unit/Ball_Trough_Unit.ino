/*
 * Pinball Machine, EPIC Robotz, Fall 2022
 * Ball_Trough_Unit
 * 
 * Controls the Servo on the Ball Trough, and
 * also monitors the sensors on the Ball Trough.
 * 
 * This device is not connected to the comm_bus
 * that is used by the Raspberry pi to control
 * all the nodes.  Instead this device is a 
 * sister unit for the Flipper Node.  
 * 
 * Inputs are:
 *   4 IR sensors on the Ball Trough -- Input into A0-A3
 *   1 Control wire to command the servo
 * 
 * Outputs are:
 *   4 IR sensor conditions
 * 
 */


#include <Servo.h>

#define PIN_LED   13  // Used to tell condition of input for servo

#define PIN_SERVO 12

#define PIN_IRD_1 A0
#define PIN_IRD_2 A1
#define PIN_IRD_3 A2
#define PIN_IRD_4 A3

#define PIN_BALL_1 6
#define PIN_BALL_2 5
#define PIN_BALL_3 4
#define PIN_BALL_4 3

#define PIN_SERVO_CTRL 2

#define DETECT_THRESHOLD 500

uint8_t detector_pins[] = {PIN_IRD_1, PIN_IRD_2, PIN_IRD_3, PIN_IRD_4};
uint8_t ball_pins[] = {PIN_BALL_1, PIN_BALL_2, PIN_BALL_3, PIN_BALL_4};

// Define Servo Parameters
#define PWM_MIN   800 // Min micro seconds in PWM Pulse
#define PWM_MAX  2200 // Max micro seconds in PWM Pulse
#define PWM_OPEN  1365
#define PWM_CLOSE 1725
#define PWM_MID  (PWM_MAX - PWM_MIN)/2
#define MAX_USEC  1000 // Max velocity allowed: in units of pulsewidth change in usec per second.
#define USEC_PER_MSEC (1000 / MAX_USEC) // Number of micro seconds needed to move one usec in pulse.

// Servo Variables
Servo servo;  
double current_pwm = PWM_MID;         // Servo position in usec, as best we know.
double target_pwm = PWM_MID;          // Target servo position
uint32_t last_servo_cmd_time = 0;     // last time servo was commanded, in usec.
int16_t last_servo_cmd_pwm = PWM_MIN; // last pwm command issued to servo.
uint32_t last_servo_update_time = 0;  // Time at which we last updated the servo.
uint32_t last_report_time = 0;        // Time that we issued last debugging report.
bool servo_inited = false;            // For first time though the update loop.

void setup() {
  servo.attach(PIN_SERVO, PWM_MIN, PWM_MAX);  
  for (int i = 0; i < 4; i++) {
    pinMode(detector_pins[i], INPUT);
    pinMode(ball_pins[i], OUTPUT);
    digitalWrite(ball_pins[i], HIGH);   
  }
  pinMode(PIN_SERVO_CTRL, INPUT_PULLUP);
  // Serial.begin(115200);
  servo_inited = false;
}

// Monitors the servo input.  Returns true for Open, and false for Close.
bool servo_action() {
  if (digitalRead(PIN_SERVO_CTRL) == LOW) {
      digitalWrite(PIN_LED, LOW);
      return false;
  } else {
      digitalWrite(PIN_LED, HIGH);
      return true;
  }
}

// Sends the condition of the IR sensors to the host.
void send_sensors() {
  for(int i = 0; i < 4; i++) {
    int reading = analogRead(detector_pins[i]);
    if (reading > DETECT_THRESHOLD) digitalWrite(ball_pins[i], HIGH);
    else digitalWrite(ball_pins[i], LOW);
  }
}

// Attempt Below to filter out bad ADC readings.  No Luck.

// int a0_values[20];
// int a1_values[20];
// int iptr = 0;
// float a0, a1;
// void update_analog() {
//   iptr++;
//   if(iptr >= 20) iptr = 0;
//   a0_values[iptr] = analogRead(A0);
//   a1_values[iptr] = analogRead(A1);
// }

// void cal_analog() {
//   a0 = 0.0;
//   a1 = 0.0;
//   for(int i = 0; i < 20; i++) {
//     a0 += a0_values[i];
//     a1 += a1_values[i];
//   }
//   a0 = a0 / 20.0;
//   a1 = a1 / 20.0;
// }

void manage_servo() {
  // We only update the servo once every 25 msec...
  uint32_t tnow = millis();
  if (tnow - last_servo_update_time  < 25) return;
  last_servo_update_time = tnow;
  // int aval = 0;
  // cal_analog();
  // if (servo_action()) aval = a0;
  // else                aval = a1;
  // target_pwm = (double) map(aval, 0, 1023, PWM_MIN, PWM_MAX); 
  // Make double sure we are in bounds.
  if (servo_action()) target_pwm = PWM_OPEN;
  else                target_pwm = PWM_CLOSE;
  if (target_pwm > PWM_MAX) target_pwm = PWM_MAX;
  if (target_pwm < PWM_MIN) target_pwm = PWM_MIN;
  if (!servo_inited) {
    // Issues a full pwm command and wait long enougth for
    // it to be complete done.
    last_servo_cmd_pwm = (int16_t) target_pwm;
    servo.writeMicroseconds(last_servo_cmd_pwm);
    //char line[100];
    //sprintf(line, "Initializing Servo to pwm = %d usec", last_servo_cmd_pwm);
    //Serial.println(line);
    delay(2000);
    //Serial.println("Normal operation starts...");
    last_servo_cmd_time = micros();
    current_pwm = target_pwm;
    servo_inited = true;
    return;
  }
  // Figure out where we think we are.
  tnow = micros();
  uint32_t telp = tnow - last_servo_cmd_time;
  double max_movment = MAX_USEC * (double) telp / (double) 1000000.0;
  double delta_pwm = last_servo_cmd_pwm - current_pwm;
  if (delta_pwm < 0) {
    double x = -delta_pwm;
    if (x > max_movment) delta_pwm = -max_movment;
  } else {
    if(delta_pwm > max_movment) delta_pwm = max_movment;
  }
  current_pwm += delta_pwm;
  double e = (target_pwm - current_pwm);
  if (e < 0.0) e = -e;
  if (e <= 1.0) return;   // We are within range, nothing to do.
  // Issue new command to go where we want.
  delta_pwm = target_pwm - current_pwm;
  max_movment = (double) MAX_USEC * 25.0 / 1000.0;
  if (delta_pwm > 0) {
    if(delta_pwm > max_movment) delta_pwm = max_movment;
  } else {
    double x = - delta_pwm;
    if(x > max_movment) delta_pwm = -max_movment;
  }
  last_servo_cmd_pwm = (int16_t) (current_pwm + delta_pwm);
  last_servo_cmd_time = micros();
  servo.writeMicroseconds(last_servo_cmd_pwm);
}

// void report() {
//   char line[100];
//   char sval[25];
//   uint32_t tnow = millis();
//   if (tnow - last_report_time < 1000) return;
//   last_report_time = tnow;

//   int r0 = analogRead(detector_pins[0]);
//   int r1 = analogRead(detector_pins[1]);
//   int r2 = analogRead(detector_pins[2]);
//   int r3 = analogRead(detector_pins[3]);

//   sprintf(line, "Analog Reads: %3d %3d %3d %3d", r0, r1, r2, r3);
//   Serial.println(line);

//   // // Serial.println("");
//   // // sprintf(line, "Servo A0, A1 readings: %d, %d", ia0, ia1);
//   // // Serial.println(line);
  
//   // dtostrf(target_pwm, 8, 3, sval);
//   // sprintf(line, "target_pwm = %s", sval);
//   // Serial.println(line);

//   // dtostrf(current_pwm, 8, 3, sval);
//   // sprintf(line, "current_pwm = %s", sval);
//   // Serial.println(line);

//   // sprintf(line, "last_servo_cmd_pwm = %d", last_servo_cmd_pwm);
//   // Serial.println(line);
// }

void loop() {
  // update_analog();
  send_sensors();
  manage_servo();
  // report();
}