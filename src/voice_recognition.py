import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer


# important things to consider : serial size is 64 byte on this chip so you can't just send the 300 bytes at once
# colors is a list of (r, g, b, brightness) tuples
# Clamp values to 0-254 to avoid colliding with the 0xFF marker

import serial
import time


from utils.light_sound import LightSoundController

leds = LightSoundController("COM5")
time.sleep(2)


state =  "WAIT_BONJOUR"



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
                    leds.light_up()
                    state = "WAIT_AU_REVOIR"
            elif state == "WAIT_AU_REVOIR":
                if "au revoir" in value :
                    leds.fade_out()
                    state = "WAIT_BONJOUR"
