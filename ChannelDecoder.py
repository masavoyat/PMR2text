# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:46:37 2020

@author: masavoyat
"""

import queue
import threading
import RadioReceiver
import FIRdecimator
import FMdemodulator
import Squelch
import numpy as np
from scipy import signal

class ChannelDecoder:
    """ PMR446 channel decoder.
    Attach to the radio_receiver and assume center_frequency is 446.1MHz
    and sample_rate is 250KHz."""
    
    def __init__(self, radio_recevier : RadioReceiver, channel):
        if radio_recevier.center_freq != 446.1e6:
            raise ValueError("RadioRecevier shall have 446.1 MHz center frequency")
            return
        if radio_recevier.sample_rate != 250e3:
            raise ValueError("RadioRecevier shall have 250 KHz sample rate")
            return
        if channel < 1 or channel > 16:
            raise ValueError("Channel shall be in range 1 to 16")
            return
        self._thread = threading.Thread(target=self._main_loop)
        self._run = threading.Event()
        self._radio_recevier = radio_recevier
        self._channel = channel
        self._queue = queue.Queue(10)
        # Build the filter 1KHz transition band to 40dB attenuation
        numtaps, beta = signal.kaiserord(40, 1/250)
        taps = signal.firwin(numtaps, 1/250,
                             window=('kaiser', beta),
                             scale=False,
                             nyq=0.5*radio_recevier.sample_rate)
        self._filter = FIRdecimator.FIRdecimator(taps, 16)
        self._run.set()
        self._thread.start()
        
    def _main_loop(self):
        n = 80*16
        channel_freq = 446e6 + 6.25e3 + 12.5e3*(self._channel-1)
        lo_freq = channel_freq - self._radio_recevier.center_freq
        samp_rate = self._radio_recevier.sample_rate
        lo = np.exp(-2*np.pi*1j*lo_freq/samp_rate*np.arange(n))
        buffer = list() # local buffer used for group data processing
        self._radio_recevier.registerQueue(self._queue)
        squelch = Squelch.Squelch(-10)
        # Channel signal filtering (baseband) before demodulation (low pass)
        numtaps_demod, beta_demod = signal.kaiserord(40, 1/(250*0.5))
        taps_demod = signal.firwin(numtaps_demod, (6.25-1)*1e3,
                             window=('kaiser', beta_demod),
                             scale=True,
                             fs=samp_rate)
        filt_demod = FIRdecimator.FIRdecimator(taps_demod, 4)
        # Demodulation is at samp_rate/4
        demod = FMdemodulator.FMdemodulator(samp_rate/4, 5e3)
        # Filter for audio signal (band pass)
        numtaps_audio, beta_audio = signal.kaiserord(40, 0.01/(62.5*0.5))
        taps_audio = signal.firwin(numtaps_audio, [10, (3.125-0.5)*1e3],
                             window=('kaiser', beta_audio),
                             scale=True, pass_zero=False,
                             fs=samp_rate/4)
        filt_audio = FIRdecimator.FIRdecimator(taps_audio, 4)
        # Decimation by 4 at demodulation and 4 at audio filtering => 16 total
        while self._run.is_set():
            data = self._queue.get()
            if not data: # in case the radio return None
                self._run.clear()
                continue
            buffer.extend(data)
            # Process data by n samples
            while len(buffer)>n:
                data_mix = buffer[:n]*lo
                data_filt = filt_demod.process(data_mix)
                data_squelch = squelch.process(data_filt)
                data_demod = demod.process(data_squelch)
                data_audio = filt_audio.process(data_demod)
                del buffer[:n]
        
        self._radio_recevier.unregisterQueue(self._queue)
        
    def close(self):
        if self._run.is_set():
            self._run.clear()
            self._thread.join()