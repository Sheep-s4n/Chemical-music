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
last_led_update = 0

# -------------------------
# MAIN LOOP (ALWAYS RUNNING)
# -------------------------

while True:

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
            controller.start_loading_animation()
            print("System activated") 

        # -------------------------
        # OTHER COMMANDS
        # -------------------------
        if cmd == "LIGHT_ON":
            controller.light_up()

        elif cmd == "LIGHT_OFF":
            controller.fade_out()

        elif cmd == "SELF_INTRODUCTION":
            controller.self_introduction()

        vc.command_locked = True
        vc.latest_command = None

    # -------------------------
    # ONLY RUN CLOCK IF SYSTEM IS ACTIVE
    # ------------------------- 
    if system_started:
    # start audio ONLY when tracker is ready
        if tracker.clock_initialized and not audio_started:
            controller.end_loading_animation() # blocks the thread but it's made on purpose

            audio.start()
            audio_started = True


        clock.update()
        # run every 0.25 second (4 fps) without blocking the thread :
        current_time = time.time()

        if current_time - last_led_update >= 0.25:
            controller.briggs_rauscher(tracker.p)
            last_led_update = current_time
        


