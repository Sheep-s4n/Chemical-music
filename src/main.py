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



# ------------------------
# LIST OF LED SECTIONS 
# -----------------------

LED_SECTIONS = [ [(0,100)] , [(0,140)], [(0,180)]]

# -------------------------
# STATE & VARIABLES
# -------------------------

system_started = False
audio_started = False
current_sections_index = 0

# -------------------------
# MAIN LOOP (ALWAYS RUNNING)
# -------------------------

last_briggs_time = 0

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
            controller.start_loading_animation() # shouldn't block the thread anymore
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
        
        elif cmd == "LED_SECTION":
            controller.led_sections(LED_SECTIONS[current_sections_index])
            current_sections_index = (current_sections_index + 1) % len(LED_SECTIONS)
            vc.command_locked = True
            vc.latest_command = None

        elif cmd == "STOP" and system_started:
            tracker.stop()
            audio.stop()
            plotter.stop()
            system_started = False
            audio_started = False
            vc.command_locked = True
            vc.latest_command = None
            controller.stop_chemical_music()
            print("System stopped")
        
        elif cmd == "ACKNOWLEDGEMENT" : 
            controller.acknowledgment()
            vc.command_locked = True
            vc.latest_command = None

    # -------------------------
    # ONLY RUN CLOCK IF SYSTEM IS ACTIVE
    # ------------------------- 
    if system_started:
    # start audio ONLY when tracker is ready
        clock.update()

        if tracker.clock_initialized and not audio_started:
            #controller.end_loading_animation() # blocks the thread but it's made on purpose

            audio.start()
            audio_started = True

        if audio_started:
            now = time.time()
            if now - last_briggs_time >= 0.1:
                controller.briggs_rauscher(tracker.p)
                print(tracker.p)
                last_briggs_time = now


