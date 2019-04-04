import pyaudio
import struct
import math
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import time
from scipy.io.wavfile import write
import scipy.io.wavfile as wavfile
from StepperManager import StepperManager
import serial.tools.list_ports
from Stepper import current_milli_time

ports = list(serial.tools.list_ports.comports())
for p in ports:
	if p.manufacturer is not None and "Arduino" in p.manufacturer:
		serialPort = p.device
		print "Connecting to " + p.device

ser = serial.Serial(serialPort, 115200)
time.sleep(1) # Try allowing some time before starting to send messages
print "Connected"

stepperManagers = [StepperManager(ser, 0, 1)]

# THRESHOLD = 0 # dB
# RATE = 44100
# INPUT_BLOCK_TIME = 1 # 30 ms
# INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)
# INPUT_FRAMES_PER_BLOCK_BUFFER = int(RATE * INPUT_BLOCK_TIME)
#
# def get_rms(block):
#     return np.sqrt(np.mean(np.square(block)))
#
# class AudioHandler(object):
#     def __init__(self):
#         self.pa = pyaudio.PyAudio()
#         self.stream = self.open_mic_stream()
#         self.threshold = THRESHOLD
#         self.plot_counter = 0
#
#     def stop(self):
#         self.stream.close()
#
#     def find_input_device(self):
#         device_index = None
#         for i in range( self.pa.get_device_count() ):
#             devinfo = self.pa.get_device_info_by_index(i)
#             print('Device %{}: %{}'.format(i, devinfo['name']))
#
#             for keyword in ['mic','input']:
#                 if keyword in devinfo['name'].lower():
#                     print('Found an input: device {} - {}'.format(i, devinfo['name']))
#                     device_index = i
#                     return device_index
#
#         if device_index == None:
#             print('No preferred input found; using default input device.')
#
#         return device_index
#
#     def open_mic_stream( self ):
#         device_index = self.find_input_device()
#
#         stream = self.pa.open(  format = self.pa.get_format_from_width(2,False),
#                                 channels = 1,
#                                 rate = RATE,
#                                 input = True,
#                                 input_device_index = device_index)
#
#         stream.start_stream()
#         return stream
#
#     def processBlock(self, snd_block):
#         f, t, Sxx = signal.spectrogram(snd_block, RATE)
#         zmin = Sxx.min()
#         zmax = Sxx.max()
#
#         while zmax > 8000:
#             zmax /= 2
#
#         stepperManagers[0].setNoteOn(zmax, 5)
#         for manager in stepperManagers:
#             manager.run()
#         # plt.pcolormesh(t, f, Sxx, cmap='RdBu', norm=LogNorm(vmin=zmin, vmax=zmax))
#         # plt.ylabel('Frequency [Hz]')
#         # plt.xlabel('Time [sec]')
#         # plt.axis([t.min(), t.max(), f.min(), f.max()])
#         # plt.colorbar()
#         # plt.savefig('data/spec{}.png'.format(self.plot_counter), bbox_inches='tight')
#         # plt.close()
#         # write('data/audio{}.wav'.format(self.plot_counter),RATE,snd_block)
#         self.plot_counter += 1
#
#     def listen(self):
#         try:
#             print "start", self.stream.is_active(), self.stream.is_stopped()
#             #raw_block = self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
#
#             total = 0
#             t_snd_block = []
#             while total < INPUT_FRAMES_PER_BLOCK:
#                 while self.stream.get_read_available() <= 0:
#                   print 'waiting'
#                   time.sleep(0.01)
#                 while self.stream.get_read_available() > 0 and total < INPUT_FRAMES_PER_BLOCK:
#                     raw_block = self.stream.read(self.stream.get_read_available(), exception_on_overflow = False)
#                     count = len(raw_block) / 2
#                     total = total + count
#                     print "done", total,count
#                     format = '%dh' % (count)
#                     t_snd_block.append(np.fromstring(raw_block,dtype=np.int16))
#             snd_block = np.hstack(t_snd_block)
#         except Exception as e:
#             print('Error recording: {}'.format(e))
#             return
#
#         self.processBlock(snd_block)
#
# if __name__ == '__main__':
#     audio = AudioHandler()
#     for i in range(0,50):
#         audio.listen()

