import sys
import os

import usb.core
import usb.util
import time

import math

# Add parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from tuning import Tuning

L = 1

devices = usb.core.find(find_all=True, idVendor=0x2886, idProduct=0x0018)

devices_list = list(devices)
print("Found \033[92m"+str(len(devices_list))+" devices: "+str(devices_list)+"\033[0m")

while True:
    try:
        Mic_tuning1 = Tuning(devices_list[0])
        Mic_tuning2 = Tuning(devices_list[1])
        dir1 = Mic_tuning1.direction
        dir2 = Mic_tuning2.direction

        dir1_rad = math.radians(dir1)
        dir2_rad = math.radians(dir2)

        try:
            xx = math.sin(dir2_rad)*math.cos(dir1_rad)/math.sin(dir2_rad-dir1_rad)*L
            yy = math.sin(dir2_rad)*math.sin(dir1_rad)/math.sin(dir2_rad-dir1_rad)*L
        except:
            xx = 0
            yy = 0
        sys.stdout.write("Direction1: {} Direction2: {}\tLocation: ({}, {})\n".format(dir1, dir2, xx, yy))
        sys.stdout.flush()

    except KeyboardInterrupt:
        break
