from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
from utils.led_controller import LEDController

import time
import threading



vc = VoiceLEDController("../models/vosk-model-small-fr-0.22")
vc.start()



while True:

    vc.update()

    if vc.heard_trigger():
        #print("Trigger heard!")
        cmd = vc.get_command()
        
        #print("Command :", cmd)
        if cmd == "LIGHT_ON":
            vc.command_locked = True
            vc.latest_command = None
        if cmd == "LIGHT_OFF":
            vc.command_locked = True
            vc.latest_command = None
        if cmd == "SELF_INTRODUCTION":
            vc.command_locked = True
            vc.latest_command = None   
            
        if cmd == "START_LOADING":
            
            vc.command_locked = True
            vc.latest_command = None

# 1. tester avec deux micros
# faire la nouvelle commande pour lancer l'analyse
 

"""" 
leds = LightSoundController("COM5")
#leds = LEDController("COM5")       
time.sleep(2)
leds.start_music() #for background music
leds.light_up()
time.sleep(2)
leds.briggs_rauscher(0.8) 

"""