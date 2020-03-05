# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:46:37 2020

@author: masavoyat
"""

import queue
import threading
import RadioReceiver
import numpy as np

class ChannelDecoder:
    """ PMR446 channel decoder.
    Attach to the radio_receiver and assume center_frequency is 446.1MHz
    and sample_rate is 250KHz."""
    
    def __init__(self, radio_recevier : RadioReceiver, channel):
        self._thread = threading.Thread(target=self._main_loop)
        self._run = threading.Event()
        self._radio_recevier = radio_recevier
        self._channel = channel
        self._queue = queue.Queue(10)
        self._run.set()
        self._thread.start()
        
    def _main_loop(self):
        channel_freq = 446e6 + 3.125e3 + 6.25e3*self._channel
        lo_freq = channel_freq - self._radio_recevier.center_freq
        samp_rate = self._radio_recevier.sample_rate
        lo = np.exp(1j*lo_freq/samp_rate)
        buffer = list() # local buffer used for group data processing
        self._radio_recevier.registerQueue(self._queue)
        while self._run.is_set():
            data = self._queue.get()
            if not data: # in case the radio return None
                self._run.clear()
                continue
            buffer.extend(data)
            # Process data by 80*16 samples so that is can be mixed and downsampled by packet
            while len(buffer)>80*16:
                
                del buffer[:80*16]
        
        self._radio_recevier.unregisterQueue(self._queue)
        
    def close(self):
        if self._run.is_set():
            self._run.clear()
            self._thread.join()