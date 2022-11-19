// Pinball Machine Project, EPIC Robotz, Fall 2022
//
// This module is for the Light Control Unit in the
// score box.  The hardware is set up to control 6 
// 12v lamps, and one neostrip, 104 LEDs long. 
//
// This module communicates with the Main Pinball Brain
// (MPB) over I2C.

#include <Adafruit_NeoPixel.h>
#include <comm_bus.h>

#define PIN_LAMP_1 3
#define PIN_LAMP_2 5
#define PIN_LAMP_3 6
#define PIN_LAMP_4 9
#define PIN_LAMP_5 10
#define PIN_LAMP_6 11
#define PIN_NEO 12
#define NLAMPS 6
#define LED_COUNT 104

char lamps[] = {PIN_LAMP_1, PIN_LAMP_2, PIN_LAMP_3, PIN_LAMP_4, PIN_LAMP_5, PIN_LAMP_6};
uint32_t color_red;
uint32_t color_blue;
uint32_t color_green;
uint32_t color_white;
uint32_t color_black;

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, PIN_NEO, NEO_GRB + NEO_KHZ800);
CommBus bus(4);

void neo_setup() {
  strip.begin();  
  strip.clear();          
  strip.show();       // Causes           
  strip.setBrightness(255); 
  color_red = strip.Color(255, 0, 0);
  color_blue = strip.Color(0, 255, 0);
  color_green = strip.Color(0, 0, 255);
  color_white = strip.Color(255, 255, 255);
  color_black = strip.Color(0, 0, 0);
}

void colorWipe(uint32_t color, int wait) {
  for(int i=0; i < LED_COUNT; i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}

void colorSet(uint32_t color) {
  for(int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

void clear_neo() {
  strip.clear();
  strip.show();
}

void lamp_setup() {
    for(int i = 0; i < NLAMPS; i++) {
      pinMode(lamps[i], OUTPUT);
      digitalWrite(lamps[i], 0);
    }
}

bool lamp_on(int lamp, float brightness) {
  int pin = lamps[lamp];
  int ib = brightness * 255;
  if (ib < 0) ib = 0;
  if (ib > 255) ib = 255;
  analogWrite(pin, ib);
}

bool lamp_off(int lamp) {
  int pin = lamps[lamp];
  digitalWrite(pin, 0);
}

void flash(int lamp) {
  lamp_on(lamp, 1.0);
  delay(50);
  lamp_off(lamp);
}

void all_on(float brightness) {
  for(int i = 0; i < NLAMPS; i++) lamp_on(i, brightness);
}

void all_off() {
  for(int i = 0; i < NLAMPS; i++) lamp_off(i);
}

void all_flash() {
  all_off();
  all_on(1.0);
  delay(50);
  all_off();
}

void ramp_up(int lamp) {
  int i;
  for(i = 0; i < 100; i++) {
    float b = i / 100.0;
    lamp_on(lamp, b);
    delay(40);
  }
  lamp_off(lamp);
}

void setup() {
  lamp_setup();
  neo_setup();
}


void loop() {
  colorWipe(color_green, 5);
  for(int i = 0; i < NLAMPS; i++) {
    flash(i);
    delay(200);
  }
  delay(200);
  colorWipe(color_red, 5);
  all_on(0.08);
  colorWipe(color_blue, 10);
  delay(5000);
  all_off();
  clear_neo();
  delay(700);
  all_flash();
  colorWipe(color_white, 0);
  delay(1000);
  clear_neo();
  all_off();
  delay(1000);
  colorSet(color_white);
  delay(500);
  clear_neo();
  delay(500);
}
