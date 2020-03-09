# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 17:44:41 2020

@author: masavoyat
"""

import wave
import struct
import numpy as np
import FIRdecimator
import numpy as np
from scipy import signal

n = 80
channel = 1
samp_rate = 250e3
center_freq = 446.1e6
channel_freq = 446e6 + 6.25e3 + 12.5e3*(channel-1)
lo_freq = channel_freq - center_freq
lo = np.exp(-2*np.pi*1j*lo_freq/samp_rate*np.arange(n))
buffer = list() # local buffer used for group data processing

numtaps, beta = signal.kaiserord(40, 1/250)
taps = signal.firwin(numtaps, 1/250,
                     window=('kaiser', beta),
                     scale=False,
                     nyq=0.5*samp_rate)
filt = FIRdecimator.FIRdecimator(taps, 16)

waveFile = wave.open('radio_test.wav', 'r')

length = waveFile.getnframes()
for i in range(length//1024):
    waveData = waveFile.readframes(1024)
    data = np.array(struct.unpack("<2048h", waveData))*1.0
    data /= 2**15
    c_data = data[0::2] + 1j*data[1::2]
    buffer.extend(c_data)
    # Process data by n samples
    while len(buffer) > n:
        data_mix = buffer[:n]*lo
        data_filt_decim = filt.filt(data_mix)
        del buffer[:n]


waveFile.close()