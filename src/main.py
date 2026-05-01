import time

from utils.oscillation_tracker import OscillationTracker
from utils.audio_engine import AudioEngine
from utils.plot_monitor import PlotMonitor
from utils.clock_display import ClockDisplay

from utils.voice_led_controller import VoiceLEDController
from utils.light_sound import LightSoundController


# -------------------------
# INIT (NO START YET)
# -------------------------

controller = LightSoundController("COM5")
vc = VoiceLEDController("../models/vosk-model-small-fr-0.22")

tracker = OscillationTracker("COM6")
audio = AudioEngine(tracker, "music_files/pulse.chm", light_animation_controller=controller)
plotter = PlotMonitor(tracker)
clock = ClockDisplay(tracker)

time.sleep(2)


vc.start()
controller.start_music()



# -------------------------
# STATE
# -------------------------

system_started = False
audio_started = False

# ------------------------
# LIST OF LED SECTIONS 
# -----------------------

LED_SECTIONS = [ [(0,100)] , [(0,140)], [(0,180)]]

# -------------------------
# MAIN LOOP (ALWAYS RUNNING)
# -------------------------

while True:
    time.sleep(0.01) # to avoid busy waiting and reduce CPU usage
    vc.update()

    if vc.heard_trigger():
        cmd = vc.get_command()

        # -------------------------
        # START SYSTEM ON DEMAND
        # -------------------------
        if cmd == "START_LOADING" and not system_started:
            tracker.start()
            plotter.start()

            system_started = True
            controller.start_loading_animation() # blocks the thread --> to fix
            print("System activated") 

        # -------------------------
        # OTHER COMMANDS
        # -------------------------
        if cmd == "LIGHT_ON":
            controller.light_up()
            vc.command_locked = True
            vc.latest_command = None
        elif cmd == "LIGHT_OFF":
            controller.fade_out()
            vc.command_locked = True
            vc.latest_command = None
            
        elif cmd == "SELF_INTRODUCTION":
            controller.self_introduction()
            vc.command_locked = True
            vc.latest_command = None


    # -------------------------
    # ONLY RUN CLOCK IF SYSTEM IS ACTIVE
    # ------------------------- 
    if system_started:
    # start audio ONLY when tracker is ready
        clock.update()

        if tracker.clock_initialized and not audio_started:
            controller.end_loading_animation() # blocks the thread but it's made on purpose

            audio.start()
            audio_started = True


        controller.briggs_rauscher(tracker.p)
        


