import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer


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
state =  "WAIT_BONJOUR"

def send_frame(colors):
    # colors is a list of (r, g, b, brightness) tuples
    # Clamp all values to 0-254 to avoid colliding with the 0xFF start marker
    frame = [START_MARKER]
    print(colors)
    for r, g, b, brightness in colors:
        frame.extend([min(r, 254), min(g, 254), min(b, 254), min(brightness, 254)])
    arduino.write(bytes(frame))



q = queue.Queue()

model = Model("../models/vosk-model-small-fr-0.22")
rec = KaldiRecognizer(model, 16000)

def callback(indata, frames, time, status):
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback): #uses the default microphone

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("FINAL:", result.get("text"))
        else:
            partial = json.loads(rec.PartialResult())
            value = partial.get("partial")
            if state == "WAIT_BONJOUR":
                if "bonjour" in value :
                    for frame in white_wipe(NUM_LEDS):
                        send_frame(frame)
                        time.sleep(0.02)
                    state = "WAIT_AU_REVOIR"
            elif state == "WAIT_AU_REVOIR":
                if "au revoir" in value :
                    for frame in fade_out(NUM_LEDS, 10):
                        send_frame(frame)
                        time.sleep(0.02)
                    state = "WAIT_BONJOUR"
