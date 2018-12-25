#include "config.h"
#include "Stepper.h"

Stepper steppers[NUM_STEPPERS] = {
  Stepper(X_STEP_PIN, X_DIR_PIN, X_ENABLE_PIN, X_MS1_PIN, X_MS2_PIN, X_MS3_PIN),
  Stepper(Y_STEP_PIN, Y_DIR_PIN, Y_ENABLE_PIN, Y_MS1_PIN, Y_MS2_PIN, Y_MS3_PIN),
  Stepper(Z_STEP_PIN, Z_DIR_PIN, Z_ENABLE_PIN, Z_MS1_PIN, Z_MS2_PIN, Z_MS3_PIN),
  Stepper(E_STEP_PIN, E_DIR_PIN, E_ENABLE_PIN, E_MS1_PIN, E_MS2_PIN, E_MS3_PIN),
  Stepper(Q_STEP_PIN, Q_DIR_PIN, Q_ENABLE_PIN, Q_MS1_PIN, Q_MS2_PIN, Q_MS3_PIN)
};

// create a random integer from 0 - bound
unsigned int rng(int bound) {
  static unsigned int y = 0;
  y += micros(); // seeded with changing number
  y ^= y << 2; y ^= y >> 7; y ^= y << 7;
  return (y / 65535.0f) * bound;
}

byte i;

void setupSteppers() {
   for (i = 0; i < NUM_STEPPERS; i++) {
      steppers[i].setup();
    }
}

unsigned long start = 0, current = 0, total = 0;

void setup() {
    Serial.begin(500000);
    setupSteppers();
    start = millis();

//    for (i = 0; i < NUM_STEPPERS; i++) {
//        steppers[i].setNote(440, 5);
//      }
}

int f = 0, s = 1;
void loop() {
    current = millis();

//    if (current - start > 10) {
//      for (i = 0; i < NUM_STEPPERS; i++) {
//        if (f > 800) s = -1;
//        if (f < 0) s = 1;
//        f += s;
//        steppers[i].setNote(440 + f, 5);
//      }
//      start = current;
//    }
    handleSerial();

    for (i = 0; i < NUM_STEPPERS; i++) {
      steppers[i].run();
    }
}

void handleSerial() {
    if (Serial.available() >= 3) {
        char idAndVol = Serial.read();
        char speedlo = Serial.read();
        char speedhi = Serial.read();

        int id = (idAndVol >> 4) & 0xf; //top_nibble
        int vol = idAndVol & 0xf; //bottom_nibble
        int note = word(speedhi, speedlo);

//        Serial.print("Got: ");
//        Serial.print(id);
//        Serial.print(" ");
//        Serial.print(vol);
//        Serial.print(" ");
//        Serial.println(note);

        steppers[id].setNote(note, vol);
    }
}
