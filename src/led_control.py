# important things to consider : serial size is 64 byte on this chip so you can't just send the 300 bytes at once
# colors is a list of (r, g, b, brightness) tuples
# Clamp values to 0-254 to avoid colliding with the 0xFF marker

import serial
import time
from LED_animations.wipe import *
from LED_animations.fade import *


arduino = serial.Serial('COM5', 115200)
time.sleep(2)

NUM_LEDS = 100
START_MARKER = 0xFF

def send_frame(colors):
    # colors is a list of (r, g, b, brightness) tuples
    # Clamp all values to 0-254 to avoid colliding with the 0xFF start marker
    frame = [START_MARKER]
    print(colors)
    for r, g, b, brightness in colors:
        frame.extend([min(r, 254), min(g, 254), min(b, 254), min(brightness, 254)])
    arduino.write(bytes(frame))


dt = 0.05
next_time = time.time()
        
for frame in white_wipe(NUM_LEDS):
    send_frame(frame)

    next_time += dt
    sleep_time = next_time - time.time()
    if sleep_time > 0:
        time.sleep(sleep_time)


time.sleep(2)
for frame in fade_out(NUM_LEDS, 10):
    send_frame(frame)
    time.sleep(0.02)
