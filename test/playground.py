# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 17:44:41 2020

@author: masavoyat
"""
import sys
if ".." not in sys.path:
    sys.path.append("..")
import wave
import struct
import numpy as np
import FIRdecimator
import FMdemodulator
import Squelch
from scipy import signal
from matplotlib import pyplot as plt
import sounddevice as sd

channel = 8
samp_rate = 250e3
center_freq = 446.1e6
channel_freq = 446e6 + 6.25e3 + 12.5e3*(channel-1)
lo_freq = channel_freq - center_freq
buffer = list() # local buffer used for group data processing

squelch = Squelch.Squelch(-10)
numtaps, beta = signal.kaiserord(40, 1/(250*0.5))
print(numtaps)
taps = signal.firwin(numtaps, (6.25-1)*1e3,
                     window=('kaiser', beta),
                     scale=True,
                     fs=samp_rate)
filt_demod = FIRdecimator.FIRdecimator(taps, 4)
demod = FMdemodulator.FMdemodulator(samp_rate/4, 5e3)
numtaps_audio, beta_audio = signal.kaiserord(40, 0.01/(62.5*0.5))
print(numtaps_audio)
taps_audio = signal.firwin(numtaps_audio, [10, (3.125-0.5)*1e3],
                     window=('kaiser', beta_audio),
                     scale=True, pass_zero=False,
                     fs=samp_rate/4)
filt_audio = FIRdecimator.FIRdecimator(taps_audio, 4)
n = (1+(max(numtaps, numtaps_audio)//80))*80
lo = np.exp(-2*np.pi*1j*lo_freq/samp_rate*np.arange(n))

waveFile = wave.open('radio_test.wav', 'r')

length = waveFile.getnframes()
#length //= 2
data_out = list()
for i in range(length//1024):
    waveData = waveFile.readframes(1024)
    data = np.array(struct.unpack("<2048h", waveData))*1.0
    data /= 2**15
    c_data = data[0::2] + 1j*data[1::2]
    buffer.extend(c_data)
    # Process data by n samples
    while len(buffer) > n:
        data_mix = buffer[:n]*lo
        data_filt = filt_demod.process(data_mix)
        data_squelch = squelch.process(data_filt)
        data_demod = demod.process(data_squelch)
        data_audio = filt_audio.process(data_demod)
        data_out.extend(data_audio)
        del buffer[:n]

waveFile.close()
plt.figure()
plt.plot(data_out)
#plt.plot(np.real(data_out))
#plt.plot(np.imag(data_out))
sd.play(np.array(data_out)*3, samp_rate/16)
