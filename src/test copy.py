from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
import time



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
            print("light on detected")
            vc.latest_command = None
        if cmd == "LIGHT_OFF":
            print("light off detected")
            vc.command_locked = True
            vc.latest_command = None
        if cmd == "SELF_INTRODUCTION":
            print("self introduction command detected")
            vc.command_locked = True
            vc.latest_command = None   
            
        if cmd == "START_LOADING":
            print("start loading command detected")
            vc.command_locked = True
            vc.latest_command = None
        if cmd == "LED_SECTION":
            print("prochaine section")
            vc.command_locked = True
            vc.latest_command = None

        if cmd == "STOP":
            vc.command_locked = True
            vc.latest_command = None
            print("System stopped")
        
        elif cmd == "ACKNOWLEDGEMENT" : 
            print("acknowledgmeent")
            vc.command_locked = True
            vc.latest_command = None
            
