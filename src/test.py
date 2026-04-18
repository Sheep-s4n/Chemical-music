from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
from utils.led_controller import LEDController
import time


leds = LightSoundController("COM5")
#leds = LEDController("COM5")
time.sleep(2)

leds.fade_out()
