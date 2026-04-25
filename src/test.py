from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
from utils.led_controller import LEDController
import time
import threading


leds = LightSoundController("COM5")
#leds = LEDController("COM5")       
time.sleep(2)
leds.start_music() #for background music
leds.light_up()
time.sleep(2)
leds.briggs_rauscher(0.8) 
while True :
    time.sleep(3)
    leds.flash_leds()
