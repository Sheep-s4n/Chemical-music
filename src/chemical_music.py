import time

from utils.oscillation_tracker import OscillationTracker
from utils.audio_engine import AudioEngine
from utils.plot_monitor import PlotMonitor
from utils.clock_display import ClockDisplay


tracker = OscillationTracker(port="COM4")
audio = AudioEngine(tracker, "music_files/progressive.json")
plotter = PlotMonitor(tracker)
clock = ClockDisplay(tracker)

tracker.start()
audio.start()
plotter.start()

while True:
    clock.update()
    time.sleep(0.01)