# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 07:11:17 2020

@author: masavoyat
"""
import sys
if not ".." in sys.path:
    sys.path.append("..")
import RadioReceiver
import queue
import time


radio = RadioReceiver.RadioReceiver()

q = queue.Queue(10)
radio.registerQueue(q)


try:
    while True:
        if q.empty():
            time.sleep(1e-3)
        else:
            print(len(q.get()))
except KeyboardInterrupt:
    pass

print(radio.center_freq)
print(radio.sample_rate)

radio.close()

while not q.empty():
    print(q.get())
