# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 21:56:39 2020

@author: masavoyat
"""
import sys
if not ".." in sys.path:
    sys.path.append("..")
import RadioReceiver
import ChannelDecoder


radio = RadioReceiver.RadioReceiver()
cd = ChannelDecoder.ChannelDecoder(radio, 8)

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

cd.close()
radio.close()
