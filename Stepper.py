import time
import math
from EffectsManager import EffectsManager


def current_milli_time():
    return int(round(time.time() * 1000))

def freq_calc(_note):
    return math.pow(2.0, (_note - 69) / 12.0) * 440.0

class Stepper:
    def __init__(self, _id, serial):
        self.id = _id
        self.serial = serial
        self.isActive = False
        self.speed = 0
        self.speedFactor1 = 1.0
        self.speedFactor2 = 1.0
        self.totalSpeed = 0

        self.volume = 5

        self.effects_manager = EffectsManager()
        self.currentValues = None

    def setup(self, initial_millis):
        self.effects_manager.setup(initial_millis)

    def run(self, current_millis):
        if self.isActive:
            (volumeTmp, effectsSpeedFactor) = self.effects_manager.run(current_millis, self.volume)
        else:
            (volumeTmp, effectsSpeedFactor) = (-1, 1)

        # if volumeTmp == 0:
        #     return

        # pitch = self.speed * self.speedFactor1 * self.speedFactor2 * effectsSpeedFactor

        # if volumeTmp != -1 and volumeTmp != self.volume:
        #     self.volume = volumeTmp
            # self.setVolume()

        self.sendToSerial()

    # note is in Hz
    def setNote(self, note, volume):
        self.note = note
        self.speed = 0 if note == 0 else int(freq_calc(note))
        self.volume = volume
        self.isActive = self.speed > 0
        self.effects_manager.setup(current_milli_time())
        # updatePitch();

    def getNote(self):
        return self.note

    def getVolume(self):
        return self.volume

    def sendToSerial(self):
        idAndVol = (self.id << 4) | self.volume
        lobyte = self.speed & 0xff
        hibyte = (self.speed & 0xff00) >> 8
        values = bytearray([idAndVol, lobyte, hibyte])
        if self.currentValues is None or self.currentValues != values:
            self.serial.write(values)
            print self.serial.readline()
            self.currentValues = values


    def setDetune(self, detune):
        self.speedFactor1 = detune
        #updatePitch();

    def setPitchShift(self, detune):
        self.speedFactor2 = detune
        #updatePitch();

    def setPeriod(self, effectType, period):
        self.effects_manager.setPeriod(effectType, period)

    def setRange(self, effectType, range):
        self.effects_manager.setRange(effectType, range)