# import pyaudio
# import struct
# import math
# import numpy as np
# from scipy import signal
# import matplotlib.pyplot as plt
#
#
# THRESHOLD = 40 # dB
# RATE = 44100
# INPUT_BLOCK_TIME = 1.0 # 30 ms
# INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)
#
# def get_rms(block):
#     return np.sqrt(np.mean(np.square(block)))
#
# class AudioHandler(object):
#     def __init__(self):
#         self.pa = pyaudio.PyAudio()
#         self.stream = self.open_mic_stream()
#         self.threshold = THRESHOLD
#         self.plot_counter = 0
#
#     def stop(self):
#         self.stream.close()
#
#     def find_input_device(self):
#         device_index = None
#         for i in range( self.pa.get_device_count() ):
#             devinfo = self.pa.get_device_info_by_index(i)
#             print('Device %{}: %{}'.format(i, devinfo['name']))
#
#             for keyword in ['mic','input']:
#                 if keyword in devinfo['name'].lower():
#                     print('Found an input: device {} - {}'.format(i, devinfo['name']))
#                     device_index = i
#                     return device_index
#
#         if device_index == None:
#             print('No preferred input found; using default input device.')
#
#         return device_index
#
#     def open_mic_stream( self ):
#         device_index = self.find_input_device()
#
#         stream = self.pa.open(  format = pyaudio.paInt16,
#                                 channels = 1,
#                                 rate = RATE,
#                                 input = True,
#                                 input_device_index = device_index,
#                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)
#
#         return stream
#
#     def processBlock(self, snd_block):
#         f, t, Sxx = signal.spectrogram(snd_block, RATE)
#         zmax = Sxx.max()
#         maxx = f[np.argmax(Sxx, axis=0)]
#         print(maxx)
#         # if maxx < 8000:
#         #     stepperManagers[0].setNoteOn(maxx, 5)
#         # else:
#         #     stepperManagers[0].setNoteOn(0, 0)
#         #
#         # for manager in stepperManagers:
#         #     manager.run()
#
#         # plt.pcolormesh(t, f, Sxx)
#         # plt.ylabel('Frequency [Hz]')
#         # plt.xlabel('Time [sec]')
#         # plt.savefig('data/spec{}.png'.format(self.plot_counter), bbox_inches='tight')
#         # self.plot_counter += 1
#
#     def listen(self):
#         try:
#             raw_block = self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
#             count = len(raw_block) / 2
#             format = '%dh' % (count)
#             snd_block = np.array(struct.unpack(format, raw_block))
#         except Exception as e:
#             print('Error recording: {}'.format(e))
#             return
#
#         amplitude = get_rms(snd_block)
#         if amplitude > self.threshold:
#             self.processBlock(snd_block)
#         else:
#             pass
#
# if __name__ == '__main__':
#     audio = AudioHandler()
#     for i in range(0,10000):
#         audio.listen()

f = 440  # Frequency, in cycles per second, or Hertz
fs = 1000  # Sampling rate, or number of measurements per second

t = np.linspace(0, 2000, 2000 * fs, endpoint=False)
data = np.sin(f * 2 * np.pi * t) # * np.cos(0.6*f * 2 * np.pi * t)

fs, data = wavfile.read("hello2.wav")

# 	data = data[:, 0]

frequencies, times, spectrogram = signal.spectrogram(data, fs) #, nperseg=256, noverlap=128, nfft=512, window=('hamming'))

maxx = frequencies[np.argmax(spectrogram, axis=0)]
print(maxx)
prev = 0
for idx, val in enumerate(times):
	print(val, maxx[idx])
	stepperManagers[0].setNoteOn(maxx[idx], 5)
	for manager in stepperManagers:
		manager.run()

	before = current_milli_time()

	stepperManagers[0].run()
	realDelta = val - prev
	delta = current_milli_time() - before
	if delta < realDelta:
		print(delta)
		time.sleep((realDelta - delta)) # sleep to complete a frame

	prev = val
#11,025

stepperManagers[0].setNoteOn(0, 0)
for manager in stepperManagers:
	manager.run()
# print(x)

