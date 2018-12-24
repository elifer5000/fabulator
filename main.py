#!/usr/bin/env python

import sys

import math
import time
import random
import rtmidi
import serial
import serial.tools.list_ports

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROLLER_CHANGE


def freq_calc(_note):
	return math.pow(2.0, (_note - 69) / 12.0) * 440.0


ports = list(serial.tools.list_ports.comports())
for p in ports:
	if p.manufacturer is not None and "Arduino" in p.manufacturer:
		serialPort = p.device

ser = serial.Serial(serialPort, 115200)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
midiport = sys.argv[1] if len(sys.argv) > 1 else None

try:
	midiin, port_name = open_midiinput(midiport)
except (EOFError, KeyboardInterrupt):
	sys.exit()

print("Entering main loop. Press Control-C to exit.")

active_notes = {}
try:
	timer = time.time()
	while True:
		random.random()

		msg = midiin.get_message()

		note = int(440 + random.random() * 440)
		lobyte = note & 0xff
		hibyte = (note & 0xff00) >> 8
		vol = 5

		for x in range(1, 6):
			id = x
			idAndVol = (id << 4) | vol
			values = bytearray([idAndVol, lobyte, hibyte])
			ser.write(values)

		if msg:
			message, deltatime = msg
			timer += deltatime
			print("[%s] @%0.6f %r" % (port_name, timer, message))
			note = message[1]
			if message[0] & 0xF0 == NOTE_ON:
				active_notes[note] = note
				note = int(freq_calc(note))
			elif message[0] & 0xF0 == NOTE_OFF:
				if active_notes.has_key(note):
					active_notes.pop(note)
				note = 0

			lobyte = note & 0xff
			hibyte = (note & 0xff00) >> 8
			vol = 5

			#id, vol, note
			for x in range(1,6):
				id = x
				idAndVol = (id << 4) | vol
				values = bytearray([idAndVol, lobyte, hibyte])
				ser.write(values)

			print ser.readline()


except KeyboardInterrupt:
	print('')
finally:
	print("Exit.")
	# Close midi
	midiin.close_port()
	del midiin

	print("Done")

