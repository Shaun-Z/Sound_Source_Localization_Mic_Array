# -*- coding: utf-8 -*-
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

# Distance parameter for microphone array geometry
L = 1

# Microphone array configuration:
# This script assumes 3 microphones arranged in an equilateral triangle:
# Mic1 at (0, 0)
# Mic2 at (L, 0) 
# Mic3 at (L/2, L*sqrt(3)/2)
# You may need to adjust the coordinates based on your actual microphone positions

devices = usb.core.find(find_all=True, idVendor=0x2886, idProduct=0x0018)

devices_list = list(devices)
print("Found \033[92m"+str(len(devices_list))+" devices: "+str(devices_list)+"\033[0m")

while True:
    try:
        # Check if we have at least 3 devices
        if len(devices_list) < 3:
            print("Error: Need at least 3 microphone devices for triangulation")
            break
            
        Mic_tuning1 = Tuning(devices_list[0])
        Mic_tuning2 = Tuning(devices_list[1])
        Mic_tuning3 = Tuning(devices_list[2])
        
        dir1 = Mic_tuning1.direction
        dir2 = Mic_tuning2.direction
        dir3 = Mic_tuning3.direction

        dir1_rad = math.radians(dir1)
        dir2_rad = math.radians(dir2)
        dir3_rad = math.radians(dir3)

        # Triangulation using 3 microphones
        # Assuming microphones are positioned at:
        # Mic1: (0, 0)
        # Mic2: (L, 0) 
        # Mic3: (L/2, L*sqrt(3)/2) - forming an equilateral triangle
        
        mic1_x, mic1_y = 0, 0
        mic2_x, mic2_y = L, 0
        mic3_x, mic3_y = L/2, L*math.sqrt(3)/2
        
        try:
            # Calculate intersection lines from each microphone
            # Line from mic1: y = x * tan(dir1_rad)
            # Line from mic2: y = (x - L) * tan(dir2_rad)
            # Line from mic3: y - mic3_y = (x - mic3_x) * tan(dir3_rad)
            
            # Find intersection of lines from mic1 and mic2
            if abs(math.sin(dir2_rad - dir1_rad)) > 1e-6:  # Avoid division by zero
                x12 = L * math.sin(dir2_rad) / math.sin(dir2_rad - dir1_rad)
                y12 = x12 * math.tan(dir1_rad)
            else:
                x12, y12 = 0, 0
                
            # Find intersection of lines from mic1 and mic3
            denom13 = math.tan(dir1_rad) - math.tan(dir3_rad)
            if abs(denom13) > 1e-6:
                x13 = (mic3_y - mic3_x * math.tan(dir3_rad)) / denom13
                y13 = x13 * math.tan(dir1_rad)
            else:
                x13, y13 = 0, 0
                
            # Find intersection of lines from mic2 and mic3
            denom23 = math.tan(dir2_rad) - math.tan(dir3_rad)
            if abs(denom23) > 1e-6:
                x23 = (mic3_y - mic3_x * math.tan(dir3_rad) + mic2_x * math.tan(dir2_rad)) / denom23
                y23 = mic2_y + (x23 - mic2_x) * math.tan(dir2_rad)
            else:
                x23, y23 = 0, 0
            
            # Average the three intersection points for better accuracy
            xx = (x12 + x13 + x23) / 3
            yy = (y12 + y13 + y23) / 3
            
            # Calculate confidence based on how close the three intersections are
            dist12_13 = math.sqrt((x12-x13)**2 + (y12-y13)**2)
            dist12_23 = math.sqrt((x12-x23)**2 + (y12-y23)**2)
            dist13_23 = math.sqrt((x13-x23)**2 + (y13-y23)**2)
            avg_deviation = (dist12_13 + dist12_23 + dist13_23) / 3
            
        except Exception as e:
            xx, yy = 0, 0
            avg_deviation = float('inf')
            
        sys.stdout.write("Dir1: {:.1f}deg Dir2: {:.1f}deg Dir3: {:.1f}deg\tLocation: ({:.2f}, {:.2f}) Deviation: {:.2f}\n".format(
            dir1, dir2, dir3, xx, yy, avg_deviation))
        sys.stdout.flush()

    except KeyboardInterrupt:
        break
