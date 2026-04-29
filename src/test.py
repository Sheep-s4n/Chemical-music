"""
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



# was commmented: --
leds = LightSoundController("COM5")
#leds = LEDController("COM5")       
time.sleep(2)
leds.start_music() #for background music
leds.light_up()
time.sleep(2)
leds.briggs_rauscher(0.8) 
--

On  part sur un système de buffer tailler ilimité pour stoquer les donnés (pas un système de queue comme pour le temps réel)

on trouve un treshold avec min et max ça va juste etre (max -min) / 2, je pense que le critère pour arreter l'analyse de min et max, va etre genre la densité de points par lequelle on est passer 2 fois atteint les 80% (en gros sur toute les données qu'on a si plus de 80% sont dupliquer alors on considère qu'on a un min et max cohérent --> j'ai pas trouver d'autre critère comme ça mais si t'a une meilleur idée je prend)
maintenant qu'on dispose de min et max on peut définir un treshold
avec le treshold on peut calcule la période de deux cycle : on fait leur moyenne
Mtn on passe à la phase en temps réel avec un buffer qui fonctionne comme une queu :
1. le système de treshold va suffir pour trouver les changement de cycle pour l'horloge 

pour la musique réactionnel et le pulse, on analyse la dérive pour voir son signe si plus de -50% (la pente) alors on considére qu'on passe à la phase bleu , ce qui correspond au moment ou la courbe chute drastiquement presque comme une asymptote verticale et on confirme mais jsp comment et pour le blanc j'imagine dès qu'on remonte avec une courbe de 5% on peut considérer qu'on repasser au blanc -jaune

"""


MUSIC_FILE_RELATIVE_PATH = "music_files/progressive.chm" 
# put your music file here, relative to the src folder
# than open a command line interface and run the command : python chm_player.py
# keep in mind that each reaction is different so the music might be faster or slower













from utils.oscillation_tracker import OscillationTracker
from utils.audio_engine import AudioEngine
from utils.plot_monitor import PlotMonitor
import time 

tracker = OscillationTracker(arduino_mode=False)
audio = AudioEngine(tracker, MUSIC_FILE_RELATIVE_PATH)
plotter = PlotMonitor(tracker)

tracker.start()
plotter.start()
audio.start()

while True :
    #print(tracker.derivative)
    time.sleep(0.2)


# transition to blue : 
#    if (tracker.derivative < -400):
#        print("BLUE")
# check there is no like too litlle time between two blue 
# if we moved to the blue phase according to treshold but it hasn't been seen with the derivative : consider we are in blue phase