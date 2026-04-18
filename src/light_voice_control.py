from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController
import time


controller = LightSoundController("COM5")
time.sleep(2)
controller.start_music() #for background music



vc = VoiceLEDController("../models/vosk-model-small-fr-0.22")
vc.start()


while True:

    vc.update()

    if vc.heard_trigger():
        print("Trigger heard!")
        cmd = vc.get_command()
        
        print("Command :", cmd)
        if cmd == "LIGHT_ON":
            controller.light_up()
            vc.command_locked = True
            vc.latest_command = None

        if cmd == "LIGHT_OFF":
            controller.fade_out()
            vc.command_locked = True
            vc.latest_command = None
        
        if cmd == "SELF_INTRODUCTION":
            controller.self_introduction()
            vc.command_locked = True
            vc.latest_command = None

""" 
words ['antho', 'éteint', 'la', 'lumière', 'sublet']
"""
