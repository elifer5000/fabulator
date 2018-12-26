import math
from Stepper import Stepper
from Stepper import current_milli_time

NOTES_BUFFER_SZ = 32

PULSE_PERIOD_KNOB  =  21
PITCH_SHIFT_KNOB   =  22
OCTAVER_KNOB       =  23
VOLUME_SWELL_KNOB  =  24
VIBRATO_PERIOD_KNOB = 25
VIBRATO_RANGE_KNOB  = 26


def convertVolume(volume):
	if volume > 80:
		return 5
	if volume > 40:
		return 4
	if volume > 20:
		return 3
	if volume > 10:
		return 2

	return 1


def detuneCalcApprox(maxDetune, val):
	cents = maxDetune*((val / 127.0) * 2.0 - 1.0)

	if cents > 0:
		return 1 + 0.059463094*cents

	return 1 + 0.056125687*cents


# Returns between -12 and 12
def detuneCalc(maxDetune, val):
	cents = maxDetune*((val / 127.0) * 2.0 - 1.0)

	return math.pow(2.0, cents/12.0)


class StepperManager:
	def __init__(self, serial, first_id, num_steppers, is_mono=False):
		self.serial = serial
		self.numNotes = 0
		self.numOldNotes = 0
		self.oldNotesStack = [None] * NOTES_BUFFER_SZ
		self.oldVolumesStack = [None] * NOTES_BUFFER_SZ
		self.isMono = is_mono
		self.numSteppers = num_steppers

		self.steppers = []
		for i in range(first_id, first_id + self.numSteppers):
			self.steppers.append(Stepper(i, serial))

	def run(self):
		currentMillis = current_milli_time()
		for i in range(0, self.numSteppers):
			self.steppers[i].run(currentMillis)

	def setPolyNoteOn(self, note, volume):
		if self.numNotes < self.numSteppers:
			# Search for next available motor
			for i in range(0, self.numSteppers):
				if not self.steppers[i].isActive:
					self.steppers[i].setNote(note, volume)
					self.numNotes += 1
					break
		else: # Search for active motor with closest distance
			closestDist = 1000000
			idx = -1
			for i in range(0, self.numSteppers):
				dist = note - self.steppers[i].getNote()
				dist = math.fabs(dist)
				if dist < closestDist:
					closestDist = dist
					idx = i

			if self.numOldNotes < NOTES_BUFFER_SZ:
				self.oldNotesStack[self.numOldNotes] = self.steppers[idx].getNote()
				self.oldVolumesStack[self.numOldNotes] = self.steppers[idx].getVolume()
				self.numOldNotes += 1

			self.steppers[idx].setNote(note, volume)

	def setPolyNoteOff(self, note):
		# int i, j, oldNote, oldVolume;
		# Search for motor with this note
		i = 0
		for i in range(0, self.numSteppers):
			if note == self.steppers[i].getNote():
				if self.numOldNotes > 0:  # Play old note from stack
					self.numOldNotes -= 1
					oldNote = self.oldNotesStack[self.numOldNotes]
					oldVolume = self.oldVolumesStack[self.numOldNotes]
					self.steppers[i].setNote(oldNote, oldVolume)
				else: # Turn off motor
					self.steppers[i].setNote(0, 0)
					self.numNotes -= 1

				break

		if i == self.numSteppers - 1: # No active motor with this note
			for i in range(0, self.numOldNotes):
				if self.oldNotesStack[i] == note:	# Remove from stack
					self.numOldNotes -= 1
					for j in range(i, self.numOldNotes):
						self.oldNotesStack[j] = self.oldNotesStack[j + 1]
						self.oldVolumesStack[j] = self.oldVolumesStack[j + 1]

					break

	def	setMonoNoteOn(self, note, volume):
		if self.steppers[0].isActive and self.numOldNotes < NOTES_BUFFER_SZ:
			self.oldNotesStack[self.numOldNotes] = self.steppers[0].getNote()
			self.oldVolumesStack[self.numOldNotes] = self.steppers[0].getVolume()
			self.numOldNotes += 1

		for i in range(0, self.numSteppers):
			self.steppers[i].setNote(note, volume)

	def setMonoNoteOff(self, note):
		if note == self.steppers[0].getNote():  # Is this note currently playing?
			if self.numOldNotes > 0:  # Play old note from stack
				self.numOldNotes -= 1
				oldNote = self.oldNotesStack[self.numOldNotes]
				oldVolume = self.oldVolumesStack[self.numOldNotes]

				for i in range(0, self.numSteppers):
					self.steppers[i].setNote(oldNote, oldVolume)
			else: # Turn off motors
				for i in range(0, self.numSteppers):
					self.steppers[i].setNote(0, 0)
		else:
			for i in range(0, self.numOldNotes):
				if self.oldNotesStack[i] == note:	# Remove from stack
					self.numOldNotes -= 1
					for j in range(i, self.numOldNotes):
						self.oldNotesStack[j] = self.oldNotesStack[j + 1]
						self.oldVolumesStack[j] = self.oldVolumesStack[j + 1]

					break

	def setAllNotesOff(self):
		for i in range(0, self.numSteppers):
			self.steppers[i].setNote(0, 0)

		self.numOldNotes = 0

	def setNoteOn(self, note, volume):
		if self.isMono:
			self.setMonoNoteOn(note, convertVolume(volume))
		else:
			self.setPolyNoteOn(note, convertVolume(volume))

	def setNoteOff(self,note):
		if self.isMono:
			self.setMonoNoteOff(note)
		else:
			self.setPolyNoteOff(note)

	def	handleControlChange(self, number, value):
		if number == PULSE_PERIOD_KNOB:
			k = 50000.0 if value > 60 else 25000.0 # Higher	granularity in lower range.Up to 500 ms
			f = ((k * value) / 127) / 100.0
			for i in range(0, self.numSteppers):
				self.steppers[i].setPeriod("pulse", f)
		elif number == PITCH_SHIFT_KNOB:
			if self.isMono:
				f = detuneCalcApprox(0.333, value) # Detune up to 1 / 3 semitone
				for i in range(1, self.numSteppers):
					self.steppers[i].setDetune((float(i) / (self.numSteppers-1)) * f)
			else:
				f = detuneCalcApprox(1.0, value) # Detune up to 1 semitone
				for i in range(0, self.numSteppers):
					self.steppers[i].setDetune(f)
		elif number == OCTAVER_KNOB:
			f = detuneCalc(12.0, value) # Detune up to 1 octave
			for i in range(0, self.numSteppers):
				self.steppers[i].setPitchShift(f)
		elif number == VOLUME_SWELL_KNOB:
			k = 50000.0 if value > 60 else 25000.0  # Higher granularity in lower range.Up to 500 ms
			f = ((k * value) / 127) / 100.0
			for i in range(0, self.numSteppers):
				self.steppers[i].setPeriod("swell", f)
		elif number == VIBRATO_PERIOD_KNOB:
			k = 50000.0 if value > 60 else 25000.0  # Higher granularity in lower range.Up to 500 ms
			f = ((k * value) / 127) / 100.0
			for i in range(0, self.numSteppers):
				self.steppers[i].setPeriod("vibrato", f)
		elif number == VIBRATO_RANGE_KNOB:
			for i in range(0, self.numSteppers):
				self.steppers[i].setRange("vibrato", value / 127.0)
		elif number == 120 or number == 123: # All sound off case. All notes off
			self.setAllNotesOff()
