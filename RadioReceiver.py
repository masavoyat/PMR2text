# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 07:11:17 2020

@author: masavoyat
"""

from rtlsdr import RtlSdr
import threading

class RadioReceiver:
    
    def __init__(self, center_freq=446.1e6, sample_rate=250e3, freq_correction=0, buffer_size=2048, device_index=0):
        self._thread = threading.Thread(target=self._main_loop)
        self._registeredQueueList = list()
        self._registeredQueueListLock = threading.Lock()
        self._run = threading.Event()
        self._center_freq = center_freq
        self._sample_rate = sample_rate
        self._freq_correction = freq_correction
        self._buffer_size = buffer_size
        self._device_index = device_index
        self._param_update = threading.Event()
        self._param_update.set()
        self._run.set()
        self._thread.start()
    
    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = value
        self._param_update.set()
        
    @property
    def center_freq(self):
        return self._center_freq
    
    @center_freq.setter
    def center_freq(self, value):
        self._center_freq = value
        self._param_update.set()
    
    @property
    def freq_correction(self):
        return self._sample_rate
    
    @freq_correction.setter
    def freq_correction(self, value):
        self._freq_correction = value
        self._param_update.set()
    
    def registerQueue(self, q):
        self._registeredQueueListLock.acquire()
        self._registeredQueueList.append(q)
        self._registeredQueueListLock.release()
        
    def unregisterQueue(self, q):
        self._registeredQueueListLock.acquire()
        if q in self._registeredQueueList:
            self._registeredQueueList.remove(q)
        self._registeredQueueListLock.release()
        
    def _main_loop(self):
        sdr = RtlSdr(self._device_index)
        sdr.gain = 'auto'
        while self._run.is_set():
            if self._param_update.is_set():
                sdr.sample_rate = self._sample_rate # Hz suported ranges: 225001 - 300000 Hz and 900001 - 3200000 Hz
                sdr.center_freq = self._center_freq # Hz
                if self._freq_correction != sdr.freq_correction: # Make sure we don't write the same value to avoid error
                    sdr.freq_correction = self._freq_correction # ppm
                self._param_update.clear()
            data = sdr.read_samples(self._buffer_size)
            for q in self._registeredQueueList:
                if q.full():
                    q.get_nowait()
                q.put_nowait(data)
        # Thread end: close radio and put None to registered queue
        sdr.close()
        for q in self._registeredQueueList:
            if q.full():
                q.get_nowait()
            q.put_nowait(None)
            
    def close(self):
        self._run.clear()
        self._thread.join()