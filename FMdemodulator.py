# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:55:23 2020

@author: sam
"""

import numpy as np

class FMdemodulator:
    
    def __init__(self, dt):
        self.z1 = 0+0j
        self.dt = dt
        
    def filt(self, data):
        # w = 2/dt*abs(z1-z2)/abs(z1+z2)
        out = list()
        for z0 in data:
            self.z1 = z0
            
