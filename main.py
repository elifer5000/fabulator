#!/usr/bin/env python

import sys

import math
import time
import random
import rtmidi
import serial
import serial.tools.list_ports
from StepperManager import StepperManager

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROLLER_CHANGE

ports = list(serial.tools.list_ports.comports())
for p in ports:
	if p.manufacturer is not None and "Arduino" in p.manufacturer:
		serialPort = p.device
		print "Connecting to " + p.device

ser = serial.Serial(serialPort, 115200)
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

stepperManager = StepperManager(ser, 0, 5)

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
			print("[%s] @%0.6f %r" % (port_name, timer, message))
			note = message[1]
			if message[0] & 0xF0 == NOTE_ON:
				stepperManager.setNoteOn(note, message[2])
			elif message[0] & 0xF0 == NOTE_OFF:
				stepperManager.setNoteOff(note)

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

		stepperManager.run()
		time.sleep(0.05)






except KeyboardInterrupt:
	print('')
finally:
	print("Exit.")
	# Close midi
	midiin.close_port()
	del midiin

	ser.close()

	print("Done")

