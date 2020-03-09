# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:55:23 2020

@author: sam
"""

import numpy as np

class FMdemodulator:
    
    def __init__(self, dt):
        self.z1 = 0+0j
        self.fs = 1/dt
        
    def filt(self, data):
        # w = 2*fs*IM((z1-z2)*(z1+z2).conjugate())/((z1+z2)*(z1+z2).conjugate())
        out = list()
        for z0 in data:
            m = z0 - self.z1
            p = z0 + self.z1
            projection = (m*p.conjugate()).imag
            norm2 = (p*p.conjugate()).real
            w = 2*self.fs*projection/norm2
            out.append(w)
            self.z1 = z0
            
