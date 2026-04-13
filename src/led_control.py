# important things to consider : serial size is 64 byte on this chip so you can't just send the 300 bytes at once
# colors is a list of (r, g, b, brightness) tuples
# Clamp values to 0-254 to avoid colliding with the 0xFF marker
import serial
import time

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

while True:
    # Forward gradient — full brightness
    send_frame([(255, i, 0, 254) for i in range(NUM_LEDS)])
    time.sleep(1)

    # Reverse gradient — half brightness
    send_frame([(255, 254 - i, 0, i) for i in range(NUM_LEDS)])
    time.sleep(1)