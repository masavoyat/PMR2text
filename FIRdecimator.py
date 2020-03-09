# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:43:18 2020

@author: sam
"""
import numpy as np

class FIRdecimator:
    
    def __init__(self, h, decim):
        self.h = np.array(h)
        self.x = np.zeros(len(h))
        self.decim = decim
        self.index = 0
        
    def filt(self, data):
        # Filter
        x = np.concatenate((self.x, data))
        data_filt = np.convolve(x, self.h, mode='valid')
        self.x = x[-len(self.h):]
        # decimate
        data_out = data_filt[self.index::self.decim]
        self.index = self.index + len(data_out)*self.decim - len(data)
        return data_out