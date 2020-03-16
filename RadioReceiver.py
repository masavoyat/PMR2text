# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 07:11:17 2020

@author: masavoyat
"""

from rtlsdr import RtlSdr
import threading
import queue

class RadioReceiver:
    
    def __init__(self, center_freq=446.1e6, sample_rate=250e3, freq_correction=0, buffer_size=2048, device_index=0):
        self._registeredQueueList = list()
        self._registeredQueueListLock = threading.Lock()
        self._sdr = RtlSdr(device_index)
        self._sdr.sample_rate = sample_rate
        self._sdr.center_freq = center_freq
        if self._sdr.freq_correction != freq_correction:
            self._sdr.freq_correction = freq_correction
        self._thread = threading.Thread(target=self._read_thread,
                                        args=(buffer_size, ))
        self._thread.start()
    
    @property
    def sample_rate(self):
        return self._sdr.sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value):
        self._sdr.sample_rate = value
        
    @property
    def center_freq(self):
        return self._sdr.center_freq
    
    @center_freq.setter
    def center_freq(self, value):
        self._sdr.center_freq = value
    
    @property
    def freq_correction(self):
        return self._sdr.sample_rate
    
    @freq_correction.setter
    def freq_correction(self, value):
        if self._sdr.freq_correction != value:
            self._sdr.freq_correction = value
    
    def registerQueue(self, q : queue):
        with self._registeredQueueListLock:
            self._registeredQueueList.append(q)
        
    def unregisterQueue(self, q : queue):
        with self._registeredQueueListLock:
            if q in self._registeredQueueList:
                self._registeredQueueList.remove(q)
        
    @staticmethod
    def _read_samples_callback(buffer, self):
        with self._registeredQueueListLock:
            for q in self._registeredQueueList:
                if q.full():
                    q.get_nowait()
                q.put_nowait(buffer)

    def _read_thread(self, buffer_size):
        try:
            self._sdr.read_samples_async(RadioReceiver._read_samples_callback, buffer_size, self)
        except IOError: #IOError is raised when read_async is canceled
            pass
        
    def close(self):
        self._sdr.cancel_read_async()
        self._thread.join()
        with self._registeredQueueListLock:
            for q in self._registeredQueueList:
                if q.full():
                    q.get_nowait()
                q.put_nowait(None)