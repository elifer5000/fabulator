class PeriodicEffect:
    def __init__(self):
        self.period = 0
        self.range = 0
        self.toggle = True
        self.prevToggle = True
        self.startMillis = 0
        self.currentMillis = 0

    def setup(self, start_millis):
        self.startMillis = start_millis
        self.prevToggle = self.toggle = True

    def setPeriod(self, period):
        if period == 0:
            self.prevToggle = self.toggle = True # If it was off, start from an 'on' state

        self.period = period

    def setRange(self, range):
        self.range = range

    def isActive(self):
        return self.period > 0

    def run(self, current_millis):
        self.prevToggle = self.toggle
        self.currentMillis = current_millis
        if self.currentMillis - self.startMillis >= self.period:
            self.startMillis = self.currentMillis
            self.toggle = not self.toggle

    def getVolume(self):
        return 1

    def getSpeedFactor(self):
        return 1.0


class PulseEffect(PeriodicEffect):
    def getVolume(self):
        return 1 if self.toggle else 0


class VolumeSwellEffect(PeriodicEffect):
    def __init__(self):
        super.__init__()
        self.volume = 1

    def getVolume(self):
        if self.prevToggle != self.toggle:
            self.volume += 1

        return self.volume % 6


class VibratoEffect(PeriodicEffect):
    def __init__(self):
        super.__init__()
        self.sign = 2

    def getSpeedFactor(self):
        if self.prevToggle != self.toggle:
            self.sign = -self.sign

    # if cents > 0: # range is between 0 and 1
    #     return 1 + 0.059463094 * cents
    #
    # return 1 + 0.056125687 * cents

    # factor = 10 # Range seems to be too small, maybe need a factor
        y = self.range * self.sign * (-0.5 + (self.currentMillis - self.startMillis) / self.period)

        return (1 + 0.059463094 * y) if y > 0 else (1 + 0.056125687 * y)


class RandomEffect(PeriodicEffect):
    def __init__(self):
        super.__init__()


class EffectManager:
    def __init__(self):
        self.effects = {
            "pulse": PulseEffect(),
            "swell": VolumeSwellEffect(),
            "vibrato": VibratoEffect(),
            "random": RandomEffect()
        }

    def setup(self, initial_milllis):
        for effect in self.effects.values():
            effect.setup(initial_milllis)

    def run(self, current_millis, volume):
        for effect in self.effects.values():
            effect.run(current_millis)

        if self.effects["pulse"].isActive():
            volume *= self.effects["pulse"].getVolume()

        if volume > 0 and self.effects["swell"].isActive():
            volume = self.effects["swell"].getVolume()

        speed_factor = 1.0
        if self.effects["vibrato"].isActive():
            speed_factor = self.effects["vibrato"].getSpeedFactor()

        return volume, speed_factor

    def setPeriod(self, effect_type, period):
        self.effects[effect_type].setPeriod(period)

    def setRange(self, effect_type, range):
        self.effects[effect_type].setRange(range)
