from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
from utils.led_controller import LEDController
import time


leds = LightSoundController("COM5")
#leds = LEDController("COM5")
time.sleep(2)
leds.fade_out()
""" 
leds.light_up()
time.sleep(2)
p = 0.0
while True:
    if p > 1.0:
        p = 0.0
    time.sleep(1)
    leds.briggs_rauscher(p)
    p+=0.05
    print(p)
"""