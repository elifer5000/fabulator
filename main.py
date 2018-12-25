#!/usr/bin/env python

import sys

import math
import time
import random
import rtmidi
import serial
import serial.tools.list_ports
from StepperManager import StepperManager
from Stepper import current_milli_time

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROLLER_CHANGE

ports = list(serial.tools.list_ports.comports())
for p in ports:
	if p.manufacturer is not None and "Arduino" in p.manufacturer:
		serialPort = p.device
		print "Connecting to " + p.device

ser = serial.Serial(serialPort, 115200)
time.sleep(1) # Try allowing some time before starting to send messages
print "Connected"

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
midiport = sys.argv[1] if len(sys.argv) > 1 else None

try:
	midiin, port_name = open_midiinput(midiport)
except (EOFError, KeyboardInterrupt):
	sys.exit()

print("Entering main loop. Press Control-C to exit.")

# stepperManagers = [StepperManager(ser, 0, 5)]
# stepperManagers = [StepperManager(ser, 0, 5, True)]  # mono

stepperManagers = [StepperManager(ser, 0, 1), StepperManager(ser, 1, 1), StepperManager(ser, 2, 3)]

numManagers = len(stepperManagers)

try:
	timer = time.time()
	while True:
		msg = midiin.get_message()

		# random notes
		# time.sleep(0.005)
		# note = int(440 + random.random() * 440)
		# lobyte = note & 0xff
		# hibyte = (note & 0xff00) >> 8
		# vol = 5
		#
		# for x in range(1, 6):
		# 	idAndVol = (x << 4) | vol
		# 	values = bytearray([idAndVol, lobyte, hibyte])
		# 	ser.write(values)

		if msg:
			message, deltatime = msg
			timer += deltatime

			channel = message[0] & 0x0F if numManagers > 1 else 0
			print("[%s:%d] @%0.6f %r" % (port_name, channel, timer, message))

			if message[0] & 0xF0 == NOTE_ON:
				stepperManagers[channel].setNoteOn(message[1], message[2])
			elif message[0] & 0xF0 == NOTE_OFF:
				stepperManagers[channel].setNoteOff(message[1])
			elif message[0] & 0xF0 == CONTROLLER_CHANGE:
				stepperManagers[channel].handleControlChange(message[1], message[2])

			# lobyte = note & 0xff
			# hibyte = (note & 0xff00) >> 8
			# vol = 5
			#
			# #id, vol, note
			# for x in range(1, 6):
			# 	idAndVol = (x << 4) | vol
			# 	values = bytearray([idAndVol, lobyte, hibyte])
			# 	ser.write(values)
			# 	# print ser.readline()

		before = current_milli_time()
		for manager in stepperManagers:
			manager.run()
		delta = current_milli_time()

		if delta < 5:
			print(delta)
			# time.sleep((5 - delta) / 1000) # sleep to complete a 5 ms frame
		# time.sleep(0.05)

except KeyboardInterrupt:
	print('')
finally:
	print("Exit.")
	# Close midi
	midiin.close_port()
	del midiin

	ser.close()

	print("Done")

