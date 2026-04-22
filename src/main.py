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

tracker = OscillationTracker("COM4")
audio = AudioEngine(tracker, "music_files/progressive.json")
plotter = PlotMonitor(tracker)
clock = ClockDisplay(tracker)

controller = LightSoundController("COM5")
vc = VoiceLEDController("../models/vosk-model-small-fr-0.22")
time.sleep(2)


vc.start()
controller.start_music()



# -------------------------
# STATE
# -------------------------

system_started = False
audio_started = False

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
            controller.start_loading_animation()
            tracker.start()
            plotter.start()

            system_started = True
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
            audio.start()
            audio_started = True

            # stop loading animation exactly once
            controller.end_loading_animation()

        clock.update()


