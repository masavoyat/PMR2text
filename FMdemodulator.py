# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:55:23 2020

@author: sam
"""

import numpy as np

class FMdemodulator:
    
    def __init__(self, fs, max_deviation):
        self.z = 0+0j
        self.gain = fs/(2*np.pi*max_deviation)
        
    def process(self, data):
        # w = gain * np.angle(z0*np.conj(z1))
        z = np.concatenate(([self.z], data))
        w = self.gain * np.angle(z[1:]*np.conj(z[:-1]))
        self.z = z[-1]
        return w
            
