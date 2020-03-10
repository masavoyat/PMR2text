# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:55:23 2020

@author: sam
"""

import numpy as np

class Squelch:
    
    def __init__(self, level_db=0, alpha=1.0):
        self.threshold = 10**(level_db/10)
        self.alpha = alpha
        
    def process(self, data):
        data_array = np.array(data)
        data_filt = np.real(data_array*np.conj(data_array))
        return np.where(data_filt >= self.threshold,
                        data,
                        np.zeros(data.shape))
            
