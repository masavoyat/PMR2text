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

radio = RadioReceiver.RadioReceiver(buffer_size=1023)
cd8 = ChannelDecoder.ChannelDecoder(radio, 8)
cd7 = ChannelDecoder.ChannelDecoder(radio, 7)

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

cd8.close()
cd7.close()
radio.close()
