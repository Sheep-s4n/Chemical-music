import time

from utils.oscillation_tracker import OscillationTracker
from utils.audio_engine import AudioEngine
from utils.plot_monitor import PlotMonitor
from utils.clock_display import ClockDisplay


tracker = OscillationTracker(port="COM6")
audio = AudioEngine(tracker, "music_files/pulse.chm")
plotter = PlotMonitor(tracker)
clock = ClockDisplay(tracker)


tracker.start()
audio.start()
plotter.start()

while True:
    clock.update()
    time.sleep(0.01)
# clock_initialized --> 
#for the other event, rework voice led control so it can take tracker data 
# and trigger the light show when the clock is initialized
# , then trigger the music when the clock is active.