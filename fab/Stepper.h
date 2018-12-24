#include "AccelStepper.h"

class Stepper {
protected:
    AccelStepper stepper;
    uint8_t ms1;
    uint8_t ms2;
    uint8_t ms3;
    bool isActive;
    bool useAcceleration;
    int speed;
    int acceleration;
    int volume;

    void setupStepper() {
      if (useAcceleration) {
        stepper.setMaxSpeed(0);
        stepper.setAcceleration(acceleration);
        stepper.moveTo(1000000);
      } else {
        stepper.setSpeed(0.0);
        stepper.setMaxSpeed(10000);        
      }
    }

    void setSpeed() {
      if (useAcceleration) {
        stepper.setMaxSpeed(speed);
      } else {
        stepper.setSpeed(speed);
      }
    }

    void setVolume(int val) {
      switch (val) {
      case 5: // 1
        digitalWrite(ms1, LOW);
        digitalWrite(ms2, LOW);
        digitalWrite(ms3, LOW);
        break;
      case 4: // 1/2
        digitalWrite(ms1, HIGH);
        digitalWrite(ms2, LOW);
        digitalWrite(ms3, LOW);
        break;
      case 3: // 1/4
        digitalWrite(ms1, LOW);
        digitalWrite(ms2, HIGH);
        digitalWrite(ms3, LOW);
        break;
      case 2: // 1/8
        digitalWrite(ms1, HIGH);
        digitalWrite(ms2, HIGH);
        digitalWrite(ms3, LOW);
        break;
      case 1: // 1/16
        digitalWrite(ms1, HIGH);
        digitalWrite(ms2, HIGH);
        digitalWrite(ms3, HIGH);
        break;
    }
  }

public:
  Stepper(uint8_t stepPin, uint8_t dirPin, uint8_t enablePin, uint8_t _ms1 = -1, uint8_t _ms2 = -1, uint8_t _ms3 = -1) :
      stepper(AccelStepper::DRIVER, stepPin, dirPin),
      ms1(_ms1), ms2(_ms2), ms3(_ms3),  
      isActive(false),
      useAcceleration(false),
      speed(0),
      acceleration(10000),
      volume(0)
  {
    stepper.setPinsInverted(false, false, true);
    stepper.setEnablePin(enablePin);

    pinMode(ms1, OUTPUT);
    pinMode(ms2, OUTPUT);
    pinMode(ms3, OUTPUT);  
  }
  
  void setup() {
    setupStepper();
  }

  void run() {
    if (!isActive) return;

    if (useAcceleration) {
      if (stepper.distanceToGo() == 0)
          stepper.moveTo(-stepper.currentPosition());
        stepper.run();
    } else {
      stepper.runSpeed();
    }
  }

  // note is in Hz
  void setNote(int _note, int _volume) {
    speed = _note;
    isActive = speed > 0;
    setSpeed();

    if (volume != _volume) {
        volume = _volume;
        setVolume(volume);
    }
  }

  bool getIsActive() {
    return isActive;
  }

  int getNote() {
    return speed;
  }

  int getVolume() {
    return volume;
  }
};
